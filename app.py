import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO

# 1. PAGE CONFIG
st.set_page_config(page_title="Vehicle Prepaid Reporter", layout="wide")

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

# ---------------- SESSION STATE ----------------
if 'vehicles' not in st.session_state:
    st.session_state.vehicles = {} 
if 'entry_status' not in st.session_state:
    st.session_state.entry_status = "Ready"
if 'show_report' not in st.session_state:
    st.session_state.show_report = False

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("📋 Vehicle Entry")
    
    if "Success" in st.session_state.entry_status:
        st.success(st.session_state.entry_status)
    elif "Error" in st.session_state.entry_status:
        st.error(st.session_state.entry_status)

    with st.form("entry_form", clear_on_submit=True):
        v_no = st.text_input("Vehicle No", placeholder="BG-3-A0394").strip().upper()
        v_desc = st.text_input("Description", placeholder="(Bolero)")
        v_fuel = st.number_input("Fuel Prepaid (Nu.)", min_value=0.0)
        
        st.markdown("---")
        def doc_input_group(label):
            st.markdown(f"**{label}**")
            amt = st.number_input(f"{label} Amount", min_value=0.0, key=f"{label}_a")
            s_d = st.date_input(f"{label} Start", value=date(2025,1,1), format="DD/MM/YYYY", key=f"{label}_s")
            e_d = st.date_input(f"{label} End", value=date(2025,12,31), format="DD/MM/YYYY", key=f"{label}_e")
            return amt, s_d, e_d

        ins_a, ins_s, ins_e = doc_input_group("Insurance")
        bb_a, bb_s, bb_e = doc_input_group("Blue Book")
        fit_a, fit_s, fit_e = doc_input_group("Fitness")
        em_a, em_s, em_e = doc_input_group("Emission")

        submitted = st.form_submit_button("➕ Add / Update Vehicle", use_container_width=True)
        
        if submitted:
            if not v_no:
                st.session_state.entry_status = "Error: Vehicle No required!"
            else:
                i_c, i_p = get_split(ins_a, ins_s, ins_e)
                b_c, b_p = get_split(bb_a, bb_s, bb_e)
                f_c, f_p = get_split(fit_a, fit_s, fit_e)
                e_c, e_p = get_split(em_a, em_s, em_e)
                
                existing = st.session_state.vehicles.get(v_no, {})
                
                st.session_state.vehicles[v_no] = {
                    "Vehicle No.": v_no,
                    "Vehicle Description": v_desc if v_desc else existing.get("Vehicle Description", ""),
                    "Fuel Prepaid": v_fuel if v_fuel > 0 else existing.get("Fuel Prepaid", 0.0),
                    "Ins_C": i_c if ins_a > 0 else existing.get("Ins_C", 0.0),
                    "Ins_P": i_p if ins_a > 0 else existing.get("Ins_P", 0.0),
                    "BB_C": b_c if bb_a > 0 else existing.get("BB_C", 0.0),
                    "BB_P": b_p if bb_a > 0 else existing.get("BB_P", 0.0),
                    "Fit_C": f_c if fit_a > 0 else existing.get("Fit_C", 0.0),
                    "Fit_P": f_p if fit_a > 0 else existing.get("Fit_P", 0.0),
                    "Em_C": e_c if em_a > 0 else existing.get("Em_C", 0.0),
                    "Em_P": e_p if em_a > 0 else existing.get("Em_P", 0.0)
                }
                st.session_state.entry_status = f"Success: {v_no} added to draft."
                st.session_state.show_report = False 
                st.rerun()

    if st.button("🚀 Calculate & Show Report", type="primary", use_container_width=True):
        if not st.session_state.vehicles:
            st.session_state.entry_status = "Error: No data to calculate!"
        else:
            st.session_state.show_report = True
            st.rerun()

    if st.button("🗑️ Reset Everything", use_container_width=True):
        st.session_state.vehicles = {}
        st.session_state.show_report = False
        st.session_state.entry_status = "Ready"
        st.rerun()

# ---------------- MAIN CONTENT ----------------
st.markdown("""
<div style="text-align:center; padding:10px; border-radius:10px; background: linear-gradient(90deg, #1f77b4, #2ca02c); color:white;">
    <h1 style="margin:0;">Vehicle Prepaid Statement Generator</h1>
    <p style="margin:0;">Developed by: PRAKASH GIRI (KASH BRO)</p>
</div>
""", unsafe_allow_html=True)

if st.session_state.show_report and st.session_state.vehicles:
    st.button("⬅️ Back to Entry Form", on_click=lambda: setattr(st.session_state, 'show_report', False))

    df_raw = pd.DataFrame(list(st.session_state.vehicles.values()))
    
    numeric_cols = ["Fuel Prepaid", "Ins_C", "Ins_P", "BB_C", "BB_P", "Fit_C", "Fit_P", "Em_C", "Em_P"]
    for col in numeric_cols:
        if col not in df_raw.columns:
            df_raw[col] = 0.0

    # Display Renaming
    cols_map = {
        "Vehicle No.": "Vehicle No.", "Vehicle Description": "Description",
        "Fuel Prepaid": "Fuel Prepaid", "Ins_C": "Ins Current", "Ins_P": "Ins Prepaid",
        "BB_C": "BB Current", "BB_P": "BB Prepaid", "Fit_C": "Fit Current",
        "Fit_P": "Fit Prepaid", "Em_C": "Em Current", "Em_P": "Em Prepaid"
    }
    df_display = df_raw.rename(columns=cols_map)
    disp_numeric = [cols_map[c] for c in numeric_cols]

    sums = df_display[disp_numeric].sum()
    total_row = pd.DataFrame([["TOTAL", ""] + sums.tolist()], columns=df_display.columns)
    final_table = pd.concat([df_display, total_row], ignore_index=True)

    st.write("### 1. Consolidated Statement")
    st.dataframe(final_table, use_container_width=True)

    # Journal Entry
    total_f = sums["Fuel Prepaid"]
    total_i_p = sums["Ins Prepaid"]
    total_rm_p = sums["BB Prepaid"] + sums["Fit Prepaid"] + sums["Em Prepaid"]
    total_dr = total_f + total_i_p + total_rm_p
    
    je_data = [
        ["Dr.", f"{GL_CODES['Prepaid']} Prepaid Expenses", f"{total_dr:,.2f}", ""],
        ["Cr.", f"{GL_CODES['Fuel']} vehicle fuel", "", f"{total_f:,.2f}"],
        ["Cr.", f"{GL_CODES['Insurance']} insurance of Vehicle", "", f"{total_i_p:,.2f}"],
        ["Cr.", f"{GL_CODES['Blue Book']} R & M of Vehicle", "", f"{total_rm_p:,.2f}"]
    ]
    st.write("### 2. Accounting Journal Entries")
    st.table(pd.DataFrame(je_data, columns=["Type", "Particulars", "Debit", "Credit"]))

else:
    # --- PENDING LIST & REMOVE BUTTONS ---
    st.subheader("📝 Draft Entries (Manage before calculating)")
    if st.session_state.vehicles:
        for v_id in list(st.session_state.vehicles.keys()):
            col1, col2, col3 = st.columns([3, 5, 2])
            with col1:
                st.write(f"**{v_id}**")
            with col2:
                st.write(f"({st.session_state.vehicles[v_id]['Vehicle Description']})")
            with col3:
                if st.button(f"❌ Remove {v_id}", key=f"del_{v_id}"):
                    del st.session_state.vehicles[v_id]
                    st.rerun()
        
        st.info("💡 You can add more vehicles or update existing ones in the sidebar. When ready, click 'Calculate & Show Report'.")
    else:
        st.info("👈 Your list is empty. Add a vehicle using the sidebar to begin.")
