from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from core.extends_logger import logger
from core.i18n import _
from . import BaseNode, BaseModel, RelationshipType, graph
from .relationship import Relationship


class Keyword(BaseNode, BaseModel):
    """
    Represents a keyword in the graph database. This class handles the creation, updating, and querying of keywords,
    as well as their relationships with nodes.
    """

    # Index names for full-text and vector searches
    title_full_text_index_name: str = "keyword_title_full_text_index"
    content_full_text_index_name: str = "keyword_content_full_text_index"
    lib_id_index_name: str = "keyword_lib_id_index"
    subject_id_index_name: str = "keyword_subject_id_index"
    title_vector_index_name: str = "keyword_title_vector_index"
    content_vector_index_name: str = "keyword_content_vector_index"

    # Cypher query clause for returning keyword properties
    return_clause = """
        RETURN id(keyword) AS id, 
        elementId(keyword) AS element_id, 
        keyword.lib_id AS lib_id,
        keyword.subject_id AS subject_id,
        keyword.content AS content, 
        keyword.content_vector AS content_vector, 
        keyword.embedding_model AS embedding_model,
        keyword.created_at AS created_at, 
        keyword.updated_at AS updated_at
    """

    def __init__(self, **kwargs):
        """
        Initializes a Keyword instance with the provided keyword arguments.

        Args:
            **kwargs: Arbitrary keyword arguments to set keyword attributes.
        """
        super().__init__(**kwargs)

    def __repr__(self):
        """
        Returns a string representation of the Keyword instance.

        Returns:
            str: A string representation of the Keyword.
        """
        repr = super().__repr__()
        return f"Keyword({repr})"

    @classmethod
    def to_model(cls, query_item: Dict[str, Any]) -> "Keyword":
        """
        Converts a database result item into a Keyword instance.

        Args:
            query_item (Dict): A dictionary representing a keyword from the database.

        Returns:
            Keyword: A Keyword instance populated with data from the result item.
        """
        return Keyword(**query_item)

    def to_dict(self, filter=None) -> Dict[str, Any]:
        """
        Converts the Keyword instance to a dictionary.

        Args:
            filter (Optional[List[str]]): List of keys to include in the dictionary. If None, all keys are included.

        Returns:
            Dict[str, Any]: A dictionary representation of the Keyword.
        """
        return super().to_dict(filter)

    def save(self) -> "Keyword":
        """
        Saves the current keyword to the graph database.

        Returns:
            Keyword: The saved Keyword instance with updated attributes.

        Raises:
            ValueError: If the keyword creation fails.
        """
        try:
            set_vector_clause = self.compose_set_vector_clause("keyword")
            query = f"""
            CREATE (keyword:Keyword {{
                lib_id: $lib_id, 
                subject_id: $subject_id, 
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
                "subject_id": 0,  # Default subject_id for keywords
                "content": self.content,
                "content_vector": self.content_vector,
                "embedding_model": self.embedding_model,
                "created_at": datetime.now(timezone.utc).timestamp(),
                "updated_at": datetime.now(timezone.utc).timestamp()
            }
            result = graph.query(query, params)
            if not result:
                logger.error("Failed to add Keyword Node: No result returned from the database.")
                raise ValueError(_("Keyword node creation failed with no result."))

            # Update instance attributes with database results
            self.id = result[0].get("id")
            self.element_id = result[0].get("element_id")
            self.created_at = result[0].get("created_at")
            self.updated_at = result[0].get("updated_at")

            self.create_index("Keyword")

            return self
        except Exception as e:
            logger.error(f"Failed to add Keyword Node: {e}, Parameters: {params}")
            raise

    @classmethod
    def add_keyword_node(cls, lib_id: int, subject_id: int,
                         node_element_id: str,
                         content: str,
                         content_vector: List[float] = None,
                         embedding_model: str = "sbert") -> "Keyword":
        """
        Adds a keyword node to the graph database and links it to a specified node.

        Args:
            lib_id (int): The library ID.
            subject_id (int): The subject ID.
            node_element_id (str): The element ID of the node to link the keyword to.
            content (str): The content of the keyword.
            content_vector (List[float], optional): The vector representation of the content.
            embedding_model (str, optional): The embedding model used for the content vector.

        Returns:
            Keyword: The newly created or existing Keyword instance.
        """
        keyword = cls.find_keyword_by_content(lib_id, content)
        if not keyword:
            keyword = Keyword(lib_id=lib_id,
                              subject_id=subject_id,
                              content=content,
                              content_vector=content_vector,
                              embedding_model=embedding_model)
            keyword = keyword.save()

        # Create a relationship between the keyword and the node
        Relationship.add_relationship(
            lib_id, 0, keyword.element_id, node_element_id, RelationshipType.HAS_CHILD
        )
        return keyword

    @classmethod
    def find_keyword_by_content(cls, lib_id: int, content: str) -> Optional["Keyword"]:
        """
        Finds and returns a keyword by its content.

        Args:
            lib_id (int): The library ID.
            content (str): The content of the keyword.

        Returns:
            Optional[Keyword]: The Keyword instance if found, otherwise None.

        Raises:
            ValueError: If the query fails.
        """
        try:
            query = f"""
                MATCH (keyword:Keyword)
                WHERE keyword.lib_id = $lib_id AND keyword.content = $content
                {cls.return_clause}
                """
            query_result = graph.query(query, params={"lib_id": lib_id, "content": content})
            if not query_result:
                return None

            return cls.to_model(query_result[0])
        except Exception as e:
            logger.error(f"Failed to get keyword by content: {e}")
            raise ValueError(_("Failed to get keyword by content."))

    @classmethod
    def delete_keywords_of_node(cls, node_element_id: str):
        """
        Deletes all keywords linked to a specified node.

        Args:
            node_element_id (str): The element ID of the node.

        Returns:
            Optional[Dict]: The result of the deletion query.

        Raises:
            ValueError: If the deletion fails.
        """
        try:
            query = f"""
                MATCH (keyword:Keyword)-[r]->(node:Node) 
                WHERE elementId(node) = $node_element_id 
                DETACH DELETE r
                """
            return graph.query(query, params={"node_element_id": node_element_id})
        except Exception as e:
            logger.error(f"Failed to delete keywords of node: {e}")
            raise ValueError(_("Failed to delete keywords of node."))

    @classmethod
    def delete_keyword(cls, keyword_element_id: str, node_element_id: str):
        """
        Deletes a specific keyword linked to a specified node.

        Args:
            keyword_element_id (str): The element ID of the keyword.
            node_element_id (str): The element ID of the node.

        Returns:
            Optional[Dict]: The result of the deletion query.

        Raises:
            ValueError: If the deletion fails.
        """
        try:
            query = f"""
                MATCH (keyword:Keyword)-[r]->(node:Node) 
                WHERE elementId(keyword) = $keyword_element_id AND elementId(node) = $node_element_id 
                DETACH DELETE r
                """
            return graph.query(query,
                               params={"node_element_id": node_element_id, "keyword_element_id": keyword_element_id})
        except Exception as e:
            logger.error(f"Failed to delete keyword: {e}")
            raise ValueError(_("Failed to delete keyword."))

    @classmethod
    def get_keywords_of_node(cls, node_element_id: str) -> List["Keyword"]:
        """
        Retrieves all keywords linked to a specified node.

        Args:
            node_element_id (str): The element ID of the node.

        Returns:
            List[Keyword]: A list of Keyword instances linked to the node.

        Raises:
            ValueError: If the query fails.
        """
        try:
            query = f"""
                MATCH (keyword:Keyword)-[r]->(node:Node) 
                WHERE elementId(node) = $node_element_id 
                {cls.return_clause}
                """
            query_result = graph.query(query, params={"node_element_id": node_element_id})
            if not query_result:
                return []

            keywords: List[Keyword] = []
            for result in query_result:
                keywords.append(cls.to_model(result))
            return keywords
        except Exception as e:
            logger.error(f"Failed to get keywords: {e}")
            raise ValueError(_("Failed to get keywords of node."))