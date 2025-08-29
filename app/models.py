from __future__ import annotations

from datetime import date as Date, datetime as DateTime
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class AccountType(str, Enum):
    checking = "checking"
    savings = "savings"
    credit = "credit"
    cash = "cash"
    investment = "investment"


class CategoryType(str, Enum):
    expense = "expense"
    income = "income"
    transfer = "transfer"


class AccountBase(SQLModel):
    name: str = Field(index=True)
    type: AccountType = Field(default=AccountType.checking, index=True)
    initial_balance: float = 0.0
    archived: bool = False


class Account(AccountBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transactions: list[Transaction] = Relationship(back_populates="account")  # type: ignore


class AccountCreate(AccountBase):
    pass


class AccountRead(AccountBase):
    id: int


class AccountUpdate(SQLModel):
    name: Optional[str] = None
    type: Optional[AccountType] = None
    initial_balance: Optional[float] = None
    archived: Optional[bool] = None


class CategoryBase(SQLModel):
    name: str = Field(index=True)
    type: CategoryType = Field(default=CategoryType.expense, index=True)
    parent_id: Optional[int] = Field(default=None, foreign_key="category.id")


class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    parent: Optional[Category] = Relationship(sa_relationship_kwargs={"remote_side": "Category.id"})  # type: ignore
    transactions: list[Transaction] = Relationship(back_populates="category")  # type: ignore


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int


class CategoryUpdate(SQLModel):
    name: Optional[str] = None
    type: Optional[CategoryType] = None
    parent_id: Optional[int] = None


class TransactionBase(SQLModel):
    date: Date = Field(index=True)
    amount: float = Field(description="Positive for income, negative for expenses")
    description: Optional[str] = None
    payee: Optional[str] = Field(default=None, index=True)
    tags_csv: Optional[str] = Field(default=None, description="Comma-separated list of tags")
    account_id: int = Field(foreign_key="account.id", index=True)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id", index=True)


class Transaction(TransactionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: DateTime = Field(default_factory=DateTime.utcnow, index=True)
    updated_at: DateTime = Field(default_factory=DateTime.utcnow, index=True)

    account: Account = Relationship(back_populates="transactions")  # type: ignore
    category: Optional[Category] = Relationship(back_populates="transactions")  # type: ignore


class TransactionCreate(TransactionBase):
    pass


class TransactionRead(TransactionBase):
    id: int
    created_at: DateTime
    updated_at: DateTime


class TransactionUpdate(SQLModel):
    date: Optional[Date] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    payee: Optional[str] = None
    tags_csv: Optional[str] = None
    account_id: Optional[int] = None
    category_id: Optional[int] = None


class BudgetBase(SQLModel):
    category_id: int = Field(foreign_key="category.id")
    month: str = Field(index=True, description="YYYY-MM")
    amount: float
    notes: Optional[str] = None


class Budget(BudgetBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class BudgetCreate(BudgetBase):
    pass


class BudgetRead(BudgetBase):
    id: int


class BudgetUpdate(SQLModel):
    category_id: Optional[int] = None
    month: Optional[str] = None
    amount: Optional[float] = None
    notes: Optional[str] = None


class Frequency(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"


class RecurringBase(SQLModel):
    name: str
    frequency: Frequency = Field(default=Frequency.monthly)
    next_occurrence: Date
    end_date: Optional[Date] = None
    amount: float
    description: Optional[str] = None
    account_id: int = Field(foreign_key="account.id")
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")


class Recurring(RecurringBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    auto_post: bool = Field(default=False)


class RecurringCreate(RecurringBase):
    auto_post: bool = False


class RecurringRead(RecurringBase):
    id: int
    auto_post: bool


class RecurringUpdate(SQLModel):
    name: Optional[str] = None
    frequency: Optional[Frequency] = None
    next_occurrence: Optional[Date] = None
    end_date: Optional[Date] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    account_id: Optional[int] = None
    category_id: Optional[int] = None
    auto_post: Optional[bool] = None


class GoalBase(SQLModel):
    name: str
    target_amount: float
    target_date: Optional[Date] = None
    current_amount: float = 0.0


class Goal(GoalBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class GoalCreate(GoalBase):
    pass


class GoalRead(GoalBase):
    id: int


class GoalUpdate(SQLModel):
    name: Optional[str] = None
    target_amount: Optional[float] = None
    target_date: Optional[Date] = None
    current_amount: Optional[float] = None
