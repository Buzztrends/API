from .utils import build_vectorstore
from utils.utils import get_sitetexts,get_related_links
from langchain.memory.vectorstore import VectorStoreRetrieverMemory

def get_memory_for_custom_moment(moment,business_type,country_code):
    moment =moment.split(" | ")[0]
    moment_context_sitetexts = get_sitetexts(get_related_links(moment.replace("Title: ", "") + f" {business_type}", country=country_code, num_results=5))
    moment_vectorstore, moment_retriver, _, _ = build_vectorstore(moment_context_sitetexts)
    moment_memory= VectorStoreRetrieverMemory(
                            retriever=moment_retriver,
                            input_key="moment_query"
                            )
    return moment_memory

