from langchain.vectorstores.chroma import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm
from langchain.memory.vectorstore import VectorStoreRetrieverMemory

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
    print("Splitting")
    docs, metadatas = build_splited_docs(sitetexts)
    print("encoding")
    vectorstore = Chroma.from_texts(docs, OpenAIEmbeddings(), metadatas=metadatas)
    print("building retriver")
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

    return vectorstore, retriever, keyword_memory, moment_memory
