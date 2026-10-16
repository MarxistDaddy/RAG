

def build_prompt(chunks, obj):
    
    context = "\n\n".join(
        f"source: {chunk['file_path']}\n"
        f"content: {chunk['text']}\n"
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
                f"<question>\n{obj.question}\n</question>"
            ),
        },
    ]
        

    return prompt









