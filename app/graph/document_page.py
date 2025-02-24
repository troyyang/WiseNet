from core.extends_logger import logger
from core.i18n import _
from . import BaseNode, BaseModel, RelationshipType, graph
from .relationship import Relationship
from typing import List, Optional, Dict, Any


class DocumentPage(BaseNode, BaseModel):
    """
    Represents a document page in the graph database. This class handles the creation, updating, and querying of document pages,
    as well as their relationships with parent nodes.
    """

    # Index names for full-text and vector searches
    title_full_text_index_name: str = "document_page_title_full_text_index"
    content_full_text_index_name: str = "document_page_content_full_text_index"
    lib_id_index_name: str = "document_page_lib_id_index"
    subject_id_index_name: str = "document_page_subject_id_index"
    title_vector_index_name: str = "document_page_title_vector_index"
    content_vector_index_name: str = "document_page_content_vector_index"

    return_clause = """
        RETURN id(documentPage) AS id, 
        elementId(documentPage) AS element_id, 
        documentPage.lib_id AS lib_id,
        documentPage.subject_id AS subject_id,
        documentPage.source AS source, 
        documentPage.title AS title,
        documentPage.subtitle AS subtitle,
        documentPage.row AS row,
        documentPage.page AS page,
        documentPage.content AS content,
        documentPage.title_vector AS title_vector, 
        documentPage.content_vector AS content_vector, 
        documentPage.embedding_model AS embedding_model,
        documentPage.created_at AS created_at, 
        documentPage.updated_at AS updated_at
    """

    def __init__(self, **kwargs):
        """
        Initializes a DocumentPage instance with the provided keyword arguments.

        Args:
            **kwargs: Arbitrary keyword arguments to set document page attributes.
        """
        super().__init__(**kwargs)
        self.source = kwargs.get("source")  # Source of the document page
        self.title = kwargs.get("title")  # Title of the document page
        self.subtitle = kwargs.get("subtitle")  # Subtitle of the document page
        self.row = kwargs.get("row")  # Row number of the document page
        self.page = kwargs.get("page")  # Page number of the document page

    def __repr__(self):
        """
        Returns a string representation of the DocumentPage instance.

        Returns:
            str: A string representation of the DocumentPage.
        """
        return (f"DocumentPage(id={self.id}, source={self.source}, "
                f"title={self.title}, subtitle={self.subtitle}, page={self.page})")

    @classmethod
    def to_model(cls, query_item: Dict[str, Any]) -> "DocumentPage":
        """
        Converts a database result item into a DocumentPage instance.

        Args:
            query_item (Dict): A dictionary representing a document page from the database.

        Returns:
            DocumentPage: A DocumentPage instance populated with data from the result item.
        """
        return DocumentPage(**query_item)

    def to_dict(self, filter=None) -> Dict[str, Any]:
        """
        Converts the DocumentPage instance to a dictionary.

        Args:
            filter (Optional[List[str]]): List of keys to include in the dictionary. If None, all keys are included.

        Returns:
            Dict[str, Any]: A dictionary representation of the DocumentPage.
        """
        return super().to_dict(filter)

    def save(self) -> "DocumentPage":
        """
        Saves the current document page to the graph database.

        Returns:
            DocumentPage: The saved DocumentPage instance with updated attributes.

        Raises:
            ValueError: If the document page creation fails.
        """
        try:
            set_vector_clause = self.compose_set_vector_clause("documentPage")
            query = f"""
            CREATE (documentPage:DocumentPage {{
                lib_id: $lib_id, 
                subject_id: $subject_id, 
                source: $source, 
                title: $title, 
                subtitle: $subtitle, 
                row: $row, 
                page: $page, 
                content: $content, 
                content_vector: $content_vector, 
                embedding_model: $embedding_model,
                created_at: $created_at, 
                updated_at: $updated_at
            }})
            {set_vector_clause}
            {self.return_clause}
            """
            params = {
                "lib_id": self.lib_id,
                "subject_id": self.subject_id,
                "source": self.source,
                "title": self.title,
                "subtitle": self.subtitle,
                "row": self.row,
                "page": self.page,
                "content": self.content,
                "content_vector": self.content_vector,
                "embedding_model": self.embedding_model,
                "created_at": self.created_at,
                "updated_at": self.updated_at
            }
            result = graph.query(query, params=params)
            if not result:
                logger.error("Failed to save document page: No result returned from the database.")
                raise ValueError(_("Document page creation failed with no result."))

            # Update instance attributes with database results
            self.id = result[0].get("id")
            self.element_id = result[0].get("element_id")
            self.created_at = result[0].get("created_at")
            self.updated_at = result[0].get("updated_at")

            self.create_index("DocumentPage")

            return self
        except Exception as e:
            logger.error(f"Failed to save document page: {e}")
            raise ValueError(_("Failed to save document page."))

    @classmethod
    def add_document_page_node(cls, lib_id: int, subject_id: int, parent_element_id: str, document_element_id: str,
                               source: str, title: str, subtitle: str, row: int, page: int, content: str,
                               content_vector: List[float] = None, embedding_model: str = None) -> "DocumentPage":
        """
        Adds a new document page node and establishes relationships with parent nodes.

        Args:
            lib_id (int): The library ID.
            subject_id (int): The subject ID.
            parent_element_id (str): The element ID of the parent node.
            document_element_id (str): The element ID of the document node.
            source (str): The source of the document page.
            title (str): The title of the document page.
            subtitle (str): The subtitle of the document page.
            row (int): The row number of the document page.
            page (int): The page number of the document page.
            content (str): The content of the document page.
            content_vector (List[float], optional): The vector representation of the content.
            embedding_model (str, optional): The embedding model used for the content vector.

        Returns:
            DocumentPage: The newly created DocumentPage instance.

        Raises:
            ValueError: If the document page creation fails.
        """
        try:
            document_page = cls(lib_id=lib_id, subject_id=subject_id, source=source, title=title, subtitle=subtitle,
                                row=row, page=page, content=content, content_vector=content_vector,
                                embedding_model=embedding_model).save()

            cls._add_relationships(document_page.element_id, lib_id, subject_id, [parent_element_id, document_element_id])

            return document_page
        except Exception as e:
            logger.error(f"Failed to add document page node: {e}")
            raise ValueError(_("Failed to add document page node."))

    @staticmethod
    def _add_relationships(element_id: str, lib_id: int, subject_id: int, target_ids: List[str]):
        """
        Helper method to create HAS_CHILD relationships between nodes.

        Args:
            element_id (str): The element ID of the source node.
            lib_id (int): The library ID.
            subject_id (int): The subject ID.
            target_ids (List[str]): A list of target element IDs to create relationships with.

        Raises:
            ValueError: If the relationship creation fails.
        """
        try:
            for target_id in target_ids:
                Relationship.add_relationship(lib_id, subject_id, target_id, element_id, RelationshipType.HAS_CHILD)
        except Exception as e:
            logger.error(f"Failed to add relationships: {e}")
            raise ValueError(_("Failed to add relationships."))

    @classmethod
    def delete_document_pages_of_parent(cls, parent_element_id: str):
        """
        Deletes all document pages associated with a given parent node.

        Args:
            parent_element_id (str): The element ID of the parent node.

        Raises:
            ValueError: If the deletion fails.
        """
        try:
            query = """
                MATCH (p)-[r]->(documentPage:DocumentPage) 
                WHERE elementId(p) = $parent_element_id 
                DETACH DELETE r, documentPage
            """
            graph.query(query, params={"parent_element_id": parent_element_id})
        except Exception as e:
            logger.error(f"Failed to delete document pages of parent: {e}")
            raise ValueError(_("Failed to delete document pages of parent."))

    @classmethod
    def delete_document_page(cls, element_id: str):
        """
        Deletes a specific document page by its element ID.

        Args:
            element_id (str): The element ID of the document page.

        Raises:
            ValueError: If the deletion fails.
        """
        try:
            query = """
                MATCH (p)-[r]->(documentPage:DocumentPage) 
                WHERE elementId(documentPage) = $element_id 
                DETACH DELETE r, documentPage
            """
            graph.query(query, params={"element_id": element_id})
        except Exception as e:
            logger.error(f"Failed to delete document page by element_id: {e}")
            raise ValueError(_("Failed to delete document page by element_id."))

    @classmethod
    def get_document_pages_of_parent(cls, document_element_id: str) -> List["DocumentPage"]:
        """
        Retrieves all document pages associated with a given parent node.

        Args:
            document_element_id (str): The element ID of the parent node.

        Returns:
            List[DocumentPage]: A list of DocumentPage instances associated with the parent node.

        Raises:
            ValueError: If the query fails.
        """
        try:
            query = f"""
                MATCH (p)-[r]->(documentPage:DocumentPage) 
                WHERE elementId(p) = $document_element_id 
                {cls.return_clause}
            """
            results = graph.query(query, params={"document_element_id": document_element_id})
            return [cls.to_model(result) for result in results]
        except Exception as e:
            logger.error(f"Failed to get document pages of document: {e}")
            raise ValueError(_("Failed to get document pages of document."))