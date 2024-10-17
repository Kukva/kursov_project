import requests
from datetime import datetime

BASE_URL = "http://app:8080"
test_data = {
  "fixed_acidity": 7.4,
  "volatile_acidity": 0.7,
  "citric_acid": 0.0,
  "residual_sugar": 1.9,
  "chlorides": 0.076,
  "free_sulfur_dioxide": 11.0,
  "total_sulfur_dioxide": 34.0,
  "density": 0.9978,
  "pH": 3.51,
  "sulphates": 0.56,
  "alcohol": 9.4
}

def test_home_request():
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "text/html" in response.headers["Content-Type"]

def test_signup():
    response = requests.post(f"{BASE_URL}/user/signup", params={
    "username": "testuser",
    "password": "password123",
    "email": "testuser@example.com",
    "is_admin": False
    }, headers={
        "Content-Type": "application/json"
    })
    print(response.status_code)
    print(response.json())

    assert response.status_code == 200
    assert response.json() == {"message": "User successfully registered!",
                               "user_id": 1}

def test_signup_user_exists():
    requests.post(f"{BASE_URL}/user/signup", params={
        "username": "testadmin",
        "password": "password1231",
        "email": "testadmin@example.com",
        "is_admin": True
    })
    response = requests.post(f"{BASE_URL}/user/signup", params={
        "username": "testadmin",
        "password": "password1231",
        "email": "testadmin@example.com",
        "is_admin": True
    })
    assert response.status_code == 409
    assert response.json() in [
        {"detail": "User with supplied username exists"},
        {"detail": "User with supplied email exists"}
    ]

def test_add_credits():
    # Создайте пользователя
    user_response = requests.post(f"{BASE_URL}/user/signin", params={
        "password": "password123",
        "email": "testuser@example.com",
    })
    user_id = user_response.json().get('user_id')

    response = requests.post(f"{BASE_URL}/user/add_credits/{user_id}", params={"amount": 100})
    assert response.status_code == 200
    assert response.json() == {f"Added to {user_id} user": "100 credits"}

    balance_response = requests.get(f"{BASE_URL}/user/balance/{user_id}")
    assert balance_response.status_code == 200
    assert balance_response.json().get(str(user_id)) == 100

def test_show_balance_no_user():
    response = requests.get(f"{BASE_URL}/user/balance/9999")
    assert response.status_code == 404

def test_process_request():
    user_response = requests.post(f"{BASE_URL}/user/signin", params={
        "password": "password123",
        "email": "testuser@example.com",
    })
    user_id = user_response.json().get('user_id')  # Предполагается, что ID пользователя возвращается

    assert user_id is not None, "User ID is missing from the response"

    # Создайте запрос на обработку
    response = requests.post(f"{BASE_URL}/ml/process_request/{int(user_id)}", json=test_data,
                             headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    assert response.json().get('prediction') == "made successfully"