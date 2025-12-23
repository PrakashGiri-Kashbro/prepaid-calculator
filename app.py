import streamlit as st
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
import calendar

# Mapping Item Types to GL Codes
GL_MAPPING = {
    "Vehicle Register (Blue Book)": "450110 - R&M Vehicle",
    "Emission": "450110 - R&M Vehicle",
    "Road Worthiness (Fitness)": "450110 - R&M Vehicle",
    "Route Permit": "450110 - R&M Vehicle",
    "Insurance": "432200 - Insurance on Vehicle"
}

def calculate_prepaid_logic(premium, start_date, end_date):
    # INCLUSIVE COUNT: (End - Start) + 1
    total_days = (end_date - start_date).days + 1
    
    if total_days <= 0:
        return None, "Error: End date must be on or after start date."
    
    # Calculate rate per day rounded to 2 decimals
    rate_per_day = round(premium / total_days, 2)
    
    # Prepaid starts Jan 1st of the following year
    first_prepaid_day = date(start_date.year + 1, 1, 1)
    
    if end_date < first_prepaid_day:
        current_booking_days = total_days
        prepaid_days = 0
        monthly_breakdown = []
    else:
        last_day_current_year = date(start_date.year, 12, 31)
        current_booking_days = (last_day_current_year - start_date).days + 1
        prepaid_days = (end_date - first_prepaid_day).days + 1
        
        monthly_breakdown = []
        curr = first_prepaid_day
        while curr <= end_date:
            month_label = curr.strftime("%b %Y")
            last_day_of_month = date(curr.year, curr.month, calendar.monthrange(curr.year, curr.month)[1])
            actual_end = min(last_day_of_month, end_date)
            days_in_this_month = (actual_end - curr).days + 1
            
            monthly_breakdown.append({
                "Month": month_label,
                "Number of Days": days_in_this_month,
                "Amount (Nu.)": round(days_in_this_month * rate_per_day, 2)
            })
            curr = last_day_of_month + relativedelta(days=1)

    prepaid_amount = round(rate_per_day * prepaid_days, 2)
    current_amount = round(premium - prepaid_amount, 2)
    
    return {
        "rate": rate_per_day,
        "total_days": total_days,
        "prepaid_days": prepaid_days,
        "current_days": current_booking_days,
        "prepaid_amount": prepaid_amount
