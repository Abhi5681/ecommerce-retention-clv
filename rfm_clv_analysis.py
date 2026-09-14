import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 1. Load & clean data
data_file = "ecommerce_transactions.csv"
if not os.path.exists(data_file):
    import sys
    sys.exit("Please run generate_data.py first to generate the dataset!")

df = pd.read_csv(data_file)
df["invoice_date"] = pd.to_datetime(df["invoice_date"])
df["line_total"] = df["quantity"] * df["unit_price"]

# 2. RFM Calculation
snapshot_date = df["invoice_date"].max() + pd.Timedelta(days=1)

rfm = df.groupby("customer_id").agg({
    "invoice_date": lambda x: (snapshot_date - x.max()).days,
    "invoice_id": "nunique",
    "line_total": "sum"
}).rename(columns={
    "invoice_date": "Recency",
    "invoice_id": "Frequency",
    "line_total": "Monetary"
})

# 3. RFM Scoring (1-4 quantiles; 4 is highest performance)
rfm["R_Score"] = pd.qcut(rfm["Recency"], 4, labels=[4, 3, 2, 1]).astype(int)
rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
rfm["M_Score"] = pd.qcut(rfm["Monetary"], 4, labels=[1, 2, 3, 4]).astype(int)
rfm["RFM_Score"] = rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)

# 4. Actionable Customer Tier Mapping
def assign_segment(row):
    r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]
    if r >= 3 and f >= 3 and m >= 3:
        return "Champions"
    elif r >= 3 and f >= 2:
        return "Loyal Customers"
    elif r >= 3 and f == 1:
        return "Recent Inactive / New"
    elif r == 2 and f >= 2:
        return "Needs Attention"
    elif r <= 2 and f >= 3:
        return "At Risk"
    else:
        return "Hibernating"

rfm["Segment"] = rfm.apply(assign_segment, axis=1)

# 5. Cohort Heatmap Preparation
df["OrderMonth"] = df["invoice_date"].dt.to_period("M")
df["CohortMonth"] = df.groupby("customer_id")["OrderMonth"].transform("min")

def get_cohort_index(df):
    year_diff = df["OrderMonth"].dt.year - df["CohortMonth"].dt.year
    month_diff = df["OrderMonth"].dt.month - df["CohortMonth"].dt.month
    return year_diff * 12 + month_diff

df["CohortIndex"] = get_cohort_index(df)

cohort_data = df.groupby(["CohortMonth", "CohortIndex"])["customer_id"].nunique().reset_index()
cohort_counts = cohort_data.pivot(index="CohortMonth", columns="CohortIndex", values="customer_id")
cohort_sizes = cohort_counts.iloc[:, 0]
retention_matrix = cohort_counts.divide(cohort_sizes, axis=0) * 100

# 6. Visualizations
fig, axes = plt.subplots(1, 2, figsize=(18, 7))

# Heatmap
sns.heatmap(
    retention_matrix.iloc[:12, :12], 
    annot=True, 
    fmt=".1f", 
    cmap="YlGnBu", 
    ax=axes[0], 
    cbar_kws={'label': 'Retention Rate (%)'}
)
axes[0].set_title("Cohort Monthly Retention Matrix (First 12 Cohorts)", fontsize=13, pad=12)
axes[0].set_xlabel("Cohort Index (Months Since First Order)")
axes[0].set_ylabel("Acquisition Cohort")

# RFM Segment Breakdown
segment_summary = rfm.groupby("Segment").agg(
    customer_count=("Recency", "count"),
    avg_monetary=("Monetary", "mean")
).reset_index().sort_values("customer_count", ascending=False)

sns.barplot(
    data=segment_summary, 
    x="customer_count", 
    y="Segment", 
    palette="Blues_r", 
    ax=axes[1]
)
axes[1].set_title("Customer Segmentation Distribution", fontsize=13, pad=12)
axes[1].set_xlabel("Number of Customers")
axes[1].set_ylabel("")

plt.tight_layout()
plt.savefig("retention_rfm_summary.png", dpi=300)
print("Saved summary visualization to retention_rfm_summary.png")

# Export segmented customer list
rfm.to_csv("customer_rfm_segments.csv")
print("Saved customer RFM segments to customer_rfm_segments.csv")
