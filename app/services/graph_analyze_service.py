import asyncio
import concurrent.futures
import datetime
import os
import threading
from typing import Optional, List, Any

from numpy import lib
from sqlalchemy import select

import core.database as db
from ai.document_service import DocumentService
from ai.llm import Llm
from ai.nlp import extract_entities
from core import config
from core.extends_logger import logger
from core.i18n import _
from graph import NodeType
from graph.document import Document
from graph.document_page import DocumentPage
from graph.entity import Entity
from graph.keyword import Keyword
from graph.node import Node
from graph.tag import Tag
from graph.webpage import WebPage
from models.models import KnowledgeLib
from schemas.graph import GraphGenerateConditionView
from services.graph_generate_service import GraphGenerateService


class GraphAnalyzeService(GraphGenerateService):
    def __init__(self):
        super(GraphAnalyzeService, self).__init__()
        self.document_service = DocumentService()

    async def analyze_graph(self, lib_id: int,
                            subject_ids: List[int] = None,
                            llm_name: str = config.DEFAULT_LLM_NAME,
                            embedding_model: str = "sbert",
                            max_tokens_each_chunk: int = 128):
        """
        Analyzes the graph using asyncio.gather for concurrent tasks.

        Args:
            lib_id (int): The ID of the knowledge library.
            subject_ids (List[int]): The list of subject IDs to analyze.
            llm_name (str): The name of the LLM to use.
            embedding_model (str): The embedding model to use.
            max_tokens_each_chunk (int): The maximum number of tokens per chunk.

        Raises:
            ValueError: If lib_id or subject_ids are not provided.
            RuntimeError: If the analysis fails or is cancelled.
        """
        if not lib_id or not subject_ids or len(subject_ids) == 0:
            raise ValueError(_("Lib id and subject id are required."))

        knowledge_lib = await self.find_knowledge_lib_by_id(lib_id)
        if knowledge_lib.status in ['GENERATING', 'ANALYZING']:
            logger.warning(f"Graph generation or analysis is already in progress for library ID: {lib_id}.")
            raise RuntimeError(_("Graph generation or analysis is already in progress."))

        if knowledge_lib.status == 'PUBLISHED':
            logger.warning(f"Library is published. Please unpublish the library first.")
            raise RuntimeError(_("Library is published. Please unpublish the library first."))

        try:
            # Set the status to 'ANALYZING'
            await self.update_knowledge_lib_status(lib_id, 'ANALYZING')

            # Fetch the knowledge library and subject nodes
            nodes, overviews = Node.query_graph_node(lib_id, subject_ids=subject_ids)
            if not nodes:
                logger.info(f"No nodes found for subject_ids: {subject_ids}")
                raise ValueError(_("Lib id and subject id are required."))

            # Prepare the data for each node
            data_list = [
                GraphGenerateConditionView(
                    lib_id=lib_id,
                    llm_name=llm_name,
                    embedding_model=embedding_model,
                    max_tokens_each_chunk=max_tokens_each_chunk,
                    subject_id=node.subject_id,
                    element_id=node.element_id,
                    max_depth = i,

                )
                for i, node in enumerate(nodes)
            ]

            # Define async task processing function
            async def process_node(data):
                try:
                    await self.analyze_graph_node(data)
                    logger.info(f"Successfully analyzed node with element_id: {data.element_id}")
                except Exception as e:
                    logger.error(f"Failed to analyze node with element_id {data.element_id}. Error: {e}")
                    raise RuntimeError(f"Failed to analyze node: {e}") from e

            # Use asyncio.gather to process all nodes concurrently
            tasks = [process_node(data) for data in data_list]
            await asyncio.gather(*tasks)

            # Update the knowledge library status to 'PENDING'
            await self.update_knowledge_lib_status(lib_id, 'PENDING')
        except Exception as e:
            # Rollback the transaction and log the error
            await self.update_knowledge_lib_status(lib_id, 'PENDING')

            error_msg = f"Failed to analyze graph for lib_id: {lib_id}, subject_id: {subject_ids}. Error: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def get_knowledge_lib_sync(self, lib_id):
        """Fetches the knowledge library from an async function in a thread-safe way."""
        loop = asyncio.get_event_loop()

        if loop.is_running():
            # If we're already inside an event loop, use a background thread
            executor_loop = asyncio.new_event_loop()
            threading.Thread(target=lambda: executor_loop.run_forever(), daemon=True).start()
            future = asyncio.run_coroutine_threadsafe(self.find_knowledge_lib_by_id(lib_id), executor_loop)
        else:
            # If no event loop is running, just use the current loop
            future = asyncio.run_coroutine_threadsafe(self.find_knowledge_lib_by_id(lib_id), loop)

        return future.result()  # Block

    async def analyze_graph_node(self, data: GraphGenerateConditionView) -> Optional[Node]:
        """
        Analyzes a graph node by extracting entities, generating titles, keywords, tags, and embeddings.

        Args:
            data (GraphGenerateConditionView): The data for analyzing the node.

        Returns:
            Optional[Node]: The updated node if successful, otherwise None.

        Raises:
            ValueError: If the node element ID is not provided or the node is not found.
            RuntimeError: If any step in the analysis fails.
        """
        logger.info(f"Starting analysis for node with element_id: {data.element_id}")

        lib_id = data.lib_id
        # Check if analysis is cancelled
        if lib_id:
            knowledge_lib = await self.find_knowledge_lib_by_id(lib_id)
            if knowledge_lib.status in ['GENERATING']:
                logger.warning(f"Graph generation is already in progress for library ID: {lib_id}.")
                raise RuntimeError(_("Graph generation is already in progress."))

            if knowledge_lib.status == 'PUBLISHED':
                logger.warning(f"Library is published. Please unpublish the library first.")
                raise RuntimeError(_("Library is published. Please unpublish the library first."))

        # Validate input
        if data.element_id is None:
            error_msg = "Node element id must be provided."
            logger.error(error_msg)
            raise ValueError(_(error_msg))

        # Fetch the node
        node = Node.find_detail_by_element_id(data.element_id)
        if node is None:
            error_msg = f"Node with element_id {data.element_id} not found."
            logger.error(error_msg)
            raise ValueError(_(error_msg))

        try:
            # Step 1: Analyze entities
            self._analyze_entities(node, data.embedding_model, data.max_tokens_each_chunk)

            # Step 2: Analyze title (for HUMAN or INFO nodes)
            if node.type in [NodeType.HUMAN, NodeType.INFO]:
                self._analyze_title(node, data.llm_name, data.embedding_model, data.max_tokens_each_chunk)

            # Step 3: Analyze keywords
            self._analyze_keywords(node, data.llm_name, data.embedding_model, data.max_tokens_each_chunk)

            # Step 4: Analyze tags
            self._analyze_tags(node, data.llm_name, data.embedding_model, data.max_tokens_each_chunk)

            # Step 5: Convert content to vector
            self._convert_content_to_vector(node, data.embedding_model, data.max_tokens_each_chunk)

            # Step 6: Analyze documents associated with the node
            self._analyze_documents(node, data.llm_name, data.embedding_model, data.max_tokens_each_chunk)

            # Step 7: Analyze web pages associated with the node
            self._analyze_webpages(node, data.llm_name, data.embedding_model, data.max_tokens_each_chunk)

            # Step 8: Update the node with the new embedding model
            node.embedding_model = data.embedding_model
            updated_node = node.update()

            logger.info(f"Successfully analyzed and updated node with element_id: {data.element_id}")
            return updated_node

        except Exception as e:
            logger.error(f"Failed to analyze node with element_id {data.element_id}. Error: {e}")
            raise RuntimeError(f"Failed to analyze node: {e}") from e

    def _analyze_entities(self, node: Node, embedding_model: str, max_tokens_each_chunk: int) -> None:
        """
        Extracts entities from the node content and adds them to the graph.

        Args:
            node (Node): The node to analyze.
            embedding_model (str): The embedding model to use.
            max_tokens_each_chunk (int): The maximum number of tokens per chunk.

        Returns:
            None
        """
        analysis_entities = extract_entities(node.content)
        if not analysis_entities:
            logger.debug(f"No entities found for node with element_id: {node.element_id}")
            return

        # Delete existing entities
        Entity.delete_entities_of_node(node.element_id)

        # Add new entities
        for entity in analysis_entities:
            entity_vector = self.embedding_factory.get_embedding(
                text=entity,
                model_name=embedding_model,
                max_tokens_each_chunk=max_tokens_each_chunk,
            ).tolist()
            Entity.add_entity_node(
                lib_id=node.lib_id,
                subject_id=node.subject_id,
                node_element_id=node.element_id,
                content=entity,
                content_vector=entity_vector,
                embedding_model=embedding_model,
            )
        logger.debug(f"Added {len(analysis_entities)} entities for node with element_id: {node.element_id}")

    def _analyze_title(self, node: Node, llm_name: str, embedding_model: str, max_tokens_each_chunk: int) -> None:
        """
        Analyzes and updates the title of the node using an LLM.

        Args:
            node (Node): The node to analyze.
            llm_name (str): The name of the LLM to use.
            embedding_model (str): The embedding model to use.
            max_tokens_each_chunk (int): The maximum number of tokens per chunk.

        Returns:
            None
        """
        title_template = Llm.get_prompt_template("analysis_title")
        title_prompt = title_template.format(input=node.content)
        analysis_title = Llm.get_ai_json_response(title_prompt, llm_name)

        if analysis_title:
            node.title = analysis_title.strip()
            node.title_vector = self.embedding_factory.get_embedding(
                text=analysis_title.strip(),
                model_name=embedding_model,
                max_tokens_each_chunk=max_tokens_each_chunk,
            ).tolist()
            logger.debug(f"Updated title for node with element_id: {node.element_id}")

    def _analyze_keywords(self, node: Node, llm_name: str, embedding_model: str, max_tokens_each_chunk: int) -> None:
        """
        Analyzes and updates the keywords of the node using an LLM.

        Args:
            node (Node): The node to analyze.
            llm_name (str): The name of the LLM to use.
            embedding_model (str): The embedding model to use.
            max_tokens_each_chunk (int): The maximum number of tokens per chunk.

        Returns:
            None
        """
        keywords_template = Llm.get_prompt_template("analysis_keywords")
        keywords_prompt = keywords_template.format(input=node.content)
        analysis_keywords = Llm.get_ai_json_response(keywords_prompt, llm_name)

        if analysis_keywords:
            Keyword.delete_keywords_of_node(node.element_id)
            for keyword in analysis_keywords:
                keyword_vector = self.embedding_factory.get_embedding(
                    text=keyword,
                    model_name=embedding_model,
                    max_tokens_each_chunk=max_tokens_each_chunk,
                ).tolist()
                Keyword.add_keyword_node(
                    lib_id=node.lib_id,
                    subject_id=node.subject_id,
                    node_element_id=node.element_id,
                    content=keyword,
                    content_vector=keyword_vector,
                    embedding_model=embedding_model,
                )
            logger.debug(f"Added {len(analysis_keywords)} keywords for node with element_id: {node.element_id}")

    def _analyze_tags(self, node: Node, llm_name: str, embedding_model: str, max_tokens_each_chunk: int) -> None:
        """
        Analyzes and updates the tags of the node using an LLM.

        Args:
            node (Node): The node to analyze.
            llm_name (str): The name of the LLM to use.
            embedding_model (str): The embedding model to use.
            max_tokens_each_chunk (int): The maximum number of tokens per chunk.

        Returns:
            None
        """
        tags_template = Llm.get_prompt_template("analysis_tags")
        tags_prompt = tags_template.format(input=node.content)
        analysis_tags = Llm.get_ai_json_response(tags_prompt, llm_name)

        if analysis_tags:
            Tag.delete_tags_of_node(node.element_id)
            for tag in analysis_tags:
                tag_vector = self.embedding_factory.get_embedding(
                    text=tag,
                    model_name=embedding_model,
                    max_tokens_each_chunk=max_tokens_each_chunk,
                ).tolist()
                Tag.add_tag_node(
                    lib_id=node.lib_id,
                    subject_id=node.subject_id,
                    node_element_id=node.element_id,
                    content=tag,
                    content_vector=tag_vector,
                    embedding_model=embedding_model,
                )
            logger.debug(f"Added {len(analysis_tags)} tags for node with element_id: {node.element_id}")

    def _convert_content_to_vector(self, node: Node, embedding_model: str, max_tokens_each_chunk: int) -> None:
        """
        Converts the node content to a vector using the specified embedding model.

        Args:
            node (Node): The node to analyze.
            embedding_model (str): The embedding model to use.
            max_tokens_each_chunk (int): The maximum number of tokens per chunk.

        Returns:
            None
        """
        if node.content:
            node.content_vector = self.embedding_factory.get_embedding(
                text=node.content,
                model_name=embedding_model,
                max_tokens_each_chunk=max_tokens_each_chunk,
            ).tolist()
            logger.debug(f"Converted content to vector for node with element_id: {node.element_id}")

    def _analyze_documents(self, node: Node, llm_name: str, embedding_model: str, max_tokens_each_chunk: int) -> None:
        """
        Analyzes documents associated with the node.

        Args:
            node (Node): The node to analyze.
            llm_name (str): The name of the LLM to use.
            embedding_model (str): The embedding model to use.
            max_tokens_each_chunk (int): The maximum number of tokens per chunk.

        Returns:
            None
        """
        documents = Document.get_documents_of_node(node.element_id)
        if documents:
            for document in documents:
                self.analyze_graph_node_file(
                    document.element_id,
                    llm_name=llm_name,
                    embedding_model=embedding_model,
                    max_tokens_each_chunk=max_tokens_each_chunk,
                )
            logger.debug(f"Analyzed {len(documents)} documents for node with element_id: {node.element_id}")

    def _analyze_webpages(self, node: Node, llm_name: str, embedding_model: str, max_tokens_each_chunk: int) -> None:
        """
        Analyzes web pages associated with the node.

        Args:
            node (Node): The node to analyze.
            llm_name (str): The name of the LLM to use.
            embedding_model (str): The embedding model to use.
            max_tokens_each_chunk (int): The maximum number of tokens per chunk.

        Returns:
            None
        """
        webpages = WebPage.get_webpages_of_node(node.element_id)
        if webpages:
            for webpage in webpages:
                self.analyze_graph_node_webpage(
                    webpage.element_id,
                    llm_name=llm_name,
                    embedding_model=embedding_model,
                    max_tokens_each_chunk=max_tokens_each_chunk,
                )
            logger.debug(f"Analyzed {len(webpages)} web pages for node with element_id: {node.element_id}")


    def analyze_graph_node_file(
            self,
            document_element_id: str,
            llm_name: str = config.DEFAULT_LLM_NAME,
            embedding_model: str = "sbert",
            max_tokens_each_chunk: int = 128,
    ) -> Optional[Document]:
        """
        Analyzes a file associated with a graph node by extracting its content and generating embeddings.

        Args:
            document_element_id (str): The unique identifier of the document.
            llm_name (str): The name of the LLM to use for analysis. Defaults to config.DEFAULT_LLM_NAME.
            embedding_model (str): The embedding model to use. Defaults to "sbert".
            max_tokens_each_chunk (int): The maximum number of tokens per chunk. Defaults to 128.

        Returns:
            Optional[Document]: The updated document if successful, otherwise None.

        Raises:
            ValueError: If the document is not found.
            RuntimeError: If the analysis fails.
        """
        logger.info(f"Starting analysis for document with element_id: {document_element_id}")

        # Fetch the document
        document = Document.get_document_by_element_id(document_element_id)
        if not document:
            error_msg = f"Document with element_id {document_element_id} not found."
            logger.error(error_msg)
            raise ValueError(_(error_msg))

        try:
            # Prepare file path
            file_path = os.path.join(config.UPLOAD_DIR, document.saved_at)
            if not os.path.isfile(file_path):
                error_msg = f"File not found at path: {file_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)

            # Analyze the file
            summary, splits = self.document_service.analysis_file(
                file_path, llm_name=llm_name, embedding_model=embedding_model
            )
            if not summary:
                error_msg = f"Failed to analyze file at path: {file_path}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            # Extract title and summary
            document_title = summary.get("title", "")
            document_summary = summary.get("summary", "")

            # Generate embeddings for the title and summary
            document_title_vector = self.embedding_factory.get_embedding(
                text=document_title,
                model_name=embedding_model,
                max_tokens_each_chunk=max_tokens_each_chunk,
            ).tolist()
            document_summary_vector = self.embedding_factory.get_embedding(
                text=document_summary,
                model_name=embedding_model,
                max_tokens_each_chunk=max_tokens_each_chunk,
            ).tolist()

            # Update the document
            document.title = document_title
            document.content = document_summary
            document.title_vector = document_title_vector
            document.content_vector = document_summary_vector
            document.embedding_model = embedding_model
            updated_document = document.update()
            logger.info(f"Successfully updated document with element_id: {document_element_id}")

            # Save the document splits (if any)
            self._save_document_splits(
                lib_id=document.lib_id,
                subject_id=document.subject_id,
                node_element_id=Document.get_parent_element_id_by_document(document_element_id),
                document_element_id=document_element_id,
                splits=splits,
                embedding_model=embedding_model,
                max_tokens_each_chunk=max_tokens_each_chunk,
            )

            return self.get_document_detail(document_element_id)
        except Exception as e:
            logger.error(f"Failed to analyze document with element_id {document_element_id}. Error: {e}")
            raise RuntimeError(f"Failed to analyze document: {e}") from e

    def _save_document_splits(
            self,
            lib_id: int,
            subject_id: int,
            node_element_id: str,
            document_element_id: str,
            splits: List[Any],
            embedding_model: str,
            max_tokens_each_chunk: int,
    ) -> None:
        """
        Saves the splits of a document as individual pages in the graph.

        Args:
            lib_id (int): The ID of the knowledge library.
            subject_id (int): The ID of the knowledge library subject.
            node_element_id (str): The unique identifier of the node.
            document_element_id (str): The unique identifier of the document.
            splits (List[Any]): The splits of the document content.
            embedding_model (str): The embedding model to use.
            max_tokens_each_chunk (int): The maximum number of tokens per chunk.

        Returns:
            None
        """
        logger.info(f"Saving document splits for document with element_id: {document_element_id}")
        if not splits:
            logger.warning(f"No splits found for document with element_id: {document_element_id}")
            return

        try:
            # Delete existing document pages
            DocumentPage.delete_document_pages_of_parent(document_element_id)

            # Add new document pages
            for split in splits:
                if not split.metadata.get("source", "") or not split.page_content:
                    continue

                DocumentPage.add_document_page_node(
                    lib_id=lib_id,
                    subject_id=subject_id,
                    parent_element_id=node_element_id,
                    document_element_id=document_element_id,
                    source=split.metadata.get("source", ""),
                    title=split.metadata.get("title", ""),
                    subtitle=split.metadata.get("subtitle", ""),
                    page=split.metadata.get("page", 0),
                    row=split.metadata.get("row", 0),
                    content=split.page_content,
                    content_vector=self.embedding_factory.get_embedding(
                        text=split.page_content,
                        model_name=embedding_model,
                        max_tokens_each_chunk=max_tokens_each_chunk,
                    ).tolist(),
                    embedding_model=embedding_model,
                )
            logger.info(
                f"Successfully saved {len(splits)} document splits for document with element_id: {document_element_id}")

        except Exception as e:
            logger.error(
                f"Failed to save document splits for document with element_id {document_element_id}. Error: {e}")
            raise RuntimeError(f"Failed to save document splits: {e}") from e


    def analyze_graph_node_webpage(
            self,
            webpage_element_id: str,
            llm_name: str = config.DEFAULT_LLM_NAME,
            embedding_model: str = "sbert",
            max_tokens_each_chunk: int = 128,
    ) -> Optional[WebPage]:
        """
        Analyzes a webpage associated with a graph node by extracting its content and generating embeddings.

        Args:
            webpage_element_id (str): The unique identifier of the webpage.
            llm_name (str): The name of the LLM to use for analysis. Defaults to config.DEFAULT_LLM_NAME.
            embedding_model (str): The embedding model to use. Defaults to "sbert".
            max_tokens_each_chunk (int): The maximum number of tokens per chunk. Defaults to 128.

        Returns:
            Optional[WebPage]: The updated webpage if successful, otherwise None.

        Raises:
            ValueError: If the webpage is not found.
            RuntimeError: If the analysis fails.
        """
        logger.info(f"Starting analysis for webpage with element_id: {webpage_element_id}")

        # Fetch the webpage
        webpage: WebPage = WebPage.get_webpage_by_element_id(webpage_element_id)
        if not webpage:
            error_msg = f"Webpage with element_id {webpage_element_id} not found."
            logger.error(error_msg)
            raise ValueError(_(error_msg))

        try:
            # Analyze the webpage URL
            summary, splits = self.document_service.analysis_url(webpage.url, llm_name)
            if summary:
                webpage.title = summary.get("title", "")
                webpage.content = summary.get("summary", "")

            # Generate embeddings for the title and content
            webpage.title_vector = self.embedding_factory.get_embedding(
                text=webpage.title,
                model_name=embedding_model,
                max_tokens_each_chunk=max_tokens_each_chunk,
            ).tolist()
            webpage.content_vector = self.embedding_factory.get_embedding(
                text=webpage.content,
                model_name=embedding_model,
                max_tokens_each_chunk=max_tokens_each_chunk,
            ).tolist()
            webpage.embedding_model = embedding_model

            # Update the webpage
            updated_webpage = webpage.update()
            logger.info(f"Successfully updated webpage with element_id: {webpage_element_id}")

            # Save the document splits (if any)
            lib_id = webpage.lib_id
            subject_id = webpage.subject_id
            node_element_id = WebPage.get_parent_element_id(webpage.element_id)
            document_element_id = webpage.element_id
            self._save_document_splits(
                lib_id, subject_id, node_element_id, document_element_id, splits, embedding_model, max_tokens_each_chunk
            )

            return self.get_analyzed_graph_node_webpage(webpage_element_id)

        except Exception as e:
            logger.error(f"Failed to analyze webpage with element_id {webpage_element_id}. Error: {e}")
            raise RuntimeError(f"Failed to analyze webpage: {e}") from e