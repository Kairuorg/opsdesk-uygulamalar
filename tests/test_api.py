"""Baseline testleri: ilk dersten önce bunların hepsi GEÇMELİDİR."""


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_incidents_without_filter(client):
    response = client.get("/incidents")
    assert response.status_code == 200
    assert [x["id"] for x in response.json()] == [1042, 1043, 1044]


def test_incident_by_id(client):
    assert client.get("/incidents/1042").json()["severity"] == "critical"
    assert client.get("/incidents/9999").status_code == 404


def test_create_incident(client):
    response = client.post("/incidents", json={"title": "Test incident", "severity": "medium"})
    assert response.status_code == 201
    assert response.json()["status"] == "open"
    assert response.json()["id"] > 0


def test_invalid_incident_payload(client):
    assert client.post("/incidents", json={"title": "Demo", "severity": "urgent"}).status_code == 422


def test_task_creation_and_list(client):
    response = client.post("/tasks", json={"title": "New work", "priority": "high"})
    assert response.status_code == 201
    assert any(t["title"] == "New work" for t in client.get("/tasks").json())


def test_log_list(client):
    response = client.get("/logs")
    assert response.status_code == 200
    assert response.json()[0]["correlation_id"] == "test-001"
