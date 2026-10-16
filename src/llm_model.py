from transformers import AutoTokenizer, AutoModelForCausalLM


class Model:
    def __init__(
        self,
        model_name="Qwen/Qwen3-0.6B",
    ) -> None:
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)


    def build_prompt(self, chunks, obj):
        #cond to check the correct obj
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
   

    def generate(self, messages: list[dict]) -> str:
        inputs = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
            enable_thinking=False,
        )

    
        input_ids = inputs["input_ids"]
    
        outputs = self.model.generate(
            input_ids=input_ids,
            max_new_tokens=200,
            do_sample=False,
            eos_token_id=self.tokenizer.eos_token_id,
        )
    
        input_length = input_ids.shape[1]
    
        generated_tokens = outputs[0][input_length:]
    
        return self.tokenizer.decode(
            generated_tokens,
            skip_special_tokens=True,
        )

