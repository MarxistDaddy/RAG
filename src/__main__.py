import sys
import fire
from pathlib import Path

from .indexing import index_files
import bm25s
from .retrieve import retrieve_chunks
from .llm_model import Model


class RAG:
    def __init__(self, data_path="data/raw/vllm-0.10.1"):
        self.path = Path(data_path)

        if not self.path.exists():
            print("[Error] Data path does not exist!", file=sys.stderr)
            sys.exit(1)
        else:
            print("YES PATH!")

        self.model = Model()

    def index(self, max_chunk_size: int = 2000):
        index_files(max_chunk_size, self.path)
        

    def search(self, query: str, k: int = 5):
        chunks = retrieve_chunks(query, k)

        context = "\n\n".join(
            f"source: {chunk['file_path']}\n"
            f"content: {chunk['text']}"
            for chunk in chunks
        )

        prompt = f"""

        Answer the question using only the context below.

        If the context does not contain the answer,
        say that you don't have enough information.
        context:
        {context}

        question:
        {query}

        answer:
        """

        res = self.model.generate(prompt)
        print(res)
        





def main() -> None:
    fire.Fire(RAG)

if __name__ == "__main__":
    main()

