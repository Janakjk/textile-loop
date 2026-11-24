import streamlit as st
from database import query
from classification import MATERIALS, FTYPES
import components as ui

ui.hero("Find Recyclers & NGOs", "Verified destination directory used for automatic category and region matching", "building")

st.info("Directory listings represent verified cloth donation centres, NGOs, and recycling facilities. Select your city to easily access local donation and recycling options.")

d = query("SELECT * FROM recycler_directory")
ok = lambda ms, mat: "All" in [m.strip() for m in ms.split(",")] or mat in [m.strip() for m in ms.split(",")]

st.subheader("Filter Directory by City & Organization")

# Quick City Filter
city_options = ["All Cities", "Mumbai", "Pune", "Latur", "Other Regions"]
c1, c2, c3 = st.columns([1.2, 1, 1])
selected_city = c1.selectbox("Select City", city_options, key="rec_city_filter")
mat = c2.selectbox("Accepted Fiber", ["Any"] + MATERIALS, key="rec_mat_filter")
ft = c3.selectbox("Facility Classification", ["Any"] + FTYPES, key="rec_ftype_filter")

search_kw = st.text_input("Quick Search (Name, Locality, or Keyword)", placeholder="e.g. Hopenlife, Kapada Bank, ReCircle, Sakhi, Moshi, Roadside", key="rec_kw_filter").strip()

v = d
# City filtering
if selected_city == "Mumbai":
    v = v[v.location.str.contains("Mumbai", case=False, na=False)]
elif selected_city == "Pune":
    v = v[v.location.str.contains("Pune|Moshi|Talegaon", case=False, na=False)]
elif selected_city == "Latur":
    v = v[v.location.str.contains("Latur", case=False, na=False)]
elif selected_city == "Other Regions":
    v = v[~v.location.str.contains("Mumbai|Pune|Moshi|Talegaon|Latur", case=False, na=False)]

# Fiber & classification filters
if mat != "Any":
    v = v[v.materials.apply(lambda m: ok(m, mat))]
if ft != "Any":
    v = v[v.ftype == ft]
if search_kw:
    kw_mask = (
        v.name.str.contains(search_kw, case=False, na=False) |
        v.description.str.contains(search_kw, case=False, na=False) |
        v.location.str.contains(search_kw, case=False, na=False) |
        v.contact.str.contains(search_kw, case=False, na=False)
    )
    v = v[kw_mask]

st.markdown(f"**Showing {len(v)} verified organization(s)** for **{selected_city}**:")

if v.empty:
    st.warning("No facilities match the selected filter criteria. Try choosing 'All Cities' or clearing the search keyword.")
else:
    display_cols = {
        "name": "Organization / Facility",
        "ftype": "Facility Type",
        "location": "Operational City / Region",
        "materials": "Accepted Materials",
        "collection": "Collection Method",
        "contact": "Contact Channel / Location Link",
        "description": "Intake Scope & Capability"
    }
    v_display = v[list(display_cols.keys())].rename(columns=display_cols)
    st.dataframe(v_display, hide_index=True, width="stretch")

    st.subheader("📍 Direct Contact & Map Navigation")
    fac_choices = {row.id: f"{row.name} ({row.location} — {row.ftype})" for row in v.itertuples()}
    target_id = st.selectbox("Select Organization for Direct Contact & Location Links", list(fac_choices), format_func=fac_choices.get, key="direct_fac_select")
    selected_fac = v[v.id == target_id].iloc[0]

    contact_val = str(selected_fac.contact).strip()
    is_link = contact_val.startswith("http://") or contact_val.startswith("https://")

    col_details, col_action = st.columns([2, 1])
    with col_details:
        st.markdown(f"""
        ### {selected_fac['name']}
        * **Classification:** `{selected_fac.ftype}`
        * **Operational City / Region:** {selected_fac.location}
        * **Accepted Materials:** {selected_fac.materials}
        * **Collection / Drop-off Method:** {selected_fac.collection}
        * **Scope & Guidelines:** {selected_fac.description}
        """)
    with col_action:
        st.markdown("#### Direct Action")
        if is_link:
            st.link_button("🗺️ Open Google Maps Location", contact_val, type="primary")
        elif "Phone:" in contact_val or any(c.isdigit() for c in contact_val):
            st.success(f"📞 **Direct Phone:** {contact_val}")
        else:
            st.info(f"**Contact Channel:** {contact_val}")
