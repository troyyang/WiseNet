import json
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders.excel import UnstructuredExcelLoader
from langchain_community.document_loaders.html import UnstructuredHTMLLoader
from langchain_community.document_loaders.markdown import UnstructuredMarkdownLoader
from langchain_community.document_loaders.powerpoint import UnstructuredPowerPointLoader
from langchain_community.document_loaders.text import TextLoader
from langchain_community.document_loaders.web_base import WebBaseLoader
from langchain_community.document_loaders.word_document import UnstructuredWordDocumentLoader
from langchain_community.document_loaders.xml import UnstructuredXMLLoader
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import RecursiveJsonSplitter
from pydantic import FilePath

import core.config as config
from graph.graph_query import KnowledgeGraphQuery
from.embedding import EmbeddingFactory
from.llm import Llm


# HTMLSemanticPreservingSplitter class with added comments
class HTMLSemanticPreservingSplitter:
    """
    A class to split HTML content while preserving its semantic structure.
    It splits the HTML content into chunks based on a specified maximum chunk size
    and chunk overlap.
    """
    def __init__(self, max_chunk_size: int = 500, chunk_overlap: int = 50):
        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, html_content: str) -> List[str]:
        """
        Split the given HTML content into chunks.

        Args:
            html_content (str): The HTML content to be split.

        Returns:
            List[str]: A list of split HTML chunks.
        """
        soup = BeautifulSoup(html_content, 'lxml')
        chunks = []
        current_chunk = []
        current_size = 0

        for element in soup.recursiveChildGenerator():
            element_str = str(element)
            element_size = len(element_str)

            if current_size + element_size > self.max_chunk_size and current_chunk:
                chunks.append(''.join(current_chunk))
                current_chunk = current_chunk[-self.chunk_overlap:]
                current_size = sum(len(item) for item in current_chunk)

            current_chunk.append(element_str)
            current_size += element_size

        if current_chunk:
            chunks.append(''.join(current_chunk))

        return chunks

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split a list of documents containing HTML content.

        Args:
            documents (List[Document]): A list of documents with HTML page content.

        Returns:
            List[Document]: A list of split documents.
        """
        split_docs = []
        for doc in documents:
            html_content = doc.page_content
            chunks = self.split_text(html_content)
            for chunk in chunks:
                new_doc = Document(
                    page_content=chunk,
                    metadata=doc.metadata
                )
                split_docs.append(new_doc)
        return split_docs


class DocumentService:
    """
    A service class for handling document - related operations such as loading, splitting,
    and analyzing documents.
    """
    # Class - level constants for chunk size and overlap
    DEFAULT_CHUNK_SIZE = 500
    DEFAULT_CHUNK_OVERLAP = 50

    def __init__(self):
        self.knowledge_graph_query = KnowledgeGraphQuery()
        self.embedding_factory = EmbeddingFactory()
        self.llm = Llm()

        self.file_type_mapping = {
            'md': UnstructuredMarkdownLoader,
            'pdf': PyPDFLoader,
            'docx': UnstructuredWordDocumentLoader,
            'doc': UnstructuredWordDocumentLoader,
            'xlsx': UnstructuredExcelLoader,
            'xls': UnstructuredExcelLoader,
            'pptx': UnstructuredPowerPointLoader,
            'ppt': UnstructuredPowerPointLoader,
            'csv': CSVLoader,
            'html': UnstructuredHTMLLoader,
            'xml': UnstructuredXMLLoader,
            'txt': TextLoader,
            'json': TextLoader
        }

    def get_file_extension(self, filename: str) -> str:
        """
        Get the file extension of the given file name.

        Args:
            filename (str): The name of the file.

        Returns:
            str: The file extension in lowercase without the leading dot.
        """
        return Path(filename).suffix.lower()[1:]

    def is_file_type(self, filename: str, extensions: List[str]) -> bool:
        """
        Check if the file has one of the specified extensions.

        Args:
            filename (str): The name of the file.
            extensions (List[str]): A list of file extensions to check against.

        Returns:
            bool: True if the file has one of the specified extensions, False otherwise.
        """
        return self.get_file_extension(filename) in extensions

    def load_documents(self, file_path: FilePath | str) -> List[Document]:
        """
        Load documents from the given file path.

        Args:
            file_path (FilePath | str): The path to the file.

        Returns:
            List[Document]: A list of loaded documents.

        Raises:
            ValueError: If the file type is not supported.
        """
        file_extension = self.get_file_extension(file_path)
        loader_class = self.file_type_mapping.get(file_extension)
        if loader_class:
            loader = loader_class(file_path)
            return loader.load()
        supported_types = ', '.join(self.file_type_mapping.keys())
        raise ValueError(f"Unsupported file type: {file_extension}. Supported types are: {supported_types}")

    def split_markdown_document(self, markdown_path: str) -> List[Document]:
        """
        Split a markdown document into smaller documents.

        Args:
            markdown_path (str): The path to the markdown document.

        Returns:
            List[Document]: A list of split markdown documents.
        """
        headers_to_split_on = [
            ("#", "source"),
            ("##", "title"),
            ("###", "subtitle"),
        ]
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on, strip_headers=False)
        with open(markdown_path, 'r') as f:
            markdown_string = f.read()
        md_header_splits = markdown_splitter.split_text(markdown_string)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.DEFAULT_CHUNK_SIZE,
                                                      chunk_overlap=self.DEFAULT_CHUNK_OVERLAP)
        return text_splitter.split_documents(md_header_splits)

    def split_common_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split a list of common documents (using a set of default separators).

        Args:
            documents (List[Document]): A list of documents to split.

        Returns:
            List[Document]: A list of split documents.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            separators=[
                "\n\n", "\n", " ", ".", ",", "\u200b", "\uff0c", "\u3001", "\uff0e", "\u3002", ""
            ],
            chunk_size=self.DEFAULT_CHUNK_SIZE,
            chunk_overlap=self.DEFAULT_CHUNK_OVERLAP
        )
        return text_splitter.split_documents(documents)

    def split_csv_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split a list of CSV documents.

        Args:
            documents (List[Document]): A list of CSV documents to split.

        Returns:
            List[Document]: A list of split CSV documents.
        """
        text_splitter = CharacterTextSplitter(chunk_size=10, chunk_overlap=10)
        return text_splitter.split_documents(documents)

    def split_html_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split a list of HTML documents.

        Args:
            documents (List[Document]): A list of HTML documents to split.

        Returns:
            List[Document]: A list of split HTML documents.
        """
        splitter = HTMLSemanticPreservingSplitter(max_chunk_size=5, chunk_overlap=0)
        return splitter.split_documents(documents)

    def split_json_document(self, file_path: str) -> List[Document]:
        """
        Split a JSON document into smaller documents.

        Args:
            file_path (str): The path to the JSON document.

        Returns:
            List[Document]: A list of split JSON documents.
        """
        splitter = RecursiveJsonSplitter(max_chunk_size=500)
        with open(file_path, 'r') as file:
            json_data = json.load(file)
        if isinstance(json_data, dict):
            json_data = [json_data]
        return splitter.create_documents(texts=json_data)

    def split_documents(self, file_path: str, docs: List[Document], embedding_model: str) -> List[Document]:
        """
        Split documents based on their file type.

        Args:
            file_path (str): The path to the file.
            docs (List[Document]): A list of loaded documents.
            embedding_model (str): The embedding model to use.

        Returns:
            List[Document]: A list of split documents.
        """
        file_extension = self.get_file_extension(file_path)
        if file_extension =='md':
            return self.split_markdown_document(file_path)
        elif file_extension == 'csv':
            return self.split_csv_documents(docs)
        elif file_extension == 'html':
            return self.split_common_documents(docs)
        elif file_extension == 'json':
            return self.split_json_document(file_path)
        else:
            return self.split_common_documents(docs)

    def analysis_url(self, url: str, llm_name: str = config.DEFAULT_LLM_NAME) -> tuple:
        """
        Analyze the content of a given URL.

        Args:
            url (str): The URL to analyze.
            llm_name (str): The name of the LLM to use for summarization.

        Returns:
            tuple: A tuple containing the summary and the split documents.
        """
        loader = WebBaseLoader(url)
        docs = loader.load()
        summary = self.llm.summarize_documents(documents=docs, llm_name=llm_name)
        splits = self.split_common_documents(docs)

        return summary, splits

    def analysis_file(self, file_path: FilePath | str, llm_name: str = config.DEFAULT_LLM_NAME,
                      embedding_model: str = "sbert") -> tuple:
        """
        Analyze the content of a given file.

        Args:
            file_path (FilePath | str): The path to the file.
            llm_name (str): The name of the LLM to use for summarization.
            embedding_model (str): The embedding model to use.

        Returns:
            tuple: A tuple containing the summary and the split documents.
        """
        if not file_path:
            return None, None

        documents = self.load_documents(file_path)
        summary = self.llm.summarize_documents(documents=documents, llm_name=llm_name)
        splits = self.split_documents(file_path, documents, embedding_model)
        return summary, splits
