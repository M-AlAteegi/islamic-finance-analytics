"""
Islamic Finance Company - Data Visualizations
==============================================

This script creates professional visualizations for the Islamic finance database.
These charts can be included in presentations or reports.
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

# Connect to database
conn = sqlite3.connect('islamic_finance_company.db')

print("=" * 80)
print("GENERATING VISUALIZATIONS")
print("=" * 80)

# ============================================
# VISUALIZATION 1: LOAN DISTRIBUTION BY INDUSTRY
# ============================================

def viz_loan_by_industry():
    """Bar chart of loans by industry"""
    print("\n📊 Creating: Loan Distribution by Industry...")
    
    data = pd.read_sql("""
        SELECT 
            b.industry,
            COUNT(*) as num_loans,
            SUM(bl.loan_amount) as total_amount
        FROM business_loans bl
        JOIN borrowers b ON bl.borrower_id = b.borrower_id
        GROUP BY b.industry
        ORDER BY total_amount DESC
    """, conn)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Chart 1: Number of loans
    ax1.barh(data['industry'], data['num_loans'], color='steelblue')
    ax1.set_xlabel('Number of Loans', fontsize=12, fontweight='bold')
    ax1.set_title('Loan Volume by Industry', fontsize=14, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    
    # Chart 2: Total amount
    ax2.barh(data['industry'], data['total_amount']/1000000, color='coral')
    ax2.set_xlabel('Total Amount (Millions $)', fontsize=12, fontweight='bold')
    ax2.set_title('Loan Value by Industry', fontsize=14, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('viz_loan_by_industry.png', dpi=300, bbox_inches='tight')
    print("   ✓ Saved: viz_loan_by_industry.png")
    plt.close()

# ============================================
# VISUALIZATION 2: DEFAULT RATE ANALYSIS
# ============================================

def viz_default_analysis():
    """Visualization of default rates"""
    print("\n📊 Creating: Default Rate Analysis...")
    
    # Default rate by credit score
    data = pd.read_sql("""
        SELECT 
            CASE 
                WHEN b.credit_score >= 750 THEN '750+'
                WHEN b.credit_score >= 700 THEN '700-749'
                WHEN b.credit_score >= 650 THEN '650-699'
                WHEN b.credit_score >= 600 THEN '600-649'
                ELSE '<600'
            END as credit_category,
            COUNT(*) as total_loans,
            SUM(CASE WHEN bl.loan_status = 'Defaulted' THEN 1 ELSE 0 END) as defaults,
            ROUND(100.0 * SUM(CASE WHEN bl.loan_status = 'Defaulted' THEN 1 ELSE 0 END) / 
                  COUNT(*), 2) as default_rate
        FROM business_loans bl
        JOIN borrowers b ON bl.borrower_id = b.borrower_id
        GROUP BY credit_category
        ORDER BY 
            CASE credit_category
                WHEN '750+' THEN 1
                WHEN '700-749' THEN 2
                WHEN '650-699' THEN 3
                WHEN '600-649' THEN 4
                ELSE 5
            END
    """, conn)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    x = range(len(data))
    width = 0.35
    
    ax.bar([i - width/2 for i in x], data['total_loans'], width, 
           label='Total Loans', color='lightblue', edgecolor='black')
    ax.bar([i + width/2 for i in x], data['defaults'], width,
           label='Defaulted Loans', color='red', alpha=0.7, edgecolor='black')
    
    ax.set_xlabel('Credit Score Category', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Loans', fontsize=12, fontweight='bold')
    ax.set_title('Loan Performance by Credit Score Category', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(data['credit_category'])
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    
    # Add default rate percentages on top
    for i, (idx, row) in enumerate(data.iterrows()):
        ax.text(i, row['total_loans'] + 2, f"{row['default_rate']:.1f}%", 
                ha='center', fontweight='bold', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('viz_default_analysis.png', dpi=300, bbox_inches='tight')
    print("   ✓ Saved: viz_default_analysis.png")
    plt.close()

# ============================================
# VISUALIZATION 3: SUKUK PERFORMANCE
# ============================================

def viz_sukuk_performance():
    """Sukuk issuance and investment trends"""
    print("\n📊 Creating: Sukuk Performance Trends...")
    
    data = pd.read_sql("""
        SELECT 
            strftime('%Y-%m', sp.purchase_date) as month,
            COUNT(DISTINCT sp.purchase_id) as num_purchases,
            SUM(sp.amount) as total_invested,
            COUNT(DISTINCT sp.investor_id) as unique_investors
        FROM sukuk_purchases sp
        GROUP BY month
        ORDER BY month
    """, conn)
    
    data['month'] = pd.to_datetime(data['month'])
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Chart 1: Investment amount over time
    ax1.plot(data['month'], data['total_invested']/1000000, marker='o', 
             linewidth=2, markersize=6, color='green')
    ax1.fill_between(data['month'], data['total_invested']/1000000, alpha=0.3, color='green')
    ax1.set_ylabel('Total Investment (Millions $)', fontsize=12, fontweight='bold')
    ax1.set_title('Sukuk Investment Trends Over Time', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # Chart 2: Number of investors and purchases
    ax2_twin = ax2.twinx()
    
    line1 = ax2.plot(data['month'], data['num_purchases'], marker='s', 
                     linewidth=2, markersize=6, color='blue', label='Number of Purchases')
    line2 = ax2_twin.plot(data['month'], data['unique_investors'], marker='^', 
                          linewidth=2, markersize=6, color='orange', label='Unique Investors')
    
    ax2.set_xlabel('Month', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Number of Purchases', fontsize=12, fontweight='bold', color='blue')
    ax2_twin.set_ylabel('Unique Investors', fontsize=12, fontweight='bold', color='orange')
    ax2.set_title('Sukuk Purchase Activity', fontsize=14, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='blue')
    ax2_twin.tick_params(axis='y', labelcolor='orange')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)
    
    # Combine legends
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax2.legend(lines, labels, loc='upper left', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('viz_sukuk_performance.png', dpi=300, bbox_inches='tight')
    print("   ✓ Saved: viz_sukuk_performance.png")
    plt.close()

# ============================================
# VISUALIZATION 4: PAYMENT STATUS PIE CHART
# ============================================

def viz_payment_status():
    """Payment status distribution"""
    print("\n📊 Creating: Payment Status Distribution...")
    
    data = pd.read_sql("""
        SELECT 
            payment_status,
            COUNT(*) as count,
            SUM(payment_amount) as total_amount
        FROM loan_payments
        GROUP BY payment_status
    """, conn)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Colors
    colors = {'On Time': '#2ecc71', 'Late': '#f39c12', 'Missed': '#e74c3c'}
    color_list = [colors[status] for status in data['payment_status']]
    
    # Pie chart 1: By count
    ax1.pie(data['count'], labels=data['payment_status'], autopct='%1.1f%%',
            startangle=90, colors=color_list, textprops={'fontsize': 12, 'fontweight': 'bold'})
    ax1.set_title('Payment Status by Count', fontsize=14, fontweight='bold')
    
    # Pie chart 2: By amount
    ax2.pie(data['total_amount'], labels=data['payment_status'], autopct='%1.1f%%',
            startangle=90, colors=color_list, textprops={'fontsize': 12, 'fontweight': 'bold'})
    ax2.set_title('Payment Status by Amount', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('viz_payment_status.png', dpi=300, bbox_inches='tight')
    print("   ✓ Saved: viz_payment_status.png")
    plt.close()

# ============================================
# VISUALIZATION 5: INVESTOR RISK PROFILE
# ============================================

def viz_investor_profiles():
    """Investor segmentation by risk profile"""
    print("\n📊 Creating: Investor Profile Analysis...")
    
    data = pd.read_sql("""
        SELECT 
            risk_profile,
            COUNT(*) as num_investors,
            AVG(total_invested) as avg_investment,
            SUM(total_invested) as total_capital
        FROM investors
        GROUP BY risk_profile
        ORDER BY 
            CASE risk_profile
                WHEN 'Conservative' THEN 1
                WHEN 'Moderate' THEN 2
                WHEN 'Aggressive' THEN 3
            END
    """, conn)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Chart 1: Number of investors
    bars1 = ax1.bar(data['risk_profile'], data['num_investors'], 
                    color=['#3498db', '#9b59b6', '#e74c3c'], edgecolor='black')
    ax1.set_ylabel('Number of Investors', fontsize=12, fontweight='bold')
    ax1.set_title('Investor Count by Risk Profile', fontsize=14, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    
    # Add values on bars
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    # Chart 2: Total capital
    bars2 = ax2.bar(data['risk_profile'], data['total_capital']/1000000,
                    color=['#3498db', '#9b59b6', '#e74c3c'], edgecolor='black')
    ax2.set_ylabel('Total Capital (Millions $)', fontsize=12, fontweight='bold')
    ax2.set_title('Capital Distribution by Risk Profile', fontsize=14, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    
    # Add values on bars
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:.1f}M', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('viz_investor_profiles.png', dpi=300, bbox_inches='tight')
    print("   ✓ Saved: viz_investor_profiles.png")
    plt.close()

# ============================================
# VISUALIZATION 6: LOAN STATUS BREAKDOWN
# ============================================

def viz_loan_status():
    """Current loan portfolio status"""
    print("\n📊 Creating: Loan Portfolio Status...")
    
    data = pd.read_sql("""
        SELECT 
            loan_status,
            COUNT(*) as num_loans,
            SUM(loan_amount) as total_amount,
            SUM(outstanding_balance) as outstanding
        FROM business_loans
        GROUP BY loan_status
    """, conn)
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    colors_map = {'Active': '#2ecc71', 'Paid Off': '#3498db', 'Defaulted': '#e74c3c'}
    colors = [colors_map[status] for status in data['loan_status']]
    
    # Create stacked data
    statuses = data['loan_status']
    amounts = data['total_amount'] / 1000000
    
    bars = ax.bar(statuses, amounts, color=colors, edgecolor='black', linewidth=2)
    
    ax.set_ylabel('Total Loan Amount (Millions $)', fontsize=12, fontweight='bold')
    ax.set_title('Loan Portfolio Status Distribution', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # Add values and counts on bars
    for i, (bar, row) in enumerate(zip(bars, data.iterrows())):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:.1f}M\n({row[1]["num_loans"]} loans)',
                ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('viz_loan_status.png', dpi=300, bbox_inches='tight')
    print("   ✓ Saved: viz_loan_status.png")
    plt.close()

# ============================================
# VISUALIZATION 7: PROFIT DISTRIBUTION HEATMAP
# ============================================

def viz_profit_heatmap():
    """Heatmap of profit distributions over time"""
    print("\n📊 Creating: Profit Distribution Heatmap...")
    
    data = pd.read_sql("""
        SELECT 
            strftime('%Y', distribution_date) as year,
            strftime('%m', distribution_date) as month,
            SUM(amount) as total_distributed
        FROM profit_distributions
        GROUP BY year, month
        ORDER BY year, month
    """, conn)
    
    if len(data) > 0:
        # Pivot the data
        pivot_data = data.pivot_table(
            values='total_distributed',
            index='month',
            columns='year',
            fill_value=0
        )
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        sns.heatmap(pivot_data/1000, annot=True, fmt='.1f', cmap='YlGnBu',
                   cbar_kws={'label': 'Amount (Thousands $)'}, linewidths=0.5,
                   ax=ax)
        
        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Month', fontsize=12, fontweight='bold')
        ax.set_title('Profit Distributions to Sukuk Holders (Heatmap)', 
                    fontsize=14, fontweight='bold')
        
        # Set month labels
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        ax.set_yticklabels(month_names, rotation=0)
        
        plt.tight_layout()
        plt.savefig('viz_profit_heatmap.png', dpi=300, bbox_inches='tight')
        print("   ✓ Saved: viz_profit_heatmap.png")
        plt.close()
    else:
        print("   ⚠ Skipped: No profit distribution data available")

# ============================================
# VISUALIZATION 8: COMPREHENSIVE DASHBOARD
# ============================================

def viz_dashboard():
    """Create a comprehensive dashboard"""
    print("\n📊 Creating: Executive Dashboard...")
    
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # 1. Total metrics (top-left)
    ax1 = fig.add_subplot(gs[0, :])
    metrics = pd.read_sql("""
        SELECT 
            (SELECT SUM(amount) FROM sukuk_purchases) as capital_raised,
            (SELECT SUM(loan_amount) FROM business_loans) as loans_disbursed,
            (SELECT COUNT(*) FROM investors WHERE is_active = 1) as active_investors,
            (SELECT COUNT(*) FROM business_loans WHERE loan_status = 'Active') as active_loans,
            (SELECT SUM(amount) FROM profit_distributions) as profit_distributed
    """, conn)
    
    metric_names = ['Capital Raised', 'Loans Disbursed', 'Active Investors', 
                   'Active Loans', 'Profit Distributed']
    metric_values = [
        f"${metrics['capital_raised'][0]/1e6:.1f}M",
        f"${metrics['loans_disbursed'][0]/1e6:.1f}M",
        f"{metrics['active_investors'][0]:,}",
        f"{metrics['active_loans'][0]:,}",
        f"${metrics['profit_distributed'][0]/1e6:.1f}M"
    ]
    
    ax1.axis('tight')
    ax1.axis('off')
    table_data = [metric_names, metric_values]
    table = ax1.table(cellText=table_data, cellLoc='center', loc='center',
                     colWidths=[0.2]*5)
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 3)
    
    # Style the header row
    for i in range(5):
        table[(0, i)].set_facecolor('#3498db')
        table[(0, i)].set_text_props(weight='bold', color='white')
        table[(1, i)].set_facecolor('#ecf0f1')
        table[(1, i)].set_text_props(weight='bold')
    
    ax1.set_title('Key Performance Indicators', fontsize=16, fontweight='bold', pad=20)
    
    # 2. Loan status (middle-left)
    ax2 = fig.add_subplot(gs[1, 0])
    loan_status = pd.read_sql("""
        SELECT loan_status, COUNT(*) as count
        FROM business_loans
        GROUP BY loan_status
    """, conn)
    colors_map = {'Active': '#2ecc71', 'Paid Off': '#3498db', 'Defaulted': '#e74c3c'}
    colors = [colors_map.get(s, '#95a5a6') for s in loan_status['loan_status']]
    ax2.pie(loan_status['count'], labels=loan_status['loan_status'], 
           autopct='%1.1f%%', colors=colors, startangle=90)
    ax2.set_title('Loan Status Distribution', fontweight='bold')
    
    # 3. Industry distribution (middle-center)
    ax3 = fig.add_subplot(gs[1, 1])
    industries = pd.read_sql("""
        SELECT b.industry, COUNT(*) as count
        FROM business_loans bl
        JOIN borrowers b ON bl.borrower_id = b.borrower_id
        GROUP BY b.industry
        ORDER BY count DESC
        LIMIT 6
    """, conn)
    ax3.barh(industries['industry'], industries['count'], color='coral')
    ax3.set_xlabel('Number of Loans', fontweight='bold')
    ax3.set_title('Top Industries', fontweight='bold')
    ax3.grid(axis='x', alpha=0.3)
    
    # 4. Investor profiles (middle-right)
    ax4 = fig.add_subplot(gs[1, 2])
    risk_profiles = pd.read_sql("""
        SELECT risk_profile, COUNT(*) as count
        FROM investors
        GROUP BY risk_profile
    """, conn)
    colors = ['#3498db', '#9b59b6', '#e74c3c']
    ax4.bar(risk_profiles['risk_profile'], risk_profiles['count'], color=colors)
    ax4.set_ylabel('Number of Investors', fontweight='bold')
    ax4.set_title('Investor Risk Profiles', fontweight='bold')
    ax4.grid(axis='y', alpha=0.3)
    
    # 5. Monthly trends (bottom - spans all columns)
    ax5 = fig.add_subplot(gs[2, :])
    monthly = pd.read_sql("""
        SELECT 
            strftime('%Y-%m', disbursement_date) as month,
            SUM(loan_amount) as amount
        FROM business_loans
        GROUP BY month
        ORDER BY month
    """, conn)
    monthly['month'] = pd.to_datetime(monthly['month'])
    ax5.plot(monthly['month'], monthly['amount']/1000000, marker='o', 
            linewidth=2, markersize=5, color='green')
    ax5.fill_between(monthly['month'], monthly['amount']/1000000, alpha=0.3, color='green')
    ax5.set_xlabel('Month', fontweight='bold')
    ax5.set_ylabel('Loan Amount (Millions $)', fontweight='bold')
    ax5.set_title('Monthly Loan Disbursement Trends', fontweight='bold')
    ax5.grid(True, alpha=0.3)
    ax5.tick_params(axis='x', rotation=45)
    
    plt.suptitle('Islamic Finance Company - Executive Dashboard', 
                fontsize=18, fontweight='bold', y=0.98)
    
    plt.savefig('viz_dashboard.png', dpi=300, bbox_inches='tight')
    print("   ✓ Saved: viz_dashboard.png")
    plt.close()

# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Generate all visualizations"""
    try:
        viz_loan_by_industry()
        viz_default_analysis()
        viz_sukuk_performance()
        viz_payment_status()
        viz_investor_profiles()
        viz_loan_status()
        viz_profit_heatmap()
        viz_dashboard()
        
        print("\n" + "=" * 80)
        print("✅ ALL VISUALIZATIONS GENERATED!")
        print("=" * 80)
        print("\n📁 Generated Files:")
        print("   • viz_loan_by_industry.png")
        print("   • viz_default_analysis.png")
        print("   • viz_sukuk_performance.png")
        print("   • viz_payment_status.png")
        print("   • viz_investor_profiles.png")
        print("   • viz_loan_status.png")
        print("   • viz_profit_heatmap.png")
        print("   • viz_dashboard.png")
        
    except Exception as e:
        print(f"\n❌ Error generating visualizations: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
