from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from core.extends_logger import logger
from core.i18n import _
from . import BaseNode, BaseModel, RelationshipType, graph
from .document_page import DocumentPage
from .relationship import Relationship


class Document(BaseNode, BaseModel):
    """
    Represents a document in the graph database. This class handles the creation, updating, and querying of documents,
    as well as their relationships with nodes and document pages.
    """

    # Index names for full-text and vector searches
    title_full_text_index_name: str = "document_title_full_text_index"
    content_full_text_index_name: str = "document_content_full_text_index"
    lib_id_index_name: str = "document_lib_id_index"
    subject_id_index_name: str = "document_subject_id_index"
    title_vector_index_name: str = "document_title_vector_index"
    content_vector_index_name: str = "document_content_vector_index"

    # Cypher query clause for returning document properties
    return_clause = """
        RETURN id(document) AS id, 
        elementId(document) AS element_id, 
        document.lib_id AS lib_id,
        document.subject_id AS subject_id,
        document.name AS name, 
        document.saved_at AS saved_at,
        document.title AS title,
        document.content AS content,
        document.title_vector AS title_vector, 
        document.content_vector AS content_vector, 
        document.embedding_model AS embedding_model,
        document.created_at AS created_at, 
        document.updated_at AS updated_at
    """

    def __init__(self, **kwargs):
        """
        Initializes a Document instance with the provided keyword arguments.

        Args:
            **kwargs: Arbitrary keyword arguments to set document attributes.
        """
        super().__init__(**kwargs)
        self.name = kwargs.get("name")  # Name of the document
        self.saved_at = kwargs.get("saved_at")  # Timestamp when the document was saved
        self.title = kwargs.get("title")  # Title of the document
        self.title_vector = kwargs.get("title_vector")  # Vector representation of the title
        self.pages: List[DocumentPage] = []  # List of document pages associated with the document

    def __repr__(self):
        """
        Returns a string representation of the Document instance.

        Returns:
            str: A string representation of the Document.
        """
        repr = super().__repr__()
        return f"Document({repr}, name={self.name}, saved_at={self.saved_at}, title={self.title})"

    @classmethod
    def to_model(cls, result: Dict[str, Any]) -> "Document":
        """
        Converts a database result item into a Document instance.

        Args:
            result (Dict): A dictionary representing a document from the database.

        Returns:
            Document: A Document instance populated with data from the result item.
        """
        return Document(**result)

    def to_dict(self, filter=None) -> Dict[str, Any]:
        """
        Converts the Document instance to a dictionary.

        Args:
            filter (Optional[List[str]]): List of keys to include in the dictionary. If None, all keys are included.

        Returns:
            Dict[str, Any]: A dictionary representation of the Document.
        """
        dict = super().to_dict(filter)
        dict.update({
            "pages": super()._to_dict_list(self.pages, DocumentPage, filter.get("pages.page", None) if filter else None) if self.pages and (not filter or "pages" in filter) else []
        })
        return dict

    def save(self) -> "Document":
        """
        Saves the current document to the graph database.

        Returns:
            Document: The saved Document instance with updated attributes.

        Raises:
            ValueError: If the document creation fails.
        """
        try:
            set_vector_clause = self.compose_set_vector_clause("document")
            query = f"""
            CREATE (document:Document {{
                lib_id: $lib_id, 
                subject_id: $subject_id, 
                name: $name, 
                title: $title, 
                content: $content,
                saved_at: $saved_at, 
                embedding_model: $embedding_model,
                created_at: $created_at, 
                updated_at: $updated_at
            }})
            {set_vector_clause}
            {Document.return_clause}
            """
            params = {
                "lib_id": self.lib_id,
                "subject_id": self.subject_id,
                "name": self.name,
                "title": self.title,
                "content": self.content,
                "title_vector": self.title_vector,
                "content_vector": self.content_vector,
                "saved_at": self.saved_at,
                "embedding_model": self.embedding_model,
                "created_at": datetime.now(timezone.utc).timestamp(),
                "updated_at": datetime.now(timezone.utc).timestamp()
            }
            result = graph.query(query, params)
            if not result:
                logger.error("Failed to add document node: No result returned from the database.")
                raise ValueError(_("Document node creation failed with no result."))

            # Update instance attributes with database results
            self.id = result[0].get("id")
            self.element_id = result[0].get("element_id")
            self.created_at = result[0].get("created_at")
            self.updated_at = result[0].get("updated_at")

            self.create_index("Document")

            return self
        except Exception as e:
            logger.error(f"Failed to add document node: {e}, Parameters: {params}")
            raise

    def update(self) -> "Document":
        """
        Updates the current document in the graph database.

        Returns:
            Document: The updated Document instance.

        Raises:
            ValueError: If the document update fails.
        """
        try:
            set_vector_clause = self.compose_set_vector_clause("document")
            query = f"""
            MATCH (document:Document)
            WHERE elementId(document) = $element_id
            SET document.name = $name, 
            document.title = $title, 
            document.content = $content, 
            document.embedding_model = $embedding_model,
            document.updated_at = $updated_at
            {set_vector_clause}
            {Document.return_clause}
            """
            params = {
                "element_id": self.element_id,
                "name": self.name,
                "title": self.title,
                "content": self.content,
                "title_vector": self.title_vector,
                "content_vector": self.content_vector,
                "embedding_model": self.embedding_model,
                "updated_at": datetime.now(timezone.utc).timestamp()
            }
            result = graph.query(query, params)
            if not result:
                logger.error("Failed to update document node: No result returned from the database.")
                raise ValueError(_("Document node update failed with no result."))

            # Update instance attributes with database results
            self.id = result[0].get("id")
            self.element_id = result[0].get("element_id")
            self.created_at = result[0].get("created_at")
            self.updated_at = result[0].get("updated_at")
            return self
        except Exception as e:
            logger.error(f"Failed to update document node: {e}, Parameters: {params}")
            raise

    @classmethod
    def add_document_node(cls,
                          lib_id: int,
                          subject_id: int,
                          parent_element_id: str,
                          name: str,
                          saved_at: str,
                          title: str = None,
                          content: str = None,
                          title_vector: List[float] = None,
                          content_vector: List[float] = None,
                          embedding_model: str = "sbert") -> "Document":
        """
        Adds a document node to the graph database and links it to a specified parent node.

        Args:
            lib_id (int): The library ID.
            subject_id (int): The subject ID.
            parent_element_id (str): The element ID of the parent node.
            name (str): The name of the document.
            saved_at (str): The timestamp when the document was saved.
            title (str, optional): The title of the document.
            content (str, optional): The content of the document.
            title_vector (List[float], optional): The vector representation of the title.
            content_vector (List[float], optional): The vector representation of the content.
            embedding_model (str, optional): The embedding model used for the content vector.

        Returns:
            Document: The newly created Document instance.

        Raises:
            Exception: If the document creation fails.
        """
        try:
            document: Document = Document(lib_id=lib_id,
                                          subject_id=subject_id,
                                          name=name,
                                          saved_at=saved_at,
                                          title=title,
                                          content=content,
                                          title_vector=title_vector,
                                          content_vector=content_vector,
                                          embedding_model=embedding_model)
            document = document.save()
            Relationship.add_relationship(
                lib_id, subject_id, parent_element_id, document.element_id, RelationshipType.HAS_CHILD
            )
            return document
        except Exception as e:
            logger.error(f"Failed to add document node: {e}")
            raise

    @classmethod
    def delete_documents_of_node(cls, parent_element_id: str):
        """
        Deletes all documents linked to a specified parent node.

        Args:
            parent_element_id (str): The element ID of the parent node.

        Returns:
            Optional[Dict]: The result of the deletion query.

        Raises:
            ValueError: If the deletion fails.
        """
        try:
            query = f"""
                MATCH (p)-[r]->(c:Document) 
                WHERE elementId(p) = $parent_element_id 
                DETACH DELETE r, c
                """
            return graph.query(query, params={"parent_element_id": parent_element_id})
        except Exception as e:
            logger.error(f"Failed to delete documents of node: {e}")
            raise ValueError(_("Failed to delete documents of node."))

    @classmethod
    def delete_document(cls, element_id: str):
        """
        Deletes a specific document by its element ID.

        Args:
            element_id (str): The element ID of the document.

        Returns:
            Optional[Dict]: The result of the deletion query.

        Raises:
            ValueError: If the deletion fails.
        """
        try:
            query = f"""
                MATCH (p)-[r]->(c:Document) 
                WHERE elementId(c) = $element_id 
                DETACH DELETE r, c
                """
            return graph.query(query, params={"element_id": element_id})
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            raise ValueError(_("Failed to delete document."))

    @classmethod
    def get_documents_of_node(cls, parent_element_id: str) -> List["Document"]:
        """
        Retrieves all documents linked to a specified parent node.

        Args:
            parent_element_id (str): The element ID of the parent node.

        Returns:
            List[Document]: A list of Document instances linked to the parent node.

        Raises:
            ValueError: If the query fails.
        """
        try:
            query = f"""
                MATCH (p)-[r]->(document:Document) 
                WHERE elementId(p) = $parent_element_id 
                {Document.return_clause}
                """
            query_result = graph.query(query, params={"parent_element_id": parent_element_id})
            if not query_result:
                return []

            documents: List[Document] = []
            for result in query_result:
                documents.append(cls.to_model(result))
            return documents
        except Exception as e:
            logger.error(f"Failed to get documents: {e}")
            raise ValueError(_("Failed to get documents of node."))

    @classmethod
    def get_documents_by_subject(cls, lib_id: int, subject_id: int) -> List["Document"]:
        """
        Retrieves all documents associated with a specific subject.

        Args:
            lib_id (int): The library ID.
            subject_id (int): The subject ID.

        Returns:
            List[Document]: A list of Document instances associated with the subject.

        Raises:
            ValueError: If the query fails.
        """
        try:
            query = f"""
                MATCH (document:Document) 
                WHERE document.lib_id = $lib_id AND document.subject_id = $subject_id
                {Document.return_clause}
                """
            query_result = graph.query(query, params={"lib_id": lib_id, "subject_id": subject_id})
            if not query_result:
                return []

            documents: List[Document] = []
            for result in query_result:
                documents.append(cls.to_model(result))
            return documents
        except Exception as e:
            logger.error(f"Failed to get documents by subject: {e}")
            raise ValueError(_("Failed to get documents by subject."))

    @classmethod
    def get_documents_by_lib(cls, lib_id: int) -> List["Document"]:
        """
        Retrieves all documents associated with a specific library.

        Args:
            lib_id (int): The library ID.

        Returns:
            List[Document]: A list of Document instances associated with the library.

        Raises:
            ValueError: If the query fails.
        """
        try:
            query = f"""
                MATCH (document:Document) 
                WHERE document.lib_id = $lib_id
                {Document.return_clause}
                """
            query_result = graph.query(query, params={"lib_id": lib_id})
            if not query_result:
                return []

            documents: List[Document] = []
            for result in query_result:
                documents.append(cls.to_model(result))
            return documents
        except Exception as e:
            logger.error(f"Failed to get documents by lib: {e}")
            raise ValueError(_("Failed to get documents by lib."))

    @classmethod
    def get_document_by_element_id(cls, element_id: str) -> Optional["Document"]:
        """
        Retrieves a document by its element ID.

        Args:
            element_id (str): The element ID of the document.

        Returns:
            Optional[Document]: The Document instance if found, otherwise None.

        Raises:
            ValueError: If the query fails.
        """
        try:
            query = f"""
                MATCH (document:Document) 
                WHERE elementId(document) = $element_id
                {Document.return_clause}
                """
            query_result = graph.query(query, params={"element_id": element_id})
            if not query_result:
                return None

            result = query_result[0]
            document: Document = cls.to_model(result)
            document.pages = DocumentPage.get_document_pages_of_parent(document.element_id)

            return document
        except Exception as e:
            logger.error(f"Failed to get document by element_id: {e}")
            raise ValueError(_("Failed to get document by element_id."))

    @classmethod
    def get_parent_element_id_by_document(cls, document_element_id: str) -> Optional[str]:
        """
        Retrieves the parent element ID of a document.

        Args:
            document_element_id (str): The element ID of the document.

        Returns:
            Optional[str]: The element ID of the parent node if found, otherwise None.

        Raises:
            ValueError: If the query fails.
        """
        try:
            query = f"""
                MATCH (p)-[r]->(document:Document) 
                WHERE elementId(document) = $document_element_id 
                RETURN elementId(p) AS parent_element_id
                """
            query_result = graph.query(query, params={"document_element_id": document_element_id})
            if not query_result:
                return None

            result = query_result[0]
            return result["parent_element_id"]
        except Exception as e:
            logger.error(f"Failed to get parent element id by document element_id: {e}")
            raise ValueError(_("Failed to get parent element id by document element_id."))

    @classmethod
    def find_document_by_document_page(cls, document_page_element_id: str) -> Optional["Document"]:
        """
        Retrieves a document by its associated document page element ID.

        Args:
            document_page_element_id (str): The element ID of the document page.

        Returns:
            Optional[Document]: The Document instance if found, otherwise None.

        Raises:
            ValueError: If the query fails.
        """
        try:
            query = f"""
                MATCH (document:Document)-[r]->(documentPage:DocumentPage) 
                WHERE elementId(documentPage) = $document_page_element_id 
                {Document.return_clause}
                """
            query_result = graph.query(query, params={"document_page_element_id": document_page_element_id})
            if not query_result:
                return None

            return cls.to_model(query_result[0])
        except Exception as e:
            logger.error(f"Failed to get document by document page: {e}")
            raise ValueError(_("Failed to get document by document page."))