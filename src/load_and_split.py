import sys
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_community.document_loaders import TextLoader


def retrieve_files(path) -> list:
    valid_files = {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".rst"}
    skip_dir = {".git", ".github", ".__pycahche__", ".mypy_cache", ".venv"}
    list_of_files = []
    try:
        for item in path.rglob("*"):
            if (
                item.is_file()
                and item.suffix.lower() in valid_files
                and not any(skip in item.parts for skip in skip_dir)
            ):
                list_of_files.append(item)
    except OSError as e:
        raise ValueError(f"Could not scan folder '{path} : {e}")

    #print(f"len: {len(list_of_files)}")
    return list_of_files


def build_splitter(c_size: int,):  # -> tuple[RecursiveCharacterTextSplitter * 2]
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=c_size, chunk_overlap=50, add_start_index=True
    )

    python_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON,
        chunk_size=c_size,
        chunk_overlap=50,
        add_start_index=True,
    )

    return text_splitter, python_splitter


def load_and_split(files: list[pathlib.path], chunk_size: int) -> list[Document]:
    if not isinstance(chunk_size, int):
        raise ValueError("chunk_size must be an int")

    try:
        if not 0 <= chunk_size <= 2000:
            raise ValueError("chunk_size must be between 0 and 2000")

    documents: list[Document] = []
    text_splitter, python_splitter = build_splitter(chunk_size)

    for file in files:
        loaded_doc = TextLoader(file, autodetect_encoding=True).load()
        splitter = python_splitter if file.suffix == ".py" else text_splitter
        documents.extend(splitter.split_documents(loaded_doc))



    return documents

