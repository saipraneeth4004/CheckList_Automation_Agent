"""
Script to generate sample month-end accounting data files
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import random

# Create sample data directories
COMPLETE_DIR = Path("sample_data/complete_month_end")
INCOMPLETE_DIR = Path("sample_data/incomplete_month_end")

COMPLETE_DIR.mkdir(parents=True, exist_ok=True)
INCOMPLETE_DIR.mkdir(parents=True, exist_ok=True)


def generate_bank_reconciliation():
    """Generate bank reconciliation sample"""
    data = {
        'Description': [
            'Opening Balance per Bank Statement', '', 
            'Add: Deposits in Transit', 
            'Deposit - Customer ABC', 
            'Deposit - Customer XYZ',
            'Total Deposits in Transit', '',
            'Less: Outstanding Checks',
            'Check #1001 - Supplier A',
            'Check #1002 - Supplier B',
            'Total Outstanding Checks', '',
            'Balance per Books'
        ],
        'Amount': [
            50000, '',
            '', 
            2500, 
            1800,
            4300, '',
            '',
            1200,
            900,
            2100, '',
            52200
        ]
    }
    df = pd.DataFrame(data)
    df.to_excel(COMPLETE_DIR / "bank_reconciliation_dec2024.xlsx", index=False)
    print("✅ Created bank_reconciliation_dec2024.xlsx")


def generate_ar_aging():
    """Generate AR aging report"""
    customers = ['ABC Corp', 'XYZ Ltd', 'LMN Inc', '123 Company', 'Tech Solutions']
    data = []
    
    for customer in customers:
        for i in range(random.randint(1, 3)):
            inv_num = f"INV-{random.randint(1000, 9999)}"
            total = random.randint(1000, 10000)
            current = total * random.uniform(0.4, 0.7)
            days_30 = (total - current) * random.uniform(0.3, 0.6)
            days_60 = (total - current - days_30) * random.uniform(0.2, 0.5)
            days_90 = total - current - days_30 - days_60
            
            data.append({
                'Customer Name': customer,
                'Invoice Number': inv_num,
                'Invoice Date': (datetime.now() - timedelta(days=random.randint(1, 120))).strftime('%Y-%m-%d'),
                'Total Amount': round(total, 2),
                'Current (0-30)': round(current, 2),
                '31-60 Days': round(days_30, 2),
                '61-90 Days': round(days_60, 2),
                '90+ Days': round(days_90, 2)
            })
    
    df = pd.DataFrame(data)
    df.to_excel(COMPLETE_DIR / "ar_aging_report_dec2024.xlsx", index=False)
    print("✅ Created ar_aging_report_dec2024.xlsx")


def generate_ap_aging():
    """Generate AP aging report"""
    vendors = ['Supplier A', 'Supplier B', 'Vendor Corp', 'ABC Supplies', 'Tech Vendor']
    data = []
    
    for vendor in vendors:
        for i in range(random.randint(1, 3)):
            inv_num = f"PINV-{random.randint(1000, 9999)}"
            total = random.randint(500, 8000)
            current = total * random.uniform(0.5, 0.8)
            days_30 = (total - current) * random.uniform(0.3, 0.6)
            days_60 = (total - current - days_30) * random.uniform(0.1, 0.4)
            days_90 = total - current - days_30 - days_60
            
            data.append({
                'Vendor Name': vendor,
                'Invoice Number': inv_num,
                'Invoice Date': (datetime.now() - timedelta(days=random.randint(1, 100))).strftime('%Y-%m-%d'),
                'Total Amount': round(total, 2),
                'Current (0-30)': round(current, 2),
                '31-60 Days': round(days_30, 2),
                '61-90 Days': round(days_60, 2),
                '90+ Days': round(days_90, 2)
            })
    
    df = pd.DataFrame(data)
    df.to_excel(COMPLETE_DIR / "ap_aging_report_dec2024.xlsx", index=False)
    print("✅ Created ap_aging_report_dec2024.xlsx")


def generate_accruals():
    """Generate accrual journal entries"""
    entries = [
        {'JE Number': 'JE-001', 'Date': '2024-12-31', 'Account Code': '5100', 'Account Name': 'Salaries Expense', 'Description': 'December salary accrual', 'Debit': 15000, 'Credit': 0},
        {'JE Number': 'JE-001', 'Date': '2024-12-31', 'Account Code': '2100', 'Account Name': 'Accrued Salaries', 'Description': 'December salary accrual', 'Debit': 0, 'Credit': 15000},
        {'JE Number': 'JE-002', 'Date': '2024-12-31', 'Account Code': '5200', 'Account Name': 'Utilities Expense', 'Description': 'December utilities accrual', 'Debit': 2500, 'Credit': 0},
        {'JE Number': 'JE-002', 'Date': '2024-12-31', 'Account Code': '2110', 'Account Name': 'Accrued Utilities', 'Description': 'December utilities accrual', 'Debit': 0, 'Credit': 2500},
    ]
    
    df = pd.DataFrame(entries)
    df.to_excel(COMPLETE_DIR / "accrual_journal_entries_dec2024.xlsx", index=False)
    print("✅ Created accrual_journal_entries_dec2024.xlsx")


def generate_gl_extract():
    """Generate GL extract / trial balance"""
    accounts = [
        ('1000', 'Cash', 0, 0, 52200),
        ('1100', 'Accounts Receivable', 0, 0, 35000),
        ('1200', 'Inventory', 0, 0, 28000),
        ('1500', 'Fixed Assets', 0, 0, 150000),
        ('2000', 'Accounts Payable', 0, 0, -22000),
        ('2100', 'Accrued Expenses', 0, 0, -17500),
        ('3000', 'Share Capital', 0, 0, -100000),
        ('4000', 'Revenue', 0, 0, -180000),
        ('5000', 'Cost of Sales', 0, 0, 85000),
        ('5100', 'Salaries', 0, 0, 45000),
        ('5200', 'Operating Expenses', 0, 0, 24300),
    ]
    
    data = []
    for code, name, debit, credit, balance in accounts:
        if balance > 0:
            debit = balance
        else:
            credit = abs(balance)
        
        data.append({
            'Account Code': code,
            'Account Name': name,
            'Debit': debit,
            'Credit': credit,
            'Balance': balance
        })
    
    df = pd.DataFrame(data)
    df.to_excel(COMPLETE_DIR / "gl_extract_trial_balance_dec2024.xlsx", index=False)
    print("✅ Created gl_extract_trial_balance_dec2024.xlsx")


def generate_prepayments():
    """Generate prepayments schedule"""
    data = [
        {'Asset': 'Insurance Premium', 'Total Amount': 12000, 'Start Date': '2024-01-01', 'Period (months)': 12, 'Monthly Amortization': 1000, 'Amortized to Date': 11000, 'Remaining Balance': 1000},
        {'Asset': 'Software License', 'Total Amount': 6000, 'Start Date': '2024-07-01', 'Period (months)': 12, 'Monthly Amortization': 500, 'Amortized to Date': 3000, 'Remaining Balance': 3000},
    ]
    
    df = pd.DataFrame(data)
    df.to_excel(COMPLETE_DIR / "prepayments_schedule_dec2024.xlsx", index=False)
    print("✅ Created prepayments_schedule_dec2024.xlsx")


def generate_fixed_assets():
    """Generate fixed assets register"""
    data = [
        {'Asset': 'Computer Equipment', 'Purchase Date': '2023-01-15', 'Cost': 50000, 'Useful Life (years)': 5, 'Annual Depreciation': 10000, 'Accumulated Depreciation': 20000, 'Net Book Value': 30000},
        {'Asset': 'Office Furniture', 'Purchase Date': '2022-06-01', 'Cost': 30000, 'Useful Life (years)': 10, 'Annual Depreciation': 3000, 'Accumulated Depreciation': 7500, 'Net Book Value': 22500},
        {'Asset': 'Vehicles', 'Purchase Date': '2021-03-20', 'Cost': 70000, 'Useful Life (years)': 7, 'Annual Depreciation': 10000, 'Accumulated Depreciation': 37500, 'Net Book Value': 32500},
    ]
    
    df = pd.DataFrame(data)
    df.to_excel(COMPLETE_DIR / "fixed_assets_register_dec2024.xlsx", index=False)
    print("✅ Created fixed_assets_register_dec2024.xlsx")


def generate_revenue_schedule():
    """Generate revenue recognition schedule"""
    data = [
        {'Product/Service': 'Product A', 'Contract Value': 100000, 'Start Date': '2024-01-01', 'End Date': '2024-12-31', 'Period': 'December 2024', 'Revenue Recognized': 8333, 'Cumulative Revenue': 100000},
        {'Product/Service': 'Service B', 'Contract Value': 60000, 'Start Date': '2024-06-01', 'End Date': '2025-05-31', 'Period': 'December 2024', 'Revenue Recognized': 5000, 'Cumulative Revenue': 35000},
    ]
    
    df = pd.DataFrame(data)
    df.to_excel(COMPLETE_DIR / "revenue_schedule_dec2024.xlsx", index=False)
    print("✅ Created revenue_schedule_dec2024.xlsx")


def generate_expense_analysis():
    """Generate expense analysis"""
    data = [
        {'Category': 'Salaries & Wages', 'Budget': 50000, 'Actual': 45000, 'Variance': -5000, 'Variance %': -10.0},
        {'Category': 'Rent', 'Budget': 12000, 'Actual': 12000, 'Variance': 0, 'Variance %': 0.0},
        {'Category': 'Utilities', 'Budget': 3000, 'Actual': 3200, 'Variance': 200, 'Variance %': 6.7},
        {'Category': 'Marketing', 'Budget': 8000, 'Actual': 9500, 'Variance': 1500, 'Variance %': 18.8},
        {'Category': 'Office Supplies', 'Budget': 2000, 'Actual': 1800, 'Variance': -200, 'Variance %': -10.0},
    ]
    
    df = pd.DataFrame(data)
    df.to_excel(COMPLETE_DIR / "expense_analysis_dec2024.xlsx", index=False)
    print("✅ Created expense_analysis_dec2024.xlsx")


def generate_intercompany_recon():
    """Generate intercompany reconciliation"""
    data = [
        {'Entity': 'Parent Company', 'Counterparty': 'Subsidiary A', 'Account': 'Intercompany Receivable', 'Our Balance': 15000, 'Their Balance': 15000, 'Difference': 0, 'Status': 'Reconciled'},
        {'Entity': 'Parent Company', 'Counterparty': 'Subsidiary B', 'Account': 'Intercompany Payable', 'Our Balance': -8000, 'Their Balance': -8000, 'Difference': 0, 'Status': 'Reconciled'},
    ]
    
    df = pd.DataFrame(data)
    df.to_excel(COMPLETE_DIR / "intercompany_reconciliation_dec2024.xlsx", index=False)
    print("✅ Created intercompany_reconciliation_dec2024.xlsx")


def generate_incomplete_samples():
    """Generate incomplete samples (missing some files)"""
    # Copy only some files to incomplete directory
    import shutil
    
    files_to_copy = [
        "bank_reconciliation_dec2024.xlsx",
        "ar_aging_report_dec2024.xlsx",
        "gl_extract_trial_balance_dec2024.xlsx"
    ]
    
    for file in files_to_copy:
        src = COMPLETE_DIR / file
        dst = INCOMPLETE_DIR / file
        if src.exists():
            shutil.copy2(src, dst)
    
    print(f"\n✅ Copied {len(files_to_copy)} files to incomplete folder")
    print("❌ Missing files in incomplete folder (intentionally):")
    all_files = list(COMPLETE_DIR.glob("*.xlsx"))
    missing = [f.name for f in all_files if f.name not in files_to_copy]
    for m in missing:
        print(f"   - {m}")


def main():
    """Generate all sample files"""
    print("🚀 Generating sample month-end data files...\n")
    print(f"📁 Complete folder: {COMPLETE_DIR}")
    print(f"📁 Incomplete folder: {INCOMPLETE_DIR}\n")
    
    # Generate complete set
    print("Generating complete month-end folder:")
    generate_bank_reconciliation()
    generate_ar_aging()
    generate_ap_aging()
    generate_accruals()
    generate_gl_extract()
    generate_prepayments()
    generate_fixed_assets()
    generate_revenue_schedule()
    generate_expense_analysis()
    generate_intercompany_recon()
    
    # Generate incomplete set
    print("\nGenerating incomplete month-end folder:")
    generate_incomplete_samples()
    
    print("\n✅ Sample data generation complete!")
    print(f"\nTotal files in complete folder: {len(list(COMPLETE_DIR.glob('*.xlsx')))}")
    print(f"Total files in incomplete folder: {len(list(INCOMPLETE_DIR.glob('*.xlsx')))}")


if __name__ == "__main__":
    main()
