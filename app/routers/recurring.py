from __future__ import annotations

from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlmodel import Session, select

from ..db import get_session
from ..models import Recurring, RecurringCreate, RecurringRead, RecurringUpdate, Transaction
from ..utils import advance_date_by_frequency


router = APIRouter(prefix="/recurring", tags=["recurring"])


@router.get("/", response_model=List[RecurringRead])
def list_recurring(*, session: Session = Depends(get_session)) -> list[Recurring]:
    return session.exec(select(Recurring).order_by(Recurring.next_occurrence.asc())).all()


@router.post("/", response_model=RecurringRead, status_code=201)
def create_recurring(*, session: Session = Depends(get_session), item: RecurringCreate) -> Recurring:
    db_obj = Recurring.from_orm(item)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


@router.get("/{recurring_id}", response_model=RecurringRead)
def get_recurring(*, session: Session = Depends(get_session), recurring_id: int) -> Recurring:
    db_obj = session.get(Recurring, recurring_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Recurring item not found")
    return db_obj


@router.patch("/{recurring_id}", response_model=RecurringRead)
def update_recurring(
    *, session: Session = Depends(get_session), recurring_id: int, item: RecurringUpdate
) -> Recurring:
    db_obj = session.get(Recurring, recurring_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Recurring item not found")
    update_data = item.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_obj, key, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


@router.delete("/{recurring_id}", status_code=204, response_class=Response)
def delete_recurring(*, session: Session = Depends(get_session), recurring_id: int) -> Response:
    db_obj = session.get(Recurring, recurring_id)
    if not db_obj:
        return Response(status_code=204)
    session.delete(db_obj)
    session.commit()
    return Response(status_code=204)


@router.post("/{recurring_id}/run", response_model=RecurringRead)
def run_recurring(
    *, session: Session = Depends(get_session), recurring_id: int, run_date: date | None = Query(default=None)
) -> Recurring:
    db_obj = session.get(Recurring, recurring_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Recurring item not found")
    post_date = run_date or db_obj.next_occurrence
    # create transaction if auto_post
    if db_obj.auto_post:
        txn = Transaction(
            date=post_date,
            amount=db_obj.amount,
            description=db_obj.description,
            account_id=db_obj.account_id,
            category_id=db_obj.category_id,
            payee=db_obj.name,
        )
        session.add(txn)
    # update next occurrence
    db_obj.next_occurrence = advance_date_by_frequency(db_obj.next_occurrence, db_obj.frequency)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj
