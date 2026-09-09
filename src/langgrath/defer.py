from time import sleep
from typing import TypedDict, Annotated
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from operator import add

class OverAllState(TypedDict):
    logs: Annotated[list[str],add]
    cur_id: Annotated[list[str],add]

class OutputState(TypedDict):
    cur_id: list[str]

class PrivateState(TypedDict):
    rewritten_query: str

def node1(state: OverAllState) -> OverAllState:
    for k,v in state.items():
        print(f"1k:{k}: v:{v}")
    return {
        "logs": ['node1运行完毕']
    }

def node2(state: OverAllState) -> OverAllState:
    for k,v in state.items():
        print(f"2k:{k}: v:{v}")
    return {
        "logs": ['node2运行完毕'],
        "cur_id": ['node2']
    }

def node3(state: OverAllState) -> OverAllState:
    sleep(1)
    for k,v in state.items():
        print(f"3k:{k}: v:{v}")
    return {
        "logs": ['node3运行完毕'],
        "cur_id": ['node3']
    }

def node4(state: OverAllState) -> OverAllState:
    sleep(2)
    for k,v in state.items():
        print(f"4k:{k}: v:{v}")
    return {
        "logs": ['node4运行完毕'],
        "cur_id": ['node4']
    }

def node5(state: OverAllState) -> OverAllState:
    sleep(2)
    for k,v in state.items():
        print(f"5k:{k}: v:{v}")
    return {
        "logs": ['node5运行完毕'],
        "cur_id": ['node5']
    }


builder = StateGraph(OverAllState, output_schema = OutputState)

builder.add_node(node1)
builder.add_node(node2)
builder.add_node(node3)
builder.add_node(node4)
builder.add_node(node5, defer=True)

builder.add_edge(START, "node1")
builder.add_edge(START, "node5")
builder.add_edge("node1", "node2")
builder.add_edge("node1", "node3")
builder.add_edge("node2", "node4")
builder.add_edge("node3", "node4")
builder.add_edge("node5", END)


grapth = builder.compile()
result = grapth.invoke({ "cur_id": ['start'], "logs": ["start"] })
print(result)