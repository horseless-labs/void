import faiss

from langchain import hub
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

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

# TODO: at the moment, the plan is one index per user, so we need to figure out a cleaner
#       way to do this.
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
    with open("base/services/openai_api_key.txt", "r") as file:
        key = file.read().strip()

    embeddings = OpenAIEmbeddings(api_key=key)
    vector_store = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
    return vector_store

# TODO: consider renaming this. It is only referrenced to create the index on
# the user registration page. open_faiss_index() is used everywhere else.
def open_or_create_faiss_index(username):
    db_path = f"base/indices/{username}_faiss_index"
    init_faiss(db_path)

# TODO: Determine if this is redundant. Journal is current just using add_string_to_store()
# `doc` here is the path to a plaintext document
# This function or a version of it will come into play in the implementation
# of Journal Mode
def add_doc_to_store(doc, db_path="./faiss_index"):
    check_document_existence(doc)
    check_db_existence(db_path)

    with open(doc, "r") as file:
        content = file.read()

    # TODO: Figure out chunk size optimization
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=250, chunk_overlap=10)
    splits = text_splitter.split_text(content)
    documents = [Document(page_content=x) for x in splits]

    vector_store = open_faiss_index(db_path)
    vector_store.add_documents(documents)
    vector_store.save_local(db_path)

# Add a user's chat string to their vector store
def add_string_to_store(chat_string, db_path="./faiss_index"):
    vector_store = open_faiss_index(db_path)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=25)
    splits = text_splitter.split_text(chat_string)
    documents = [Document(page_content=x) for x in splits]

    print(f"From vectorize.py, add_string_to_store.\nSplits: {splits}\ndocuments: {documents}")
    vector_store.add_documents(documents)
    vector_store.save_local(db_path)

# Makes a query to the given vector store.
# This one is more akin to a search engine.
def query_store(query, db_path="./faiss_index"):
    vector_store = open_faiss_index(db_path)
    results = vector_store.similarity_search_with_score(query=query)

    output = ""
    for doc, score in results:
        output += f"* {doc.page_content} [{doc.metadata}], score: {score}\n"

    return output

# Helper function for ask_store()
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Uses an LLM to ask questions about the contents of a vector store.
def ask_store(query, db_path="./faiss_index"):
    with open("base/services/openai_api_key.txt", "r") as file:
        key = file.read().strip()
    
    # TODO: Experiment with different temperatures.
    # The default in BaseChatOpenAI is 0.7. This produced hallucinations when
    # queried on a very small amount of vectorized data. (Seriously, just
    # stuff like "Just testing" and "How much coffee is safe to drink?")
    llm = ChatOpenAI(api_key=key, temperature=0.0)
    vector_store = open_faiss_index(db_path)
    retriever = vector_store.as_retriever()

    # The text of this prompt can be found in a playground here:
    # https://smith.langchain.com/hub/rlm/rag-prompt/playground
    prompt = hub.pull("rlm/rag-prompt")

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough() }
        | prompt
        | llm
        | StrOutputParser()
    )

    output = rag_chain.invoke(query)
    return output