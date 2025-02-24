import pytest_asyncio
from httpx import AsyncClient, ASGITransport
import main
import core.config as config
import pytest
from services.user_service import UserService
from core.security import hash_password_md5

@pytest.fixture(autouse=True)
def setup_function(monkeypatch) -> None:
    monkeypatch.setattr(config, 'API_ENV', 'test')
    monkeypatch.setattr(config, 'UPLOAD_DIR', '.')
    monkeypatch.setattr(config, 'IS_CAMEL_CASE', False)
    yield

@pytest.fixture(scope="module")
def user_service() -> UserService:
    return UserService()

@pytest_asyncio.fixture(scope="module")
async def client():
    config.API_ENV = 'test' 
    config.UPLOAD_DIR = '.'
    config.IS_CAMEL_CASE = False
    transport = ASGITransport(app=main.create_app())
    async with AsyncClient(base_url="http://test", transport=transport) as ac:
        yield ac

@pytest_asyncio.fixture(scope="module")
async def setup_test_data(
    client: AsyncClient,
) -> str:
    response = await client.post("/api/auth/login", json={
        "username": "troy.yang2@gmail.com",
        "password": "admin"
    })
    assert response.status_code == 200
    data = response.json()["data"]
    valid_token = f"Bearer {data['token']}"

    yield valid_token

# Test successful user info retrieval
@pytest.mark.asyncio(loop_scope="session")
async def test_user_list_success(client: AsyncClient, setup_test_data: str):
    valid_token = setup_test_data
    # Retrieve user info
    response = await client.post(
        "/api/user/list",
        headers={"Authorization": valid_token, "Content-Type": "application/json"},
        json={
            "keyword": "troy.yang2@gmail.com",
            "role": "ADMIN",
            "page": 1,
            "page_size": 10
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert "data" in result
    data = result["data"]
    assert isinstance(data, dict)
    assert data.get("total") > 0
    users = data.get("list")
    assert isinstance(users, list)
    assert len(users) > 0


@pytest.mark.asyncio(loop_scope="session")
async def test_user_update_success(client: AsyncClient, setup_test_data: str, user_service: UserService):
    valid_token = setup_test_data
    # Retrieve user info
    response = await client.put(
        "/api/user",
        headers={"Authorization": valid_token, "Content-Type": "application/json"},
        json={
            "id": 1,
            "username": "admin",
            "email": "troy.yang@gmail.com",
            "mobile": "1234567890",
            "password": "newpassword",
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert "data" in result
    user = result["data"]
    assert user.get("mobile") == "1234567890"
    assert user.get("password")== None

@pytest.mark.asyncio(loop_scope="session")
async def test_user_update_invalid_id(client: AsyncClient, setup_test_data: str, user_service: UserService):
    valid_token = setup_test_data
    # Retrieve user info
    response = await client.put(
        "/api/user",
        headers={"Authorization": valid_token, "Content-Type": "application/json"},
        json={
            "id": -1,
            "username": "admin",
            "email": "troy.yang@gmail.com",
            "mobile": "1234567890",
            "password": "newpassword",
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert result.get("code") == -1
    assert result.get("msg") == "User not found."


@pytest.mark.asyncio(loop_scope="session")
async def test_user_save_success(client: AsyncClient, setup_test_data: str, user_service: UserService):
    valid_token = setup_test_data
    # Retrieve user info
    response = await client.put(
        "/api/user",
        headers={"Authorization": valid_token, "Content-Type": "application/json"},
        json={
            "username": "troy.yang",
            "email": "max@gmail.com",
            "mobile": "230-341-382",
            "password": "112233",
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert "data" in result
    user = result["data"]
    assert user.get("mobile") == "230-341-382"
    assert user.get("password")== None


@pytest.mark.asyncio(loop_scope="session")
async def test_user_save_duplicate(client: AsyncClient, setup_test_data: str, user_service: UserService):
    valid_token = setup_test_data
    # Retrieve user info
    response = await client.put(
        "/api/user",
        headers={"Authorization": valid_token, "Content-Type": "application/json"},
        json={
            "username": "admin",
            "email": "max@gmail.com",
            "mobile": "230-341-382",
            "password": "112233",
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert result.get("code") == -1
    assert result.get("msg") == "Username already registered"


@pytest.mark.asyncio(loop_scope="session")
async def test_user_delete_success(client: AsyncClient, setup_test_data: str, user_service: UserService):
    valid_token = setup_test_data
    # Retrieve user info
    response = await client.delete(
        "/api/user/1",
        headers={"Authorization": valid_token, "Content-Type": "application/json"}
    )
    assert response.status_code == 200
    result = response.json()
    assert "data" in result
    user = result["data"]
    assert user.get("success") == True

@pytest.mark.asyncio(loop_scope="session")
async def test_user_delete_invalid_id(client: AsyncClient, setup_test_data: str, user_service: UserService):
    valid_token = setup_test_data
    # Retrieve user info
    response = await client.delete(
        "/api/user/-1",
        headers={"Authorization": valid_token, "Content-Type": "application/json"}
    )
    assert response.status_code == 200
    result = response.json()
    assert "data" in result
    assert result.get("code") == -1
    assert result.get("msg") == "User not found."