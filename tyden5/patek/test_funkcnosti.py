from litellm import completion

response = completion(
  model="ollama/ministral-3:3b",
  messages=[{"role": "user", "content": "Hello, how are you?"}],
  api_base="http://localhost:11434"
)
print(response)
