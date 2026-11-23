"""OPS-101 için referans testler: kabul testlerinin sınamadığı kriterler.

Uygulama 1.1, Aşama 4'te kullanılır. Dosya adı "test_" ile başlamadığı için
`pytest -q` bu testleri çalıştırmaz; açıkça çağrılmaları gerekir:

    pytest -q tests/referans_ops101.py

Hikâyeye uyan bir uygulamada beşi de geçer.
"""


def ids(response):
    return [i["id"] for i in response.json()]


def test_low_is_a_supported_value(client):
    response = client.get("/incidents?severity=low")
    assert response.status_code == 200
    assert ids(response) == [1044]


def test_filtered_results_are_in_ascending_id_order(client):
    first = client.post("/incidents", json={"title": "Ikinci kritik", "severity": "critical"}).json()["id"]
    second = client.post("/incidents", json={"title": "Ucuncu kritik", "severity": "critical"}).json()["id"]

    response = client.get("/incidents?severity=critical")

    assert ids(response) == [1042, first, second]
    assert first < second


def test_value_with_different_case_is_rejected(client):
    assert client.get("/incidents?severity=Critical").status_code == 422


def test_invalid_value_returns_the_standard_validation_body(client):
    response = client.get("/incidents?severity=urgent")
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert detail[0]["loc"] == ["query", "severity"]


def test_empty_value_is_rejected(client):
    assert client.get("/incidents?severity=").status_code == 422
