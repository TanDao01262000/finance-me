from __future__ import annotations

import os
from typing import Any, Dict

from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.checkpoint.memory import MemorySaver


class AdviceState(dict):
    pass


def make_advice_node(model: ChatOpenAI):
    async def node(state: AdviceState) -> AdviceState:
        user_question = state.get("question") or "Provide general personal finance advice."
        context = state.get("context") or ""
        messages = [
            {"role": "system", "content": "You are a helpful personal finance assistant."},
            {
                "role": "user",
                "content": f"Question: {user_question}\nContext: {context}",
            },
        ]
        resp = await model.ainvoke(messages)
        return {"answer": resp.content}

    return node


def build_advice_graph() -> Any:
    api_key = os.getenv("OPENAI_API_KEY")
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, api_key=api_key)
    graph = StateGraph(AdviceState)
    graph.add_node("advice", make_advice_node(model))
    graph.add_edge(START, "advice")
    return graph.compile(checkpointer=MemorySaver())


def simple_rule_categorize(description: str, payee: str | None = None) -> str:
    text = f"{description or ''} {payee or ''}".lower()
    rules = [
        ("uber" in text or "lyft" in text, "Transport"),
        ("starbucks" in text or "coffee" in text, "Coffee"),
        ("groceries" in text or "walmart" in text or "target" in text, "Groceries"),
        ("rent" in text or "mortgage" in text, "Housing"),
        ("salary" in text or "payroll" in text, "Income"),
        ("amazon" in text, "Shopping"),
        ("electric" in text or "water" in text or "gas bill" in text, "Utilities"),
    ]
    for cond, label in rules:
        if cond:
            return label
    return "Uncategorized"
