import math
from datetime import timedelta, date

def calculate_emi(loan_amount, annual_interest_rate, tenure_months, disbursement_date, monthly_income):
    interest_rate = max(annual_interest_rate, 14)
    
    monthly_interest_rate = interest_rate / (12 * 100)
    max_emi = 0.6 * monthly_income
    emi = loan_amount * monthly_interest_rate * ((1 + monthly_interest_rate) ** tenure_months) / ((1 + monthly_interest_rate) ** tenure_months - 1)
    
    if emi > max_emi:
        raise ValueError(f"EMI amount {emi} exceeds 60% of the user's monthly income")

    emi_schedule = []
    remaining_principal = loan_amount
    total_interest = 0
    
    # Start EMI from the 1st of the month after the disbursement date
    next_emi_date = date(disbursement_date.year, disbursement_date.month, 1) + timedelta(days=31)
    next_emi_date = date(next_emi_date.year, next_emi_date.month, 1)
    
    for month in range(tenure_months):
        interest_for_month = remaining_principal * monthly_interest_rate
        total_interest += interest_for_month
        
        principal_for_month = emi - interest_for_month
        
        if month == tenure_months - 1:
            principal_for_month = remaining_principal
            emi = principal_for_month + interest_for_month
        
        # Add the EMI details to the schedule
        emi_schedule.append({
            "Date": next_emi_date,
            "Principal": round(principal_for_month, 2),
            "Interest": round(interest_for_month, 2),
            "EMI_Amount": round(emi, 2)
        })
        
        remaining_principal -= principal_for_month
        
        # Move to the next EMI date (next month)
        next_emi_date = next_emi_date + timedelta(days=31)
        next_emi_date = date(next_emi_date.year, next_emi_date.month, 1)
    
    # Ensure total interest earned is more than 10,000
    if total_interest <= 10000:
        raise ValueError("Total interest earned should be greater than ₹10,000")
    
    return emi_schedule, round(total_interest, 2)
