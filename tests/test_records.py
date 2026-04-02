def test_analyst_can_create_record(client, analyst_headers, sample_record_payload):
    r = client.post("/records", headers=analyst_headers, json=sample_record_payload)
    assert r.status_code == 201
    data = r.json()
    assert data["amount"] == 5000.00
    assert data["record_type"] == "income"
    assert data["category"] == "salary"


def test_admin_can_create_record(client, admin_headers, sample_record_payload):
    r = client.post("/records", headers=admin_headers, json=sample_record_payload)
    assert r.status_code == 201


def test_viewer_cannot_create_record(client, viewer_headers, sample_record_payload):
    r = client.post("/records", headers=viewer_headers, json=sample_record_payload)
    assert r.status_code == 403


def test_all_roles_can_list_records(client, admin_headers, viewer_headers, analyst_headers):
    for headers in [admin_headers, viewer_headers, analyst_headers]:
        r = client.get("/records", headers=headers)
        assert r.status_code == 200


def test_zero_amount_rejected(client, analyst_headers):
    r = client.post(
        "/records",
        headers=analyst_headers,
        json={
            "amount": 0,
            "record_type": "income",
            "category": "salary",
            "record_date": "2024-01-01",
        },
    )
    assert r.status_code == 422


def test_negative_amount_rejected(client, analyst_headers):
    r = client.post(
        "/records",
        headers=analyst_headers,
        json={
            "amount": -100,
            "record_type": "expense",
            "category": "food",
            "record_date": "2024-01-01",
        },
    )
    assert r.status_code == 422


def test_invalid_category_rejected(client, analyst_headers):
    r = client.post(
        "/records",
        headers=analyst_headers,
        json={
            "amount": 100,
            "record_type": "income",
            "category": "not_a_real_category",
            "record_date": "2024-01-01",
        },
    )
    assert r.status_code == 422


def test_filter_by_type(client, admin_headers):
    client.post(
        "/records",
        headers=admin_headers,
        json={"amount": 1000, "record_type": "income", "category": "salary", "record_date": "2024-01-01"},
    )
    client.post(
        "/records",
        headers=admin_headers,
        json={"amount": 200, "record_type": "expense", "category": "food", "record_date": "2024-01-02"},
    )

    r = client.get("/records?record_type=income", headers=admin_headers)
    assert r.status_code == 200
    items = r.json()["items"]
    assert all(item["record_type"] == "income" for item in items)


def test_filter_by_date_range(client, admin_headers):
    client.post(
        "/records",
        headers=admin_headers,
        json={"amount": 500, "record_type": "income", "category": "freelance", "record_date": "2024-01-10"},
    )
    client.post(
        "/records",
        headers=admin_headers,
        json={"amount": 300, "record_type": "expense", "category": "food", "record_date": "2024-03-15"},
    )

    r = client.get("/records?date_from=2024-01-01&date_to=2024-01-31", headers=admin_headers)
    assert r.status_code == 200
    items = r.json()["items"]
    assert all(item["record_date"] >= "2024-01-01" for item in items)
    assert all(item["record_date"] <= "2024-01-31" for item in items)


def test_pagination(client, admin_headers):
    for i in range(5):
        client.post(
            "/records",
            headers=admin_headers,
            json={"amount": 100 + i, "record_type": "expense", "category": "food", "record_date": "2024-01-01"},
        )

    r = client.get("/records?page=1&page_size=2", headers=admin_headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 2
    assert data["total"] >= 5


def test_update_own_record(client, analyst_headers, sample_record_payload):
    r = client.post("/records", headers=analyst_headers, json=sample_record_payload)
    record_id = r.json()["id"]

    r = client.patch(
        f"/records/{record_id}",
        headers=analyst_headers,
        json={"amount": 6000.00, "description": "Updated"},
    )
    assert r.status_code == 200
    assert r.json()["amount"] == 6000.00


def test_analyst_cannot_update_others_record(client, admin_headers, analyst_headers, sample_record_payload):
    # Admin creates a record
    r = client.post("/records", headers=admin_headers, json=sample_record_payload)
    record_id = r.json()["id"]

    # Analyst tries to update it
    r = client.patch(
        f"/records/{record_id}",
        headers=analyst_headers,
        json={"amount": 9999},
    )
    assert r.status_code == 403


def test_admin_can_update_any_record(client, analyst_headers, admin_headers, sample_record_payload):
    r = client.post("/records", headers=analyst_headers, json=sample_record_payload)
    record_id = r.json()["id"]

    r = client.patch(
        f"/records/{record_id}",
        headers=admin_headers,
        json={"description": "Admin override"},
    )
    assert r.status_code == 200


def test_soft_delete_record(client, admin_headers, sample_record_payload):
    r = client.post("/records", headers=admin_headers, json=sample_record_payload)
    record_id = r.json()["id"]

    r = client.delete(f"/records/{record_id}", headers=admin_headers)
    assert r.status_code == 204

    # Deleted record should return 404
    r = client.get(f"/records/{record_id}", headers=admin_headers)
    assert r.status_code == 404


def test_get_nonexistent_record(client, admin_headers):
    r = client.get("/records/99999", headers=admin_headers)
    assert r.status_code == 404