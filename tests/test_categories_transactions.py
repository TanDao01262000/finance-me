from __future__ import annotations

from datetime import date
from fastapi.testclient import TestClient


def test_categories_and_transactions_filters(client: TestClient):
    # create account
    acc = client.post(
        "/accounts/",
        json={"name": "Main", "type": "checking", "initial_balance": 0.0},
    ).json()
    # create categories
    cat_food = client.post("/categories/", json={"name": "Food", "type": "expense"}).json()
    cat_income = client.post("/categories/", json={"name": "Salary", "type": "income"}).json()

    # create transactions
    t1 = client.post(
        "/transactions/",
        json={
            "date": date.today().isoformat(),
            "amount": -20.5,
            "description": "Lunch",
            "payee": "Cafe",
            "account_id": acc["id"],
            "category_id": cat_food["id"],
        },
    )
    assert t1.status_code == 201
    t2 = client.post(
        "/transactions/",
        json={
            "date": date.today().isoformat(),
            "amount": 1000.0,
            "description": "Salary",
            "payee": "Company",
            "account_id": acc["id"],
            "category_id": cat_income["id"],
        },
    )
    assert t2.status_code == 201

    # filter by category
    r = client.get(f"/transactions/?category_id={cat_food['id']}")
    assert r.status_code == 200
    assert all(x["category_id"] == cat_food["id"] for x in r.json())

    # filter by payee
    r = client.get("/transactions/?payee=Cafe")
    assert r.status_code == 200
    assert any(x["description"] == "Lunch" for x in r.json())

    # delete a category
    r = client.delete(f"/categories/{cat_food['id']}")
    assert r.status_code == 204
