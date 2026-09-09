from typing import Literal, TypedDict

from langchain.messages import HumanMessage
from langchain_deepseek import ChatDeepSeek
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

model = ChatDeepSeek(
    model="deepseek-v4-flash",
    extra_body={
        "thinking": {
            "type": "disabled"
        }
    }
)

class OverAllState():
    topic: str
    content_type: Literal["poem", "joke"]
    poem: str
    joke: str

def router(state):
    content_type = state["content_type"]
    if content_type == "poem":
        return Command (
            goto="poem_node"
        )
    else:
        return Command (
            goto="joke_node"
        )

def poem_node(state: OverAllState) -> OverAllState:
    topic = state["topic"]
    prompt = f"请生成一首关于 {topic} 的七言绝句"
    poem = model.invoke([HumanMessage(prompt)]).content

    return {
        "poem": poem
    }

def joke_node(state: OverAllState) -> OverAllState:
    topic = state["topic"]
    prompt = f"请生成一个关于 {topic} 的冷笑话"
    joke = model.invoke([HumanMessage(prompt)]).content

    return {
        "joke": joke
    }

builder = StateGraph(OverAllState)
builder.add_node("poem_node", poem_node)
builder.add_node("joke_node", joke_node)
builder.add_node("router", router)
builder.add_edge(START, "router")
builder.add_edge("poem_node", END)
builder.add_edge("joke_node", END)

graph = builder.compile()
poem_res = graph.invoke({"topic": "布偶猫", "content_type": "poem"})
joke_res = graph.invoke({"topic": "布偶猫", "content_type": "joke"})
print(poem_res)
print(joke_res)