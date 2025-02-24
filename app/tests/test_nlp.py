import unittest
from ai.nlp import extract_entities
from ai.embedding import EmbeddingFactory, calculate_cosine_similarity
from typing import List
import numpy as np

class TestNLP(unittest.TestCase):
    def setUp(self):
        self.embedding_factory = EmbeddingFactory()

    def test_extract_entities_en(self):
        text = "Barack Obama visited San Francisco last Thursday to attend a conference on artificial intelligence at Stanford University."
        enities = extract_entities(text)
        assert enities == ['Barack Obama', 'San Francisco', 'Stanford University']

        entities_embedding = self.embedding_factory.get_embeddings_for_texts(texts=enities, model_name="sbert")
        assert entities_embedding.shape == (3, 768)
        test_embedding = self.embedding_factory.get_embedding(text="Obama")
        assert test_embedding.shape == (768,)
        call = self.embedding_factory.get_model("sbert").similarity(entities_embedding[0], test_embedding)
        assert call > 0.8
        test_embedding = self.embedding_factory.get_embedding(text="Bill Clinton")
        assert test_embedding.shape == (768,)
        call = self.embedding_factory.get_model("sbert").similarity(entities_embedding[0], test_embedding)
        assert call > 0.4
        test_embedding = self.embedding_factory.get_embedding(text="Trump")
        assert test_embedding.shape == (768,)
        call = self.embedding_factory.get_model("sbert").similarity(entities_embedding[0], test_embedding)
        assert call > 0.3
        test_embedding = self.embedding_factory.get_embedding(text="Tom Cruise")
        assert test_embedding.shape == (768,)
        call = self.embedding_factory.get_model("sbert").similarity(entities_embedding[0], test_embedding)
        assert call < 0.5

    def test_extract_entities_zh(self):
        text = "巴拉克·奥巴马于上周四访问了旧金山，参加在斯坦福大学举行的人工智能会议。"
        enities = extract_entities(text)
        assert enities == ['巴拉克·奥巴马', '旧金山', '斯坦福大学']
        entities_embedding = self.embedding_factory.get_embeddings_for_texts(texts=enities, model_name="sbert")
        assert entities_embedding.shape == (3, 768)
        test_embedding = self.embedding_factory.get_embedding(text="奥巴马")
        assert test_embedding.shape == (768,)
        call = self.embedding_factory.get_model("sbert").similarity(entities_embedding[0], test_embedding)
        assert call > 0.8
        test_embedding = self.embedding_factory.get_embedding(text="克林顿")
        assert test_embedding.shape == (768,)
        call = self.embedding_factory.get_model("sbert").similarity(entities_embedding[0], test_embedding)
        assert call > 0.6
        test_embedding = self.embedding_factory.get_embedding(text="特朗普")
        assert test_embedding.shape == (768,)
        call = self.embedding_factory.get_model("sbert").similarity(entities_embedding[0], test_embedding)
        assert call > 0.4
        test_embedding = self.embedding_factory.get_embedding(text="汤姆·克鲁斯")
        assert test_embedding.shape == (768,)
        call = self.embedding_factory.get_model("sbert").similarity(entities_embedding[0], test_embedding)
        assert call < 0.5

if __name__ == '__main__':
    unittest.main()

