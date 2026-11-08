# ci-cd-workshop-backend

Todo List API，使用 FastAPI + SQLAlchemy 2.0 + PostgreSQL，以 Alembic 管理資料庫 schema。

## 本機開發

需求：[uv](https://docs.astral.sh/uv/) 0.12 以上（會自動安裝 Python 3.12）、Docker。

`docker compose up -d db` 會把 PostgreSQL 開在 `127.0.0.1:5432`（可用 `DB_PORT` 調整），預設的 `DATABASE_URL` 即可直接連線。

```bash
uv sync
docker compose up -d db
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

API 文件：http://localhost:8000/docs

## 測試與靜態檢查

```bash
uv run pytest
uv run pytest tests/test_todos.py::test_stats
uv run ruff check .
uv run ruff format --check .
```

測試使用 SQLite in-memory，不需要啟動 PostgreSQL。

## Docker

```bash
cp .env.example .env
docker compose up --build -d
curl http://localhost:8000/api/health
```

容器啟動時會先執行 `alembic upgrade head`，再啟動 uvicorn。

## 環境變數

| 名稱 | 預設值 | 說明 |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg://todo:todo@localhost:5432/todo` | SQLAlchemy 連線字串 |
| `CORS_ORIGINS` | `["http://localhost:5173","http://localhost:8080"]` | 允許的前端來源（JSON 陣列） |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | `todo` | docker compose 中 PostgreSQL 的設定 |
| `API_PORT` | `8000` | docker compose 對外的 port |
| `DB_PORT` | `5432` | docker compose 中 PostgreSQL 開在本機的 port（只綁 127.0.0.1） |

## API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/health` | 健康檢查 |
| GET | `/api/todos` | 列表，支援 `due_date`、`due_from`、`due_to`、`overdue`、`is_completed`、`priority`、`tag_ids`、`search`、`sort_by`、`order`、`limit`、`offset` |
| GET | `/api/todos/stats` | 統計 |
| GET / PATCH / DELETE | `/api/todos/{id}` | 取得 / 更新（含標記完成）/ 刪除 |
| POST | `/api/todos` | 新增 |
| DELETE | `/api/todos/completed` | 清除所有已完成 |
| GET / POST | `/api/tags` | 列出 / 新增 tag |
| PATCH / DELETE | `/api/tags/{id}` | 更新 / 刪除 tag |
