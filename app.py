import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO

# ---------------- GL MAPPING ----------------
# As per your sample file
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
    if premium == 0:
        return 0.0, 0.0
    total_days = (end_dt - start_dt).days + 1
    if total_days <= 0:
        return 0.0, 0.0
    
    # Financial Year ends on Dec 31
    year_end = date(start_dt.year, 12, 31)
    
    if end_dt <= year_end:
        curr_days = total_days
        pre_days = 0
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

# ---------------- HEADER ----------------
st.markdown("""
<div style="text-align:center; padding:10px; border-radius:10px; background: linear-gradient(90deg, #1f77b4, #2ca02c); color:white;">
    <h1 style="margin:0;">Vehicle Prepaid Statement Generator</h1>
    <p style="margin:0;">Standardized Reporting Format | Developed by: PRAKASH GIRI (KASH BRO)</p>
</div>
""", unsafe_allow_html=True)

# ---------------- INPUT SECTION ----------------
st.write("### 1. Enter Vehicle Information")
with st.expander("Click to enter details for a new vehicle", expanded=True):
    row1_col1, row1_col2, row1_col3 = st.columns([2, 2, 1])
    v_no = row1_col1.text_input("Vehicle No", placeholder="e.g. BG-3-A0394")
    v_desc = row1_col2.text_input("Description", placeholder="e.g. (Bolero)")
    v_fuel = row1_col3.number_input("Fuel Prepaid (Nu.)", min_value=0.0, value=15000.0)

    st.divider()
    # Using 4 columns for each document type: Amount, Start Date, End Date
    def doc_inputs(label):
        st.write(f"**{label} Details**")
        c1, c2, c3 = st.columns(3)
        amt = c1.number_input(f"{label} Amount", min_value=0.0, key=f"{label}_amt")
        start = c2.date_input(f"{label} Start", value=date(2025, 1, 1), key=f"{label}_s")
        end = c3.date_input(f"{label} End", value=date(2025, 12, 31), key=f"{label}_e")
        return amt, start, end

    ins_amt, ins_s, ins_e = doc_inputs("Insurance")
    bb_amt, bb_s, bb_e = doc_inputs("Blue Book")
    fit_amt, fit_s, fit_e = doc_inputs("Fitness")
    em_amt, em_s, em_e = doc_inputs("Emission")

    # Action Buttons
    btn_col1, btn_col2 = st.columns(2)
    if btn_col1.button("➕ Add Vehicle to List", use_container_width=True):
        if v_no:
            # Calculate splits immediately
            i_c, i_p = get_split(ins_amt, ins_s, ins_e)
            b_c, b_p = get_split(bb_amt, bb_s, bb_e)
            f_c, f_p = get_split(fit_amt, fit_s, fit_e)
            e_c, e_p = get_split(em_amt, em_s, em_e)
            
            st.session_state.vehicles.append({
                "Vehicle No.": v_no,
                "Vehicle Discription": v_desc,
                "Fuel Prepaid": v_fuel,
                "Ins_C": i_c, "Ins_P": i_p,
                "BB_C": b_c, "BB_P": b_p,
                "Fit_C": f_c, "Fit_P": f_p,
                "Em_C": e_c, "Em_P": e_p
            })
            st.success(f"Added {v_no}")
        else:
            st.error("Please enter a Vehicle Number.")
            
    if btn_col2.button("🚀 Calculate & Generate Report", type="primary", use_container_width=True):
        st.session_state.show_report = True

# ---------------- REPORT SECTION ----------------
if st.session_state.get('show_report') and st.session_state.vehicles:
    st.divider()
    st.subheader("Final Prepaid Report")

    # Prepare Dataframe for table display
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
    
    df_report = pd.DataFrame(data, columns=cols)
    
    # Calculate Totals
    totals = df_report.sum(numeric_only=True)
    total_row = pd.DataFrame([["", "", "TOTAL", totals["Fuel Prepaid"], 
                               totals["Insurance Current"], totals["Insurance Prepaid"],
                               totals["Blue Book Current"], totals["Blue Book Prepaid"],
                               totals["Fitness Current"], totals["Fitness Prepaid"],
                               totals["Emission Current"], totals["Emission Prepaid"]]], columns=cols)
    
    final_display_df = pd.concat([df_report, total_row], ignore_index=True)
    st.dataframe(final_display_df, use_container_width=True)

    # ---------------- JOURNAL ENTRIES ----------------
    st.write("### Accounting Journal Entries")
    total_fuel = totals["Fuel Prepaid"]
    total_ins_pre = totals["Insurance Prepaid"]
    total_rm_pre = totals["Blue Book Prepaid"] + totals["Fitness Prepaid"] + totals["Emission Prepaid"]
    grand_prepaid = total_fuel + total_ins_pre + total_rm_pre

    je_data = [
        ["Dr.", f"{GL_CODES['Prepaid']} Prepaid Expenses", f"{grand_prepaid:,.2f}", ""],
        ["Cr.", f"{GL_CODES['Fuel']} vehicle fuel", "", f"{total_fuel:,.2f}"],
        ["Cr.", f"{GL_CODES['Insurance']} insurance of Vehicle", "", f"{total_ins_pre:,.2f}"],
        ["Cr.", f"{GL_CODES['Blue Book']} R & M of Vehicle", "", f"{total_rm_pre:,.2f}"],
    ]
    je_df = pd.DataFrame(je_data, columns=["Type", "Particulars", "Debit", "Credit"])
    st.table(je_df)

    # ---------------- DOWNLOAD ----------------
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        final_display_df.to_excel(writer, sheet_name='Report', index=False)
    
    st.download_button(
        label="📥 Download Excel Report",
        data=output.getvalue(),
        file_name=f"Vehicle_Prepaid_Report_{date.today()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    if st.button("Clear All Data"):
        st.session_state.vehicles = []
        st.session_state.show_report = False
        st.rerun()
