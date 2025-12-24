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

# ---------------- SIDEBAR: ENTRY INDICATOR & FORM ----------------
with st.sidebar:
    st.header("📋 New Vehicle Entry")
    
    # Status Message
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
            # Forced DD/MM/YYYY
            s_d = st.date_input(f"{label} Start", value=date(2025,1,1), format="DD/MM/YYYY", key=f"{label}_s")
            e_d = st.date_input(f"{label} End", value=date(2025,12,31), format="DD/MM/YYYY", key=f"{label}_e")
            return amt, s_d, e_d

        ins_a, ins_s, ins_e = doc_input_group("Insurance")
        bb_a, bb_s, bb_e = doc_input_group("Blue Book")
        fit_a, fit_s, fit_e = doc_input_group("Fitness")
        em_a, em_s, em_e = doc_input_group("Emission")

        submitted = st.form_submit_button("➕ Add to List", use_container_width=True)
        
        if submitted:
            if not v_no:
                st.session_state.entry_status = "Error: Vehicle No is required!"
            elif any(v['Vehicle No.'] == v_no for v in st.session_state.vehicles):
                st.session_state.entry_status = f"Duplicate Error: {v_no} exists!"
            else:
                # Calculations
                i_c, i_p = get_split(ins_a, ins_s, ins_e)
                b_c, b_p = get_split(bb_a, bb_s, bb_e)
                f_c, f_p = get_split(fit_a, fit_s, fit_e)
                e_c, e_p = get_split(em_a, em_s, em_e)
                
                st.session_state.vehicles.append({
                    "Vehicle No.": v_no, "Vehicle Description": v_desc, "Fuel Prepaid": v_fuel,
                    "Ins_C": i_c, "Ins_P": i_p, "BB_C": b_c, "BB_P": b_p,
                    "Fit_C": f_c, "Fit_P": f_p, "Em_C": e_c, "Em_P": e_p
                })
                st.session_state.entry_status = f"Success: {v_no} added."
                st.rerun()

    if st.button("🚀 Calculate & Show Report", type="primary", use_container_width=True):
        if not st.session_state.vehicles:
            st.session_state.entry_status = "Error: No data added!"
        else:
            st.session_state.show_report = True

    if st.button("🗑️ Reset All", use_container_width=True):
        st.session_state.vehicles = []
        st.session_state.show_report = False
        st.session_state.entry_status = "Ready for new entry"
        st.rerun()

# ---------------- MAIN CONTENT ----------------
st.markdown("""
<div style="text-align:center; padding:10px; border-radius:10px; background: linear-gradient(90deg, #1f77b4, #2ca02c); color:white;">
    <h1 style="margin:0;">Vehicle Prepaid Statement Generator</h1>
    <p style="margin:0;">Developed by: PRAKASH GIRI (KASH BRO)</p>
</div>
""", unsafe_allow_html=True)

if st.session_state.show_report and st.session_state.vehicles:
    # 1. Main Data Table
    data = []
    for i, v in enumerate(st.session_state.vehicles):
        data.append([
            i+1, v["Vehicle No."], v["Vehicle Description"], v["Fuel Prepaid"],
            v["Ins_C"], v["Ins_P"], v["BB_C"], v["BB_P"],
            v["Fit_C"], v["Fit_P"], v["Em_C"], v["Em_P"]
        ])
    
    cols = ["Si. No.", "Vehicle No.", "Vehicle Description", "Fuel Prepaid", 
            "Ins Current", "Ins Prepaid", "BB Current", "BB Prepaid",
            "Fit Current", "Fit Prepaid", "Em Current", "Em Prepaid"]
    
    df_main = pd.DataFrame(data, columns=cols)
    sums = df_main.sum(numeric_only=True)
    
    total_row = pd.DataFrame([["", "TOTAL", "", sums["Fuel Prepaid"], 
                               sums.get("Ins Current",0), sums.get("Ins Prepaid",0),
                               sums.get("BB Current",0), sums.get("BB Prepaid",0),
                               sums.get("Fit Current",0), sums.get("Fit Prepaid",0),
                               sums.get("Em Current",0), sums.get("Em Prepaid",0)]], columns=cols)
    
    final_table = pd.concat([df_main, total_row], ignore_index=True)

    # 2. Journal Entry Data
    total_f = sums["Fuel Prepaid"]
    total_i_p = sums["Ins Prepaid"]
    total_rm_p = sums["BB Prepaid"] + sums["Fit Prepaid"] + sums["Em Prepaid"]
    
    je_data = [
        ["Dr.", f"{GL_CODES['Prepaid']} Prepaid Expenses", f"{(total_f+total_i_p+total_rm_p):,.2f}", ""],
        ["Cr.", f"{GL_CODES['Fuel']} vehicle fuel", "", f"{total_f:,.2f}"],
        ["Cr.", f"{GL_CODES['Insurance']} insurance of Vehicle", "", f"{total_i_p:,.2f}"],
        ["Cr.", f"{GL_CODES['Blue Book']} R & M of Vehicle", "", f"{total_rm_p:,.2f}"]
    ]
    df_je = pd.DataFrame(je_data, columns=["Type", "Particulars", "Debit", "Credit"])

    st.write("### 1. Consolidated Statement")
    st.dataframe(final_table, use_container_width=True)
    
    st.write("### 2. Accounting Journal Entries")
    st.table(df_je)

    # 3. EXCEL EXPORT (Combined)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        final_table.to_excel(writer, sheet_name='Report', index=False)
        
        # Insert Journal Entry at bottom of Excel
        start_row_je = len(final_table) + 4
        worksheet = writer.sheets['Report']
        worksheet.write(start_row_je - 1, 0, "ACCOUNTING JOURNAL ENTRIES")
        df_je.to_excel(writer, sheet_name='Report', index=False, startrow=start_row_je)

    st.download_button(
        label="📥 Download Excel Report with JE",
        data=output.getvalue(),
        file_name=f"Vehicle_Report_{date.today().strftime('%d_%m_%Y')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("👈 Use the Sidebar to add vehicles, then click 'Calculate & Show Report'.")
