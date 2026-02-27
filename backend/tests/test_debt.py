def test_debt_simplification(client):
    # Create users
    client.post("/api/v1/users", json={"name": "Alice", "email": "alice@test.com"})
    client.post("/api/v1/users", json={"name": "Bob", "email": "bob@test.com"})
    client.post("/api/v1/users", json={"name": "Charlie", "email": "charlie@test.com"})

    # Create group
    client.post("/api/v1/groups", json={
        "name": "Trip",
        "description": "Vacation",
        "member_ids": [1, 2, 3]
    })

    # Create expense
    client.post("/api/v1/expenses", json={
        "group_id": 1,
        "paid_by": 1,
        "description": "Dinner",
        "amount": "90.00",
        "splits": [
            {"user_id": 1, "amount": "30.00"},
            {"user_id": 2, "amount": "30.00"},
            {"user_id": 3, "amount": "30.00"}
        ]
    })

    response = client.get("/api/v1/groups/1/balances")
    data = response.get_json()

    debts = data["simplified_debts"]
    
    # Verify: 2 debts (Bob pays Alice, Charlie pays Alice)
    assert len(debts) == 2
    assert debts[0]["from_user_id"] in [2, 3]
    assert debts[0]["to_user_id"] == 1