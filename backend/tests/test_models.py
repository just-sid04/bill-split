def test_zero_sum_invariant(client):
    # Create users
    client.post("/api/v1/users", json={"name": "Alice", "email": "alice@test.com"})
    client.post("/api/v1/users", json={"name": "Bob", "email": "bob@test.com"})

    # Create group with members
    client.post("/api/v1/groups", json={
        "name": "Test Group",
        "description": "Test",
        "member_ids": [1, 2]
    })

    # Create expense with splits
    client.post("/api/v1/expenses", json={
        "group_id": 1,
        "paid_by": 1,
        "description": "Test expense",
        "amount": "100.00",
        "splits": [
            {"user_id": 1, "amount": "50.00"},
            {"user_id": 2, "amount": "50.00"}
        ]
    })

    # Fetch balances
    response = client.get("/api/v1/groups/1/balances")
    data = response.get_json()

    total = sum(float(member["net_balance"]) for member in data["balances"])
    assert round(total, 2) == 0.00