import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

n_customers = 2500
n_transactions = 50000

customer_ids = [f"CUST-{i:05d}" for i in range(1, n_customers + 1)]
start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 12, 31)
date_range_days = (end_date - start_date).days

# Assign base acquisition dates to simulate cohorts
customer_acquisition = {
    cid: start_date + timedelta(days=int(np.random.beta(2, 5) * date_range_days))
    for cid in customer_ids
}

records = []
countries = ["United Kingdom", "Germany", "France", "United States", "Spain"]
country_weights = [0.65, 0.12, 0.10, 0.08, 0.05]

for i in range(1, n_transactions + 1):
    cid = np.random.choice(customer_ids)
    acq_date = customer_acquisition[cid]
    days_since_acq = int(np.random.exponential(scale=110))
    tx_date = acq_date + timedelta(days=days_since_acq)
    
    if tx_date > end_date:
        tx_date = end_date - timedelta(days=np.random.randint(0, 30))
        
    invoice_no = f"INV-{100000 + i}"
    quantity = int(np.random.choice([1, 2, 3, 4, 5, 8, 12], p=[0.40, 0.25, 0.15, 0.10, 0.05, 0.03, 0.02]))
    unit_price = round(float(np.random.gamma(shape=3.0, scale=12.0)), 2)
    country = np.random.choice(countries, p=country_weights)

    records.append({
        "invoice_id": invoice_no,
        "customer_id": cid,
        "invoice_date": tx_date.strftime("%Y-%m-%d %H:%M:%S"),
        "quantity": quantity,
        "unit_price": unit_price,
        "country": country
    })

df = pd.DataFrame(records)
df["line_total"] = (df["quantity"] * df["unit_price"]).round(2)
output_path = "ecommerce_transactions.csv"
df.to_csv(output_path, index=False)
print(f"Generated {len(df)} transactions -> saved to {output_path}")
