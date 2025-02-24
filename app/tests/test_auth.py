import asyncio
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
import main
from core.security import create_access_token
import core.config as config
from datetime import timedelta
import pytest

@pytest.fixture(autouse=True)
def setup_function():
    # Save original settings
    org_api_env = config.API_ENV
    org_upload_dir = config.UPLOAD_DIR
    
    # Set test environment
    config.API_ENV = 'test' 
    config.UPLOAD_DIR = '.'
    config.IS_CAMEL_CASE = False
    
    yield  # Run the test
    
    # Restore original settings
    config.API_ENV = org_api_env
    config.UPLOAD_DIR = org_upload_dir

@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    transport = ASGITransport(app=main.create_app())
    async with AsyncClient(base_url="http://test", transport=transport) as ac:
        yield ac

# Test user registration
@pytest.mark.asyncio(loop_scope="session")
async def test_register(async_client):
    response = await async_client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "mobile": "1234567890",
        "password": "admin"
    })
    assert response.status_code == 200
    assert response.json()["data"]["username"] == "testuser"

# Test user login
@pytest.mark.asyncio(loop_scope="session")
async def test_login(async_client):
    response = await async_client.post("/api/auth/login", json={
        "username": "troy.yang2@gmail.com",
        "password": "admin"
    })
    assert response.status_code == 200
    assert "data" in response.json()
    data = response.json()["data"]
    assert "token" in data

# Test successful user info retrieval
@pytest.mark.asyncio(loop_scope="session")
async def test_user_info_success(async_client):
    # Login to get a valid token
    response = await async_client.post("/api/auth/login", json={
        "username": "troy.yang2@gmail.com",
        "password": "admin"
    })
    assert response.status_code == 200
    data = response.json()["data"]
    valid_token = f"Bearer {data['token']}"

    # Retrieve user info
    response = await async_client.post(
        "/api/auth/info",
        headers={"Authorization": valid_token, "Content-Type": "application/json"}
    )
    assert response.status_code == 200
    result = response.json()
    assert "data" in result
    user_info = result["data"]
    assert "id" in user_info
    assert "username" in user_info
    assert "email" in user_info
    assert "mobile" in user_info

# Test missing token
@pytest.mark.asyncio(loop_scope="session")
async def test_user_info_missing_token(async_client):
    response = await async_client.post("/api/auth/info")
    assert response.status_code == 401
    assert response.json()["msg"] == "Token not provided"

# Test invalid token
@pytest.mark.asyncio(loop_scope="session")
async def test_user_info_invalid_token(async_client):
    invalid_token = "Bearer invalid_token"
    response = await async_client.post("/api/auth/info", headers={"Authorization": invalid_token, "Content-Type": "application/json"})
    assert response.status_code == 401
    assert response.json()["msg"] == "Invalid token"

# Test expired token
@pytest.mark.asyncio(loop_scope="session")
async def test_user_info_expired_token(async_client):
    expired_token = create_access_token(data={"userid": 1}, expires_delta=timedelta(seconds=1))
    await asyncio.sleep(2)  # Wait for the token to expire
    expired_token = f"Bearer {expired_token}"
    response = await async_client.post("/api/auth/info", headers={"Authorization": expired_token, "Content-Type": "application/json"})
    assert response.status_code == 401
    assert response.json()["msg"] == "Token has expired"

# Test user not found
@pytest.mark.asyncio(loop_scope="session")
async def test_user_info_user_not_found(async_client):
    non_existent_token = create_access_token(data={"userid": -1})
    non_existent_token = f"Bearer {non_existent_token}"
    response = await async_client.post("/api/auth/info", headers={"Authorization": non_existent_token, "Content-Type": "application/json"})
    assert response.status_code == 401
    assert response.json()["msg"] == "User not found"

# Test token without Bearer prefix
@pytest.mark.asyncio(loop_scope="session")
async def test_user_info_token_without_bearer(async_client):
    token_without_bearer = create_access_token(data={"userid": 1})
    response = await async_client.post("/api/auth/info", headers={"Authorization": token_without_bearer, "Content-Type": "application/json"})
    assert response.status_code == 401
    assert response.json()["msg"] == "Token not provided"

# Test token without userid in payload
@pytest.mark.asyncio(loop_scope="session")
async def test_user_info_token_without_userid(async_client):
    token_without_userid = create_access_token(data={"username": "troy.yang2@gmail.com"})
    token_without_userid = f"Bearer {token_without_userid}"
    response = await async_client.post("/api/auth/info", headers={"Authorization": token_without_userid, "Content-Type": "application/json"})
    assert response.status_code == 401
    assert response.json()["msg"] == "Userid not found in token"

@pytest.mark.asyncio(loop_scope="session")
async def test_update_user_info_success(async_client):
    # Login to get a valid token
    response = await async_client.post("/api/auth/login", json={
        "username": "troy.yang2@gmail.com",
        "password": "admin"
    })
    assert response.status_code == 200
    data = response.json()["data"]
    valid_token = f"Bearer {data['token']}"

    # Retrieve user info
    response = await async_client.put(
        "/api/auth/update",
        headers={"Authorization": valid_token, "Content-Type": "application/json"},
        json={
            "id": 1,
            "username": "testuser",
            "email": "testuser@example.com",
            "mobile": "112233",
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert "data" in result
    user_info = result["data"]
    assert user_info.get("username") == "testuser"
    assert user_info.get("email") == "testuser@example.com"
    assert user_info.get("mobile") == "112233"


@pytest.mark.asyncio(loop_scope="session")
async def test_update_user_password_success(async_client):
    # Login to get a valid token
    response = await async_client.post("/api/auth/login", json={
        "username": "troy.yang2@gmail.com",
        "password": "admin"
    })
    assert response.status_code == 200
    data = response.json()["data"]
    valid_token = f"Bearer {data['token']}"

    # Retrieve user info
    response = await async_client.put(
        "/api/auth/update/password",
        headers={"Authorization": valid_token, "Content-Type": "application/json"},
        json={
            "id": 1,
            "org_password": "admin",
            "new_password": "123456",
            "confirm_password": "123456",
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert "data" in result
    user_info = result["data"]
    assert user_info.get("username") == "admin"
    assert user_info.get("email") == "troy.yang2@gmail.com"