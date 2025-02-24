from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from ai.llm import Llm
from core.config import DEFAULT_LLM_NAME
from core.extends_logger import logger
from core.i18n import _
from schemas.graph import GraphConditionView
from . import BaseNode, BaseModel, NodeType, RelationshipType, graph, Overview
from .document import Document
from .entity import Entity
from .keyword import Keyword
from .relationship import Relationship
from .tag import Tag
from .webpage import WebPage


class Node(BaseNode, BaseModel):
    """
    Represents a node in the graph database. This class handles the creation, updating, and querying of nodes,
    as well as their relationships with other entities like documents, keywords, tags, and webpages.
    """

    # Index names for full-text and vector searches
    title_full_text_index_name: str = "node_title_full_text_index"
    content_full_text_index_name: str = "node_content_full_text_index"
    lib_id_index_name: str = "node_lib_id_index"
    subject_id_index_name: str = "node_subject_id_index"
    title_vector_index_name: str = "node_title_vector_index"
    content_vector_index_name: str = "node_content_vector_index"

    # Cypher query clause for returning node properties
    return_clause: str = """
                RETURN id(node) AS id, 
                elementId(node) AS element_id, 
                node.lib_id as lib_id, 
                node.subject_id as subject_id, 
                node.content as content, 
                node.type as type,
                node.title as title, 
                node.title_vector as title_vector, 
                node.content_vector as content_vector,
                node.created_at as created_at, 
                node.updated_at as updated_at
            """

    def __init__(self, **kwargs):
        """
        Initializes a Node instance with the provided keyword arguments.

        Args:
            **kwargs: Arbitrary keyword arguments to set node attributes.
        """
        super().__init__(**kwargs)
        self.type = kwargs.get('type')  # Type of the node (e.g., ROOT, SUBJECT, PROMPT, etc.)
        self.title = kwargs.get('title')  # Title of the node
        self.title_vector = kwargs.get('title_vector')  # Vector representation of the title
        self.depth = kwargs.get('depth', 0)  # Depth of the node in the graph hierarchy
        self.entities: List[Entity] = []  # List of entities associated with the node
        self.keywords: List[Keyword] = []  # List of keywords associated with the node
        self.tags: List[Tag] = []  # List of tags associated with the node
        self.documents: List[Document] = []  # List of documents associated with the node
        self.webpages: List[WebPage] = []  # List of webpages associated with the node

    def __eq__(self, other):
        if not isinstance(other, Node):
            return NotImplemented
        return self.element_id == other.element_id
    
    def __repr__(self):
        """
        Returns a string representation of the Node instance.

        Returns:
            str: A string representation of the Node.
        """
        repr = super().__repr__()
        return f"Node({repr}, type={self.type}, title={self.title}, depth={self.depth})"

    def to_dict(self, filter=None) -> Dict[str, Any]:
        """
        Converts the Node instance to a dictionary.

        Args:
            filter (Optional[List[str]]): List of keys to include in the dictionary. If None, all keys are included.

        Returns:
            Dict[str, Any]: A dictionary representation of the Node.
        """
        dict = super().to_dict(filter)
        dict.update({
            "type": self.type.value if self.type and (not filter or "type" in filter) else None,
            "entities": super()._to_dict_list(self.entities, Entity, filter.get("entities.entity", None) if filter else None) if self.entities and (not filter or "entities" in filter) else [],
            "keywords": super()._to_dict_list(self.keywords, Keyword, filter.get("keywords.keyword", None) if filter else None) if self.keywords and (not filter or "keywords" in filter) else [],
            "tags": super()._to_dict_list(self.tags, Tag, filter.get("tags.tag", None) if filter else None) if self.tags and (not filter or "tags" in filter) else [],
            "documents": super()._to_dict_list(self.documents, Document, filter.get("documents.document", None) if filter else None) if self.documents and (not filter or "documents" in filter) else [],
            "webpages": super()._to_dict_list(self.webpages, WebPage, filter.get("documents.webpage", None) if filter else None) if self.webpages and (not filter or "documents" in filter) else []
        })
        return dict

    def save(self) -> "Node":
        """
        Saves the current node to the graph database.

        Returns:
            Node: The saved Node instance with updated attributes.
        """
        set_vector_clause = self.compose_set_vector_clause("node")
        query = f"""
        CREATE (node:Node {{
                lib_id: $lib_id, 
                subject_id: $subject_id, 
                type: $type, 
                title: $title, 
                content: $content, 
                embedding_model: $embedding_model,
                created_at: $created_at, 
                updated_at: $updated_at
        }})
        {set_vector_clause}
        {Node.return_clause}
        """
        params = {
            "lib_id": self.lib_id,
            "subject_id": self.subject_id,
            "type": self.type.value,
            "title": self.title,
            "content": self.content,
            "title_vector": self.title_vector,
            "content_vector": self.content_vector,
            "embedding_model": self.embedding_model,
            "created_at": datetime.now(timezone.utc).timestamp(),
            "updated_at": datetime.now(timezone.utc).timestamp()
        }
        result = self._query_database(query, params)
        if result:
            self.id = result[0].get("id")
            self.element_id = result[0].get("element_id")
            self.lib_id = result[0].get("lib_id")
            self.subject_id = result[0].get("subject_id")
            self.content = result[0].get("content")
            self.type = NodeType(result[0].get("type"))
            self.title = result[0].get("title")
            self.title_vector = result[0].get("title_vector")
            self.content_vector = result[0].get("content_vector")
            self.embedding_model = result[0].get("embedding_model")
            self.created_at = result[0].get("created_at")
            self.updated_at = result[0].get("updated_at")

        self.create_index("Node")

        return self

    def update(self) -> "Node":
        """
        Updates the current node in the graph database.

        Returns:
            Node: The updated Node instance.
        """
        set_vector_clause = self.compose_set_vector_clause("node")
        query = f"""
            MATCH (node:Node)
            WHERE elementId(node) = $element_id
            SET node.title = $title, 
            node.content = $content, 
            node.embedding_model = $embedding_model, 
            node.updated_at = $updated_at
            {set_vector_clause}
            {Node.return_clause}
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
        result = self._query_database(query, params)
        if result:
            self.title = result[0].get("title")
            self.content = result[0].get("content")
            self.title_vector = result[0].get("title_vector")
            self.content_vector = result[0].get("content_vector")
            self.embedding_model = result[0].get("embedding_model")
            self.updated_at = result[0].get("updated_at")

        return self

    def delete(self):
        Node.delete_node(self.element_id)
        
    @classmethod
    def compose_node_query_clause(cls, lib_id, subject_ids: List[str] = None):
        """
        Composes a Cypher query clause based on the provided conditions.

        Args:
            lib_id (int): The library ID to filter nodes.
            condition (GraphConditionView): The conditions to filter nodes.

        Returns:
            Tuple[str, Dict]: A tuple containing the query clause and parameters.
        """
        params = {"lib_id": lib_id}
        query_clause = ""
        if subject_ids and len(subject_ids) > 0:
            query_clause += " AND node.subject_id IN $subject_ids"
            subject_ids.append(0)
            params["subject_ids"] = subject_ids

        return query_clause, params

    @classmethod
    def add_node(cls, lib_id: int, subject_id: int, content: str, node_type: NodeType) -> "Node":
        """
        Creates and saves a new node in the graph database.

        Args:
            lib_id (int): The library ID.
            subject_id (int): The subject ID.
            content (str): The content of the node.
            node_type (NodeType): The type of the node.

        Returns:
            Node: The newly created Node instance.
        """
        node: Node = cls(lib_id=lib_id,
                         subject_id=subject_id,
                         content=content,
                         type=node_type.value)
        return node.save()

    @classmethod
    def add_root_node(cls, lib_id: int, lib_name: str) -> "Node":
        """
        Creates and saves a root node in the graph database.

        Args:
            lib_id (int): The library ID.
            lib_name (str): The name of the library.

        Returns:
            Node: The newly created root Node instance.
        """
        root_node: Node = cls(lib_id=lib_id,
                              subject_id=0,
                              content=lib_name,
                              type=NodeType.ROOT)
        root_node = root_node.save()

        # if root_node:
        #     for _ in range(config.GDS_CONCURRENT_QUERIES):
        #         VirtualNode.add_virtual_node(lib_id, 0, root_node.element_id)

        return root_node

    @classmethod
    def add_subject_node(cls, lib_id: int, subject_id: int, content, depth) -> "Node":
        """
        Creates and saves a subject node in the graph database.

        Args:
            lib_id (int): The library ID.
            subject_id (int): The subject ID.
            content (str): The content of the node.
            depth (int): The depth of the node in the graph hierarchy.

        Returns:
            Node: The newly created subject Node instance.
        """
        root_node = Node.query_root_node(lib_id)
        if not root_node:
            root_node = Node.add_root_node(lib_id, "root_node")

        node: Node = cls(lib_id=lib_id,
                         subject_id=subject_id,
                         content=content,
                         type=NodeType.SUBJECT,
                         depth=depth)
        node = node.save()
        Relationship.add_relationship(
            lib_id=lib_id,
            subject_id=subject_id,
            source_element_id=root_node.element_id,
            target_element_id=node.element_id,
            type=RelationshipType.HAS_CHILD,
            content=None)

        return node

    @classmethod
    def add_prompt_node(cls, lib_id: int, subject_id: int, content, depth) -> "Node":
        """
        Creates and saves a prompt node in the graph database.

        Args:
            lib_id (int): The library ID.
            subject_id (int): The subject ID.
            content (str): The content of the node.
            depth (int): The depth of the node in the graph hierarchy.

        Returns:
            Node: The newly created prompt Node instance.
        """
        node: Node = cls(lib_id=lib_id,
                         subject_id=subject_id,
                         content=content,
                         type=NodeType.PROMPT,
                         depth=depth)
        return node.save()

    @classmethod
    def add_question_node(cls, lib_id: int, subject_id: int, content) -> "Node":
        """
        Creates and saves a question node in the graph database.

        Args:
            lib_id (int): The library ID.
            subject_id (int): The subject ID.
            content (str): The content of the node.

        Returns:
            Node: The newly created question Node instance.
        """
        node: Node = cls(lib_id=lib_id,
                         subject_id=subject_id,
                         content=content,
                         type=NodeType.QUESTION)
        return node.save()

    @classmethod
    def add_info_node(cls, lib_id: int, subject_id: int, content, depth) -> "Node":
        """
        Creates and saves an info node in the graph database.

        Args:
            lib_id (int): The library ID.
            subject_id (int): The subject ID.
            content (str): The content of the node.
            depth (int): The depth of the node in the graph hierarchy.

        Returns:
            Node: The newly created info Node instance.
        """
        node: Node = cls(lib_id=lib_id,
                         subject_id=subject_id,
                         content=content,
                         type=NodeType.INFO,
                         depth=depth)
        return node.save()

    @classmethod
    def add_human_node(cls, lib_id: int, subject_id: int, content: str, parent_element_id: str = None) -> "Node":
        """
        Creates and saves a human node in the graph database.

        Args:
            lib_id (int): The library ID.
            subject_id (int): The subject ID.
            content (str): The content of the node.
            parent_element_id (str, optional): The element ID of the parent node.

        Returns:
            Tuple[Node, Optional[Relationship]]: The newly created human Node instance and its relationship with the parent node.
        """
        node: Node = cls(lib_id=lib_id,
                         subject_id=subject_id,
                         content=content,
                         type=NodeType.HUMAN, )
        node = node.save()
        relationship = None
        if parent_element_id:
            relationship = Relationship.add_relationship(lib_id=lib_id,
                                                         subject_id=subject_id,
                                                         source_element_id=parent_element_id,
                                                         target_element_id=node.element_id,
                                                         type=RelationshipType.HAS_CHILD,
                                                         content=None)
        return node, relationship

    @classmethod
    def to_model(cls, result_item) -> "Node":
        """
        Converts a database result item into a Node instance.

        Args:
            result_item (Dict): A dictionary representing a node from the database.

        Returns:
            Node: A Node instance populated with data from the result item.
        """
        return Node(lib_id=result_item.get("lib_id"),
                    subject_id=result_item.get("subject_id"),
                    id=result_item.get("id"),
                    element_id=result_item.get("element_id"),
                    content=result_item.get("content"),
                    type=NodeType(result_item.get("type")),
                    title=result_item.get("title"),
                    title_vector=result_item.get("title_vector"),
                    content_vector=result_item.get("content_vector"),
                    embedding_model=result_item.get("embedding_model"),
                    created_at=result_item.get("created_at"),
                    updated_at=result_item.get("updated_at"))

    @classmethod
    def query_root_node(cls, lib_id) -> Optional["Node"]:
        """
        Queries the root node for a given library ID.

        Args:
            lib_id (int): The library ID.

        Returns:
            Optional[Node]: The root Node instance if found, otherwise None.
        """
        query = f"""
        MATCH (node:Node)
        WHERE node.lib_id = $lib_id AND node.subject_id=0 AND node.type=$type
        {Node.return_clause}
        """
        params = {"lib_id": lib_id, "type": NodeType.ROOT.value}
        result = cls._query_database(query, params)
        if result:
            return cls.to_model(result[0])
        return None

    @classmethod
    def query_child(cls, element_id) -> List["Node"]:
        """
        Queries the child nodes of a given node.

        Args:
            element_id (str): The element ID of the parent node.

        Returns:
            List[Node]: A list of child Node instances.
        """
        query = f"""
        MATCH (p:Node)-[r]->(node:Node)
        WHERE elementId(p) = $element_id
        {Node.return_clause}
        """
        params = {"element_id": element_id}
        result = cls._query_database(query, params)
        if result:
            return [cls.to_model(row) for row in result]
        return []

    @classmethod
    def query_parent(cls, element_id) -> List["Node"]:
        """
        Queries the parent nodes of a given node.

        Args:
            element_id (str): The element ID of the child node.

        Returns:
            List[Node]: A list of parent Node instances.
        """
        try:
            query = f"""
                    MATCH (node:Node)-[r]->(c:Node)
                    WHERE elementId(child) = $element_id
                    {Node.return_clause}
                    """
            params = {"element_id": element_id}
            result = graph.query(query, params)

            if not result:
                return []

            parents = []
            for row in result:
                parents.append(Node.to_model(row))
            return parents
        except Exception as e:
            logger.error(f"Failed to query graph: {e}")
            raise ValueError(_("Failed to query graph"))

    @classmethod
    def find_detail_by_element_id(cls, element_id: str) -> Optional["Node"]:
        """
        Finds and returns detailed information about a node by its element ID.

        Args:
            element_id (str): The element ID of the node.

        Returns:
            Optional[Node]: The detailed Node instance if found, otherwise None.
        """
        try:
            query = f"""
                MATCH (node:Node)
                WHERE elementId(node) = $element_id
                {Node.return_clause}
                """
            result = graph.query(query, params={"element_id": element_id})
            if not result:
                return None

            node = Node.to_model(result[0])

            node.entities = Entity.get_entities_of_node(node.element_id)
            node.keywords = Keyword.get_keywords_of_node(node.element_id)
            node.tags = Tag.get_tags_of_node(node.element_id)
            node.documents = Document.get_documents_of_node(node.element_id)
            node.webpages = WebPage.get_webpages_of_node(node.element_id)

            return node
        except Exception as e:
            logger.error(f"Failed to get graph node detail: {e}")
            raise ValueError(_("The node does not exist."))

    @classmethod
    def query_graph_node_overviews(cls, lib_id, subject_ids: List[int] = None) -> List[Overview]:
        """
        Queries and returns overviews of nodes based on the provided conditions.

        Args:
            lib_id (int): The library ID.
            subject_ids (GraphConditionView): The conditions to filter nodes.

        Returns:
            List[Overview]: A list of Overview instances representing node types and their counts.
        """
        try:
            if not subject_ids or len(subject_ids) == 0:
                return []

            query_clause, params = cls.compose_node_query_clause(lib_id, subject_ids)
            query = f"""
                            MATCH (node:Node) 
                            WHERE node.lib_id = $lib_id {query_clause}
                            RETURN node.type AS type, COUNT(node) AS count
                        """
            result = graph.query(query, params)
            if not result:
                return []

            overviews: List[Overview] = []
            for row in result:
                overviews.append(Overview(type=row.get("type"), count=row.get("count")))
            return overviews
        except Exception as e:
            logger.error(f"Failed to query_graph_node_overview: {e}")
            raise ValueError(_("Failed to query graph node overview"))

    @classmethod
    def query_graph_node(cls, lib_id, subject_ids: List[int] = None):
        """
        Queries and returns nodes based on the provided conditions.

        Args:
            lib_id (int): The library ID.
            subject_ids (List[int]): The conditions to filter nodes.

        Returns:
            Tuple[List[Node], List[Overview]]: A tuple containing a list of Node instances and a list of Overview instances.
        """
        if not subject_ids or len(subject_ids) == 0:
            return [], []

        query_clause, params = cls.compose_node_query_clause(lib_id, subject_ids)
        query = f"""
            MATCH (node:Node)
            WHERE node.lib_id = $lib_id {query_clause}
            RETURN elementId(node) AS element_id, id(node) AS id, node.lib_id as lib_id, 
            node.subject_id as subject_id, node.type as type
            """
        # logger.debug(f"-----query_graph_node query: {query}, params: {params}")
        nodes: List[Node] = []
        query_result = cls._query_database(query, params)
        if query_result:
            for query_item in query_result:
                nodes.append(Node.to_model(query_item))

        # query overview
        overviews: List[Overview] = cls.query_graph_node_overviews(lib_id, subject_ids)
        return nodes, overviews

    @classmethod
    def search_graph_node(cls, lib_id, condition: GraphConditionView):
        """
        Queries and returns relationships based on the provided conditions.

        Args:
            lib_id (int): The library ID.
            condition (GraphConditionView): The conditions to filter relationships.

        Returns:
            Tuple[List[Relationship], List[Overview]]: A tuple containing a list of Relationship instances and a list of Overview instances.

        Raises:
            Exception: If the query fails.
        """
        try:
            subject_ids = condition.subject_ids
            if not subject_ids or len(subject_ids) == 0:
                return [], []

            query_clause = ""
            params = {"lib_id": lib_id}
            if condition.subject_ids and len(condition.subject_ids) > 0:
                query_clause += " AND source.subject_id IN $subject_ids and target.subject_id IN $subject_ids"
                condition.subject_ids.append(0)
                params["subject_ids"] = condition.subject_ids

            if condition.type:
                query_clause += " AND source.type = $type"
                params["type"] = condition.type

            if condition.content:
                query_clause += " AND (source.content CONTAINS $content or source.title CONTAINS $content)"
                params["content"] = condition.content
            
            query = f"""
                MATCH (source:Node)-[r]-(target:Node)
                WHERE source.lib_id = $lib_id {query_clause}
                RETURN
                id(source) as source_id, id(target) as target_id, 
                elementId(source) as source_element_id, elementId(target) as target_element_id, 
                id(r) as r_id, elementId(r) as r_element_id,
                type(r) as r_type, 
                source, r, target
                """
            query_result = graph.query(query, params)
            nodes: List[Node] = []
            links: List[Relationship] = []
            if query_result:
                seen = set()
                for result in query_result:
                    links.append(Relationship(lib_id=result.get("r")[0].get("lib_id"),
                                              subject_id=result.get("r")[0].get("subject_id"),
                                              element_id=result["r_element_id"],
                                              id=result["r_id"],
                                              source=result["source_id"],
                                              target=result["target_id"],
                                              source_element_id=result["source_element_id"],
                                              target_element_id=result["target_element_id"],
                                              type=RelationshipType(result["r_type"]),
                                              content=result.get("r")[0].get("content"),
                                              content_vector=result.get("r")[0].get("content_vector"),
                                              embedding_model=result.get("r")[0].get("embedding_model"),
                                              created_at=result.get("r")[0].get("created_at"),
                                              updated_at=result.get("r")[0].get("updated_at")))
                    if result["source_element_id"] not in seen:
                        seen.add(result["source_element_id"])
                        nodes.append(Node(lib_id=result.get("source").get("lib_id"),
                                        subject_id=result.get("source").get("subject_id"),
                                        id=result["source_id"],
                                        element_id=result["source_element_id"],
                                        content=result.get("source").get("content"),
                                        type=NodeType(result.get("source").get("type")),
                                        title=result.get("source").get("title"),
                                        title_vector=result.get("source").get("title_vector"),
                                        content_vector=result.get("source").get("content_vector"),
                                        embedding_model=result.get("source").get("embedding_model"),
                                        created_at=result.get("source").get("created_at"),
                                        updated_at=result.get("source").get("updated_at")))
                    if result["target_element_id"] not in seen:
                        seen.add(result["target_element_id"])
                        nodes.append(Node(lib_id=result.get("target").get("lib_id"),
                                        subject_id=result.get("target").get("subject_id"),
                                        id=result["target_id"],
                                        element_id=result["target_element_id"],
                                        content=result.get("target").get("content"),
                                        type=NodeType(result.get("target").get("type")),
                                        title=result.get("target").get("title"),
                                        title_vector=result.get("target").get("title_vector"),
                                        content_vector=result.get("target").get("content_vector"),
                                        embedding_model=result.get("target").get("embedding_model"),
                                        created_at=result.get("target").get("created_at"),
                                        updated_at=result.get("target").get("updated_at")))

            return nodes, links
        except Exception as e:
            logger.error(f"Failed to query graph: {e}")
            raise


    @classmethod
    def delete_node(cls, element_id: str):
        """
        Deletes a node from the graph database by its element ID.

        Args:
            element_id (str): The element ID of the node to delete.
        """
        try:
            query = f"""
            MATCH (node:Node)
            WHERE elementId(node) = $element_id
            DETACH DELETE node
            """
            params = {"element_id": element_id}
            graph.query(query, params)
        except Exception as e:
            logger.error(f"Failed to delete node: {e}")
            raise ValueError(_("Failed to delete node"))

    @classmethod
    def generate_answer(cls, lib_id: int, subject_id: int,
                        node_element_id: str, llm_name: str = DEFAULT_LLM_NAME):
        """
        Generates an answer using an LLM and creates a new info node linked to the original node.

        Args:
            lib_id (int): The library ID.
            subject_id (int): The subject ID.
            node_element_id (str): The element ID of the node to generate an answer for.
            llm_name (str): The name of the LLM to use.

        Returns:
            Tuple[Node, Relationship]: The newly created info Node instance and its relationship with the original node.
        """
        node_detail = Node.find_detail_by_element_id(node_element_id)
        prompt = node_detail.content
        ai_response = Llm.get_ai_response(prompt, llm_name)
        if not ai_response:
            return None

        ai_node = Node.add_info_node(lib_id, subject_id, ai_response, 1)
        relationship = Relationship.add_relationship(
            lib_id, subject_id, node_element_id, ai_node.element_id, RelationshipType.HAS_CHILD
        )

        return ai_node, relationship

    @classmethod
    def generate_prompts(cls, lib_id: int, subject_id: int,
                         node_element_id: str, llm_name: str = DEFAULT_LLM_NAME):
        """
        Generates prompts using an LLM and creates new prompt nodes linked to the original node.

        Args:
            lib_id (int): The library ID.
            subject_id (int): The subject ID.
            node_element_id (str): The element ID of the node to generate prompts for.
            llm_name (str): The name of the LLM to use.

        Returns:
            Tuple[List[Node], List[Relationship]]: A list of newly created prompt Node instances and their relationships with the original node.
        """
        node_detail = Node.find_detail_by_element_id(node_element_id)
        prompt = node_detail.content
        generated_prompts = Llm.generate_prompts_from_text(prompt, llm_name)
        if not generated_prompts:
            return []

        nodes: List[Node] = []
        relationships: List[Relationship] = []
        for generated_prompt in generated_prompts:
            prompt_node = Node.add_prompt_node(lib_id,
                                               subject_id,
                                               generated_prompt["prompt"], 1)
            nodes.append(prompt_node)
            relationships.append(
                Relationship.add_relationship(
                    lib_id,
                    subject_id,
                    node_element_id,
                    prompt_node.element_id,
                    RelationshipType.HAS_CHILD
                ))

        return nodes, relationships

    @classmethod
    def find_prompts(cls, node_element_id: str) -> List["Node"]:
        """
        Finds prompts for a given node element ID.

        Args:
            node_element_id (str): The element ID of the node to find prompts for.

        Returns:
            List[Node]: A list of child Node instances.
        """
        query = f"""
        MATCH (p:Node)-[r]->(node:Node) 
        WHERE elementId(p) = $element_id and node.type = $type
        {Node.return_clause}
        """
        params = {"element_id": node_element_id, "type": NodeType.PROMPT.value}
        result = cls._query_database(query, params)
        if result:
            return [cls.to_model(row) for row in result]
        return []

    @classmethod
    def find_nodes_by_prompt(cls, prompt_element_id: str) -> List["Node"]:
        """
        Finds nodes for a given prompt element ID.

        Args:
            prompt_element_id (str): The element ID of the prompt to find nodes for.

        Returns:
            List[Node]: A list of child Node instances.
        """
        query = f"""
        MATCH (p:Node)-[r]->(node:Node) 
        WHERE elementId(p) = $prompt_element_id and p.type = $prompt_type
        {Node.return_clause}
        """
        params = {"prompt_element_id": prompt_element_id, "prompt_type": NodeType.PROMPT.value}
        result = cls._query_database(query, params)
        if result:
            return [cls.to_model(row) for row in result]
        return []

    @classmethod
    def generate_questions(cls, lib_id: int,
                           subject_id: int,
                           node_element_id: str,
                           llm_name: str = DEFAULT_LLM_NAME):
        """
        Generates questions using an LLM and creates new question nodes linked to the original node.

        Args:
            lib_id (int): The library ID.
            subject_id (int): The subject ID.
            node_element_id (str): The element ID of the node to generate questions for.
            llm_name (str): The name of the LLM to use.

        Returns:
            Tuple[List[Node], List[Relationship]]: A list of newly created question Node instances and their relationships with the original node.
        """
        node_detail = Node.find_detail_by_element_id(node_element_id)
        content = node_detail.content
        questions = Llm.generate_questions_from_text(content, llm_name)
        nodes: List[Node] = []
        relationships: List[Relationship] = []
        for question in questions:
            question_node = Node.add_question_node(lib_id, subject_id, question["question"])
            nodes.append(question_node)
            new_relationship = Relationship.add_relationship(
                lib_id, subject_id, question_node.element_id, node_element_id, RelationshipType.HAS_CHILD
            )
            relationships.append(new_relationship)

        return nodes, relationships

    @classmethod
    def find_node_by_document(cls, document_element_id: str) -> Optional["Node"]:
        """
        Finds and returns a node associated with a specific document.

        Args:
            document_element_id (str): The element ID of the document.

        Returns:
            Optional[Node]: The Node instance associated with the document if found, otherwise None.
        """
        try:
            query = f"""
                    MATCH (node:Node)-[r]->(document:Document) where elementId(document)=$document_element_id 
                    {Node.return_clause}
                    """
            query_result = graph.query(query, params={"document_element_id": document_element_id})
            if not query_result:
                return None

            return Node.to_model(query_result[0])
        except Exception as e:
            logger.error(f"Failed to find node by document: {e}")
            raise ValueError(_("Failed to find node by document."))

    @classmethod
    def find_node_by_webpage(cls, webpage_element_id: str) -> Optional["Node"]:
        """
        Finds and returns a node associated with a specific webpage.

        Args:
            webpage_element_id (str): The element ID of the webpage.

        Returns:
            Optional[Node]: The Node instance associated with the webpage if found, otherwise None.
        """
        try:
            query = f"""
                    MATCH (node:Node)-[r]->(webpage:WebPage) where elementId(webpage)=$webpage_element_id 
                    {Node.return_clause}
                    """
            query_result = graph.query(query, params={"webpage_element_id": webpage_element_id})
            if not query_result:
                return None

            return Node.to_model(query_result[0])
        except Exception as e:
            logger.error(f"Failed to find node by webpage: {e}")
            raise ValueError(_("Failed to find node by webpage."))

    @classmethod
    def find_node_by_document_page(cls, document_page_element_id: str) -> Optional["Node"]:
        """
        Finds and returns a node associated with a specific document page.

        Args:
            document_page_element_id (str): The element ID of the document page.

        Returns:
            Optional[Node]: The Node instance associated with the document page if found, otherwise None.
        """
        try:
            query = f"""
                   MATCH (node:Node)-[r]->(documentPage:DocumentPage) WHERE elementId(documentPage)=$document_page_element_id 
                   {Node.return_clause}
                   """
            query_result = graph.query(query, params={"document_page_element_id": document_page_element_id})
            if not query_result:
                return None

            return Node.to_model(query_result[0])
        except Exception as e:
            logger.error(f"Failed to get node by document page: {e}")
            raise ValueError(_("Failed to get node by document page."))


    @classmethod
    def find_human_nodes(cls, node_element_id: str) -> List["Node"]:
        """
        Finds human nodes for a given node element ID.

        Args:
            node_element_id (str): The element ID of the node to find human child nodes for.

        Returns:
            List[Node]: A list of human Node instances.
        """
        query = f"""
        MATCH (p:Node)<-[r]->(c:Node) 
        WHERE (elementId(p) = $element_id and c.type = $type) or (elementId(c) = $element_id and p.type = $type) 
        WITH p, r, c
        RETURN DISTINCT
        CASE 
        WHEN p.type = $type THEN id(p)
        ELSE id(c)
        END AS id,
        CASE 
        WHEN p.type = $type THEN elementId(p)
        ELSE elementId(c)
        END AS element_id,
        CASE 
        WHEN p.type = $type THEN p.lib_id
        ELSE c.lib_id
        END AS lib_id,
        CASE 
        WHEN p.type = $type THEN p.subject_id
        ELSE c.subject_id
        END AS subject_id,
        CASE 
        WHEN p.type = $type THEN p.content
        ELSE c.content
        END AS content,
        CASE 
        WHEN p.type = $type THEN p.type
        ELSE c.type
        END AS type,
        CASE 
        WHEN p.type = $type THEN p.title
        ELSE c.title
        END AS title,
        CASE 
        WHEN p.type = $type THEN p.title_vector
        ELSE c.title_vector
        END AS title_vector,
        CASE 
        WHEN p.type = $type THEN p.content_vector
        ELSE c.content_vector
        END AS content_vector,
        CASE 
        WHEN p.type = $type THEN p.created_at
        ELSE c.created_at
        END AS created_at,
        CASE 
        WHEN p.type = $type THEN p.updated_at
        ELSE c.updated_at
        END AS updated_at
        """
        params = {"element_id": node_element_id, "type": NodeType.HUMAN.value}
        result = cls._query_database(query, params)
        if result:
            return [cls.to_model(row) for row in result]
        return []