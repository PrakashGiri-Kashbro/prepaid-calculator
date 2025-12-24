import streamlit as st
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
import calendar
from io import BytesIO

# ---------------- GL MAPPING ----------------
GL_MAPPING = {
    "Insurance": ("432200", "Insurance on Vehicle"),
    "Blue Book": ("450110", "R&M of Vehicle (Ser)"),
    "Fitness": ("450110", "R&M of Vehicle (Ser)"),
    "Emission": ("450110", "R&M of Vehicle (Ser)")
}

DOC_TYPES = list(GL_MAPPING.keys())

# ---------------- PREPAID LOGIC ----------------
def calculate_prepaid(premium, start_date, end_date):
    total_days = (end_date - start_date).days + 1
    rate = premium / total_days

    first_prepaid_day = date(start_date.year + 1, 1, 1)

    if end_date < first_prepaid_day:
        prepaid_days = 0
    else:
        prepaid_days = (end_date - first_prepaid_day).days + 1

    prepaid_amt = round(prepaid_days * rate, 2)
    current_amt = round(premium - prepaid_amt, 2)

    return current_amt, prepaid_amt

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Vehicle Prepaid Calculator", layout="wide")

st.title("🚗 Vehicle Prepaid Calculator (Multiple Vehicles)")

st.markdown("Enter multiple vehicles below 👇")

# ---------------- INPUT TABLE ----------------
input_df = st.data_editor(
    pd.DataFrame({
        "Sl No": [1],
        "Vehicle No": ["BG-3-A0394"],
        "Vehicle Description": ["Bolero"],
        "Document Type": ["Insurance"],
        "Amount (Nu.)": [15000.00],
        "Start Date": [date(2025, 1, 1)],
        "End Date": [date(2025, 12, 31)]
    }),
    num_rows="dynamic",
    use_container_width=True
)

# ---------------- RUN ----------------
if st.button("Run Report"):
    result_rows = []

    for _, row in input_df.iterrows():
        curr, prepaid = calculate_prepaid(
            row["Amount (Nu.)"],
            row["Start Date"],
            row["End Date"]
        )

        gl_code, _ = GL_MAPPING[row["Document Type"]]

        result_rows.append({
            "Sl No": row["Sl No"],
            "Vehicle No": row["Vehicle No"],
            "Vehicle Description": row["Vehicle Description"],
            "GL Code": gl_code,
            "Document Type": row["Document Type"],
            "Current Amount (Nu.)": curr,
            "Prepaid Amount (Nu.)": prepaid
        })

    result_df = pd.DataFrame(result_rows)

    # ---------------- PIVOT (LIKE YOUR EXCEL) ----------------
    final_table = result_df.pivot_table(
        index=["Sl No", "Vehicle No", "Vehicle Description"],
        columns=["Document Type"],
        values=["Current Amount (Nu.)", "Prepaid Amount (Nu.)"],
        aggfunc="sum",
        fill_value=0
    )

    final_table = final_table.reset_index()

    st.subheader("📊 Vehicle Prepaid Summary")
    st.dataframe(final_table, use_container_width=True)

    # ---------------- TOTAL CHECK ----------------
    st.success(
        f"Total Prepaid Amount: Nu. {result_df['Prepaid Amount (Nu.)'].sum():,.2f}"
    )

    # ---------------- EXPORT ----------------
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        final_table.to_excel(writer, sheet_name="Prepaid Report", index=False)

    output.seek(0)

    st.download_button(
        "📤 Export Final Report to Excel",
        data=output,
        file_name="Vehicle_Prepaid_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
