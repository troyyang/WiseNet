import logging
from transformers import MT5Tokenizer, MT5EncoderModel
from sentence_transformers import SentenceTransformer, SimilarityFunction
import torch
import numpy as np
from typing import List, Dict, Optional, Union
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two embeddings while ensuring they meet the criteria for cosine vector indexes.

    Args:
        embedding1 (np.ndarray): First embedding vector.
        embedding2 (np.ndarray): Second embedding vector.

    Returns:
        float: Cosine similarity between the vectors if they are valid; otherwise, 0.0.
    """
    # Ensure embeddings are 2D
    if embedding1.ndim == 1:
        embedding1 = embedding1.reshape(1, -1)
    if embedding2.ndim == 1:
        embedding2 = embedding2.reshape(1, -1)

    # Calculate the l2-norms
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)

    # Check the conditions for valid cosine vector index
    if np.isfinite(norm1) and np.isfinite(norm2) and norm1 > 0 and norm2 > 0:
        # Normalize the vectors to avoid issues with large or small values
        embedding1_normalized = embedding1 / norm1
        embedding2_normalized = embedding2 / norm2

        # Ensure that the ratios are representable in single precision
        if np.all(np.isfinite(embedding1_normalized.astype(np.float32))) and np.all(
                np.isfinite(embedding2_normalized.astype(np.float32))):
            similarity = np.dot(embedding1_normalized, embedding2_normalized.T).item()
            return similarity

    return 0.0


def split_text_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences using a regex pattern that supports both Chinese and English punctuation.

    Args:
        text (str): Input text.

    Returns:
        List[str]: List of sentences.
    """
    sentence_endings = "\n\n", "\n", ".", "!", "?", ":", "\uff01", "\uff1f", "\uff0e", "\u3002", "\uff1a"
    pattern = r'(?<=[{}])'.format('|'.join(sentence_endings))
    sentences = re.split(pattern, text)
    return [s.strip() for s in sentences if s.strip()]

class EmbeddingModel:
    """Base class for embedding models."""

    def __init__(self, model_name: str, device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self.model: Optional[torch.nn.Module] = None
        self.tokenizer: Optional[Union[torch.nn.Module, MT5Tokenizer]] = None

    def load_model(self):
        """Load the model and tokenizer."""
        raise NotImplementedError("Subclasses should implement this method.")

    def get_embedding(self, text: str, max_tokens_each_chunk: int = 128) -> np.ndarray:
        """Generate embedding for a given text."""
        raise NotImplementedError("Subclasses should implement this method.")

    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate similarity between two embeddings."""
        raise NotImplementedError("Subclasses should implement this method.")

class SBERTModel(EmbeddingModel):
    """Wrapper for SBERT models."""

    def load_model(self):
        if self.model is None:
            try:
                self.model = SentenceTransformer(self.model_name, device=self.device)
                self.model.similarity_fn_name = SimilarityFunction.COSINE
            except Exception as e:
                logger.error(f"Failed to load SBERT model {self.model_name}: {e}")
                raise RuntimeError(f"Failed to load SBERT model {self.model_name}: {e}")

    def get_embedding(self, text: str, max_tokens_each_chunk: int = 128) -> np.ndarray:
        self.load_model()
        sentences = split_text_into_sentences(text)
        all_embeddings = []
        for sentence in sentences:
            try:
                encoding = self.model.tokenizer(
                    sentence, add_special_tokens=True, truncation=True,
                    padding="max_length", max_length=max_tokens_each_chunk,
                    return_tensors='pt'
                )
                input_dict = {
                    'input_ids': encoding['input_ids'].to(self.device),
                    'attention_mask': encoding['attention_mask'].to(self.device)
                }
                with torch.no_grad():
                    embedding = self.model(input_dict)['sentence_embedding']
                all_embeddings.append(embedding.cpu().numpy())
            except Exception as e:
                logger.error(f"Error processing sentence: {sentence}. Error: {e}")
                continue

        if all_embeddings:
            aggregated_embedding = np.mean(all_embeddings, axis=0)
        else:
            aggregated_embedding = np.zeros(self.model.get_sentence_embedding_dimension())
        return aggregated_embedding.flatten()

    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        return self.model.similarity(embedding1, embedding2)

class MLongT5ModelWrapper(EmbeddingModel):
    """Wrapper for mLongT5 models."""

    def load_model(self):
        if self.model is None:
            try:
                self.model = MT5EncoderModel.from_pretrained(self.model_name).to(self.device)
                self.tokenizer = MT5Tokenizer.from_pretrained(self.model_name)
            except Exception as e:
                logger.error(f"Failed to load mLongT5 model {self.model_name}: {e}")
                raise RuntimeError(f"Failed to load mLongT5 model {self.model_name}: {e}")

    def get_embedding(self, text: str, max_tokens_each_chunk: int = 128) -> np.ndarray:
        self.load_model()
        try:
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            inputs = {key: val.to(self.device) for key, val in inputs.items()}
            with torch.no_grad():
                outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1)
            embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
            return embeddings.cpu().numpy().flatten()
        except Exception as e:
            logger.error(f"Error generating embedding for text: {text}. Error: {e}")
            return np.zeros(self.model.config.hidden_size)

    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        return calculate_cosine_similarity(embedding1, embedding2)

class EmbeddingFactory:
    """Factory class to manage embedding models."""

    def __init__(self):
        self.models: Dict[str, EmbeddingModel] = {
            "sbert": SBERTModel("sentence-transformers/paraphrase-multilingual-mpnet-base-v2"),
            "mlongt5": MLongT5ModelWrapper("agemagician/mlong-t5-tglobal-base")
        }

    @classmethod
    def all_embeddings(cls):
        return ["sbert"]

    def get_model(self, model_name: str) -> EmbeddingModel:
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' is not supported. Available models are: {list(self.models.keys())}")
        return self.models[model_name]
        
    def get_embedding(self, text: str, model_name: str = "sbert", max_tokens_each_chunk: int = 128,
                      device: str = "cpu") -> np.ndarray:
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' is not supported. Available models are: {list(self.models.keys())}")

        if not text:
            return np.zeros(self.models[model_name].model.get_sentence_embedding_dimension())

        model = self.models[model_name]
        model.device = device
        return model.get_embedding(text, max_tokens_each_chunk)

    def get_embeddings_for_texts(self, texts: List[str], model_name: str = "sbert", max_tokens_each_chunk: int = 128,
                                 device: str = "cpu") -> np.ndarray:
        embeddings = [self.get_embedding(text, model_name, max_tokens_each_chunk, device) for text in texts]
        return np.vstack(embeddings)


# Example usage
if __name__ == "__main__":
    factory = EmbeddingFactory()

    texts = [
        "This is a test sentence.",
        "这是一个测试句子。",
        "Longformer can handle long documents.",
        "BigBird is designed for long sequences."
    ]

    for model_name in ["sbert", "mlongt5"]:
        try:
            embeddings = factory.get_embeddings_for_texts(texts, model_name, device="cpu")
            similarity = calculate_cosine_similarity(embeddings[0], embeddings[1])
        except Exception as e:
            logger.error(f"Error occurred: {e}")