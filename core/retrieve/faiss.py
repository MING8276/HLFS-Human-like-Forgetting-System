from llama_index import Document
from langchain.llms import OpenAIChat
from llama_index import LLMPredictor, GPTSimpleVectorIndex, PromptHelper, ServiceContext
import utils.tools as tools
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

class AServiceContext:

    def __init__(self, model_name: str = 'gpt-3.5-turbo', max_input_size: int = 4096, num_output: int = 256,
                 max_chunk_overlap: int = 20):
        llm_predictor = LLMPredictor(llm=OpenAIChat(model_name=model_name))
        prompt_helper = PromptHelper(max_input_size, num_output, max_chunk_overlap)
        self.service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)


service_manager = AServiceContext()


def retrieve_in_PAISS(text: str, query: str, index_path: str) -> str:

    cur_index = GPTSimpleVectorIndex.from_documents([Document(text)], service_context=service_manager.service_context)
    cur_index.save_to_disk(index_path)
    user_memory_index = GPTSimpleVectorIndex.load_from_disk(index_path)
    related_memos = user_memory_index.query(query, service_context=service_manager.service_context)
    return related_memos.response.strip()


if __name__ == '__main__':
    pass
