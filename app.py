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
def calculate_row(row):
    premium = row["Total Amount (Nu.)"]
    start_date = row["Start Date"]
    end_date = row["End Date"]
    
    total_days = (end_date - start_date).days + 1
    if total_days <= 0:
        return None

    rate_per_day = round(premium / total_days, 4)
    first_prepaid_day = date(start_date.year + 1, 1, 1)

    if end_date < first_prepaid_day:
        current_days = total_days
        prepaid_days = 0
    else:
        last_day_year = date(start_date.year, 12, 31)
        current_days = (last_day_year - start_date).days + 1
        prepaid_days = (end_date - first_prepaid_day).days + 1

    prepaid_amount = round(rate_per_day * prepaid_days, 2)
    current_amount = round(premium - prepaid_amount, 2)
    
    gl_code, gl_desc = GL_MAPPING.get(row["Document Type"], ("N/A", "N/A"))

    return pd.Series({
        "GL Code": gl_code,
        "GL Description": gl_desc,
        "Total Days": total_days,
        "Rate/Day": rate_per_day,
        "Curr. Days": current_days,
        "Prepaid Days": prepaid_days,
        "Current Exp": current_amount,
        "Prepaid Exp": prepaid_amount
    })

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Multi-Vehicle Prepaid Calculator", layout="wide")

st.markdown("""
<div style="text-align:center; padding:10px; border-radius:12px; background: linear-gradient(90deg, #1f77b4, #2ca02c);">
    <h1 style="margin:0; color:white;">Vehicle Prepaid Calculator</h1>
    <h3 style="margin-top:5px; color:#e8f4ff;">Developed by: PRAKASH GIRI (KASH BRO)</h3>
</div>
""", unsafe_allow_html=True)

st.write("### Enter Vehicle Details Below")
st.info("Add rows by clicking the '+' at the bottom of the table. Ensure dates are in YYYY-MM-DD format.")

# ---------------- DATA INPUT TABLE ----------------
# Default empty dataframe for the editor
if 'df_input' not in st.session_state:
    st.session_state.df_input = pd.DataFrame([{
        "Vehicle No": "BP-1-A1234",
        "Document Type": "Insurance",
        "Total Amount (Nu.)": 5000.00,
        "Start Date": date(2025, 1, 1),
        "End Date": date(2025, 12, 31)
    }])

edited_df = st.data_editor(
    st.session_state.df_input,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Document Type": st.column_config.SelectboxColumn(options=list(GL_MAPPING.keys())),
        "Start Date": st.column_config.DateColumn(),
        "End Date": st.column_config.DateColumn(),
        "Total Amount (Nu.)": st.column_config.NumberColumn(format="Nu. %.2f")
    }
)

# ---------------- EXECUTION ----------------
if st.button("Generate Consolidated Report"):
    try:
        # Apply calculation logic to every row
        results_df = edited_df.apply(calculate_row, axis=1)
        
        # Combine input data with calculated results
        final_report = pd.concat([edited_df, results_df], axis=1)
        
        st.divider()
        st.subheader("Final Prepaid Report")
        st.dataframe(final_report, use_container_width=True)

        # Totals Summary
        t1, t2, t3 = st.columns(3)
        t1.metric("Total Premium", f"Nu. {final_report['Total Amount (Nu.)'].sum():,.2f}")
        t2.metric("Total Current Expense", f"Nu. {final_report['Current Exp'].sum():,.2f}")
        t3.metric("Total Prepaid (GL 284000)", f"Nu. {final_report['Prepaid Exp'].sum():,.2f}")

        # ---------------- EXCEL EXPORT ----------------
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            final_report.to_excel(writer, sheet_name="Prepaid_Summary", index=False)
        processed_data = output.getvalue()

        st.download_button(
            label="📤 Download Excel Report",
            data=processed_data,
            file_name=f"Vehicle_Prepaid_Report_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        st.error(f"Error in calculation. Please check your date entries. Details: {e}")

st.markdown("---")
st.caption("Vehicle Prepaid Calculator | Financial Year Alignment | Bhutan")
