import streamlit as st
from database import init_db
from components import inject_css, render_html

st.set_page_config(page_title="TextileLoop - Circular Textile Systems", page_icon=":material/recycling:", layout="wide")
init_db()
inject_css()

st.logo(":material/recycling:", size="large")

render_html("""
<div style="padding: 10px 4px 16px 4px; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 14px;">
    <div style="display:flex; align-items:center; gap:10px;">
        <div style="width:34px; height:34px; border-radius:8px; background:#1B4332; border:1px solid #2D6A4F; display:flex; align-items:center; justify-content:center; color:#52B788;">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 19H4.815a1.83 1.83 0 0 1-1.57-.881 1.785 1.785 0 0 1-.004-1.784L7.196 9.5"/><path d="M11 19h8.2a1.8 1.8 0 0 0 1.577-.925 1.785 1.785 0 0 0 0-1.8L17.5 10"/><path d="m15.5 13-3.5 6 3.5 6"/><path d="M17 19H8"/><path d="m2 9 3.5-6 3.5 6"/><path d="m12 3 5.5 9.5"/></svg>
        </div>
        <div>
            <div style="font-size:16px; font-weight:700; color:#FFFFFF; letter-spacing:-0.01em;">TextileLoop</div>
            <div style="font-size:11px; font-weight:500; color:#94A3B8; text-transform:uppercase; letter-spacing:0.04em;">Circular Textile Systems</div>
        </div>
    </div>
</div>
""", sidebar=True)

P = lambda f, t, i: st.Page(f"pages/{f}.py", title=t, icon=i)
pg = st.navigation([
    P("home", "Home Dashboard", ":material/dashboard:"),
    P("register", "Register Textile Waste", ":material/post_add:"),
    P("classify", "Waste Classification", ":material/category:"),
    P("recyclers", "Find Recyclers & NGOs", ":material/domain:"),
    P("collection", "Collection Requests", ":material/local_shipping:"),
    P("tracking", "Waste Tracking", ":material/route:"),
    P("impact_page", "Environmental Impact", ":material/analytics:"),
    P("admin", "Admin Panel", ":material/admin_panel_settings:"),
    P("about", "About Project", ":material/info:")
])

pg.run()
