from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from langgraph.graph.message import MessagesState
from langgraph.runtime import Runtime
from langchain.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_deepseek import ChatDeepSeek
from typing import Final, Tuple
from langgraph.store.postgres import PostgresStore

from loguru import logger

model = ChatDeepSeek(
    model="deepseek-v4-flash", extra_body={"thinking": {"type": "disabled"}}
)


class OverAllState(MessagesState):
    username: str
    user_input: str
    output: str
    preferences: dict[str, str]  # 用户偏好


USERS_NS: Final[Tuple[str]] = ("users",)
PREFERENCES_KEY: Final[str] = "preferences"


def check_preferences_node(state: OverAllState, runtime: Runtime) -> OverAllState:
    username = state["username"]
    store = runtime.store
    nameSpace = (*USERS_NS, username)
    key = PREFERENCES_KEY
    item = store.get(nameSpace, key)
    if not item:
        logger.warning("长期记忆中没有 {} 的偏好数据", username)
        return {}

    logger.info("长期记忆中保存的用户偏好: {}", item.value)
    return {"preferences": item.value}


def router(state: OverAllState) -> Literal["check_preferences", "end"]:
    if not state.get("preferences"):
        logger.info("需要从长期记忆中查询用户偏好")
        return "check_preferences_node"
    logger.info("用户长期记忆已存在")
    return "llm_node"


def llm_node(state: OverAllState) -> OverAllState:
    preferences = state.get("preferences", {})
    user_input = state["user_input"]
    human_prompt = f"这是用户的偏好: \n{preferences}\n这是用户的需求: \n{user_input}\n"
    system_prompt = "请根据用户偏好解决用户需求"
    messages: list[SystemMessage | HumanMessage | AIMessage | ToolMessage] = (
        [SystemMessage(content=system_prompt)]
        if not state.get("messages", [])
        else state["messages"]
    )
    model_response = model.invoke(messages + [HumanMessage(content=human_prompt)])
    output = model_response.content
    return {
        "messages": messages + [HumanMessage(content=human_prompt), model_response],
        "output": output,
    }

builder = StateGraph(OverAllState)
builder.add_node("check_preferences_node", check_preferences_node)
builder.add_node("llm_node", llm_node)
builder.add_conditional_edges(START, router, path_map=["check_preferences_node", "llm_node"])
builder.add_edge("check_preferences_node", "llm_node")
builder.add_edge("llm_node", END)

DB_URL = "postgresql://admin:123456@localhost:5432/test_db"
# 编译时传递短期记忆和长期记忆存储器（均使用 PostgreSQL）
with PostgresSaver.from_conn_string(DB_URL) as checkpointer, \
     PostgresStore.from_conn_string(DB_URL) as store:
    checkpointer.setup()
    graph = builder.compile(checkpointer=checkpointer, store=store)

    config = {"configurable": {"thread_id": "1231"}}
    res = graph.invoke({"username": "Alice", "user_input": "我有点无聊，和我聊聊天吧"}, config=config)

    print('=' * 30, '->  <-', '=' * 30)
    print(res)

    # 第二次调用：复用同一个 thread_id，观察短期记忆缓存效果
    new_res = graph.invoke({"user_input": "推荐一下酸奶"}, config=config)
    new_messages = new_res.pop("messages")
    print('=' * 30, '->  <-', '=' * 30)
    print(new_res)