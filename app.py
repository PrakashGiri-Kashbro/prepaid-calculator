def calculate_prepaid_logic(premium, start_date, end_date):
    # Inclusive day count
    total_days = (end_date - start_date).days + 1

    if total_days <= 0:
        return None, "Error: End date must be on or after start date."

    # Rate per day
    rate_per_day = round(premium / total_days, 2)

    # Prepaid starts from 1st Jan of next year
    first_prepaid_day = date(start_date.year + 1, 1, 1)

    monthly_breakdown = []

    if end_date < first_prepaid_day:
        current_booking_days = total_days
        prepaid_days = 0
    else:
        last_day_current_year = date(start_date.year, 12, 31)
        current_booking_days = (last_day_current_year - start_date).days + 1
        prepaid_days = (end_date - first_prepaid_day).days + 1

        curr = first_prepaid_day
        while curr <= end_date:
            last_day_of_month = date(
                curr.year,
                curr.month,
                calendar.monthrange(curr.year, curr.month)[1]
            )
            actual_end = min(last_day_of_month, end_date)
            days_in_month = (actual_end - curr).days + 1

            monthly_breakdown.append({
                "Month": curr.strftime("%b %Y"),
                "Number of Days": days_in_month,
                "Amount (Nu.)": round(days_in_month * rate_per_day, 2)
            })

            curr = actual_end + relativedelta(days=1)

    prepaid_amount = round(rate_per_day * prepaid_days, 2)
    current_amount = round(premium - prepaid_amount, 2)

    return {
        "rate_per_day": rate_per_day,
        "total_days": total_days,
        "current_days": current_booking_days,
        "prepaid_days": prepaid_days,
        "current_amount": current_amount,
        "prepaid_amount": prepaid_amount,
        "monthly_breakdown": monthly_breakdown
    }, None
