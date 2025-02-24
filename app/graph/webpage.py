from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from core.extends_logger import logger
from core.i18n import _
from . import BaseNode, BaseModel, RelationshipType, graph
from .document_page import DocumentPage
from .relationship import Relationship


class WebPage(BaseNode, BaseModel):
    """
    Represents a webpage in the graph database. This class handles the creation, updating, and querying of webpages,
    as well as their relationships with nodes and document pages.
    """

    # Index names for full-text and vector searches
    title_full_text_index_name: str = "web_page_title_full_text_index"
    content_full_text_index_name: str = "web_page_content_full_text_index"
    lib_id_index_name: str = "web_page_lib_id_index"
    subject_id_index_name: str = "web_page_subject_id_index"
    title_vector_index_name: str = "web_page_title_vector_index"
    content_vector_index_name: str = "web_page_content_vector_index"

    # Cypher query clause for returning webpage properties
    return_clause = """
        RETURN id(webPage) AS id, 
        elementId(webPage) AS element_id, 
        webPage.lib_id AS lib_id, 
        webPage.subject_id AS subject_id, 
        webPage.title AS title,
        webPage.url AS url, 
        webPage.content AS content, 
        webPage.title_vector AS title_vector, 
        webPage.content_vector AS content_vector, 
        webPage.embedding_model AS embedding_model,
        webPage.created_at AS created_at, 
        webPage.updated_at AS updated_at
    """

    def __init__(self, **kwargs):
        """
        Initializes a WebPage instance with the provided keyword arguments.

        Args:
            **kwargs: Arbitrary keyword arguments to set webpage attributes.
        """
        super().__init__(**kwargs)
        self.url = kwargs.get("url")  # URL of the webpage
        self.title = kwargs.get("title")  # Title of the webpage
        self.title_vector = kwargs.get("title_vector")  # Vector representation of the title
        self.pages: List[DocumentPage] = []  # List of document pages associated with the webpage

    def __repr__(self):
        """
        Returns a string representation of the WebPage instance.

        Returns:
            str: A string representation of the WebPage.
        """
        repr = super().__repr__()
        return f"WebPage({repr}, title={self.title}, url={self.url})"

    @classmethod
    def to_model(cls, query_item: Dict[str, Any]) -> "WebPage":
        """
        Converts a database result item into a WebPage instance.

        Args:
            query_item (Dict): A dictionary representing a webpage from the database.

        Returns:
            WebPage: A WebPage instance populated with data from the result item.
        """
        return WebPage(**query_item)

    def to_dict(self, filter=None) -> Dict[str, Any]:
        """
        Converts the WebPage instance to a dictionary.

        Args:
            filter (Optional[List[str]]): List of keys to include in the dictionary. If None, all keys are included.

        Returns:
            Dict[str, Any]: A dictionary representation of the WebPage.
        """
        dict = super().to_dict(filter)
        dict.update({
            "pages": super()._to_dict_list(self.pages, DocumentPage, filter.get("pages.page", None) if filter else None) if self.pages and (not filter or "pages" in filter) else []
        })
        return dict

    def save(self) -> "WebPage":
        """
        Saves the current webpage to the graph database.

        Returns:
            WebPage: The saved WebPage instance with updated attributes.

        Raises:
            ValueError: If the webpage creation fails.
        """
        try:
            set_vector_clause = self.compose_set_vector_clause("webPage")
            query = f"""
            CREATE (webPage:WebPage {{
                lib_id: $lib_id, 
                subject_id: $subject_id, 
                url: $url, 
                title: $title, 
                content: $content, 
                title_vector: $title_vector, 
                content_vector: $content_vector, 
                embedding_model: $embedding_model,
                created_at: $created_at, 
                updated_at: $updated_at
            }})
            {set_vector_clause}
            {WebPage.return_clause}
            """
            params = {
                "lib_id": self.lib_id,
                "subject_id": self.subject_id,
                "url": self.url,
                "title": self.title,
                "content": self.content,
                "title_vector": self.title_vector,
                "content_vector": self.content_vector,
                "embedding_model": self.embedding_model,
                "created_at": datetime.now(timezone.utc).timestamp(),
                "updated_at": datetime.now(timezone.utc).timestamp()
            }
            result = graph.query(query, params=params)
            if not result:
                logger.error("Failed to save webpage: No result returned from the database.")
                raise ValueError(_("Webpage creation failed with no result."))

            # Update instance attributes with database results
            self.id = result[0].get("id")
            self.element_id = result[0].get("element_id")
            self.created_at = result[0].get("created_at")
            self.updated_at = result[0].get("updated_at")

            self.create_index("WebPage")

            return self
        except Exception as e:
            logger.error(f"Failed to save webpage: {e}")
            raise ValueError(_("Failed to save webpage."))

    def update(self) -> "WebPage":
        """
        Updates the current webpage in the graph database.

        Returns:
            WebPage: The updated WebPage instance.

        Raises:
            ValueError: If the webpage update fails.
        """
        try:
            set_vector_clause = self.compose_set_vector_clause("webPage")
            query = f"""
            MATCH (webPage:WebPage)
            WHERE elementId(webPage) = $element_id
            SET webPage.title = $title, 
            webPage.content = $content, 
            webPage.title_vector = $title_vector, 
            webPage.content_vector = $content_vector, 
            webPage.embedding_model = $embedding_model,
            webPage.updated_at = $updated_at
            {set_vector_clause}
            {WebPage.return_clause}
            """
            params = {
                "element_id": self.element_id,
                "title": self.title,
                "content": self.content,
                "title_vector": self.title_vector,
                "content_vector": self.content_vector,
                "embedding_model": self.embedding_model,
                "updated_at": datetime.now(timezone.utc).timestamp()
            }
            result = graph.query(query, params=params)
            if not result:
                logger.error("Failed to update webpage: No result returned from the database.")
                raise ValueError(_("Webpage update failed with no result."))

            # Update instance attributes with database results
            self.id = result[0].get("id")
            self.element_id = result[0].get("element_id")
            self.created_at = result[0].get("created_at")
            self.updated_at = result[0].get("updated_at")
            return self
        except Exception as e:
            logger.error(f"Failed to update webpage: {e}, Parameters: {params}")
            raise

    @classmethod
    def add_webpage_node(cls, lib_id: int,
                         subject_id: int,
                         parent_element_id: str,
                         url: str) -> "WebPage":
        """
        Adds a webpage node to the graph database and links it to a specified parent node.

        Args:
            lib_id (int): The library ID.
            subject_id (int): The subject ID.
            parent_element_id (str): The element ID of the parent node.
            url (str): The URL of the webpage.

        Returns:
            WebPage: The newly created WebPage instance.

        Raises:
            Exception: If the webpage creation fails.
        """
        try:
            web_page = WebPage(lib_id=lib_id,
                               subject_id=subject_id,
                               url=url)
            web_page = web_page.save()
            Relationship.add_relationship(
                lib_id, subject_id, parent_element_id, web_page.element_id, RelationshipType.HAS_CHILD
            )
            return web_page
        except Exception as e:
            logger.error(f"Failed to add webpage node: {e}")
            raise

    @classmethod
    def delete_webpages_of_node(cls, parent_element_id: str):
        """
        Deletes all webpages linked to a specified parent node.

        Args:
            parent_element_id (str): The element ID of the parent node.

        Raises:
            ValueError: If the deletion fails.
        """
        try:
            # Delete all document pages in the webpage node
            webpages: List[WebPage] = cls.get_webpages_of_node(parent_element_id)
            if webpages:
                for webpage in webpages:
                    cls.delete_webpage(webpage.element_id)

            # Delete all document pages in the parent node of the webpage
            DocumentPage.delete_document_pages_of_parent(parent_element_id)
        except Exception as e:
            logger.error(f"Failed to delete webpages of node: {e}")
            raise ValueError(_("Failed to delete webpages of node."))

    @classmethod
    def delete_webpage(cls, element_id: str):
        """
        Deletes a specific webpage by its element ID.

        Args:
            element_id (str): The element ID of the webpage.

        Raises:
            ValueError: If the deletion fails.
        """
        try:
            # Delete all document pages associated with the webpage
            DocumentPage.delete_document_pages_of_parent(element_id)

            # Delete the webpage
            query = f"""
                MATCH (p)-[r]->(webPage:WebPage) 
                WHERE elementId(webPage) = $element_id 
                DETACH DELETE r, webPage
                """
            graph.query(query, params={"element_id": element_id})
        except Exception as e:
            logger.error(f"Failed to delete webpage by element_id: {e}")
            raise ValueError(_("Failed to delete webpage by element_id."))

    @classmethod
    def get_webpages_of_node(cls, parent_element_id: str) -> List["WebPage"]:
        """
        Retrieves all webpages linked to a specified parent node.

        Args:
            parent_element_id (str): The element ID of the parent node.

        Returns:
            List[WebPage]: A list of WebPage instances linked to the parent node.

        Raises:
            ValueError: If the query fails.
        """
        try:
            query = f"""
                MATCH (p)-[r]->(webPage:WebPage) 
                WHERE elementId(p) = $parent_element_id 
                {WebPage.return_clause}
                """
            query_result = graph.query(query, params={"parent_element_id": parent_element_id})
            if not query_result:
                return []

            webpages: List[WebPage] = []
            for result in query_result:
                webpages.append(cls.to_model(result))
            return webpages
        except Exception as e:
            logger.error(f"Failed to get webpages of node: {e}")
            raise ValueError(_("Failed to get webpages of node."))

    @classmethod
    def get_webpage_by_element_id(cls, element_id: str) -> Optional["WebPage"]:
        """
        Retrieves a webpage by its element ID.

        Args:
            element_id (str): The element ID of the webpage.

        Returns:
            Optional[WebPage]: The WebPage instance if found, otherwise None.

        Raises:
            ValueError: If the query fails.
        """
        try:
            query = f"""
                MATCH (p)-[r]->(webPage:WebPage) 
                WHERE elementId(webPage) = $element_id 
                {WebPage.return_clause}
                """
            query_result = graph.query(query, params={"element_id": element_id})
            if not query_result:
                return None

            result = query_result[0]
            webpage: WebPage = cls.to_model(result)
            # The webpage also acts as a document, so fetch its associated pages
            webpage.pages = DocumentPage.get_document_pages_of_parent(element_id)
            return webpage
        except Exception as e:
            logger.error(f"Failed to get webpage by element_id: {e}")
            raise ValueError(_("Failed to get webpage by element_id."))

    @classmethod
    def get_parent_element_id(cls, webpage_element_id: str) -> Optional[str]:
        """
        Retrieves the parent element ID of a webpage.

        Args:
            webpage_element_id (str): The element ID of the webpage.

        Returns:
            Optional[str]: The element ID of the parent node if found, otherwise None.

        Raises:
            ValueError: If the query fails.
        """
        try:
            query = f"""
                MATCH (p)-[r]->(webPage:WebPage) 
                WHERE elementId(webPage) = $webpage_element_id 
                RETURN elementId(p) AS parent_element_id
                """
            query_result = graph.query(query, params={"webpage_element_id": webpage_element_id})
            if not query_result:
                return None

            result = query_result[0]
            return result["parent_element_id"]
        except Exception as e:
            logger.error(f"Failed to get parent element id by webpage element_id: {e}")
            raise ValueError(_("Failed to get parent element id by webpage element_id."))

    @classmethod
    def find_webpage_by_document_page(cls, document_page_element_id: str) -> Optional["WebPage"]:
        """
        Retrieves a webpage by its associated document page element ID.

        Args:
            document_page_element_id (str): The element ID of the document page.

        Returns:
            Optional[WebPage]: The WebPage instance if found, otherwise None.

        Raises:
            ValueError: If the query fails.
        """
        try:
            query = f"""
                MATCH (webPage:WebPage)-[r]->(documentPage:DocumentPage) 
                WHERE elementId(documentPage) = $document_page_element_id 
                {WebPage.return_clause}
                """
            query_result = graph.query(query, params={"document_page_element_id": document_page_element_id})
            if not query_result:
                return None

            return cls.to_model(query_result[0])
        except Exception as e:
            logger.error(f"Failed to get webpage by document page: {e}")
            raise ValueError(_("Failed to get webpage by document page."))