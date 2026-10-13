import sys
import fire
from pathlib import Path

from .indexing import index_files
import bm25s
from .retrieve import retrieve_chunks
from .llm_model import Model

from .data_models import (
    UnansweredQuestion,
    MinimalSource,
    MinimalSearchResults,
    StudentSearchResults,
    MinimalAnswer,
)


import json
import tqdm

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
        question = UnansweredQuestion(question=query)

        chunks = retrieve_chunks(question.question, k)

        sources = [
            MinimalSource(
                file_path=chunk["file_path"],
                first_character_index=chunk["start"],
                last_character_index=chunk["end"]
            )
            for chunk in chunks
        ]
        
        return chunks, MinimalSearchResults(
            question_id=question.question_id,
            question=question.question,
            retrieved_sources=sources
        )
    

    def search_dataset(self, dataset_path: str, k: int, save_directory: str="dataset_output"):
        data_path = Path(dataset_path)
        data_save = Path(save_directory)

        #cond to see if data_path is a file or not
        #cond to see if k <= 0, rasie error

        with data_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        data = data.get("rag_questions", data.get("question"))
        #learn this syntax

        result = []
        for q in tqdm.tqdm(data, desc="Searching Dataset"):
            res = self.search(q["question"], k)
            result.append(res)

        for q in result:
            print(type(q))
            print()
        a = StudentSearchResults(search_results=result, k=k)
        with open( save_directory, "w") as file:
            json.dump(a.model_dump(mode='json'), file, indent=4)
        
        print(type(a))
        print(a.search_results)
        print(a.k)


    def answer(self, query, k):
        chunks, search_result = self.search(query, k)

        context = "\n\n".join(
            f"source: {chunk['file_path']}\n"
            f"content: {chunk['text']}"
            for chunk in chunks
        )
        
        prompt = [
            {
                "role": "system",
                "content": (
                    "Answer using only the provided context. "
                    'If the context is insufficient, say "I don\'t know."'
                ),
            },
            {
                "role": "user",
                "content": (
                    f"<context>\n{context}\n</context>\n\n"
                    f"<question>\n{search_result.question}\n</question>"
                ),
            },
        ]

        


        generated_answer = self.model.generate(prompt)








def main() -> None:
    fire.Fire(RAG)

if __name__ == "__main__":
    main()

