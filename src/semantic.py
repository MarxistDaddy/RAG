import json
from functools import lru_cache as lru
from pathlib import Path 

import faiss
import numpy as num
from sentence_transformers import SentenceTransformer


CORPUS_PATH = Path("data/processed/bm25_index/corpus.jsonl")




def build_index()
    with CORPUS_PATH.open("r", encoding="utf-8") as file:
        records = [json.loads(line) for line in file]

    #cond to check if file exists or not!






