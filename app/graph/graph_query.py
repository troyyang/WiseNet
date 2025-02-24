from collections import namedtuple
from typing import List, Optional

import core.config as config
from ai.embedding import EmbeddingFactory
from . import NodeType, graph
from .document import Document
from .document_page import DocumentPage
from .entity import Entity
from .gds_graph import GdsGraph
from .keyword import Keyword
from .node import Node
from .tag import Tag
from .webpage import WebPage
from core.extends_logger import logger

QueryResult = namedtuple('QueryResult', ['document_page', 'webpage', 'document', 'main_node', 'prompts', 'related_nodes', 'entities', 'keywords', 'tags'])

class KnowledgeGraphQuery:
    def __init__(self, gds_graph_name: str = GdsGraph.graph_name):
        self.embedding_factory = EmbeddingFactory()
        if config.API_ENV.lower() == "test":
            self.gds_graph_name = GdsGraph.test_graph_name
        else:
            self.gds_graph_name = gds_graph_name

        if not GdsGraph.check_gds_graph(self.gds_graph_name):
            GdsGraph.create_gds_graph(self.gds_graph_name)

    def delete_graph_by_lib(self, lib_id: int):
        graph.query("MATCH (n) WHERE n.lib_id = $lib_id DETACH DELETE n", {"lib_id": lib_id})

    def delete_graph_by_subject(self, lib_id: int, subject_id: int):
        graph.query(
            "MATCH (n) WHERE n.lib_id = $lib_id AND n.subject_id = $subject_id DETACH DELETE n",
            {"lib_id": lib_id, "subject_id": subject_id}
        )

    def delete_node_and_posterity(self, node_element_id: str):
        graph.query(
            "MATCH (p)-[r*0..]->(c) WHERE elementId(p)=$node_element_id DETACH DELETE p,r,c",
            {"node_element_id": node_element_id}
        )

    def search_knowledge_graph_by_prompt(self, prompt_element_id: str, limit: int = 5) -> Optional[QueryResult]:
        nodes: List[Node] = Node.find_nodes_by_prompt(prompt_element_id)
        return self.compose_query_result(nodes, limit=limit)

    def search_knowledge_graph_by_related_node(self, related_node_element_id: str, limit: int = 5) -> Optional[QueryResult]:
        node = Node.find_detail_by_element_id(related_node_element_id)
        return self.compose_query_result([node], limit=limit)

    def compose_query_result(self, nodes: List[Node], limit: int) -> Optional[QueryResult]:
        """Compose a QueryResult from a list of nodes."""
        if nodes and len(nodes) > 0:
            main_node: Node = nodes[0]
            prompts = self.find_prompts(main_node.element_id)
            related_nodes = self.find_related_nodes(main_node.lib_id, main_node.subject_id, main_node.id, limit)
            return QueryResult(
                document_page=None,
                webpage=None,
                document=None,
                main_node=main_node,
                prompts=prompts,
                related_nodes=related_nodes,
                entities=main_node.entities if main_node.entities else Entity.get_entities_of_node(main_node.element_id),
                keywords=main_node.keywords if main_node.keywords else Keyword.get_keywords_of_node(main_node.element_id),
                tags=main_node.tags if main_node.tags else Tag.get_tags_of_node(main_node.element_id)
            )

        return None

    def search_knowledge_graph(self,
                                message,
                                lib_id: int,
                                subject_id: Optional[int] = None,
                                limit: int = 5,
                                embedding_model: str = "sbert",
                                max_tokens_each_chunk = 128,
                                search_scope = ["question", "page", "document", "webpage", "node"],
                                search_type = "vector", # fulltext, vector, hybrid
                                only_title: bool = False,) -> Optional[QueryResult]:
        if not message:
            return None

        message_vector: List[float] = self.embedding_factory.get_embedding(
            text=message,
            model_name=embedding_model,
            max_tokens_each_chunk=max_tokens_each_chunk
        ).tolist()

        query_methods = {
            "question": self.query_by_question,
            "page": self.query_by_document_page,
            "document": self.query_by_document,
            "webpage": self.query_by_webpage,
            "node": self.query_by_node
        }

        # the order of scope element will effect the priority
        if not search_scope or len(search_scope) == 0:
            search_scope = ["question", "page", "document", "webpage", "node"]

        for method in search_scope:
            logger.info(f"--------searching by {method}")
            query_result = query_methods.get(method, lambda **kwargs: dict)(lib_id=lib_id, subject_id=subject_id, message=message, message_vector=message_vector, limit=limit, only_title=only_title, search_type=search_type)
            if query_result:
                return query_result

        return None

    def find_related_nodes(self, lib_id: str, subject_id: int, node_id: int, limit: int = 5) -> List[Node]:
        human_child_nodes = Node.find_human_nodes(node_id)
        similar_nodes = self.find_similar_nodes(lib_id, subject_id, node_id, limit)

        seen = set()
        related_nodes = []
        for node in human_child_nodes + similar_nodes:
            if node.id not in seen:
                seen.add(node.id)
                related_nodes.append(node)

        return related_nodes

    def find_similar_nodes(self, lib_id: str, subject_id: int, node_id: int, limit: int = 5) -> List[Node]:
        # Implement logic to find related nodes
        query = f"""
        CALL gds.nodeSimilarity.filtered.stream($gds_graph_name, {{
            topK: $top_k,
            similarityCutoff: $similarity_cutoff,
            sourceNodeFilter: $node_id }} )
        YIELD node1, node2, similarity
        WHERE gds.util.asNode(node2).lib_id=$lib_id AND gds.util.asNode(node2).type in $types
                RETURN
                    gds.util.asNode(node2) AS neighborNode,
                    node2 AS neighborNodeId,
                    elementId(gds.util.asNode(node2)) AS neighborElementId,
                    labels(gds.util.asNode(node2)) AS neighborLabels,
                    similarity
                ORDER BY similarity DESC
                LIMIT $limit
        """

        params = {
            "gds_graph_name": self.gds_graph_name,
            "lib_id": lib_id,
            "subject_id": subject_id,
            "node_id": node_id,
            "top_k": config.GDS_TOP_K,
            "similarity_cutoff": config.GDS_SIMILARITY_CUTOFF,
            "limit": limit,
            "types": [NodeType.INFO.value, NodeType.HUMAN.value],
        }
        query_result = graph.query(query, params)
        node_models: list[Node] = []
        if query_result:
            for item in query_result:
                if item.get("neighborLabels")[0] == "Node":
                    node = Node(
                            id=item.get("neighborNodeId"),
                            element_id=item.get("neighborElementId"),
                            lib_id=item.get("neighborNode").get("lib_id"),
                            subject_id=item.get("neighborNode").get("subject_id"),
                            content=item.get("neighborNode").get("content"),
                            type=NodeType(item.get("neighborNode").get("type")),
                            title=item.get("neighborNode").get("title"),
                            title_vector=item.get("neighborNode").get("title_vector"),
                            content_vector=item.get("neighborNode").get("content_vector"),
                            embedding_model=item.get("neighborNode").get("embedding_model"),
                            created_at=item.get("neighborNode").get("created_at"),
                            updated_at=item.get("neighborNode").get("updated_at")
                        )    
                    node.score = item.get("similarity")
                    node_models.append(node)

        return node_models


    def find_prompts(self, node_element_id: str) -> List[Node]:
        return Node.find_prompts(node_element_id)

    def query_by_document_page(self, lib_id: int, subject_id: Optional[int], 
                                message: str, 
                                message_vector: List[float], 
                                limit: int = 5, 
                                only_title: bool = False,
                                search_type="vector") -> Optional[QueryResult]:
        query_result = self._query_document_page_by_content(lib_id, message, message_vector, search_type, subject_id)
        if query_result:
            document_page = DocumentPage.to_model(query_result[0])
            document_page.score = query_result[0].get("score")
            webpage = WebPage.find_webpage_by_document_page(document_page.element_id)
            document = Document.find_document_by_document_page(document_page.element_id)
            node = Node.find_node_by_document_page(document_page.element_id)
            related_nodes = self.find_related_nodes(lib_id, subject_id, node.id, limit)
            prompts = self.find_prompts(node.element_id)
            return QueryResult(
                document_page=document_page,
                webpage=webpage,
                document=document,
                main_node=node,
                prompts=prompts,
                related_nodes=related_nodes,
                entities=Entity.get_entities_of_node(node.element_id),
                keywords=Keyword.get_keywords_of_node(node.element_id),
                tags=Tag.get_tags_of_node(node.element_id),
            )
        return None

    def _query_by_document_page(self, lib_id: int, subject_id: Optional[int], message:str, message_vector: List[float], index_name: str, search_type: str) -> Optional[QueryResult]:
        call_clause = f"CALL db.index.vector.queryNodes($index_name, $top_k, $message_vector)" if search_type == "vector" else "CALL db.index.fulltext.queryNodes($index_name, $message)"
        subject_query_clause = f" AND node.subject_id=$subject_id" if subject_id else ""
        query = f"""
        {call_clause}
        YIELD node, score
        WITH node, score
        WHERE score > $similarity_cutoff AND node.lib_id = $lib_id{subject_query_clause}
        RETURN DISTINCT id(node) AS id,
               elementId(node) AS element_id,
               node.lib_id as lib_id,
               node.subject_id as subject_id,
               node.source as source,
               node.title as title,
               node.subtitle as subtitle,
               node.row as row,
               node.page as page,
               node.content as content,
               node.content_vector as content_vector,
               node.embedding_model as embedding_model,
               node.created_at as created_at,
               node.updated_at as updated_at,
               score
        ORDER BY score DESC
        LIMIT $limit
        """
        params = {
            "lib_id": lib_id,
            "subject_id": subject_id,
            "index_name": index_name,
            "message": '\"'+ message + '\"',
            "message_vector": message_vector,
            "top_k": config.TOP_K,
            "similarity_cutoff": max(config.SIMILARITY_CUTOFF, 0.85),
            "limit": 1,
        }
        return graph.query(query, params)

    def _query_document_page_by_content(self, lib_id: int, 
                                    message: str, 
                                    message_vector: List[float], 
                                    search_type: str, 
                                    subject_id: Optional[int]) -> Optional[QueryResult]:
        options = [
            (DocumentPage.content_vector_index_name, "vector") if search_type in ["vector", "hybrid"] else None,
            (DocumentPage.content_full_text_index_name, "fulltext") if search_type in ["fulltext", "hybrid"] else None,
        ]
        for option in options:
            if option:
                query_result = self._query_by_document_page(lib_id, subject_id, message, message_vector, option[0], option[1])
                
                if query_result:
                    return query_result
        return None

    def query_by_document(self, lib_id: int, subject_id: Optional[int], 
                            message: str,
                            message_vector: List[float], 
                            limit: int = 5, 
                            only_title: bool = False,
                            search_type="vector") -> Optional[QueryResult]:
        query_result = self._query_document_by_title(lib_id, message, message_vector, search_type, subject_id)
        if not query_result and not only_title:
            query_result = self._query_document_by_content(lib_id, message, message_vector, search_type, subject_id)
        if query_result:
            document = Document.to_model(query_result[0])
            document.score = query_result[0].get("score")
            node = Node.find_node_by_document(document.element_id)
            related_nodes = self.find_related_nodes(lib_id, subject_id, node.id, limit)
            prompts = self.find_prompts(node.element_id)
            return QueryResult(
                document_page=None,
                webpage=None,
                document=document,
                main_node=node,
                prompts=prompts,
                related_nodes=related_nodes,
                entities= Entity.get_entities_of_node(node.element_id),
                keywords= Keyword.get_keywords_of_node(node.element_id),
                tags= Tag.get_tags_of_node(node.element_id)
            )
        return None

    def _query_by_document(self, lib_id: int, subject_id: Optional[int], message:str, message_vector: List[float], index_name: str, search_type: str) -> Optional[QueryResult]:
        call_clause = f"CALL db.index.vector.queryNodes($index_name, $top_k, $message_vector)" if search_type == "vector" else "CALL db.index.fulltext.queryNodes($index_name, $message)"
        subject_query_clause = f" AND node.subject_id=$subject_id" if subject_id else ""
        query = f"""
        {call_clause}
        YIELD node, score
        WITH node, score
        WHERE score > $similarity_cutoff AND node.lib_id = $lib_id{subject_query_clause}
        RETURN DISTINCT id(node) AS id,
               elementId(node) AS element_id,
               node.lib_id as lib_id,
               node.subject_id as subject_id,
               node.name as name,
               node.saved_at as saved_at,
               node.title as title,
               node.title_vector as title_vector,
               node.content as content,
               node.content_vector as content_vector,
               node.created_at as created_at,
               node.updated_at as updated_at,
               score
        ORDER BY score DESC
        LIMIT $limit
        """
        params = {
            "lib_id": lib_id,
            "subject_id": subject_id,
            "index_name": index_name,
            "message": '\"'+ message + '\"',
            "message_vector": message_vector,
            "top_k": config.TOP_K,
            "similarity_cutoff": max(config.SIMILARITY_CUTOFF, 0.85),
            "limit": 1,
        }
        return graph.query(query, params)

    
    def _query_document_by_content(self, lib_id: int, 
                                    message: str, 
                                    message_vector: List[float], 
                                    search_type: str, 
                                    subject_id: Optional[int]) -> Optional[QueryResult]:
        options = [
            (Document.content_vector_index_name, "vector") if search_type in ["vector", "hybrid"] else None,
            (Document.content_full_text_index_name, "fulltext") if search_type in ["fulltext", "hybrid"] else None,
        ]
        for option in options:
            if option:
                query_result = self._query_by_document(lib_id, subject_id, message, message_vector, option[0], option[1])
                if query_result:
                    return query_result
        return None

    def _query_document_by_title(self, lib_id: int, 
                                message: str, 
                                message_vector: List[float], 
                                search_type: str, 
                                subject_id: Optional[int]) -> Optional[QueryResult]:
        options = [
            (Document.title_vector_index_name, "vector") if search_type in ["vector", "hybrid"] else None,
            (Document.title_full_text_index_name, "fulltext") if search_type in ["fulltext", "hybrid"] else None,
        ]
        for option in options:
            if option:
                query_result = self._query_by_document(lib_id, subject_id, message, message_vector, option[0], option[1])
                if query_result:
                    return query_result
        return None

    def query_by_webpage(self, lib_id: int, subject_id: Optional[int], 
                                message:str, 
                                message_vector: List[float], 
                                limit: int = 5, 
                                only_title: bool = False,
                                search_type="vector") -> Optional[QueryResult]:
        query_result = self._query_webpage_by_title(lib_id, message, message_vector, search_type, subject_id)
        if not query_result and not only_title:
            query_result = self._query_webpage_by_content(lib_id, message, message_vector, search_type,
                                                          subject_id)
        if query_result:
            webpage = WebPage.to_model(query_result[0])
            webpage.score = query_result[0].get("score")
            node = Node.find_node_by_webpage(webpage.element_id)
            related_nodes = self.find_related_nodes(lib_id, subject_id, node.id, limit)
            prompts = self.find_prompts(node.element_id)
            return QueryResult(
                document_page=None,
                webpage=webpage,
                document=None,
                main_node=node,
                prompts=prompts,
                related_nodes=related_nodes,
                entities=Entity.get_entities_of_node(node.element_id),
                keywords=Keyword.get_keywords_of_node(node.element_id),
                tags=Tag.get_tags_of_node(node.element_id)
            )
        return None

    def _query_by_webpage(self, lib_id: int, 
                        subject_id: Optional[int], 
                        message: str,
                        message_vector: List[float], 
                        index_name: str,
                        search_type="vector") -> Optional[QueryResult]:
        call_clause = f"CALL db.index.vector.queryNodes($index_name, $top_k, $message_vector)" if search_type == "vector" else "CALL db.index.fulltext.queryNodes($index_name, $message)"
        subject_query_clause = f" AND node.subject_id=$subject_id" if subject_id else ""
        query = f"""
        {call_clause}
        YIELD node, score
        WITH node, score
        WHERE score > $similarity_cutoff AND node.lib_id = $lib_id{subject_query_clause}
        RETURN DISTINCT id(node) AS id,
               elementId(node) AS element_id,
               node.lib_id as lib_id,
               node.subject_id as subject_id,
               node.url as url,
               node.title as title,
               node.title_vector as title_vector,
               node.content as content,
               node.content_vector as content_vector,
               node.created_at as created_at,
               node.updated_at as updated_at,
               score
        ORDER BY score DESC
        LIMIT $limit
        """
        params = {
            "lib_id": lib_id,
            "subject_id": subject_id,
            "index_name": index_name,
            "message": '\"'+ message + '\"',
            "message_vector": message_vector,
            "top_k": config.TOP_K,
            "similarity_cutoff": max(config.SIMILARITY_CUTOFF, 0.85),
            "limit": 1,
        }
        return graph.query(query, params)

    def _query_webpage_by_content(self, lib_id: int, message: str, message_vector: List[float], search_type: str, subject_id: Optional[int]) -> Optional[QueryResult]:
        options = [
            (WebPage.content_vector_index_name, "vector") if search_type in ["vector", "hybrid"] else None,
            (WebPage.content_full_text_index_name, "fulltext") if search_type in ["fulltext", "hybrid"] else None,
        ]
        for option in options:
            if option:
                query_result = self._query_by_webpage(lib_id, subject_id, message, message_vector, option[0], option[1])
                if query_result:
                    return query_result
        return None

    def _query_webpage_by_title(self, lib_id: int, message: str, message_vector: List[float], search_type: str, subject_id: Optional[int]) -> Optional[QueryResult]:
        options = [
            (WebPage.title_vector_index_name, "vector") if search_type in ["vector", "hybrid"] else None,
            (WebPage.title_full_text_index_name, "fulltext") if search_type in ["fulltext", "hybrid"] else None,
        ]
        for option in options:
            if option:
                query_result = self._query_by_webpage(lib_id, subject_id, message, message_vector, option[0], option[1])
                if query_result:
                    return query_result
        return None

    def query_by_question(self, lib_id: int, subject_id: Optional[int], 
                            message:str,
                            message_vector: List[float], 
                            limit: int = 5, 
                            only_title: bool = False, 
                            search_type="vector") -> Optional[QueryResult]:
        query_result = self._query_node_by_content(lib_id, subject_id, 
                                message,
                                message_vector, 
                                search_type=search_type,
                                node_types=[NodeType.QUESTION], 
                                similarity_cutoff=0.90,
                               )
        if query_result:
            question_node = Node.to_model(query_result[0])
            question_node.score = query_result[0].get("score")
            child_nodes = Node.query_child(question_node.element_id)
            if child_nodes:
                main_node: Node = child_nodes[0]
                related_nodes = child_nodes[1:limit] if len(child_nodes) > 1 else []
                prompts = self.find_prompts(main_node.element_id)
                return QueryResult(
                    document_page=None,
                    webpage=None,
                    document=None,
                    main_node=main_node,
                    prompts=prompts,
                    related_nodes=related_nodes,
                    entities=Entity.get_entities_of_node(main_node.element_id),
                    keywords=Keyword.get_keywords_of_node(main_node.element_id),
                    tags=Tag.get_tags_of_node(main_node.element_id)
                )
        return None

    def _query_by_node(self, lib_id: int, subject_id: Optional[int], 
                        message: str,
                        message_vector: List[float], 
                        index_name: str,
                        node_types: Optional[List[NodeType]] = None, 
                        similarity_cutoff: float = config.SIMILARITY_CUTOFF,
                        search_type="vector") -> Optional[QueryResult]:
        call_clause = f"CALL db.index.vector.queryNodes($index_name, $top_k, $message_vector)" if search_type == "vector" else "CALL db.index.fulltext.queryNodes($index_name, $message)"
        subject_query_clause = f" AND node.subject_id=$subject_id" if subject_id else ""
        type_query_clause = f" AND node.type in $node_types" if node_types else ""
        query = f"""
        {call_clause}
        YIELD node, score
        WITH node, score
        WHERE score > $similarity_cutoff AND node.lib_id = $lib_id{subject_query_clause}{type_query_clause}
        RETURN DISTINCT id(node) AS id,
               elementId(node) AS element_id,
               node.lib_id as lib_id,
               node.subject_id as subject_id,
               node.content as content,
               node.type as type,
               node.title as title,
               node.title_vector as title_vector,
               node.content_vector as content_vector,
               node.created_at as created_at,
               node.updated_at as updated_at,
               score
        ORDER BY score DESC
        LIMIT $limit
        """
        params = {
            "lib_id": lib_id,
            "subject_id": subject_id,
            "node_types": [node_type.value for node_type in node_types] if node_types else None,
            "index_name": index_name,
            "message": '\"'+ message + '\"',
            "message_vector": message_vector,
            "top_k": config.TOP_K,
            "similarity_cutoff": max(config.SIMILARITY_CUTOFF, similarity_cutoff),
            "limit": 1,
        }
        return graph.query(query, params)

    def query_by_node(self, lib_id: int, subject_id: Optional[int], 
                        message: str, 
                        message_vector: List[float], 
                        limit: int = 5, 
                        only_title: bool = False,
                        search_type="vector") -> Optional[QueryResult]:
        query_result = self._query_node_by_title(lib_id, message, message_vector, search_type, subject_id)
        if not query_result and not only_title:
            query_result = self._query_node_by_content(lib_id, subject_id, message, message_vector, search_type)
        if query_result:
            node = Node.to_model(query_result[0])
            node.score = query_result[0].get("score")
            if node and node.type == NodeType.PROMPT:
                child_nodes = Node.query_child(node.element_id)
                if child_nodes:
                    node = child_nodes[0]
            if node and (node.type == NodeType.INFO or node.type == NodeType.HUMAN):
                related_nodes = self.find_related_nodes(lib_id, subject_id, node.id, limit) 
                prompts = self.find_prompts(node.element_id)
                return QueryResult(
                    document_page=None,
                    webpage=None,
                    document=None,
                    main_node=node,
                    prompts=prompts,
                    related_nodes=related_nodes,
                    entities=Entity.get_entities_of_node(node.element_id),
                    keywords=Keyword.get_keywords_of_node(node.element_id),
                    tags=Tag.get_tags_of_node(node.element_id)
                )
        return None

    def _query_node_by_title(self, lib_id, message, message_vector, search_type, subject_id):
        options = [
            (Node.title_vector_index_name, "vector") if search_type in ["vector", "hybrid"] else None,
            (Node.title_full_text_index_name, "fulltext") if search_type in ["fulltext", "hybrid"] else None,
        ]
        for option in options:
            if option:
                query_result = self._query_by_node(lib_id, subject_id, message, message_vector, option[0], similarity_cutoff=0.90, search_type=option[1])
                if query_result:
                    return query_result
        return None

    def _query_node_by_content(self, lib_id, subject_id, message, message_vector, search_type="vector", 
                    node_types: Optional[List[NodeType]] = None, 
                    similarity_cutoff: float = config.SIMILARITY_CUTOFF):
        options = [
            (Node.content_vector_index_name, "vector") if search_type in ["vector", "hybrid"] else None,
            (Node.content_full_text_index_name, "fulltext") if search_type in ["fulltext", "hybrid"] else None,
        ]
        for option in options:
            if option:
                query_result = self._query_by_node(lib_id, subject_id, message, message_vector, option[0], node_types=node_types, similarity_cutoff=similarity_cutoff, search_type=option[1])
                if query_result:
                    return query_result
        return None