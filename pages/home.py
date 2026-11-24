import streamlit as st
from impact import stats
import components as ui

ui.hero("TextileLoop Dashboard", "Operational overview of institutional textile waste collection, diversion, and recovery", "dashboard")

s = stats()

ui.stat_cards([
    ("package", "Total Registered", s["total"]),
    ("truck", "Collected", s["collected"]),
    ("heart", "Donated via NGOs", s["donated"]),
    ("craft", "Upcycled (Craft Products)", s["upcycled"]),
    ("recycle", "Recycled", s["recycled"]),
    ("cog", "Under Processing", s["in_process"]),
    ("clock", "Pending Dispatch", s["pending"]),
    ("leaf", "Diverted from Landfill", s["diverted"])
])

st.subheader("Textile Circularity Lifecycle")
ui.flow()

st.subheader("Diversion & Material Distribution")
a, b = st.columns([1, 2])
with a:
    ui.ring(s["pct"], "Verified Landfill Diversion Rate")
with b:
    ui.segbar([
        ("Reused", s["reused"], "#1B4332"),
        ("Upcycled (Craft Products)", s["upcycled"], "#40916C"),
        ("Recycled", s["recycled"], "#2D6A4F"),
        ("In Process", s["in_process"], "#52B788"),
        ("Awaiting Collection", s["awaiting"], "#CBD5E1"),
        ("Authorized Disposal", s["disposal"], "#94A3B8")
    ])
    st.caption("Figures come from registered batches only. Audited reuse, craft upcycling, and recycling count as diversion.")

st.subheader("Platform Objectives & Operational Scope")
st.write(
    "Textile waste from institutions, commercial entities, and tailoring hubs is frequently discarded into mixed landfill streams. "
    "TextileLoop provides end-to-end digital tracking: registering batch quantities, executing rule-based classification, matching batches to verified recovery partners, "
    "and auditing materials through each stage of reuse, recycling, or authorized clinical disposal."
)

ui.render_html(f'''
<div class="tl-feature-grid">
    <div class="tl-feature-item">
        <div class="tl-feature-icon">{ui.icon_svg("check", 16, "#1B4332")}</div>
        <div class="tl-feature-text"><b>Systematic Waste Segregation</b><br>Structured differentiation of reusable garments, mechanical recycling candidates, and bio-waste.</div>
    </div>
    <div class="tl-feature-item">
        <div class="tl-feature-icon">{ui.icon_svg("check", 16, "#1B4332")}</div>
        <div class="tl-feature-text"><b>Verified Partner Matching</b><br>Direct connection to verified local recyclers, upcycling organizations, and accredited NGOs.</div>
    </div>
    <div class="tl-feature-item">
        <div class="tl-feature-icon">{ui.icon_svg("check", 16, "#1B4332")}</div>
        <div class="tl-feature-text"><b>Regulatory Bio-Waste Compliance</b><br>Strict diversion protocols for contaminated healthcare linens to authorized disposal agencies.</div>
    </div>
    <div class="tl-feature-item">
        <div class="tl-feature-icon">{ui.icon_svg("check", 16, "#1B4332")}</div>
        <div class="tl-feature-text"><b>Audited Diversion Metrics</b><br>Chain-of-custody logging guaranteeing verifiable environmental accounting without estimates.</div>
    </div>
</div>
''')

ui.disclaimer()
