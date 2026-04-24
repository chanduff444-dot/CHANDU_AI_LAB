from datasets import load_dataset
import pandas as pd

# Load dataset
dataset = load_dataset("emotion")

df = pd.DataFrame(dataset["train"])

# Label mapping
label_map = {
    0: "sadness",
    1: "joy",
    2: "love",
    3: "anger",
    4: "fear",
    5: "surprise"
}

df["emotion"] = df["label"].map(label_map)

# Remove original numeric label
df = df.drop(columns=["label"])

print("First 5 Cleaned Samples:")
print(df.head())

# Text length analysis
df["text_length"] = df["text"].apply(lambda x: len(x.split()))

print("\nText Length Statistics:")
print(df["text_length"].describe())

print("\nEmotion Distribution:")
print(df["emotion"].value_counts())

# Save cleaned dataset
df.to_csv("neuralmigrane_cleaned.csv", index=False)

print("\nCleaned dataset saved as neuralmigrane_cleaned.csv")
