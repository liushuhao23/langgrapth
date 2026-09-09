from operator import add
from random import randint
from typing import Annotated

from langchain.messages import HumanMessage, SystemMessage, ToolMessage
from langchain.tools import tool
from langchain_deepseek import ChatDeepSeek
from langgraph.types import Command
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import MessagesState

model = ChatDeepSeek(
    model="deepseek-v4-flash", extra_body={"thinking": {"type": "disabled"}}
)


@tool(parse_docstring=True)
def get_weather(city: str = "北京"):
    """
     查询指定城市当日天气

    Args:
        city: 城市名称
    """
    return f"${city}的天气是晴天。"


@tool(parse_docstring=True)
def get_news(topic: str = "科技"):
    """
    查询特定领域的当日热点

    Args:
        topic: 新闻主题
    """
    print(topic)
    if topic == "AI":
        return "Anthropic 发布了 Claude Opus-4.8，但通过 API 用中文向它发送“你是谁？”时，大多数情况下返回的却是“Qwen”或“Deepseek”"
    else:
        return "双汇发展子公司猪肉产品被抽检出抗生素超标37.5倍"


tools = [get_weather, get_news]

model_with_tools = model.bind_tools(tools=tools)


class OverAllState(MessagesState):
    user_input: str
    final_answer: str


def user_input(state: OverAllState) -> OverAllState:
    return {"messages": [HumanMessage(state["user_input"])]}


def llm_node(state: OverAllState) -> OverAllState:
    ai_message = model_with_tools.invoke(state["messages"])
    print(f"ai_message: {ai_message}")
    if ai_message.tool_calls:
        goto="tool"
    else:
        goto="output"
    return Command(
        update={"messages": [ai_message]},
        goto=goto
    )

def tool_node(state: OverAllState) -> OverAllState:
    message = state["messages"]
    ai_message = message[-1]
    tool_calls = ai_message.tool_calls
    fail_prob  = 6
    for tool_call in tool_calls:
        if tool_call["name"] == "get_weather":
            if  randint(0, 9) < fail_prob:
                message.append(
                    ToolMessage(
                        content="网络波动，调用失败，请重试",
                        tool_call_id=tool_call['id']
                    )
                )
            else:
              message.append(get_weather.invoke(tool_call))
        elif tool_call["name"] == "get_news":
            if  randint(0, 9) < fail_prob:
                message.append(
                    ToolMessage(
                        content="网络波动，调用失败，请重试",
                        tool_call_id=tool_call['id']
                    )
                )
            else:
                message.append(get_news.invoke(tool_call))
        else:
            message.append(
                ToolMessage(
                    content="工具名称错误，调用失败，请重试",
                    tool_call_id=tool_call["id"]
                )
            )
    return {"messages": message}

def output_node(state: OverAllState) -> OverAllState:
    return {"final_answer": state["messages"][-1].content}

builder = StateGraph(OverAllState)

builder.add_node("user_input", user_input)
builder.add_node("llm", llm_node)
builder.add_node("tool", tool_node)
builder.add_node("output", output_node)

builder.add_edge(START, "user_input")
builder.add_edge("user_input", "llm")
builder.add_edge("tool", "llm")
builder.add_edge("output", END)

grapth = builder.compile()

res = grapth.invoke({"user_input": "北京今天天气和AI 热点?", "messages": [SystemMessage(content="如果调试失败，必须重试到成功为止")]})
# print(f"Result: {res}")
