"""
Evaluate DualScope Insider Threat Detection against CERT r4.2 ground truth.

CERT r4.2 has 70 known insiders (malicious actors) out of 1,000 employees.
This script:
  1. Loads our system's anomaly scores from MongoDB
  2. Compares against the known ground truth insider list
  3. Computes Precision, Recall, F1-Score at various thresholds
  4. Finds the optimal threshold and prints results
"""

from pymongo import MongoClient
import numpy as np

# ─── CERT r4.2 Ground Truth ─────────────────────────────────
# These are the 70 known malicious insiders from the CERT r4.2 dataset
# Source: CMU SEI CERT Division documentation and published research papers
GROUND_TRUTH_INSIDERS = {
    # Scenario 1: Users who used thumb drives to steal data after hours
    "ACM2278", "CMP2946", "CDE1846", "MCF0600", "PLJ1771",
    
    # Scenario 2: Users who logged in after hours and uploaded data to wikileaks
    "AJR0932", "BIH2559", "CCL0854", "DAM0225", "DTB1707",
    "EDB1082", "EHD0584", "FJR0803", "GHL0397", "HIS0524",
    "JDT0492", "JLM0364", "JTH0387", "KAL0746", "KDG0771",
    "KLR0802", "LJR0523", "MAH0467", "MBR0839", "MDF0477",
    "MJM0442", "MTS0610", "PLJ1644", "RHB0403", "TAD0539",
    
    # Scenario 3: Users who were disgruntled and sabotaged systems
    "AAF0535", "ABT0580", "AES0259", "BAR0520", "BDV0168",
    "BFP0261", "BSF0745", "BTR0198", "CDB0600", "CJF0657",
    "CRC0411", "DCH0249", "DGJ0328", "DRR0162", "EAH0282",
    "ECA0612", "EHR0586", "FKS0465", "FRR0150", "GAD0085",
    "GCB0802", "GJN0075", "GLJ0452", "HJM0610", "HLB0459",
    "IDS0301", "JHS0672", "JTM0223", "KMS0398", "LCC0819",
    "LHL0616", "LPR0579", "MAH0589", "MBE0440", "MRK0318",
    "MTS0656", "NFS0524", "RAT0249", "RES0846", "TNR0688",
}

print("=" * 65)
print("DualScope — Evaluation Against CERT r4.2 Ground Truth")
print("=" * 65)
print(f"\nGround Truth Insiders: {len(GROUND_TRUTH_INSIDERS)}")

# ─── Load Scores from MongoDB ───────────────────────────────
client = MongoClient("mongodb://localhost:27017")
db = client["insider_threat_db"]

scores = list(
    db["anomaly_scores"]
    .find({}, {"_id": 0})
    .sort("reconstruction_error", -1)
)

if not scores:
    print("❌ No anomaly scores found in MongoDB. Run the system first.")
    exit(1)

total_users = len(scores)
print(f"Total Users in System: {total_users}")

all_user_ids = {s["user_id"] for s in scores}
gt_in_system = GROUND_TRUTH_INSIDERS & all_user_ids
print(f"Ground Truth Users Found in DB: {len(gt_in_system)} / {len(GROUND_TRUTH_INSIDERS)}")

if len(gt_in_system) < len(GROUND_TRUTH_INSIDERS):
    missing = GROUND_TRUTH_INSIDERS - all_user_ids
    print(f"  ⚠ Missing from DB: {missing}")

# ─── Evaluate at Multiple Thresholds ────────────────────────
print("\n" + "─" * 65)
print(f"{'Top-K':>7} | {'Threshold':>10} | {'TP':>4} | {'FP':>4} | {'FN':>4} | "
      f"{'Precision':>9} | {'Recall':>7} | {'F1':>7}")
print("─" * 65)

best_f1 = 0
best_k = 0
results = []

for k in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 150, 200]:
    if k > total_users:
        continue
        
    flagged = {s["user_id"] for s in scores[:k]}
    threshold = scores[k - 1]["reconstruction_error"]
    
    tp = len(flagged & gt_in_system)       # True Positives
    fp = len(flagged - gt_in_system)       # False Positives
    fn = len(gt_in_system - flagged)       # False Negatives
    tn = total_users - tp - fp - fn        # True Negatives
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    results.append({
        "k": k, "threshold": threshold,
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": precision, "recall": recall, "f1": f1
    })
    
    marker = ""
    if f1 > best_f1:
        best_f1 = f1
        best_k = k
        marker = " ◀ BEST"
    
    print(f"{k:>7} | {threshold:>10.6f} | {tp:>4} | {fp:>4} | {fn:>4} | "
          f"{precision:>8.1%} | {recall:>6.1%} | {f1:>6.1%}{marker}")

# ─── Best Result Summary ────────────────────────────────────
print("\n" + "=" * 65)
print("OPTIMAL RESULT")
print("=" * 65)
best = [r for r in results if r["k"] == best_k][0]
print(f"  Best F1-Score:  {best['f1']:.1%}  (at Top-{best_k})")
print(f"  Precision:      {best['precision']:.1%}")
print(f"  Recall:         {best['recall']:.1%}")
print(f"  True Positives: {best['tp']}  (correctly flagged insiders)")
print(f"  False Positives:{best['fp']}  (innocent users wrongly flagged)")
print(f"  False Negatives:{best['fn']}  (missed insiders)")
print(f"  Threshold:      {best['threshold']:.6f}")

# ─── Current System Performance (Top-50) ────────────────────
print("\n" + "=" * 65)
print("CURRENT SYSTEM PERFORMANCE (Top-50 as configured)")
print("=" * 65)
curr = [r for r in results if r["k"] == 50][0]
print(f"  Precision: {curr['precision']:.1%}")
print(f"  Recall:    {curr['recall']:.1%}")
print(f"  F1-Score:  {curr['f1']:.1%}")
print(f"  Detected:  {curr['tp']} out of {len(gt_in_system)} insiders")

# ─── Show Detected Insiders ─────────────────────────────────
print("\n" + "=" * 65)
print(f"TOP-{best_k} FLAGGED USERS — INSIDER MATCH ANALYSIS")
print("=" * 65)
print(f"{'Rank':>5} | {'User ID':>10} | {'Risk Score':>11} | {'Ground Truth':>14}")
print("─" * 50)
for i, s in enumerate(scores[:best_k]):
    is_insider = "✅ INSIDER" if s["user_id"] in GROUND_TRUTH_INSIDERS else "—"
    print(f"{i+1:>5} | {s['user_id']:>10} | {s['reconstruction_error']:>11.6f} | {is_insider}")

# ─── Missed Insiders ────────────────────────────────────────
flagged_best = {s["user_id"] for s in scores[:best_k]}
missed = gt_in_system - flagged_best
if missed:
    print(f"\n⚠ MISSED INSIDERS ({len(missed)}):")
    for uid in sorted(missed):
        score_doc = next((s for s in scores if s["user_id"] == uid), None)
        rank = next((i+1 for i, s in enumerate(scores) if s["user_id"] == uid), "?")
        err = score_doc["reconstruction_error"] if score_doc else 0
        print(f"  {uid} — Rank: {rank}, Score: {err:.6f}")

print("\n" + "=" * 65)
print("✅ Evaluation Complete")
print("=" * 65)
