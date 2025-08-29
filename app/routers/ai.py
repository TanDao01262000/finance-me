from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..db import get_session
from ..models import Transaction
from ..ai.agent import build_advice_graph, simple_rule_categorize


router = APIRouter(prefix="/ai", tags=["ai"])

_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_advice_graph()
    return _graph


@router.post("/advice")
async def ai_advice(payload: Dict[str, Any], session: Session = Depends(get_session)) -> Dict[str, Any]:
    question: str = payload.get("question", "Provide general finance advice.")
    # Basic context: last 50 transactions summary
    try:
        txns = session.exec(
            select(Transaction).order_by(Transaction.date.desc()).limit(50)
        ).all()
        income = sum((t.amount or 0.0) for t in txns if (t.amount or 0.0) > 0)
        expenses = sum((t.amount or 0.0) for t in txns if (t.amount or 0.0) < 0)
        context = f"Recent income: {income:.2f}, expenses: {expenses:.2f}, net: {income+expenses:.2f}"
    except Exception as e:
        context = f"Context unavailable: {e}"
    if os.getenv("OPENAI_API_KEY"):
        try:
            graph = get_graph()
            state = {"question": question, "context": context}
            res = await graph.ainvoke(state)
            return {"answer": res.get("answer", "")}
        except Exception:
            pass
    # Fallback if no key
    return {
        "answer": f"[Local fallback] {context}. For personalized insights, set OPENAI_API_KEY."
    }


@router.post("/categorize")
def ai_categorize(payload: Dict[str, Any]) -> Dict[str, str]:
    description: str = payload.get("description", "")
    payee: Optional[str] = payload.get("payee")
    label = simple_rule_categorize(description, payee)
    return {"category": label}


@router.post("/categorize/bulk")
def ai_categorize_bulk(items: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    labels = [simple_rule_categorize(i.get("description", ""), i.get("payee")) for i in items]
    return {"categories": labels}


@router.get("/auto-categorize-latest")
def auto_categorize_latest(limit: int = 50, session: Session = Depends(get_session)) -> Dict[str, Any]:
    txns = session.exec(
        select(Transaction).where(Transaction.category_id.is_(None)).order_by(Transaction.date.desc()).limit(limit)
    ).all()
    suggestions = [
        {
            "id": t.id,
            "description": t.description,
            "payee": t.payee,
            "suggested_category": simple_rule_categorize(t.description or "", t.payee),
        }
        for t in txns
    ]
    return {"suggestions": suggestions}
