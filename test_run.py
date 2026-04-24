import csv
from pathlib import Path
import ollama
print("Hello from CHANDU Lab!")
csv_path = Path("datasets/cognitive_benchmark/dataset.csv")
print("Loading dataset from:", csv_path.resolve())
if not csv_path.exists():
    raise SystemExit("dataset.csv not found at this path.")
with csv_path.open(newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
print(f"Total tasks: {len(rows)}\n")
def query_model(prompt: str) -> str:
    response = ollama.chat(
        model="qwen3:14b",  # or "llama3", "gemma3:4b", etc.
        messages=[
            {"role": "system", "content": "Answer ONLY the final result, no explanation."},
            {"role": "user", "content": prompt},
        ],
    )
    return response["message"]["content"].strip()
correct = 0
for i, row in enumerate(rows, start=1):
    prompt = row["prompt"]
    gold = row["correct_answer"].strip()

    print(f"\n=== Task {i} ===")
    print(prompt)

    model_output = query_model(prompt)
    print("Model output:", model_output)
    print("Gold answer :", gold)

    if model_output == gold:
        print("✅ Correct")
        correct += 1
    else:
        print("❌ Wrong")
accuracy = correct / len(rows)
print(f"\nFinal accuracy: {accuracy:.3f} ({correct}/{len(rows)})")