import sys
import fire
from pathlib import Path

from .indexing import index_files


class RAG:
    def __init__(self, data_path="data/raw/vllm-0.10.1"):
        self.path = Path(data_path)

        if not self.path.exists():
            print("[Error] Data path does not exist!", file=sys.stderr)
            sys.exit(1)
        else:
            print(self.path)

    def index(self, max_chunk_size: int = 2000):
        res = index_files(max_chunk_size, self.path)
        print(f"main_index == {res}")
        










def main() -> None:
    fire.Fire(RAG)

if __name__ == "__main__":
    main()

