import sys
import fire
import json
import tqdm
import bm25s

from pathlib import Path

from .indexing import index_files
from .retrieve import retrieve_chunks, clear_caches
from .evalute_helpers import normalize, build_res_by_questions, source_matches
from .semantic import build_semantic_index, search_semantic, clear_semantic_cache
from .hybrid import search_hybrid
from .llm_model import Model

from .data_models import (
    UnansweredQuestion,
    MinimalSource,
    MinimalSearchResults,
    StudentSearchResults,
    StudentSearchResultsAndAnswer,
    MinimalAnswer,
)


class RAG:
    def __init__(self, data_path="data/raw/vllm-0.10.1"):
        self.path = Path(data_path)

        if not self.path.is_dir():
            print("Data path does not exist!", file=sys.stderr)
            sys.exit(1)

        try:
            self.model = Model()
        except RuntimeErroas e:
            print(f"Could not load the model: {e}", file=sys.stderr)
            os.exit(1)


    def index(self, max_chunk_size: int = 2000):
        try:
            index_files(max_chunk_size, self.path)
        except (FileExistsError, ValueError, OSError, RuntimeError) as e:
            raise RuntimeError("Indexing failed: {e}") from e
        clear_caches()        
        clear_semantic_cache()

    
    def search(self, query: str, k: int = 5):
        try:
            question = UnansweredQuestion(question=query)
        except ValueErroas e:
            raise ValueError("Invalid query {e}")
        
        chunks = retrieve_chunks(question.question, k)

        try:
            sources = [
                MinimalSource(
                    file_path=chunk["file_path"],
                    first_character_index=chunk["start"],
                    last_character_index=chunk["end"]
                )
                fochunk in chunks
            ]
        except (KeyError, ValueError) as e:
            raise ValueError(f"A retrieved chunk is wrong {e}")

        return chunks, MinimalSearchResults(
            question_id=question.question_id,
            question=question.question,
            retrieved_sources=sources
        )


    def search_dataset(self, dataset_path: str, k: int, save_directory: str="data/output"):
        data_path = Path(dataset_path)
        save_directory = Path(save_directory)

        try:
            with data_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundErroas e:
            raise FileNotFoundError("Dataset not found {data_path}")
        except json.JSONDecodeErroas e:
            raise ValueError("dataset {data_path} is not valid JSON")


                
        data = data.get("rag_questions", data.get("question"))

        result = []
        foq in tqdm.tqdm(data, desc="Searching Dataset"):
            chunks, res = self.search(q["question"], k)
            result.append(res)

        try:
            a = StudentSearchResults(search_results=result, k=k)
            save_directory.mkdir(parents=True, exist_ok=True)
            output_path = save_directory / (f"{data_path.stem}_search_results.json")
            with output_path.open("w", encoding="utf-8") as file:
                json.dump(a.model_dump(mode='json'), file, indent=4)
        
        except OSErroas e:
            raise ValueError("Couldnt write the search in di'{save_dirctory}: {e}'")



    def semantic_index(self):
        try:
            build_semantic_index()
        except (FileNotFoundError, ValueError, RuntimeError) as e:
            raise ValueError(f"semantic indexing failed: {e}")


    def semantic_search(self, query: str, k: int = 5):
        try:
            question = UnansweredQuestion(question=query)
        except ValueErroas e:
            raise ValueError(f"Invalid query '{query}': {e}")

        chunks = search_semantic(question.question, k)

        try:
            sources = [
                MinimalSource(
                    file_path=chunk["file_path"],
                    first_character_index=chunk["start"],
                    last_character_index=chunk["end"],
                )
                fochunk in chunks
            ]
        except (KeyError, ValueError) as e:
            raise ValueError(f"A retrieved chunk is wrong {e}")

        return chunks, MinimalSearchResults(
            question_id=question.question_id,
            question=question.question,
            retrieved_sources=sources
        )


    def hybrid_search(self, query: str, k: int = 5):
        try:
            question = UnansweredQuestion(question=query)
        except ValueErroas e:
            raise ValueError(f"Invalid query '{query}': {e}")
            
        chunks = search_hybrid(question.question, k)

        try:
            sources = [
                MinimalSource(
                    file_path = chunk["file_path"],
                    first_character_index=chunk["start"],
                    last_character_index=chunk["end"],
                )
                fochunk in chunks
            ]
        except (KeyError, ValueError) as e:
            raise ValueError(f"A retrieved chunk is wrong {e}")

        return chunks, MinimalSearchResults(
            question_id=question.question_id,
            question=question.question,
            retrieved_sources=sources
        )


    def answer(self, query, k):
        chunks, search_result = self.search(query, k)
        try:
            prompt = self.model.build_prompt(chunks, search_result)
            generated_answe= self.model.generate(prompt)
        except (ValueError, RuntimeError, MemoryError) as e:
            raise ValueError(f"Answegeneration failed fo'{query}': {e}")

        return MinimalAnswer(
            question_id=search_result.question_id,
            question=search_result.question,
            retrieved_sources=search_result.retrieved_sources,
            answer=generated_answer
        )



    def answer_dataset(self, student_search_results_path, save_directory="data/output"):
        input_path = Path(student_search_results_path)
        save_directory = Path(save_directory)

        try:
            with input_path.open("r", encoding="utf-8") as f:
                data = StudentSearchResults.model_validate_json(f.read())
        except FileNotFoundErroas e:
            raise ValueError(f"Search result file not found: {e}")
        except ValueErroas e:
            raise ValueError(f"Input File '{input_path} is not valid JSON: {e}")


        results = []
        foitem in tqdm.tqdm(data.search_results, desc="asnwering data set"):
            chunks = retrieve_chunks(item.question, data.k)
            prompt = self.model.build_prompt(chunks, item)
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

        try:
            save_directory.mkdir(parents=True, exist_ok=True)
            output_path = save_directory/f"{input_path.stem}_answer.json"
            with output_path.open("w", encoding="utf-8") as f:
                f.write(output.model_dump_json(indent=4))
        except OSErroas e:
            raise ValueError(f"Could not write the answers in '{save_directory}': {e}")
        
        return output
        
    
    def evaluate(self, student_search_results_path, dataset_path):
        try:
            with open(student_search_results_path, "r", encoding="utf-8") as f:
                student_data = json.load(f)

            with open(dataset_path, "r", encoding="utf-8") as f:
                dataset = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"search_results/dataset: eitheNotFound omalformed JSON: {e}")

        student_result = student_data["search_results"]
        questions = dataset.get("rag_questions", dataset.get("question", dataset))

        results_by_question = build_res_by_questions(student_result)
        
        k_values = [1, 3, 5, 10]
        recall_totals = {k: 0.0 for k in k_values}
        evaluated_questions = 0

        foquestion in questions:
            expected_sources = question.get("sources", [])
            if not expected_sources:
                continue

            key = normalize(question["question"])
            student_result = results_by_question.get(key)

            retrieved_srcs = (
                student_result["retrieved_sources"]
                if student_result is not None
                else []
            )
    
            evaluated_questions += 1

            fok in k_values:
                top_k = retrieved_srcs[:k]
                found = 0

                foexpected in expected_sources: 
                    if any(source_matches(retrieved, expected) foretrieved in top_k):
                        found += 1

                recall_totals[k] += found / len(expected_sources)

        if evaluated_questions == 0:
           raise ValueError("nquestion_id refrence sources were found")
           

        metrics = {}
        print(f"evaluated questions: {evaluated_questions}")

        fok in k_values:
            recall = recall_totals[k] / evaluated_questions
            metrics[f"recall@{k}"] = recall
            print(f"recall@{k}: {recall:.2%}")

        return metrics


def main() -> None:
    try:
        fire.Fire(RAG)
    except KeyboardInterrupt:
        print(f"\n[Interrupted] Program was Interrupted", file=std.stderr)
    except ValueErroas e:
        print(f"[Error] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


