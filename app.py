import streamlit as st
import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import calendar

def calculate_prepaid(premium, start_date, end_date):
    # Calculate Total Days in the Period
    total_days = (end_date - start_date).days
    if total_days <= 0:
        return None, "End date must be after start date."
    
    rate_per_day = premium / total_days
    
    # Identify the start of the prepaid period (Jan 1st of the following year)
    first_prepaid_day = date(start_date.year + 1, 1, 1)
    
    # If the policy ends before the next year starts, there are no prepaid days
    if end_date < first_prepaid_day:
        prepaid_days = 0
        current_booking_days = total_days
        monthly_breakdown = {}
    else:
        prepaid_days = (end_date - first_prepaid_day).days + 1
        current_booking_days = total_days - prepaid_days
        
        # Calculate monthly breakdown for the prepaid period
        monthly_breakdown = {}
        current_month_start = first_prepaid_day
        
        while current_month_start <= end_date:
            month_name = current_month_start.strftime("%b")
            # Last day of current month or end_date
            last_day_of_month = date(current_month_start.year, current_month_start.month, 
                                     calendar.monthrange(current_month_start.year, current_month_start.month)[1])
            
            period_end = min(last_day_of_month, end_date)
            days_in_month = (period_end - current_month_start).days + 1
            
            monthly_breakdown[month_name] = days_in_month
            current_month_start = last_day_of_month + relativedelta(days=1)

    prepaid_amount = rate_per_day * prepaid_days
    current_amount = premium - prepaid_amount
    
    return {
        "rate": rate_per_day,
        "total_days": total_days,
        "prepaid_days": prepaid_days,
        "prepaid_amount": prepaid_amount,
        "current_amount": current_amount,
        "breakdown": monthly_breakdown
    }, None

# Streamlit UI
st.set_page_config(page_title="Vehicle Prepaid Calculator", layout="centered")
st.title("🚗 Vehicle Prepaid Calculator")
st.write("Calculate your prepaid insurance amounts and monthly breakdowns.")

# Sidebar Inputs
st.sidebar.header("Input Parameters")
premium = st.sidebar.number_input("Premium Amount", min_value=0.0, value=2550.0, step=50.0)
start_date = st.sidebar.date_input("Start Date", value=date(2025, 12, 14))
end_date = st.sidebar.date_input("End Date", value=date(2026, 12, 14))

if st.sidebar.button("Calculate"):
    results, error = calculate_prepaid(premium, start_date, end_date)
    
    if error:
        st.error(error)
    else:
        # Layout columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Summary")
            st.metric("Total Days", results["total_days"])
            st.metric("Rate Per Day", f"${results['rate']:.4f}")
            st.metric("Total Prepaid Days", results["prepaid_days"])

        with col2:
            st.subheader("Financials")
            st.metric("Prepaid Amount", f"${results['prepaid_amount']:.2f}")
            st.metric("Current Booking Amount", f"${results['current_amount']:.2f}")

        # Monthly Breakdown Table
        st.subheader("Number of Prepaid Days (Monthly Breakdown)")
        if results["breakdown"]:
            df_breakdown = pd.DataFrame(list(results["breakdown"].items()), columns=["Month", "Days"])
            st.table(df_breakdown)
            st.info(f"Total calculated prepaid days: {df_breakdown['Days'].sum()}")
        else:
            st.info("No prepaid days (period falls entirely within the starting year).")

st.markdown("---")
st.caption("Logic based on standard calendar days. Rate per day = Premium / Total Days.")
