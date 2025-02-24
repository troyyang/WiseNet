import unittest
from ai.embedding import EmbeddingFactory, calculate_cosine_similarity
import numpy as np


class TestEmbedding(unittest.TestCase):
    def setUp(self):
        self.embedding_factory = EmbeddingFactory()

    def test_embedding_single_text_en_by_sbert(self):
        """Test SBERT embedding for English text."""
        text = "Barack Obama visited San Francisco last Thursday to attend a conference on artificial intelligence at Stanford University."
        embedding = self.embedding_factory.get_embedding(text=text, model_name="sbert")
        self.assertEqual(embedding.shape, (768,))  # SBERT embedding dimension is 768

        # Test similar text
        test_text = "Obama visited San Francisco last Thursday to attend a conference."
        test_embedding = self.embedding_factory.get_embedding(text=test_text, model_name="sbert")
        similarity = self.embedding_factory.get_model("sbert").similarity(embedding, test_embedding)
        self.assertGreater(similarity, 0.8)  # Similar text should have high similarity

        # Test dissimilar text
        test_text = "This is a lie."
        test_embedding = self.embedding_factory.get_embedding(text=test_text, model_name="sbert")
        similarity = self.embedding_factory.get_model("sbert").similarity(embedding, test_embedding)
        self.assertLess(similarity, 0.1)  # Dissimilar text should have low similarity

    def test_embedding_single_text_zh_by_sbert(self):
        """Test SBERT embedding for Chinese text."""
        text = "巴拉克·奥巴马上周四访问了旧金山，参加在斯坦福大学举行的人工智能会议。"
        embedding = self.embedding_factory.get_embedding(text=text, model_name="sbert")
        self.assertEqual(embedding.shape, (768,))  # SBERT embedding dimension is 768

        # Test similar text
        test_text = "巴拉克·奥巴马上周四访问了旧金山，参加在斯坦福大学举行的人工智能会议。"
        test_embedding = self.embedding_factory.get_embedding(text=test_text, model_name="sbert")
        similarity = self.embedding_factory.get_model("sbert").similarity(embedding, test_embedding)
        self.assertGreater(similarity, 0.8)  # Similar text should have high similarity

        # Test dissimilar text
        test_text = "这是一个谎言。"
        test_embedding = self.embedding_factory.get_embedding(text=test_text, model_name="sbert")
        similarity = self.embedding_factory.get_model("sbert").similarity(embedding, test_embedding)
        self.assertLess(similarity, 0.1)  # Dissimilar text should have low similarity

    def test_embedding_single_text_en_by_mlongt5(self):
        """Test MLongT5 embedding for English text."""
        text = "Barack Obama visited San Francisco last Thursday to attend a conference on artificial intelligence at Stanford University."
        embedding = self.embedding_factory.get_embedding(text=text, model_name="mlongt5")
        self.assertEqual(embedding.shape, (768,))  # MLongT5 embedding dimension is 768

        # Test similar text
        test_text = "Obama visited San Francisco last Thursday to attend a conference."
        test_embedding = self.embedding_factory.get_embedding(text=test_text, model_name="mlongt5")
        similarity = self.embedding_factory.get_model("mlongt5").similarity(embedding, test_embedding)
        self.assertGreater(similarity, 0.8)  # Similar text should have high similarity

        # Test dissimilar text
        test_text = "This is a lie."
        test_embedding = self.embedding_factory.get_embedding(text=test_text, model_name="mlongt5")
        similarity = self.embedding_factory.get_model("mlongt5").similarity(embedding, test_embedding)
        self.assertLess(similarity, 0.8)  # Dissimilar text should have low similarity

    def test_embedding_multi_text_en_by_sbert(self):
        """Test SBERT embedding for multiple English texts."""
        texts = [
            "Barack Obama visited San Francisco last Thursday to attend a conference on artificial intelligence at Stanford University.",
            "This is a test sentence.",
            "This is another test sentence.",
            "This is a third test sentence.",
            "This is a fourth test sentence.",
            "This is a fifth test sentence.",
            "This is a sixth test sentence.",
            "This is a seventh test sentence.",
            "This is an eighth test sentence.",
            "This is a ninth test sentence.",
            "This is a tenth test sentence.",
            "This is an eleventh test sentence.",
        ]
        embeddings_matrix = self.embedding_factory.get_embeddings_for_texts(texts=texts, model_name="sbert")
        self.assertEqual(embeddings_matrix.shape, (12, 768))  # SBERT embedding dimension is 768

        # Test similarity with the first text
        test_embedding1 = self.embedding_factory.get_embedding(
            text="Barack Obama visited San Francisco last Thursday to attend a conference on artificial intelligence at Stanford University.",
            model_name="sbert")
        similarity1 = self.embedding_factory.get_model("sbert").similarity(embeddings_matrix[0], test_embedding1)
        self.assertGreater(similarity1, 0.8)  # Similar text should have high similarity

        # Test dissimilarity with a random text
        test_embedding2 = self.embedding_factory.get_embedding(text="This is a lie.", model_name="sbert")
        similarity2 = self.embedding_factory.get_model("sbert").similarity(embeddings_matrix[1], test_embedding2)
        self.assertLess(similarity2, 0.40)  # Dissimilar text should have low similarity

    def test_embedding_multi_text_zh_by_sbert(self):
        """Test SBERT embedding for multiple Chinese texts."""
        texts = [
            "巴拉克·奥巴马上周四访问了旧金山，参加在斯坦福大学举行的人工智能会议。",
            "这是一个测试句子。",
            "这是另一个测试句子。",
            "这是第三个测试句子。",
            "这是第四个测试句子。",
            "这是第五个测试句子。",
            "这是第六个测试句子。",
            "这是第七个测试句子。",
            "这是第八个测试句子。",
            "这是第九个测试句子。",
            "这是第十个测试句子。",
            "这是第十一个测试句子。",
        ]
        embeddings_matrix = self.embedding_factory.get_embeddings_for_texts(texts=texts, model_name="sbert")
        self.assertEqual(embeddings_matrix.shape, (12, 768))  # SBERT embedding dimension is 768

        # Test similarity with the first text
        test_embedding1 = self.embedding_factory.get_embedding(
            text="巴拉克·奥巴马上周四访问了旧金山，参加在斯坦福大学举行的人工智能会议。", model_name="sbert")
        similarity1 = self.embedding_factory.get_model("sbert").similarity(embeddings_matrix[0], test_embedding1)
        self.assertGreater(similarity1, 0.8)  # Similar text should have high similarity

        # Test dissimilarity with a random text
        test_embedding2 = self.embedding_factory.get_embedding(text="这是一个谎言。", model_name="sbert")
        similarity2 = self.embedding_factory.get_model("sbert").similarity(embeddings_matrix[1], test_embedding2)
        self.assertLess(similarity2, 0.40)  # Dissimilar text should have low similarity

    def test_embedding_long_text_en_by_sbert(self):
        """Test SBERT embedding for long English text."""
        # Generate a long English text
        with open("tests/data/13_query_test_data_simple_weight_loss_diet.txt", "r") as f:
            long_text = f.read()
        embedding = self.embedding_factory.get_embedding(text=long_text, model_name="sbert")
        self.assertEqual(embedding.shape, (768,))  # SBERT embedding dimension is 768
        # use numpy.loadtxt to read the file, specify the separator as a comma
        assert_embedding_array = np.loadtxt('tests/data/14_query_test_data_simple_weight_loss_diet_vector.txt', delimiter=',')
        # print(assert_embedding_array.shape)
        # print(embedding.shape)
        # self.assertEqual(embedding.tolist(), assert_embedding_array.tolist())  # Test embedding

        # Test similarity with a shorter version of the text
        test_text = " **Choose healthy fats Such as fish oil, olive o"
        test_embedding = self.embedding_factory.get_embedding(text=test_text, model_name="sbert")
        similarity = self.embedding_factory.get_model("sbert").similarity(embedding, test_embedding)
        self.assertGreater(similarity, 0.7)  # Similar text should have moderate to high similarity


        test_text = "Breakfast, Lunch, Dinner, and Evening Snack"
        test_embedding = self.embedding_factory.get_embedding(text=test_text, model_name="sbert")
        similarity = calculate_cosine_similarity(embedding, test_embedding)
        self.assertGreater(similarity, 0.6) 

        test_text = "Barack Obama visited San Francisco last Thursday to attend a conference on artificial intelligence at Stanford University."
        test_embedding = self.embedding_factory.get_embedding(text=test_text, model_name="sbert")
        similarity = calculate_cosine_similarity(embedding, test_embedding)
        self.assertLessEqual(similarity, 0.1)  

        test_text = """
         8. **Temperature monitoring equipment**: The temperature monitoring equipment should be cal
            ibrated and qualified, and the measured temperature parameters should meet
             the following requirements: the measurement range should not be less than 
             -30°C to 30°C and include the temperature range required for transporting goods;
              the accuracy should not be greater than ±0.5°C; the display resolution should not be greater than 0.1°C.
        """
        test_embedding = self.embedding_factory.get_embedding(text=test_text, model_name="sbert")
        similarity = self.embedding_factory.get_model("sbert").similarity(embedding, test_embedding)
        self.assertLessEqual(similarity, 0.45)  

    def test_embedding_long_text_zh_by_sbert(self):
        """Test SBERT embedding for long Chinese text."""
        # Generate a long Chinese text
        long_text = """减肥饮食应遵循均衡、营养、低热量饮食的原则。
                        以下是一个简单的减肥食谱示例，
                        包括一天的膳食计划：
                        ### 早餐
                        - 燕麦片或全麦面包搭配新鲜水果（如苹果或梨）
                        - 一份低脂酸奶或果味酸奶
                        - 一小杯低脂牛奶或豆奶
                        - 一份低脂奶酪（如卡路里奶酪）
                        ### 上午茶点
                        - 一份新鲜水果（如橙子或香蕉）
                        - 一小把核桃或亚麻籽
                        ### 午餐
                        - 烤鸡胸肉或烤鱼（约150-200克，根据个人饮食需求调整）
                        - 大量蒸或生吃的蔬菜（如西兰花、胡萝卜、菠菜等）
                        - 一小份糙米或全麦面包
                        - 一把新鲜沙拉（可用柠檬汁或淡油调味）
                        ### 下午点心
                        - 一份低脂酸奶或果味酸奶
                        - 几片乳清或苹果片
                        ### 晚餐
                        - 烤鱼或豆类（如黑豆、黄豆或鹰嘴豆）（约150-200克，依个人饮食需求调整）
                        - 大量蔬菜（如番茄、豌豆、绿豆等） - 一小份全麦面包或糙米
                        ### 晚间点心（可选）
                        - 一小份坚果（如杏仁、腰果等，注意控制份量，避免热量摄入过高）
                        - 一小杯绿茶或水
                        ### 注意事项：
                        1.**控制份量**：
                        减肥不只是选择正确的食物，还要控制份量，避免热量摄入过高。
                        2. **多吃蔬菜和水果**：
                        它们富含纤维、维生素和矿物质，有助于促进健康的消化系统，减少饱腹感。
                        3. **选择健康的脂肪**：
                        如鱼油、橄榄油、坚果等，有益于心脏健康，还能提供持久的能量。
                        4. **适量蛋白质**：
                        蛋白质有助于修复和增强肌肉，还能让你有饱腹感。
                        5. **限制加工食品和糖的摄入**：
                        减少糖的摄入有助于控制体重，改善血糖水平。
                        6. **保持水分**：
                        每天至少喝8杯水（约2升），帮助提高新陈代谢率。
                        7. **定时吃饭**：
                        尽量每天在同一时间吃饭，帮助调节身体的内啡肽循环，促进新陈代谢。
                        8. **适度运动**：
                        结合适度的有氧和无氧运动，有助于加速减肥过程。
                        请记住，这只是一个通用的减肥食谱，每个人的身体状况都不同，
                        最好在改变饮食习惯之前咨询医生或营养师，以便制定一个更适合您个人情况的计划。"""
        embedding = self.embedding_factory.get_embedding(text=long_text, model_name="sbert", max_tokens_each_chunk=100)
        self.assertEqual(embedding.shape, (768,))  # SBERT embedding dimension is 768

        # Test similarity with a shorter version of the text
        test_text = "一小份坚果和水"
        test_embedding = self.embedding_factory.get_embedding(text=test_text, model_name="sbert")
        similarity = self.embedding_factory.get_model("sbert").similarity(embedding, test_embedding)
        self.assertGreater(similarity, 0.6)  # Similar text should have moderate to high similarity

        test_text = "早餐, 午餐, 晚餐"
        test_embedding = self.embedding_factory.get_embedding(text=test_text, model_name="sbert")
        similarity = self.embedding_factory.get_model("sbert").similarity(embedding, test_embedding)
        self.assertGreater(similarity, 0.6)  

        test_text = "这是一个谎言。"
        test_embedding = self.embedding_factory.get_embedding(text=test_text, model_name="sbert")
        similarity = self.embedding_factory.get_model("sbert").similarity(embedding, test_embedding)
        self.assertLessEqual(similarity, 0.2)  

if __name__ == '__main__':
    unittest.main()