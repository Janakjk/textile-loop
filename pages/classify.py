import pandas as pd
import streamlit as st
from classification import *
from database import query
import components as ui

ui.hero("Waste Classification Engine", "Automated rule-based categorization evaluating fiber chemistry, condition, and clinical exposure", "category")

st.subheader("Interactive Classification Simulator")
st.caption("Select parameters below to test real-time classification logic and downstream routing rules.")

a, b, c = st.columns(3)
m = a.selectbox("Fiber / Material Type", MATERIALS)
cd = b.selectbox("Physical Condition", CONDITIONS)
g = c.selectbox("Source Sector", GEN_CATS)

ui.result_card(classify(m, cd, g))

st.markdown("<div style='height: 14px'></div>", unsafe_allow_html=True)
st.info("Operational Note: Downstream acceptance is subject to each partner facility's active intake rules and machinery specifications. Pre-dispatch coordination is required.")

st.subheader("Routing & Destination Decision Matrix")
rule_df = pd.DataFrame({
    "Waste Category": list(SUITABLE),
    "Eligible Destination Facility Types": [", ".join(v) for v in SUITABLE.values()]
})
st.dataframe(rule_df, hide_index=True, width="stretch")

st.subheader("Registered Batches & Current Classification")
rec_df = query("SELECT reg_id, material, cond, quantity_kg, waste_category FROM waste_records ORDER BY id DESC")
if not rec_df.empty:
    rec_df.columns = ["Registration ID", "Material", "Condition", "Quantity (kg)", "Assigned Category"]
    st.dataframe(rec_df, hide_index=True, width="stretch")
else:
    st.caption("No registered records found in the database.")
