"""OPS-101 kabul testleri. Değiştirilmemiş başlangıç kodunda KALMASI BEKLENİR.

Özellik yazıldıktan sonra bu testlerin hepsi geçmelidir. Beklentileri gevşetme.
"""
import pytest

pytestmark = pytest.mark.ops101


def test_filter_critical(client):
    response = client.get("/incidents?severity=critical")
    assert response.status_code == 200
    assert [i["id"] for i in response.json()] == [1042]


def test_filter_high(client):
    response = client.get("/incidents?severity=high")
    assert response.status_code == 200
    assert [i["id"] for i in response.json()] == [1043]


def test_filter_without_matches(client):
    response = client.get("/incidents?severity=medium")
    assert response.status_code == 200
    assert response.json() == []


def test_invalid_severity_returns_422(client):
    assert client.get("/incidents?severity=urgent").status_code == 422


def test_no_filter_preserves_existing_behavior(client):
    response = client.get("/incidents")
    assert response.status_code == 200
    assert len(response.json()) == 3
