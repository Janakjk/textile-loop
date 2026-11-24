import re
from datetime import date
import streamlit as st
from database import add_waste
from classification import *
import components as ui

ui.hero("Register Textile Waste", "Log institutional and commercial fabric inventory for automated classification and collection", "document")

with st.form("reg", clear_on_submit=False):
    st.markdown("#### Waste Origin & Generator")
    c1, c2 = st.columns(2)
    gen = c1.text_input("Point of Contact / Generator Name", placeholder="e.g. Dr. Rajesh Sharma")
    inst = c2.text_input("Institution or Organization", placeholder="e.g. Pune Institute of Technology")
    gc = c1.selectbox("Generator Sector", GEN_CATS)
    loc = c2.text_input("Facility Location / City", placeholder="e.g. Shivajinagar, Pune")
    contact = c1.text_input("Contact Email or Phone Number", placeholder="e.g. contact@institution.edu or 9876543210")
    rdate = c2.date_input("Registration Date", value=date.today(), max_value=date.today())

    st.markdown("#### Material Specifications")
    m1, m2, m3 = st.columns(3)
    item = m1.selectbox("Item Classification", ITEM_TYPES)
    mat = m2.selectbox("Primary Fiber / Material", MATERIALS)
    cond = m3.selectbox("Material Condition", CONDITIONS)
    
    q1, q2 = st.columns([1, 2])
    qty = q1.number_input("Batch Quantity (kg)", min_value=0.0, step=0.5, format="%.1f")
    desc = q2.text_input("Additional Notes or Batch Description", placeholder="e.g. Sorted uniforms, buttons removed, clean dry storage")

    st.markdown("#### Batch Photograph Verification")
    st.caption("Upload or capture a photograph of the fabric batch for visual condition verification by recycling partners and administrators.")
    photo_mode = st.radio("Photograph Method", ["Upload Image File", "Capture with Camera", "No Photograph"], horizontal=True)
    
    active_img = None
    if photo_mode == "Upload Image File":
        active_img = st.file_uploader("Select Image (JPG, JPEG, PNG, WEBP)", type=["jpg", "jpeg", "png", "webp"])
    elif photo_mode == "Capture with Camera":
        active_img = st.camera_input("Capture Photograph of Batch")
        
    if active_img:
        st.image(active_img, caption="Photograph Preview — Verified for Ingestion", width=280)

    st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
    go = st.form_submit_button("Submit Waste Registration")

if go:
    ok_contact = re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", contact.strip()) or len(re.sub(r"\D", "", contact)) >= 10
    if not (gen.strip() and inst.strip() and loc.strip()):
        st.error("Generator name, institution, and location are mandatory fields.")
    elif qty <= 0:
        st.error("Batch quantity must be greater than 0 kg.")
    elif not ok_contact:
        st.error("Please provide a valid email address or 10-digit telephone number.")
    else:
        reg = add_waste(dict(
            generator=gen.strip(),
            institution=inst.strip(),
            gen_category=gc,
            item_type=item,
            material=mat,
            cond=cond,
            quantity_kg=qty,
            location=loc.strip(),
            contact=contact.strip(),
            reg_date=rdate,
            description=desc.strip(),
            file_obj=active_img
        ))
        st.success(f"Registration successful. System Tracking Identifier: **{reg}**")
        if active_img:
            st.info("Batch photograph stored and linked to Registration ID.")
        ui.result_card(classify(mat, cond, gc))
