import pytest

from graph.graph_query import KnowledgeGraphQuery
from graph.node import Node
from ai.document_service import DocumentService
from services.graph_service import GraphService
import core.config as config

@pytest.fixture(autouse=True)
def setup_function():
    org_api_env = config.API_ENV
    org_upload_dir = config.UPLOAD_DIR
    config.API_ENV = 'test' 
    config.UPLOAD_DIR = ''
    yield
    config.API_ENV = org_api_env
    config.UPLOAD_DIR = org_upload_dir

@pytest.fixture(scope="module")
def document_service() -> DocumentService:
    return DocumentService()

@pytest.fixture(scope="module")
def knowledge_graph_query() -> KnowledgeGraphQuery:
    return KnowledgeGraphQuery()

@pytest.fixture(scope="module")
def graph_service() -> GraphService:
    config.API_ENV = 'test' 
    config.UPLOAD_DIR = '.'
    return GraphService()


def assert_summary_and_splits(summary, splits, expected_metadata=None, expected_content=None):
    """Helper function to assert summary and splits."""
    assert summary is not None
    assert isinstance(summary, dict)
    assert "title" in summary
    assert "summary" in summary

    assert splits is not None
    assert isinstance(splits, list)
    assert len(splits) > 0

    if expected_metadata:
        print("metadata: ", splits[-1].metadata)
        assert splits[-1].metadata == expected_metadata

    if expected_content:
        assert splits[-1].page_content == expected_content


@pytest.mark.parametrize(
    "file_path, expected_metadata, expected_content",
    [
        ("tests/data/01_logists.txt", {'source': 'tests/data/01_logists.txt'}, None),
        ("tests/data/02_Difference Between Alpha and Beta Testing.pdf", {'source': 'tests/data/02_Difference Between Alpha and Beta Testing.pdf', 'page': 26, 'page_label': '27'}, None),
        ("tests/data/03_专业术语解释.docx", {'source': 'tests/data/03_专业术语解释.docx'}, None),
        ("tests/data/04_battery.xlsx", {'source': 'tests/data/04_battery.xlsx'}, None),
        ("tests/data/05_cmc.pptx", {'source': 'tests/data/05_cmc.pptx'}, None),
        ("tests/data/06_contact.csv", {'source': 'tests/data/06_contact.csv', 'row': 10}, "Name: William Clark\nPhone: +1-818-555-0120\nCompany: Los Angeles Film Production\nPosition: Producer"),
        ("tests/data/07_products.html", {'source': 'tests/data/07_products.html'}, None),
        ("tests/data/08_contact.xml", {'source': 'tests/data/08_contact.xml'}, None),
        ("tests/data/09_contact.json", {}, '{"name": "William Clark", "phone": "+1-818-555-0120", "company": "Los Angeles Film Production", "position": "Producer"}'),
        ("tests/data/10_README_en.md", {'source': 'WiseNet', 'title': 'Contribution and Feedback'}, '---  \nRegarding the GitHub link, I encountered some issues while trying to parse the webpage. This could be due to the link itself or network issues. Please check the validity of the webpage link and try again if necessary. If you have any other questions or need further assistance, feel free to ask!'),
    ],
)
def test_analysis_document(document_service, file_path, expected_metadata, expected_content):
    """Test analysis of different document types."""
    summary, splits = document_service.analysis_file(file_path)
    assert_summary_and_splits(summary, splits, expected_metadata, expected_content)


def test_upload_document(graph_service, knowledge_graph_query):
    """Test uploading a document to the knowledge graph."""
    # Arrange
    lib_id = -13
    subject_id = -13
    parent_node, r = Node.add_human_node(lib_id, subject_id, "Logistics transportation process")
    file_path = "tests/data/01_logists.txt"
    filename = "logists.txt"

    # Act
    document = graph_service.upload_graph_node_file(
        lib_id=lib_id,
        subject_id=subject_id,
        node_element_id=parent_node.element_id,
        saved_at=file_path,
        filename=filename
    )

    # Assert
    assert document is not None
    assert document.element_id is not None
    assert document.lib_id == lib_id
    assert document.subject_id == subject_id
    assert document.name == filename
    assert document.saved_at == file_path

    node = Node.find_detail_by_element_id(element_id=parent_node.element_id)
    assert len(node.documents) == 1

    # Clean up
    knowledge_graph_query.delete_graph_by_lib(lib_id)


def test_analysis_graph_node_file(graph_service, knowledge_graph_query):
    # Arrange
    lib_id = -13
    subject_id = -13
    parent_node, r = Node.add_human_node(lib_id, subject_id, "Logistics transportation process")
    file_path = "tests/data/01_logists.txt"
    filename = "logists.txt"
    document = graph_service.upload_graph_node_file(
        lib_id=lib_id,
        subject_id=subject_id,
        node_element_id=parent_node.element_id,
        saved_at=file_path,
        filename=filename
    )
    assert document is not None

    # Act
    document = graph_service.analyze_graph_node_file(document.element_id)

    # Assert
    assert document is not None
    assert document.element_id is not None
    assert document.lib_id == lib_id
    assert document.subject_id == subject_id
    assert document.name == filename
    assert document.saved_at == file_path
    assert document.title is not None
    assert document.content is not None
    assert document.title_vector is not None
    assert document.content_vector is not None
    assert document.embedding_model == "sbert"
    assert document.created_at is not None
    assert document.updated_at is not None
    assert len(document.pages) == 2

    # Clean up
    knowledge_graph_query.delete_graph_by_lib(lib_id)

def test_analysis_url(document_service):
    # Arrange
    url = "https://www.womenshealthmag.com/weight-loss/a42112641/7-day-meal-plan-for-weight-loss/"
    # Act
    summary, splits = document_service.analysis_url(url)

    # Assert
    assert 'title' in summary
    assert 'summary' in summary
    assert len(splits) == 21