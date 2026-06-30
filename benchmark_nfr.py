"""
benchmark_nfr.py
================
Measures real performance numbers for Non-Functional Requirements.
Run this from the project folder:  python benchmark_nfr.py
Results are printed to terminal only — no files are written.
"""

import time
import os
import tracemalloc
import statistics

import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder
import json

SEP = "=" * 60

print(SEP)
print("  NFR BENCHMARK — E-Commerce Analytics Dashboard")
print(SEP)

# ─────────────────────────────────────────────────────────────
# 1. DATASET LOAD TIME
# ─────────────────────────────────────────────────────────────
print("\n[1] DATASET LOAD TIME")
print("-" * 40)

RUNS = 5
load_times = []

for i in range(RUNS):
    t0 = time.perf_counter()

    # Mirror exact fallback logic from dashboard.py
    data_path = os.path.join('archive (3)', 'E Commerce Dataset.xlsx')
    alt_path   = os.path.join('data', 'E_Commerce_Dataset.xlsx')

    if os.path.exists(data_path):
        df = pd.read_excel(data_path, sheet_name='E Comm')
        source = "Excel (archive folder)"
    elif os.path.exists(alt_path):
        df = pd.read_excel(alt_path, sheet_name='E Comm')
        source = "Excel (data folder)"
    elif os.path.exists('cleaned_ecommerce_dataset.csv'):
        df = pd.read_csv('cleaned_ecommerce_dataset.csv')
        source = "CSV (cleaned_ecommerce_dataset.csv)"
    else:
        print("  ERROR: No dataset file found. Aborting.")
        exit(1)

    elapsed = time.perf_counter() - t0
    load_times.append(elapsed)

avg_load = statistics.mean(load_times)
min_load = min(load_times)
max_load = max(load_times)

print(f"  Data source      : {source}")
print(f"  Rows loaded      : {len(df):,}")
print(f"  Columns          : {len(df.columns)}")
print(f"  Runs             : {RUNS}")
print(f"  Min load time    : {min_load:.3f} s")
print(f"  Max load time    : {max_load:.3f} s")
print(f"  Avg load time    : {avg_load:.3f} s  ← USE THIS FOR NFR")

# ─────────────────────────────────────────────────────────────
# 2. DATA CLEANING TIME (mirrors dashboard.py exactly)
# ─────────────────────────────────────────────────────────────
print("\n[2] DATA CLEANING TIME")
print("-" * 40)

clean_times = []
for _ in range(RUNS):
    df_raw = df.copy()
    t0 = time.perf_counter()

    df_raw['PreferredLoginDevice'] = df_raw['PreferredLoginDevice'].str.strip().replace({'Mobile Phone': 'Mobile'})
    df_raw['PreferredPaymentMode'] = df_raw['PreferredPaymentMode'].str.strip().replace({
        'COD': 'Cash on Delivery', 'CC': 'Credit Card'
    })
    df_raw['PreferedOrderCat'] = df_raw['PreferedOrderCat'].str.strip().replace({
        'Mobile': 'Mobile Phone', 'Mobile Phone': 'Mobile Phone'
    })
    num_cols_with_na = ['Tenure', 'WarehouseToHome', 'HourSpendOnApp',
                         'OrderAmountHikeFromlastYear', 'CouponUsed',
                         'OrderCount', 'DaySinceLastOrder']
    for col in num_cols_with_na:
        df_raw[col] = df_raw[col].fillna(df_raw[col].median())
    df_raw.drop_duplicates(inplace=True)
    df_raw.reset_index(drop=True, inplace=True)

    elapsed = time.perf_counter() - t0
    clean_times.append(elapsed)

df_clean = df_raw  # keep clean df for later steps
avg_clean = statistics.mean(clean_times)
print(f"  Avg cleaning time: {avg_clean:.3f} s")
print(f"  Total startup    : {avg_load + avg_clean:.3f} s  ← DATASET LOAD + CLEAN")

# ─────────────────────────────────────────────────────────────
# 3. MODEL (.pkl) LOAD TIME
# ─────────────────────────────────────────────────────────────
print("\n[3] MODEL FILE LOAD TIME (.pkl)")
print("-" * 40)

if not os.path.exists('best_model_gb.pkl') or not os.path.exists('scaler.pkl'):
    print("  ERROR: best_model_gb.pkl or scaler.pkl not found.")
    print("  Run  python phase2_ml.py  first.")
    exit(1)

pkl_times = []
for _ in range(RUNS):
    t0 = time.perf_counter()
    model  = joblib.load('best_model_gb.pkl')
    scaler = joblib.load('scaler.pkl')
    elapsed = time.perf_counter() - t0
    pkl_times.append(elapsed)

avg_pkl = statistics.mean(pkl_times)
print(f"  Avg model load time : {avg_pkl:.3f} s")

# ─────────────────────────────────────────────────────────────
# 4. SINGLE-ROW INFERENCE TIME (What-If Simulator)
# ─────────────────────────────────────────────────────────────
print("\n[4] SINGLE-CUSTOMER ML INFERENCE TIME")
print("-" * 40)

# Load feature columns list
with open('model_summary.json', 'r') as f:
    ms = json.load(f)
feature_cols = ms.get('feature_cols')
W_HOUR   = ms.get('engagement_weights', {}).get('HourSpendOnApp', 0.4)
W_ORDER  = ms.get('engagement_weights', {}).get('OrderCount', 0.3)
W_COUPON = ms.get('engagement_weights', {}).get('CouponUsed', 0.3)

# Prepare one sample row (average customer)
df_fe = df_clean.copy()
df_fe["CLV"]              = df_fe["CashbackAmount"] * df_fe["OrderCount"] * (df_fe["Tenure"] + 1)
df_fe["RecencyScore"]     = 1 / (df_fe["DaySinceLastOrder"] + 1)
df_fe["EngagementScore"]  = (df_fe["HourSpendOnApp"] * W_HOUR
                              + df_fe["OrderCount"] * W_ORDER
                              + df_fe["CouponUsed"] * W_COUPON)
df_fe["SpendingEfficiency"]   = df_fe["CashbackAmount"] / (df_fe["OrderCount"] + 1)
df_fe["HighRisk"]             = ((df_fe["Complain"] == 1) & (df_fe["Tenure"] < 3)).astype(int)
df_fe["AddressDiversityFlag"] = (df_fe["NumberOfAddress"] > 3).astype(int)

cat_cols = ["PreferredLoginDevice", "PreferredPaymentMode", "Gender", "PreferedOrderCat", "MaritalStatus"]
for col in cat_cols:
    le = LabelEncoder()
    df_fe[col] = le.fit_transform(df_fe[col].astype(str))

# Pick first customer row as sample
sample_row = df_fe[feature_cols].iloc[[0]]

infer_times = []
INFER_RUNS = 100  # more runs for stable inference timing
for _ in range(INFER_RUNS):
    t0 = time.perf_counter()
    X_scaled = scaler.transform(sample_row)
    prob = model.predict_proba(X_scaled)[:, 1][0] * 100
    elapsed = time.perf_counter() - t0
    infer_times.append(elapsed)

avg_infer = statistics.mean(infer_times)
max_infer = max(infer_times)
print(f"  Runs             : {INFER_RUNS}")
print(f"  Avg inference    : {avg_infer*1000:.2f} ms")
print(f"  Max inference    : {max_infer*1000:.2f} ms  ← WORST CASE")
print(f"  (Single customer churn probability: {prob:.2f}%)")

# ─────────────────────────────────────────────────────────────
# 5. BATCH INFERENCE TIME (Full dataset — 5,630 rows)
# ─────────────────────────────────────────────────────────────
print("\n[5] BATCH INFERENCE TIME (Full Dataset)")
print("-" * 40)

X_full = df_fe[feature_cols]
batch_times = []
for _ in range(RUNS):
    t0 = time.perf_counter()
    X_scaled_full = scaler.transform(X_full)
    probs = model.predict_proba(X_scaled_full)[:, 1]
    elapsed = time.perf_counter() - t0
    batch_times.append(elapsed)

avg_batch = statistics.mean(batch_times)
print(f"  Rows             : {len(X_full):,}")
print(f"  Avg batch time   : {avg_batch:.3f} s")

# ─────────────────────────────────────────────────────────────
# 6. MEMORY (RAM) USAGE
# ─────────────────────────────────────────────────────────────
print("\n[6] PEAK MEMORY USAGE")
print("-" * 40)

tracemalloc.start()

# Simulate full dashboard startup sequence
_df = df_clean.copy()
_df["CLV"]              = _df["CashbackAmount"] * _df["OrderCount"] * (_df["Tenure"] + 1)
_df["RecencyScore"]     = 1 / (_df["DaySinceLastOrder"] + 1)
_df["EngagementScore"]  = _df["HourSpendOnApp"] * W_HOUR + _df["OrderCount"] * W_ORDER + _df["CouponUsed"] * W_COUPON
_df["SpendingEfficiency"]   = _df["CashbackAmount"] / (_df["OrderCount"] + 1)
_df["HighRisk"]             = ((_df["Complain"] == 1) & (_df["Tenure"] < 3)).astype(int)
_df["AddressDiversityFlag"] = (_df["NumberOfAddress"] > 3).astype(int)
for col in cat_cols:
    le = LabelEncoder()
    _df[col] = le.fit_transform(_df[col].astype(str))
_X = scaler.transform(_df[feature_cols])
_probs = model.predict_proba(_X)[:, 1]

_, peak_bytes = tracemalloc.get_traced_memory()
tracemalloc.stop()

peak_mb = peak_bytes / (1024 * 1024)
print(f"  Peak RAM usage   : {peak_mb:.2f} MB  ← USE THIS FOR NFR")

# ─────────────────────────────────────────────────────────────
# 7. SUMMARY FOR NFR TABLE
# ─────────────────────────────────────────────────────────────
print()
print(SEP)
print("  SUMMARY — PASTE THESE INTO YOUR NFR TABLE")
print(SEP)
print(f"  Dataset load time    : {avg_load:.2f} s  (avg over {RUNS} runs)")
print(f"  Data cleaning time   : {avg_clean:.3f} s  (avg over {RUNS} runs)")
print(f"  Total startup time   : {avg_load + avg_clean:.2f} s  (load + clean)")
print(f"  Model (.pkl) load    : {avg_pkl:.3f} s  (avg over {RUNS} runs)")
print(f"  Single inference     : {avg_infer*1000:.2f} ms  (avg over {INFER_RUNS} runs)")
print(f"  Batch inference      : {avg_batch:.3f} s  (5,630 rows)")
print(f"  Peak RAM usage       : {peak_mb:.2f} MB")
print(SEP)
print()
