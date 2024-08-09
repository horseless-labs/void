import faiss

from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from langchain_community.document_loaders import TextLoader
# from langchain.schema import Document
from langchain_core.documents import Document

from typing import List

import os

def text_split(documents: TextLoader):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=25)
    texts = text_splitter.split_documents(documents)
    return texts

def get_embeddings(texts: List[Document]):
    embeddings = OpenAIEmbeddings()
    vector_db = FAISS.from_documents(texts, embeddings)
    return vector_db

def check_document_existence(document_path):
    if not os.path.isfile(document_path):
        raise FileNotFoundError(f"The document file '{document_path}' does not exist.")

def check_db_existence(db_path):
    if not os.path.isdir(db_path):
        raise NotADirectoryError(f"The DB directory '{db_path}' does not exist.")

def init_faiss(db_path="./faiss_index"):
    if os.path.exists(db_path):
        print(f"FAISS index already exists at {db_path}. Aborting.")
        return

    dir = os.path.dirname(os.path.abspath(__file__))
    loader = TextLoader(os.path.join(dir, "init_faiss.txt"))
    document = loader.load()
    texts = text_split(document)
    print(texts)

    vector_db = get_embeddings(texts)
    print("Initializing the vector.")
    vector_db.save_local(db_path)

def open_faiss_index(db_path):
    with open("openai_api_key.txt", "r") as file:
        key = file.read().strip()

    embeddings = OpenAIEmbeddings(api_key=key)
    vector_store = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
    return vector_store

def add_doc_to_store(doc, db_path="./faiss_index"):
    check_document_existence(doc)
    check_db_existence(db_path)

    with open("openai_api_key.txt", "r") as file:
        key = file.read().strip()

    with open(doc, "r") as file:
        content = file.read()
    print(content)

    embeddings = OpenAIEmbeddings(api_key=key)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=250, chunk_overlap=10)
    splits = text_splitter.split_text(content)
    documents = [Document(page_content=x) for x in splits]
    print(documents)

    """
    index = faiss.IndexFlatL2(len(OpenAIEmbeddings().embed_query("hello world")))

    vector_store = FAISS(
        embedding_function=OpenAIEmbeddings(),
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={}
    )
    """

    vector_store = open_faiss_index(db_path)

    vector_store.add_documents(documents)
    vector_store.save_local(db_path)

if __name__ == '__main__':
    # init_faiss()
    # add_doc_to_store("new_doc.txt")

    vector_store = open_faiss_index("./faiss_index")
    results = vector_store.similarity_search(query="appreciating the little things", k=1)
    for doc in results:
        print(f"* {doc.page_content} [{doc.metadata}]")