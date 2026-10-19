import json
from pathlib import Path

import bm25s

def retrieve_chunks(query: str, k: int):
    index_path = Path("data/processed/bm25_index")

    indexer = bm25s.BM25.load(str(index_path))
    query_token = bm25s.tokenize([query])

    doc_ids, score = indexer.retrieve(query_token, k=k)
    corpus_path = index_path / "corpus.jsonl"

    with open(corpus_path, "r", encoding="utf-8") as file:
        records = [json.loads(line) for line in file]


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

    return chunks

