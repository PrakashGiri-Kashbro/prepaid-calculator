import streamlit as st
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
import calendar

st.title("Prepaid Insurance Calculator")

premium = st.number_input("Premium Amount (Nu.)", min_value=0.0)
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")

def calculate_prepaid_logic(premium, start_date, end_date):
    total_days = (end_date - start_date).days + 1
    if total_days <= 0:
        return None, "End date must be after start date"

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
            last_day_month = date(curr.year, curr.month, calendar.monthrange(curr.year, curr.month)[1])
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
        "rate_per_day": rate_per_day,
        "total_days": total_days,
        "current_days": current_days,
        "prepaid_days": prepaid_days,
        "current_amount": current_amount,
        "prepaid_amount": prepaid_amount,
        "monthly_breakdown": monthly_breakdown
    }, None

if st.button("Calculate"):
    result, error = calculate_prepaid_logic(premium, start_date, end_date)

    if error:
        st.error(error)
    else:
        st.success("Calculation done")

        st.write(result)

        if result["monthly_breakdown"]:
            st.dataframe(pd.DataFrame(result["monthly_breakdown"]))
