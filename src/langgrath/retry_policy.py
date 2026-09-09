from time import sleep
from typing import TypedDict, Annotated
from requests.exceptions import HTTPError
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from operator import add
from loguru import logger

from langgraph.types import RetryPolicy


class EmptyState(TypedDict):
    pass


def node_a(state: EmptyState) -> EmptyState:
    logger.info("node1运行完毕")
    raise HTTPError("网络连接超时...")


builder = StateGraph(EmptyState)
builder.add_node("node_a", node_a, retry_policy=RetryPolicy(max_attempts=3))
builder.add_edge(START, "node_a")
builder.add_edge("node_a", END)

graph = builder.compile()
try:
    graph.invoke({})
except HTTPError as e:
    logger.info("重试次数耗尽: {}", e)
