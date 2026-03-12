import ollama
r = ollama.generate(
    model="llama3.2:3b-instruct-q4_K_M",
    prompt="Reply with one sentence only: confirm you are operational."
)
print(r["response"])
