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
    yield parent_node, lib_id
    knowledge_graph_query.delete_graph_by_lib(lib_id)


class TestGraphNodeAnalysis:
    def test_analyze_graph_node_en_by_sbert(self, client, setup_test_node):
        parent_node, lib_id = setup_test_node

        response = client.post(
            "/api/graph/node/analyze",
            json={"element_id": parent_node.element_id, "llm_name": "llama3.1", "embedding_model": "sbert"}
        )

        assert response.status_code == 200
        result = response.json()
        assert result.get("code") == 0
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert data.get("element_id") == parent_node.element_id
        assert data.get("title") is not None
        assert data.get("title_vector") is not None
        assert data.get("content") is not None
        assert data.get("content_vector") is not None
        assert len(data.get("keywords")) == 3
        assert data.get("tags") is not None
        assert len(data.get("entities")) > 0
        assert data.get("documents") == []
        assert data.get("webpages") == []

    def test_analyze_graph_node_zh_by_sbert(self, client, setup_test_node):
        parent_node, lib_id = setup_test_node
        info_content = Llm.get_ai_response("冷链运输过程", "wizardlm2")
        parent_node, relationship = Node.add_human_node(lib_id, -13, info_content)

        response = client.post(
            "/api/graph/node/analyze",
            headers={"Accept-Language": "zh-CN"},
            json={"element_id": parent_node.element_id, "llm_name": "wizardlm2", "embedding_model": "sbert"}
        )

        assert response.status_code == 200
        result = response.json()
        assert result.get("code") == 0
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert data.get("element_id") == parent_node.element_id
        assert data.get("title") is not None
        assert data.get("title_vector") is not None
        assert data.get("content") is not None
        assert data.get("content_vector") is not None
        assert len(data.get("keywords")) == 3
        assert len(data.get("tags")) == 3
        assert len(data.get("entities")) > 0
        assert data.get("documents") == []
        assert data.get("webpages") == []


class TestDocumentAnalysis:
    def test_analysis_document(self, client, knowledge_graph_query, setup_test_node):
        parent_node, lib_id = setup_test_node
        file_path = "tests/data/01_logists.txt"
        filename = "logists.txt"
        document = Document.add_document_node(
            lib_id=lib_id,
            subject_id=-13,
            parent_element_id=parent_node.element_id,
            name=filename,
            saved_at=file_path
        )
        assert document is not None

        response = client.post(
            "/api/graph/node/document/analyze",
            json={"element_id": document.element_id, "llm_name": "llama3.1", "embedding_model": "sbert"}
        )

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


class TestWebPageAnalysis:
    def test_analysis_graph_node_webpage(self, client, knowledge_graph_query, setup_test_node):
        parent_node, lib_id = setup_test_node
        url = "https://www.dudutalk.com/"
        webpage_node = WebPage.add_webpage_node(lib_id, -13, parent_node.element_id, url)
        assert webpage_node is not None

        response = client.post(
            "/api/graph/node/webpage/analyze",
            json={
                "element_id": webpage_node.element_id,
                "llm_name": "llama3.1",
                "embedding_model": "sbert",
                "max_tokens_each_chunk": 128
            }
        )

        assert response.status_code == 200
        result = response.json()
        assert result.get("code") == 0
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert data.get("element_id") == webpage_node.element_id
        assert data.get("url") == "https://www.dudutalk.com/"
        assert data.get("title") is not None
        assert data.get("title_vector") is not None
        assert data.get("content") is not None
        assert data.get("content_vector") is not None
        assert data.get("embedding_model") == "sbert"
        assert len(data.get("pages")) == 11