import requests
from datetime import datetime

BASE_URL = "http://localhost:8080"
test_data = {
    "project_name": "Innovative Smartwatch",
    "category": "Wearable Technology",
    "created_date": "2023-06-01",  # Дата создания проекта
    "launch_date": "2023-06-10",   # Дата запуска кампании
    "deadline_date": "2023-07-10", # Дата завершения кампании
    "goal_amount": 50000.00,       # Целевая сумма для сбора
    "staff_pick": 1,               # Признак выбора командой (0 - нет, 1 - да)
    "num_projects_created": 2,     # Количество проектов, созданных создателем
    "num_projects_backed": 5,      # Количество поддержанных создателем проектов
    "project_description": "A next-generation smartwatch with health monitoring features and seamless integration with other devices.",
    "creator_description": "A tech enthusiast with a background in developing wearable technology. Previously successfully launched two crowdfunding campaigns."
}

def test_home_request():
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "text/html" in response.headers["Content-Type"]

def test_signup():
    response = requests.post(f"{BASE_URL}/user/signup", params={
    "username": "test",
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
        "user_type": "startup"
    })
    response = requests.post(f"{BASE_URL}/user/signup", params={
        "username": "testadmin",
        "password": "password1231",
        "email": "testadmin@example.com",
        "user_type": "startup"
    })
    assert response.status_code == 409
    assert response.json() in [
        {"detail": "User with supplied username exists"},
        {"detail": "User with supplied email exists"}
    ]


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