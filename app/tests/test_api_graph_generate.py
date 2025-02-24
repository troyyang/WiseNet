import pytest
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


@pytest.fixture
def client():
    config.IS_CAMEL_CASE = False
    return TestClient(main.create_app())


@pytest.fixture
def knowledge_graph_query() -> KnowledgeGraphQuery:
    return KnowledgeGraphQuery()


@pytest.fixture
def setup_test_node(knowledge_graph_query):
    lib_id = -13
    knowledge_graph_query.delete_graph_by_lib(lib_id)
    subject_id = -13
    info_content = Llm.get_ai_response("Logistics transportation process", "llama3.1")
    parent_node, relationship = Node.add_human_node(lib_id, subject_id, info_content)
    yield parent_node, lib_id, subject_id
    knowledge_graph_query.delete_graph_by_lib(lib_id)


class TestGraphGeneration:
    def test_generate_answer(self, client, setup_test_node):
        parent_node, lib_id, subject_id = setup_test_node

        data = {
            "lib_id": lib_id,
            "subject_id": subject_id,
            "element_id": parent_node.element_id,
            "llm_name": "llama3.1"
        }
        response = client.post(f"/api/graph/generate/answer", json=data)

        assert response.status_code == 200
        result = response.json()
        assert result.get("code") == 0
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert data.get("node").get("type") == NodeType.INFO.value
        assert data.get("relationship").get("type") == RelationshipType.HAS_CHILD.value

        nodes, overviews = Node.query_graph_node(lib_id, [subject_id])
        assert len(nodes) == 2
        assert overviews[0].type == NodeType.HUMAN.value
        links, overviews = Relationship.query_graph_relationship(lib_id, [subject_id])
        assert len(links) == 1
        assert links[0].type == RelationshipType.HAS_CHILD
        assert overviews[0].type == RelationshipType.HAS_CHILD.value

    def test_generate_questions(self, client, setup_test_node):
        parent_node, lib_id, subject_id = setup_test_node

        data = {
            "lib_id": lib_id,
            "subject_id": subject_id,
            "element_id": parent_node.element_id,
            "llm_name": "llama3.1"
        }
        response = client.post(f"/api/graph/generate/questions", json=data)

        assert response.status_code == 200
        result = response.json()
        assert result.get("code") == 0
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert data.get("nodes")[0].get("type") == NodeType.QUESTION.value
        assert data.get("relationships")[0].get("type") == RelationshipType.HAS_CHILD.value


    def test_generate_prompts(self, client, setup_test_node):
        parent_node, lib_id, subject_id = setup_test_node

        data = {
            "lib_id": lib_id,
            "subject_id": subject_id,
            "element_id": parent_node.element_id,
            "llm_name": "llama3.1"
        }
        response = client.post(f"/api/graph/generate/prompts", json=data)

        assert response.status_code == 200
        result = response.json()
        assert result.get("code") == 0
        assert "data" in result
        data = result["data"]
        assert data.get("nodes")[0].get("type") == NodeType.PROMPT.value
        assert data.get("relationships")[0].get("type") == RelationshipType.HAS_CHILD.value

    def test_cancel_generate_graph(self, client):
        response = client.post("/api/graph/cancel/1")
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert data.get("success") == True