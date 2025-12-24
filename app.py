import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO

# ---------------- GL MAPPING ----------------
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
    
    # Financial Year ends Dec 31
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

if 'vehicles' not in st.session_state:
    st.session_state.vehicles = []
if 'entry_status' not in st.session_state:
    st.session_state.entry_status = "Ready for new entry"
if 'show_report' not in st.session_state:
    st.session_state.show_report = False

# ---------------- SIDEBAR: NEW VEHICLE ENTRY (INDICATOR) ----------------
with st.sidebar:
    st.header("📋 New Vehicle Entry")
    
    if "Success" in st.session_state.entry_status:
        st.success(st.session_state.entry_status)
    elif "Error" in st.session_state.entry_status or "Duplicate" in st.session_state.entry_status:
        st.error(st.session_state.entry_status)
    else:
        st.info(st.session_state.entry_status)

    with st.form("entry_form", clear_on_submit=True):
        v_no = st.text_input("Vehicle No", placeholder="BG-3-A0394").strip().upper()
        v_desc = st.text_input("Description", placeholder="(Bolero)")
        v_fuel = st.number_input("Fuel Prepaid (Nu.)", min_value=0.0)
        
        st.markdown("---")
        def doc_input_group(label):
            st.markdown(f"**{label}**")
            amt = st.number_input(f"{label} Amount", min_value=0.0, key=f"{label}_a")
            s_date = st.date_input(f"{label} Start", value=date(2025,1,1), format="DD/MM/YYYY", key=f"{label}_s")
            e_date = st.date_input(f"{label} End", value=date(2025,12,31), format="DD/MM/YYYY", key=f"{label}_e")
            return amt, s_date, e_date

        ins_a, ins_s, ins_e = doc_input_group("Insurance")
        bb_a, bb_s, bb_e = doc_input_group("Blue Book")
        fit_a, fit_s, fit_e = doc_input_group("Fitness")
        em_a, em_s, em_e = doc_input_group("Emission")

        submitted = st.form_submit_button("➕ Add to List", use_container_width=True)
        
        if submitted:
            if not v_no:
                st.session_state.entry_status = "Error: Vehicle No is required!"
            elif any(v['Vehicle No.'] == v_no for v in st.session_state.vehicles):
                st.session_state.entry_status = f"Duplicate Error: {v_no} already exists!"
            else:
                i_c, i_p = get_split(ins_a, ins_s, ins_e)
                b_c, b_p = get_split(bb_a, bb_s, bb_e)
                f_c, f_p = get_split(fit_a, fit_s, fit_e)
                e_c, e_p = get_split(
