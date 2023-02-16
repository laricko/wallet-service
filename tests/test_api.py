import requests


def assert_balance(user, expected_balance):
    url = f'http://localhost:8000/v1/user/{user["id"]}/balance'
    balance_resp = requests.get(url)
    assert balance_resp.status_code == 200
    assert balance_resp.json()["balance"] == expected_balance


def test_api():
    u = {"name": "petr"}
    user_resp = requests.post("http://localhost:8000/v1/user", data=u)
    assert user_resp.status_code == 201
    user = user_resp.json()
    assert user["id"] > 0
    assert user["name"] == "petr"
    user_id = user["id"]
    assert_balance(user, 0)


    txn = {"type": "DEPOSIT", "amount": 100, "user_id": user_id}
    txn_resp = requests.post("http://localhost:8000/v1/transaction", data=txn)
    assert txn_resp.status_code == 200
    assert_balance(user, 100)

    txn = {"type": "WITHDRAW", "amount": 50, "user_id": user_id}
    txn_resp = requests.post("http://localhost:8000/v1/transaction", data=txn)
    assert txn_resp.status_code == 200
    assert_balance(user, 50)

    txn = {"type": "WITHDRAW", "amount": 60, "user_id": user_id}
    txn_resp = requests.post("http://localhost:8000/v1/transaction", data=txn)
    assert txn_resp.status_code == 400  # insufficient funds
    assert_balance(user, 50)

    txn = {"type": "WITHDRAW", "amount": 10, "user_id": user_id}
    txn_resp = requests.post("http://localhost:8000/v1/transaction", data=txn)
    assert txn_resp.status_code == 200
    assert_balance(user, 40)
