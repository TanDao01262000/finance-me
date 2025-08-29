from __future__ import annotations

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlmodel import Session, select

from ..db import get_session
from ..models import Transaction, TransactionCreate, TransactionRead, TransactionUpdate
from ..utils import parse_date


router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/", response_model=List[TransactionRead])
def list_transactions(
    *,
    session: Session = Depends(get_session),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    account_id: Optional[int] = Query(default=None),
    category_id: Optional[int] = Query(default=None),
    payee: Optional[str] = Query(default=None),
    tag: Optional[str] = Query(default=None),
    limit: int = Query(default=200, le=1000),
    offset: int = Query(default=0),
) -> list[Transaction]:
    statement = select(Transaction)
    if start_date:
        statement = statement.where(Transaction.date >= parse_date(start_date))
    if end_date:
        statement = statement.where(Transaction.date <= parse_date(end_date))
    if account_id:
        statement = statement.where(Transaction.account_id == account_id)
    if category_id:
        statement = statement.where(Transaction.category_id == category_id)
    if payee:
        statement = statement.where(Transaction.payee == payee)
    if tag:
        statement = statement.where(Transaction.tags_csv.like(f"%{tag}%"))
    statement = statement.order_by(Transaction.date.desc(), Transaction.id.desc())
    statement = statement.offset(offset).limit(limit)
    return session.exec(statement).all()


@router.post("/", response_model=TransactionRead, status_code=201)
def create_transaction(
    *, session: Session = Depends(get_session), transaction: TransactionCreate
) -> Transaction:
    db_obj = Transaction.from_orm(transaction)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(*, session: Session = Depends(get_session), transaction_id: int) -> Transaction:
    db_obj = session.get(Transaction, transaction_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_obj


@router.patch("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    *, session: Session = Depends(get_session), transaction_id: int, transaction: TransactionUpdate
) -> Transaction:
    db_obj = session.get(Transaction, transaction_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Transaction not found")
    update_data = transaction.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_obj, key, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


@router.delete("/{transaction_id}", status_code=204, response_class=Response)
def delete_transaction(*, session: Session = Depends(get_session), transaction_id: int) -> Response:
    db_obj = session.get(Transaction, transaction_id)
    if not db_obj:
        return Response(status_code=204)
    session.delete(db_obj)
    session.commit()
    return Response(status_code=204)
