import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ── Style ──────────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")
COLORS = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3"]
plt.rcParams.update({"figure.dpi": 150, "font.family": "DejaVu Sans"})

# ── Load Data ──────────────────────────────────────────────────────────────
df = pd.read_excel('archive (3)/E Commerce Dataset.xlsx', sheet_name='E Comm')
print(f"Dataset loaded: {df.shape[0]} rows × {df.shape[1]} columns")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: DATA CLEANING
# ═══════════════════════════════════════════════════════════════════════════

# 1a. Fix inconsistent categorical values
df['PreferredLoginDevice'] = df['PreferredLoginDevice'].str.strip().replace({'Mobile Phone': 'Mobile'})
df['PreferredPaymentMode'] = df['PreferredPaymentMode'].str.strip().replace({
    'COD': 'Cash on Delivery', 'CC': 'Credit Card'
})
df['PreferedOrderCat'] = df['PreferedOrderCat'].str.strip().replace({
    'Mobile': 'Mobile Phone', 'Mobile Phone': 'Mobile Phone'
})

# 1b. Impute missing numerical values with median (robust to outliers)
num_cols_with_na = ['Tenure', 'WarehouseToHome', 'HourSpendOnApp',
                     'OrderAmountHikeFromlastYear', 'CouponUsed',
                     'OrderCount', 'DaySinceLastOrder']
for col in num_cols_with_na:
    df[col] = df[col].fillna(df[col].median())

# 1c. Remove duplicates
df.drop_duplicates(inplace=True)

# 1d. Reset index
df.reset_index(drop=True, inplace=True)

print(f"After cleaning: {df.shape[0]} rows | Missing values: {df.isnull().sum().sum()}")

# Save cleaned dataset
df.to_csv('cleaned_ecommerce_dataset.csv', index=False)
print("Cleaned dataset saved.")

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 1: Overview Dashboard
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("Customer Behavior Analysis – Overview Dashboard", fontsize=18, fontweight='bold', y=1.01)

# 1. Churn Distribution
churn_counts = df['Churn'].value_counts()
axes[0,0].pie(churn_counts, labels=['Active','Churned'], autopct='%1.1f%%',
              colors=[COLORS[0], COLORS[3]], startangle=140,
              wedgeprops=dict(edgecolor='white', linewidth=2))
axes[0,0].set_title("Churn Distribution", fontsize=13, fontweight='bold')

# 2. Gender Distribution
gender_counts = df['Gender'].value_counts()
sns.barplot(x=gender_counts.index, y=gender_counts.values, ax=axes[0,1], palette=[COLORS[0], COLORS[1]])
axes[0,1].set_title("Gender Distribution", fontsize=13, fontweight='bold')
axes[0,1].set_xlabel("Gender"); axes[0,1].set_ylabel("Count")
for i, v in enumerate(gender_counts.values):
    axes[0,1].text(i, v + 30, str(v), ha='center', fontweight='bold')

# 3. Marital Status
ms = df['MaritalStatus'].value_counts()
sns.barplot(x=ms.index, y=ms.values, ax=axes[0,2], palette=COLORS[:3])
axes[0,2].set_title("Marital Status Distribution", fontsize=13, fontweight='bold')
axes[0,2].set_xlabel("Marital Status"); axes[0,2].set_ylabel("Count")

# 4. Tenure Distribution
sns.histplot(df['Tenure'], bins=25, kde=True, ax=axes[1,0], color=COLORS[0])
axes[1,0].set_title("Customer Tenure Distribution", fontsize=13, fontweight='bold')
axes[1,0].set_xlabel("Tenure (months)"); axes[1,0].set_ylabel("Count")
axes[1,0].axvline(df['Tenure'].median(), color='red', linestyle='--', label=f"Median: {df['Tenure'].median():.1f}")
axes[1,0].legend()

# 5. City Tier
ct = df['CityTier'].value_counts().sort_index()
sns.barplot(x=[f"Tier {i}" for i in ct.index], y=ct.values, ax=axes[1,1], palette=COLORS[:3])
axes[1,1].set_title("City Tier Distribution", fontsize=13, fontweight='bold')
axes[1,1].set_xlabel("City Tier"); axes[1,1].set_ylabel("Count")

# 6. Satisfaction Score
sc = df['SatisfactionScore'].value_counts().sort_index()
sns.barplot(x=sc.index, y=sc.values, ax=axes[1,2], palette=sns.color_palette("YlOrRd", len(sc)))
axes[1,2].set_title("Satisfaction Score Distribution", fontsize=13, fontweight='bold')
axes[1,2].set_xlabel("Score (1–5)"); axes[1,2].set_ylabel("Count")

plt.tight_layout()
plt.savefig('fig1_overview.png', bbox_inches='tight')
plt.close()
print("Figure 1 saved.")

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 2: Churn Analysis
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("Churn Analysis – Key Drivers", fontsize=18, fontweight='bold')

# 1. Churn by Gender
ct1 = pd.crosstab(df['Gender'], df['Churn'], normalize='index') * 100
ct1.plot(kind='bar', ax=axes[0,0], color=[COLORS[0], COLORS[3]], edgecolor='white')
axes[0,0].set_title("Churn Rate by Gender", fontsize=13, fontweight='bold')
axes[0,0].set_xlabel("Gender"); axes[0,0].set_ylabel("Percentage (%)")
axes[0,0].legend(['Active', 'Churned']); axes[0,0].tick_params(axis='x', rotation=0)

# 2. Churn by Marital Status
ct2 = pd.crosstab(df['MaritalStatus'], df['Churn'], normalize='index') * 100
ct2.plot(kind='bar', ax=axes[0,1], color=[COLORS[0], COLORS[3]], edgecolor='white')
axes[0,1].set_title("Churn Rate by Marital Status", fontsize=13, fontweight='bold')
axes[0,1].set_xlabel("Marital Status"); axes[0,1].set_ylabel("Percentage (%)")
axes[0,1].legend(['Active', 'Churned']); axes[0,1].tick_params(axis='x', rotation=0)

# 3. Churn by City Tier
ct3 = pd.crosstab(df['CityTier'], df['Churn'], normalize='index') * 100
ct3.plot(kind='bar', ax=axes[0,2], color=[COLORS[0], COLORS[3]], edgecolor='white')
axes[0,2].set_title("Churn Rate by City Tier", fontsize=13, fontweight='bold')
axes[0,2].set_xlabel("City Tier"); axes[0,2].set_ylabel("Percentage (%)")
axes[0,2].legend(['Active', 'Churned']); axes[0,2].tick_params(axis='x', rotation=0)

# 4. Tenure vs Churn
sns.boxplot(x='Churn', y='Tenure', data=df, ax=axes[1,0],
            palette=[COLORS[0], COLORS[3]])
axes[1,0].set_title("Tenure vs Churn", fontsize=13, fontweight='bold')
axes[1,0].set_xticklabels(['Active', 'Churned'])
axes[1,0].set_xlabel("Status"); axes[1,0].set_ylabel("Tenure (months)")

# 5. Satisfaction Score vs Churn
sns.boxplot(x='Churn', y='SatisfactionScore', data=df, ax=axes[1,1],
            palette=[COLORS[0], COLORS[3]])
axes[1,1].set_title("Satisfaction Score vs Churn", fontsize=13, fontweight='bold')
axes[1,1].set_xticklabels(['Active', 'Churned'])
axes[1,1].set_xlabel("Status"); axes[1,1].set_ylabel("Satisfaction Score")

# 6. Complain vs Churn
ct6 = pd.crosstab(df['Complain'], df['Churn'], normalize='index') * 100
ct6.plot(kind='bar', ax=axes[1,2], color=[COLORS[0], COLORS[3]], edgecolor='white')
axes[1,2].set_title("Churn Rate by Complaint Filed", fontsize=13, fontweight='bold')
axes[1,2].set_xlabel("Complain (0=No, 1=Yes)"); axes[1,2].set_ylabel("Percentage (%)")
axes[1,2].legend(['Active', 'Churned']); axes[1,2].tick_params(axis='x', rotation=0)

plt.tight_layout()
plt.savefig('fig2_churn.png', bbox_inches='tight')
plt.close()
print("Figure 2 saved.")

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 3: Behavioral Patterns
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("Customer Behavioral Patterns", fontsize=18, fontweight='bold')

# 1. Preferred Login Device
ld = df['PreferredLoginDevice'].value_counts()
axes[0,0].pie(ld, labels=ld.index, autopct='%1.1f%%', colors=COLORS,
              wedgeprops=dict(edgecolor='white', linewidth=2))
axes[0,0].set_title("Preferred Login Device", fontsize=13, fontweight='bold')

# 2. Preferred Payment Mode
pm = df['PreferredPaymentMode'].value_counts()
sns.barplot(y=pm.index, x=pm.values, ax=axes[0,1], palette=COLORS[:len(pm)])
axes[0,1].set_title("Preferred Payment Mode", fontsize=13, fontweight='bold')
axes[0,1].set_xlabel("Count"); axes[0,1].set_ylabel("")

# 3. Preferred Order Category
oc = df['PreferedOrderCat'].value_counts()
sns.barplot(y=oc.index, x=oc.values, ax=axes[0,2], palette=COLORS[:len(oc)])
axes[0,2].set_title("Preferred Order Category", fontsize=13, fontweight='bold')
axes[0,2].set_xlabel("Count"); axes[0,2].set_ylabel("")

# 4. Hours Spent on App
sns.histplot(df['HourSpendOnApp'], bins=20, kde=True, ax=axes[1,0], color=COLORS[2])
axes[1,0].set_title("Hours Spent on App", fontsize=13, fontweight='bold')
axes[1,0].set_xlabel("Hours"); axes[1,0].set_ylabel("Count")

# 5. Order Count Distribution
sns.histplot(df['OrderCount'], bins=20, kde=True, ax=axes[1,1], color=COLORS[1])
axes[1,1].set_title("Order Count Distribution", fontsize=13, fontweight='bold')
axes[1,1].set_xlabel("Number of Orders"); axes[1,1].set_ylabel("Count")

# 6. Cashback Amount Distribution
sns.histplot(df['CashbackAmount'], bins=30, kde=True, ax=axes[1,2], color=COLORS[4])
axes[1,2].set_title("Cashback Amount Distribution", fontsize=13, fontweight='bold')
axes[1,2].set_xlabel("Cashback Amount (₹)"); axes[1,2].set_ylabel("Count")

plt.tight_layout()
plt.savefig('fig3_behavior.png', bbox_inches='tight')
plt.close()
print("Figure 3 saved.")

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 4: Correlations & Relationships
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(18, 7))
fig.suptitle("Correlation & Relationship Analysis", fontsize=18, fontweight='bold')

# 1. Correlation Heatmap
num_cols = ['Churn','Tenure','WarehouseToHome','HourSpendOnApp',
            'NumberOfDeviceRegistered','SatisfactionScore','NumberOfAddress',
            'Complain','OrderAmountHikeFromlastYear','CouponUsed',
            'OrderCount','DaySinceLastOrder','CashbackAmount']
corr = df[num_cols].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap='coolwarm',
            ax=axes[0], linewidths=0.5, annot_kws={"size": 8},
            vmin=-1, vmax=1, center=0)
axes[0].set_title("Correlation Heatmap", fontsize=13, fontweight='bold')

# 2. Cashback vs Order Count (coloured by churn)
scatter = axes[1].scatter(df['OrderCount'], df['CashbackAmount'],
                           c=df['Churn'], cmap='coolwarm', alpha=0.4, s=20)
axes[1].set_title("Order Count vs Cashback Amount\n(Red = Churned)", fontsize=13, fontweight='bold')
axes[1].set_xlabel("Order Count"); axes[1].set_ylabel("Cashback Amount (₹)")
plt.colorbar(scatter, ax=axes[1], label='Churn (1=Yes)')

plt.tight_layout()
plt.savefig('fig4_correlation.png', bbox_inches='tight')
plt.close()
print("Figure 4 saved.")

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 5: High-Value Customer Segmentation
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle("Customer Segmentation & Value Analysis", fontsize=18, fontweight='bold')

# Segment customers by cashback quartile
df['CustomerSegment'] = pd.qcut(df['CashbackAmount'], q=4,
                                 labels=['Low Value', 'Mid Value', 'High Value', 'Premium'])

# 1. Segment size
seg = df['CustomerSegment'].value_counts()
sns.barplot(x=seg.index, y=seg.values, ax=axes[0], palette=COLORS[:4])
axes[0].set_title("Customer Segment Sizes", fontsize=13, fontweight='bold')
axes[0].set_xlabel("Segment"); axes[0].set_ylabel("Count")
axes[0].tick_params(axis='x', rotation=15)

# 2. Churn rate per segment
churn_seg = df.groupby('CustomerSegment')['Churn'].mean() * 100
sns.barplot(x=churn_seg.index, y=churn_seg.values, ax=axes[1], palette=COLORS[:4])
axes[1].set_title("Churn Rate by Customer Segment", fontsize=13, fontweight='bold')
axes[1].set_xlabel("Segment"); axes[1].set_ylabel("Churn Rate (%)")
axes[1].tick_params(axis='x', rotation=15)
for i, v in enumerate(churn_seg.values):
    axes[1].text(i, v + 0.3, f"{v:.1f}%", ha='center', fontweight='bold')

# 3. Avg Order Count per Segment
avg_ord = df.groupby('CustomerSegment')['OrderCount'].mean()
sns.barplot(x=avg_ord.index, y=avg_ord.values, ax=axes[2], palette=COLORS[:4])
axes[2].set_title("Avg Order Count by Segment", fontsize=13, fontweight='bold')
axes[2].set_xlabel("Segment"); axes[2].set_ylabel("Avg Order Count")
axes[2].tick_params(axis='x', rotation=15)

plt.tight_layout()
plt.savefig('fig5_segmentation.png', bbox_inches='tight')
plt.close()
print("Figure 5 saved.")

# ═══════════════════════════════════════════════════════════════════════════
# Print Summary Stats for Report
# ═══════════════════════════════════════════════════════════════════════════
print("\n=== KEY STATS ===")
print(f"Total Customers: {len(df)}")
print(f"Churn Rate: {df['Churn'].mean()*100:.2f}%")
print(f"Avg Tenure: {df['Tenure'].mean():.2f} months")
print(f"Avg Satisfaction: {df['SatisfactionScore'].mean():.2f}/5")
print(f"Avg Cashback: Rs. {df['CashbackAmount'].mean():.2f}")
print(f"Avg Order Count: {df['OrderCount'].mean():.2f}")
print(f"Customers who complained: {df['Complain'].sum()} ({df['Complain'].mean()*100:.1f}%)")
print(f"\nChurn by complain:\n{df.groupby('Complain')['Churn'].mean()*100}")
print(f"\nTop Login Device: {df['PreferredLoginDevice'].mode()[0]}")
print(f"Top Payment Mode: {df['PreferredPaymentMode'].mode()[0]}")
print(f"Top Order Category: {df['PreferedOrderCat'].mode()[0]}")
