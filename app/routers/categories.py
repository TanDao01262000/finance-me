from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select

from ..db import get_session
from ..models import Category, CategoryCreate, CategoryRead, CategoryUpdate


router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=List[CategoryRead])
def list_categories(*, session: Session = Depends(get_session)) -> list[Category]:
    return session.exec(select(Category).order_by(Category.name.asc())).all()


@router.post("/", response_model=CategoryRead, status_code=201)
def create_category(*, session: Session = Depends(get_session), category: CategoryCreate) -> Category:
    db_obj = Category.from_orm(category)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(*, session: Session = Depends(get_session), category_id: int) -> Category:
    db_obj = session.get(Category, category_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_obj


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(
    *, session: Session = Depends(get_session), category_id: int, category: CategoryUpdate
) -> Category:
    db_obj = session.get(Category, category_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Category not found")
    update_data = category.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_obj, key, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


@router.delete("/{category_id}", status_code=204, response_class=Response)
def delete_category(*, session: Session = Depends(get_session), category_id: int) -> Response:
    db_obj = session.get(Category, category_id)
    if not db_obj:
        return Response(status_code=204)
    session.delete(db_obj)
    session.commit()
    return Response(status_code=204)
