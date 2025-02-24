import json
from typing import List, Dict, Optional, AsyncGenerator, Union

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from langchain_community.llms.tongyi import Tongyi
from langchain_core.messages import BaseMessage
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain_anthropic import ChatAnthropic
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import OllamaLLM

from core.extends_logger import logger
from core.i18n import _
from core import config
from .doubao_llm import DouBao


class Llm:
    @classmethod
    def all_llms(cls) -> List[str]:
        """Returns a list of all supported LLM names."""
        return ["wizardlm2", "llama3.1", 
                "gpt-4o", "gpt-4-turbo", "gpt-4", 
                "claude3.5-sonnet", "claude3.5-haiku", "claude3.5-opus",
                "deepseek", 
                "qwen-plus", "qwen-max", 
                "Doubao-1.5-pro-32k", "Doubao-1.5-pro-256k", "Doubao-1.5-lite-32k", "Doubao-pro-32k"]

    @classmethod
    def get_model_info(cls, llm_name: str) -> str:
        """Returns a description of the specified LLM."""
        model_info = {
            "wizardlm2": "A powerful open-source LLM based on LLaMA.",
            "llama3.1": "Meta's LLaMA 3 model.",
            "gpt-4o": "OpenAI's GPT-4o model.",
            "gpt-4-turbo": "OpenAI's GPT-4 Turbo model.",
            "gpt-4": "OpenAI's GPT-4 model.",
            "claude3.5-sonnet": "Anthropic's Claude 3.5 model.",
            "claude3.5-haiku": "Anthropic's Claude 3.5 Haiku",
            "claude3.5-opus": "Anthropic's Claude 3.5 Opus",
            "deepseek": "DeepSeek's LLM.",
            "qwen-plus": "Aliyun's Qwen series model.",
            "qwen-max": "Aliyun's Qwen Max model.",
            "Doubao-1.5-pro-32k": "ByteDance's DouBao model.",
            "Doubao-1.5-pro-256k": "ByteDance's DouBao model.",
            "Doubao-1.5-lite-32k": "ByteDance's DouBao model.",
            "Doubao-pro-32k": "ByteDance's DouBao model.",
        }
        return model_info.get(llm_name, "Unknown model.")

    @classmethod
    def retrieve_llm_by_name(cls, llm_name: str, **kwargs) -> Optional[object]:
        """Retrieves an LLM instance by name with optional parameters."""
        if llm_name not in cls.all_llms():
            logger.warning(f"Model {llm_name} not found. Defaulting to {cls.all_llms()[0]}.")
            llm_name = cls.all_llms()[0]

        default_params = {
            "top_p": 0.5,
            "temperature": 0.7,
            "n": 1,
        }
        params = {**default_params, **kwargs}

        try:
            if llm_name == "gpt-4o":
                return OpenAI(model="gpt-4o", api_key=config.OPENAI_API_KEY, request_timeout=60, **params)
            elif llm_name == "gpt-4-turbo":
                return OpenAI(model="gpt-4-turbo", api_key=config.OPENAI_API_KEY, request_timeout=60, **params)
            elif llm_name == "gpt-4":
                return OpenAI(model="gpt-4", api_key=config.OPENAI_API_KEY, request_timeout=60, **params)
            elif llm_name == "claude3.5-sonnet":
                return ChatAnthropic(model="claude-3-5-sonnet-latest", api_key=config.ANTHROPIC_API_KEY, default_request_timeout=60, **params)
            elif llm_name == "claude3.5-haiku":
                return ChatAnthropic(model="claude-3-5-haiku-latest", api_key=config.ANTHROPIC_API_KEY, default_request_timeout=60, **params)
            elif llm_name == "claude3-opus":
                return ChatAnthropic(model="claude-3-opus-latest", api_key=config.ANTHROPIC_API_KEY, default_request_timeout=60, **params)
            elif llm_name == "deepseek":
                return ChatDeepSeek(
                            model='deepseek-chat', 
                            openai_api_key=config.DEEPSEEK_API_KEY, 
                            request_timeout=60,
                            **params
                        )
            elif llm_name == "qwen-plus":
                return Tongyi(model="qwen-plus", api_key=config.DASHSCOPE_API_KEY, **params)
            elif llm_name == "qwen-max":
                return Tongyi(model="qwen-max", api_key=config.DASHSCOPE_API_KEY, **params)
            elif llm_name == "Doubao-1.5-pro-32k":
                return DouBao(model=config.DOUBAO_1_5_PRO_32K_MODEL, **params)
            elif llm_name == "Doubao-1.5-pro-256k":
                return DouBao(model=config.DOUBAO_1_5_PRO_256K_MODEL, **params)
            elif llm_name == "Doubao-1.5-lite-32k":
                return DouBao(model=config.DOUBAO_1_5_LITE_32K_MODEL, **params)
            elif llm_name == "Doubao-pro-32k":
                return DouBao(model=config.DOUBAO_PRO_32K_MODEL, **params)
            else:
                return OllamaLLM(base_url=config.OLLAMA_ENDPOINT, model=llm_name, num_predict=8192, **params)
        except Exception as e:
            logger.error(f"Failed to load model {llm_name}: {e}")
            return None

    @classmethod
    def parse_json_data(cls, ai_message: str | BaseMessage) -> str:
        """Extracts JSON data from the AI response."""
        try:
            if isinstance(ai_message, BaseMessage):
                ai_message = ai_message.content
            if ai_message and ai_message.find("result\":") > 0 and ai_message.rfind("}") > 0:
                json_str = ai_message.split("result\":")[1]
                json_str = json_str[:json_str.rfind("}")]
                return json_str
        except Exception as e:
            logger.error(f"Error parsing JSON data: {e}")
        return ""

    @classmethod
    def get_ai_response(cls, user_message: str, llm_name: str) -> str:
        """Gets a response from the specified LLM."""
        if not user_message:
            return ""

        try:
            llm = cls.retrieve_llm_by_name(llm_name)
            if not llm:
                return ""

            prompt = PromptTemplate.from_template("{input}")
            llm_chain = prompt | llm
            ai_message = llm_chain.invoke({"input": user_message.strip()})
            if isinstance(ai_message, BaseMessage):
                return ai_message.content
            return ai_message
        except Exception as e:
            logger.error(f"Failed to get AI response: {e}")
            return ""

    @classmethod
    async def get_ai_response_async(cls, user_message: str, llm_name: str) -> str:
        """Gets a response from the specified LLM asynchronously."""
        if not user_message:
            return ""

        try:
            llm = cls.retrieve_llm_by_name(llm_name)
            if not llm:
                return ""

            prompt = PromptTemplate.from_template("{input}")
            llm_chain = prompt | llm
            ai_message = await llm_chain.ainvoke({"input": user_message.strip()})
            if isinstance(ai_message, BaseMessage):
                return ai_message.content
            return ai_message
        except Exception as e:
            logger.error(f"Failed to get AI response asynchronously: {e}")
            return ""

    @classmethod
    def get_ai_json_response(cls, user_message: str, llm_name: str) -> Optional[Dict]:
        """Gets a JSON response from the specified LLM."""
        if not user_message:
            return None

        try:
            llm = cls.retrieve_llm_by_name(llm_name)
            if not llm:
                return None

            prompt = PromptTemplate.from_template("{input}")
            llm_chain = prompt | llm | cls.parse_json_data
            ai_response = llm_chain.invoke({"input": user_message.strip()})
            return json.loads(ai_response) if ai_response else None
        except Exception as e:
            logger.error(f"Failed to get AI JSON response: {e}")
            return None

    @classmethod
    def generate_prompts_from_text(cls, text: str, llm_name: str) -> Optional[List]:
        """Generates prompts from the given text."""
        if not text:
            return []

        try:
            llm = cls.retrieve_llm_by_name(llm_name)
            if not llm:
                return []

            prompt = ChatPromptTemplate.from_messages([
                ("system", _("System prompt for generate_prompts_from_text")),
                ("user", _("User prompt for generate_prompts_from_text")),
            ])
            llm_chain = prompt | llm | cls.parse_json_data
            prompts = llm_chain.invoke({"input": text, "count": 3})
            return json.loads(prompts) if prompts else []
        except Exception as e:
            logger.error(f"Failed to generate prompts: {e}")
            return []

    @classmethod
    async def generate_prompts_from_text_async(cls, text: str, llm_name: str) -> Optional[List]:
        if not text:
            return []

        try:
            llm = cls.retrieve_llm_by_name(llm_name)
            if not llm:
                return []

            prompt = ChatPromptTemplate.from_messages([
                ("system", _("System prompt for generate_prompts_from_text")),
                ("user", _("User prompt for generate_prompts_from_text")),
            ])
            llm_chain = prompt | llm | cls.parse_json_data
            prompts = await llm_chain.ainvoke({"input": text, "count": 3})
            return json.loads(prompts) if prompts else []
        except Exception as e:
            logger.error(f"Failed to generate prompts: {e}")
            return []

    @classmethod
    def generate_questions_from_text(cls, text: str, llm_name: str) -> Optional[List]:
        """Generates questions from the given text."""
        if not text:
            return []

        try:
            llm = cls.retrieve_llm_by_name(llm_name)
            if not llm:
                return []

            prompt = ChatPromptTemplate.from_messages([
                ("system", _("System prompt for generate question")),
                ("user", _("User prompt for generate question")),
            ])
            llm_chain = prompt | llm | cls.parse_json_data
            questions = llm_chain.invoke({"input": text, "count": 3})
            return json.loads(questions) if questions else []
        except Exception as e:
            logger.error(f"Failed to generate questions: {e}")
            return []

    @classmethod
    async def generate_questions_from_text_async(cls, text: str, llm_name: str) -> Optional[List]:
        """Generates questions from the given text."""
        if not text:
            return []

        try:
            llm = cls.retrieve_llm_by_name(llm_name)
            if not llm:
                return []

            prompt = ChatPromptTemplate.from_messages([
                ("system", _("System prompt for generate question")),
                ("user", _("User prompt for generate question")),
            ])
            llm_chain = prompt | llm | cls.parse_json_data
            questions = await llm_chain.invoke({"input": text, "count": 3})
            return json.loads(questions) if questions else []
        except Exception as e:
            logger.error(f"Failed to generate questions: {e}")
            return []

    @classmethod
    def summarize_documents(cls, documents: List, llm_name: str) -> Optional[Dict]:
        """Summarizes a list of documents using the specified LLM."""
        try:
            llm = cls.retrieve_llm_by_name(llm_name)
            if not llm:
                return None

            prompt = ChatPromptTemplate.from_template(_("System prompt for summarize documents"))
            llm_chain = create_stuff_documents_chain(llm, prompt)
            final_chain = llm_chain | cls.parse_json_data
            result = final_chain.invoke({"context": documents})
            return json.loads(result) if result else None
        except Exception as e:
            logger.exception(f"Error summarizing documents: {e}")
            return None

    @classmethod
    async def summarize_documents_async(cls, documents: List, llm_name: str) -> Optional[Dict]:
        """Summarizes a list of documents using the specified LLM."""
        try:
            llm = cls.retrieve_llm_by_name(llm_name)
            if not llm:
                return None

            prompt = ChatPromptTemplate.from_template(_("System prompt for summarize documents"))
            llm_chain = create_stuff_documents_chain(llm, prompt)
            final_chain = llm_chain | cls.parse_json_data
            result = await final_chain.ainvoke({"context": documents})
            return json.loads(result) if result else None
        except Exception as e:
            logger.exception(f"Error summarizing documents: {e}")
            return None

    @classmethod
    def summary_message_history(cls, messages, llm_name: str, chain_type: str = "stuff") -> Optional[str]:
        """Processes a list of messages asynchronously using the specified LLM."""
        try:
            if not messages:
                return None

            llm = cls.retrieve_llm_by_name(llm_name)
            if not llm:
                return None

            documents = []
            for msg in messages:
                if msg is None:
                    continue
                
                if isinstance(msg, str):
                    documents.append(Document(page_content=msg))
                elif isinstance(msg, BaseMessage) or 'content' in msg:
                    content = msg.get('content', '')
                    documents.append(Document(page_content=content))

            # Extract key information
            chain = load_summarize_chain(llm, chain_type=chain_type)
            ai_summary = chain.invoke(documents)
            if isinstance(ai_summary, dict):
                return ai_summary
            if isinstance(ai_summary, BaseMessage):
                ai_summary = ai_summary.content
            
            return json.loads(ai_summary) if ai_summary else None
        except Exception as e:
            logger.exception(f"Error processing message history: {e}")
            return None
    
    
    @classmethod
    async def summary_message_history_streaming(
        cls, messages: List[Union[str, BaseMessage, dict]], llm_name: str, chain_type: str = "stuff"
    ) -> AsyncGenerator[str, None]:
        """
        Processes a list of messages asynchronously using the specified LLM and streams the summary.

        Args:
            messages (List[Union[str, BaseMessage, dict]]): The messages to summarize.
            llm_name (str): The name of the LLM to use.
            chain_type (str): The type of summarization chain to use (default: "stuff").

        Yields:
            str: Chunks of the summarized text as they are generated.

        Raises:
            Exception: If an error occurs during summarization.
        """
        try:
            if not messages:
                logger.warning("No messages provided for summarization.")
                return

            # Retrieve the LLM instance
            llm = cls.retrieve_llm_by_name(llm_name)
            if not llm:
                logger.error(f"LLM with name '{llm_name}' not found.")
                return

            # Prepare documents for summarization
            documents = []
            for msg in messages:
                if msg is None:
                    continue

                if isinstance(msg, str):
                    documents.append(Document(page_content=msg))
                elif isinstance(msg, BaseMessage) or isinstance(msg, dict) and 'content' in msg:
                    content = msg.get('content', '') if isinstance(msg, dict) else msg.content
                    documents.append(Document(page_content=content))

            if not documents:
                logger.warning("No valid documents found for summarization.")
                return

            # Load the summarization chain
            chain = load_summarize_chain(llm, chain_type=chain_type)

            # Stream the summarization process
            async for chunk in chain.astream(documents):
                if isinstance(chunk, BaseMessage):
                    chunk = chunk.content
                yield chunk  # Yield intermediate results

        except Exception as e:
            logger.exception(f"Error processing message history: {e}")
            raise RuntimeError(f"Failed to summarize messages: {e}") from e

    @classmethod
    def get_prompt_template(cls, template_name: str) -> str:
        """Retrieves a prompt template by name."""
        templates = {
            "content": _("Content prompt template"),
            "analysis_title": _("Analysis title prompt template"),
            "analysis_keywords": _("Analysis keywords prompt template"),
            "analysis_tags": _("Analysis tags prompt template")
        }
        return templates.get(template_name, "")


if __name__ == '__main__':
    import sys
    llm_name = sys.argv[1] if len(sys.argv) > 1 else 'wizardlm2'
    llm_instance = Llm.retrieve_llm_by_name(llm_name)
    print(f'Retrieved LLM: {type(llm_instance).__name__}')