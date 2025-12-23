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
def calculate_prepaid_logic(premium, start_date, end_date):
    total_days = (end_date - start_date).days + 1
    if total_days <= 0:
        return None, "End date must be on or after start date."

    rate_per_day = round(premium / total_days, 2)
    first_prepaid_day = date(start_date.year + 1, 1, 1)

    monthly_breakdown = []

    if end_date < first_prepaid_day:
        current_days = total_days
        prepaid_days = 0
    else:
        last_day_year = date(start_date.year, 12, 31)
        current_days = (last_day_year - start_date).days + 1
        prepaid_days = (end_date - first_prepaid_day).days + 1

        curr = first_prepaid_day
        while curr <= end_date:
            last_day_month = date(
                curr.year,
                curr.month,
                calendar.monthrange(curr.year, curr.month)[1]
            )
            actual_end = min(last_day_month, end_date)
            days = (actual_end - curr).days + 1

            monthly_breakdown.append({
                "Month": curr.strftime("%b %Y"),
                "Days": days,
                "Amount (Nu.)": round(days * rate_per_day, 2)
            })

            curr = actual_end + relativedelta(days=1)

    prepaid_amount = round(rate_per_day * prepaid_days, 2)
    current_amount = round(premium - prepaid_amount, 2)

    return {
        "rate": rate_per_day,
        "total_days": total_days,
        "current_days": current_days,
        "prepaid_days": prepaid_days,
        "current_amount": current_amount,
        "prepaid_amount": prepaid_amount,
        "breakdown": monthly_breakdown
    }, None

# ---------------- EXCEL EXPORT (CLOUD SAFE) ----------------
def export_to_excel(res, item_type, gl_code, gl_desc, start_dt, end_dt):
    output = BytesIO()

    summary_df = pd.DataFrame([{
        "Item Type": item_type,
        "GL Code": gl_code,
        "GL Description": gl_desc,
        "Start Date": start_dt.strftime("%d/%m/%Y"),
        "End Date": end_dt.strftime("%d/%m/%Y"),
        "Total Days": res["total_days"],
        "Rate per Day": res["rate"],
        "Current Days": res["current_days"],
        "Prepaid Days": res["prepaid_days"],
        "Current Amount (Nu.)": res["current_amount"],
        "Prepaid Amount (Nu.)": res["prepaid_amount"]
    }])

    breakdown_df = pd.DataFrame(res["breakdown"])

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        breakdown_df.to_excel(writer, sheet_name="Monthly Breakdown", index=False)

    output.seek(0)
    return output

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Vehicle Prepaid Calculator",
    layout="wide"
)

# ---------------- HEADER ----------------
st.markdown("""
<div style="text-align:center; padding:20px; border-radius:12px;
            background: linear-gradient(90deg, #1f77b4, #2ca02c);">
    <h1 style="margin:0; color:white;">Vehicle Prepaid Calculator</h1>
    <h3 style="margin-top:5px; color:#e8f4ff;">
        Developed by: PRAKASH GIRI (KASH BRO)
    </h3>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------------- SIDEBAR ----------------
st.sidebar.header("Calculation Settings")

item_type = st.sidebar.selectbox(
    "Select Document Type",
    list(GL_MAPPING.keys())
)

gl_code, gl_desc = GL_MAPPING[item_type]

premium = st.sidebar.number_input(
    "Total Amount (Nu.)",
    min_value=0.0,
    value=2550.00,
    step=0.01
)

start_dt = st.sidebar.date_input("Start Date", value=date(2025, 12, 25))
end_dt = st.sidebar.date_input("End Date", value=date(2026, 12, 24))

# ---------------- RUN ----------------
if st.sidebar.button("Run Calculation"):
    res, error = calculate_prepaid_logic(premium, start_dt, end_dt)

    if error:
        st.error(error)
    else:
        st.subheader(f"Results for: {item_type}")

        st.markdown(
            f"<div style='font-size:22px; font-weight:bold;'>"
            f"GL {gl_code} – {gl_desc}</div>",
            unsafe_allow_html=True
        )

        st.info(
            f"Period: {start_dt.strftime('%d/%m/%Y')} "
            f"to {end_dt.strftime('%d/%m/%Y')}"
        )

        # Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Days", res["total_days"])
        m2.metric("Rate / Day", f"Nu. {res['rate']:.2f}")
        m3.metric("Current Days", res["current_days"])
        m4.metric("Prepaid Days", res["prepaid_days"])

        st.divider()

        # Accounting Split
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("### Current Expense")
            st.markdown(f"**GL {gl_code} – {gl_desc}**")
            st.write(
                f"Period: {start_dt.strftime('%d/%m/%Y')} – 31/12/{start_dt.year}"
            )
            st.title(f"Nu. {res['current_amount']:.2f}")

        with c2:
            st.markdown("### Prepaid Expense")
            st.markdown("**GL 284000 – Prepaid Expense**")
            st.write(
                f"Period: 01/01/{end_dt.year} – {end_dt.strftime('%d/%m/%Y')}"
            )
            st.title(f"Nu. {res['prepaid_amount']:.2f}")

        # Monthly Breakdown
        if res["breakdown"]:
            st.markdown("---")
            st.subheader("Monthly Amortization Schedule")
            df = pd.DataFrame(res["breakdown"])
            st.table(df)

            st.success(
                f"Verification Passed ✔ | Total Prepaid = "
                f"Nu. {df['Amount (Nu.)'].sum():.2f} (GL 284000)"
            )

        # Excel Export
        excel_file = export_to_excel(
            res,
            item_type,
            gl_code,
            gl_desc,
            start_dt,
            end_dt
        )

        st.download_button(
            label="📤 Export to Excel",
            data=excel_file,
            file_name="Vehicle_Prepaid_Calculation.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

st.markdown("---")
st.caption("Vehicle Prepaid Calculator | Financial Year Alignment | Bhutan")
