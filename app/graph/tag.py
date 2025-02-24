from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from core.extends_logger import logger
from core.i18n import _
from . import BaseNode, BaseModel, RelationshipType, graph
from .relationship import Relationship


class Tag(BaseNode, BaseModel):
    """
    Represents a tag in the graph database. This class handles the creation, updating, and querying of tags,
    as well as their relationships with nodes.
    """

    # Index names for full-text and vector searches
    title_full_text_index_name: str = "tag_title_full_text_index"
    content_full_text_index_name: str = "tag_content_full_text_index"
    lib_id_index_name: str = "tag_lib_id_index"
    subject_id_index_name: str = "tag_subject_id_index"
    title_vector_index_name: str = "tag_title_vector_index"
    content_vector_index_name: str = "tag_content_vector_index"

    # Cypher query clause for returning tag properties
    return_clause = """
        RETURN id(tag) AS id, 
        elementId(tag) AS element_id, 
        tag.lib_id AS lib_id,
        tag.subject_id AS subject_id,
        tag.content AS content, 
        tag.content_vector AS content_vector, 
        tag.embedding_model AS embedding_model,
        tag.created_at AS created_at, 
        tag.updated_at AS updated_at
    """

    def __init__(self, **kwargs):
        """
        Initializes a Tag instance with the provided keyword arguments.

        Args:
            **kwargs: Arbitrary keyword arguments to set tag attributes.
        """
        super().__init__(**kwargs)

    def __repr__(self):
        """
        Returns a string representation of the Tag instance.

        Returns:
            str: A string representation of the Tag.
        """
        repr = super().__repr__()
        return f"Tag({repr})"

    @classmethod
    def to_model(cls, query_item: Dict[str, Any]) -> "Tag":
        """
        Converts a database result item into a Tag instance.

        Args:
            query_item (Dict): A dictionary representing a tag from the database.

        Returns:
            Tag: A Tag instance populated with data from the result item.
        """
        return Tag(**query_item)

    def to_dict(self, filter=None) -> Dict[str, Any]:
        """
        Converts the Tag instance to a dictionary.

        Args:
            filter (Optional[List[str]]): List of keys to include in the dictionary. If None, all keys are included.

        Returns:
            Dict[str, Any]: A dictionary representation of the Tag.
        """
        return super().to_dict(filter)

    def save(self) -> "Tag":
        """
        Saves the current tag to the graph database.

        Returns:
            Tag: The saved Tag instance with updated attributes.

        Raises:
            ValueError: If the tag creation fails.
        """
        try:
            set_vector_clause = self.compose_set_vector_clause("tag")
            query = f"""
            CREATE (tag:Tag {{
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
                "subject_id": 0,  # Default subject_id for tags
                "content": self.content,
                "content_vector": self.content_vector,
                "embedding_model": self.embedding_model,
                "created_at": datetime.now(timezone.utc).timestamp(),
                "updated_at": datetime.now(timezone.utc).timestamp()
            }
            result = graph.query(query, params)
            if not result:
                logger.error("Failed to add Tag Node: No result returned from the database.")
                raise ValueError(_("Tag node creation failed with no result."))

            # Update instance attributes with database results
            self.id = result[0].get("id")
            self.element_id = result[0].get("element_id")
            self.created_at = result[0].get("created_at")
            self.updated_at = result[0].get("updated_at")

            self.create_index("Tag")

            return self
        except Exception as e:
            logger.error(f"Failed to add Tag Node: {e}, Parameters: {params}")
            raise

    @classmethod
    def add_tag_node(cls,
                     lib_id: int,
                     subject_id: int,
                     node_element_id: str,
                     content: str,
                     content_vector: List[float] = None,
                     embedding_model: str = "sbert") -> "Tag":
        """
        Adds a tag node to the graph database and links it to a specified node.

        Args:
            lib_id (int): The library ID.
            subject_id (int): The subject ID.
            node_element_id (str): The element ID of the node to link the tag to.
            content (str): The content of the tag.
            content_vector (List[float], optional): The vector representation of the content.
            embedding_model (str, optional): The embedding model used for the content vector.

        Returns:
            Tag: The newly created or existing Tag instance.
        """
        tag = cls.find_tag_by_content(lib_id, content)
        if not tag:
            tag = Tag(lib_id=lib_id,
                      subject_id=subject_id,
                      content=content,
                      content_vector=content_vector,
                      embedding_model=embedding_model)
            tag = tag.save()

        # Create a relationship between the tag and the node
        Relationship.add_relationship(
            lib_id, subject_id, tag.element_id, node_element_id, RelationshipType.HAS_CHILD
        )
        return tag

    @classmethod
    def find_tag_by_content(cls, lib_id: int, content: str) -> Optional["Tag"]:
        """
        Finds and returns a tag by its content.

        Args:
            lib_id (int): The library ID.
            content (str): The content of the tag.

        Returns:
            Optional[Tag]: The Tag instance if found, otherwise None.

        Raises:
            ValueError: If the query fails.
        """
        try:
            query = f"""
                MATCH (tag:Tag)
                WHERE tag.lib_id = $lib_id AND tag.content = $content
                {cls.return_clause}
                """
            query_result = graph.query(query, params={"lib_id": lib_id, "content": content})
            if not query_result:
                return None

            return cls.to_model(query_result[0])
        except Exception as e:
            logger.error(f"Failed to get tag by content: {e}")
            raise ValueError(_("Failed to get tag by content."))

    @classmethod
    def delete_tags_of_node(cls, node_element_id: str):
        """
        Deletes all tags linked to a specified node.

        Args:
            node_element_id (str): The element ID of the node.

        Returns:
            Optional[Dict]: The result of the deletion query.

        Raises:
            ValueError: If the deletion fails.
        """
        try:
            query = f"""
                MATCH (tag:Tag)-[r]->(node:Node) 
                WHERE elementId(node) = $node_element_id 
                DETACH DELETE r
                """
            return graph.query(query, params={"node_element_id": node_element_id})
        except Exception as e:
            logger.error(f"Failed to delete tags of node: {e}")
            raise ValueError(_("Failed to delete tags of node."))

    @classmethod
    def delete_tag(cls, tag_element_id: str, node_element_id: str):
        """
        Deletes a specific tag linked to a specified node.

        Args:
            tag_element_id (str): The element ID of the tag.
            node_element_id (str): The element ID of the node.

        Returns:
            Optional[Dict]: The result of the deletion query.

        Raises:
            ValueError: If the deletion fails.
        """
        try:
            query = f"""
                MATCH (tag:Tag)-[r]->(node:Node) 
                WHERE elementId(tag) = $tag_element_id AND elementId(node) = $node_element_id 
                DETACH DELETE r
                """
            return graph.query(query, params={"node_element_id": node_element_id, "tag_element_id": tag_element_id})
        except Exception as e:
            logger.error(f"Failed to delete tag: {e}")
            raise ValueError(_("Failed to delete tag."))

    @classmethod
    def get_tags_of_node(cls, node_element_id: str) -> List["Tag"]:
        """
        Retrieves all tags linked to a specified node.

        Args:
            node_element_id (str): The element ID of the node.

        Returns:
            List[Tag]: A list of Tag instances linked to the node.

        Raises:
            ValueError: If the query fails.
        """
        try:
            query = f"""
                MATCH (tag:Tag)-[r]->(node:Node) 
                WHERE elementId(node) = $node_element_id 
                {cls.return_clause}
                """
            query_result = graph.query(query, params={"node_element_id": node_element_id})
            if not query_result:
                return []

            tags: List[Tag] = []
            for result in query_result:
                tags.append(cls.to_model(result))
            return tags
        except Exception as e:
            logger.error(f"Failed to get tags: {e}")
            raise ValueError(_("Failed to get tags of node."))