from enum import Enum
from typing import Optional, List, Dict, Any
import logging
from langchain_neo4j import Neo4jGraph
from core.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from core.extends_logger import logger
from core.i18n import _
from abc import ABC, abstractmethod
import reprlib


logging.getLogger("neo4j").setLevel(logging.ERROR)
graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD,
                   driver_config={"max_connection_pool_size": 100, "max_transaction_retry_time": 10})


class RelationshipType(Enum):
    """Enum representing different relationship types in the graph database."""
    HAS_CHILD = "HAS_CHILD"
    RELATED_TO = "RELATED_TO"


class NodeType(Enum):
    """Enum representing different node types in the graph database."""
    ROOT = "ROOT"
    SUBJECT = "SUBJECT"
    PROMPT = "PROMPT"
    INFO = "INFO"
    HUMAN = "HUMAN"
    QUESTION = "QUESTION"


class DatabaseError(Exception):
    """Custom exception for database - related errors."""
    pass


class BaseModel:
    vector_dimensions = 768
    similarity_function = "cosine"
    lib_id_index_name = "lib_id_index"
    subject_id_index_name = "subject_id_index"
    content_vector_index_name = "content_vector_index"
    title_vector_index_name = "title_vector_index"

    def compose_set_vector_clause(self, node_name):
        """
        Compose Cypher clauses to set vector properties on a node.

        :param node_name: The name of the node in the Cypher query.
        :return: A string containing the composed Cypher clauses.
        """
        clauses = []
        for attr, vector in [("title_vector", getattr(self, 'title_vector', None)),
                             ("content_vector", getattr(self, 'content_vector', None))]:
            if vector is not None and len(vector) > 0:
                clauses.append(
                    f""" WITH {node_name} CALL db.create.setNodeVectorProperty({node_name}, '{attr}', ${attr})""")
        return "\n".join(clauses)

    def create_index(self, node_label):
        """
        Create necessary indexes for a given node label.

        :param node_label: The label of the node for which indexes are to be created.
        :raises DatabaseError: If there is an error during index creation.
        """
        queries = [
            f"""CREATE INDEX {self.lib_id_index_name} IF NOT EXISTS FOR (n:{node_label}) ON (n.lib_id);""",
            f"""CREATE INDEX {self.subject_id_index_name} IF NOT EXISTS FOR (n:{node_label}) ON (n.subject_id);""",
            f"""CREATE FULLTEXT INDEX {self.content_full_text_index_name} IF NOT EXISTS 
            FOR (n:{node_label}) ON EACH [n.content]
            OPTIONS {{
            indexConfig: {{
                `fulltext.analyzer`: 'standard',
                `fulltext.eventually_consistent`: true
            }}
            }};""", 
            f"""CREATE VECTOR INDEX {self.content_vector_index_name} IF NOT EXISTS 
            FOR (node:{node_label})
            ON (node.content_vector)
            OPTIONS {{ indexConfig: {{
            `vector.dimensions`: {self.vector_dimensions},
            `vector.similarity_function`: '{self.similarity_function}'
            }}
            }};""",
        ]

        if hasattr(self, 'title_vector'):
            queries.append(f"""CREATE FULLTEXT INDEX {self.title_full_text_index_name} IF NOT EXISTS 
            FOR (n:{node_label}) ON EACH [n.title]
            OPTIONS {{
            indexConfig: {{
                `fulltext.analyzer`: 'standard',
                `fulltext.eventually_consistent`: true
            }}
            }};""")
            queries.append(f"""CREATE VECTOR INDEX {self.title_vector_index_name} IF NOT EXISTS 
            FOR (node:{node_label})
            ON (node.title_vector)
            OPTIONS {{ indexConfig: {{
            `vector.dimensions`: {self.vector_dimensions},
            `vector.similarity_function`: '{self.similarity_function}'
            }}}};""")
        for query in queries:
            try:
                self._query_database(query, {})
            except Exception as e:
                logger.error(f"Failed to create index: {e}, Query: {query}")
                raise DatabaseError(_("Failed to create index"))


class BaseNode(ABC):
    """Abstract base class for nodes in the graph database."""
    __abstract__ = True

    def __init__(self, **kwargs):
        self.lib_id: int = kwargs.get('lib_id')
        self.subject_id: int = kwargs.get('subject_id')
        self.id: Optional[int] = kwargs.get('id')
        self.element_id: Optional[str] = kwargs.get('element_id')
        self.content: Optional[str] = kwargs.get('content')
        self.content_vector: Optional[List[float]] = kwargs.get('content_vector')
        self.embedding_model: Optional[str] = kwargs.get('embedding_model')
        self.created_at: Optional[float] = kwargs.get('created_at')
        self.updated_at: Optional[float] = kwargs.get('updated_at')
        self.score: Optional[float] = kwargs.get('score', 0.0)

    def __repr__(self):
        content_repr = reprlib.repr(self.content)
        return f"id={self.id}, element_id={self.element_id}, \
                lib_id={self.lib_id}, subject_id={self.subject_id}, \
                content={content_repr}, created_at={self.created_at}, \
                updated_at={self.updated_at}"

    @classmethod
    def _query_database(cls, query, params):
        try:
            return graph.query(query, params)
        except Exception as e:
            # Consider catching more specific Neo4j - related exceptions
            logger.error(f"Failed to query database: {e}, Query: {query}, Parameters: {params}")
            raise DatabaseError(_("Failed to query database"))

    @classmethod
    def to_model(cls, result_item):
        return cls(lib_id=result_item.get("lib_id"),
                   subject_id=result_item.get("subject_id"),
                   id=result_item.get("id"),
                   element_id=result_item.get("element_id"),
                   content=result_item.get("content"),
                   content_vector=result_item.get("content_vector"),
                   embedding_model=result_item.get("embedding_model"),
                   created_at=result_item.get("created_at"),
                   updated_at=result_item.get("updated_at"))

    @classmethod
    def _to_dict_list(self, items, item_class, filter=None):
        if items and isinstance(items, list):
            return [item.to_dict(filter) if isinstance(item, item_class) else item for item in items]
        return []

    def to_dict(self, filter=None) -> Dict[str, Any]:
        if filter:
            return {key: value for key, value in self.__dict__.items() if key in filter}

        return self.__dict__

    @abstractmethod
    def save(self):
        """Abstract method to save the node to the database."""
        pass


    def update(self):
        """Abstract method to update the node in the database."""
        pass

class Overview():
    def __init__(self, type: str, count: int):
        self.type = type
        self.count = count

    def __repr__(self):
        return f"Overview(type={self.type}, count={self.count})"

    def to_dict(self, filter=None) -> Dict[str, Any]:
        if filter:
            return {key: value for key, value in self.__dict__.items() if key in filter}
        return self.__dict__