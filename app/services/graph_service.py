from graph.node import Node
from graph.relationship import RelationshipType, Relationship
from graph.webpage import WebPage
from graph.document import Document
from graph.document_page import DocumentPage
from services.graph_analyze_service import GraphAnalyzeService
from core.extends_logger import logger

class GraphService(GraphAnalyzeService):
    def __init__(self):
        super(GraphService, self).__init__()

    async def initialize_graph(self):
        """
        Initializes the knowledge graph by adding root, subject, info, prompt, and question nodes, and their relationships, webpages, and documents.
        Create graph index for each node type.
        """
        logger.info("Initializing graph database...")
        lib_id = -13
        subject_id = -13
        subject_node: Node = Node.add_subject_node(lib_id, subject_id, "test", depth=1)
        info_node: Node = Node.add_info_node(lib_id, subject_id, "test", depth=2)
        Relationship.add_relationship(lib_id, subject_id, subject_node.element_id, info_node.element_id, RelationshipType.HAS_CHILD)
        prompt_node: Node = Node.add_prompt_node(lib_id, subject_id, "test", depth=3)
        Relationship.add_relationship(lib_id, subject_id, info_node.element_id, prompt_node.element_id, RelationshipType.HAS_CHILD)
        human_node, relationship = Node.add_human_node(lib_id, subject_id, "test")
        Relationship.add_relationship(lib_id, subject_id, prompt_node.element_id, human_node.element_id, RelationshipType.RELATED_TO)
        question_node: Node = Node.add_question_node(lib_id, subject_id, "test")
        Relationship.add_relationship(lib_id, subject_id, question_node.element_id, human_node.element_id, RelationshipType.HAS_CHILD)
        WebPage.add_webpage_node(lib_id, subject_id, info_node.element_id, "www.example.com")
        document = Document.add_document_node(lib_id, subject_id,
                                                        info_node.element_id,
                                                        "document",
                                                        "file path/url",
                                                        "title1",
                                                        "summary1",
                                                        [1, 2, 3],
                                                        [1, 2, 3],
                                                        "sbert")
        document_page = DocumentPage.add_document_page_node(lib_id, subject_id,
                                                        info_node.element_id,
                                                        document.element_id,
                                                        "source",
                                                        "title",
                                                        "sub title",
                                                        0,
                                                        0,
                                                        "page content",
                                                        [1, 2, 3],
                                                        "sbert")

        self.knowledge_graph_query.delete_graph_by_lib(lib_id)
        logger.info("Initializing graph database finished...")