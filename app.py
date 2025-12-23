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
    # Balance amount goes to current year to ensure total matches exactly
    current_amount = round(premium - prepaid_amount, 2)
    
    return {
        "rate": rate_per_day,
        "total_days": total_days,
        "prepaid_days": prepaid_days,
        "current_days": current_booking_days,
        "prepaid_amount": prepaid_amount,
        "current_amount": current_amount,
        "breakdown": monthly_breakdown
    }, None

# --- Streamlit Layout ---
st.set_page_config(page_title="Vehicle Prepaid Calculator (Bhutan)", page_icon="🇧🇹", layout="wide")

# Bold and Clear Credentials Header
st.markdown("""
    <div style="text-align: center; background-color: #f9f9f9; padding: 25px; border-radius: 15px; border: 3px solid #ff4b4b; margin-bottom: 20px;">
        <h1 style="margin: 0; color: #333;">🇧🇹 Vehicle Prepaid Calculator</h1>
        <hr style="border: 1px solid #ddd;">
        <h2 style="margin: 10px; color: #ff4b4b; font-weight: bold; letter-spacing: 1px;">
            Developed by: PRAKASH GIRI (KASH BRO)
        </h2>
    </div>
    """, unsafe_allow_html=True)

# Sidebar for inputs
st.sidebar.header("Calculation Settings")
item_type = st.sidebar.selectbox("Select Document Type", list(GL_MAPPING.keys()))
gl_code = GL_MAPPING[item_type]

premium_input = st.sidebar.number_input("Amount (Nu.)", min_value=0.0, value=2550.00, step=0.01)
start_dt = st.sidebar.date_input("Start Date", value=date(2025, 12, 25))
end_dt = st.sidebar.date_input("End Date", value=date(2026, 12, 24))

if st.sidebar.button("Run Calculation"):
    res, error = calculate_prepaid_logic(premium_input, start_dt, end_dt)
    
    if error:
        st.error(error)
    else:
        st.header(f"Results for: {item_type}")
        st.info(f"**Period:** {start_dt.strftime('%d/%m/%Y')} to {end_dt.strftime('%d/%m/%Y')} | **Expense GL:** {gl_code}")
        
        # Dashboard Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Days", f"{res['total_days']}")
        m2.metric("Rate / Day", f"Nu. {res['rate']:.2f}")
        m3.metric("Current Days", f"{res['current_days']}")
        m4.metric("Prepaid Days", f"{res['prepaid_days']}")

        st.divider()

        # Split View
        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown(f"### Current Expense ({start_dt.year
