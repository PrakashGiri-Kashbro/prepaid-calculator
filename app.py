import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO

# ---------------- GL MAPPING (From your CSV structure) ----------------
GL_CODES = {
    "Insurance": "432200",
    "Blue Book": "450110",
    "Fitness": "450110",
    "Emission": "450110",
    "Fuel": "450600",
    "Prepaid": "284000"
}

# ---------------- CALCULATION LOGIC ----------------
def get_split(premium, start_dt, end_dt):
    if premium == 0: return 0.0, 0.0
    total_days = (end_dt - start_dt).days + 1
    if total_days <= 0: return 0.0, 0.0
    
    # Financial Year Alignment (Dec 31)
    year_end = date(start_dt.year, 12, 31)
    if end_dt <= year_end:
        curr_days, pre_days = total_days, 0
    else:
        curr_days = (year_end - start_dt).days + 1
        pre_days = total_days - curr_days
        
    rate = premium / total_days
    prepaid_amt = round(rate * pre_days, 2)
    current_amt = round(premium - prepaid_amt, 2)
    return current_amt, prepaid_amt

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Vehicle Prepaid Reporter", layout="wide")

# Initialize Session States
if 'vehicles' not in st.session_state:
    st.session_state.vehicles = []
if 'entry_status' not in st.session_state:
    st.session_state.entry_status = "Waiting for input..."

# ---------------- SIDEBAR (ENTRY INDICATOR) ----------------
with st.sidebar:
    st.header("Activity Monitor")
    if "Waiting" in st.session_state.entry_status:
        st.info(st.session_state.entry_status)
    elif "Success" in st.session_state.entry_status:
        st.success(st.session_state.entry_status)
    else:
        st.error(st.session_state.entry_status)
    
    st.divider()
    st.write(f"**Total Records:** {len(st.session_state.vehicles)}")

# ---------------- HEADER ----------------
st.markdown("""
<div style="text-align:center; padding:10px; border-radius:10px; background: linear-gradient(90deg, #1f77b4, #2ca02c); color:white;">
    <h1 style="margin:0;">Vehicle Prepaid Statement Generator</h1>
    <p style="margin:0;">Developed by: PRAKASH GIRI (KASH BRO)</p>
</div>
""", unsafe_allow_html=True)

# ---------------- INPUT FORM ----------------
st.write("### 1. New Vehicle Entry Form")
with st.container(border=True):
    c1, c2, c3 = st.columns([2, 2, 1])
    v_no = c1.text_input("Vehicle No", placeholder="BG-3-A0394").strip().upper()
    v_desc = c2.text_input("Description", placeholder="(Bolero)")
    v_fuel = c3.number_input("Fuel Prepaid", min_value=0.0)

    # Helper function for document rows
    def doc_row(label):
        st.markdown(f"**{label}**")
        r1, r2, r3 = st.columns(3)
        amt = r1.number_input("Amount", min_value=0.0, key=f"{label}_a")
        start = r2.date_input("Start Date", value=date(2025,1,1), key=f"{label}_s")
        end = r3.date_input("End Date", value=date(2025,12,31), key=f"{label}_e")
        return amt, start, end

    ins_a, ins_s, ins_e = doc_row("Insurance")
    bb_a, bb_s, bb_e = doc_row("Blue Book")
    fit_a, fit_s, fit_e = doc_row("Fitness")
    em_a, em_s, em_e = doc_row("Emission
