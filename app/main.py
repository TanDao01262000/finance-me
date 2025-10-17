from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import create_db_and_tables
from .routers import accounts, categories, transactions, budgets, recurring, goals, reports, health, ai


def create_app() -> FastAPI:
    app = FastAPI(title="Personal Finance API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def on_startup() -> None:
        create_db_and_tables()

    app.include_router(health.router)
    app.include_router(accounts.router)
    app.include_router(categories.router)
    app.include_router(transactions.router)
    app.include_router(budgets.router)
    app.include_router(recurring.router)
    app.include_router(goals.router)
    app.include_router(reports.router)
    app.include_router(ai.router)

    return app


app = create_app()
