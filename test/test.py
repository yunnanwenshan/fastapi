from starlette.testclient import TestClient
from app.main import app
from app.db.models import CreateUserModel, UpdateUserModel, UserResponse
import json
import uuid
import pytest
import os
import shutil

client = TestClient(app)


def test_read_main():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'message': 'Fast API in Python'}


def backup_users_json():
    """Create a backup of users.json file for tests"""
    if os.path.exists('data/users.json'):
        shutil.copyfile('data/users.json', 'data/users.json.bak')


def restore_users_json():
    """Restore the original users.json file after tests"""
    if os.path.exists('data/users.json.bak'):
        shutil.copyfile('data/users.json.bak', 'data/users.json')
        os.remove('data/users.json.bak')


@pytest.fixture(autouse=True)
def setup_teardown():
    """Fixture to handle setup and teardown for each test"""
    backup_users_json()
    yield
    restore_users_json()


def test_read_user():
    response = client.get('/users')
    assert response.status_code == 200
    assert len(response.json()) != 0


def test_create_user():
    user_data = {
        "name": "Test User",
        "mail": "test@example.com",
        "phone": "1234567890",
        "password": "securepassword123"
    }
    
    response = client.post('/users', json=user_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == "Test User"
    assert data["mail"] == "test@example.com"
    assert data["phone"] == "1234567890"
    assert "password_hash" not in data
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    
    # Verify user was actually created
    user_id = data["id"]
    get_response = client.get(f'/users/{user_id}')
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Test User"


def test_create_user_duplicate_email():
    # Create first user
    user_data = {
        "name": "First User",
        "mail": "duplicate@example.com",
        "phone": "1234567890",
        "password": "securepassword123"
    }
    response = client.post('/users', json=user_data)
    assert response.status_code == 201
    
    # Try to create second user with same email
    user_data2 = {
        "name": "Second User",
        "mail": "duplicate@example.com",
        "phone": "0987654321",
        "password": "anotherpassword456"
    }
    response2 = client.post('/users', json=user_data2)
    assert response2.status_code == 400
    assert "Email already registered" in response2.json()["detail"]


def test_get_users():
    # Create some test users first
    user1 = {
        "name": "John Doe",
        "mail": "john@example.com",
        "phone": "1111111111",
        "password": "password1"
    }
    user2 = {
        "name": "Jane Smith",
        "mail": "jane@example.com",
        "phone": "2222222222",
        "password": "password2"
    }
    
    client.post('/users', json=user1)
    client.post('/users', json=user2)
    
    # Test all users retrieval
    response = client.get('/users')
    assert response.status_code == 200
    users = response.json()
    assert len(users) >= 2  # At least our 2 new users plus any existing ones
    
    # Test pagination
    response = client.get('/users?skip=0&limit=1')
    assert response.status_code == 200
    assert len(response.json()) == 1
    
    # Test name filtering
    response = client.get('/users?name=John')
    assert response.status_code == 200
    filtered_users = response.json()
    assert any(user["name"] == "John Doe" for user in filtered_users)
    assert not any(user["name"] == "Jane Smith" for user in filtered_users)
    
    # Test email filtering
    response = client.get('/users?mail=jane')
    assert response.status_code == 200
    filtered_users = response.json()
    assert any(user["mail"] == "jane@example.com" for user in filtered_users)
    assert not any(user["mail"] == "john@example.com" for user in filtered_users)


def test_get_user_by_id():
    # Create a test user
    user_data = {
        "name": "Get User Test",
        "mail": "getuser@example.com",
        "phone": "3333333333",
        "password": "userpassword"
    }
    
    create_response = client.post('/users', json=user_data)
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]
    
    # Get the user by ID
    response = client.get(f'/users/{user_id}')
    assert response.status_code == 200
    user = response.json()
    assert user["name"] == "Get User Test"
    assert user["mail"] == "getuser@example.com"
    assert user["phone"] == "3333333333"
    assert "password_hash" not in user


def test_get_user_not_found():
    # Use a UUID that shouldn't exist
    fake_id = str(uuid.uuid4())
    response = client.get(f'/users/{fake_id}')
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


def test_update_user():
    # Create a test user
    user_data = {
        "name": "Update Test",
        "mail": "update@example.com",
        "phone": "4444444444",
        "password": "updatepassword"
    }
    
    create_response = client.post('/users', json=user_data)
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]
    
    # Update the user
    update_data = {
        "name": "Updated Name",
        "phone": "5555555555"
    }
    
    update_response = client.put(f'/users/{user_id}', json=update_data)
    assert update_response.status_code == 200
    updated_user = update_response.json()
    assert updated_user["name"] == "Updated Name"
    assert updated_user["mail"] == "update@example.com"  # Unchanged
    assert updated_user["phone"] == "5555555555"  # Changed
    
    # Verify the update persisted
    get_response = client.get(f'/users/{user_id}')
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Updated Name"


def test_update_nonexistent_user():
    fake_id = str(uuid.uuid4())
    update_data = {"name": "This Won't Work"}
    
    response = client.put(f'/users/{fake_id}', json=update_data)
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


def test_update_user_duplicate_email():
    # Create two users
    user1 = {
        "name": "First Update User",
        "mail": "first@example.com",
        "phone": "6666666666",
        "password": "firstpass"
    }
    
    user2 = {
        "name": "Second Update User",
        "mail": "second@example.com",
        "phone": "7777777777",
        "password": "secondpass"
    }
    
    response1 = client.post('/users', json=user1)
    response2 = client.post('/users', json=user2)
    assert response1.status_code == 201
    assert response2.status_code == 201
    
    user2_id = response2.json()["id"]
    
    # Try to update second user with first user's email
    update_data = {"mail": "first@example.com"}
    response = client.put(f'/users/{user2_id}', json=update_data)
    
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_delete_user():
    # Create a test user
    user_data = {
        "name": "Delete Test",
        "mail": "delete@example.com",
        "phone": "8888888888",
        "password": "deletepass"
    }
    
    create_response = client.post('/users', json=user_data)
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]
    
    # Delete the user
    delete_response = client.delete(f'/users/{user_id}')
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "User deleted successfully"
    
    # Verify the user is gone
    get_response = client.get(f'/users/{user_id}')
    assert get_response.status_code == 404


def test_delete_nonexistent_user():
    fake_id = str(uuid.uuid4())
    response = client.delete(f'/users/{fake_id}')
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


def test_read_question():
    response = client.get('/question/1')
    assert response.status_code == 200
    assert response.json()['position'] == 1


def test_read_question_invalid():
    response = client.get('/question/0')
    assert response.status_code == 400
    assert response.json() == {'detail': 'Error'}


def test_read_alternatives():
    response = client.get('/alternatives/1')
    assert response.status_code == 200
    assert response.json()[1]['question_id'] == 1


def test_create_answer():
    body = {"user_id": 1, "answers": [{"question_id": 1, "alternative_id": 2}, {
        "question_id": 2, "alternative_id": 2}, {"question_id": 2, "alternative_id": 2}]}
    body = json.dumps(body)
    response = client.post('/answer', data=body)
    assert response.status_code == 201


def test_read_result():
    response = client.get('/result/1')
    assert response.status_code == 200

def test_read_result1():
    response = client.get('/result/1')
    assert response.status_code == 200