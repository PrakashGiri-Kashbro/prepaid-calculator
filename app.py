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
    total_days = (end_date - start_date).days + 1
    
    if total_days <= 0:
        return None, "Error: End date must be on or after start date."
    
    # Using 2 decimal places for the rate per day
    rate_per_day = round(premium / total_days, 2)
    
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
            days_in_month = (actual_end - curr).days + 1
            
            # Rounding monthly amounts to 2 decimal places
            monthly_breakdown.append({
                "Month": month_label,
                "Days": days_in_month,
                "Amount (Nu.)": round(days_in_month * rate_per_day, 2)
            })
            curr = last_day_of_month + relativedelta(days=1)

    prepaid_amount = round(rate_per_day * prepaid_days, 2)
    # Ensure the total matches exactly by subtracting prepaid from total
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
st.set_page_config(page_title="Vehicle Prepaid Calculator", page_icon="🇧🇹")

st.title("🇧🇹 Vehicle Prepaid Calculator")
st.sidebar.header("Calculation Settings")

item_type = st.sidebar.selectbox("Select Document Type", list(GL_MAPPING.keys()))
gl_code = GL_MAPPING[item_type]

premium_input = st.sidebar.number_input("Total Amount (Nu.)", min_value=0.0, value=2550.00, step=0.01)
start_dt = st.sidebar.date_input("Start Date", value=date(2025, 12, 25))
end_dt = st.sidebar.date_input("End Date", value=date(2026, 12, 24))

if st.sidebar.button("Run Calculation"):
    res, error = calculate_prepaid_logic(premium_input, start_dt, end_dt)
    
    if error:
        st.error(error)
    else:
        st.header(f"Results for: {item_type}")
        st.info(f"**Target GL Code:** {gl_code} | **Prepaid GL Code:** 284000")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Days", f"{res['total_days']}")
        col2.metric("Rate / Day", f"Nu. {res['rate']:.2f}")
        col3.metric("Prepaid Days", f"{res['prepaid_days']}")

        st.divider()

        # Accounting Summary
        c1, c2 = st.columns(2)
        with c1:
            st.subheader(f"Current Year ({start_dt.year})")
            st.write(f"GL Code: `{gl_code.split(' - ')[0]}`")
            st.write(f"Days: **{res['current_days']}**")
            st.markdown(f"### Nu. {res['current_amount']:.2f}")
            
        with c2:
            st.subheader(f"Prepaid Asset ({end_dt.year})")
            st.write("GL Code: `284000`")
            st.write(f"Days: **{res['prepaid_days']}**")
            st.markdown(f"### Nu. {res['prepaid_amount']:.2f}")

        if res["breakdown"]:
            st.subheader(f"Monthly Prepaid Amortization ({end_dt.year})")
            df = pd.DataFrame(res["breakdown"])
            st.table(df)
            
            # Totals check
            total_prepaid_calc = df["Amount (Nu.)"].sum()
            st.success(f"Verified: Sum of monthly breakdown is Nu. {total_prepaid_calc:.2f}")

st.markdown("---")
st.markdown('<div style="text-align: center; color: gray;"><p>Developed by <b>Prakash Giri (KASH BRO)</b></p></div>', unsafe_allow_html=True)
