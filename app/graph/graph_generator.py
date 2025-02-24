import asyncio
from typing import Dict, List, Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import make_transient

import core.database as db
from ai.llm import Llm
from core.config import DEEP_LIMIT, LLM_TIMEOUT
from core.extends_logger import logger
from core.i18n import _
from models.models import KnowledgeLib
from . import RelationshipType, graph
from .node import Node
from .relationship import Relationship

GENERATING_CANCELED: str = "PENDING"

class KnowledgeGraphGenerator:
    def __init__(self, lib_name: str, title: str, llm_name: str, max_depth: int = 4, lib_id: int = 1,
                 subject_id: int = 1):
        """
        Initializes the KnowledgeGraphGenerator.

        Args:
            lib_name (str): Name of the knowledge library.
            title (str): Title of the subject.
            llm_name (str): Name of the LLM to use.
            max_depth (int): Maximum depth of the knowledge graph. Defaults to 4.
            lib_id (int): ID of the knowledge library. Defaults to 1.
            subject_id (int): ID of the subject. Defaults to 1.

        Raises:
            ValueError: If lib_name, title, or max_depth are invalid.
        """
        if not lib_name:
            raise ValueError(_("lib_name cannot be empty."))
        if not title:
            raise ValueError(_("title cannot be empty."))
        if max_depth > DEEP_LIMIT:
            raise ValueError(_(f"max_depth must be less than {DEEP_LIMIT}"))
        if max_depth < 2:
            raise ValueError(_("max_depth must be greater than 1."))
        if max_depth % 2 != 0:
            raise ValueError(_("max_depth must be an even number."))

        self.lib_name = lib_name
        self.title = title
        self.llm_name = llm_name
        self.lib_id = lib_id
        self.subject_id = subject_id
        self.max_depth = max_depth
        self.progress = 0  # Tracks the progress of graph generation

    async def __call__(self):
        """
        Entry point for generating the knowledge graph asynchronously.
        """
        knowledge_lib = await self._get_knowledge_lib()
        if knowledge_lib and knowledge_lib.status == GENERATING_CANCELED:
            logger.info("Knowledge lib is generating canceled")
            return

        root_node = self._get_or_create_root_node()
        logger.debug(f"lib_id: {self.lib_id}, subject_id: {self.subject_id}, root_node: {root_node}")

        await self._delete_existing_nodes()
        logger.debug(f"generate_knowledge_graph deep: 1, title: {self.title}")

        subject_node = Node.add_subject_node(self.lib_id, self.subject_id, self.title, depth=1)
        await self.generate_knowledge_graph_recursive(subject_node)

    async def _get_knowledge_lib(self) -> Optional[KnowledgeLib]:
        """
        Fetches the KnowledgeLib record from the database.

        Returns:
            Optional[KnowledgeLib]: The KnowledgeLib record, or None if not found.
        """
        try:
            async with db.get_async_session() as session:
                result = await session.execute(select(KnowledgeLib).filter(KnowledgeLib.id == self.lib_id))
                knowledge_lib = result.scalar_one_or_none()
                if knowledge_lib:
                    # Detach the object from the session
                    make_transient(knowledge_lib)
                return knowledge_lib
        except Exception as e:
            logger.error(f"Failed to fetch KnowledgeLib: {e}")
            raise

    def _get_or_create_root_node(self) -> Node:
        """
        Fetches or creates the root node for the knowledge graph.

        Returns:
            Node: The root node.
        """
        root_node = Node.query_root_node(self.lib_id)
        if not root_node:
            root_node = Node.add_root_node(self.lib_id, self.lib_name)
        return root_node

    async def _delete_existing_nodes(self):
        """
        Deletes existing nodes for the given lib_id and subject_id asynchronously.
        """
        exists_query = "MATCH (n) WHERE n.lib_id=$lib_id AND n.subject_id=$subject_id RETURN COUNT(n) AS count"
        query_result = graph.query(exists_query, {"lib_id": self.lib_id, "subject_id": self.subject_id})
        existing_count = query_result[0]["count"]

        if existing_count > 0:
            logger.debug(f"Found existing nodes with lib_id: {self.lib_id}, subject_id: {self.subject_id}. Deleting existing nodes.")
            delete_query = "MATCH (n) WHERE n.lib_id=$lib_id AND n.subject_id=$subject_id DETACH DELETE n"
            graph.query(delete_query, {"lib_id": self.lib_id, "subject_id": self.subject_id})

    async def generate_knowledge_graph_recursive(self, parent_node: Node):
        """
        Recursively generates the knowledge graph starting from the parent node asynchronously.

        Args:
            parent_node (Node): The parent node to start generation from.
        """
        knowledge_lib = await self._get_knowledge_lib()
        if knowledge_lib and knowledge_lib.status == GENERATING_CANCELED:
            logger.info("Knowledge lib is generating canceled")
            return

        if parent_node.depth >= self.max_depth:
            logger.debug(f"Stopping recursion at depth {parent_node.depth} for node: {parent_node.id}")
            return

        logger.debug(f"parent_node depth: {parent_node.depth}, prompt_input: {parent_node.id}")
        try:
            # Add timeout for LLM interaction
            ai_response = await asyncio.wait_for(Llm.get_ai_response_async(parent_node.content, self.llm_name), timeout=LLM_TIMEOUT)
        except asyncio.TimeoutError:
            logger.error(f"LLM interaction timed out for node: {parent_node.id}")
            return
        except Exception as e:
            logger.error(f"Failed to get AI response: {e}")
            return

        if not ai_response:
            logger.warning(f"No AI response for node: {parent_node.id}")
            return

        # Start a database transaction
        ai_node = Node.add_info_node(self.lib_id, self.subject_id, ai_response, parent_node.depth + 1)
        logger.debug(f"ai_node depth: {ai_node.depth}")

        Relationship.add_relationship(
            self.lib_id, self.subject_id, parent_node.element_id, ai_node.element_id, RelationshipType.HAS_CHILD
        )

        if ai_node.depth >= self.max_depth:
            logger.debug(f"Stopping recursion at depth {ai_node.depth} for node: {ai_node.id}")
            return

        generated_prompts = await asyncio.wait_for(Llm.generate_prompts_from_text_async(ai_response, self.llm_name), timeout=LLM_TIMEOUT)
        logger.debug(f"generated_prompts: {generated_prompts}")

        if not generated_prompts:
            logger.debug("No prompts generated from AI response.")
            return

        # Batch process prompts asynchronously
        await self._process_prompts_batch(ai_node, generated_prompts)

        # Update progress
        self.progress += 1
        logger.info(f"Progress: {self.progress} nodes processed.")

    async def _process_prompts_batch(self, ai_node: Node, generated_prompts: List[Dict[str, Any]]):
        """
        Processes a batch of prompts generated from the AI response asynchronously.

        Args:
            ai_node (Node): The AI node to which the prompts are linked.
            generated_prompts (List[Dict[str, Any]]): List of generated prompts.
        """
        tasks = []
        for generated_prompt in generated_prompts:
            knowledge_lib = await self._get_knowledge_lib()
            if knowledge_lib and knowledge_lib.status == GENERATING_CANCELED:
                logger.info("Knowledge lib is generating canceled")
                return

            prompt_content = generated_prompt.get("prompt")
            if not prompt_content:
                logger.warning("Skipping empty prompt.")
                continue

            # Create a task for each prompt
            task = self._process_prompt(ai_node, prompt_content)
            tasks.append(task)

        # Run all tasks concurrently
        await asyncio.gather(*tasks)

    async def _process_prompt(self, ai_node: Node, prompt_content: str):
        """
        Processes a single prompt asynchronously.

        Args:
            ai_node (Node): The AI node to which the prompt is linked.
            prompt_content (str): The content of the prompt.
        """
        prompt_node = Node.add_prompt_node(self.lib_id, self.subject_id, prompt_content, ai_node.depth + 1)
        Relationship.add_relationship(
            self.lib_id, self.subject_id, ai_node.element_id, prompt_node.element_id, RelationshipType.HAS_CHILD
        )
        await self.generate_knowledge_graph_recursive(prompt_node)