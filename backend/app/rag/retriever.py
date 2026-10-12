import os
from pathlib import Path
from typing import Dict, Any, Optional
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

VECTOR_STORE_DIR = "./chroma_db"

def get_knowledge_base_dir() -> str:
    """Resolves the knowledge base directory robustly across environments."""
    env_dir = os.environ.get("KNOWLEDGE_BASE_DIR")
    if env_dir and os.path.isdir(env_dir):
        return os.path.abspath(env_dir)

    rag_dir = Path(__file__).resolve().parent

    # 1. Standard repo structure: <repo_root>/knowledge-base (parents[2] from app/rag)
    repo_kb = rag_dir.parents[2] / "knowledge-base"
    if repo_kb.is_dir():
        return str(repo_kb)

    # 2. Container/package structure: backend/knowledge-base
    backend_kb = rag_dir.parents[1] / "knowledge-base"
    if backend_kb.is_dir():
        return str(backend_kb)

    # 3. Relative to current working directory
    cwd_kb = Path.cwd() / "knowledge-base"
    if cwd_kb.is_dir():
        return str(cwd_kb)

    cwd_parent_kb = Path.cwd().parent / "knowledge-base"
    if cwd_parent_kb.is_dir():
        return str(cwd_parent_kb)

    return str(repo_kb)

KNOWLEDGE_BASE_DIR = get_knowledge_base_dir()

def init_vector_store(kb_dir: Optional[str] = None):
    """Initializes the vector store from markdown files."""
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-2",
        google_api_key=os.environ.get("GEMINI_API_KEY", "dummy_key")
    )

    target_dir = kb_dir or get_knowledge_base_dir()
    loader = DirectoryLoader(target_dir, glob="**/*.md", loader_cls=TextLoader)
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

def get_rag_answer(query: str, intent: str, llm: ChatGoogleGenerativeAI) -> Dict[str, Any]:
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
