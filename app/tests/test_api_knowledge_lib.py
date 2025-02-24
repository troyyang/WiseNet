import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient
from httpx import ASGITransport

import core.config as config
import core.database as db
import main
from graph import RelationshipType
from graph.graph_query import KnowledgeGraphQuery
from graph.node import Node
from graph.relationship import Relationship
from services.knowledge_lib_service import KnowledgeLibService

@pytest.fixture(autouse=True)
def setup_function():
    org_api_env = config.API_ENV
    org_upload_dir = config.UPLOAD_DIR
    config.API_ENV = 'test' 
    config.UPLOAD_DIR = '.'
    config.IS_CAMEL_CASE = False
    yield
    config.API_ENV = org_api_env
    config.UPLOAD_DIR = org_upload_dir

@pytest.fixture(scope="module")
def knowledge_lib_service() -> KnowledgeLibService:
    return KnowledgeLibService()
    
@pytest_asyncio.fixture
async def client() -> AsyncClient:
    config.IS_CAMEL_CASE = False
    transport = ASGITransport(app=main.create_app())
    async with AsyncClient(base_url="http://test", transport=transport) as ac:
        yield ac

@pytest_asyncio.fixture
async def setup_test_node(client: AsyncClient):
    knowledge_graph_query = KnowledgeGraphQuery()
    lib_id = 1
    knowledge_graph_query.delete_graph_by_lib(lib_id)
    subject_id = 1
    response = await client.post("/api/auth/login", json={
        "username": "troy.yang2@gmail.com",
        "password": "admin"
    })
    assert response.status_code == 200
    data = response.json()["data"]
    valid_token = f"Bearer {data['token']}"
    yield lib_id, subject_id, valid_token
    knowledge_graph_query.delete_graph_by_lib(lib_id)

@pytest.mark.asyncio(loop_scope="session")
class TestKnowledgeLib:
    async def test_read_knowledge_lib_valid_id(self, client: AsyncClient, setup_test_node: tuple[Node, int, int, str]):
        lib_id, subject_id, valid_token = setup_test_node
        knowledge_id = 1
        response = await client.get(f'/api/knowledge/lib/{knowledge_id}', headers={"Authorization": valid_token})
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert "id" in data
        assert "title" in data
        assert "content" in data
        assert "create_time" in data
        assert "update_time" in data
        assert data["title"] == "Logistics and transportation"
        assert data["content"] is not None

    async def test_read_knowledge_lib_invalid_id(self, client: AsyncClient, setup_test_node: tuple[Node, int, int, str]):
        lib_id, subject_id, valid_token = setup_test_node
        knowledge_id = -1
        response = await client.get(f'/api/knowledge/lib/{knowledge_id}', headers={"Authorization": valid_token})
        assert response.status_code == 200
        assert response.json() == {'code': -1, 'data': None, 'msg': 'Knowledge lib not found', 'status_code': 404}

    async def test_find_knowledge_libs_by_condition_valid(self, client: AsyncClient, setup_test_node: tuple[Node, int, int, str]):
        lib_id, subject_id, valid_token = setup_test_node
        condition = {'keyword': 'Logistics and transportation'}
        response = await client.post("/api/knowledge/lib/find", json=condition, headers={"Authorization": valid_token})
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, list)
        assert len(data) > 0

    async def test_find_knowledge_libs_by_condition_edge_case(self, client: AsyncClient, setup_test_node: tuple[Node, int, int, str]):
        lib_id, subject_id, valid_token = setup_test_node
        response = await client.post("/api/knowledge/lib/find", headers={"Authorization": valid_token}, json={})  # No condition
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, list)
        assert len(data) > 0

    async def test_find_knowledge_libs_by_condition_no_results(self, client: AsyncClient, setup_test_node: tuple[Node, int, int, str]):
        lib_id, subject_id, valid_token = setup_test_node
        condition = {'keyword': 'Nonexistent Title'}
        response = await client.post("/api/knowledge/lib/find", headers={"Authorization": valid_token}, json=condition)
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, list)
        assert len(data) == 0

    async def test_update_knowledge_lib_success(self, client: AsyncClient, setup_test_node: tuple[Node, int, int, str]):
        lib_id, subject_id, valid_token = setup_test_node
        response = await client.put("/api/knowledge/lib", headers={"Authorization": valid_token}, json={"id": lib_id, "title": "Updated Title", "content": "Updated Content"})
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert data["title"] == "Updated Title"
        assert data["content"] is not None

    async def test_update_knowledge_lib_not_found(self, client: AsyncClient, setup_test_node: tuple[Node, int, int, str]):
        lib_id, subject_id, valid_token = setup_test_node
        response = await client.put("/api/knowledge/lib", headers={"Authorization": valid_token}, json={"id": -1, "title": "Non-existent Title", "content": "Content"})
        assert response.status_code == 200
        assert response.json() == {'code': -1, 'data': None, 'msg': 'Knowledge not found'}

    async def test_publish_knowledge_lib_success(self, client: AsyncClient, setup_test_node: tuple[Node, int, int, str]):
        lib_id, subject_id, valid_token = setup_test_node
        response = await client.get(f"/api/knowledge/lib/publish/{lib_id}", headers={"Authorization": valid_token})
        assert response.status_code == 200
        result = response.json()
        data = result["data"]
        assert data["status"] == "PUBLISHED"

    async def test_publish_knowledge_lib_not_found(self, client: AsyncClient, setup_test_node: tuple[Node, int, int, str]):
        lib_id, subject_id, valid_token = setup_test_node
        response = await client.get(f"/api/knowledge/lib/publish/-1", headers={"Authorization": valid_token})
        assert response.status_code == 200
        assert response.json() == {'code': -1, 'data': None, 'msg': 'Knowledge library not found.'}

    async def test_publish_knowledge_lib_generating_error(self, client: AsyncClient, setup_test_node: tuple[Node, int, int, str], knowledge_lib_service: KnowledgeLibService):
        lib_id, subject_id, valid_token = setup_test_node
        config.API_ENV = 'dev'
        await knowledge_lib_service.update_knowledge_lib_status(3, "GENERATING")
        response = await client.get(f"/api/knowledge/lib/publish/3", headers={"Authorization": valid_token})
        assert response.status_code == 200
        print(response.json())
        assert response.json() == {'code': -1, 'data': None, 'msg': 'Cannot toggle publish status while generating or analyzing.'}

        # clean up
        await knowledge_lib_service.update_knowledge_lib_status(3, "PENDING")
        config.API_ENV = 'test'   

    async def test_search_knowledge_libs(self, client: AsyncClient, knowledge_lib_service: KnowledgeLibService, setup_test_node: tuple[Node, int, int, str]):
        lib_id, subject_id, valid_token = setup_test_node
        config.API_ENV = 'dev'
        await knowledge_lib_service.update_knowledge_lib_status(3, "PUBLISHED")
        response = await client.post("/api/knowledge/lib/search", headers={"Authorization": valid_token}, json={})
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, list)
        assert len(data) > 0

        # clean up
        config.API_ENV = 'dev'
        await knowledge_lib_service.update_knowledge_lib_status(3, "PENDING")
        config.API_ENV = 'test'   

    async def test_delete_knowledge_lib_not_found(self, client: AsyncClient, setup_test_node: tuple[Node, int, int, str]):
        lib_id, subject_id, valid_token = setup_test_node
        response = await client.delete(f"/api/knowledge/lib/-13", headers={"Authorization": valid_token})
        assert response.status_code == 200
        assert response.json() == {'code': -1, 'data': None, 'msg': 'Knowledge not found'}

    # async def test_delete_knowledge_lib_success(self, client: AsyncClient):
    #     # Arrange
    #     new_entry = KnowledgeLib(
    #         title=knowledge_data.title,
    #         content=knowledge_data.content,
    #         create_time=datetime.datetime.now(),
    #         update_time=datetime.datetime.now()
    #     )
    #     db.session.add(new_entry)
    #     db.session.commit()
    #     db.session.refresh(new_entry)

    #     knowledge_graph_query = KnowledgeGraphQuery()
    #     lib_id = new_entry.id
    #     subject_id = -13
    #     parent_node = await Node.add_subject_node(lib_id, subject_id, "Parent Node", 1)
    #     child_node = await Node.add_prompt_node(lib_id, subject_id, "Child Node", 1)
    #     relationship = await Relationship.add_relationship(lib_id, subject_id, parent_node.element_id, child_node.element_id, RelationshipType.HAS_CHILD)

    #     # Assuming there's an existing knowledge item with ID 1
    #     response = await client.delete(f"/api/knowledge/lib/{lib_id}")
    #     assert response.status_code == 200
    #     result = response.json()
    #     assert "data" in result
    #     data = result["data"]
    #     assert data["success"] == True

    #     # Clean up
    #     await knowledge_graph_query.delete_graph_by_lib(lib_id)

@pytest.mark.asyncio(loop_scope="session")
class TestKnowledgeLibSubject:
    async def test_create_knowledge_lib_subject_success(self, client: AsyncClient, setup_test_node: tuple[Node, int, int, str]):
        lib_id, subject_id, valid_token = setup_test_node
        response = await client.post("/api/knowledge/subject", headers={"Authorization": valid_token}, json={"name": "Test Subject", "knowledge_lib_id": lib_id})
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert "name" in data
        assert "knowledge_lib_id" in data
        assert data["name"] == "Test Subject"
        assert data["knowledge_lib_id"] == 1

    async def test_create_knowledge_lib_subject_missing_name(self, client: AsyncClient, setup_test_node: tuple[Node, int, int, str]):
        lib_id, subject_id, valid_token = setup_test_node
        response = await client.post("/api/knowledge/subject", headers={"Authorization": valid_token}, json={"knowledge_lib_id": lib_id})
        assert response.status_code == 422  # Unprocessable Entity

    async def test_read_knowledge_lib_subject(self, client: AsyncClient, setup_test_node: tuple[Node, int, int, str]):
        lib_id, subject_id, valid_token = setup_test_node
        response = await client.get(f"/api/knowledge/subject/{subject_id}", headers={"Authorization": valid_token})  # Assuming subject with ID 1 exists
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert "name" in data
        assert "knowledge_lib_id" in data
        assert data["name"] == "What goods are transported on the trunk line?"

    async def test_read_knowledge_lib_subject_invalid_id(self, client: AsyncClient, setup_test_node: tuple[Node, int, int, str]):
        lib_id, subject_id, valid_token = setup_test_node
        response = await client.get(f"/api/knowledge/subject/-1", headers={"Authorization": valid_token})  # Assuming this ID does not exist
        assert response.status_code == 200
        assert response.json() == {'code': -1, 'data': None, 'msg': 'Subject not found'}

    async def test_update_knowledge_lib_subject_success(self, client: AsyncClient, setup_test_node: tuple[Node, int, int, str]):
        lib_id, subject_id, valid_token = setup_test_node
        response = await client.put("/api/knowledge/subject", headers={"Authorization": valid_token}, json={"id": subject_id, "name": "Updated Subject", "knowledge_lib_id": lib_id})
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert data["name"] == "Updated Subject"

    async def test_update_knowledge_lib_subject_not_found(self, client: AsyncClient, setup_test_node: tuple[Node, int, int, str]):
        lib_id, subject_id, valid_token = setup_test_node
        response = await client.put("/api/knowledge/subject", headers={"Authorization": valid_token}, json={"id": -13, "name": "Nonexistent Subject", "knowledge_lib_id": lib_id})
        assert response.status_code == 200
        assert response.json() == {'code': -1, 'data': None, 'msg': 'Knowledge lib subject not found'}

    async def test_delete_knowledge_lib_subject_not_found(self, client: AsyncClient, setup_test_node: tuple[Node, int, int, str]):
        lib_id, subject_id, valid_token = setup_test_node
        response = await client.delete("/api/knowledge/subject/-13", headers={"Authorization": valid_token})  # Assuming this ID does not exist
        assert response.status_code == 200
        assert response.json() == {'code': -1, 'data': None, 'msg': 'Subject not found'}

    async def test_find_knowledge_subjects_valid(self, client: AsyncClient, setup_test_node: tuple[Node, int, int, str]):
        lib_id, subject_id, valid_token = setup_test_node
        response = await client.get("/api/knowledge/subject/find/1", headers={"Authorization": valid_token})  # Assuming knowledge_lib_id 1 exists
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, list)
        assert len(data) > 0

    async def test_find_knowledge_subjects_invalid_knowledge_lib_id(self, client: AsyncClient, setup_test_node):
        lib_id, subject_id, valid_token = setup_test_node

        response = await client.get("/api/knowledge/subject/find/-1", headers={"Authorization": valid_token})  # Invalid knowledge_lib_id
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, list)
        assert len(data) == 0

    # async def test_delete_knowledge_lib_subject_success(self, client: AsyncClient):
    #     # Arrange
    #     knowledge_graph_query = KnowledgeGraphQuery()
    #     lib_id = -13
    #     subject_id = -13
    #     parent_node = await knowledge_graph_query.history.add_subject_message(lib_id, subject_id, "Parent Node", 1)
    #     child_node = await knowledge_graph_query.history.add_subject_message(lib_id, subject_id, "Child Node", 1)
    #     relationship = await knowledge_graph_query.history.add_relationship(lib_id, subject_id, parent_node["element_id"], child_node["element_id"], RelationshipType.HAS_CHILD)

    #     # Execution
    #     response = await client.delete(f"/api/knowledge/subject/{subject_id}")  # Assuming subject with ID 1 exists
    #     assert response.status_code == 200
    #     result = response.json()
    #     assert "data" in result
    #     data = result["data"]
    #     assert data["success"] == True

    #     # Clean up
    #     await knowledge_graph_query.delete_graph_by_lib(lib_id)