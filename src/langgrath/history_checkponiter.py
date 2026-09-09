from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_deepseek import ChatDeepSeek
from langchain.messages import HumanMessage
from loguru import logger



model = ChatDeepSeek(
    model="deepseek-v4-flash", extra_body={"thinking": {"type": "disabled"}}
)
class OverAllState(MessagesState):
    topic: str
    poem: str
    joke: str
    final_output: str

class InputState(MessagesState):
    topic: str

class OutputState(MessagesState):
    final_output: str

def node_poem(state: OverAllState) -> OverAllState:
    logger.info("node_poem运行完毕")
    poem = model.invoke([HumanMessage(f"写一首关于 {state['topic']} 的七言绝句")]).content
    return {"poem": poem}

def node_joke(state: OverAllState) -> OverAllState:
    logger.info("node_joke运行完毕")
    joke = model.invoke([HumanMessage(f"讲一个关于 {state['topic']} 的笑话")]).content
    return {"joke": joke} 

def node_output(state: OverAllState) -> OverAllState:
    logger.info("node_output运行完毕")
    poem  = state['poem']
    joke  = state['joke']
    topic = state['topic']
    final_output = f"关于 {topic} 的七言绝句是：\n{poem}，：\n笑话是：\n{joke}"
    return {"final_output": final_output}

builder = StateGraph(OverAllState, input_schema=InputState, output_schema=OutputState)
builder.add_node(node_poem)
builder.add_node(node_joke)
builder.add_node(node_output)
builder.add_edge(START, "node_poem")
builder.add_edge(START, "node_joke")
builder.add_edge("node_poem", "node_output")
builder.add_edge("node_joke", "node_output")
builder.add_edge("node_output", END)



DB_URL = "postgresql://admin:123456@localhost:5432/test_db"
with PostgresSaver.from_conn_string(DB_URL) as checkpointer:
    checkpointer.setup()
    graph = builder.compile(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "chapter_6_6.2.5"}} 
    res = graph.invoke({"topic": "春天"}, config=config)
    # print('=' * 30, '-> 历史检查点列表 <-', '=' * 30)
    # history_checkpoints = list(graph.get_state_history(config=config))
    # print(history_checkpoints)
    print('=' * 30, '-> 最新的检查点 <-', '=' * 30)
    new_checkpoints = list(graph.get_state(config=config))
    print(new_checkpoints)