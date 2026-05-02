import pandas as pd
import numpy as np

# Load
df = pd.read_excel('archive (3)/E Commerce Dataset.xlsx', sheet_name='E Comm')

with open('data_stats.txt', 'w') as f:
    f.write("=== DATASET INFO ===\n")
    df.info(buf=f)
    f.write("\n\n=== SUMMARY STATISTICS ===\n")
    f.write(df.describe().to_string())
    f.write("\n\n=== FIRST 5 ROWS ===\n")
    f.write(df.head().to_string())
    f.write("\n\n=== MISSING VALUES ===\n")
    f.write(df.isnull().sum().to_string())
    f.write("\n\n=== DUPLICATES ===\n")
    f.write(str(df.duplicated().sum()))

# Clean a bit to show "after" stats
df_clean = df.copy()
df_clean['PreferredLoginDevice'] = df_clean['PreferredLoginDevice'].str.strip().replace({'Mobile Phone': 'Mobile'})
df_clean['PreferredPaymentMode'] = df_clean['PreferredPaymentMode'].str.strip().replace({'COD': 'Cash on Delivery', 'CC': 'Credit Card'})
df_clean['PreferedOrderCat'] = df_clean['PreferedOrderCat'].str.strip().replace({'Mobile': 'Mobile Phone'})
num_cols_with_na = ['Tenure', 'WarehouseToHome', 'HourSpendOnApp', 'OrderAmountHikeFromlastYear', 'CouponUsed', 'OrderCount', 'DaySinceLastOrder']
for col in num_cols_with_na:
    df_clean[col] = df_clean[col].fillna(df_clean[col].median())
df_clean.drop_duplicates(inplace=True)

with open('data_stats_clean.txt', 'w') as f:
    f.write("=== CLEANED DATASET INFO ===\n")
    df_clean.info(buf=f)
    f.write("\n\n=== MISSING VALUES AFTER CLEANING ===\n")
    f.write(df_clean.isnull().sum().to_string())
    f.write("\n\n=== ROWS AFTER CLEANING ===\n")
    f.write(str(len(df_clean)))
