"""
visualizations.py
Generates charts into charts/ and returns list of file paths.
"""

import os
import json
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

CHARTS_DIR = "charts"
DATA_DIR = "data"

os.makedirs(CHARTS_DIR, exist_ok=True)

try:
    plt.style.use("seaborn-v0_8-darkgrid")
except Exception:
    pass


def load_data():
    sales_data = []
    marketing_data = []

    try:
        with open(os.path.join(DATA_DIR, "sales_data.json"), "r", encoding="utf-8") as f:
            sales_data = json.load(f)
    except Exception as e:
        print(f"Could not load sales data: {e}")

    try:
        with open(os.path.join(DATA_DIR, "marketing_data.json"), "r", encoding="utf-8") as f:
            marketing_data = json.load(f)
    except Exception as e:
        print(f"Could not load marketing data: {e}")

    return sales_data, marketing_data


def _save(fig, filename):
    path = os.path.join(CHARTS_DIR, filename)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def create_sales_by_region_chart(sales_data):
    revenue = defaultdict(float)

    for s in sales_data:
        revenue[s.get("region", "Unknown")] += float(s.get("revenue", 0))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(list(revenue.keys()), list(revenue.values()))
    ax.set_title("Sales Revenue by Region")
    ax.set_ylabel("Revenue")
    return _save(fig, "sales_by_region.png")


def create_quarterly_performance_chart(sales_data):
    revenue = defaultdict(float)

    for s in sales_data:
        revenue[s.get("quarter", "Unknown")] += float(s.get("revenue", 0))

    quarters = sorted(revenue.keys())
    values = [revenue[q] for q in quarters]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(quarters, values, marker="o")
    ax.set_title("Quarterly Sales Performance")
    ax.set_ylabel("Revenue")

    return _save(fig, "quarterly_performance.png")


def create_product_performance_chart(sales_data):
    revenue = defaultdict(float)

    for s in sales_data:
        revenue[s.get("product", "Unknown")] += float(s.get("revenue", 0))

    fig, ax = plt.subplots(figsize=(8, 8))

    labels = list(revenue.keys())
    values = list(revenue.values())

    if values:
        ax.pie(values, labels=labels, autopct="%1.1f%%")

    ax.set_title("Product Revenue Distribution")

    return _save(fig, "product_performance.png")


def create_marketing_roi_chart(marketing_data):
    campaigns = [m.get("campaign_name", "Campaign")[:20] for m in marketing_data]
    budgets = [float(m.get("budget", 0)) for m in marketing_data]
    conversions = [float(m.get("conversions", 0)) for m in marketing_data]

    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(campaigns))
    width = 0.4

    ax.bar(x - width / 2, budgets, width, label="Budget")
    ax.bar(x + width / 2, conversions, width, label="Conversions")

    ax.set_xticks(x)
    ax.set_xticklabels(campaigns, rotation=45, ha="right")
    ax.legend()

    ax.set_title("Marketing Campaign Performance")

    return _save(fig, "marketing_roi.png")


def create_channel_performance_chart(marketing_data):
    conversions = defaultdict(float)

    for m in marketing_data:
        conversions[m.get("channel", "Unknown")] += float(m.get("conversions", 0))

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.bar(list(conversions.keys()), list(conversions.values()))
    ax.set_title("Conversions by Marketing Channel")

    return _save(fig, "channel_performance.png")


def create_top_products_chart(sales_data):
    revenue = defaultdict(float)

    for s in sales_data:
        revenue[s.get("product", "Unknown")] += float(s.get("revenue", 0))

    top = sorted(revenue.items(), key=lambda x: x[1], reverse=True)[:10]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.barh([x[0] for x in top], [x[1] for x in top])
    ax.set_title("Top Products by Revenue")

    return _save(fig, "top_products.png")


def create_region_comparison_chart(sales_data):
    revenue = defaultdict(float)
    units = defaultdict(float)

    for s in sales_data:
        region = s.get("region", "Unknown")
        revenue[region] += float(s.get("revenue", 0))
        units[region] += float(s.get("units_sold", 0))

    regions = list(revenue.keys())
    x = np.arange(len(regions))

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.bar(x - 0.2, [revenue[r] for r in regions], 0.4, label="Revenue")
    ax.bar(x + 0.2, [units[r] for r in regions], 0.4, label="Units Sold")

    ax.set_xticks(x)
    ax.set_xticklabels(regions)
    ax.legend()

    ax.set_title("Regional Comparison")

    return _save(fig, "regional_comparison.png")


def create_quarterly_growth_chart(sales_data):
    revenue = defaultdict(float)

    for s in sales_data:
        revenue[s.get("quarter", "Unknown")] += float(s.get("revenue", 0))

    quarters = sorted(revenue.keys())
    values = [revenue[q] for q in quarters]

    growth = [0]

    for i in range(1, len(values)):
        prev = values[i - 1]
        cur = values[i]
        growth.append(((cur - prev) / prev * 100) if prev else 0)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(quarters, growth, marker="o")
    ax.set_title("Quarterly Growth %")
    ax.set_ylabel("Growth %")

    return _save(fig, "quarterly_growth.png")


def generate_all_charts(
    sales_data=None,
    marketing_data=None,
    region=None,
    quarter=None,
    product=None,
    channel=None,
):
    if sales_data is None or marketing_data is None:
        sales_data, marketing_data = load_data()

    if region:
        sales_data = [x for x in sales_data if x.get("region") == region]

    if quarter:
        sales_data = [x for x in sales_data if x.get("quarter") == quarter]
        marketing_data = [x for x in marketing_data if x.get("quarter") == quarter]

    if product:
        sales_data = [x for x in sales_data if x.get("product") == product]

    if channel:
        marketing_data = [x for x in marketing_data if x.get("channel") == channel]

    charts = []

    try:
        charts.append(create_sales_by_region_chart(sales_data))
    except Exception as e:
        print(e)

    try:
        charts.append(create_quarterly_performance_chart(sales_data))
    except Exception as e:
        print(e)

    try:
        charts.append(create_product_performance_chart(sales_data))
    except Exception as e:
        print(e)

    try:
        charts.append(create_marketing_roi_chart(marketing_data))
    except Exception as e:
        print(e)

    try:
        charts.append(create_channel_performance_chart(marketing_data))
    except Exception as e:
        print(e)

    try:
        charts.append(create_top_products_chart(sales_data))
    except Exception as e:
        print(e)

    try:
        charts.append(create_region_comparison_chart(sales_data))
    except Exception as e:
        print(e)

    try:
        charts.append(create_quarterly_growth_chart(sales_data))
    except Exception as e:
        print(e)

    return charts


if __name__ == "__main__":
    files = generate_all_charts()
    print(files)
