from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_community.document_loaders import TextLoader


def retrieve_files(path) -> list:
    valid_files = {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".rst"}
    skip_dir = {".git", ".github", ".__pycahche__", ".mypy_cache", ".venv"}
    list_of_files = []
    for item in path.rglob("*"):
        if (
            item.is_file()
            and item.suffix in valid_files
            and not any(skip in item.parts for skip in skip_dir)
        ):
            list_of_files.append(item)
    print(f"len: {len(list_of_files)}")
    return list_of_files


def build_splitter(
    c_size: int,
):  # -> tuple[RecursiveCharacterTextSplitter * 2]
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


def load_and_split(
    files: list[pathlib.path], chunk_size: int
) -> list[Document]:
    # try:
    if 0 <= chunk_size <= 2000:
        print(f"chunk_size: {chunk_size}")
    else:
        print("wrong size: has to be 0 - 2000 ")

    documents: list[Document] = []
    text_splitter, python_splitter = build_splitter(chunk_size)

    # print("language:")
    # for key in Language:
    #    print(key)

    for file in files:
        loaded_doc = TextLoader(file, autodetect_encoding=True).load()
        splitter = python_splitter if file.suffix == ".py" else text_splitter
        # print(f"{file.suffix} == {splitter}")
        documents.extend(splitter.split_documents(loaded_doc))

    return documents
