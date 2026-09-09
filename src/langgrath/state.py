from operator import add
from typing import  Annotated
from langchain.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import MessagesState
from langchain_deepseek import ChatDeepSeek

model = ChatDeepSeek(
    model="deepseek-v4-flash", extra_body={"thinking": {"type": "disabled"}}
)


class OverAllState(MessagesState):
    topic: str
    poem: str
    res: Annotated[list, add]
    joke: str


def node1(state: OverAllState) -> OverAllState:
    poem = model.invoke([HumanMessage(f"写一首关于 {state['topic']} 的七言绝句")])
    return {"poem": poem}


def node2(state: OverAllState) -> OverAllState:
    joke = model.invoke([HumanMessage(f"讲一个关于 {state['joke']} 的笑话")])
    return {"joke": joke}


builder = StateGraph(OverAllState)
builder.add_node(node1)
builder.add_node( node2)
builder.add_edge(START, "node1")
builder.add_edge(START, "node2")
builder.add_edge("node1", END)
builder.add_edge("node2", END)

grapth = builder.compile()
result = grapth.invoke({"topic": "春天",  "joke": "后端开发工程师"})
print(result)
