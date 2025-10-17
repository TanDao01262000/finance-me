from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func

from ..db import get_session
from ..models import Account, Transaction
from ..utils import parse_date, month_iter, parse_month


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/net-worth")
def net_worth(*, session: Session = Depends(get_session)) -> dict[str, float]:
    total = 0.0
    accounts = session.exec(select(Account)).all()
    for acct in accounts:
        delta = session.exec(
            select(func.coalesce(func.sum(Transaction.amount), 0.0)).where(Transaction.account_id == acct.id)
        ).one()
        balance = (acct.initial_balance or 0.0) + float(delta or 0.0)
        total += balance
    return {"net_worth": float(total)}


@router.get("/cashflow")
def cashflow(
    *,
    session: Session = Depends(get_session),
    start_date: str,
    end_date: str,
) -> dict[str, float]:
    start = parse_date(start_date)
    end = parse_date(end_date)
    total = session.exec(
        select(func.coalesce(func.sum(Transaction.amount), 0.0))
        .where(Transaction.date >= start)
        .where(Transaction.date <= end)
    ).one()
    income = session.exec(
        select(func.coalesce(func.sum(Transaction.amount), 0.0))
        .where(Transaction.date >= start)
        .where(Transaction.date <= end)
        .where(Transaction.amount > 0)
    ).one()
    expenses = session.exec(
        select(func.coalesce(func.sum(Transaction.amount), 0.0))
        .where(Transaction.date >= start)
        .where(Transaction.date <= end)
        .where(Transaction.amount < 0)
    ).one()
    return {
        "net": float(total or 0.0),
        "income": float(income or 0.0),
        "expenses": float(expenses or 0.0),
    }


@router.get("/spending-by-category")
def spending_by_category(
    *,
    session: Session = Depends(get_session),
    start_date: str,
    end_date: str,
) -> dict[str, float]:
    start = parse_date(start_date)
    end = parse_date(end_date)
    rows = session.exec(
        select(Transaction.category_id, func.coalesce(func.sum(Transaction.amount), 0.0))
        .where(Transaction.date >= start)
        .where(Transaction.date <= end)
        .where(Transaction.amount < 0)
        .group_by(Transaction.category_id)
    ).all()
    result: dict[str, float] = {}
    for category_id, total in rows:
        key = str(category_id) if category_id is not None else "uncategorized"
        result[key] = float(total or 0.0)
    return result


@router.get("/trend")
def trend(
    *,
    session: Session = Depends(get_session),
    start_month: str,
    end_month: str,
    category_id: Optional[int] = Query(default=None),
) -> dict[str, dict[str, float]]:
    result: dict[str, dict[str, float]] = {}
    for month in month_iter(start_month, end_month):
        start, end = parse_month(month)
        base_stmt = select(func.coalesce(func.sum(Transaction.amount), 0.0)).where(
            Transaction.date >= start
        ).where(Transaction.date <= end)
        if category_id is not None:
            base_stmt = base_stmt.where(Transaction.category_id == category_id)

        net = session.exec(base_stmt).one() or 0.0
        income_stmt = base_stmt.where(Transaction.amount > 0)
        expenses_stmt = base_stmt.where(Transaction.amount < 0)
        income = session.exec(income_stmt).one() or 0.0
        expenses = session.exec(expenses_stmt).one() or 0.0
        result[month] = {
            "net": float(net),
            "income": float(income),
            "expenses": float(expenses),
        }
    return result
