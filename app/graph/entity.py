from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from core.extends_logger import logger
from core.i18n import _
from . import BaseNode, BaseModel, RelationshipType, graph
from .relationship import Relationship


class Entity(BaseNode, BaseModel):
    """
    Represents an entity in the graph database. This class handles the creation, updating, and querying of entities,
    as well as their relationships with nodes.
    """

    # Index names for full-text and vector searches
    title_full_text_index_name: str = "entity_title_full_text_index"
    content_full_text_index_name: str = "entity_content_full_text_index"
    lib_id_index_name: str = "entity_lib_id_index"
    subject_id_index_name: str = "entity_subject_id_index"
    title_vector_index_name: str = "entity_title_vector_index"
    content_vector_index_name: str = "entity_content_vector_index"

    # Cypher query clause for returning entity properties
    return_clause = """
        RETURN id(entity) AS id, 
        elementId(entity) AS element_id, 
        entity.lib_id AS lib_id,
        entity.subject_id AS subject_id,
        entity.content AS content, 
        entity.content_vector AS content_vector, 
        entity.embedding_model AS embedding_model,
        entity.created_at AS created_at, 
        entity.updated_at AS updated_at
    """

    def __init__(self, **kwargs):
        """
        Initializes an Entity instance with the provided keyword arguments.

        Args:
            **kwargs: Arbitrary keyword arguments to set entity attributes.
        """
        super().__init__(**kwargs)

    def __repr__(self):
        """
        Returns a string representation of the Entity instance.

        Returns:
            str: A string representation of the Entity.
        """
        repr = super().__repr__()
        return f"Entity({repr}, content={self.content})"

    @classmethod
    def to_model(cls, query_item: Dict[str, Any]) -> "Entity":
        """
        Converts a database result item into an Entity instance.

        Args:
            query_item (Dict): A dictionary representing an entity from the database.

        Returns:
            Entity: An Entity instance populated with data from the result item.
        """
        return Entity(**query_item)

    def to_dict(self, filter=None) -> Dict[str, Any]:
        """
        Converts the Entity instance to a dictionary.

        Args:
            filter (Optional[List[str]]): List of keys to include in the dictionary. If None, all keys are included.

        Returns:
            Dict[str, Any]: A dictionary representation of the Entity.
        """
        return super().to_dict(filter)

    def save(self) -> "Entity":
        """
        Saves the current entity to the graph database.

        Returns:
            Entity: The saved Entity instance with updated attributes.

        Raises:
            ValueError: If the entity creation fails.
        """
        try:
            set_vector_clause = self.compose_set_vector_clause("entity")

            query = f"""
            CREATE (entity:Entity {{
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
                "subject_id": 0,  # Default subject_id for entities
                "content": self.content,
                "content_vector": self.content_vector,
                "embedding_model": self.embedding_model,
                "created_at": datetime.now(timezone.utc).timestamp(),
                "updated_at": datetime.now(timezone.utc).timestamp()
            }
            result = graph.query(query, params)
            if not result:
                logger.error("Failed to add Entity Node: No result returned from the database.")
                raise ValueError(_("Entity node creation failed with no result."))

            # Update instance attributes with database results
            self.id = result[0].get("id")
            self.element_id = result[0].get("element_id")
            self.created_at = result[0].get("created_at")
            self.updated_at = result[0].get("updated_at")

            self.create_index("Entity")

            return self
        except Exception as e:
            logger.error(f"Failed to add Entity Node: {e}, Parameters: {params}")
            raise

    @classmethod
    def add_entity_node(cls,
                        lib_id: int,
                        subject_id: int,
                        node_element_id: str,
                        content: str,
                        content_vector: List[float] = None,
                        embedding_model: str = "sbert") -> "Entity":
        """
        Adds an entity node to the graph database and links it to a specified node.

        Args:
            lib_id (int): The library ID.
            subject_id (int): The subject ID.
            node_element_id (str): The element ID of the node to link the entity to.
            content (str): The content of the entity.
            content_vector (List[float], optional): The vector representation of the content.
            embedding_model (str, optional): The embedding model used for the content vector.

        Returns:
            Entity: The newly created or existing Entity instance.
        """
        entity = cls.find_entity_by_content(lib_id, content)
        if not entity:
            entity = Entity(lib_id=lib_id, subject_id=subject_id, content=content, content_vector=content_vector,
                            embedding_model=embedding_model)
            entity = entity.save()

        # Create a relationship between the entity and the node
        Relationship.add_relationship(
            lib_id, 0, entity.element_id, node_element_id, RelationshipType.HAS_CHILD
        )
        return entity

    @classmethod
    def find_entity_by_content(cls, lib_id: int, content: str) -> Optional["Entity"]:
        """
        Finds and returns an entity by its content.

        Args:
            lib_id (int): The library ID.
            content (str): The content of the entity.

        Returns:
            Optional[Entity]: The Entity instance if found, otherwise None.

        Raises:
            ValueError: If the query fails.
        """
        try:
            query = f"""
                MATCH (entity:Entity)
                WHERE entity.lib_id = $lib_id AND entity.content = $content
                {cls.return_clause}
                """
            query_result = graph.query(query, params={"lib_id": lib_id, "content": content})
            if not query_result:
                return None

            return cls.to_model(query_result[0])
        except Exception as e:
            logger.error(f"Failed to get entity by content: {e}")
            raise ValueError(_("Failed to get entity by content."))

    @classmethod
    def delete_entities_of_node(cls, node_element_id: str):
        """
        Deletes all entities linked to a specified node.

        Args:
            node_element_id (str): The element ID of the node.

        Returns:
            Optional[Dict]: The result of the deletion query.

        Raises:
            ValueError: If the deletion fails.
        """
        try:
            query = f"""
                MATCH (entity:Entity)-[r]->(node:Node) 
                WHERE elementId(node) = $node_element_id 
                DETACH DELETE r
                """
            return graph.query(query, params={"node_element_id": node_element_id})
        except Exception as e:
            logger.error(f"Failed to delete entities of node: {e}")
            raise ValueError(_("Failed to delete entities of node."))

    @classmethod
    def delete_entity(cls, entity_element_id: str, node_element_id: str):
        """
        Deletes a specific entity linked to a specified node.

        Args:
            entity_element_id (str): The element ID of the entity.
            node_element_id (str): The element ID of the node.

        Returns:
            Optional[Dict]: The result of the deletion query.

        Raises:
            ValueError: If the deletion fails.
        """
        try:
            query = f"""
                MATCH (entity:Entity)-[r]->(node:Node) 
                WHERE elementId(entity) = $entity_element_id AND elementId(node) = $node_element_id 
                DETACH DELETE r
                """
            return graph.query(query,
                               params={"node_element_id": node_element_id, "entity_element_id": entity_element_id})
        except Exception as e:
            logger.error(f"Failed to delete entity: {e}")
            raise ValueError(_("Failed to delete entity."))

    @classmethod
    def get_entities_of_node(cls, node_element_id: str) -> List["Entity"]:
        """
        Retrieves all entities linked to a specified node.

        Args:
            node_element_id (str): The element ID of the node.

        Returns:
            List[Entity]: A list of Entity instances linked to the node.

        Raises:
            ValueError: If the query fails.
        """
        try:
            query = f"""
                MATCH (entity:Entity)-[r]->(node:Node) 
                WHERE elementId(node) = $node_element_id 
                {cls.return_clause}
                """
            query_result = graph.query(query, params={"node_element_id": node_element_id})
            if not query_result:
                return []

            entities: List[Entity] = []
            for result in query_result:
                entities.append(cls.to_model(result))
            return entities
        except Exception as e:
            logger.error(f"Failed to get entities: {e}")
            raise ValueError(_("Failed to get entities of node."))