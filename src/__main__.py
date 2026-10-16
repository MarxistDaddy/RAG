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
    StudentSearchResultsAndAnswer,
    MinimalAnswer,
)


import json
import tqdm
from .utils import build_prompt



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
    

    def search_dataset(self, dataset_path: str, k: int, save_directory: str="data/output"):
        data_path = Path(dataset_path)
        save_directory = Path(save_directory)

        #cond to see if data_path is a file or not
        #cond to see if k <= 0, rasie error

        with data_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        data = data.get("rag_questions", data.get("question"))
        #learn this syntax

        result = []
        for q in tqdm.tqdm(data, desc="Searching Dataset"):
            chunks, res = self.search(q["question"], k)
            result.append(res)

        a = StudentSearchResults(search_results=result, k=k)
        
        save_directory.mkdir(parents=True, exist_ok=True)
        output_path = save_directory / (
            f"{data_path.stem}_search_results.json"
        )

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(a.model_dump(mode='json'), file, indent=4)
        



    def answer(self, query, k):
        chunks, search_result = self.search(query, k)
        prompt = build_prompt(chunks, search_result)
        #context = "\n\n".join(
        #    f"source: {chunk['file_path']}\n"
        #    f"content: {chunk['text']}"
        #    for chunk in chunks
        #)
        
        #prompt = [
        #    {
        #        "role": "system",
        #        "content": (
        #            "Answer using only the provided context. "
        #            'If the context is insufficient, say "I don\'t know."'
        #        ),
        #    },
        #    {
        #        "role": "user",
        #        "content": (
        #            f"<context>\n{context}\n</context>\n\n"
        #            f"<question>\n{search_result.question}\n</question>"
        #        ),
        #    },
        #]


        generated_answer = self.model.generate(prompt)

        result = MinimalAnswer(
            question_id=search_result.question_id,
            question=search_result.question,
            retrieved_sources=search_result.retrieved_sources,
            answer=generated_answer
        )


    def answer_dataset(self, student_search_results_path, save_directory="data/output"):
        input_path = Path(student_search_results_path)
        save_directory = Path(save_directory)

        #cond to see if input_file is a file!

        #upon opening the file, we need to check if the py_obj is the corerct one or not
        with input_path.open("r", encoding="utf-8") as f:
            data = StudentSearchResults.model_validate_json(f.read())

        results = []

        for item in tqdm.tqdm(data.search_results, desc="asnwering data set"):
            chunks = retrieve_chunks(item.question, data.k)
            prompt = build_prompt(chunks, item)

            #context = "\n\n".join(
            #        f"source: {chunk['file_path']}\n"
            #        f"content: {chunk['text']}\n"
            #        for chunk in chunks
            #    )

            #prompt = [
            #{
            #    "role": "system",
            #    "content": (
            #        "Answer using only the provided context. "
            #        'If the context is insufficient, say "I don\'t know."'
            #        ),
            #    },
            #    {
            #        "role": "user",
            #        "content": (
            #            f"<context>\n{context}\n</context>\n\n"
            #            f"<question>\n{item.question}\n</question>"
            #        ),
            #    },
            #]

            answer_text = self.model.generate(prompt)
            
            result = MinimalAnswer(
                question_id=item.question_id,
                question=item.question,
                retrieved_sources=item.retrieved_sources,
                answer=answer_text,
            )

            results.append(result)

        output = StudentSearchResultsAndAnswer(
            search_results=results,
            k=data.k
        )

        save_directory.mkdir(parents=True, exist_ok=True)
        output_path = save_directory/f"{input_path.stem}_answer.json"

        with output_path.open("w", encoding="utf-8") as f:
            f.write(output.model_dump_json(indent=4))

        print(f"saved_answer to: {output_path}")
        
        return output
        
        





def main() -> None:
    fire.Fire(RAG)

if __name__ == "__main__":
    main()

