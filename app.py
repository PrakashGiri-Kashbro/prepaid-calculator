import streamlit as st
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
import calendar

# Function to calculate the breakdown
def calculate_prepaid_logic(premium, start_date, end_date):
    # INCLUSIVE COUNT: (End - Start) + 1
    total_days = (end_date - start_date).days + 1
    
    if total_days <= 0:
        return None, "Error: End date must be on or after start date."
    
    rate_per_day = premium / total_days
    
    # The 'Prepaid' period starts on January 1st of the year following the start date
    first_prepaid_day = date(start_date.year + 1, 1, 1)
    
    if end_date < first_prepaid_day:
        current_booking_days = total_days
        prepaid_days = 0
        monthly_breakdown = {}
    else:
        last_day_current_year = date(start_date.year, 12, 31)
        current_booking_days = (last_day_current_year - start_date).days + 1
        prepaid_days = (end_date - first_prepaid_day).days + 1
        
        monthly_breakdown = {}
        curr = first_prepaid_day
        while curr <= end_date:
            month_label = curr.strftime("%b")
            last_day_of_month = date(curr.year, curr.month, calendar.monthrange(curr.year, curr.month)[1])
            actual_end = min(last_day_of_month, end_date)
            days_in_this_month = (actual_end - curr).days + 1
            monthly_breakdown[month_label] = days_in_this_month
            curr = last_day_of_month + relativedelta(days=1)

    prepaid_amount = rate_per_day * prepaid_days
    current_amount = premium - prepaid_amount
    
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
st.set_page_config(page_title="Vehicle Prepaid Calculator (Bhutan)", page_icon="🇧🇹")

# Header and Developer Credentials
st.title("🇧🇹 Vehicle Prepaid Calculator")
st.markdown("---")

# Sidebar for inputs
st.sidebar.header("Calculation Settings")

# Dropdown for Item Type
item_type = st.sidebar.selectbox(
    "Select Document Type",
    [
        "Vehicle Register (Blue Book)",
        "Emission",
        "Road Worthiness (Fitness)",
        "Route Permit",
        "Insurance"
    ]
)

premium_input = st.sidebar.number_input("Amount (Nu.)", min_value=0.0, value=2550.00, step=0.01)
start_dt = st.sidebar.date_input("Start Date", value=date(2025, 12, 25))
end_dt = st.sidebar.date_input("End Date", value=date(2026, 12, 24))

if st.sidebar.button("Run Calculation"):
    res, error = calculate_prepaid_logic(premium_input, start_dt, end_dt)
    
    if error:
        st.error(error)
    else:
        st.header(f"Results for: {item_type}")
        
        # Display Results
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Days", f"{res['total_days']}")
        col2.metric("Rate / Day", f"Nu. {res['rate']:.4f}")
        col3.metric("Prepaid Days", f"{res['prepaid_days']}")

        st.divider()

        c1, c2 = st.columns(2)
        with c1:
            st.subheader(f"Current Period ({start_dt.year})")
            st.write(f"Days: **{res['current_days']}**")
            st.write(f"Booking Amount: **Nu. {res['current_amount']:.2f}**")
            
        with c2:
            st.subheader(f"Prepaid Period ({end_dt.year})")
            st.write(f"Days: **{res['prepaid_days']}**")
            st.write(f"Prepaid Amount: **Nu. {res['prepaid_amount']:.2f}**")

        if res["breakdown"]:
            st.subheader("Monthly Prepaid Breakdown (2026)")
            df = pd.DataFrame(list(res["breakdown"].items()), columns=["Month
