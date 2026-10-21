    def evaluate(self, student_search_results_path, dataset_path):
        # Load student retrieval results
        with open(student_search_results_path, "r", encoding="utf-8") as f:
            student_data = json.load(f)
    
        # Load ground-truth dataset
        with open(dataset_path, "r", encoding="utf-8") as f:
            dataset = json.load(f)
    
        student_results = student_data["search_results"]
        questions = dataset.get("rag_questions", dataset.get("question", dataset))
    
        # Match questions by their text
        def normalize(text):
            return " ".join(text.lower().split())
    
        results_by_question = {
            normalize(item["question"]): item
            for item in student_results
        }
    
        # Check if two source spans match
        def source_matches(retrieved, expected):
            if retrieved["file_path"] != expected["file_path"]:
                return False
    
            retrieved_start = retrieved["first_character_index"]
            retrieved_end = retrieved["last_character_index"]
            expected_start = expected["first_character_index"]
            expected_end = expected["last_character_index"]
    
            intersection = max(
                0,
                min(retrieved_end, expected_end)
                - max(retrieved_start, expected_start)
            )
    
            union = (
                (retrieved_end - retrieved_start)
                + (expected_end - expected_start)
                - intersection
            )
    
            if union <= 0:
                return False
    
            return intersection / union >= 0.05
    
        # Calculate Recall@k
        k_values = [1, 3, 5]
        recall_totals = {k: 0.0 for k in k_values}
        evaluated_questions = 0
    
        for question in questions:
            expected_sources = question.get("sources", [])
    
            if not expected_sources:
                continue
    
            key = normalize(question["question"])
            student_result = results_by_question.get(key)
    
            retrieved_sources = (
                student_result["retrieved_sources"]
                if student_result is not None
                else []
            )
    
            evaluated_questions += 1
    
            for k in k_values:
                top_k = retrieved_sources[:k]
                found = 0
    
                for expected in expected_sources:
                    if any(
                        source_matches(retrieved, expected)
                        for retrieved in top_k
                    ):
                        found += 1
    
                recall_totals[k] += found / len(expected_sources)
    
        if evaluated_questions == 0:
            raise ValueError("No questions with reference sources were found.")
    
        # Print and return average recall
        metrics = {}
    
        print(f"Evaluated questions: {evaluated_questions}")
    
        for k in k_values:
            recall = recall_totals[k] / evaluated_questions
            metrics[f"recall@{k}"] = recall
            print(f"Recall@{k}: {recall:.2%}")
    
        return metrics 

