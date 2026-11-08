from fastapi.testclient import TestClient


def test_create_and_list_tags(client: TestClient) -> None:
    client.post("/api/tags", json={"name": "work", "color": "#ff0000"})
    client.post("/api/tags", json={"name": "home"})

    response = client.get("/api/tags")

    assert response.status_code == 200
    assert [tag["name"] for tag in response.json()] == ["home", "work"]


def test_create_duplicate_tag_returns_conflict(client: TestClient) -> None:
    client.post("/api/tags", json={"name": "work"})

    response = client.post("/api/tags", json={"name": "work"})

    assert response.status_code == 409


def test_create_tag_rejects_invalid_color(client: TestClient) -> None:
    response = client.post("/api/tags", json={"name": "work", "color": "red"})

    assert response.status_code == 422


def test_update_tag(client: TestClient) -> None:
    tag_id = client.post("/api/tags", json={"name": "work"}).json()["id"]

    response = client.patch(f"/api/tags/{tag_id}", json={"name": "office", "color": "#00ff00"})

    assert response.status_code == 200
    assert response.json() == {"id": tag_id, "name": "office", "color": "#00ff00"}


def test_delete_tag_detaches_it_from_todos(client: TestClient) -> None:
    tag_id = client.post("/api/tags", json={"name": "work"}).json()["id"]
    todo_id = client.post("/api/todos", json={"title": "Report", "tag_ids": [tag_id]}).json()["id"]

    assert client.delete(f"/api/tags/{tag_id}").status_code == 204
    assert client.get(f"/api/todos/{todo_id}").json()["tags"] == []


def test_delete_missing_tag_returns_not_found(client: TestClient) -> None:
    assert client.delete("/api/tags/999").status_code == 404
