from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlmodel import Session, select, func

from ..db import get_session
from ..models import Budget, BudgetCreate, BudgetRead, BudgetUpdate, Transaction
from ..utils import parse_month


router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("/", response_model=List[BudgetRead])
def list_budgets(*, session: Session = Depends(get_session), month: str | None = Query(default=None)) -> list[Budget]:
    statement = select(Budget)
    if month:
        statement = statement.where(Budget.month == month)
    statement = statement.order_by(Budget.month.desc())
    return session.exec(statement).all()


@router.post("/", response_model=BudgetRead, status_code=201)
def create_budget(*, session: Session = Depends(get_session), budget: BudgetCreate) -> Budget:
    db_obj = Budget.from_orm(budget)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


@router.get("/{budget_id}", response_model=BudgetRead)
def get_budget(*, session: Session = Depends(get_session), budget_id: int) -> Budget:
    db_obj = session.get(Budget, budget_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Budget not found")
    return db_obj


@router.patch("/{budget_id}", response_model=BudgetRead)
def update_budget(*, session: Session = Depends(get_session), budget_id: int, budget: BudgetUpdate) -> Budget:
    db_obj = session.get(Budget, budget_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Budget not found")
    update_data = budget.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_obj, key, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


@router.delete("/{budget_id}", status_code=204, response_class=Response)
def delete_budget(*, session: Session = Depends(get_session), budget_id: int) -> Response:
    db_obj = session.get(Budget, budget_id)
    if not db_obj:
        return Response(status_code=204)
    session.delete(db_obj)
    session.commit()
    return Response(status_code=204)


@router.get("/{category_id}/usage")
def budget_usage(
    *,
    session: Session = Depends(get_session),
    category_id: int,
    month: str,
) -> dict[str, float]:
    start, end = parse_month(month)
    spent = session.exec(
        select(func.coalesce(func.sum(Transaction.amount), 0.0))
        .where(Transaction.category_id == category_id)
        .where(Transaction.date >= start)
        .where(Transaction.date <= end)
        .where(Transaction.amount < 0)
    ).one()
    budget_row = session.exec(
        select(Budget).where(Budget.category_id == category_id).where(Budget.month == month)
    ).first()
    budget_amount = budget_row.amount if budget_row else 0.0
    return {"budget": float(budget_amount), "spent": float(spent or 0.0), "remaining": float(budget_amount) + float(spent or 0.0)}
