from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..db import get_session
from ..models import Goal, GoalCreate, GoalRead, GoalUpdate


router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("/", response_model=List[GoalRead])
def list_goals(*, session: Session = Depends(get_session)) -> list[Goal]:
    return session.exec(select(Goal).order_by(Goal.target_date.is_(None), Goal.target_date.asc())).all()


@router.post("/", response_model=GoalRead, status_code=201)
def create_goal(*, session: Session = Depends(get_session), goal: GoalCreate) -> Goal:
    db_obj = Goal.from_orm(goal)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


@router.get("/{goal_id}", response_model=GoalRead)
def get_goal(*, session: Session = Depends(get_session), goal_id: int) -> Goal:
    db_obj = session.get(Goal, goal_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Goal not found")
    return db_obj


@router.patch("/{goal_id}", response_model=GoalRead)
def update_goal(*, session: Session = Depends(get_session), goal_id: int, goal: GoalUpdate) -> Goal:
    db_obj = session.get(Goal, goal_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Goal not found")
    update_data = goal.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_obj, key, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


@router.delete("/{goal_id}", status_code=204)
def delete_goal(*, session: Session = Depends(get_session), goal_id: int) -> None:
    db_obj = session.get(Goal, goal_id)
    if not db_obj:
        return
    session.delete(db_obj)
    session.commit()
