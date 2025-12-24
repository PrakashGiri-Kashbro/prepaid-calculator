import streamlit as st
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
import calendar
from io import BytesIO

# ---------------- GL MAPPING ----------------
GL_MAPPING = {
    "Vehicle Register (Blue Book)": ("450110", "R&M of Vehicle (Ser)"),
    "Emission": ("450110", "R&M of Vehicle (Ser)"),
    "Road Worthiness (Fitness)": ("450110", "R&M of Vehicle (Ser)"),
    "Route Permit": ("450110", "R&M of Vehicle (Ser)"),
    "Insurance": ("432200", "Insurance on Vehicle")
}

# ---------------- CALCULATION LOGIC ----------------
def calculate_prepaid_details(vehicle_no, item_type, premium, start_dt, end_dt):
    gl_code, gl_desc = GL_MAPPING[item_type]
    total_days = (end_dt - start_dt).days + 1
    
    if total_days <= 0:
        return None

    rate_per_day = premium / total_days
    year_end = date(start_dt.year, 12, 31)
    
    if end_dt <= year_end:
        curr_days = total_days
        pre_days = 0
    else:
        curr_days = (year_end - start_dt).days + 1
        pre_days = total_days - curr_days
            
    prepaid_amt = round(rate_per_day * pre_days, 2)
    current_amt = round(premium - prepaid_amt, 2)
    
    return {
        "Vehicle No": vehicle_no,
        "Document": item_type,
        "GL Code": gl_code,
        "GL Desc": gl_desc,
        "Premium": premium,
        "Start": start_dt,
        "End": end_dt,
        "Total Days": total_days,
        "Rate/Day": round(rate_per_day, 2),
        "Curr Days": curr_days,
        "Prepaid Days": pre_days,
        "Current Amt": current_amt,
        "Prepaid Amt": prepaid_amt
    }

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Vehicle Prepaid Accumulator", layout="wide")

# Initialize Session State to store the list of vehicles
if 'master_list' not in st.session_state:
    st.session_state.master_list = []

# ---------------- HEADER ----------------
st.markdown("""
<div style="text-align:center; padding:15px; border-radius:12px; background: linear-gradient(90deg, #1f77b4, #2ca02c);">
    <h1 style="margin:0; color:white;">Vehicle Prepaid Accumulator</h1>
    <h4 style="margin-top:5px; color:#e8f4ff;">Enter vehicles one by one to build your report</h4>
</div>
""", unsafe_allow_html=True)

# ---------------- ENTRY FORM ----------------
with st.container():
    st.write("### 1. New Vehicle Entry")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        v_no = st.text_input("Vehicle No", placeholder="BP-1-A1234")
    with col2:
        v_type = st.selectbox("Document Type", list(GL_MAPPING.keys()))
    with col3:
        v_amt = st.number_input("Total Amount", min_value=0.0, value=2500.0, step=0.01)
    with col4:
        v_start = st.date_input("Start Date", value=date.today())
    with col5:
        v_end = st.date_input("End Date", value=date.today() + relativedelta(years=1, days=-1))

    if st.button("➕ Add Vehicle to Table", use_container_width=True):
        if v_no:
            new_record = calculate_prepaid_details(v_no, v_type, v_amt, v_start, v_end)
            if new_record:
                st.session_state.master_list.append(new_record)
                st.toast(f"Added {v_no} successfully!")
            else:
                st.error("End Date must be after Start Date.")
        else:
            st.warning("Please enter a Vehicle Number.")

# ---------------- MASTER TABLE ----------------
if st.session_state.master_list:
    st.write("---")
    st.subheader("2. Consolidated Vehicle Records")
    
    df = pd.DataFrame(st.session_state.master_list)
    
    # Display the table
    st.table(df)

    # Summary Calculations
    total_prepaid = df["Prepaid Amt"].sum()
    total_current = df["Current Amt"].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Vehicles Added", len(df))
    c2.metric("Total Current Expense", f"Nu. {total_current:,.2f}")
    c3.metric("Total Prepaid (GL 284000)", f"Nu. {total_prepaid:,.2f}")

    # ---------------- EXPORT & CLEAR ----------------
    st.write("---")
    col_ex, col_cl = st.columns([1, 1])
    
    with col_ex:
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Prepaid_Report", index=False)
        st.download_button(
            label="📥 Download Consolidated Excel",
            data=output.getvalue(),
            file_name="Vehicle_Prepaid_Summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col_cl:
        if st.button("🗑️ Clear All Records"):
            st.session_state.master_list = []
            st.rerun()

else:
    st.info("No records added yet. Use the form above to start.")

st.markdown("---")
st.caption("Developed by: PRAKASH GIRI (KASH BRO) | Bhutan")
