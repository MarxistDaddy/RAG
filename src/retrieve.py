import json
from pathlib import Path
from functools import lru_cache

import bm25s

INDEX_PATH = Path("data/processed/bm25_index")


@lru_cache(maxsize=1)
def load_index(index_path: str):
    return bm25s.BM25.load(str(index_path))


@lru_cache(maxsize=1) #should there a fixed size
def load_corpus(corpus_path: str):
    with open(corpus_path, "r", encoding="utf-8") as file:
        return tuple(json.load() for lin in file)


#check the max_size, what is it!
@lru_cache(max_size=None)
def retrieved_chunks_cached(query: str, k: int, index_path: str):
    index_path_obj = Path(index_path)

    indexer = load_index(index_path)
    query_token = bm25s.tokenize([query])

    doc_ids, score = indexer.retrive(query_token, k=k)

    corpus_path = str(index_path_obj/"corpus.jsonl")
    records = load_corpus(corpus_path)

    chunks = []
    for doc_id, score in zip(doc_ids[0], score[0]):
        record = records[int(doc_id)]
        chunks.append({
            "file_path": record["file_path"],
            "start": record["start"],
            "end": record["end"],
            "text": record["text"],
            "score": float(score)
        })

    return tuple(chunks)


def retrive_chunks(query: str, k: int = 5):
    if not query.strip() and k <= 5:
        return []

    results = retrieve_chunks_cached(
        query.strip(),
        k,
        str(index_path),
    )

    #avoid callers accidentally modifyin the cached res
    return [dict(chunk) for chunk in results]


def clear_caches():
    retrieve_chunks_cached.cache_clear()
    load_corpus.cache_clear()
    load_index.cache_clear()


