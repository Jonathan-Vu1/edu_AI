from transformers import pipeline
import os

generate_text = pipeline(
    model="fbellame/llama2-pdf-to-quizz-13b",
    torch_dtype="auto",
    trust_remote_code=True,
    use_fast=True,
    device_map={"": "cuda:0"},
    token= os.getenv("OPENAI_API_KEY"),
)

res = generate_text(
    "Why is drinking water so healthy?",
    min_new_tokens=2,
    max_new_tokens=256,
    do_sample=False,
    num_beams=1,
    temperature=float(0.3),
    repetition_penalty=float(1.2),
    renormalize_logits=True
)
print(res[0]["generated_text"])


