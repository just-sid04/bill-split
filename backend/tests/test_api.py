def test_invalid_settlement_transition(client):
    # Setup
    client.post("/api/v1/users", json={"name": "Alice", "email": "alice@test.com"})
    client.post("/api/v1/users", json={"name": "Bob", "email": "bob@test.com"})
    client.post("/api/v1/groups", json={
        "name": "Test Group",
        "member_ids": [1, 2]
    })

    client.post("/api/v1/expenses", json={
        "group_id": 1,
        "paid_by": 1,
        "description": "Test",
        "amount": "100.00",
        "splits": [
            {"user_id": 1, "amount": "50.00"},
            {"user_id": 2, "amount": "50.00"}
        ]
    })

    # Create settlement
    response = client.post("/api/v1/settlements", json={
        "from_user_id": 2,
        "to_user_id": 1,
        "amount": "50.00"
    })

    settlement_id = response.get_json()["id"]

    # Try completing before confirming - should fail
    invalid = client.post(f"/api/v1/settlements/{settlement_id}/complete")
    assert invalid.status_code == 400
    
    # Confirm first, then complete should work
    client.post(f"/api/v1/settlements/{settlement_id}/confirm")
    valid = client.post(f"/api/v1/settlements/{settlement_id}/complete")
    assert valid.status_code == 200