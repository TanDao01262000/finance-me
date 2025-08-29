from __future__ import annotations

from fastapi.testclient import TestClient


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_accounts_crud_and_balance(client: TestClient):
    # create account
    r = client.post(
        "/accounts/",
        json={"name": "Checking", "type": "checking", "initial_balance": 100.0},
    )
    assert r.status_code == 201
    acc = r.json()
    acc_id = acc["id"]

    # list accounts
    r = client.get("/accounts/")
    assert r.status_code == 200
    assert any(a["name"] == "Checking" for a in r.json())

    # get account
    r = client.get(f"/accounts/{acc_id}")
    assert r.status_code == 200

    # update account
    r = client.patch(f"/accounts/{acc_id}", json={"archived": True})
    assert r.status_code == 200
    assert r.json()["archived"] is True

    # balance initially should be 100
    r = client.get(f"/accounts/{acc_id}/balance")
    assert r.status_code == 200
    assert r.json()["balance"] == 100.0

    # delete account
    r = client.delete(f"/accounts/{acc_id}")
    assert r.status_code == 204
