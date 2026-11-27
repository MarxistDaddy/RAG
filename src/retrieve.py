import json
import bm25s

from pathlib import Path
from functools import lru_cache

#redundant
INDEX_PATH = Path("data/processed/bm25_index")

#indexing caching
@lru_cache(maxsize=1)
def load_index(index_path: str):
    #print("load_index")
    try:
        return bm25s.BM25.load(index_path)
    except FileNotFoundError as e:
        raise ValueError(f"BM25 index not found at {index_path}}. Run the index command first")
    except Exception as e:
        raise ValueError(F"Failed to load the BM25 index from '{index_path}': {e}")


@lru_cache(maxsize=1)
def load_corpus(corpus_path: str):
    #print("load_corpus")
    try:
        with open(corpus_path, "r", encoding="utf-8") as file:
            return tuple(json.loads(line) for line in file)
    except FileNotFoundError as e:
        raise ValueError(f"Corpus not found in '{corpus_path}'. Run the index command first")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format at '{corpus_path}': {e}")
    except Exception as e:
        raise ValueError(f"Failed to load '{corpus_path}': {e}")


@lru_cache(maxsize=512)
def retrieve_chunks_cached(query: str, k: int, index_path: str):
    indexer = load_index(index_path)
    query_tokens = bm25s.tokenize([query])

    doc_ids, scores = indexer.retrieve(query_tokens, k=k)
    records = load_corpus(str(Path(index_path) / "corpus.jsonl"))

    chunks = []
    try:
        for doc_id, score in zip(doc_ids[0], scores[0]):
            record = records[int(doc_id)]

            chunks.append({
                "file_path": record["file_path"],
                "start": record["start"],
                "end": record["end"],
                "text": record["text"],
                "score": float(score),
            })
    except (KeyError, IndexError, TypeError, ValueError) as e:
        raise ValueError(
                "the BM25 and corpus jsonl do not match (missing field or out-of-range indxe)"
                f"re-run the index command: {e}"
        )

    return tuple(chunks)


def retrieve_chunks(query: str, k: int = 5):
    if not isinstance((query, str)):
        raise ValueError("query must be a string")

    if not isinstance((k, int)):
        raise ValueError("K must be an int")
    
    try:
        if not query.strip() or k <= 0:
            return []
    except (AttributeError, TypeError) as e:
        raise ValueError("query must be a string and 'k' an int")

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

