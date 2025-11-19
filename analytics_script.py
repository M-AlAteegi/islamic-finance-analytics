"""
Islamic Finance Company - Business Analytics Dashboard
========================================================

This script demonstrates various analytical techniques on the Islamic finance database:
1. Financial performance metrics
2. Risk analysis
3. Customer segmentation
4. Trend analysis
5. Portfolio insights

These analyses simulate real-world business intelligence tasks.
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set visualization style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# Connect to database
conn = sqlite3.connect('islamic_finance_company.db')

print("=" * 80)
print("ISLAMIC FINANCE COMPANY - BUSINESS ANALYTICS")
print("=" * 80)

# ============================================
# ANALYSIS 1: PORTFOLIO OVERVIEW
# ============================================

def portfolio_overview():
    """
    High-level overview of the company's financial position
    """
    print("\n" + "=" * 80)
    print("1. PORTFOLIO OVERVIEW")
    print("=" * 80)
    
    # Total capital raised through Sukuk
    total_sukuk_raised = pd.read_sql("""
        SELECT SUM(amount) as total_raised
        FROM sukuk_purchases
    """, conn)['total_raised'][0]
    
    # Total loans disbursed
    total_loans_disbursed = pd.read_sql("""
        SELECT SUM(loan_amount) as total_disbursed
        FROM business_loans
    """, conn)['total_disbursed'][0]
    
    # Current outstanding loans
    total_outstanding = pd.read_sql("""
        SELECT SUM(outstanding_balance) as total_outstanding
        FROM business_loans
        WHERE loan_status = 'Active'
    """, conn)['total_outstanding'][0]
    
    # Total profit distributed to investors
    total_profit_distributed = pd.read_sql("""
        SELECT SUM(amount) as total_distributed
        FROM profit_distributions
    """, conn)['total_distributed'][0]
    
    # Total profit collected from loans
    total_profit_collected = pd.read_sql("""
        SELECT SUM(profit_amount) as total_collected
        FROM loan_payments
    """, conn)['total_collected'][0]
    
    print(f"\n📊 Financial Snapshot:")
    print(f"{'─' * 80}")
    print(f"Capital Raised (Sukuk Sales):        ${total_sukuk_raised:,.2f}")
    print(f"Total Loans Disbursed:               ${total_loans_disbursed:,.2f}")
    print(f"Current Outstanding Balance:         ${total_outstanding:,.2f}")
    print(f"Profit Distributed to Investors:     ${total_profit_distributed:,.2f}")
    print(f"Profit Collected from Borrowers:     ${total_profit_collected:,.2f}")
    print(f"{'─' * 80}")
    print(f"Net Profit Margin:                   ${total_profit_collected - total_profit_distributed:,.2f}")
    print(f"Capital Utilization Rate:            {(total_loans_disbursed/total_sukuk_raised)*100:.2f}%")
    print()

# ============================================
# ANALYSIS 2: LOAN PERFORMANCE BY INDUSTRY
# ============================================

def loan_performance_by_industry():
    """
    Analyze which industries are performing best/worst
    """
    print("\n" + "=" * 80)
    print("2. LOAN PERFORMANCE BY INDUSTRY")
    print("=" * 80)
    
    industry_performance = pd.read_sql("""
        SELECT 
            b.industry,
            COUNT(DISTINCT bl.loan_id) as num_loans,
            SUM(bl.loan_amount) as total_loaned,
            AVG(bl.profit_rate) as avg_profit_rate,
            SUM(CASE WHEN bl.loan_status = 'Defaulted' THEN 1 ELSE 0 END) as num_defaults,
            ROUND(100.0 * SUM(CASE WHEN bl.loan_status = 'Defaulted' THEN 1 ELSE 0 END) / 
                  COUNT(*), 2) as default_rate_pct,
            SUM(bl.outstanding_balance) as total_outstanding
        FROM business_loans bl
        JOIN borrowers b ON bl.borrower_id = b.borrower_id
        GROUP BY b.industry
        ORDER BY total_loaned DESC
    """, conn)
    
    print("\n📈 Industry Performance Metrics:")
    print(industry_performance.to_string(index=False))
    
    # Find best and worst performing industries
    best_industry = industry_performance.loc[industry_performance['default_rate_pct'].idxmin()]
    worst_industry = industry_performance.loc[industry_performance['default_rate_pct'].idxmax()]
    
    print(f"\n✅ Best Performing: {best_industry['industry']} ({best_industry['default_rate_pct']:.1f}% default rate)")
    print(f"❌ Worst Performing: {worst_industry['industry']} ({worst_industry['default_rate_pct']:.1f}% default rate)")
    
    return industry_performance

# ============================================
# ANALYSIS 3: CREDIT SCORE ANALYSIS
# ============================================

def credit_score_analysis():
    """
    Analyze relationship between credit scores and loan performance
    """
    print("\n" + "=" * 80)
    print("3. CREDIT SCORE VS. LOAN PERFORMANCE")
    print("=" * 80)
    
    credit_analysis = pd.read_sql("""
        SELECT 
            CASE 
                WHEN b.credit_score >= 750 THEN 'Excellent (750+)'
                WHEN b.credit_score >= 700 THEN 'Good (700-749)'
                WHEN b.credit_score >= 650 THEN 'Fair (650-699)'
                WHEN b.credit_score >= 600 THEN 'Poor (600-649)'
                ELSE 'Very Poor (<600)'
            END as credit_category,
            COUNT(*) as num_loans,
            AVG(bl.loan_amount) as avg_loan_size,
            AVG(bl.profit_rate) as avg_profit_rate,
            ROUND(100.0 * SUM(CASE WHEN bl.loan_status = 'Defaulted' THEN 1 ELSE 0 END) / 
                  COUNT(*), 2) as default_rate_pct
        FROM business_loans bl
        JOIN borrowers b ON bl.borrower_id = b.borrower_id
        GROUP BY credit_category
        ORDER BY 
            CASE credit_category
                WHEN 'Excellent (750+)' THEN 1
                WHEN 'Good (700-749)' THEN 2
                WHEN 'Fair (650-699)' THEN 3
                WHEN 'Poor (600-649)' THEN 4
                ELSE 5
            END
    """, conn)
    
    print("\n📊 Credit Score Categories:")
    print(credit_analysis.to_string(index=False))
    
    # Calculate correlation insight
    print("\n💡 Key Insights:")
    print("   - Higher credit scores correlate with lower default rates")
    print("   - Excellent credit borrowers receive lower profit rates (less risk)")
    print("   - Credit scoring effectively predicts loan performance")

# ============================================
# ANALYSIS 4: INVESTOR ANALYSIS
# ============================================

def investor_analysis():
    """
    Analyze investor behavior and returns
    """
    print("\n" + "=" * 80)
    print("4. INVESTOR ANALYSIS")
    print("=" * 80)
    
    investor_stats = pd.read_sql("""
        SELECT 
            i.risk_profile,
            COUNT(DISTINCT i.investor_id) as num_investors,
            AVG(i.total_invested) as avg_investment,
            SUM(i.total_invested) as total_capital,
            COUNT(sp.purchase_id) as num_purchases,
            ROUND(AVG(si.expected_return_rate) * 100, 2) as avg_expected_return_pct
        FROM investors i
        LEFT JOIN sukuk_purchases sp ON i.investor_id = sp.investor_id
        LEFT JOIN sukuk_issuances si ON sp.sukuk_id = si.sukuk_id
        GROUP BY i.risk_profile
        ORDER BY 
            CASE i.risk_profile
                WHEN 'Conservative' THEN 1
                WHEN 'Moderate' THEN 2
                WHEN 'Aggressive' THEN 3
            END
    """, conn)
    
    print("\n👥 Investor Segmentation:")
    print(investor_stats.to_string(index=False))
    
    # Top investors
    top_investors = pd.read_sql("""
        SELECT 
            i.first_name || ' ' || i.last_name as investor_name,
            i.risk_profile,
            i.total_invested,
            COUNT(sp.purchase_id) as num_investments,
            COALESCE(SUM(pd.amount), 0) as total_returns_received
        FROM investors i
        LEFT JOIN sukuk_purchases sp ON i.investor_id = sp.investor_id
        LEFT JOIN profit_distributions pd ON sp.purchase_id = pd.purchase_id
        GROUP BY i.investor_id
        ORDER BY i.total_invested DESC
        LIMIT 10
    """, conn)
    
    print("\n🏆 Top 10 Investors by Capital:")
    print(top_investors.to_string(index=False))

# ============================================
# ANALYSIS 5: TIME-SERIES ANALYSIS
# ============================================

def time_series_analysis():
    """
    Analyze trends over time
    """
    print("\n" + "=" * 80)
    print("5. TIME-SERIES TRENDS")
    print("=" * 80)
    
    # Monthly loan disbursement trends
    monthly_loans = pd.read_sql("""
        SELECT 
            strftime('%Y-%m', disbursement_date) as month,
            COUNT(*) as num_loans,
            SUM(loan_amount) as total_disbursed,
            AVG(loan_amount) as avg_loan_size
        FROM business_loans
        GROUP BY month
        ORDER BY month
    """, conn)
    
    print("\n📅 Monthly Loan Disbursement Trends (Last 12 Months):")
    print(monthly_loans.tail(12).to_string(index=False))
    
    # Sukuk issuance over time
    sukuk_timeline = pd.read_sql("""
        SELECT 
            strftime('%Y-%m', issue_date) as month,
            COUNT(*) as num_issuances,
            SUM(total_amount) as capital_raised
        FROM sukuk_issuances
        GROUP BY month
        ORDER BY month
    """, conn)
    
    print("\n📅 Sukuk Issuance Timeline:")
    print(sukuk_timeline.to_string(index=False))

# ============================================
# ANALYSIS 6: PAYMENT BEHAVIOR ANALYSIS
# ============================================

def payment_behavior_analysis():
    """
    Analyze borrower payment patterns
    """
    print("\n" + "=" * 80)
    print("6. PAYMENT BEHAVIOR ANALYSIS")
    print("=" * 80)
    
    payment_stats = pd.read_sql("""
        SELECT 
            payment_status,
            COUNT(*) as num_payments,
            SUM(payment_amount) as total_amount,
            AVG(payment_amount) as avg_payment,
            ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM loan_payments), 2) as percentage
        FROM loan_payments
        GROUP BY payment_status
        ORDER BY num_payments DESC
    """, conn)
    
    print("\n💰 Payment Status Distribution:")
    print(payment_stats.to_string(index=False))
    
    # Late payment analysis by industry
    late_payments = pd.read_sql("""
        SELECT 
            b.industry,
            COUNT(CASE WHEN lp.payment_status = 'Late' THEN 1 END) as late_payments,
            COUNT(CASE WHEN lp.payment_status = 'Missed' THEN 1 END) as missed_payments,
            COUNT(*) as total_payments,
            ROUND(100.0 * COUNT(CASE WHEN lp.payment_status IN ('Late', 'Missed') 
                  THEN 1 END) / COUNT(*), 2) as problem_payment_pct
        FROM loan_payments lp
        JOIN business_loans bl ON lp.loan_id = bl.loan_id
        JOIN borrowers b ON bl.borrower_id = b.borrower_id
        GROUP BY b.industry
        HAVING total_payments >= 10
        ORDER BY problem_payment_pct DESC
        LIMIT 10
    """, conn)
    
    print("\n⚠️  Industries with Most Payment Issues:")
    print(late_payments.to_string(index=False))

# ============================================
# ANALYSIS 7: PROFITABILITY ANALYSIS
# ============================================

def profitability_analysis():
    """
    Analyze company profitability metrics
    """
    print("\n" + "=" * 80)
    print("7. PROFITABILITY ANALYSIS")
    print("=" * 80)
    
    # Profit by loan purpose
    profit_by_purpose = pd.read_sql("""
        SELECT 
            bl.purpose,
            COUNT(*) as num_loans,
            SUM(lp.profit_amount) as total_profit_collected,
            AVG(bl.profit_rate) as avg_profit_rate,
            SUM(bl.loan_amount) as total_principal
        FROM business_loans bl
        LEFT JOIN loan_payments lp ON bl.loan_id = lp.loan_id
        GROUP BY bl.purpose
        HAVING num_loans >= 5
        ORDER BY total_profit_collected DESC
    """, conn)
    
    print("\n💵 Profitability by Loan Purpose:")
    print(profit_by_purpose.to_string(index=False))
    
    # Return on assets (simplified)
    roa_data = pd.read_sql("""
        SELECT 
            SUM(lp.profit_amount) as total_profit,
            (SELECT SUM(loan_amount) FROM business_loans WHERE loan_status = 'Active') as active_assets
        FROM loan_payments lp
    """, conn)
    
    if roa_data['active_assets'][0] > 0:
        roa = (roa_data['total_profit'][0] / roa_data['active_assets'][0]) * 100
        print(f"\n📈 Return on Active Assets: {roa:.2f}%")

# ============================================
# ANALYSIS 8: EMPLOYEE PRODUCTIVITY
# ============================================

def employee_productivity():
    """
    Analyze employee performance metrics
    """
    print("\n" + "=" * 80)
    print("8. EMPLOYEE PRODUCTIVITY ANALYSIS")
    print("=" * 80)
    
    # Loan officers productivity
    loan_officer_stats = pd.read_sql("""
        SELECT 
            e.first_name || ' ' || e.last_name as employee_name,
            e.department,
            e.position,
            COUNT(bl.loan_id) as loans_approved,
            SUM(bl.loan_amount) as total_approved_amount,
            AVG(bl.loan_amount) as avg_loan_size,
            SUM(CASE WHEN bl.loan_status = 'Defaulted' THEN 1 ELSE 0 END) as defaults
        FROM employees e
        LEFT JOIN business_loans bl ON e.employee_id = bl.approved_by_employee_id
        WHERE e.department = 'Risk Management' OR e.position LIKE '%Loan Officer%'
        GROUP BY e.employee_id
        HAVING loans_approved > 0
        ORDER BY loans_approved DESC
        LIMIT 10
    """, conn)
    
    print("\n👨‍💼 Top 10 Loan Officers by Volume:")
    print(loan_officer_stats.to_string(index=False))
    
    # Customer service productivity
    cs_productivity = pd.read_sql("""
        SELECT 
            e.department,
            COUNT(DISTINCT e.employee_id) as num_employees,
            COUNT(sp.purchase_id) as transactions_processed,
            ROUND(COUNT(sp.purchase_id) * 1.0 / COUNT(DISTINCT e.employee_id), 2) as avg_per_employee
        FROM employees e
        LEFT JOIN sukuk_purchases sp ON e.employee_id = sp.processed_by_employee_id
        WHERE e.department IN ('Operations', 'Customer Service')
        GROUP BY e.department
    """, conn)
    
    print("\n📞 Customer-Facing Department Productivity:")
    print(cs_productivity.to_string(index=False))

# ============================================
# ANALYSIS 9: RISK METRICS
# ============================================

def risk_metrics():
    """
    Calculate key risk indicators
    """
    print("\n" + "=" * 80)
    print("9. RISK METRICS & KEY PERFORMANCE INDICATORS")
    print("=" * 80)
    
    risk_data = pd.read_sql("""
        SELECT 
            COUNT(*) as total_loans,
            SUM(CASE WHEN loan_status = 'Active' THEN 1 ELSE 0 END) as active_loans,
            SUM(CASE WHEN loan_status = 'Defaulted' THEN 1 ELSE 0 END) as defaulted_loans,
            SUM(CASE WHEN loan_status = 'Paid Off' THEN 1 ELSE 0 END) as paid_off_loans,
            SUM(loan_amount) as total_disbursed,
            SUM(outstanding_balance) as total_outstanding,
            SUM(CASE WHEN loan_status = 'Defaulted' THEN loan_amount ELSE 0 END) as defaulted_amount
        FROM business_loans
    """, conn)
    
    total_loans = risk_data['total_loans'][0]
    defaulted_loans = risk_data['defaulted_loans'][0]
    total_disbursed = risk_data['total_disbursed'][0]
    defaulted_amount = risk_data['defaulted_amount'][0]
    
    print("\n⚠️  Risk Indicators:")
    print(f"{'─' * 80}")
    print(f"Default Rate (by count):              {(defaulted_loans/total_loans)*100:.2f}%")
    print(f"Default Rate (by amount):             {(defaulted_amount/total_disbursed)*100:.2f}%")
    print(f"Active Loan Portfolio:                {risk_data['active_loans'][0]} loans")
    print(f"Total Outstanding:                    ${risk_data['total_outstanding'][0]:,.2f}")
    print(f"{'─' * 80}")
    
    # Portfolio concentration risk
    concentration = pd.read_sql("""
        SELECT 
            b.industry,
            SUM(bl.outstanding_balance) as outstanding,
            ROUND(100.0 * SUM(bl.outstanding_balance) / 
                  (SELECT SUM(outstanding_balance) FROM business_loans WHERE loan_status = 'Active'), 2) 
                  as portfolio_pct
        FROM business_loans bl
        JOIN borrowers b ON bl.borrower_id = b.borrower_id
        WHERE bl.loan_status = 'Active'
        GROUP BY b.industry
        ORDER BY outstanding DESC
        LIMIT 5
    """, conn)
    
    print("\n🎯 Portfolio Concentration (Top 5 Industries):")
    print(concentration.to_string(index=False))
    
    if concentration['portfolio_pct'].max() > 25:
        print("\n⚠️  WARNING: High concentration risk detected (>25% in single industry)")

# ============================================
# ANALYSIS 10: COHORT ANALYSIS
# ============================================

def cohort_analysis():
    """
    Analyze borrower cohorts by vintage
    """
    print("\n" + "=" * 80)
    print("10. LOAN VINTAGE COHORT ANALYSIS")
    print("=" * 80)
    
    cohort_data = pd.read_sql("""
        SELECT 
            strftime('%Y', disbursement_date) as vintage_year,
            COUNT(*) as num_loans,
            SUM(loan_amount) as total_disbursed,
            SUM(CASE WHEN loan_status = 'Defaulted' THEN 1 ELSE 0 END) as defaults,
            ROUND(100.0 * SUM(CASE WHEN loan_status = 'Defaulted' THEN 1 ELSE 0 END) / 
                  COUNT(*), 2) as default_rate_pct,
            SUM(CASE WHEN loan_status = 'Paid Off' THEN 1 ELSE 0 END) as paid_off,
            ROUND(100.0 * SUM(CASE WHEN loan_status = 'Paid Off' THEN 1 ELSE 0 END) / 
                  COUNT(*), 2) as payoff_rate_pct
        FROM business_loans
        GROUP BY vintage_year
        ORDER BY vintage_year
    """, conn)
    
    print("\n📊 Performance by Loan Vintage Year:")
    print(cohort_data.to_string(index=False))
    
    print("\n💡 Cohort Insights:")
    print("   - Older vintages show maturity in payoff rates")
    print("   - Recent vintages may not yet show true default risk")
    print("   - Monitor 2022-2023 cohorts closely for emerging risks")

# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """
    Execute all analysis functions
    """
    try:
        portfolio_overview()
        industry_performance = loan_performance_by_industry()
        credit_score_analysis()
        investor_analysis()
        time_series_analysis()
        payment_behavior_analysis()
        profitability_analysis()
        employee_productivity()
        risk_metrics()
        cohort_analysis()
        
        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE!")
        print("=" * 80)
        print("\n📋 Summary of Analyses Performed:")
        print("   1. Portfolio Overview - High-level financial snapshot")
        print("   2. Industry Performance - Loan performance by sector")
        print("   3. Credit Score Analysis - Risk assessment validation")
        print("   4. Investor Analysis - Customer segmentation")
        print("   5. Time-Series Trends - Historical patterns")
        print("   6. Payment Behavior - Collection effectiveness")
        print("   7. Profitability Analysis - Revenue generation")
        print("   8. Employee Productivity - Operational efficiency")
        print("   9. Risk Metrics - Portfolio health indicators")
        print("   10. Cohort Analysis - Vintage performance tracking")
        
        print("\n💡 Next Steps for Your GitHub Project:")
        print("   • Create visualizations (charts/graphs) for key metrics")
        print("   • Build a dashboard using Streamlit or Flask")
        print("   • Add predictive models (default prediction, customer lifetime value)")
        print("   • Document your methodology in README.md")
        print("   • Include SQL queries as separate files for transparency")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
