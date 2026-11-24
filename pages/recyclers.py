from pathlib import Path
import streamlit as st
from database import query, add_request, remaining
from classification import MATERIALS, FTYPES, SUITABLE
import components as ui

ui.hero("Find Recyclers & NGOs", "Verified destination directory and direct collection dispatch management", "building")

if st.session_state.get("flash_dispatch"):
    st.success(st.session_state.pop("flash_dispatch"))

st.info("Directory listings represent organizations compiled from institutional disclosures and public directories. Always contact facilities directly to confirm intake guidelines prior to dispatch.")

d = query("SELECT * FROM recycler_directory")
ok = lambda ms, mat: "All" in [m.strip() for m in ms.split(",")] or mat in [m.strip() for m in ms.split(",")]

st.subheader("Filter Directory")
a, b, c = st.columns(3)
mat = a.selectbox("Accepted Fiber", ["Any"] + MATERIALS)
ft = b.selectbox("Facility Classification", ["Any"] + FTYPES)
loc = c.text_input("Filter by Location", placeholder="e.g. Pune, Moshi, Surat")

v = d
if mat != "Any":
    v = v[v.materials.apply(lambda m: ok(m, mat))]
if ft != "Any":
    v = v[v.ftype == ft]
if loc:
    v = v[v.location.str.contains(loc, case=False, regex=False)]

display_cols = {
    "name": "Organization / Facility",
    "ftype": "Facility Type",
    "materials": "Accepted Materials",
    "collection": "Collection Method",
    "location": "Operational Region",
    "contact": "Contact Channel",
    "description": "Intake Scope & Capability"
}
v_display = v[list(display_cols.keys())].rename(columns=display_cols)
st.dataframe(v_display, hide_index=True, width="stretch")

st.subheader("Dispatch Collection Request")
w = query("SELECT id, reg_id, material, waste_category, quantity_kg, image_path FROM waste_records ORDER BY id DESC")
w["rem"] = w.id.apply(remaining)
w = w[w.rem > 0]

if w.empty:
    st.info("All registered waste batches have already been allocated to active collection requests.")
else:
    c1, c2 = st.columns([1, 1])
    i = c1.selectbox(
        "Select Pending Waste Batch",
        w.index,
        format_func=lambda idx: f"{w.loc[idx, 'reg_id']} | {w.loc[idx, 'material']} ({w.loc[idx, 'rem']:.1f} kg available)"
    )
    r = w.loc[i]
    opts = d[d.ftype.isin(SUITABLE[r.waste_category]) & d.materials.apply(lambda m: ok(m, r.material))]
    
    st.caption(f"Batch Category: **{r.waste_category}** — Directory filtered strictly to eligible destinations.")
    
    if r.image_path and Path(str(r.image_path)).exists():
        st.image(str(r.image_path), caption=f"Batch Photograph ({r.reg_id})", width=220)
    
    if opts.empty:
        st.error("No eligible facility matching this material and category was found in the directory.")
    else:
        j = c2.selectbox(
            "Target Destination Facility",
            opts.index,
            format_func=lambda idx: f"{opts.loc[idx, 'name']} ({opts.loc[idx, 'location']})",
            key=f"target_fac_{r.id}"
        )
        max_q = float(r.rem)
        min_q = min(0.1, max_q)
        q = st.number_input(
            "Dispatch Quantity (kg)",
            min_value=min_q,
            max_value=max_q,
            value=max_q,
            step=0.5 if max_q < 5 else 1.0,
            key=f"dispatch_q_{r.id}"
        )
        dispatch_notes = st.text_input("Dispatch Remarks / Pickup Logistics Instructions", placeholder="e.g. Packed in labelled bags, loading dock available", key=f"disp_notes_{r.id}")
        
        if st.button("Submit Collection Request", key=f"btn_dispatch_{r.id}"):
            try:
                cid = add_request(r.id, opts.loc[j, "id"], q, notes=dispatch_notes)
                st.session_state["flash_dispatch"] = f"Collection request initiated successfully. Unique Tracking ID: **{cid}**"
                st.rerun()
            except ValueError as e:
                st.error(str(e))
