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
                st.session_state.show_report = False # Hide old report when new data added
                st.rerun()

    # --- UPDATED CALCULATE BUTTON ---
    if st.button("🚀 Calculate & Show Report", type="primary", use_container_width=True):
        if not st.session_state.vehicles:
            st.session_state.entry_status = "Error: No data added!"
            st.rerun()
        else:
            st.session_state.show_report = True
            st.session_state.entry_status = "Report Generated!"
            st.rerun() # This ensures the main area updates immediately

    if st.button("🗑️ Reset All", use_container_width=True):
        st.session_state.vehicles = []
        st.session_state.show_report = False
        st.session_state.entry_status = "Ready for new entry"
        st.rerun()
