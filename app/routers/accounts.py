from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func

from ..db import get_session
from ..models import Account, AccountCreate, AccountRead, AccountUpdate, Transaction


router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/", response_model=List[AccountRead])
def list_accounts(
    *,
    session: Session = Depends(get_session),
    include_archived: bool = Query(default=False),
) -> list[Account]:
    statement = select(Account)
    if not include_archived:
        statement = statement.where(Account.archived == False)  # noqa: E712
    statement = statement.order_by(Account.name.asc())
    return session.exec(statement).all()


@router.post("/", response_model=AccountRead, status_code=201)
def create_account(*, session: Session = Depends(get_session), account: AccountCreate) -> Account:
    db_obj = Account.from_orm(account)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


@router.get("/{account_id}", response_model=AccountRead)
def get_account(*, session: Session = Depends(get_session), account_id: int) -> Account:
    db_obj = session.get(Account, account_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_obj


@router.patch("/{account_id}", response_model=AccountRead)
def update_account(
    *, session: Session = Depends(get_session), account_id: int, account: AccountUpdate
) -> Account:
    db_obj = session.get(Account, account_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Account not found")
    update_data = account.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_obj, key, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


@router.delete("/{account_id}", status_code=204)
def delete_account(*, session: Session = Depends(get_session), account_id: int) -> None:
    db_obj = session.get(Account, account_id)
    if not db_obj:
        return
    session.delete(db_obj)
    session.commit()


@router.get("/{account_id}/balance")
def get_account_balance(
    *, session: Session = Depends(get_session), account_id: int
) -> dict[str, float]:
    db_obj = session.get(Account, account_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Account not found")
    total_delta = session.exec(
        select(func.coalesce(func.sum(Transaction.amount), 0.0)).where(Transaction.account_id == account_id)
    ).one()
    balance = (db_obj.initial_balance or 0.0) + float(total_delta or 0.0)
    return {"balance": balance}
