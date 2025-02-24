import datetime
from typing import Optional, List

from sqlalchemy import select

from core.extends_logger import logger
from core.i18n import _
from graph.graph_generator import KnowledgeGraphGenerator
import core.database as db
from graph.node import Node
from models.models import KnowledgeLib
from schemas.graph import GraphGenerateConditionView
from services.graph_query_service import GraphQueryService


class GraphGenerateService(GraphQueryService):
    def __init__(self):
        super(GraphGenerateService, self).__init__()

    async def generate_graph(
            self,
            lib_id: int,
            subject_id: int,
            llm_name: str = "wizardlm2",
            max_depth: int = 4,
            embedding_model: Optional[str] = None,
    ) -> None:
        """
        Generates a knowledge graph for a given library and subject.

        Args:
            lib_id (int): The ID of the knowledge library.
            subject_id (int): The ID of the knowledge subject.
            llm_name (str): The name of the LLM to use for generation. Defaults to "wizardlm2".
            max_depth (int): The maximum depth of the graph. Defaults to 4.
            embedding_model (Optional[str]): The embedding model to use. Defaults to None.

        Raises:
            ValueError: If the library or subject is not found.
            RuntimeError: If the graph generation fails.
        """
        logger.debug(
            f"Starting generate_graph for lib_id: {lib_id}, subject_id: {subject_id}, "
            f"llm_name: {llm_name}, max_depth: {max_depth}, embedding_model: {embedding_model}"
        )

        # Fetch the knowledge library and subject
        knowledge_lib = await self.find_knowledge_lib_by_id(lib_id)
        knowledge_subject = await self.find_knowledge_lib_subject_by_id(subject_id)

        if not knowledge_lib or not knowledge_subject:
            error_msg = f"Knowledge library (ID: {lib_id}) or subject (ID: {subject_id}) not found."
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Check if the graph is already being generated
        if knowledge_lib.status == 'GENERATING' or knowledge_lib.status == 'ANALYZING':
            logger.warning(f"Graph generation or analysis is already in progress for library ID: {lib_id}.")
            raise RuntimeError(_("Graph generation or analysis is already in progress."))

        if knowledge_lib.status == 'PUBLISHED':
            logger.warning(f"Library is published. Please unpublish the library first.")
            raise RuntimeError(_("Library is published. Please unpublish the library first."))

        try:
            # Update the generation status to 'GENERATING'
            await self.update_knowledge_lib_status(lib_id, 'GENERATING')

            # Delete old graph files
            logger.debug(f"Deleting old graph files for lib_id: {lib_id}, subject_id: {subject_id}.")
            self.delete_graph_node_document_files_by_subject(lib_id, subject_id)
            logger.debug(f"Successfully deleted old graph files for lib_id: {lib_id}, subject_id: {subject_id}.")

            # Generate the knowledge graph
            logger.debug(f"Starting knowledge graph generation for lib_id: {lib_id}, subject_id: {subject_id}.")
            knowledge_graph_generator = KnowledgeGraphGenerator(
                lib_name=knowledge_lib.title,
                title=knowledge_subject.name,
                llm_name=llm_name,
                max_depth=max_depth,
                lib_id=lib_id,
                subject_id=subject_id,
            )
            await knowledge_graph_generator()  # Run the generator asynchronously
            logger.debug(f"Successfully generated knowledge graph for lib_id: {lib_id}, subject_id: {subject_id}.")

            # Update the generation status to 'PENDING'
            await self.update_knowledge_lib_status(lib_id, 'PENDING')

            # TODO: Invoke callback (if applicable)
            # self.invoke_callback(lib_id, subject_id)

        except Exception as e:
            # Rollback the transaction and log the error
            logger.debug(f"Updated generation status to 'PENDING' for library ID: {lib_id}.")

            error_msg = f"Failed to generate graph for lib_id: {lib_id}, subject_id: {subject_id}. Error: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    async def cancel_generate_graph(self, lib_id: int) -> None:
        """
        Cancels the ongoing graph generation for a specific knowledge library.

        Args:
            lib_id (int): The ID of the knowledge library.

        Returns:
            None
        """
        logger.info(f"Starting cancel_generate_graph for lib_id: {lib_id}")
        async with db.get_async_session() as session:
            result = await session.execute(select(KnowledgeLib).filter(KnowledgeLib.id == lib_id))
            knowledge_lib = result.scalar_one_or_none()

            if knowledge_lib and (knowledge_lib.status == 'GENERATING' or knowledge_lib.status == 'ANALYZING'):
                try:
                    knowledge_lib.status = 'PENDING'
                    knowledge_lib.update_time = datetime.datetime.now()
                    await session.commit()
                    await session.refresh(knowledge_lib)
                    print(f"--------Successfully canceled generate or analyze graph for lib_id: {lib_id}")
                    logger.info(f"Successfully canceled generate or analyze graph for lib_id: {lib_id}")
                except Exception as e:
                    await session.rollback()
                    logger.error(f"Failed to cancel generate_graph for lib_id: {lib_id}. Error: {e}")
                    raise RuntimeError(f"Failed to cancel graph generation: {e}") from e
            else:
                logger.warning(f"No active graph generation or analysis found for lib_id: {lib_id}")


    def generate_answer(self, data: GraphGenerateConditionView) -> str:
        """
        Generates an answer for a given node using an LLM.

        Args:
            data (GraphGenerateConditionView): The data for generating the answer.

        Returns:
            str: The generated answer.

        Raises:
            ValueError: If required fields (lib_id, subject_id, node_element_id) are missing.
        """
        logger.info(f"Generating answer for node_element_id: {data.element_id}")
        if data.lib_id is None or data.subject_id is None or data.element_id is None:
            error_msg = "Lib id, subject id, and node element id must be provided."
            logger.error(error_msg)
            raise ValueError(_(error_msg))

        try:
            answer = Node.generate_answer(data.lib_id, data.subject_id, data.element_id, data.llm_name)
            logger.info(f"Successfully generated answer for node_element_id: {data.element_id}")
            return answer
        except Exception as e:
            logger.error(f"Failed to generate answer for node_element_id: {data.element_id}. Error: {e}")
            raise RuntimeError(f"Failed to generate answer: {e}") from e

    def generate_prompts(self, data: GraphGenerateConditionView) -> List[str]:
        """
        Generates prompts for a given node using an LLM.

        Args:
            data (GraphGenerateConditionView): The data for generating the prompts.

        Returns:
            List[str]: A list of generated prompts.

        Raises:
            ValueError: If required fields (lib_id, subject_id, node_element_id) are missing.
        """
        logger.info(f"Generating prompts for node_element_id: {data.element_id}")
        if data.lib_id is None or data.subject_id is None or data.element_id is None:
            error_msg = "Lib id, subject id, and node element id must be provided."
            logger.error(error_msg)
            raise ValueError(_(error_msg))

        try:
            prompts = Node.generate_prompts(data.lib_id, data.subject_id, data.element_id, data.llm_name)
            logger.info(f"Successfully generated prompts for node_element_id: {data.element_id}")
            return prompts
        except Exception as e:
            logger.error(f"Failed to generate prompts for node_element_id: {data.element_id}. Error: {e}")
            raise RuntimeError(f"Failed to generate prompts: {e}") from e

    def generate_questions(self, data: GraphGenerateConditionView) -> List[str]:
        """
        Generates questions for a given node using an LLM.

        Args:
            data (GraphGenerateConditionView): The data for generating the questions.

        Returns:
            List[str]: A list of generated questions.

        Raises:
            ValueError: If required fields (lib_id, subject_id, node_element_id) are missing.
        """
        logger.info(f"Generating questions for node_element_id: {data.element_id}")
        if data.lib_id is None or data.subject_id is None or data.element_id is None:
            error_msg = "Lib id, subject id, and node element id must be provided."
            logger.error(error_msg)
            raise ValueError(_(error_msg))

        try:
            questions = Node.generate_questions(data.lib_id, data.subject_id, data.element_id, data.llm_name)
            logger.info(f"Successfully generated questions for node_element_id: {data.element_id}")
            return questions
        except Exception as e:
            logger.error(f"Failed to generate questions for node_element_id: {data.element_id}. Error: {e}")
            raise RuntimeError(f"Failed to generate questions: {e}") from e