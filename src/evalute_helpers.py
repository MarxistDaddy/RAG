import typing



def normalize(question: str):
    return " ".join(question.lower().split())


def build_res_by_questions(student_results):
    return {
        normalize(item["question"]): item
        for item in student_results
    }


def source_matches(retrieved, answered):
    if retrieved["file_path"] != answered["file_path"]:
        return False


    retrieved_start = retrieved["first_character_index"]
    retrieved_end = retrieved["last_character_index"]
    
    answered_start = answered["first_character_index"]
    answered_end = answered["last_character_index"]
    

    intersection =  max(
        0, 
        min(retrieved_end, answered_end)
        - max(retrieved_start, answered_start)
    )

    union = (
        (retrieved_end - retrieved_start)
        + (answered_end - answered_start)
        - intersection
    )

    if union <= 0:
        return False

    return intersection / union >= 0.05



