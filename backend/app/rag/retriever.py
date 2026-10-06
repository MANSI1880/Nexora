import os
from typing import Dict, Any
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

VECTOR_STORE_DIR = "./chroma_db"
KNOWLEDGE_BASE_DIR = "../knowledge-base"

def init_vector_store():
    """Initializes the vector store from markdown files."""
    embeddings = OpenAIEmbeddings(
        api_key=os.environ.get("OPENAI_API_KEY", "dummy_key")
    )
    
    # For MVP, we load documents on the fly if directory is empty
    # In production, this would be a separate ingestion pipeline
    loader = DirectoryLoader(KNOWLEDGE_BASE_DIR, glob="**/*.md", loader_cls=TextLoader)
    try:
        documents = loader.load()
    except Exception:
        return None
    
    if not documents:
        return None
        
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = text_splitter.split_documents(documents)
    
    # We use in-memory chromadb for the MVP unit tests to avoid locking issues,
    # but in reality it could persist to VECTOR_STORE_DIR
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    return vectorstore

def get_rag_answer(query: str, intent: str, llm: ChatOpenAI) -> Dict[str, Any]:
    vectorstore = init_vector_store()
    
    if not vectorstore:
         return {
             "answer": "I don't have any knowledge base documents loaded to answer this.",
             "sources": []
         }
         
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(query)
    
    context = "\n\n".join([d.page_content for d in docs])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an IT Support Agent. Answer the user's question based ONLY on the provided context.
        Do not invent IT procedures or URLs. Do not claim actions were completed. If the context does not contain the answer, say "I don't have enough information to solve this and recommend creating a ticket."
        
        CONTEXT:
        {context}"""),
        ("user", "{query}")
    ])
    
    chain = prompt | llm
    result = chain.invoke({"context": context, "query": query})
    
    return {
        "answer": result.content,
        "sources": [{"page_content": d.page_content, "metadata": d.metadata} for d in docs]
    }
