from typing import Literal

from langchain.messages import HumanMessage
from langchain_deepseek import ChatDeepSeek
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import MessagesState

model = ChatDeepSeek(
    model="deepseek-v4-flash", extra_body={"thinking": {"type": "disabled"}}
)


class OverAllState(MessagesState):
    topic: str
    jokeTopic: str
    content_type: str
    poem: str
    jokeContent: str


def node1(state: OverAllState) -> OverAllState:
    res1 = model.invoke([HumanMessage(f"写一首关于 {state['topic']} 的七言绝句")])
    return {"poem": res1.content}


def node2(state: OverAllState) -> OverAllState:
    joke = model.invoke([HumanMessage(f"讲一个关于 {state['jokeTopic']} 的笑话")])
    return {"jokeContent": joke.content}

def router(state: OverAllState) -> Literal["a", "b"]:
    print(f"Content type: {state['content_type']}, 'asjkhdhas'")
    print("诗" in state["content_type"])  
    if "诗" in state['content_type']:
        return "a"
    else:
        return "b"

builder = StateGraph(OverAllState)
builder.add_node(node1)
builder.add_node(node2)
builder.add_node(router)

path_map={ 
    "a": "node1", 
    "b": "node2", 
} 
builder.add_conditional_edges(START, router, path_map)
builder.add_edge("node1", END)
builder.add_edge("node2", END)

grapth = builder.compile()
result = grapth.invoke({"topic": "春天",  "jokeTopic": "后端开发工程师", "content_type": "诗"})
print(result)
