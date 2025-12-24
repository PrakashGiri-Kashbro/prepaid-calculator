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

if 'vehicles' not in st.session_state:
    st.session_state.vehicles = []
if 'entry_status' not in st.session_state:
    st.session_state.entry_status = "Waiting for input..."

# ---------------- SIDEBAR (Indicator & Stats) ----------------
with st.sidebar:
    st.header("Activity Monitor")
    if "Waiting" in st.session_state.entry_status:
        st.info(st.session_state.entry_status)
    elif "Success" in st.session_state.entry_status:
        st.success(st.session_state.entry_status)
    else:
        st.error(st.session_state.entry_status)
    
    st.divider()
    st.metric("Total Records", len(st.session_state.vehicles))

# ---------------- HEADER ----------------
st.markdown("""
<div style="text-align:center; padding:10px; border-radius:10px; background: linear-gradient(90deg, #1f77b4, #2ca02c); color:white;">
    <h1 style="margin:0;">Vehicle Prepaid Statement Generator</h1>
    <p style="margin:0;">Standardized Reporting | Developed by: PRAKASH GIRI (KASH BRO)</p>
</div>
""", unsafe_allow_html=True)

# ---------------- INPUT FORM ----------------
st.write("### 1. New Vehicle Entry Form")
with st.container(border=True):
    c1, c2, c3 = st.columns([2, 2, 1])
    v_no = c1.text_input("Vehicle No", placeholder="BG-3-A0394").strip().upper()
    v_desc = c2.text_input("Description", placeholder="(Bolero)")
    v_fuel = c3.number_input("Fuel Prepaid", min_value=0.0)

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
    em_a, em_s, em_e = doc_row("Emission")

    st.write("")
    col_btn1, col_btn2 = st.columns(2)
    
    # ADD VEHICLE BUTTON
    if col_btn1.button("➕ Add New Vehicle", use_container_width=True):
        if not v_no:
            st.session_state.entry_status = "Error: Vehicle Number is missing!"
        elif any(v['Vehicle No.'] == v_no for v in st.session_state.vehicles):
            st.session_state.entry_status = f"Duplicate Error: {v_no} already exists!"
        else:
            i_c, i_p = get_split(ins_a, ins_s, ins_e)
            b_c, b_p = get_split(bb_a, bb_s, bb_e)
            f_c, f_p = get_split(fit_a, fit_s, fit_e)
            e_c, e_p = get_split(em_a, em_s, em_e)
            
            st.session_state.vehicles.append({
                "Vehicle No.": v_no, "Vehicle Discription": v_desc, "Fuel Prepaid": v_fuel,
                "Ins_C": i_c, "Ins_P": i_p, "BB_C": b_c, "BB_P": b_p,
                "Fit_C": f_c, "Fit_P": f_p, "Em_C": e_c, "Em_P": e_p
            })
            st.session_state.entry_status = f"Success: {v_no} added."
            st.rerun()

    # CALCULATE BUTTON
    if col_btn2.button("🚀 Calculate & Generate Report", type="primary", use_container_width=True):
        if not st.session_state.vehicles:
            st.session_state.entry_status = "Error: No data to calculate!"
        else:
            st.session_state.show_report = True

# ---------------- OUTPUT REPORT ----------------
if st.session_state.get('show_report') and st.session_state.vehicles:
    st.divider()
    data = []
    for i, v in enumerate(st.session_state.vehicles):
        data.append([
            i+1, v["Vehicle No."], v["Vehicle Discription"], v["Fuel Prepaid"],
            v["Ins_C"], v["Ins_P"], v["BB_C"], v["BB_P"],
            v["Fit_C"], v["Fit_P"], v["Em_C"], v["Em_P"]
        ])
    
    cols = ["Si. No.", "Vehicle No.", "Vehicle Discription", "Fuel Prepaid", 
            "Insurance Current", "Insurance Prepaid", "Blue Book Current", "Blue Book Prepaid",
            "Fitness Current", "Fitness Prepaid", "Emission Current", "Emission Prepaid"]
    
    df_main = pd.DataFrame(data, columns=cols)
    sums = df_main.sum(numeric_only=True)
    
    # Add Total Row
    total_row = pd.DataFrame([["", "TOTAL", "", sums["Fuel Prepaid"], 
                               sums.get("Insurance Current",0), sums.get("Insurance Prepaid",0),
                               sums.get("Blue Book Current",0), sums.get("Blue Book Prepaid",0),
                               sums.get("Fitness Current",0), sums.get("Fitness Prepaid",0),
                               sums.get("Emission Current",0), sums.get("Emission Prepaid",0)]], columns=cols)
    
    st.write("### Consolidated Table")
    st.dataframe(pd.concat([df_main, total_row], ignore_index=True), use_container_width=True)

    # ---------------- ACCOUNTING ENTRIES ----------------
    st.write("### Journal Entries")
    total_f = sums["Fuel Prepaid"]
    total_i_p = sums["Insurance Prepaid"]
    total_rm_p = sums["Blue Book Prepaid"] + sums["Fitness Prepaid"] + sums["Emission Prepaid"]
    
    je = [
        ["Dr.", f"{GL_CODES['Prepaid']} Prepaid Expenses", f"{(total_f+total_i_p+total_rm_p):,.2f}", ""],
        ["Cr.", f"{GL_CODES['Fuel']} vehicle fuel", "", f"{total_f:,.2f}"],
        ["Cr.", f"{GL_CODES['Insurance']} insurance of Vehicle", "", f"{total_i_p:,.2f}"],
        ["Cr.", f"{GL_CODES['Blue Book']} R & M of Vehicle", "", f"{total_rm_p:,.2f}"]
    ]
    st.table(pd.DataFrame(je, columns=["Type", "Particulars", "Debit (Nu.)", "Credit (Nu.)"]))

    # Download
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_main.to_excel(writer, sheet_name='Prepaid_Report', index=False)
    st.download_button("📤 Download Excel", output.getvalue(), "Vehicle_Prepaid.xlsx")

    if st.button("🗑️ Reset All Records"):
        st.session_state.vehicles = []
        st.session_state.entry_status = "Waiting for input..."
        st.session_state.show_report = False
        st.rerun()
