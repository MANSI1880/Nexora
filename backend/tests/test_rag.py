import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from langchain_community.document_loaders import DirectoryLoader, TextLoader

from app.rag.retriever import get_knowledge_base_dir, init_vector_store

EXPECTED_KB_FILES = {
    "account-unlock.md",
    "application-access.md",
    "email.md",
    "password.md",
    "software.md",
    "vpn.md",
}

def test_knowledge_base_path_resolves_and_exists():
    kb_dir = get_knowledge_base_dir()
    assert os.path.isabs(kb_dir)
    assert os.path.isdir(kb_dir)
    assert Path(kb_dir).name == "knowledge-base"

def test_knowledge_base_all_six_documents_discovered():
    kb_dir = get_knowledge_base_dir()
    loader = DirectoryLoader(kb_dir, glob="**/*.md", loader_cls=TextLoader)
    documents = loader.load()

    assert len(documents) == 6
    found_files = {Path(doc.metadata.get("source", "")).name for doc in documents}
    assert found_files == EXPECTED_KB_FILES

def test_knowledge_base_custom_env_override(tmp_path, monkeypatch):
    custom_kb = tmp_path / "custom_kb"
    custom_kb.mkdir()
    doc_file = custom_kb / "custom_topic.md"
    doc_file.write_text("# Custom Knowledge\nContent for testing.", encoding="utf-8")

    monkeypatch.setenv("KNOWLEDGE_BASE_DIR", str(custom_kb))
    resolved_dir = get_knowledge_base_dir()
    assert resolved_dir == str(custom_kb)

    loader = DirectoryLoader(resolved_dir, glob="**/*.md", loader_cls=TextLoader)
    documents = loader.load()
    assert len(documents) == 1
    assert "custom_topic.md" in documents[0].metadata.get("source", "")

@patch("app.rag.retriever.Chroma.from_documents")
@patch("app.rag.retriever.GoogleGenerativeAIEmbeddings")
def test_init_vector_store_with_custom_dir(mock_embeddings, mock_chroma, tmp_path):
    temp_kb = tmp_path / "temp_docs"
    temp_kb.mkdir()
    (temp_kb / "guide.md").write_text("Guide content for vector store test", encoding="utf-8")

    mock_chroma.return_value = MagicMock()
    vs = init_vector_store(kb_dir=str(temp_kb))

    assert vs is not None
    assert mock_chroma.called
    splits_arg = mock_chroma.call_args[1]["documents"]
    assert any("guide.md" in s.metadata.get("source", "") for s in splits_arg)
