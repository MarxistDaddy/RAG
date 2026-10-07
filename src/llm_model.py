from transformers import AutoTokenizer, AutoModelForCausalLM


class Model:
    def __init__(self, 
        model_name="Qwen/Qwen3-0.6b",
    ) -> None:
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)

    def generate(self, prompt: str) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt")


        outputs = self.model.generate(
                **inputs,
                max_new_tokens=1000,
            )

        print(outputs)        




















