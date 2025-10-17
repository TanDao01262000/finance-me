from __future__ import annotations

from datetime import date, timedelta
from fastapi.testclient import TestClient


def test_budgets_usage_and_reports(client: TestClient):
    # setup
    acc = client.post("/accounts/", json={"name": "A", "type": "checking", "initial_balance": 0}).json()
    cat_food = client.post("/categories/", json={"name": "Food", "type": "expense"}).json()
    today = date.today().isoformat()
    # spend
    client.post("/transactions/", json={"date": today, "amount": -50.0, "account_id": acc["id"], "category_id": cat_food["id"]})
    # budget
    month = today[:7]
    client.post("/budgets/", json={"category_id": cat_food["id"], "month": month, "amount": 200.0})

    # usage
    r = client.get(f"/budgets/{cat_food['id']}/usage?month={month}")
    assert r.status_code == 200
    data = r.json()
    assert data["budget"] == 200.0
    assert data["spent"] <= 0  # negative spending

    # reports
    r = client.get(f"/reports/cashflow?start_date={today}&end_date={today}")
    assert r.status_code == 200
    r = client.get("/reports/net-worth")
    assert r.status_code == 200
    r = client.get(f"/reports/spending-by-category?start_date={today}&end_date={today}")
    assert r.status_code == 200


def test_recurring_run_and_goals_and_ai(client: TestClient):
    acc = client.post("/accounts/", json={"name": "B", "type": "checking", "initial_balance": 0}).json()
    # recurring
    item = client.post(
        "/recurring/",
        json={
            "name": "Rent",
            "frequency": "monthly",
            "next_occurrence": date.today().isoformat(),
            "amount": -800.0,
            "account_id": acc["id"],
            "auto_post": True,
        },
    ).json()
    r = client.post(f"/recurring/{item['id']}/run")
    assert r.status_code == 200

    # goal
    r = client.post("/goals/", json={"name": "Emergency", "target_amount": 1000.0})
    assert r.status_code == 201

    # ai categorize
    r = client.post("/ai/categorize", json={"description": "Starbucks coffee"})
    assert r.status_code == 200

    # ai advice fallback (no key assumed)
    r = client.post("/ai/advice", json={"question": "How to save more?"})
    assert r.status_code == 200
