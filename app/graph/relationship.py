from schemas.graph import GraphConditionView
from core.extends_logger import logger
from core.i18n import _
from datetime import datetime, timezone
from . import RelationshipType, Overview, graph
from typing import List, Optional, Dict, Any, Tuple


class Relationship:
    """
    Represents a relationship between two nodes in the graph database. This class handles the creation,
    updating, and querying of relationships, as well as their properties and metadata.
    """

    # Cypher query clause for returning relationship properties
    return_clause = """
    RETURN 
    elementId(r) AS element_id, 
    id(r) AS id, 
    id(p) AS source, 
    elementId(p) AS source_element_id, 
    id(c) AS target, 
    elementId(c) AS target_element_id, 
    type(r) AS type, 
    r.lib_id as lib_id, 
    r.subject_id as subject_id, 
    r.content as content, 
    r.content_vector as content_vector, 
    r.embedding_model as embedding_model, 
    r.created_at as created_at, 
    r.updated_at as updated_at
    """

    def __init__(self, **kwargs):
        """
        Initializes a Relationship instance with the provided keyword arguments.

        Args:
            **kwargs: Arbitrary keyword arguments to set relationship attributes.
        """
        self.lib_id = kwargs.get("lib_id")  # Library ID associated with the relationship
        self.subject_id = kwargs.get("subject_id")  # Subject ID associated with the relationship
        self.element_id = kwargs.get("element_id")  # Element ID of the relationship
        self.id = kwargs.get("id")  # Internal ID of the relationship
        self.source = kwargs.get("source")  # Source node ID
        self.target = kwargs.get("target")  # Target node ID
        self.source_element_id = kwargs.get("source_element_id")  # Element ID of the source node
        self.target_element_id = kwargs.get("target_element_id")  # Element ID of the target node
        self.type = kwargs.get("type")  # Type of the relationship (e.g., HAS_CHILD)
        self.content = kwargs.get("content")  # Content associated with the relationship
        self.content_vector = kwargs.get("content_vector")  # Vector representation of the content
        self.embedding_model = kwargs.get("embedding_model")  # Embedding model used for the content vector
        self.created_at = kwargs.get("created_at")  # Timestamp when the relationship was created
        self.updated_at = kwargs.get("updated_at")  # Timestamp when the relationship was last updated

    def __repr__(self):
        """
        Returns a string representation of the Relationship instance.

        Returns:
            str: A string representation of the Relationship.
        """
        return (f"Relationship(id={self.id}, element_id={self.element_id}, "
                f"lib_id={self.lib_id}, subject_id={self.subject_id}, "
                f"source={self.source}, target={self.target}, "
                f"source_element_id={self.source_element_id}, "
                f"target_element_id={self.target_element_id}, "
                f"type={self.type.value if self.type else None}, content={self.content})")

    def to_dict(self, filter=None) -> Dict[str, Any]:
        """
        Converts the Relationship instance to a dictionary.

        Args:
            filter (Optional[List[str]]): List of keys to include in the dictionary. If None, all keys are included.

        Returns:
            Dict[str, Any]: A dictionary representation of the Relationship.
        """
        if filter:
            return {key: value for key, value in self.__dict__.items() if key in filter}
        dict = self.__dict__
        dict.update({
            "type": self.type.value if self.type else None
        })
        return dict

    def save(self) -> "Relationship":
        """
        Saves the current relationship to the graph database.

        Returns:
            Relationship: The saved Relationship instance with updated attributes.

        Raises:
            ValueError: If the relationship creation fails.
        """
        try:
            query = f"""
            MATCH (p), (c)
            WHERE elementId(p) = $source_element_id AND elementId(c) = $target_element_id
            CREATE (p)-[r:{self.type.value} {{
            lib_id: $lib_id, 
            subject_id: $subject_id, 
            content: $content, 
            content_vector: $content_vector, 
            embedding_model: $embedding_model,
            created_at: $created_at,
            updated_at: $updated_at}}
            ]->(c)
            {Relationship.return_clause}
            """
            params = {
                "source_element_id": self.source_element_id,
                "target_element_id": self.target_element_id,
                "lib_id": self.lib_id,
                "subject_id": self.subject_id,
                "content": self.content,
                "content_vector": self.content_vector,
                "embedding_model": self.embedding_model,
                "created_at": datetime.now(timezone.utc).timestamp(),
                "updated_at": datetime.now(timezone.utc).timestamp()
            }
            result = graph.query(query, params)
            if not result:
                logger.error("Failed to save Relationship: No result returned from the database.")
                raise ValueError(_("Relationship creation failed with no result."))

            # Update instance attributes with database results
            self.id = result[0].get("id")
            self.element_id = result[0].get("element_id")
            self.lib_id = result[0].get("lib_id")
            self.subject_id = result[0].get("subject_id")
            self.source = result[0].get("source")
            self.target = result[0].get("target")
            self.source_element_id = result[0].get("source_element_id")
            self.target_element_id = result[0].get("target_element_id")
            self.type = RelationshipType(result[0].get("type"))
            self.content = result[0].get("content")
            self.content_vector = result[0].get("content_vector")
            self.embedding_model = result[0].get("embedding_model")
            self.created_at = result[0].get("created_at")
            self.updated_at = result[0].get("updated_at")

            return self
        except Exception as e:
            logger.error(f"Failed to save relationship: {e}")
            raise ValueError(_("Failed to save relationship"))

    def update(self) -> "Relationship":
        """
        Updates the current relationship in the graph database.

        Returns:
            Relationship: The updated Relationship instance.

        Raises:
            ValueError: If the relationship update fails.
        """
        try:
            query = f"""
            MATCH (p)-[r]->(c)
            WHERE elementId(r) = $element_id
            SET r.content = $content, 
            r.content_vector = $content_vector, 
            r.embedding_model = $embedding_model, 
            r.updated_at = $updated_at
            {Relationship.return_clause}
            """
            params = {
                "element_id": self.element_id,
                "content": self.content,
                "content_vector": self.content_vector,
                "embedding_model": self.embedding_model,
                "updated_at": datetime.now(timezone.utc).timestamp()
            }
            result = graph.query(query, params)
            if not result:
                logger.error("Failed to update Relationship: No result returned from the database.")
                raise ValueError(_("Relationship update failed with no result."))

            # Update instance attributes with database results
            self.id = result[0].get("id")
            self.element_id = result[0].get("element_id")
            self.lib_id = result[0].get("lib_id")
            self.subject_id = result[0].get("subject_id")
            self.source = result[0].get("source")
            self.target = result[0].get("target")
            self.source_element_id = result[0].get("source_element_id")
            self.target_element_id = result[0].get("target_element_id")
            self.type = RelationshipType(result[0].get("type"))
            self.content = result[0].get("content")
            self.content_vector = result[0].get("content_vector")
            self.embedding_model = result[0].get("embedding_model")
            self.created_at = result[0].get("created_at")
            self.updated_at = result[0].get("updated_at")

            return self
        except Exception as e:
            logger.error(f"Failed to update Relationship: {e}, Parameters: {params}")
            raise ValueError(_("Failed to update relationship"))

    @classmethod
    def delete(cls, element_id: str):
        """
        Deletes a relationship from the graph database by its element ID.

        Args:
            element_id (str): The element ID of the relationship to delete.

        Raises:
            ValueError: If the relationship deletion fails.
        """
        try:
            query = f"""
            MATCH (p)-[r]->(c)
            WHERE elementId(r) = $element_id
            DETACH DELETE r
            """
            params = {"element_id": element_id}
            graph.query(query, params)
        except Exception as e:
            logger.error(f"Failed to delete relationship: {e}")
            raise ValueError(_("The relationship does not exist."))

    @classmethod
    def add_relationship(cls, lib_id: int, subject_id: int, source_element_id: str, target_element_id: str,
                         type: RelationshipType, content: str = "") -> "Relationship":
        """
        Creates and saves a new relationship in the graph database.

        Args:
            lib_id (int): The library ID.
            subject_id (int): The subject ID.
            source_element_id (str): The element ID of the source node.
            target_element_id (str): The element ID of the target node.
            type (RelationshipType): The type of the relationship.
            content (str, optional): The content associated with the relationship.

        Returns:
            Relationship: The newly created Relationship instance.
        """
        r: Relationship = Relationship(lib_id=lib_id,
                                       subject_id=subject_id,
                                       source_element_id=source_element_id,
                                       target_element_id=target_element_id,
                                       type=type,
                                       content=content)
        return r.save()

    @classmethod
    def delete_relationship(cls, element_id: str):
        """
        Deletes a relationship from the graph database by its element ID.

        Args:
            element_id (str): The element ID of the relationship to delete.

        Returns:
            Optional[Dict]: The result of the deletion query.

        Raises:
            ValueError: If the relationship deletion fails.
        """
        try:
            query = f"""
            MATCH (p)-[r]->(c)
            WHERE elementId(r) = $element_id
            DETACH DELETE r
            """
            params = {"element_id": element_id}
            result = graph.query(query, params)
            return result
        except Exception as e:
            logger.error(f"Failed to delete relationship: {e}")
            raise ValueError(_("The relationship does not exist."))

    @classmethod
    def compose_relationship_query_clause(cls, lib_id: int, subject_ids: List[int] = None, relationship_type:str = None) -> Tuple[str, str, Dict]:
        """
        Composes a Cypher query clause based on the provided conditions.

        Args:
            lib_id (int): The library ID.
            subject_ids (List[int]): The conditions to filter relationships.

        Returns:
            Tuple[str, str, Dict]: A tuple containing the relationship filter, query clause, and parameters.
        """
        query_clause = ""
        params = {"lib_id": lib_id}
        if subject_ids and len(subject_ids) > 0:
            query_clause += " AND p.subject_id IN $subject_ids and c.subject_id IN $subject_ids"
            subject_ids.append(0)
            params["subject_ids"] = subject_ids

        relationship_filter = f":{relationship_type}" if relationship_type else ""

        return relationship_filter, query_clause, params

    @classmethod
    def query_graph_relationship(cls, lib_id: int, subject_ids: List[int] = None, relationship_type:str = None) -> Tuple[List["Relationship"], List[Overview]]:
        """
        Queries and returns relationships based on the provided conditions.

        Args:
            lib_id (int): The library ID.
            subject_ids (List[int]): The conditions to filter relationships.

        Returns:
            Tuple[List[Relationship], List[Overview]]: A tuple containing a list of Relationship instances and a list of Overview instances.

        Raises:
            Exception: If the query fails.
        """
        try:
            if not subject_ids or len(subject_ids) == 0:
                return [], []

            relationship_filter, query_clause, params = cls.compose_relationship_query_clause(lib_id, subject_ids, relationship_type)
            query = f"""
                MATCH (p:Node)-[r{relationship_filter}]->(c:Node)
                WHERE p.lib_id = $lib_id {query_clause}
                {cls.return_clause}
                """
            query_result = graph.query(query, params)
            if query_result:
                links: List[Relationship] = []
                for result in query_result:
                    links.append(Relationship(lib_id=result["lib_id"],
                                              subject_id=result["subject_id"],
                                              element_id=result["element_id"],
                                              source=result["source"],
                                              target=result["target"],
                                              source_element_id=result["source_element_id"],
                                              target_element_id=result["target_element_id"],
                                              type=RelationshipType(result["type"]),
                                              content=result["content"],
                                              content_vector=result["content_vector"],
                                              embedding_model=result["embedding_model"],
                                              created_at=result["created_at"],
                                              updated_at=result["updated_at"]))
            else:
                links = []

            # Query overview
            overviews: List[Overview] = cls.query_graph_relationship_overviews(lib_id, subject_ids, relationship_type)

            return links, overviews
        except Exception as e:
            logger.error(f"Failed to query graph: {e}")
            raise

    @classmethod
    def query_graph_relationship_overviews(cls, lib_id: int, subject_ids: List[int] = None, relationship_type:str = None) -> List[Overview]:
        """
        Queries and returns overviews of relationships based on the provided conditions.

        Args:
            lib_id (int): The library ID.
            subject_ids (List[int]): The conditions to filter relationships.

        Returns:
            List[Overview]: A list of Overview instances representing relationship types and their counts.

        Raises:
            Exception: If the query fails.
        """
        try:
            if not subject_ids or len(subject_ids) == 0:
                return []

            relationship_filter, query_clause, params = cls.compose_relationship_query_clause(lib_id, subject_ids, relationship_type)
            query = f"""
                            MATCH (p)-[r{relationship_filter}]->(c)
                            WHERE p.lib_id = $lib_id {query_clause}
                            RETURN type(r) AS type, COUNT(r) AS count
                        """
            result = graph.query(query, params)
            if not result:
                return []

            overviews: List[Overview] = []
            for r in result:
                overviews.append(Overview(type=r.get("type"), count=r.get("count")))
            return overviews
        except Exception as e:
            logger.error(f"Failed to query_graph_relationship_overview: {e}")
            raise

    @classmethod
    def find_relationship_detail_by_element_id(cls, element_id: str) -> "Relationship":
        """
        Finds and returns detailed information about a relationship by its element ID.

        Args:
            element_id (str): The element ID of the relationship.

        Returns:
            Relationship: The detailed Relationship instance.

        Raises:
            ValueError: If the relationship does not exist.
        """
        try:
            query = f"""
                MATCH (p:Node)-[r]->(c:Node)
                WHERE elementId(r) = $element_id
                {cls.return_clause}
                """
            query_result = graph.query(query, params={"element_id": element_id})
            if not query_result:
                raise ValueError(_("The relationship does not exist."))

            return Relationship(lib_id=query_result[0].get("lib_id"),
                                subject_id=query_result[0].get("subject_id"),
                                element_id=query_result[0].get("element_id"),
                                source=query_result[0].get("source"),
                                target=query_result[0].get("target"),
                                source_element_id=query_result[0].get("source_element_id"),
                                target_element_id=query_result[0].get("target_element_id"),
                                type=RelationshipType(query_result[0].get("type")),
                                content=query_result[0].get("content"),
                                content_vector=query_result[0].get("content_vector"),
                                embedding_model=query_result[0].get("embedding_model"),
                                created_at=query_result[0].get("created_at"),
                                updated_at=query_result[0].get("updated_at"))
        except Exception as e:
            logger.error(f"Failed to get graph relationship detail: {e}")
            raise