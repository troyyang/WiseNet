import pytest
import asyncio
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient

import core.config as config
import core.database as db
import main
from ai.llm import Llm
from graph import RelationshipType, NodeType, graph
from graph.document import Document
from graph.document_page import DocumentPage
from graph.entity import Entity
from graph.graph_query import KnowledgeGraphQuery
from graph.keyword import Keyword
from graph.node import Node
from graph.relationship import Relationship
from graph.tag import Tag
from graph.webpage import WebPage
from schemas.graph import GraphConditionView


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

@pytest_asyncio.fixture
async def client() -> AsyncClient:
    config.IS_CAMEL_CASE = False
    transport = ASGITransport(app=main.create_app())
    async with AsyncClient(base_url="http://test", transport=transport) as ac:
        yield ac


@pytest.fixture
def knowledge_graph_query() -> KnowledgeGraphQuery:
    return KnowledgeGraphQuery()


@pytest.fixture
def setup_test_node(knowledge_graph_query):
    lib_id = -13
    knowledge_graph_query.delete_graph_by_lib(lib_id)
    subject_id = -13
    parent_node = Node.add_subject_node(lib_id, subject_id, "Parent Node", 1)
    yield parent_node, lib_id, subject_id
    knowledge_graph_query.delete_graph_by_lib(lib_id)

@pytest.mark.asyncio(loop_scope="session")
class TestGraphQuery:
    async def test_query_graph_by_lib(self, client, setup_test_node):
        parent_node, lib_id, subject_id = setup_test_node
        child_node = Node.add_prompt_node(lib_id, subject_id, "Child Node", 1)
        Relationship.add_relationship(lib_id, subject_id, parent_node.element_id, child_node.element_id, RelationshipType.HAS_CHILD)

        response = await client.post(f"/api/graph/query/{lib_id}", json={})
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert "overview" in data
        assert "nodes" in data
        assert "links" in data
        assert len(data.get("nodes")) == 0
        assert len(data.get("links")) == 0

    async def test_query_graph_by_subject(self, client, setup_test_node):
        parent_node, lib_id, subject_id = setup_test_node
        child_node = Node.add_prompt_node(lib_id, subject_id, "Child Node", 1)
        Relationship.add_relationship(lib_id, subject_id, parent_node.element_id, child_node.element_id, RelationshipType.HAS_CHILD)

        response = await client.post(f"/api/graph/query/{lib_id}", json={"subject_ids": [subject_id]})
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert "overview" in data
        assert len(data.get("nodes")) == 3
        assert len(data.get("links")) == 4

    async def test_query_graph_by_invalid_subject(self, client, setup_test_node):
        parent_node, lib_id, subject_id = setup_test_node
        child_node = Node.add_prompt_node(lib_id, subject_id, "Child Node", 1)
        Relationship.add_relationship(lib_id, subject_id, parent_node.element_id, child_node.element_id, RelationshipType.HAS_CHILD)

        response = await client.post(f"/api/graph/query/{lib_id}", json={"subject_ids": [-999]})
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert "overview" in data
        assert len(data.get("nodes")) == 1
        assert len(data.get("links")) == 0


    async def test_query_graph_by_type(self, client, setup_test_node):
        parent_node, lib_id, subject_id = setup_test_node
        prompt_node = Node.add_prompt_node(lib_id, subject_id, "Child Node", 1)
        Relationship.add_relationship(lib_id, subject_id, parent_node.element_id, prompt_node.element_id, RelationshipType.HAS_CHILD)
        info_node = Node.add_info_node(lib_id, subject_id, "Info Node", 1)
        Relationship.add_relationship(lib_id, subject_id, prompt_node.element_id, info_node.element_id, RelationshipType.HAS_CHILD)

        response = await client.post(f"/api/graph/query/{lib_id}", json={"subject_ids": [subject_id], "type": NodeType.SUBJECT.value})
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert "overview" in data
        assert len(data.get("nodes")) == 3
        assert len(data.get("links")) == 2

        response = await client.post(f"/api/graph/query/{lib_id}", json={"subject_ids": [subject_id], "type": NodeType.PROMPT.value})
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert "overview" in data
        assert len(data.get("nodes")) == 3
        assert len(data.get("links")) == 2


    async def test_query_graph_by_invalid_type(self, client, setup_test_node):
        parent_node, lib_id, subject_id = setup_test_node
        child_node = Node.add_prompt_node(lib_id, subject_id, "Child Node", 1)
        Relationship.add_relationship(lib_id, subject_id, parent_node.element_id, child_node.element_id, RelationshipType.HAS_CHILD)

        response = await client.post(f"/api/graph/query/{lib_id}", json={"subject_ids": [1], "type": "invalid_type"})
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert "overview" in data
        assert len(data.get("nodes")) == 0
        assert len(data.get("links")) == 0

    async def test_query_graph_by_message(self, client, setup_test_node):
        subject_node, lib_id, subject_id = setup_test_node
        parent_node = Node.add_prompt_node(lib_id, subject_id, "Parent Node", subject_id)
        child_node = Node.add_info_node(lib_id, subject_id, "Child Node", subject_id)
        Relationship.add_relationship(lib_id, subject_id, parent_node.element_id, child_node.element_id, RelationshipType.HAS_CHILD)

        response = await client.post(f"/api/graph/query/{lib_id}", json={"subject_ids": [subject_id], "type": NodeType.PROMPT.value, "content": "Parent Node"})
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert "overview" in data
        assert len(data.get("nodes")) == 2
        assert len(data.get("links")) == 1

    async def test_query_graph_by_invalid_message(self, client, setup_test_node):
        parent_node, lib_id, subject_id = setup_test_node
        child_node = Node.add_prompt_node(lib_id, subject_id, "Child Node", 1)
        Relationship.add_relationship(lib_id, subject_id, parent_node.element_id, child_node.element_id, RelationshipType.HAS_CHILD)

        response = await client.post("/api/graph/query/1", json={"subject_ids": [1], "type": NodeType.PROMPT.value, "content": "invalid message"})
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert "overview" in data
        assert len(data.get("nodes")) == 0
        assert len(data.get("links")) == 0

@pytest.mark.asyncio(loop_scope="session")
class TestGraphNodeDetail:
    async def test_get_graph_node_detail(self, client, setup_test_node):
        parent_node, lib_id, subject_id = setup_test_node
        prompt_node = Node.add_prompt_node(lib_id, subject_id, "test_message", 1)
        element_id = prompt_node.element_id
        prompt_node.title = "title"
        prompt_node.title_vector = [1, 2, 3]
        prompt_node.content_vector = [1, 2, 3]
        prompt_node.embedding_model = "sbert"
        prompt_node.update()

        response = await client.get(f"/api/graph/node/{element_id}")
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert data.get("element_id") == element_id
        assert data.get("content") == "test_message"
        assert data.get("title") == "title"
        assert data.get("title_vector") == [1, 2, 3]
        assert data.get("content_vector") == [1, 2, 3]

    async def test_get_graph_relationship_detail(self, client, setup_test_node):
        parent_node, lib_id, subject_id = setup_test_node
        child_node = Node.add_prompt_node(lib_id, subject_id, "child_node", 1)
        message = "test_message"
        relationship = Relationship.add_relationship(lib_id, subject_id, parent_node.element_id, child_node.element_id, RelationshipType.RELATED_TO, message)
        relationship_element_id = relationship.element_id

        response = await client.get(f"/api/graph/relationship/{relationship_element_id}")
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert data.get("element_id") == relationship_element_id
        assert data.get("source_element_id") == parent_node.element_id
        assert data.get("target_element_id") == child_node.element_id
        assert data.get("type") == RelationshipType.RELATED_TO.value
        assert data.get("content") == message

    async def test_query_graph_node_overview(self, client, setup_test_node):
        parent_node, lib_id, subject_id = setup_test_node
        child_node = Node.add_info_node(lib_id, subject_id, "child_node", 1)
        relationship = Relationship.add_relationship(lib_id, subject_id, parent_node.element_id, child_node.element_id, RelationshipType.HAS_CHILD)

        condition = {
            "subject_ids": [subject_id]
        }
        response = await client.post(f"/api/graph/overview/{lib_id}", json=condition)
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert data is not None
        assert len(data.get("nodes")) == 3
        assert data.get("links")[0].get("type") == RelationshipType.HAS_CHILD.value
        assert data.get("links")[0].get("count") == 2

@pytest.mark.asyncio(loop_scope="session")
class TestGraphDocumentAndWebpage:
    async def test_get_document_detail(self, client, setup_test_node):
        parent_node, lib_id, subject_id = setup_test_node
        file_path = "tests/data/01_logists.txt"
        filename = "logists.txt"
        document = Document.add_document_node(lib_id=lib_id, subject_id=subject_id, parent_element_id=parent_node.element_id, name=filename, saved_at=file_path)
        assert document is not None

        await client.post(f"/api/graph/node/document/analyze", json={"element_id": document.element_id, "llm_name": "llama3", "embedding_model": "sbert"})

        response = await client.get(f"/api/graph/node/document/detail/{document.element_id}")
        assert response.status_code == 200
        result = response.json()
        assert result.get("code") == 0
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert data.get("element_id") == document.element_id
        assert data.get("name") == filename
        assert data.get("saved_at") == file_path
        assert data.get("title") is not None
        assert data.get("title_vector") is not None
        assert data.get("content") is not None
        assert data.get("content_vector") is not None
        assert len(data.get("pages")) == 2

    async def test_get_graph_node_webpage(self, client, setup_test_node):
        parent_node, lib_id, subject_id = setup_test_node
        url = "https://www.dudutalk.com/"
        webpage_node = WebPage.add_webpage_node(lib_id, subject_id, parent_node.element_id, url)
        webpage_node.title = "new title"
        webpage_node.content = "new summary"
        webpage_node.title_vector = [1, 2, 3]
        webpage_node.content_vector = [4, 5, 6]
        webpage_node.embedding_model = "sbert"
        webpage_node = webpage_node.update()
        assert webpage_node is not None
        DocumentPage.add_document_page_node(lib_id, subject_id, parent_node.element_id, webpage_node.element_id, "source", "title", "sub title", 0, 0, "page content", [1, 2, 3], "sbert")

        response = await client.get(f"/api/graph/node/webpage/{webpage_node.element_id}")
        assert response.status_code == 200
        result = response.json()
        assert result.get("code") == 0
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert data.get("element_id") == webpage_node.element_id
        assert data.get("url") == "https://www.dudutalk.com/"
        assert data.get("title") == "new title"
        assert data.get("title_vector") == [1, 2, 3]
        assert data.get("content") == "new summary"
        assert data.get("content_vector") == [4, 5, 6]
        assert data.get("embedding_model") == "sbert"
        assert len(data.get("pages")) == 1