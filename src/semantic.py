import json
from functools import lru_cache
from pathlib import Path 

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


CORPUS_PATH = Path("data/processed/bm25_index/corpus.jsonl")
SEMANTIC_DIR = Path("data/processed/semantic_index")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def load_model():
    return SentenceTransformer(MODEL_NAME, device="cpu")


def build_semantic_index():
    #load the chunking fomr the json file
    with CORPUS_PATH.open("r", encoding="utf-8") as file:
        records = [json.loads(line) for line in file]

    #cond to check if file exists or not!
    
    #if not records:
    #       raise error 
    
    model = load_model()

    #extract the text/docuemnts from thisjson file
    texts = [record["text"] for record in records]
    
    #batching instead of treating 1k cgybjs at time, we treat 32 doc every time
    embeddings = model.encode(
        texts,
        batch_size=32,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
        device="cpu",
    )

    #we converted every chunk to a semantic vector, this is the semantic indexing 
    #represnts the exact meaning of every chunk
    #we can use these vectors to find the cloestest one semantically
    embeddings = np.asarray(embeddings, dtype=np.float32) #get this too!

    
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    SEMANTIC_DIR.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(SEMANTIC_DIR/"index.faiss"))

    #with (SEMANTIC_DIR/"index.faiss").open("w", encoding='utf-8') as file:
    #    for record in records:
    #        file.write(json.dumps(record, ensure_ascii=False) + "\n")

    clear_semantic_cache()

    
@lru_cache(maxsize=1)
def load_semantic_index():
    path = SEMANTIC_DIR/"index.faiss"

    #if not path.exists():
        #raise filenotfound!   

    return faiss.read_index(str(path))


@lru_cache(maxsize=1)
def load_semantic_corpus():
    with CORPUS_PATH.open("r", encoding="utf-8") as file:
        return tuple(json.loads(line) for line in file)




@lru_cache(maxsize=512)
def semantic_search_cached(query, k):
    model = load_model()
    index = load_semantic_index()
    records = load_semantic_corpus()

    query_vector = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
        device="cpu",
    )

    query_vector = np.asarray(query_vector, dtype=np.float32)

    k = min(k, index.ntotal)
    scores, ids = index.search(query_vector, k)

    results = []

    for doc_id, score in zip(ids[0], scores[0]):
        if doc_id < 0:
            continue

        record = records[int(doc_id)]

        results.append({
            "file_path": record["file_path"],
            "start": record["start"],
            "end": record["end"],
            "text": record["text"],
            "score": float(score),
        })

    return tuple(results)



def search_semantic(query: str, k: int=5):
    if not query.strip() or k <= 0:
        return []

    results = semantic_search_cached(query.strip(), k)

    return [dict(res) for res in results]



def clear_semantic_cache():
    semantic_search_cached.cache_clear()
    load_semantic_index.cache_clear()
    load_semantic_corpus.cache_clear()

















































'''
what batching?
Prevents RAM/CPU Overload: If you tried to pass all 1,000 (or 100,000) long chunks into the neural network at the exact same millisecond, the model would try to create a massive tensor in your CPU's memory, crash, and throw an Out-Of-Memory (OOM) error.


The Loop: Once those 32 are done, it takes chunks 32 to 63, processes them, and repeats until all 1,000 chunks are finished.

what does hte model return: embeddings = model.encode()
encode takes text and convert to numerical id that the computer understand

whats embedding = embeddig = model.encode()

embeddins = 2d numerical array (or pyrorch tension depemdin on the setting)

this is a grid with demension of (N, D)
N = (rows) numbers of chunks passed in this cse 1000
D = (cols) the dimensions of the semantic vector space for minilm model 
this is always 384 columns 

embdding =
each row, meaning every chunks 
has a value of 384 dimentioan array of foating point numbers 


--> high dimentional space
this geomatric space was already created, trained and baked in the model before you even downloaded it

1- the space is already built into the model
trained in the model, they fed billion of sentences and used a technique called constrasive training

2- code
when we call model.encode(texts)
we are taking the chunks and ask the model to tell us where these chunks are placed in the map (high dimentiona space thats pretarined in the model)


the list of float numbers that we get is the coordinates/pins on the map


so when we pass a chunk/doc/text to the model, we are alwayss gonna get a fixed size of loat numbers that tell us where exacatly its place in this map

regardless of the size of text, that could 5 words sentence or a whole text
we are alwys gonna get a fixed arra  of 384 float number
and this si the magic of pooling layer

------>> one catch!!!!!!!!!!!!!!!

The One Catch: Model Token Limits
While you can pass varying sizes of text, every model has a maximum hard limit on how much it can read at once (its context window, usually 256 or 512 tokens for MiniLM).

If you tried to pass a massive 1,000-word chunk:

The model wouldn't crash, but it would cut off (truncate) everything past its token limit, ignoring the rest of the text.

That is why in RAG pipelines, we deliberately chop our documents into smaller, bite-sized chunks (e.g., 100 to 300 words) before passing them to model.encode(). This ensures every chunk fits safely within the model's limit and gets a clean, accurate 384-dimensional coordinate!

'''


'''
in the mode.encode, we enabled the convert to numpy
yet we did it again here:


embeddings = np.asarray(embeddings, dtype=np.float32)

While convert_to_numpy=True tells SentenceTransformers to return a NumPy array instead of a PyTorch tensor, it doesn't strictly force the precision to float32. Depending on the model configuration or underlying libraries, it might return float64 (double precision) or standard Python floats.


Vector databases (like FAISS, ChromaDB, or custom numpy similarity search) expect 32-bit floating-point numbers (np.float32).

Using np.asarray(..., dtype=np.float32) acts as a strict type-enforcer, guaranteeing that every single number in your matrix is precisely 32 bits, saving memory and preventing type-mismatch errors down the line.


'''


'''
While both NumPy arrays and PyTorch tensors look and act very similar (both are multi-dimensional grids of numbers that support fast math operations), they are built for entirely different jobs under the hood.

Here are the key differences:

1. Hardware Acceleration (CPU vs. GPU)
NumPy: Designed exclusively to run on your CPU. It cannot use a GPU.

PyTorch Tensor: Designed to run on both CPUs and GPUs (CUDA/MPS). You can move a tensor to a graphics card with .to("cuda"), allowing it to leverage massive parallel processing for deep learning training and inference.

2. Automatic Differentiation (Grads)
NumPy: Has no concept of gradients. If you multiply two NumPy matrices, it just does the math. It cannot track operations to automatically calculate derivatives.

PyTorch Tensor: Built specifically for neural networks. It can track operations (requires_grad=True) to automatically compute gradients, which is how AI models learn during training.

3. Ecosystem Integration
NumPy: The universal standard for general data science, data manipulation (Pandas), and traditional scientific computing in Python.

PyTorch Tensor: The native data structure for PyTorch, deep learning pipelines, and neural network layers.

Summary: Why it matters for your RAG code
When your SentenceTransformer model is running its neural network layers internally, it uses PyTorch tensors on the backend.

Once the model finishes generating the final embeddings and you set convert_to_numpy=True, it converts those tensors into NumPy arrays because NumPy is lightweight, universally compatible with vector databases (like ChromaDB or FAISS), and doesn't require PyTorch installed to read or save them.
'''




