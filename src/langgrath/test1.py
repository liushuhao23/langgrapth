from typing import TypedDict, Annotated
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from operator import add

class OverAllState(TypedDict):
    logs: Annotated[list[str],add]
    cur_id: str


builder = StateGraph(OverAllState)

def node1(state: OverAllState) -> OverAllState:
    pre_id = state['cur_id']
    return {
        "logs": ['log node1运行完毕'],
        "cur_id": pre_id + 'node1 节点、'
    }


def node2(state: OverAllState) -> OverAllState:
    pre_id = state['cur_id']
    return {
        "logs": ['log node2运行完毕'],
        "cur_id": pre_id + 'node2节点'
    }

builder.add_node(node1)
builder.add_node(node2)



builder.add_edge(START, "node1")
builder.add_edge("node1", "node2")
builder.add_edge("node2", END)

grapth = builder.compile()
result = grapth.invoke({ "cur_id": 'start', "logs": [] })
print(result)