## Personal Finance API (FastAPI)

A lightweight backend API for managing personal finances: accounts, categories, transactions, budgets, recurring transactions, goals, and reporting.

### Quickstart

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. Open docs:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Tech

- FastAPI
- SQLModel + SQLite
- Uvicorn

### Notes

- No authentication included.
- SQLite database stored at `./finance.db`.
# finance_me