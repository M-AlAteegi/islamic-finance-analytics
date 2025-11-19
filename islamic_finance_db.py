"""
Islamic Finance Company Database Simulation
============================================

This script simulates a complete Islamic finance company that:
1. Issues Sukuk (Islamic bonds) to investors
2. Uses that capital to provide business financing
3. Distributes profits back to Sukuk holders
4. Tracks all transactions and employee activities

The simulation follows Islamic finance principles:
- No interest (riba) - instead profit-sharing
- Asset-backed financing
- Ethical business practices
"""

import sqlite3
import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import json

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Initialize Faker for generating realistic data
fake = Faker()
Faker.seed(42)

# ============================================
# CONFIGURATION & PARAMETERS
# ============================================

# Number of records to generate
NUM_EMPLOYEES = 50
NUM_INVESTORS = 500
NUM_BORROWERS = 300
NUM_SUKUK_ISSUANCES = 10
NUM_SUKUK_PURCHASES = 1500
NUM_LOANS = 250
NUM_LOAN_PAYMENTS = 2000
NUM_PROFIT_DISTRIBUTIONS = 800

# Financial parameters
MIN_SUKUK_AMOUNT = 1000
MAX_SUKUK_AMOUNT = 100000
MIN_LOAN_AMOUNT = 10000
MAX_LOAN_AMOUNT = 500000
EXPECTED_ANNUAL_RETURN = 0.08  # 8% expected return for Sukuk holders
DEFAULT_RATE = 0.05  # 5% of loans may default

# Date ranges
START_DATE = datetime(2020, 1, 1)
END_DATE = datetime(2024, 10, 31)

# ============================================
# DATABASE SETUP
# ============================================

def create_database():
    """
    Creates SQLite database with all necessary tables.
    SQLite is perfect for this project - it's file-based, portable, and requires no server.
    """
    conn = sqlite3.connect('islamic_finance_company.db')
    cursor = conn.cursor()
    
    # Drop existing tables if they exist (for clean restart)
    tables = ['employees', 'investors', 'borrowers', 'sukuk_issuances', 
              'sukuk_purchases', 'business_loans', 'loan_payments', 'profit_distributions']
    for table in tables:
        cursor.execute(f'DROP TABLE IF EXISTS {table}')
    
    # ============================================
    # TABLE 1: EMPLOYEES
    # ============================================
    cursor.execute('''
    CREATE TABLE employees (
        employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        department TEXT,  -- Finance, Operations, Risk Management, Customer Service
        position TEXT,
        hire_date DATE,
        salary REAL,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    # ============================================
    # TABLE 2: INVESTORS (Sukuk buyers)
    # ============================================
    cursor.execute('''
    CREATE TABLE investors (
        investor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        address TEXT,
        city TEXT,
        country TEXT,
        date_of_birth DATE,
        registration_date DATE,
        risk_profile TEXT,  -- Conservative, Moderate, Aggressive
        total_invested REAL DEFAULT 0,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    # ============================================
    # TABLE 3: BORROWERS (Businesses seeking financing)
    # ============================================
    cursor.execute('''
    CREATE TABLE borrowers (
        borrower_id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_name TEXT NOT NULL,
        contact_person TEXT,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        address TEXT,
        city TEXT,
        country TEXT,
        industry TEXT,  -- Technology, Retail, Manufacturing, Healthcare, etc.
        registration_date DATE,
        credit_score INTEGER,  -- 300-850 scale
        annual_revenue REAL,
        num_employees INTEGER,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    # ============================================
    # TABLE 4: SUKUK ISSUANCES
    # ============================================
    cursor.execute('''
    CREATE TABLE sukuk_issuances (
        sukuk_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sukuk_name TEXT NOT NULL,
        issue_date DATE,
        maturity_date DATE,
        total_amount REAL,
        expected_return_rate REAL,  -- Expected profit rate (not interest!)
        minimum_investment REAL,
        underlying_assets TEXT,  -- Description of assets backing the Sukuk
        status TEXT,  -- Active, Matured, Cancelled
        issued_by_employee_id INTEGER,
        FOREIGN KEY (issued_by_employee_id) REFERENCES employees(employee_id)
    )
    ''')
    
    # ============================================
    # TABLE 5: SUKUK PURCHASES
    # ============================================
    cursor.execute('''
    CREATE TABLE sukuk_purchases (
        purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
        investor_id INTEGER,
        sukuk_id INTEGER,
        purchase_date DATE,
        amount REAL,
        units REAL,  -- Number of Sukuk certificates
        processed_by_employee_id INTEGER,
        FOREIGN KEY (investor_id) REFERENCES investors(investor_id),
        FOREIGN KEY (sukuk_id) REFERENCES sukuk_issuances(sukuk_id),
        FOREIGN KEY (processed_by_employee_id) REFERENCES employees(employee_id)
    )
    ''')
    
    # ============================================
    # TABLE 6: BUSINESS LOANS
    # ============================================
    cursor.execute('''
    CREATE TABLE business_loans (
        loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        borrower_id INTEGER,
        loan_amount REAL,
        disbursement_date DATE,
        maturity_date DATE,
        profit_rate REAL,  -- Profit-sharing rate (not interest)
        purpose TEXT,  -- Equipment, Expansion, Working Capital, etc.
        loan_status TEXT,  -- Active, Paid Off, Defaulted
        collateral_description TEXT,
        approved_by_employee_id INTEGER,
        outstanding_balance REAL,
        FOREIGN KEY (borrower_id) REFERENCES borrowers(borrower_id),
        FOREIGN KEY (approved_by_employee_id) REFERENCES employees(employee_id)
    )
    ''')
    
    # ============================================
    # TABLE 7: LOAN PAYMENTS
    # ============================================
    cursor.execute('''
    CREATE TABLE loan_payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        loan_id INTEGER,
        payment_date DATE,
        payment_amount REAL,
        principal_amount REAL,
        profit_amount REAL,
        remaining_balance REAL,
        payment_status TEXT,  -- On Time, Late, Missed
        FOREIGN KEY (loan_id) REFERENCES business_loans(loan_id)
    )
    ''')
    
    # ============================================
    # TABLE 8: PROFIT DISTRIBUTIONS (to Sukuk holders)
    # ============================================
    cursor.execute('''
    CREATE TABLE profit_distributions (
        distribution_id INTEGER PRIMARY KEY AUTOINCREMENT,
        purchase_id INTEGER,
        distribution_date DATE,
        amount REAL,
        period_start DATE,
        period_end DATE,
        processed_by_employee_id INTEGER,
        FOREIGN KEY (purchase_id) REFERENCES sukuk_purchases(purchase_id),
        FOREIGN KEY (processed_by_employee_id) REFERENCES employees(employee_id)
    )
    ''')
    
    conn.commit()
    print("✓ Database schema created successfully!")
    return conn

# ============================================
# DATA GENERATION FUNCTIONS
# ============================================

def generate_employees(conn, num_employees):
    """
    Generate employee data.
    Departments simulate a real Islamic finance company structure.
    """
    print(f"\nGenerating {num_employees} employees...")
    
    departments = {
        'Sharia Board': ['Sharia Scholar', 'Compliance Officer'],
        'Finance': ['CFO', 'Financial Analyst', 'Accountant', 'Treasury Manager'],
        'Risk Management': ['Risk Manager', 'Credit Analyst', 'Compliance Analyst'],
        'Operations': ['Operations Manager', 'Loan Officer', 'Investment Officer'],
        'Customer Service': ['Customer Service Manager', 'Support Specialist', 'Relationship Manager'],
        'IT': ['IT Manager', 'Systems Administrator', 'Data Analyst'],
        'HR': ['HR Manager', 'Recruiter']
    }
    
    employees = []
    for i in range(num_employees):
        dept = random.choice(list(departments.keys()))
        position = random.choice(departments[dept])
        
        # Salary based on position level
        if 'Manager' in position or 'CFO' in position or 'Scholar' in position:
            salary = random.randint(80000, 150000)
        elif 'Analyst' in position or 'Officer' in position:
            salary = random.randint(50000, 85000)
        else:
            salary = random.randint(35000, 60000)
        
        hire_date = fake.date_between(start_date='-10y', end_date='-1m')
        
        employees.append({
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.unique.email(),
            'phone': fake.phone_number(),
            'department': dept,
            'position': position,
            'hire_date': hire_date,
            'salary': salary,
            'is_active': 1 if random.random() > 0.1 else 0  # 90% active
        })
    
    df = pd.DataFrame(employees)
    df.to_sql('employees', conn, if_exists='append', index=False)
    print(f"✓ Generated {len(employees)} employees")
    return df

def generate_investors(conn, num_investors):
    """
    Generate investor profiles.
    These are individuals who buy Sukuk to invest their money.
    """
    print(f"\nGenerating {num_investors} investors...")
    
    risk_profiles = ['Conservative', 'Moderate', 'Aggressive']
    
    investors = []
    for i in range(num_investors):
        registration_date = fake.date_between(start_date=START_DATE, end_date=END_DATE)
        dob = fake.date_of_birth(minimum_age=25, maximum_age=75)
        
        investors.append({
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.unique.email(),
            'phone': fake.phone_number(),
            'address': fake.street_address(),
            'city': fake.city(),
            'country': fake.country(),
            'date_of_birth': dob,
            'registration_date': registration_date,
            'risk_profile': random.choices(risk_profiles, weights=[0.5, 0.35, 0.15])[0],
            'total_invested': 0,  # Will be updated when purchases are made
            'is_active': 1
        })
    
    df = pd.DataFrame(investors)
    df.to_sql('investors', conn, if_exists='append', index=False)
    print(f"✓ Generated {len(investors)} investors")
    return df

def generate_borrowers(conn, num_borrowers):
    """
    Generate business borrowers seeking financing.
    These represent real businesses in various industries.
    """
    print(f"\nGenerating {num_borrowers} borrowers...")
    
    industries = [
        'Technology', 'Retail', 'Manufacturing', 'Healthcare', 
        'Education', 'Real Estate', 'Food & Beverage', 'Agriculture',
        'Construction', 'Transportation', 'Professional Services'
    ]
    
    borrowers = []
    for i in range(num_borrowers):
        industry = random.choice(industries)
        registration_date = fake.date_between(start_date=START_DATE, end_date=END_DATE)
        
        # Credit score follows normal distribution centered at 680
        credit_score = int(np.clip(np.random.normal(680, 60), 300, 850))
        
        # Revenue and employees correlate with industry
        if industry in ['Technology', 'Healthcare', 'Manufacturing']:
            annual_revenue = random.randint(500000, 5000000)
            num_employees = random.randint(20, 200)
        else:
            annual_revenue = random.randint(100000, 2000000)
            num_employees = random.randint(5, 100)
        
        borrowers.append({
            'business_name': fake.company(),
            'contact_person': fake.name(),
            'email': fake.unique.email(),
            'phone': fake.phone_number(),
            'address': fake.street_address(),
            'city': fake.city(),
            'country': fake.country(),
            'industry': industry,
            'registration_date': registration_date,
            'credit_score': credit_score,
            'annual_revenue': annual_revenue,
            'num_employees': num_employees,
            'is_active': 1
        })
    
    df = pd.DataFrame(borrowers)
    df.to_sql('borrowers', conn, if_exists='append', index=False)
    print(f"✓ Generated {len(borrowers)} borrowers")
    return df

def generate_sukuk_issuances(conn, num_sukuk):
    """
    Generate Sukuk issuances.
    Each Sukuk represents a pool of assets that investors can buy into.
    """
    print(f"\nGenerating {num_sukuk} Sukuk issuances...")
    
    # Get employee IDs from Finance department to assign as issuers
    employees_df = pd.read_sql("SELECT employee_id FROM employees WHERE department='Finance'", conn)
    employee_ids = employees_df['employee_id'].tolist()
    
    sukuk_types = ['Ijara', 'Mudaraba', 'Musharaka', 'Murabaha', 'Istisna']
    underlying_assets_options = [
        'Commercial Real Estate Portfolio',
        'Manufacturing Equipment Pool',
        'Technology Infrastructure',
        'Healthcare Facilities',
        'Transportation Fleet',
        'Renewable Energy Projects',
        'Educational Institutions'
    ]
    
    sukuk_list = []
    for i in range(num_sukuk):
        issue_date = fake.date_between(start_date=START_DATE, end_date='-6m')
        maturity_years = random.choice([2, 3, 5, 7, 10])
        maturity_date = issue_date + timedelta(days=maturity_years*365)
        
        # Total amount varies based on maturity
        total_amount = random.randint(1000000, 10000000)
        
        # Expected return rate: longer maturity = higher return
        base_rate = 0.05
        expected_return = base_rate + (maturity_years * 0.005) + random.uniform(-0.01, 0.01)
        
        status = 'Active' if maturity_date > datetime.now().date() else 'Matured'
        
        sukuk_list.append({
            'sukuk_name': f'{random.choice(sukuk_types)} Sukuk Series {chr(65+i)}',
            'issue_date': issue_date,
            'maturity_date': maturity_date,
            'total_amount': total_amount,
            'expected_return_rate': round(expected_return, 4),
            'minimum_investment': random.choice([1000, 5000, 10000]),
            'underlying_assets': random.choice(underlying_assets_options),
            'status': status,
            'issued_by_employee_id': random.choice(employee_ids)
        })
    
    df = pd.DataFrame(sukuk_list)
    df.to_sql('sukuk_issuances', conn, if_exists='append', index=False)
    print(f"✓ Generated {len(sukuk_list)} Sukuk issuances")
    return df

def generate_sukuk_purchases(conn, num_purchases):
    """
    Generate Sukuk purchase transactions.
    This is where investors buy Sukuk certificates.
    """
    print(f"\nGenerating {num_purchases} Sukuk purchases...")
    
    # Get relevant IDs
    investors_df = pd.read_sql("SELECT investor_id FROM investors", conn)
    sukuk_df = pd.read_sql("SELECT sukuk_id, issue_date, minimum_investment FROM sukuk_issuances", conn)
    employees_df = pd.read_sql("SELECT employee_id FROM employees WHERE department IN ('Operations', 'Customer Service')", conn)
    
    investor_ids = investors_df['investor_id'].tolist()
    employee_ids = employees_df['employee_id'].tolist()
    
    purchases = []
    for i in range(num_purchases):
        sukuk_row = sukuk_df.sample(1).iloc[0]
        sukuk_id = sukuk_row['sukuk_id']
        issue_date = pd.to_datetime(sukuk_row['issue_date'])
        min_investment = sukuk_row['minimum_investment']
        
        # Purchase date is after issue date
        issue_date_obj = pd.to_datetime(issue_date).date()
        purchase_date = fake.date_between(
            start_date=issue_date_obj, 
            end_date=min(datetime.now().date(), issue_date_obj + timedelta(days=365))
        )
        
        # Investment amount based on investor risk profile (would need to join, simplifying here)
        amount = random.randint(int(min_investment), int(min_investment * 50))
        units = amount / 1000  # Each unit is 1000
        
        purchases.append({
            'investor_id': random.choice(investor_ids),
            'sukuk_id': sukuk_id,
            'purchase_date': purchase_date,
            'amount': amount,
            'units': units,
            'processed_by_employee_id': random.choice(employee_ids)
        })
    
    df = pd.DataFrame(purchases)
    df.to_sql('sukuk_purchases', conn, if_exists='append', index=False)
    
    # Update total_invested for investors
    conn.execute('''
        UPDATE investors 
        SET total_invested = (
            SELECT COALESCE(SUM(amount), 0) 
            FROM sukuk_purchases 
            WHERE sukuk_purchases.investor_id = investors.investor_id
        )
    ''')
    conn.commit()
    
    print(f"✓ Generated {len(purchases)} Sukuk purchases")
    return df

def generate_business_loans(conn, num_loans):
    """
    Generate business loans.
    This is where the company uses Sukuk capital to finance businesses.
    """
    print(f"\nGenerating {num_loans} business loans...")
    
    # Get relevant IDs
    borrowers_df = pd.read_sql("SELECT borrower_id, credit_score FROM borrowers", conn)
    employees_df = pd.read_sql("SELECT employee_id FROM employees WHERE department='Risk Management' OR position LIKE '%Loan Officer%'", conn)
    
    employee_ids = employees_df['employee_id'].tolist()
    
    loan_purposes = [
        'Equipment Purchase', 'Business Expansion', 'Working Capital',
        'Real Estate Acquisition', 'Inventory Financing', 'Technology Upgrade',
        'Facility Renovation', 'Debt Consolidation'
    ]
    
    collateral_types = [
        'Real Estate Property', 'Equipment and Machinery', 'Inventory',
        'Accounts Receivable', 'Business Assets', 'Personal Guarantee'
    ]
    
    loans = []
    for i in range(num_loans):
        borrower_row = borrowers_df.sample(1).iloc[0]
        borrower_id = borrower_row['borrower_id']
        credit_score = borrower_row['credit_score']
        
        # Loan amount correlates with credit score
        if credit_score >= 750:
            loan_amount = random.randint(100000, 500000)
        elif credit_score >= 650:
            loan_amount = random.randint(50000, 250000)
        else:
            loan_amount = random.randint(10000, 100000)
        
        disbursement_date = fake.date_between(start_date=START_DATE, end_date=END_DATE)
        loan_term_months = random.choice([12, 24, 36, 48, 60])
        maturity_date = disbursement_date + timedelta(days=loan_term_months*30)
        
        # Profit rate inversely correlates with credit score
        base_profit_rate = 0.10
        if credit_score >= 750:
            profit_rate = base_profit_rate - 0.02
        elif credit_score >= 650:
            profit_rate = base_profit_rate
        else:
            profit_rate = base_profit_rate + 0.03
        
        profit_rate += random.uniform(-0.01, 0.01)
        
        # Determine if loan defaulted (based on DEFAULT_RATE)
        if random.random() < DEFAULT_RATE:
            loan_status = 'Defaulted'
            outstanding_balance = loan_amount * random.uniform(0.3, 0.9)
        elif maturity_date < datetime.now().date():
            loan_status = 'Paid Off'
            outstanding_balance = 0
        else:
            loan_status = 'Active'
            # Calculate outstanding based on time elapsed
            days_elapsed = (datetime.now().date() - disbursement_date).days
            total_days = (maturity_date - disbursement_date).days
            if total_days > 0:
                progress = min(days_elapsed / total_days, 1.0)
                outstanding_balance = loan_amount * (1 - progress * 0.7)  # Paid down 70% over time
            else:
                outstanding_balance = loan_amount
        
        loans.append({
            'borrower_id': borrower_id,
            'loan_amount': loan_amount,
            'disbursement_date': disbursement_date,
            'maturity_date': maturity_date,
            'profit_rate': round(profit_rate, 4),
            'purpose': random.choice(loan_purposes),
            'loan_status': loan_status,
            'collateral_description': random.choice(collateral_types),
            'approved_by_employee_id': random.choice(employee_ids),
            'outstanding_balance': round(outstanding_balance, 2)
        })
    
    df = pd.DataFrame(loans)
    df.to_sql('business_loans', conn, if_exists='append', index=False)
    print(f"✓ Generated {len(loans)} business loans")
    return df

def generate_loan_payments(conn, num_payments):
    """
    Generate loan payment records.
    Each active loan should have multiple payment records.
    """
    print(f"\nGenerating {num_payments} loan payments...")
    
    loans_df = pd.read_sql('''
        SELECT loan_id, loan_amount, disbursement_date, maturity_date, 
               profit_rate, loan_status, outstanding_balance
        FROM business_loans
    ''', conn)
    
    all_payments = []
    
    for _, loan in loans_df.iterrows():
        loan_id = loan['loan_id']
        loan_amount = loan['loan_amount']
        disbursement_date = pd.to_datetime(loan['disbursement_date']).date()
        maturity_date = pd.to_datetime(loan['maturity_date']).date()
        profit_rate = loan['profit_rate']
        loan_status = loan['loan_status']
        
        # Calculate monthly payment (simplified amortization)
        months = max(1, int((maturity_date - disbursement_date).days / 30))
        total_profit = loan_amount * profit_rate * (months / 12)
        total_to_pay = loan_amount + total_profit
        monthly_payment = total_to_pay / months
        
        # Generate payments based on loan status
        if loan_status == 'Paid Off':
            num_loan_payments = months
        elif loan_status == 'Defaulted':
            num_loan_payments = random.randint(int(months * 0.3), int(months * 0.7))
        else:  # Active
            months_elapsed = int((datetime.now().date() - disbursement_date).days / 30)
            num_loan_payments = min(months_elapsed, months)
        
        remaining = loan_amount
        for payment_num in range(num_loan_payments):
            payment_date = disbursement_date + timedelta(days=30 * (payment_num + 1))
            
            if payment_date > datetime.now().date():
                break
            
            # Calculate payment split between principal and profit
            profit_portion = remaining * (profit_rate / 12)
            principal_portion = monthly_payment - profit_portion
            
            # Determine payment status (95% on time, 3% late, 2% missed)
            payment_status_choice = random.choices(
                ['On Time', 'Late', 'Missed'],
                weights=[0.95, 0.03, 0.02]
            )[0]
            
            if payment_status_choice == 'Missed':
                actual_payment = 0
                actual_principal = 0
                actual_profit = 0
            elif payment_status_choice == 'Late':
                actual_payment = monthly_payment * random.uniform(0.5, 0.9)
                actual_principal = actual_payment * (principal_portion / monthly_payment)
                actual_profit = actual_payment * (profit_portion / monthly_payment)
            else:
                actual_payment = monthly_payment
                actual_principal = principal_portion
                actual_profit = profit_portion
            
            remaining = max(0, remaining - actual_principal)
            
            all_payments.append({
                'loan_id': loan_id,
                'payment_date': payment_date,
                'payment_amount': round(actual_payment, 2),
                'principal_amount': round(actual_principal, 2),
                'profit_amount': round(actual_profit, 2),
                'remaining_balance': round(remaining, 2),
                'payment_status': payment_status_choice
            })
            
            # Stop if we have enough payments overall
            if len(all_payments) >= num_payments:
                break
        
        if len(all_payments) >= num_payments:
            break
    
    df = pd.DataFrame(all_payments[:num_payments])
    df.to_sql('loan_payments', conn, if_exists='append', index=False)
    print(f"✓ Generated {len(df)} loan payments")
    return df

def generate_profit_distributions(conn, num_distributions):
    """
    Generate profit distributions to Sukuk holders.
    This is the return investors receive from their Sukuk investments.
    """
    print(f"\nGenerating {num_distributions} profit distributions...")
    
    purchases_df = pd.read_sql('''
        SELECT sp.purchase_id, sp.investor_id, sp.sukuk_id, sp.purchase_date, 
               sp.amount, si.expected_return_rate
        FROM sukuk_purchases sp
        JOIN sukuk_issuances si ON sp.sukuk_id = si.sukuk_id
    ''', conn)
    
    employees_df = pd.read_sql(
        "SELECT employee_id FROM employees WHERE department='Finance'", 
        conn
    )
    employee_ids = employees_df['employee_id'].tolist()
    
    distributions = []
    
    for _, purchase in purchases_df.sample(min(len(purchases_df), num_distributions)).iterrows():
        purchase_date = pd.to_datetime(purchase['purchase_date']).date()
        amount_invested = purchase['amount']
        expected_return_rate = purchase['expected_return_rate']
        
        # Generate quarterly distributions
        quarters_since_purchase = int((datetime.now().date() - purchase_date).days / 90)
        
        for quarter in range(min(quarters_since_purchase, 8)):  # Max 8 quarters (2 years)
            period_start = purchase_date + timedelta(days=90 * quarter)
            period_end = period_start + timedelta(days=90)
            distribution_date = period_end
            
            if distribution_date > datetime.now().date():
                break
            
            # Quarterly profit distribution
            quarterly_profit = (amount_invested * expected_return_rate / 4) * random.uniform(0.9, 1.1)
            
            distributions.append({
                'purchase_id': purchase['purchase_id'],
                'distribution_date': distribution_date,
                'amount': round(quarterly_profit, 2),
                'period_start': period_start,
                'period_end': period_end,
                'processed_by_employee_id': random.choice(employee_ids)
            })
            
            if len(distributions) >= num_distributions:
                break
        
        if len(distributions) >= num_distributions:
            break
    
    df = pd.DataFrame(distributions[:num_distributions])
    df.to_sql('profit_distributions', conn, if_exists='append', index=False)
    print(f"✓ Generated {len(df)} profit distributions")
    return df

# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """
    Main function to orchestrate the entire database generation process.
    """
    print("=" * 60)
    print("ISLAMIC FINANCE COMPANY DATABASE GENERATION")
    print("=" * 60)
    
    # Create database and tables
    conn = create_database()
    
    # Generate all data in proper order (respecting foreign key relationships)
    print("\n" + "=" * 60)
    print("GENERATING DATA")
    print("=" * 60)
    
    employees_df = generate_employees(conn, NUM_EMPLOYEES)
    investors_df = generate_investors(conn, NUM_INVESTORS)
    borrowers_df = generate_borrowers(conn, NUM_BORROWERS)
    sukuk_df = generate_sukuk_issuances(conn, NUM_SUKUK_ISSUANCES)
    purchases_df = generate_sukuk_purchases(conn, NUM_SUKUK_PURCHASES)
    loans_df = generate_business_loans(conn, NUM_LOANS)
    payments_df = generate_loan_payments(conn, NUM_LOAN_PAYMENTS)
    distributions_df = generate_profit_distributions(conn, NUM_PROFIT_DISTRIBUTIONS)
    
    # Print summary statistics
    print("\n" + "=" * 60)
    print("DATABASE SUMMARY")
    print("=" * 60)
    
    cursor = conn.cursor()
    tables = ['employees', 'investors', 'borrowers', 'sukuk_issuances', 
              'sukuk_purchases', 'business_loans', 'loan_payments', 'profit_distributions']
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table.upper()}: {count:,} records")
    
    print("\n" + "=" * 60)
    print("✓ DATABASE GENERATION COMPLETE!")
    print("=" * 60)
    print(f"\nDatabase saved as: islamic_finance_company.db")
    print(f"You can now run analytics on this database!")
    
    conn.close()

if __name__ == "__main__":
    main()
