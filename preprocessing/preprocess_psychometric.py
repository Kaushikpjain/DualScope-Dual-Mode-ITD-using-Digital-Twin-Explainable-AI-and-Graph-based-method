import pandas as pd
import os

# -------------------------------
# Paths (robust)
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT = os.path.join(BASE_DIR, "dataset", "psychometric.csv")
OUTPUT = os.path.join(BASE_DIR, "processed_data", "psychometric_clean.csv")

print("Loading psychometric data...")

# -------------------------------
# Load
# -------------------------------
df = pd.read_csv(INPUT)

# -------------------------------
# Rename for consistency
# -------------------------------
df.rename(columns={"user": "user_id"}, inplace=True)

# -------------------------------
# Keep only required columns
# -------------------------------
required_cols = ["user_id", "O", "C", "E", "A", "N"]
df = df[required_cols]

# -------------------------------
# Convert traits to numeric
# -------------------------------
traits = ["O", "C", "E", "A", "N"]
for col in traits:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# -------------------------------
# Drop invalid rows
# -------------------------------
df.dropna(inplace=True)

# -------------------------------
# Standardize (Z-score)
# -------------------------------
for col in traits:
    df[col] = (df[col] - df[col].mean()) / df[col].std()

# -------------------------------
# Save
# -------------------------------
df.to_csv(OUTPUT, index=False)

print("✅ Psychometric preprocessing complete")
print(f"📄 Saved to: {OUTPUT}")
