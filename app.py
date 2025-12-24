import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Vehicle Prepaid Calculator",
    layout="wide"
)

# ================= GL MAPPING =================
GL_MAPPING = {
    "Insurance": ("432200", "Insurance on Vehicle"),
    "Blue Book": ("450110", "R&M of Vehicle (Ser)"),
    "Fitness": ("450110", "R&M of Vehicle (Ser)"),
    "Emission": ("450110", "R&M of Vehicle (Ser)")
}

DOC_TYPES = list(GL_MAPPING.keys())

# ================= SESSION STATE =================
if "vehicle_data" not in st.session_state:
    st.session_state.vehicle_data = pd.DataFrame(
        columns=[
            "Vehicle No",
            "Vehicle Description",
            "Document Type",
            "Amount (Nu.)",
            "Start Date",
            "End Date"
        ]
    )

# ================= CALCULATION LOGIC =================
def calculate_prepaid(amount, start_date, end_date):
    total_days = (end_date - start_date).days + 1
    rate_per_day = amount / total_days

    first_prepaid_day = date(start_date.year + 1, 1, 1)

    if end_date < first_prepaid_day:
        prepaid_days = 0
    else:
        prepaid_days = (end_date - first_prepaid_day).days + 1

    prepaid_amount = round(prepaid_days * rate_per_day, 2)
    current_amount = round(amount - prepaid_amount, 2)

    return current_amount, prepaid_amount

# ================= HEADER =================
st.markdown(
    """
    <div style="text-align:center; padding:18px; border-radius:12px;
    background: linear-gradient(90deg, #1f77b4, #2ca02c);">
        <h1 style="color:white; margin:0;">Vehicle Prepaid Calculator</h1>
        <h4 style="color:#e6f2ff;">Developed by: PRAKASH GIRI</h4>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ================= SIDEBAR INPUT =================
st.sidebar.header("➕ Add Vehicle Entry")

vehicle_no = st.sidebar.text_input("Vehicle No")
vehicle_desc = st.sidebar.text_input("Vehicle Description")
doc_type = st.sidebar.selectbox("Document Type", DOC_TYPES)
amount = st.sidebar.number_input("Amount (Nu.)", min_value=0.0, step=0.01)
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

if st.sidebar.button("Add Vehicle"):
    if vehicle_no and vehicle_desc:
        new_row = {
            "Vehicle No": vehicle_no,
            "Vehicle Description": vehicle_desc,
            "Document Type": doc_type,
            "Amount (Nu.)": amount,
            "Start Date": start_date,
            "End Date": end_date
        }

        st.session_state.vehicle_data = pd.concat(
            [st.session_state.vehicle_data, pd.DataFrame([new_row])],
            ignore_index=True
        )

        st.sidebar.success("Vehicle added successfully")
    else:
        st.sidebar.error("Vehicle No and Description are required")

# ================= DISPLAY INPUT TABLE =================
st.subheader("📋 Entered Vehicle Data")

edited_df = st.data_editor(
    st.session_state.vehicle_data,
    use_container_width=True,
    num_rows="dynamic"
)

st.session_state.vehicle_data = edited_df

# ================= GENERATE REPORT =================
if st.button("📊 Generate Prepaid Report"):
    if edited_df.empty:
        st.warning("No vehicle data entered")
    else:
        results = []

        for idx, row in edited_df.iterrows():
            current_amt, prepaid_amt = calculate_prepaid(
                row["Amount (Nu.)"],
                row["Start Date"],
                row["End Date"]
            )

            gl_code, _ = GL_MAPPING[row["Document Type"]]

            results.append(
                {
                    "Sl No": idx + 1,
                    "Vehicle No": row["Vehicle No"],
                    "Vehicle Description": row["Vehicle Description"],
                    "GL Code": gl_code,
                    "Document Type": row["Document Type"],
                    "Current Amount (Nu.)": current_amt,
                    "Prepaid Amount (Nu.)": prepaid_amt
                }
            )

        result_df = pd.DataFrame(results)

        # ================= PIVOT TABLE =================
        pivot_df = (
            result_df.pivot_table(
                index=["Sl No", "Vehicle No", "Vehicle Description"],
                columns="Document Type",
                values=["Current Amount (Nu.)", "Prepaid Amount (Nu.)"],
                aggfunc="sum",
                fill_value=0
            )
            .reset_index()
        )

        # ===== FLATTEN MULTIINDEX COLUMNS (CRITICAL) =====
        pivot_df.columns = [
            f"{col[0]} - {col[1]}" if isinstance(col, tuple) else col
            for col in pivot_df.columns
        ]

        st.markdown("---")
        st.subheader("✅ Vehicle Prepaid Summary")
        st.dataframe(pivot_df, use_container_width=True)

        st.success(
            f"Total Prepaid Amount: Nu. {result_df['Prepaid Amount (Nu.)'].sum():,.2f}"
        )

        # ================= EXCEL EXPORT =================
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            pivot_df.to_excel(
                writer,
                sheet_name="Prepaid Report",
                index=False
            )

        output.seek(0)

        st.download_button(
            label="📤 Export to Excel",
            data=output,
            file_name="Vehicle_Prepaid_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

st.markdown("---")
st.caption("Vehicle Prepaid Calculator | Bhutan | Financial Year Based")
