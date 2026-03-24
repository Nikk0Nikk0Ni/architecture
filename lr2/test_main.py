from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_user():
    response = client.post("/users", json={
        "login": "tester", 
        "first_name": "Ivan", 
        "last_name": "Ivanov", 
        "password": "superpassword"
    })
    assert response.status_code == 201
    assert response.json()["login"] == "tester"

def test_create_user_duplicate():
    response = client.post("/users", json={
        "login": "tester", 
        "first_name": "Petr", 
        "last_name": "Petrov", 
        "password": "123"
    })
    assert response.status_code == 400

def test_login_and_get_token():
    response = client.post("/login", data={"username": "tester", "password": "superpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    return response.json()["access_token"]

def test_create_service_unauthorized():
    response = client.post("/services", json={"title": "Уборка", "price": 1500.0})
    assert response.status_code == 401

def test_create_service_authorized():
    token = test_login_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/services", json={"title": "Ремонт ПК", "price": 3000.0}, headers=headers)
    
    assert response.status_code == 201
    assert response.json()["title"] == "Ремонт ПК"
    return response.json()["id"]

def test_create_order():
    token = test_login_and_get_token()
    service_id = test_create_service_authorized()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/orders", json={"service_ids": [service_id]}, headers=headers)
    assert response.status_code == 201
    assert response.json()["user_login"] == "tester"
    assert response.json()["total_price"] == 3000.0