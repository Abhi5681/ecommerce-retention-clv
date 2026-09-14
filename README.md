# E-Commerce Customer Lifetime Value (CLV) & Cohort Retention Analysis

A comprehensive analytics project identifying repeat purchase patterns, retention decay, and high-value customer segments using SQL CTEs and Python RFM modeling.

## Project Overview

In transactional e-commerce, retaining existing customers is substantially cheaper than net-new acquisition. This project addresses two operational problems:
1. **Retention Degradation:** Pinpointing the exact drop-off period after initial conversion.
2. **Customer Segmentation:** Classifying users into actionable value tiers based on transaction velocity and monetary impact.

## Key Metrics & Methodology

* **Cohort Retention Matrix:** Modeled using SQL window functions across monthly acquisition cohorts, tracking decay rates across a 12-month lifecycle window.
* **RFM Segmentation:**
  * **Recency ($R$):** Days elapsed since the customer's last order.
  * **Frequency ($F$):** Total unique orders placed.
  * **Monetary ($M$):** Aggregate net spend.
* Customers were scored on quartile distributions ($1-4$) and grouped into 6 strategic segments: *Champions*, *Loyal Customers*, *Recent Inactive*, *Needs Attention*, *At Risk*, and *Hibernating*.

## Repository Layout

```text
ecommerce-retention-clv/
├── README.md
├── requirements.txt
├── .gitignore
├── generate_data.py
├── sql/
│   └── cohort_retention.sql
└── notebooks/
    └── rfm_clv_analysis.py
```

* `generate_data.py`: Synthesizes 50,000 multi-market transaction rows with real-world distributions.
* `sql/cohort_retention.sql`: Standalone, production-ready PostgreSQL query outputting cohort size, indices, and percentage retention.
* `notebooks/rfm_clv_analysis.py`: End-to-end Python pipeline computing RFM scores, segment assignments, and Seaborn heatmaps.

## Setup & Execution

1. **Clone the repository:**
   ```bash
   git clone https://github.com/<your-username>/ecommerce-retention-clv.git
   cd ecommerce-retention-clv
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate transactions and run analysis:**
   ```bash
   python generate_data.py
   python notebooks/rfm_clv_analysis.py
   ```

## Key Findings & Business Recommendations

* **Month 2 Churn Cliff:** Average retention drops significantly by Month 2 across all cohorts, suggesting that automated email re-engagement flows must fire within **day 14 to day 21** post-first purchase.
* **Segment Re-allocation:** The "At-Risk" cohort (high monetary history, high recency gap) accounts for a large portion of past revenue. Prioritize SMS win-back campaigns and personalized discount codes for this group.
