from pathlib import Path

import bm25s
import tqdm

from .load_and_split import load_and_split, retrieve_files


def get_metadata(documents: list[Document]) -> Any:
    content: list[str] = []
    metadata: list[dict] = []

    for doc in tqdm.tqdm(documents, desc="MB25S INDEXING"):
        content.append(doc.page_content)
        metadata.append(
            {
                "file_path": doc.metadata["source"],
                "start": doc.metadata["start_index"],
                "end": doc.metadata["start_index"] + len(doc.page_content),
            }
        )

    return content, metadata


def print_rec(rec):
    # print(f"path = {rec["file_path"]}")
    # print(f"start = {rec["start"]}")
    # print(f"end = {rec["end"]}")
    print(f"txt = {rec['text']}")
    # print(f"length of thext is --> {len(rec["text"])}")


def index_files(chunk_size, path):
    retrieved_files = retrieve_files(path)
    documents = load_and_split(retrieved_files, chunk_size)
    content, metadata = get_metadata(documents)
    #so that corpus of indexer can support it! it doesnt support list of documents
    records = [{**meta, "text": txt} for meta, txt in zip(metadata, content)]
    #i = 0
    #while i < 10:
    #    print_rec(records[i])
    #    print("=====\n\n")
    #    i += 1

    # content is a list!
    corpus_tokens = bm25s.tokenize(content)  # ids + vocab: token-id pair value
    # print(corpus_tokens) #numpy arrays
    indexer = bm25s.BM25()
    indexer.index(corpus_tokens)
    indexer.save("data/processed/bm25_index", corpus=records)

    return records

