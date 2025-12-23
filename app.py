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
    
    # Precise daily rate rounded to 2 decimals
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
            # Formatting month as "Jan 2026" for clarity
            month_label = curr.strftime("%b %Y")
            last_day_of_month = date(curr.year, curr.month, calendar.monthrange(curr.year, curr.month)[1])
            actual_end = min(last_day_of_month, end_date)
            days_in_month = (actual_end - curr).days + 1
            
            monthly_breakdown.append({
                "Month": month_label,
                "Days": days_in_month,
                "Amount (Nu.)": round(days_in_month * rate_per_day, 2)
            })
            curr = last_day_of_month + relativedelta(days=1)

    prepaid_amount = round(rate_per_day * prepaid_days, 2)
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
st.set_page_config(page_title="Vehicle Prepaid Calculator", page_icon="🇧🇹", layout="wide")

# Bold and Clear Credential Heading
st.markdown("""
    <div style="text-align: center; background-color: #f0f2f6; padding: 20px; border-radius: 10px; border: 2px solid #ff4b4b;">
        <h1 style="margin: 0; color: #1f1f1f;">🇧🇹 Vehicle Prepaid Calculator</h1>
        <h2 style="margin: 5px; color: #ff4b4b;">Developed by: PRAKASH GIRI (KASH BRO)</h2>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Sidebar
st.sidebar.header("Calculation Settings")
item_type = st.sidebar.selectbox("Select Document Type", list(GL_MAPPING.keys()))
gl_code = GL_MAPPING[item_type]

premium_input = st.sidebar.number_input("Total Amount (Nu.)", min_value=0.0, value=2550.00, step=0.01)

# Input dates - note: Streamlit date_input displays based on locale but we format results below
start_dt = st.sidebar.date_input("Start Date", value=date(2025, 12, 25))
end_dt = st.sidebar.date_input("End Date", value=date(2026, 12, 24))

if st.sidebar.button("Run Calculation"):
    res, error = calculate_prepaid_logic(premium_input, start_dt, end_dt)
    
    if error:
        st.error(error)
    else:
        st.subheader(f"Results for: {item_type}")
        st.info(f"**Period:** {start_dt.strftime('%d/%m/%Y')} to {end_dt.strftime('%d/%m/%Y')} | **GL:** {gl_code}")
        
        # Top level metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Days", f"{res['total_days']}")
        m2.metric("Rate / Day", f"Nu. {res['rate']:.2f}")
        m3.metric("Current Days", f"{res['current_days']}")
        m4.metric("Prepaid Days", f"{res['prepaid_days']}")

        st.divider()

        # Accounting Split
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"### Current Expense ({start_dt.year})")
            st.code(f"GL Code: {gl_code.split(' - ')[0]}", language="text")
            st.write(f"Duration: {start_dt.strftime('%d/%m/%Y')} - 31/12/{start_dt.year}")
            st.title(f"Nu. {res['current_amount']:.2f}")
            
        with c2:
            st.markdown(f"### Prepaid Asset (284000)")
            st.code(f"GL Code: 284000", language="text")
            st.write(f"Duration: 01/01/{end_dt.year} - {end_dt.strftime('%d/%m/%Y')}")
            st.title(f"Nu. {res['prepaid_amount']:.2f}")

        # Breakdown Table
        if res["breakdown"]:
            st.markdown("---")
            st.subheader(f"Monthly Amortization Schedule ({end_dt.year})")
            df = pd.DataFrame(res["breakdown"])
            
            # Displaying the table
            st.table(df)
            
            # Final Totals
            total_sum = round(df["Amount (Nu.)"].sum(), 2)
            st.success(f"**Verification:** Total Prepaid Nu. {total_sum:.2f} (Matched with GL 284000)")

st.markdown("---")
st.caption("Vehicle Prepaid Calculator | Financial Year Alignment | Bhutan")
