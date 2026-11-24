import streamlit as st
import components as ui

ui.hero("About TextileLoop", "Institutional and commercial textile circularity infrastructure", "info")

st.subheader("Platform Context & Problem Statement")
st.write(
    "Post-consumer and post-industrial textile waste from universities, hostels, hospitality centers, tailoring establishments, "
    "and healthcare institutions is overwhelmingly discarded into unsegregated municipal solid waste streams. "
    "Consequently, recyclable celluloid fibers, high-tensile synthetics, and reusable apparel end up in overburdened landfills, "
    "while waste generators lack transparent, structured pipelines to verified regional recyclers, upcycling studios, and charitable distribution networks."
)

st.subheader("System Architecture & Core Functionality")
ui.render_html(f'''
<div class="tl-feature-grid">
    <div class="tl-feature-item">
        <div class="tl-feature-icon">{ui.icon_svg("document", 16, "#1B4332")}</div>
        <div class="tl-feature-text">
            <b>1. Standardized Intake Registration</b><br>
            Captures granular batch metrics: generator sector, material type, physical condition, and batch weight (kg).
        </div>
    </div>
    <div class="tl-feature-item">
        <div class="tl-feature-icon">{ui.icon_svg("category", 16, "#1B4332")}</div>
        <div class="tl-feature-text">
            <b>2. Automated Rule-Based Categorization</b><br>
            Instantly evaluates fiber suitability and condition to route batches to direct reuse, mechanical recycling, craft upcycling, or hazardous biomedical channels.
        </div>
    </div>
    <div class="tl-feature-item">
        <div class="tl-feature-icon">{ui.icon_svg("building", 16, "#1B4332")}</div>
        <div class="tl-feature-text">
            <b>3. Verified Recycler Matching</b><br>
            Filters directory candidates strictly by capability, accepted fiber classes, and geographical coverage.
        </div>
    </div>
    <div class="tl-feature-item">
        <div class="tl-feature-icon">{ui.icon_svg("timeline", 16, "#1B4332")}</div>
        <div class="tl-feature-text">
            <b>4. Audited Chain of Custody</b><br>
            End-to-end status progression log with operator attribution and timestamp recording for verifiable environmental claims.
        </div>
    </div>
</div>
''')

st.subheader("Technical Specifications & Data Model")
st.markdown("""
- **Backend Architecture:** Python, Streamlit Framework, SQLite relational engine, Pandas data pipelines, Plotly vector analytics.
- **Security & Cryptography:** PBKDF2-HMAC-SHA256 password hashing with 200,000 iterations and per-user cryptographic salt generation.
- **Relational Schema:**
  - `users`: Administrator credentials and cryptographic salt keys.
  - `waste_records`: Ingested batch declarations and physical attributes.
  - `recycler_directory`: Verified organizational directory and operational criteria.
  - `collection_requests`: Linked dispatch requests with quantity constraints.
  - `processing_records`: Audited recovery outcomes (verified reuse vs. recycling).
  - `status_log`: Append-only historical audit trail of all custody transitions.
""")

st.subheader("Regulatory Compliance & Bio-Waste Safeguards")
st.write(
    "Textiles sourced from healthcare facilities or flagged as contaminated or potentially infectious are strictly prohibited "
    "from entering general donation, recycling, or upcycling pipelines. The classification engine isolates these batches under "
    "**Restricted or contaminated textiles** protocols, mandating sealed containment and transfer exclusively to authorized common bio-medical waste treatment facilities (CBWTF) "
    "in compliance with statutory pollution control board standards."
)

ui.disclaimer()
