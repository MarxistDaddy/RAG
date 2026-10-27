import json
from pathlib import Path
from functools import lru_cache

import bm25s


INDEX_PATH = Path("data/processed/bm25_index")

#indexing caching
@lru_cache(maxsize=1)
def load_index(index_path: str):
    print("load_index")
    return bm25s.BM25.load(index_path)



@lru_cache(maxsize=1)
def load_corpus(corpus_path: str):
    print("load_corpus")
    with open(corpus_path, "r", encoding="utf-8") as file:
        return tuple(json.loads(line) for line in file)




@lru_cache(maxsize=512)
def retrieve_chunks_cached(query: str, k: int, index_path: str):
    print("retrieve_chunks")
    index_path_obj = Path(index_path)

    indexer = load_index(index_path)
    query_tokens = bm25s.tokenize([query])

    doc_ids, scores = indexer.retrieve(query_tokens, k=k)

    corpus_path = str(index_path_obj / "corpus.jsonl")
    records = load_corpus(corpus_path)

    chunks = []
    for doc_id, score in zip(doc_ids[0], scores[0]):
        record = records[int(doc_id)]

        chunks.append({
            "file_path": record["file_path"],
            "start": record["start"],
            "end": record["end"],
            "text": record["text"],
            "score": float(score),
        })

    return tuple(chunks)






def retrieve_chunks(query: str, k: int = 5):
    if not query.strip() or k <= 0:
        return []

    results = retrieve_chunks_cached(
        query.strip(),
        k,
        str(INDEX_PATH),
    )
    
    return [dict(chunk) for chunk in results]








def clear_caches():
    retrieve_chunks_cached.cache_clear()
    load_corpus.cache_clear()
    load_index.cache_clear()








