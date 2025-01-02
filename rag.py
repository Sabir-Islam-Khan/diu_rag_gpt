from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from typing import List, ClassVar
from pydantic import BaseModel, Field
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from langchain_core.documents import Document
import os
from langchain_openai import OpenAIEmbeddings

from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings

from langchain_chroma import Chroma

from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


load_dotenv()

def load_documents(folder_path: str) -> List[Document]:
    documents = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif filename.endswith('.docx'):
            loader = Docx2txtLoader(file_path)
        else:
            print(f"Unsupported file type: {filename}")
            continue
        documents.extend(loader.load())
    return documents

folder_path = "documents"
documents = load_documents(folder_path)
print(f"Loaded {len(documents)} documents from the folder.")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1800,
    chunk_overlap=200,
    length_function=len
)

splits = text_splitter.split_documents(documents)
print(f"Split the documents into {len(splits)} chunks.")

embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

collection_name = "my_collection"
vectorstore = Chroma.from_documents(
    collection_name=collection_name,
    documents=splits,
    embedding=embedding_function,
    persist_directory="./chroma_db"
)
print("Vector store created and persisted to './chroma_db'")

retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

llm = ChatOpenAI(model="gpt-3.5-turbo")

template = """You are a chatbot of Daffodil International University made for assisting students answering their various queries. 
Answer questions based on the context provided. If the context does not contain the answer, say "I don't know based on the provided context." Here is the context:
{context}
Here is the question from student: {question}
Answer: """

prompt = ChatPromptTemplate.from_template(template)

def docs2str(docs):
    return "\n\n".join(doc.page_content for doc in docs)

search_results = vectorstore.similarity_search("Total departments of FSIT and their name", k=4)
print(f"\033[33mQuestion: {retriever}\033[0m")
rag_chain = (
    {"context": retriever | docs2str, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

question = "Total departments of FSIT and their name"
response = rag_chain.invoke(question)
print(f"\033[33mQuestion: {question}\033[0m")  # Yellow text
print(f"\033[32mAnswer: {response}\033[0m")    # Green text

