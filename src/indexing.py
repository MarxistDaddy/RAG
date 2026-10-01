from pathlib import Path
from .load_and_split import retrieve_files, load_and_split
import tqdm


def get_metadata(documents: list[Document]) -> Any: 
    content: list[str] = []
    metadata: list[dict] = []

    for doc in tqdm.tqdm(documents, desc="MB25S INDEXING"):
        content.append(doc.page_content)
        metadata.append(
            {
                "file_path": doc.metadata["source"],
                "start": doc.metadata["start_index"],
                "end": doc.metadata["start_index"] + len(doc.page_content)
            }
        )

    return content, metadata

def print_rec(rec):
    print(f"path = {rec[0]["file_path"]}")
    print(f"start = {rec[0]["start"]}")
    print(f"end = {rec[0]["end"]}")
    print(f"txt = {rec[0]["text"]}")


def index_files(chunk_size, path):
    retrieved_files = retrieve_files(path)
    documents = load_and_split(retrieved_files, chunk_size)
    #get the metadata and content
    content, metadata = get_metadata(documents)
    #print_metadata(content, metadata)
    #--> wrap everything in list of dict that include both meta and content as a single dict
    records = [
        {**meta, "text": txt}
        for meta, txt in zip(metadata, content)
        ]

    

    return None


