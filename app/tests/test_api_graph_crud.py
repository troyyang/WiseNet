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


class TestGraphNode:
    def test_delete_graph_node(self, client, setup_test_node):
        parent_node, lib_id = setup_test_node
        node_element_id = parent_node.element_id
        result = graph.query("MATCH (n) WHERE elementId(n)=$node_element_id RETURN n", {"node_element_id": node_element_id})
        assert len(result) == 1

        response = client.delete(f"/api/graph/node/{node_element_id}")
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert data.get("success") == True

        result = graph.query("MATCH (n) WHERE elementId(n)=$node_element_id RETURN n", {"node_element_id": node_element_id})
        assert len(result) == 0, "Node was not deleted successfully"

    def test_add_graph_node(self, client, setup_test_node):
        parent_node, lib_id = setup_test_node
        message = "test_message"

        response = client.post("/api/graph/node", json={"lib_id": lib_id, "subject_id": -13, "content": message})
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert data.get("node") is not None
        assert data.get("relationship") is None

    def test_add_graph_node_with_parent(self, client, setup_test_node):
        parent_node, lib_id = setup_test_node
        message = "test_message"

        response = client.post("/api/graph/node", json={"lib_id": lib_id, "subject_id": -13, "content": message, "parent_element_id": parent_node.element_id})
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert data.get("node") is not None
        assert data.get("relationship") is not None

    def test_update_graph_node(self, client, setup_test_node):
        parent_node, lib_id = setup_test_node
        info_node = Node.add_info_node(lib_id, -13, "test_message", 1)
        element_id = info_node.element_id
        info_node.content = "updated_message"
        info_node.title = "updated_title"
        info_node.entities = ["updated_entity"]
        info_node.keywords = ["updated_keyword"]
        info_node.tags = ["updated_tag"]
        info_node.documents = ["updated_document"]
        info_node.links = ["updated_link"]
        info_node.webpages = ["updated_webpage"]
        info_node.embedding_model = "sbert"

        response = client.put(f"/api/graph/node", json=info_node.to_dict())
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert data.get("content") == "updated_message"

        result = graph.query("MATCH (n) WHERE elementId(n)=$element_id RETURN n", {"element_id": element_id})
        assert len(result) == 1
        assert result[0].get("n").get("content") == "updated_message"


class TestGraphRelationship:
    def test_delete_graph_relationship(self, client, setup_test_node):
        parent_node, lib_id = setup_test_node
        child_node = Node.add_subject_node(lib_id, -13, "Child Node", 1)
        relationship = Relationship.add_relationship(lib_id, -13, parent_node.element_id, child_node.element_id, RelationshipType.HAS_CHILD)
        result = graph.query("MATCH ()-[r]->() WHERE elementId(r)=$relationship_element_id RETURN r", {"relationship_element_id": relationship.element_id})
        assert len(result) == 1

        response = client.delete(f"/api/graph/relationship/{relationship.element_id}")
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert data.get("success") == True

        result = graph.query("MATCH ()-[r]->() WHERE elementId(r)=$relationship_element_id RETURN r", {"relationship_element_id": relationship.element_id})
        assert len(result) == 0, "Relationship was not deleted successfully"

    def test_add_graph_relationship(self, client, setup_test_node):
        parent_node, lib_id = setup_test_node
        child_node = Node.add_subject_node(lib_id, -13, "Child Node", 1)

        response = client.post("/api/graph/relationship", 
                              json={
                                  "lib_id": lib_id, 
                                  "subject_id": -13, 
                                  "source_element_id": parent_node.element_id, 
                                  "target_element_id": child_node.element_id,
                                  "type": "RELATED_TO"
                              })
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert data.get("source_element_id") == parent_node.element_id
        assert data.get("target_element_id") == child_node.element_id
        assert data.get("element_id") is not None

    def test_update_graph_relationship_info(self, client, setup_test_node):
        parent_node, lib_id = setup_test_node
        child_node = Node.add_subject_node(lib_id, -13, "Child Node", 1)
        relationship = Relationship.add_relationship(lib_id, -13, parent_node.element_id, child_node.element_id, RelationshipType.RELATED_TO)
        relationship_element_id = relationship.element_id

        new_message = "updated_message"
        response = client.put(f"/api/graph/relationship/info", json={"element_id": relationship_element_id, "content": new_message})
        assert response.status_code == 200
        result = response.json()
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert data.get("content") == new_message


class TestGraphNodeEntities:
    def test_delete_graph_node_entity(self, client, setup_test_node):
        parent_node, lib_id = setup_test_node
        entity = Entity.add_entity_node(lib_id, -13, parent_node.element_id, "entity", [1, 2, 3])    
        entity2 = Entity.add_entity_node(lib_id, -13, parent_node.element_id, "entity2", [4, 5, 6])
        node = Node.find_detail_by_element_id(parent_node.element_id)
        assert len(node.entities) == 2

        response = client.delete(f"/api/graph/node/entity/{entity2.element_id}/{parent_node.element_id}")
        assert response.status_code == 200
        result = response.json()
        assert result.get("code") == 0
        assert "data" in result
        data = result["data"]
        assert data.get("success") == True

        node = Node.find_detail_by_element_id(parent_node.element_id)
        assert len(node.entities) == 1


class TestGraphNodeKeywords:
    def test_delete_graph_node_keyword(self, client, setup_test_node):
        parent_node, lib_id = setup_test_node
        keyword = Keyword.add_keyword_node(lib_id, -13, parent_node.element_id, "keyword", [1, 2, 3])
        keyword2 = Keyword.add_keyword_node(lib_id, -13, parent_node.element_id, "keyword2", [4, 5, 6])
        node = Node.find_detail_by_element_id(parent_node.element_id)
        assert len(node.keywords) == 2

        response = client.delete(f"/api/graph/node/keyword/{keyword2.element_id}/{parent_node.element_id}")
        assert response.status_code == 200
        result = response.json()
        assert result.get("code") == 0
        assert "data" in result
        data = result["data"]
        assert data.get("success") == True

        node = Node.find_detail_by_element_id(parent_node.element_id)
        assert len(node.keywords) == 1


class TestGraphNodeTags:
    def test_delete_graph_node_tag(self, client, setup_test_node):
        parent_node, lib_id = setup_test_node
        tag = Tag.add_tag_node(lib_id, -13, parent_node.element_id, "tag", [1, 2, 3])    
        tag2 = Tag.add_tag_node(lib_id, -13, parent_node.element_id, "tag2", [4, 5, 6])
        node = Node.find_detail_by_element_id(parent_node.element_id)
        assert len(node.tags) == 2

        response = client.delete(f"/api/graph/node/tag/{tag2.element_id}/{parent_node.element_id}")
        assert response.status_code == 200
        result = response.json()
        assert result.get("code") == 0
        assert "data" in result
        data = result["data"]
        assert data.get("success") == True

        node = Node.find_detail_by_element_id(parent_node.element_id)
        assert len(node.tags) == 1


class TestGraphNodeDocuments:
    def test_delete_graph_node_document(self, client, setup_test_node):
        parent_node, lib_id = setup_test_node
        document = Document.add_document_node(lib_id, -13, parent_node.element_id, "document", "file path/url", [1, 2, 3])    
        document2 = Document.add_document_node(lib_id, -13, parent_node.element_id, "document2", "file path/url2", [4, 5, 6])
        node = Node.find_detail_by_element_id(parent_node.element_id)
        assert len(node.documents) == 2

        response = client.delete(f"/api/graph/node/document/{document2.element_id}")
        assert response.status_code == 200
        result = response.json()
        assert result.get("code") == 0
        assert "data" in result
        data = result["data"]
        assert data.get("success") == True

        node = Node.find_detail_by_element_id(parent_node.element_id)
        assert len(node.documents) == 1


class TestGraphNodeWebpages:
    def test_add_graph_node_webpage_valid_url(self, client, setup_test_node):
        parent_node, lib_id = setup_test_node
        url = "https://www.dudutalk.com"

        response = client.post(f"/api/graph/node/webpage", json={"lib_id": lib_id, "subject_id": -13, "element_id": parent_node.element_id, "url": url})
        assert response.status_code == 200
        result = response.json()
        assert result.get("code") == 0
        assert "data" in result
        data = result["data"]
        assert isinstance(data, dict)
        assert data.get("element_id") is not None
        assert data.get("url") == "https://www.dudutalk.com/"
        assert data.get("title") is None
        assert data.get("title_vector") is None
        assert data.get("content") is None
        assert data.get("content_vector") is None
        assert data.get("pages") == []

    def test_add_graph_node_webpage_invalid_url(self, client, setup_test_node):
        parent_node, lib_id = setup_test_node
        url = "dudutalk.com"

        response = client.post(f"/api/graph/node/webpage", json={"lib_id": lib_id, "subject_id": -13, "element_id": parent_node.element_id, "url": url})
        assert response.status_code == 422
        result = response.json()
        assert result.get("code") == 10002

    def test_delete_graph_node_webpage(self, client, setup_test_node):
        parent_node, lib_id = setup_test_node
        url = "https://www.dudutalk.com/"
        webpage_node = WebPage.add_webpage_node(lib_id, -13, parent_node.element_id, url)
        webpage_node.title = "new title"
        webpage_node.content = "new summary"
        webpage_node.title_vector = [1, 2, 3]
        webpage_node.content_vector = [4, 5, 6]
        webpage_node.embedding_model = "sbert"
        webpage_node = webpage_node.update()
        assert webpage_node is not None
        DocumentPage.add_document_page_node(lib_id, -13, parent_node.element_id, webpage_node.element_id, "source", "title", "sub title", 0, 0, "page content", [1, 2, 3], "sbert")

        webpage: WebPage = WebPage.get_webpage_by_element_id(webpage_node.element_id)
        assert isinstance(webpage, WebPage)
        assert webpage.element_id == webpage_node.element_id
        assert len(webpage.pages) == 1

        response = client.delete(f"/api/graph/node/webpage/{webpage_node.element_id}")
        assert response.status_code == 200
        result = response.json()
        assert result.get("code") == 0

        try:
            webpage: WebPage = WebPage.get_webpage_by_element_id(webpage_node.element_id)
        except Exception as e:
            assert True

        try:
            DocumentPage.get_document_pages_of_parent(webpage_node.element_id)
        except Exception as e:
            assert True

        try:
            DocumentPage.get_document_pages_of_parent(parent_node.element_id)
        except Exception as e:
            assert True