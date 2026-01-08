"""
Create beautiful visualizations for sales and marketing data using matplotlib
"""
import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Arial']
rcParams['figure.facecolor'] = 'white'


def load_data():
    """Load sales and marketing data from JSON files"""
    with open("data/sales_data.json", "r") as f:
        sales_data = json.load(f)
    
    with open("data/marketing_data.json", "r") as f:
        marketing_data = json.load(f)
    
    return sales_data, marketing_data


def create_sales_by_region_chart():
    """Create sales revenue by region chart"""
    sales_data, _ = load_data()
    
    # Aggregate by region
    region_revenue = {}
    for sale in sales_data:
        region = sale["region"]
        revenue = sale["revenue"]
        region_revenue[region] = region_revenue.get(region, 0) + revenue
    
    fig, ax = plt.subplots(figsize=(10, 6))
    regions = list(region_revenue.keys())
    revenues = list(region_revenue.values())
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    bars = ax.bar(regions, revenues, color=colors, edgecolor='#2C3E50', linewidth=2)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:,.0f}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    ax.set_title('Sales Revenue by Region', fontsize=20, fontweight='bold', pad=20)
    ax.set_xlabel('Region', fontsize=14, fontweight='bold')
    ax.set_ylabel('Revenue ($)', fontsize=14, fontweight='bold')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.tight_layout()
    plt.savefig('sales_by_region.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    return "sales_by_region.png"


def create_quarterly_performance_chart():
    """Create quarterly sales performance chart"""
    sales_data, _ = load_data()
    
    # Aggregate by quarter
    quarter_revenue = {}
    for sale in sales_data:
        quarter = sale["quarter"]
        revenue = sale["revenue"]
        quarter_revenue[quarter] = quarter_revenue.get(quarter, 0) + revenue
    
    quarters = sorted(quarter_revenue.keys())
    revenues = [quarter_revenue[q] for q in quarters]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(quarters, revenues, marker='o', linewidth=3, color='#3498DB', 
            markersize=12, markerfacecolor='#E74C3C', markeredgecolor='white', 
            markeredgewidth=2)
    ax.fill_between(quarters, revenues, alpha=0.3, color='#3498DB')
    
    # Add value labels
    for x, y in zip(quarters, revenues):
        ax.text(x, y + max(revenues)*0.03, f'${y:,.0f}', 
                ha='center', fontsize=11, fontweight='bold')
    
    ax.set_title('Quarterly Sales Performance', fontsize=20, fontweight='bold', pad=20)
    ax.set_xlabel('Quarter', fontsize=14, fontweight='bold')
    ax.set_ylabel('Revenue ($)', fontsize=14, fontweight='bold')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('quarterly_performance.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    return "quarterly_performance.png"


def create_product_performance_chart():
    """Create product performance chart"""
    sales_data, _ = load_data()
    
    # Aggregate by product
    product_data = {}
    for sale in sales_data:
        product = sale["product"]
        if product not in product_data:
            product_data[product] = {"revenue": 0, "units": 0}
        product_data[product]["revenue"] += sale["revenue"]
        product_data[product]["units"] += sale["units_sold"]
    
    products = list(product_data.keys())
    revenues = [product_data[p]["revenue"] for p in products]
    
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    
    wedges, texts, autotexts = ax.pie(revenues, labels=products, autopct='%1.1f%%',
                                        colors=colors, startangle=90, 
                                        textprops={'fontsize': 11, 'fontweight': 'bold'},
                                        wedgeprops={'edgecolor': 'white', 'linewidth': 2})
    
    # Make percentage text white
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(12)
        autotext.set_fontweight('bold')
    
    ax.set_title('Product Revenue Distribution', fontsize=20, fontweight='bold', pad=20)
    
    # Add legend with revenue values
    legend_labels = [f'{p}: ${r:,.0f}' for p, r in zip(products, revenues)]
    ax.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10)
    
    plt.tight_layout()
    plt.savefig('product_performance.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    return "product_performance.png"


def create_marketing_roi_chart():
    """Create marketing ROI chart"""
    _, marketing_data = load_data()
    
    campaigns = [m["campaign_name"][:25] for m in marketing_data]
    budgets = [m["budget"] for m in marketing_data]
    conversions = [m["conversions"] for m in marketing_data]
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    x = np.arange(len(campaigns))
    width = 0.35
    
    ax1.bar(x - width/2, budgets, width, label='Budget', color='#3498DB', edgecolor='black', linewidth=1.5)
    ax1.set_xlabel('Campaign', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Budget ($)', fontsize=14, fontweight='bold', color='#3498DB')
    ax1.tick_params(axis='y', labelcolor='#3498DB')
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    ax2 = ax1.twinx()
    ax2.bar(x + width/2, conversions, width, label='Conversions', color='#2ECC71', edgecolor='black', linewidth=1.5)
    ax2.set_ylabel('Conversions', fontsize=14, fontweight='bold', color='#2ECC71')
    ax2.tick_params(axis='y', labelcolor='#2ECC71')
    
    ax1.set_xticks(x)
    ax1.set_xticklabels(campaigns, rotation=45, ha='right', fontsize=9)
    ax1.set_title('Marketing Campaign Performance', fontsize=20, fontweight='bold', pad=20)
    
    # Add legends
    ax1.legend(loc='upper left', fontsize=11)
    ax2.legend(loc='upper right', fontsize=11)
    
    plt.tight_layout()
    plt.savefig('marketing_roi.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    return "marketing_roi.png"


def create_channel_performance_chart():
    """Create marketing channel performance chart"""
    _, marketing_data = load_data()
    
    # Aggregate by channel
    channel_data = {}
    for campaign in marketing_data:
        channel = campaign["channel"]
        if channel not in channel_data:
            channel_data[channel] = {
                "budget": 0,
                "impressions": 0,
                "clicks": 0,
                "conversions": 0
            }
        channel_data[channel]["budget"] += campaign["budget"]
        channel_data[channel]["impressions"] += campaign["impressions"]
        channel_data[channel]["clicks"] += campaign["clicks"]
        channel_data[channel]["conversions"] += campaign["conversions"]
    
    channels = list(channel_data.keys())
    conversions = [channel_data[c]["conversions"] for c in channels]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = plt.cm.viridis(np.linspace(0, 1, len(channels)))
    bars = ax.bar(channels, conversions, color=colors, edgecolor='#2C3E50', linewidth=2)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    ax.set_title('Conversions by Marketing Channel', fontsize=20, fontweight='bold', pad=20)
    ax.set_xlabel('Channel', fontsize=14, fontweight='bold')
    ax.set_ylabel('Total Conversions', fontsize=14, fontweight='bold')
    ax.set_xticklabels(channels, rotation=20, ha='right')
    
    plt.tight_layout()
    plt.savefig('channel_performance.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    return "channel_performance.png"


def generate_all_charts():
    """Generate all visualization charts"""
    print("\n" + "="*80)
    print("GENERATING VISUALIZATIONS")
    print("="*80)
    
    charts = []
    
    print("\n[1/5] Creating Sales by Region chart...")
    charts.append(create_sales_by_region_chart())
    print("✓ sales_by_region.png")
    
    print("\n[2/5] Creating Quarterly Performance chart...")
    charts.append(create_quarterly_performance_chart())
    print("✓ quarterly_performance.png")
    
    print("\n[3/5] Creating Product Performance chart...")
    charts.append(create_product_performance_chart())
    print("✓ product_performance.png")
    
    print("\n[4/5] Creating Marketing ROI chart...")
    charts.append(create_marketing_roi_chart())
    print("✓ marketing_roi.png")
    
    print("\n[5/5] Creating Channel Performance chart...")
    charts.append(create_channel_performance_chart())
    print("✓ channel_performance.png")
    
    print("\n" + "="*80)
    print("ALL VISUALIZATIONS GENERATED!")
    print("="*80 + "\n")
    
    return charts


if __name__ == "__main__":
    generate_all_charts()
