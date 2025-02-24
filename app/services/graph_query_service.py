from collections import namedtuple
from typing import Optional, List, Union, AsyncGenerator
import asyncio
from ai.llm import Llm
from core.extends_logger import logger
from core.i18n import _
from graph.graph_query import QueryResult
from graph.node import Node
from graph.relationship import Relationship
from schemas.graph import GraphConditionView, ChatConditionView
from services.graph_base_service import GraphBaseService

# Define the named tuple for the query result
KnowledgeQueryResult = namedtuple(
    'KnowledgeQueryResult',
    ['text', 'main_node', 'entities', 'keywords', 'tags', 'webpage', 'document', 'prompts', 'related_nodes']
)

class GraphQueryService(GraphBaseService):
    def __init__(self):
        super(GraphQueryService, self).__init__()

    async def query_graph(self, lib_id: int, condition: GraphConditionView) -> tuple:
        """
        Queries the knowledge graph for nodes and relationships based on the given conditions.

        Args:
            lib_id (int): The ID of the knowledge library.
            condition (GraphConditionView): The conditions for filtering the graph.

        Returns:
            tuple: A tuple containing:
                - List of nodes.
                - List of node overviews.
                - List of relationships.
                - List of relationship overviews.
                - The generation status of the knowledge library.
        """
        knowledge_lib = await self.find_knowledge_lib_by_id(lib_id)
        status = knowledge_lib.status if knowledge_lib else None

        # Query nodes and relationships
        if condition.content or condition.type:
            nodes, links = Node.search_graph_node(lib_id, condition)
            node_overviews, link_overviews = self.query_graph_overview(lib_id, condition)
        else:
            nodes, node_overviews = Node.query_graph_node(lib_id, condition.subject_ids)
            links, link_overviews = Relationship.query_graph_relationship(lib_id, condition.subject_ids, condition.relationship_type)

        return nodes, node_overviews, links, link_overviews, status

    def query_graph_overview(self, lib_id: int, condition: GraphConditionView) -> tuple:
        """
        Queries the overview of nodes and relationships in the graph.

        Args:
            lib_id (int): The ID of the knowledge library.
            condition (GraphConditionView): The conditions for filtering the graph.

        Returns:
            tuple: A tuple containing:
                - List of node overviews.
                - List of relationship overviews.
        """
        logger.info(f"Querying graph overview for lib_id: {lib_id}")
        try:
            node_overviews = Node.query_graph_node_overviews(lib_id, condition.subject_ids)
            link_overviews = Relationship.query_graph_relationship_overviews(lib_id, condition.subject_ids, condition.relationship_type)
            logger.info(f"Successfully queried graph overview for lib_id: {lib_id}")
            return node_overviews, link_overviews
        except Exception as e:
            logger.error(f"Failed to query graph overview for lib_id: {lib_id}. Error: {e}")
            raise RuntimeError(f"Failed to query graph overview: {e}") from e

    async def search_knowledge_graph(
        self, query_condition: ChatConditionView
    ) -> Union[KnowledgeQueryResult, AsyncGenerator[KnowledgeQueryResult, None]]:
        """
        Queries the knowledge graph and returns results either synchronously or as a stream.

        Args:
            query_condition (ChatConditionView): The conditions for querying the knowledge graph.

        Returns:
            Union[KnowledgeQueryResult, AsyncGenerator[KnowledgeQueryResult, None]]:
                - If `query_condition.return_method == "sync"`, returns a synchronous `KnowledgeQueryResult`.
                - If `query_condition.return_method == "stream"`, returns an asynchronous generator yielding `KnowledgeQueryResult`.
        """
        print("----search_knowledge_graph start:")
        if not query_condition.lib_id:
            raise ValueError(_("Knowledge library ID is required"))

        lib = await self.find_knowledge_lib_by_id(query_condition.lib_id)
        if not lib:
            raise ValueError(_("Knowledge library not found"))

        if not lib.status == "PUBLISHED":
            raise ValueError(_("Knowledge library is not published"))

        query_result: QueryResult = None
        print("----search_knowledge_graph:", query_condition)
        if query_condition.prompt_element_id:
            query_result = await self._search_knowledge_graph_by_prompt(query_condition)
            print("----search_knowledge_graph_by_prompt:", query_result.keywords)
        elif query_condition.related_node_element_id:
            query_result = await self._search_knowledge_graph_by_related_node(query_condition)
            print("----search_knowledge_graph_by_related_node:", query_result.keywords)
        else:
            query_result = await self._search_knowledge_graph_by_message(query_condition) 

        if not query_result:
            empty_result = KnowledgeQueryResult(
                    text=_("Empty result"),
                    main_node=None,
                    entities=None,
                    keywords=None,
                    tags=None,
                    webpage=None,
                    document=None,
                    prompts=None,
                    related_nodes=None,
                )
            if query_condition.return_method == "sync":
                return empty_result
            async def async_generator():
                yield empty_result
                return
            return async_generator()

        
        # Prepare messages for summarization
        messages = self._prepare_messages_for_summarization(query_result)
        print("----messages:", messages)
        if query_condition.return_method == "sync":
            if query_condition.is_summary:
                summary = Llm.summary_message_history(
                    messages=messages,
                    llm_name=query_condition.llm_name,
                    chain_type=query_condition.chain_type,
                )
                summary_message = summary.get("output_text", "") if summary else ""
                return KnowledgeQueryResult(
                    text=summary_message,
                    main_node=query_result.main_node,
                    entities=query_result.entities,
                    keywords=query_result.keywords,
                    tags=query_result.tags,
                    webpage=query_result.webpage,
                    document=query_result.document,
                    prompts=query_result.prompts,
                    related_nodes=query_result.related_nodes,
                )
            else:
                return KnowledgeQueryResult(
                    text="\n\n".join(messages),
                    main_node=query_result.main_node,
                    entities=query_result.entities,
                    keywords=query_result.keywords,
                    tags=query_result.tags,
                    webpage=query_result.webpage,
                    document=query_result.document,
                    prompts=query_result.prompts,
                    related_nodes=query_result.related_nodes,
                )
        else:
            async def generate_stream() -> AsyncGenerator[KnowledgeQueryResult, None]:
                if query_condition.is_summary:
                    async for summary_chunk in Llm.summary_message_history_streaming(
                            messages=messages,
                            llm_name=query_condition.llm_name,
                            chain_type=query_condition.chain_type,
                    ):
                        yield KnowledgeQueryResult(summary_chunk.get("output_text"), None, None, None, None, None, None, None, None)
                    
                    yield KnowledgeQueryResult(None, query_result.main_node, None, None, None, None, None, None, None)
                    yield KnowledgeQueryResult(None, None, query_result.entities, None, None, None, None, None, None)
                    yield KnowledgeQueryResult(None, None, None, query_result.keywords, None, None, None, None, None)
                    yield KnowledgeQueryResult(None, None, None, None, query_result.tags, None, None, None, None)
                    yield KnowledgeQueryResult(None, None, None, None, None, query_result.webpage, None, None, None)
                    yield KnowledgeQueryResult(None, None, None, None, None, None, query_result.document, None, None)
                    yield KnowledgeQueryResult(None, None, None, None, None, None, None, query_result.prompts, None)
                    print("----related_nodes:", query_result.related_nodes)
                    yield KnowledgeQueryResult(None, None, None, None, None, None, None, None, query_result.related_nodes)
                else:
                    for message in messages:
                        yield KnowledgeQueryResult(message, None, None, None, None, None, None, None, None)
                    yield KnowledgeQueryResult(None, query_result.main_node, None, None, None, None, None, None, None)
                    yield KnowledgeQueryResult(None, None, query_result.entities, None, None, None, None, None, None)
                    yield KnowledgeQueryResult(None, None, None, query_result.keywords, None, None, None, None, None)
                    yield KnowledgeQueryResult(None, None, None, None, query_result.tags, None, None, None, None)
                    yield KnowledgeQueryResult(None, None, None, None, None, query_result.webpage, None, None, None)
                    yield KnowledgeQueryResult(None, None, None, None, None, None, query_result.document, None, None)
                    yield KnowledgeQueryResult(None, None, None, None, None, None, None, query_result.prompts, None)
                    yield KnowledgeQueryResult(None, None, None, None, None, None, None, None, query_result.related_nodes)

            return generate_stream()
                    
    async def _search_knowledge_graph_by_prompt(self, query_condition: ChatConditionView) -> QueryResult:
        """
        Queries the knowledge graph by prompt and returns the result.

        Args:
            query_condition (ChatConditionView): The conditions for querying the knowledge graph.

        Returns:
            KnowledgeQueryResult: The query result.
        """
        query_result: QueryResult = self.knowledge_graph_query.search_knowledge_graph_by_prompt(
            prompt_element_id=query_condition.prompt_element_id,
            limit=query_condition.limit,
        )
        return query_result

    async def _search_knowledge_graph_by_related_node(self, query_condition: ChatConditionView) -> QueryResult:
        """
        Queries the knowledge graph by related node and returns the result.

        Args:
            query_condition (ChatConditionView): The conditions for querying the knowledge graph.

        Returns:
            KnowledgeQueryResult: The query result.
        """
        query_result: QueryResult = self.knowledge_graph_query.search_knowledge_graph_by_related_node(
            related_node_element_id=query_condition.related_node_element_id,
            limit=query_condition.limit,
        )
        return query_result

    async def _search_knowledge_graph_by_message(
        self, query_condition: ChatConditionView
    ) -> QueryResult:
        """
        Queries the knowledge graph based on the provided message and streams the results.

        Args:
            query_condition (ChatConditionView): The conditions for querying the knowledge graph.

        Yields:
            KnowledgeQueryResult: The query result as it becomes available.
        """
        # Summarize the message history if there are multiple messages
        if len(query_condition.messages) > 1:
            if query_condition.is_summary:
                # Stream the summarization process
                summary = Llm.summary_message_history(
                    messages=query_condition.messages,
                    llm_name=query_condition.llm_name,
                    chain_type=query_condition.chain_type,
                )
                summary_message = summary.get("output_text", "") if summary else ""
            else:
                summary_message = "  ".join(query_condition.messages)
        else:
            summary_message = query_condition.messages[0]

        # Query the knowledge graph
        query_result: QueryResult = self.knowledge_graph_query.search_knowledge_graph(
            message=summary_message,
            lib_id=query_condition.lib_id,
            subject_id=query_condition.subject_id,
            limit=query_condition.limit,
            embedding_model=query_condition.embedding_model,
            max_tokens_each_chunk=query_condition.max_tokens_each_chunk,
            search_scope=query_condition.search_scope,
            only_title=query_condition.only_title,
        )
        return query_result


    def _prepare_messages_for_summarization(self, query_result: QueryResult) -> List[str]:
        """
        Prepares messages for summarization based on the query result.

        Args:
            query_result (QueryResult): The result of the knowledge graph query.

        Returns:
            List[str]: A list of messages for summarization.
        """
        messages = []

        if query_result.document_page:
            messages.append(query_result.document_page.content)

        if query_result.webpage:
            if query_result.webpage.title:
                messages.append(query_result.webpage.title)
            if query_result.webpage.content:
                messages.append(query_result.webpage.content)
            messages.append(_("The data from the URL: {url}".format(url=query_result.webpage.url)))
        
        if query_result.document:
            if query_result.document.content:
                messages.append(query_result.document.content)
            messages.append(_("The data from the file: {file_name}".format(file_name=query_result.document.name)))
        
        if not query_result.document_page and not query_result.webpage and not query_result.document and query_result.main_node:
            print("------query_result.main_node.content:", query_result.main_node.content)
            messages.append(query_result.main_node.content)
        
        if query_result.entities:
            messages.append(_("**Entities**"))
            for entity in query_result.entities:
                messages.append(entity.content)
        if query_result.keywords:
            messages.append(_("**Keywords**"))
            for keyword in query_result.keywords:
                messages.append(keyword.content)
        if query_result.tags:
            messages.append(_("**Tags**"))
            for tag in query_result.tags:
                messages.append(tag.content)

        return messages