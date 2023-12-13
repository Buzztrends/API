from .utils import build_vectorstore
from utils.utils import get_sitetexts,get_related_links
from langchain.memory.vectorstore import VectorStoreRetrieverMemory
from logger.MomentGenLogger import MomentGenLogger
logger = MomentGenLogger().getLogger()
def get_memory_for_custom_moment(moment,business_type,country_code):
    logger.info(f"{__name__} Called:\n- Parameters:\n\t-Moment:{moment}\n\tBusiness Type:{business_type},\n\tCountry Code:{country_code}")
    moment =moment.split(" | ")[0]

    try:
        moment_context_sitetexts = get_sitetexts(get_related_links(moment.replace("Title: ", "") + f" {business_type}", country=country_code, num_results=5))
    except Exception as e:
        logger.error(f"Unexpected Error Occured in Getting Site Texts.\nError:{e}")
    try:
        moment_vectorstore, moment_retriver, _, _ = build_vectorstore(moment_context_sitetexts)
    except Exception as e:
        logger.error(f"Unexpected Error Occured in Building Vector Store.\nError:{e}")
    moment_memory= VectorStoreRetrieverMemory(
                            retriever=moment_retriver,
                            input_key="moment_query"
                            )
    logger.info("Moment Generated Successfully")
    return moment_memory

