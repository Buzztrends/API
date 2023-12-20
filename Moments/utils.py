from langchain.vectorstores.chroma import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm
from langchain.memory.vectorstore import VectorStoreRetrieverMemory
from langchain.retrievers import BM25Retriever,EnsembleRetriever
from utils.utils import get_embedding_function
from logger.MomentGenLogger import MomentGenLogger
logger = MomentGenLogger().getLogger()
logger.info("Logger Initialize")
def build_splited_docs(sitetexts):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0, separators=[" ", ".", ",", "\n"])

    docs, metadatas = [], []
    for page in tqdm(sitetexts, "Spliting text"):
        splits = text_splitter.split_text(page['text'])
        docs.extend(splits)
        metadatas.extend([{"source": page['source']}] * len(splits))
        # print(f"Split {page['source']} into {len(splits)} chunks")

    return docs, metadatas

def build_vectorstore(sitetexts, k=20):
    logger.info("Splitting")
    docs, metadatas = build_splited_docs(sitetexts)
    logger.info("encoding")
    chunked_docs = divide_chunks(docs,160)
    chunked_metadatas = divide_chunks(metadatas,160)
    vectorstore = Chroma.from_texts(chunked_docs, get_embedding_function(), metadatas=chunked_metadatas)
    logger.info("building retriver")
    retriever = vectorstore.as_retriever(search_kwargs={'k': k})
    keyword_memory = VectorStoreRetrieverMemory(
        retriever=retriever,
        input_key="keywords",
        memory_key="company_name"
        )
    moment_memory = VectorStoreRetrieverMemory(
        retriever=retriever,
        input_key="moments",
        )
    logger.info("Returning Retriever")
    return vectorstore, retriever, keyword_memory, moment_memory
def divide_chunks(l, n):
    for i in range(0, len(l), n): 
        yield l[i:i + n]

def build_vectorstore_ensemble(sitetexts,k=20):
    print("Splitting")
    
    docs, metadatas = build_splited_docs(sitetexts)
    print("encoding")
    chunked_docs = divide_chunks(docs)
    chunked_metadatas = divide_chunks(metadatas,160)
    
    vectorstore = Chroma.from_texts(chunked_docs, get_embedding_function(), metadatas=chunked_metadatas)
    print("building retriver")
    retriever = vectorstore.as_retriever(search_kwargs={'k': 40})
    keyword_retreiver = BM25Retriever.from_texts(chunked_docs,metadatas=chunked_metadatas)
    
    keyword_retreiver.k = 40
    
    ensemble_retriever = EnsembleRetriever(retrievers=[retriever,keyword_retreiver],weights=[0.5,0.5],)

    return vectorstore, ensemble_retriever, None, None