from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_deepseek import ChatDeepSeek
from langchain.messages import HumanMessage



model = ChatDeepSeek(
    model="deepseek-v4-flash", extra_body={"thinking": {"type": "disabled"}}
)
class OverAllState(MessagesState):
    output: str

def llm_node(state: OverAllState) -> OverAllState:
    output = model.invoke(state["messages"])
    return {"messages": [output]}

def output_node(state: OverAllState) -> OverAllState: 
    return {"output": state["messages"][-1].content}

builder = StateGraph(OverAllState)
builder.add_node(llm_node)
builder.add_node(output_node)
builder.add_edge(START, "llm_node")
builder.add_edge("llm_node", "output_node")
builder.add_edge("output_node", END)


DB_URL = "postgresql://admin:123456@localhost:5432/test_db"
with PostgresSaver.from_conn_string(DB_URL) as checkpointer:
    checkpointer.setup()
    graph = builder.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "chapter_6_6.2.4"}}

        # 调用时传递
    # res =graph.invoke({"messages": [HumanMessage("你好，我是老王")]}, config=config)
    graph.invoke({"messages": [HumanMessage("从现在开始，你是小王")]}, config=config)
    res = graph.invoke({"messages": [HumanMessage("我是谁？你是谁？")]}, config=config)
    # print(res["output"])

    print('=' * 30, '-> 完整消息列表 <-', '=' * 30)
    for msg in res["messages"]:
        msg.pretty_print()