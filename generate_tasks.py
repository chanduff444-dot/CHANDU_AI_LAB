import csv
from pathlib import Path

csv_path = Path("datasets/cognitive_benchmark/dataset.csv")

# ---------- 1. Load existing tasks ----------
with csv_path.open(newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    existing = list(reader)

next_id = max(int(row["id"]) for row in existing) + 1

rows = existing[:]  # start with current 12

# ---------- 2. Helper functions ----------

def make_prompt(pairs, query):
    lines = ["Learn the pattern from the examples and answer the question.", ""]
    for a, b in pairs:
        lines.append(f"{a} -> {b}")
    lines.append(f"{query} -> ?")
    lines.append("")
    lines.append("Answer only the result.")
    return "\n".join(lines)

def add_row(prompt, answer, rule_type, difficulty, input_length):
    global next_id
    rows.append({
        "id": str(next_id),
        "prompt": prompt,
        "correct_answer": answer,
        "rule_type": rule_type,
        "difficulty": difficulty,
        "input_length": str(input_length),
    })
    next_id += 1

# ---------- 3. Reverse tasks ----------

reverse_words_easy = ["BIRD", "MILK", "STAR", "LAKE"]
reverse_words_medium = ["WINDOW", "MARKET", "GARDEN", "PLANET"]

# easy reverse (4 new)
for w in reverse_words_easy:
    ex1 = ("DOG", "GOD")
    ex2 = ("CAT", "TAC")
    pairs = [ex1, ex2]
    prompt = make_prompt(pairs, w)
    answer = w[::-1]
    add_row(prompt, answer, "reverse", "easy", len(w))

# medium reverse (4 new)
for w in reverse_words_medium:
    ex1 = ("HOUSE", "ESOUH")
    ex2 = ("WATER", "RETAW")
    pairs = [ex1, ex2]
    prompt = make_prompt(pairs, w)
    answer = w[::-1]
    add_row(prompt, answer, "reverse", "medium", len(w))

# ---------- 4. Shift +1 tasks ----------

shift_words_easy = ["DOG", "SUN", "MAP", "RAT"]       # length 3
shift_words_medium = ["HOME", "CLOUD", "RAIN", "FARM"]  # length 4–5

def shift_plus1(s):
    out = []
    for ch in s:
        if "A" <= ch <= "Y":
            out.append(chr(ord(ch) + 1))
        elif ch == "Z":
            out.append("A")   # wrap
        else:
            out.append(ch)
    return "".join(out)

# easy shift
for w in shift_words_easy:
    ex1 = ("CAT", shift_plus1("CAT"))
    ex2 = ("FAN", shift_plus1("FAN"))
    pairs = [ex1, ex2]
    prompt = make_prompt(pairs, w)
    answer = shift_plus1(w)
    add_row(prompt, answer, "shift_plus_1", "easy", len(w))

# medium shift
for w in shift_words_medium:
    ex1 = ("NOTE", shift_plus1("NOTE"))
    ex2 = ("GAME", shift_plus1("GAME"))
    pairs = [ex1, ex2]
    prompt = make_prompt(pairs, w)
    answer = shift_plus1(w)
    add_row(prompt, answer, "shift_plus_1", "medium", len(w))

# ---------- 5. Mirror digits tasks ----------

digit_strings_easy = ["789", "246", "135", "980"]
digit_strings_medium = ["1203", "6789", "4501", "9320"]

# easy digits
for s in digit_strings_easy:
    ex1 = ("12", "21")
    ex2 = ("345", "543")
    pairs = [ex1, ex2]
    prompt = make_prompt(pairs, s)
    answer = s[::-1]
    add_row(prompt, answer, "mirror_digits", "easy", len(s))

# medium digits
for s in digit_strings_medium:
    ex1 = ("1024", "4201")
    ex2 = ("3567", "7653")
    pairs = [ex1, ex2]
    prompt = make_prompt(pairs, s)
    answer = s[::-1]
    add_row(prompt, answer, "mirror_digits", "medium", len(s))

# ---------- 6. Save back to CSV ----------

with csv_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["id", "prompt", "correct_answer", "rule_type", "difficulty", "input_length"],
    )
    writer.writeheader()
    writer.writerows(rows)

print(f"Expanded dataset written to {csv_path} with {len(rows)} tasks.")