from typing import Any

from fastapi.testclient import TestClient


def create_todo(client: TestClient, **overrides: Any) -> dict[str, Any]:
    payload = {"title": "Task", **overrides}
    response = client.post("/api/todos", json=payload)
    assert response.status_code == 201
    return response.json()


def list_titles(client: TestClient, **params: Any) -> list[str]:
    response = client.get("/api/todos", params=params)
    assert response.status_code == 200
    return [item["title"] for item in response.json()["items"]]


def test_health_check(client: TestClient) -> None:
    assert client.get("/api/health").json() == {"status": "ok"}


def test_create_todo_with_defaults(client: TestClient) -> None:
    todo = create_todo(client, title="Write slides")

    assert todo["title"] == "Write slides"
    assert todo["priority"] == "medium"
    assert todo["is_completed"] is False
    assert todo["completed_at"] is None
    assert todo["tags"] == []


def test_create_todo_with_tags(client: TestClient) -> None:
    tag = client.post("/api/tags", json={"name": "work"}).json()

    todo = create_todo(client, tag_ids=[tag["id"]])

    assert [t["name"] for t in todo["tags"]] == ["work"]


def test_create_todo_with_unknown_tag_returns_not_found(client: TestClient) -> None:
    response = client.post("/api/todos", json={"title": "Task", "tag_ids": [42]})

    assert response.status_code == 404


def test_create_todo_requires_title(client: TestClient) -> None:
    assert client.post("/api/todos", json={"title": ""}).status_code == 422


def test_get_missing_todo_returns_not_found(client: TestClient) -> None:
    assert client.get("/api/todos/999").status_code == 404


def test_mark_todo_completed_and_uncompleted(client: TestClient) -> None:
    todo_id = create_todo(client)["id"]

    completed = client.patch(f"/api/todos/{todo_id}", json={"is_completed": True}).json()
    assert completed["is_completed"] is True
    assert completed["completed_at"] is not None

    reopened = client.patch(f"/api/todos/{todo_id}", json={"is_completed": False}).json()
    assert reopened["is_completed"] is False
    assert reopened["completed_at"] is None


def test_update_todo_fields_and_tags(client: TestClient) -> None:
    tag = client.post("/api/tags", json={"name": "home"}).json()
    todo_id = create_todo(client)["id"]

    response = client.patch(
        f"/api/todos/{todo_id}",
        json={"title": "Updated", "priority": "urgent", "tag_ids": [tag["id"]]},
    )

    body = response.json()
    assert body["title"] == "Updated"
    assert body["priority"] == "urgent"
    assert [t["id"] for t in body["tags"]] == [tag["id"]]


def test_delete_todo(client: TestClient) -> None:
    todo_id = create_todo(client)["id"]

    assert client.delete(f"/api/todos/{todo_id}").status_code == 204
    assert client.get(f"/api/todos/{todo_id}").status_code == 404


def test_clear_completed(client: TestClient) -> None:
    done_id = create_todo(client, title="Done")["id"]
    create_todo(client, title="Pending")
    client.patch(f"/api/todos/{done_id}", json={"is_completed": True})

    response = client.delete("/api/todos/completed")

    assert response.json() == {"deleted": 1}
    assert list_titles(client) == ["Pending"]


def test_filter_by_exact_due_date(client: TestClient) -> None:
    create_todo(client, title="Today", due_date="2026-01-15")
    create_todo(client, title="Tomorrow", due_date="2026-01-16")

    assert list_titles(client, due_date="2026-01-15") == ["Today"]


def test_filter_by_due_date_range(client: TestClient) -> None:
    create_todo(client, title="Early", due_date="2026-01-01")
    create_todo(client, title="Middle", due_date="2026-01-10")
    create_todo(client, title="Late", due_date="2026-01-31")

    titles = list_titles(client, due_from="2026-01-05", due_to="2026-01-20")

    assert titles == ["Middle"]


def test_filter_overdue_excludes_completed(client: TestClient) -> None:
    create_todo(client, title="Late", due_date="2026-01-10")
    done_id = create_todo(client, title="Late but done", due_date="2026-01-10")["id"]
    create_todo(client, title="Future", due_date="2026-02-01")
    client.patch(f"/api/todos/{done_id}", json={"is_completed": True})

    assert list_titles(client, overdue=True) == ["Late"]


def test_filter_by_status_priority_tag_and_search(client: TestClient) -> None:
    tag_id = client.post("/api/tags", json={"name": "work"}).json()["id"]
    create_todo(client, title="Prepare demo", priority="high", tag_ids=[tag_id])
    create_todo(client, title="Buy milk", priority="low")

    assert list_titles(client, priority="high") == ["Prepare demo"]
    assert list_titles(client, tag_ids=[tag_id]) == ["Prepare demo"]
    assert list_titles(client, search="milk") == ["Buy milk"]
    assert list_titles(client, is_completed=False) == ["Buy milk", "Prepare demo"]


def test_sort_by_priority(client: TestClient) -> None:
    create_todo(client, title="Medium", priority="medium")
    create_todo(client, title="Urgent", priority="urgent")
    create_todo(client, title="Low", priority="low")

    assert list_titles(client, sort_by="priority", order="desc") == ["Urgent", "Medium", "Low"]


def test_sort_by_due_date_puts_missing_dates_last(client: TestClient) -> None:
    create_todo(client, title="No date")
    create_todo(client, title="Later", due_date="2026-03-01")
    create_todo(client, title="Sooner", due_date="2026-02-01")

    assert list_titles(client, sort_by="due_date", order="asc") == ["Sooner", "Later", "No date"]


def test_pagination(client: TestClient) -> None:
    for index in range(5):
        create_todo(client, title=f"Task {index}")

    response = client.get("/api/todos", params={"limit": 2, "offset": 2}).json()

    assert response["total"] == 5
    assert len(response["items"]) == 2


def test_stats(client: TestClient) -> None:
    create_todo(client, title="Overdue", due_date="2026-01-01")
    create_todo(client, title="Due today", due_date="2026-01-15")
    done_id = create_todo(client, title="Done")["id"]
    client.patch(f"/api/todos/{done_id}", json={"is_completed": True})

    assert client.get("/api/todos/stats").json() == {
        "total": 3,
        "completed": 1,
        "active": 2,
        "overdue": 1,
        "due_today": 1,
    }
