from pathlib import Path
from .load_and_split import retrieve_files, load_and_split


def index_files(chunk_size, path):
    retrieved_files = retrieve_files(path)
    documents = load_and_split(retrieved_files, chunk_size)

    return documents 


