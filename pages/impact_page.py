import plotly.express as px
import streamlit as st
from database import query, requests_df, STATUSES
from impact import stats
import components as ui

ui.hero("Environmental Impact & Resource Analytics", "Audited landfill diversion rates, fiber recovery breakdown, and circularity indicators", "analytics")

s = stats()

ui.stat_cards([
    ("package", "Registered Material", s["total"]),
    ("truck", "Collected Volume", s["collected"]),
    ("heart", "Donated via NGOs", s["donated"]),
    ("shirt", "Direct Reuse", s["reused"]),
    ("craft", "Upcycled (Craft Products)", s["upcycled"]),
    ("recycle", "Mechanically Recycled", s["recycled"]),
    ("shield", "Authorized Bio-Disposal", s["disposal"]),
    ("clock", "Pending Requests", s["pending"]),
    ("cog", "Under Processing", s["in_process"]),
    ("building", "Active Partners", s["active_partners"])
])

st.subheader("Key Circularity Metrics")
a, b = st.columns(2)
with a:
    ui.ring(s["pct"], "Landfill Diversion Rate (of Total Registered)")
with b:
    ui.ring(s["recovery"], "Material Recovery Efficiency (of Collected)")

w = query("SELECT * FROM waste_records WHERE is_demo=0")
if w.empty:
    st.info("No registered batches yet. Totals stay at 0 kg until a real registration is submitted.")
else:
    st.subheader("Material & Categorical Analysis")
    
    chart_theme = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#334155"),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    c1, c2 = st.columns(2)
    with c1:
        fig_cat = px.pie(
            w,
            names="waste_category",
            values="quantity_kg",
            title="Waste Volume by Category",
            hole=0.45,
            color_discrete_sequence=ui.GREENS
        )
        fig_cat.update_layout(**chart_theme)
        c1.plotly_chart(fig_cat, width="stretch")
        
    with c2:
        mat_agg = w.groupby("material", as_index=False)["quantity_kg"].sum()
        fig_mat = px.bar(
            mat_agg,
            x="material",
            y="quantity_kg",
            title="Material Distribution (kg)",
            labels={"material": "Material", "quantity_kg": "Total (kg)"},
            color_discrete_sequence=["#1B4332"]
        )
        fig_mat.update_layout(**chart_theme)
        fig_mat.update_traces(marker_line_width=0, opacity=0.9)
        c2.plotly_chart(fig_mat, width="stretch")

    st.subheader("Location-Based Statistics & Regional Ingestion")
    l1, l2 = st.columns(2)
    with l1:
        loc_agg = w.groupby("location", as_index=False)["quantity_kg"].sum().sort_values("quantity_kg", ascending=True)
        fig_loc = px.bar(
            loc_agg,
            x="quantity_kg",
            y="location",
            orientation="h",
            title="Waste Volume by Facility Location (kg)",
            labels={"quantity_kg": "Volume (kg)", "location": "Location / City"},
            color_discrete_sequence=["#2D6A4F"]
        )
        fig_loc.update_layout(**chart_theme)
        l1.plotly_chart(fig_loc, width="stretch")

    with l2:
        sec_agg = w.groupby("gen_category", as_index=False)["quantity_kg"].sum()
        fig_sec = px.pie(
            sec_agg,
            names="gen_category",
            values="quantity_kg",
            title="Waste Generation by Institutional Sector",
            hole=0.45,
            color_discrete_sequence=ui.GREENS
        )
        fig_sec.update_layout(**chart_theme)
        l2.plotly_chart(fig_sec, width="stretch")

    w["month"] = w.reg_date.str[:7]
    month_agg = w.groupby("month", as_index=False)["quantity_kg"].sum()
    
    c3, c4 = st.columns(2)
    with c3:
        fig_line = px.line(
            month_agg,
            x="month",
            y="quantity_kg",
            markers=True,
            title="Monthly Intake Trajectory (kg)",
            labels={"month": "Month", "quantity_kg": "Volume (kg)"},
            color_discrete_sequence=["#2D6A4F"]
        )
        fig_line.update_layout(**chart_theme)
        c3.plotly_chart(fig_line, width="stretch")
        
    with c4:
        r = requests_df(exclude_demo=True)
        cnt = r.status.value_counts().reindex(STATUSES, fill_value=0).reset_index()
        cnt.columns = ["status", "requests"]
        fig_status = px.bar(
            cnt,
            x="status",
            y="requests",
            title="Collection Status Distribution",
            labels={"status": "Status", "requests": "Request Count"},
            color_discrete_sequence=["#52B788"]
        )
        fig_status.update_layout(**chart_theme)
        c4.plotly_chart(fig_status, width="stretch")

    st.subheader("Active Recycling & Donation Partners Directory")
    part_df = query("SELECT name, ftype, location, materials, contact FROM recycler_directory ORDER BY ftype, name")
    part_df.columns = ["Partner / Facility Name", "Classification", "Operational Region", "Accepted Materials", "Contact Channel"]
    st.dataframe(part_df, hide_index=True, width="stretch")

    st.subheader("Diversion Pathways: Reuse, Craft Products, and Mechanical Recycling")
    fig_comp = px.bar(
        x=["Direct Reuse", "Upcycled (Craft Products)", "Mechanical Recycling"],
        y=[s["reused"], s["upcycled"], s["recycled"]],
        title="Diversion Outcomes Comparison (kg)",
        labels={"x": "Recovery Channel", "y": "Quantity Diverted (kg)"},
        color_discrete_sequence=["#1B4332"]
    )
    fig_comp.update_layout(**chart_theme)
    st.plotly_chart(fig_comp, width="stretch")

ui.disclaimer()
