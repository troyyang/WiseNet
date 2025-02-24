from fastapi.testclient import TestClient
import main

client = TestClient(main.create_app())

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to FastAPI!"}
