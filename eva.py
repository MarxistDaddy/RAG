
def evaluate(
    self,
    student_search_results_path: str,
    dataset_path: str,
):
    results_path = Path(student_search_results_path)
    dataset_path = Path(dataset_path)

    # 1. Validate file paths.
    if not results_path.is_file():
        raise FileNotFoundError(
            f"Search results not found: {results_path}"
        )

    if not dataset_path.is_file():
        raise FileNotFoundError(
            f"Ground-truth dataset not found: {dataset_path}"
        )

    # 2. Load the student's retrieval results.
    with results_path.open("r", encoding="utf-8") as f:
        student_data = StudentSearchResults.model_validate_json(
            f.read()
        )

    # 3. Load the ground-truth dataset.
    with dataset_path.open("r", encoding="utf-8") as f:
        ground_truth = RagDataset.model_validate_json(f.read())

    ks = [1, 3, 5, 10]

    if student_data.k < max(ks):
        raise ValueError(
            f"Results contain only k={student_data.k} sources. "
            "Run search_dataset with --k 10."
        )

    # 4. Match questions by their text.
    def normalize_question(text):
        return " ".join(text.lower().split())

    student_by_question = {
        normalize_question(item.question): item
        for item in student_data.search_results
    }

    # 5. Normalize paths so a leading ./ doesn't cause a mismatch.
    def normalize_path(path):
        return Path(path).as_posix().removeprefix("./")

    # 6. Determine whether two source spans overlap.
    def matches(retrieved, expected):
        same_file = (
            normalize_path(retrieved.file_path)
            == normalize_path(expected.file_path)
        )

        overlaps = (
            retrieved.first_character_index
            < expected.last_character_index
            and expected.first_character_index
            < retrieved.last_character_index
        )

        return same_file and overlaps

    # 7. Evaluate only questions with ground-truth sources.
    recall_totals = {k: 0.0 for k in ks}
    evaluated = 0
    missing = 0

    for question in ground_truth.rag_questions:
        # Unanswered questions have no reference sources.
        if not isinstance(question, AnsweredQuestion):
            continue

        expected_sources = question.sources

        if not expected_sources:
            continue

        evaluated += 1

        student_item = student_by_question.get(
            normalize_question(question.question)
        )

        # Missing retrieval results count as zero recall.
        if student_item is None:
            missing += 1
            continue

        for k in ks:
            top_k = student_item.retrieved_sources[:k]

            # Count each expected source at most once.
            hits = sum(
                any(matches(retrieved, expected) for retrieved in top_k)
                for expected in expected_sources
            )

            recall_totals[k] += hits / len(expected_sources)

    # 8. Report results.
    if evaluated == 0:
        raise ValueError(
            "No answered questions with reference sources were found. "
            "Check that you supplied the correct ground-truth dataset."
        )

    print(f"Evaluated questions: {evaluated}")
    print(f"Questions without search results: {missing}")

    metrics = {}

    for k in ks:
        recall = recall_totals[k] / evaluated
        metrics[f"recall@{k}"] = recall
        print(f"Recall@{k}: {recall:.3f} ({recall:.1%})")

    return metrics

