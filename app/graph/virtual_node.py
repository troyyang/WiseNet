from datetime import datetime, timezone
from typing import Optional, Dict, Any

from core.extends_logger import logger
from core.i18n import _
from . import BaseNode, BaseModel, RelationshipType, graph
from .relationship import Relationship


class VirtualNode(BaseNode, BaseModel):
    """
    Represents a virtual node in the graph database. This class handles the creation, updating, and querying of virtual nodes,
    which are used as placeholders or temporary nodes in the graph.
    """

    # Cypher query clause for returning virtual node properties
    return_clause = """
        RETURN id(c) AS id, 
        elementId(c) AS element_id, 
        c.lib_id AS lib_id,
        c.subject_id AS subject_id,
        c.title AS title,
        c.content AS content,
        c.title_vector AS title_vector, 
        c.content_vector AS content_vector, 
        c.embedding_model AS embedding_model,
        c.created_at AS created_at, 
        c.updated_at AS updated_at
    """

    def __init__(self, **kwargs):
        """
        Initializes a VirtualNode instance with the provided keyword arguments.

        Args:
            **kwargs: Arbitrary keyword arguments to set virtual node attributes.
        """
        super().__init__(**kwargs)
        self.title = kwargs.get("title")  # Title of the virtual node
        self.title_vector = kwargs.get("title_vector")  # Vector representation of the title

    def __repr__(self):
        """
        Returns a string representation of the VirtualNode instance.

        Returns:
            str: A string representation of the VirtualNode.
        """
        return (f"VirtualNode(lib_id={self.lib_id}, subject_id={self.subject_id}, id={self.id}, "
                f"element_id={self.element_id}, title={self.title}, content={self.content}, "
                f"title_vector={self.title_vector}, content_vector={self.content_vector}, "
                f"embedding_model={self.embedding_model}, created_at={self.created_at}, "
                f"updated_at={self.updated_at})")

    def to_dict(self, filter=None) -> Dict[str, Any]:
        """
        Converts the VirtualNode instance to a dictionary.

        Args:
            filter (Optional[List[str]]): List of keys to include in the dictionary. If None, all keys are included.

        Returns:
            Dict[str, Any]: A dictionary representation of the VirtualNode.
        """
        return super().to_dict(filter)

    @classmethod
    def to_model(cls, result: Dict[str, Any]) -> "VirtualNode":
        """
        Converts a database result item into a VirtualNode instance.

        Args:
            result (Dict): A dictionary representing a virtual node from the database.

        Returns:
            VirtualNode: A VirtualNode instance populated with data from the result item.
        """
        return VirtualNode(**result)

    def save(self) -> "VirtualNode":
        """
        Saves the current virtual node to the graph database.

        Returns:
            VirtualNode: The saved VirtualNode instance with updated attributes.

        Raises:
            ValueError: If the virtual node creation fails.
        """
        try:
            query = f"""
            CREATE (c:VirtualNode {{
                lib_id: $lib_id, 
                subject_id: $subject_id, 
                title: $title, 
                title_vector: $title_vector, 
                content: $content, 
                content_vector: $content_vector, 
                embedding_model: $embedding_model,
                created_at: $created_at, 
                updated_at: $updated_at
            }})
            {VirtualNode.return_clause}
            """
            params = {
                "lib_id": self.lib_id,
                "subject_id": self.subject_id,
                "title": self.title,
                "content": self.content,
                "title_vector": self.title_vector,
                "content_vector": self.content_vector,
                "embedding_model": self.embedding_model,
                "created_at": datetime.now(timezone.utc).timestamp(),
                "updated_at": datetime.now(timezone.utc).timestamp()
            }
            result = graph.query(query, params)
            if not result:
                logger.error("Failed to add virtual node: No result returned from the database.")
                raise ValueError(_("Virtual node creation failed with no result."))

            # Update instance attributes with database results
            self.id = result[0].get("id")
            self.element_id = result[0].get("element_id")
            self.created_at = result[0].get("created_at")
            self.updated_at = result[0].get("updated_at")
            return self
        except Exception as e:
            logger.error(f"Failed to add virtual node: {e}, Parameters: {params}")
            raise

    def update(self) -> "VirtualNode":
        """
        Updates the current virtual node in the graph database.

        Returns:
            VirtualNode: The updated VirtualNode instance.

        Raises:
            ValueError: If the virtual node update fails.
        """
        try:
            query = f"""
            MATCH (c:VirtualNode)
            WHERE elementId(c) = $element_id
            SET
            c.title = $title, 
            c.content = $content, 
            c.title_vector = $title_vector, 
            c.content_vector = $content_vector, 
            c.embedding_model = $embedding_model,
            c.updated_at = $updated_at
            {VirtualNode.return_clause}
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
            result = graph.query(query, params)
            if not result:
                logger.error("Failed to update virtual node: No result returned from the database.")
                raise ValueError(_("Virtual node update failed with no result."))

            # Update instance attributes with database results
            self.id = result[0].get("id")
            self.element_id = result[0].get("element_id")
            self.created_at = result[0].get("created_at")
            self.updated_at = result[0].get("updated_at")
            return self
        except Exception as e:
            logger.error(f"Failed to update virtual node: {e}, Parameters: {params}")
            raise

    def reset(self):
        """
        Resets the virtual node's content and title attributes and updates it in the database.

        Raises:
            ValueError: If the reset operation fails.
        """
        self.title = None
        self.content = None
        self.title_vector = None
        self.content_vector = None
        self.update()

    @classmethod
    def add_virtual_node(cls,
                         lib_id: int,
                         subject_id: int,
                         root_element_id: str) -> "VirtualNode":
        """
        Adds a new virtual node to the graph database and links it to a specified root node.

        Args:
            lib_id (int): The library ID.
            subject_id (int): The subject ID.
            root_element_id (str): The element ID of the root node.

        Returns:
            VirtualNode: The newly created VirtualNode instance.

        Raises:
            ValueError: If the virtual node creation fails.
        """
        try:
            virtual_node: VirtualNode = cls(lib_id=lib_id,
                                            subject_id=subject_id)
            virtual_node = virtual_node.save()
            Relationship.add_relationship(
                lib_id, subject_id, root_element_id, virtual_node.element_id, RelationshipType.HAS_CHILD
            )
            return virtual_node
        except Exception as e:
            logger.error(f"Failed to add virtual node: {e}")
            raise ValueError(_("Failed to add virtual node."))

    @classmethod
    def find_useful_virtual_node(cls, lib_id: int) -> Optional["VirtualNode"]:
        """
        Finds and returns a virtual node that is available for use (i.e., has no content).

        Args:
            lib_id (int): The library ID.

        Returns:
            Optional[VirtualNode]: The VirtualNode instance if found, otherwise None.

        Raises:
            ValueError: If the query fails.
        """
        try:
            query = f"""
                MATCH (c:VirtualNode)
                WHERE c.lib_id = $lib_id AND c.content_vector IS NULL
                {VirtualNode.return_clause}
                LIMIT 1
                """
            params = {"lib_id": lib_id}
            result = graph.query(query, params)

            if not result:
                return None

            virtual_node = cls.to_model(result[0])
            return virtual_node
        except Exception as e:
            logger.error(f"Failed to find useful virtual node: {e}")
            raise ValueError(_("Failed to find useful virtual node."))