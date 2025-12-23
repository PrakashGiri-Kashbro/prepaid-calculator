import streamlit as st
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
import calendar

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
        current_d_
