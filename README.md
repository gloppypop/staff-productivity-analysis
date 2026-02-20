# Staff Productivity Analysis (KPI + Revenue Modeling)

## Executive Summary

This project shows how encounter-level service logs can be turned into monthly productivity and financial KPIs. The pipeline cleans raw data, converts time-based services into billable units, applies fiscal-year rate tables, and aggregates results into monthly trends. The end result is a reusable framework for evaluating provider productivity, revenue contribution, and utilization.

This project analyzes encounter-level service data to measure provider productivity, client engagement, and revenue contribution over time.

It demonstrates how operational service logs can be transformed into business-focused KPIs for performance evaluation and financial decision-making.

**Note:** This repository uses synthetic/de-identified data. No real client or private records are included.

---

## Business Objective

Given encounter-level service logs, this project answers:

- How many direct client hours were delivered each month?
- How much revenue was generated each month?
- How do productivity and revenue trend over time?
- What is revenue per client hour?
- What is the financial impact of a proposed compensation adjustment?

---

## Data

The dataset is a synthetic version of a service-based encounter export.

Key fields:

- `encounter_date`
- `cpt_code`
- `duration_min`
- `is_billable`
- `encounter_status`

Example dataset:

```
data/sample_monthly_data.csv
```

---

## KPI Definitions

**Client Hours (Monthly)**  
`client_hours = sum(duration_min) / 60`

**Units (15-Minute Time-Based Billing)**  
`units = floor(duration_min / 15)`

**Revenue (Monthly)**  
Time-based services:  
`revenue = sum(units * billing_rate)`

Per-encounter services:  
`revenue = sum(encounters * billing_rate)`

**Revenue per Client Hour**  
`revenue_per_hour = monthly_revenue / monthly_client_hours`

**Cost–Benefit Ratio (Optional Analysis)**  
`roi = monthly_revenue / monthly_compensation`

---

## Results

The following visualizations are generated from the KPI notebook and saved in the `outputs/` directory.

### Monthly Revenue
![Monthly Revenue](outputs/revenue_trends.png)

### Monthly Client Hours
![Monthly Client Hours](outputs/client_hours_trends.png)

### Revenue per Client Hour
![Revenue per Client Hour](outputs/revenue_per_hour.png)

### Utilization Rate
![Utilization Rate](outputs/utilization_rate.png)

## Key Insights

### 1. Revenue Growth Follows Productivity Gains

Monthly revenue increases significantly beginning mid-2023 and stabilizes through 2024. This mirrors the increase in client hours delivered during the same period. The revenue goal line shows that performance consistently meets or exceeds target once steady productivity levels are reached.

Revenue dips in early and late periods correspond directly with reduced client hours, indicating that financial performance is primarily volume-driven rather than rate-driven during most of the observed period.

---

### 2. Sustained Increase in Client Hours

Client hours show a clear ramp-up from approximately 30–50 hours per month early in the timeline to a sustained 85–105 hour range. This indicates a significant improvement in utilization and schedule density.

The temporary decline in the most recent month corresponds with a drop in revenue and utilization, reinforcing that hours delivered are the main performance driver.

---

### 3. Revenue per Client Hour Reflects Billing Structure Changes

The early spike in revenue per client hour (over $150/hour) is not purely a productivity effect. During that period, services were billed under an older T1012 structure at approximately $50 per encounter. Because multiple encounters could be delivered within a single hour — and those encounters did not accumulate over 15-minute billing intervals — the effective revenue per hour appeared artificially elevated.

After August 2023, billing shifted to a structure based on 15-minute units with cumulative billing rates. Under this model, revenue per hour stabilized in the ~$100–$110 range. This reflects a more consistent and scalable billing framework rather than a drop in productivity.

In other words, the change in revenue/hour is largely explained by billing mechanics — not a change in efficiency.

---

### 4. Utilization Performance Relative to Target

The utilization goal of 17.5 client hours per week (≈75.8 hours per month) translates to a utilization benchmark of roughly 47% under a 160-hour monthly baseline.

From late 2023 through 2024, utilization consistently exceeds this benchmark, often reaching 55–65%. This indicates strong schedule density and sustained client engagement.

Periods below the goal align with lower total revenue months, confirming the relationship between client hours and financial output.

---

### Overall Interpretation

Across all four metrics, performance stabilizes after mid-2023 with:

- Consistent client hours above target
- Revenue regularly exceeding monthly goal
- A normalized revenue per hour after billing standardization
- Utilization sustained above benchmark levels

The combined analysis demonstrates that long-term revenue performance is driven primarily by client-hour volume and sustained utilization, rather than rate fluctuations alone.

---

## Repository Structure

```
staff-productivity-analysis/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   └── sample_monthly_data.csv
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_revenue_calculation.ipynb
│   └── 03_kpi_analysis.ipynb
├── src/
│   ├── revenue_calculator.py
│   └── kpi_metrics.py
├── outputs/
│   ├── revenue_trends.png
│   ├── client_hours_trends.png
│   └── revenue_per_hour.png
└── report/
    └── performance_summary.pdf
```

---

## How to Run

1. Install dependencies:

```
pip install -r requirements.txt
```

2. Run notebooks in order:

```
01_data_cleaning.ipynb
02_revenue_calculation.ipynb
03_kpi_analysis.ipynb
```

---

## Tools Used

- Python
- pandas
- numpy
- matplotlib
- seaborn
- Jupyter Notebook

---

## Skills Demonstrated

- Data cleaning and normalization
- Revenue modeling from operational logs
- Time-based billing calculations
- KPI design and performance tracking
- Financial impact analysis
- Data visualization for decision support

---

## Disclaimer

This project is for portfolio demonstration purposes only.  
All data is synthetic or de-identified. Billing rates and examples are illustrative.