import pytest
from ai.llm import Llm
from core.i18n import _, set_locale

class TestLlm:

    def test_retrieve_llm_by_name(self):
        # Test retrieving a known LLM
        llm_instance = Llm.retrieve_llm_by_name('wizardlm2')
        assert llm_instance is not None
        assert type(llm_instance).__name__ == 'OllamaLLM'

        llm_instance = Llm.retrieve_llm_by_name('llama3.1')
        assert llm_instance is not None
        assert type(llm_instance).__name__ == 'OllamaLLM'

        # Test retrieving an unknown LLM, should default to first LLM
        llm_instance = Llm.retrieve_llm_by_name('UnknownLLM')
        assert llm_instance is not None
        assert type(llm_instance).__name__ == 'OllamaLLM'

    def test_get_ai_response_by_wizardlm2(self):
        user_message = "Hello, how are you?"
        response = Llm.get_ai_response(user_message, 'wizardlm2')
        assert response is not None

    def test_get_ai_response_by_llama3_1(self):
        user_message = "Hello, how are you?"
        response = Llm.get_ai_response(user_message, 'llama3.1')
        assert response is not None

    def test_get_ai_response_by_gpt_4(self):
        user_message = "Hello, how are you?"
        response = Llm.get_ai_response(user_message, 'gpt-4')
        print("test_get_ai_response_by_gpt_4:", response)
        assert response is not None


    @pytest.mark.asyncio
    async def test_get_ai_response_by_llama3_1_async(self):
        user_message = "Hello, how are you?"
        response = await Llm.get_ai_response_async(user_message, 'llama3.1')
        print("test_get_ai_response_by_llama3_1_async:", response)
        assert response is not None

    def test_get_ai_response_by_deepseek(self):
        user_message = "Hi, how are you?"
        response = Llm.get_ai_response(user_message, 'deepseek')
        assert response is not None
        print("test_get_ai_response_by_deepseek:", response)

    @pytest.mark.asyncio
    async def test_get_ai_response_by_deepseek_async(self):
        user_message = "Hi, how are you?"
        response = await Llm.get_ai_response_async(user_message, 'deepseek')
        assert response is not None
        print("test_get_ai_response_by_deepseek_async:", response)

    def test_get_ai_response_by_qwen_plus(self):
        user_message = "Hi, how are you?"
        response = Llm.get_ai_response(user_message, 'qwen-plus')
        assert response is not None
        print("test_get_ai_response_by_qwen_plus:", response)

    def test_get_ai_response_by_qwen_max(self):
        user_message = "Hi, how are you?"
        response = Llm.get_ai_response(user_message, 'qwen-max')
        assert response is not None
        print("test_get_ai_response_by_qwen_max:", response)

    def test_get_ai_response_by_DOUBAO_1_5_PRO_32K_MODEL(self):
        user_message = "Hi, how are you?"
        response = Llm.get_ai_response(user_message, 'Doubao-1.5-pro-32k')
        assert response is not None
        print("test_get_ai_response_by_DOUBAO_1_5_PRO_32K_MODEL:", response)

    def test_get_ai_response_by_DOUBAO_1_5_PRO_256K_MODEL(self):
        user_message = "Hi, how are you?"
        response = Llm.get_ai_response(user_message, 'Doubao-1.5-pro-256k')
        assert response is not None
        print("test_get_ai_response_by_DOUBAO_1_5_PRO_256K_MODEL:", response)

    def test_get_ai_response_by_DOUBAO_1_5_LITE_32K_MODEL(self):
        user_message = "Hi, how are you?"
        response = Llm.get_ai_response(user_message, 'Doubao-1.5-lite-32k')
        assert response is not None
        print("test_get_ai_response_by_DOUBAO_1_5_LITE_32K_MODEL:", response)

    def test_get_ai_response_by_DOUBAO_PRO_32K_MODEL(self):
        user_message = "Hi, how are you?"
        response = Llm.get_ai_response(user_message, 'Doubao-pro-32k')
        assert response is not None
        print("test_get_ai_response_by_DOUBAO_PRO_32K_MODEL:", response)

    def test_generate_prompts_from_sentence(self):
        # Test normal case
        result = Llm.generate_prompts_from_text("How to make a sandwich", "deepseek")
        print("test_generate_prompts_from_sentence:", result)
        assert result is not None
        assert len(result) == 3

        # Test empty input
        result = Llm.generate_prompts_from_text("", "deepseek")
        assert result is not None
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_generate_prompts_from_sentence_async(self):
        # Test normal case
        result = await Llm.generate_prompts_from_text_async("How to make a sandwich", "deepseek")
        print("test_generate_prompts_from_sentence:", result)
        assert result is not None
        assert len(result) == 3

        # Test empty input
        result = await Llm.generate_prompts_from_text_async("", "deepseek")
        assert result is not None
        assert len(result) == 0

    def test_get_prompt_template_for_en(self):
        set_locale("en_US")
        template = Llm.get_prompt_template("content")
        assert template is not None
        assert template == "{input}\nPlease generate a description based on the above information. The word count is limited to 300 words."

    def test_get_prompt_template_for_zh(self):
        set_locale("zh_CN")
        template = Llm.get_prompt_template("content")
        assert template is not None
        assert template == "{input}\n请根据以上信息，生成一段描述信息，字数限制在300个以内，输出语言限定为[中文]。"

    def test_get_ai_response_from_template_en(self):
        set_locale("en_US")
        template = Llm.get_prompt_template("content")
        prompt = template.format(input="Logistics and transportation")
        result = Llm.get_ai_response(prompt, "wizardlm2")
        assert result is not None

    def test_get_ai_response_from_template_zh(self):
        set_locale("zh_CN")
        template = Llm.get_prompt_template("content")
        prompt = template.format(input="物流和运输")
        result = Llm.get_ai_response(prompt, "llama3.1")
        print("test_get_ai_response_from_template_zh:", result)
        assert result is not None

    def test_summary_message_history_by_staff(self):
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
            {"role": "user", "content": "How are you?"},
            {"role": "assistant", "content": "I'm good, thanks!"},
            {"role": "user", "content": "What's your favorite color?"},
            {"role": "assistant", "content": "My favorite color is blue."}
        ]
        result = Llm.summary_message_history(messages, "deepseek")
        print("test_summary_message_history:", result.get("output_text"))
        assert result is not None

    @pytest.mark.asyncio
    async def test_summary_message_history_by_staff_streaming(self):
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
            {"role": "user", "content": "How are you?"},
            {"role": "assistant", "content": "I'm good, thanks!"},
            {"role": "user", "content": "What's your favorite color?"},
            {"role": "assistant", "content": "My favorite color is blue."}
        ]

        summary_chunks = []
        async for chunk in Llm.summary_message_history_streaming(messages, "llama3.1"):
            print("test_summary_message_history_by_staff_streaming:", chunk)
            summary_chunks.append(chunk)

        # Assertions
        assert len(summary_chunks) > 0

    @pytest.mark.asyncio
    async def test_summary_message_history_by_staff_streaming_by_deepseek(self):
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
            {"role": "user", "content": "How are you?"},
            {"role": "assistant", "content": "I'm good, thanks!"},
            {"role": "user", "content": "What's your favorite color?"},
            {"role": "assistant", "content": "My favorite color is blue."}
        ]

        summary_chunks = []
        async for chunk in Llm.summary_message_history_streaming(messages, "deepseek"):
            print("test_summary_message_history_by_staff_streaming_by_deepseek:", chunk)
            summary_chunks.append(chunk)

        # Assertions
        assert len(summary_chunks) > 0

    def test_summary_message_history_by_map_reduce(self):
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
            {"role": "user", "content": "How are you?"},
            {"role": "assistant", "content": "I'm good, thanks!"},
            {"role": "user", "content": "What's your favorite color?"},
            {"role": "assistant", "content": "My favorite color is blue."}
        ]
        result = Llm.summary_message_history(messages, "wizardlm2", chain_type="map_reduce")
        print("test_summary_message_history by map_reduce:", result.get("output_text"))
        assert result is not None