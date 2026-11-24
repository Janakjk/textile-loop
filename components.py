import re
import streamlit as st

GREENS = ["#1B4332", "#2D6A4F", "#40916C", "#52B788", "#74C69D", "#D8F3DC"]

SVG_ICONS = {
    "dashboard": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>',
    "package": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>',
    "truck": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.62l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/></svg>',
    "recycle": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 19H4.815a1.83 1.83 0 0 1-1.57-.881 1.785 1.785 0 0 1-.004-1.784L7.196 9.5"/><path d="M11 19h8.2a1.8 1.8 0 0 0 1.577-.925 1.785 1.785 0 0 0 0-1.8L17.5 10"/><path d="m15.5 13-3.5 6 3.5 6"/><path d="M17 19H8"/><path d="m2 9 3.5-6 3.5 6"/><path d="m12 3 5.5 9.5"/></svg>',
    "shirt": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.38 3.46 16 2a4 4 0 0 1-8 0L3.62 3.46a2 2 0 0 0-1.34 2.23l.58 3.47a1 1 0 0 0 .99.84H6v10c0 1.1.9 2 2 2h8a2 2 0 0 0 2-2V10h2.15a1 1 0 0 0 .99-.84l.58-3.47a2 2 0 0 0-1.34-2.23z"/></svg>',
    "clock": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "leaf": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>',
    "document": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/><line x1="10" x2="8" y1="9" y2="9"/></svg>',
    "category": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/></svg>',
    "building": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="20" x="4" y="2" rx="2" ry="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M12 6h.01"/><path d="M12 10h.01"/><path d="M12 14h.01"/><path d="M16 10h.01"/><path d="M16 14h.01"/><path d="M8 10h.01"/><path d="M8 14h.01"/></svg>',
    "timeline": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    "analytics": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" x2="18" y1="20" y2="10"/><line x1="12" x2="12" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="14"/></svg>',
    "shield": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/></svg>',
    "info": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>',
    "check_circle": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    "calendar": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>',
    "cog": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>',
    "x_circle": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>',
    "alert_triangle": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>',
    "arrow_right": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>',
    "search": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>',
    "users": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "heart": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>',
    "map_pin": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/></svg>',
    "check": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
}

def icon_svg(name, size=22, color="currentColor"):
    svg = SVG_ICONS.get(name, SVG_ICONS["info"])
    return svg.replace('width="24"', f'width="{size}"').replace('height="24"', f'height="{size}"').replace('stroke="currentColor"', f'stroke="{color}"')

def clean_html(html_str):
    return "".join(line.strip() for line in html_str.splitlines())

def render_html(html_str, sidebar=False):
    c = clean_html(html_str)
    if sidebar:
        st.sidebar.html(c)
    else:
        st.html(c)

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    background-color: #F8FAFC !important;
    color: #0F172A;
}

[data-testid="stSidebar"] {
    background: #0B251B !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}
[data-testid="stSidebar"] * {
    color: #E2E8F0 !important;
}
[data-testid="stSidebarNav"] li div a {
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
    padding: 8px 12px !important;
    margin: 2px 0 !important;
}
[data-testid="stSidebarNav"] li div a:hover {
    background: rgba(255, 255, 255, 0.08) !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebarNav"] li div a[aria-current="page"] {
    background: #1B4332 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border-left: 3px solid #52B788 !important;
}

h1, h2, h3, h4, h5, h6 {
    color: #0F2E22 !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}
h1 { font-size: 26px !important; }
h2 { font-size: 20px !important; margin-top: 24px !important; margin-bottom: 12px !important; }
h3 { font-size: 16px !important; }

.stButton>button, .stFormSubmitButton>button {
    background: #1B4332 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.stButton>button:hover, .stFormSubmitButton>button:hover {
    background: #2D6A4F !important;
    box-shadow: 0 4px 6px -1px rgba(27, 67, 50, 0.2) !important;
    transform: translateY(-1px);
}
.stButton>button:active, .stFormSubmitButton>button:active {
    transform: translateY(0);
}

div[data-baseweb="input"] {
    border-radius: 8px !important;
    border-color: #CBD5E1 !important;
    background-color: #FFFFFF !important;
}
div[data-baseweb="input"]:focus-within {
    border-color: #2D6A4F !important;
    box-shadow: 0 0 0 3px rgba(45, 106, 79, 0.15) !important;
}
div[data-baseweb="select"] > div {
    border-radius: 8px !important;
    border-color: #CBD5E1 !important;
    background-color: #FFFFFF !important;
}

.tl-hero {
    background: linear-gradient(135deg, #0B251B 0%, #153E2D 55%, #1B4332 100%);
    color: #FFFFFF;
    padding: 24px 28px;
    border-radius: 14px;
    margin-bottom: 22px;
    box-shadow: 0 4px 20px -2px rgba(11, 37, 27, 0.18);
    display: flex;
    align-items: center;
    gap: 20px;
}
.tl-hero-icon {
    width: 48px;
    height: 48px;
    min-width: 48px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.12);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #52B788;
    border: 1px solid rgba(255, 255, 255, 0.15);
}
.tl-hero h1 {
    color: #FFFFFF !important;
    margin: 0 !important;
    font-size: 24px !important;
    font-weight: 700 !important;
}
.tl-hero p {
    margin: 4px 0 0 !important;
    color: #CBD5E1 !important;
    font-size: 14px !important;
    font-weight: 400 !important;
}

.tl-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    gap: 14px;
    margin-bottom: 20px;
}
.tl-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 16px 18px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    transition: all 0.2s ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 90px;
}
.tl-card:hover {
    border-color: #CBD5E1;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
    transform: translateY(-2px);
}
.tl-card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
}
.tl-card-icon {
    width: 34px;
    height: 34px;
    border-radius: 8px;
    background: #E8F5E9;
    color: #1B4332;
    display: flex;
    align-items: center;
    justify-content: center;
}
.tl-card .v {
    font-size: 22px;
    font-weight: 700;
    color: #0F172A;
    line-height: 1.2;
}
.tl-card .l {
    font-size: 12px;
    font-weight: 500;
    color: #64748B;
}

.tl-flow {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
    margin-bottom: 24px;
}
.tl-step {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 18px 14px;
    text-align: center;
    position: relative;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    transition: all 0.2s ease;
}
.tl-step:hover {
    border-color: #CBD5E1;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}
.tl-step-badge {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #E8F5E9;
    color: #1B4332;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 10px;
    font-weight: 700;
    font-size: 13px;
    border: 1px solid #C8E6C9;
}
.tl-step b {
    display: block;
    color: #0F2E22;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 4px;
}
.tl-step span.desc {
    color: #64748B;
    font-size: 12px;
    line-height: 1.4;
    display: block;
}

.tl-ring-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 22px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}
.tl-ring-caption {
    margin-top: 14px;
    color: #0F2E22;
    font-weight: 600;
    font-size: 14px;
    text-align: center;
}

.tl-seg-wrap {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 22px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}
.tl-seg {
    display: flex;
    height: 20px;
    border-radius: 6px;
    overflow: hidden;
    background: #F1F5F9;
}
.tl-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    margin-top: 14px;
    font-size: 12px;
    color: #475569;
}
.tl-legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
}
.tl-legend-dot {
    width: 10px;
    height: 10px;
    border-radius: 3px;
}

.tl-res {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 20px;
    margin-top: 14px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.tl-res-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid #F1F5F9;
}
.tl-res-tag {
    font-size: 15px;
    font-weight: 700;
    letter-spacing: -0.01em;
}
.tl-res-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 12px;
    font-size: 13px;
    line-height: 1.5;
}
.tl-res-field {
    background: #F8FAFC;
    border-radius: 8px;
    padding: 10px 12px;
    border: 1px solid #EDF2F7;
}
.tl-res-field label {
    display: block;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    color: #64748B;
    margin-bottom: 4px;
}

.tl-disclaimer {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    background: #F1F5F9;
    border-radius: 8px;
    padding: 12px 14px;
    margin-top: 24px;
    font-size: 12px;
    color: #64748B;
    line-height: 1.5;
    border: 1px solid #E2E8F0;
}

.tl-feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 14px;
    margin-top: 14px;
}
.tl-feature-item {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 14px 16px;
    display: flex;
    align-items: flex-start;
    gap: 12px;
}
.tl-feature-icon {
    width: 28px;
    height: 28px;
    min-width: 28px;
    border-radius: 6px;
    background: #E8F5E9;
    color: #1B4332;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 2px;
}
.tl-feature-text {
    font-size: 13px;
    color: #334155;
    line-height: 1.45;
}

@media (max-width: 768px) {
    .tl-hero {
        padding: 18px 16px;
        flex-direction: column;
        align-items: flex-start;
        gap: 12px;
    }
    .tl-hero h1 { font-size: 20px !important; }
    .tl-cards {
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
    }
    .tl-flow {
        grid-template-columns: 1fr;
    }
    .tl-res-grid {
        grid-template-columns: 1fr;
    }
}
@media (max-width: 480px) {
    .tl-cards {
        grid-template-columns: 1fr;
    }
}
</style>"""

def inject_css():
    st.html(CSS)

def hero(title, sub, icon_name="leaf"):
    icon_html = icon_svg(icon_name, 26, "#52B788")
    render_html(f'''
    <div class="tl-hero">
        <div class="tl-hero-icon">{icon_html}</div>
        <div>
            <h1>{title}</h1>
            <p>{sub}</p>
        </div>
    </div>
    ''')

def stat_cards(items):
    cards_html = []
    for icon_name, label, val in items:
        i_html = icon_svg(icon_name, 18, "#1B4332")
        cards_html.append(f'''
        <div class="tl-card">
            <div class="tl-card-top">
                <span class="l">{label}</span>
                <div class="tl-card-icon">{i_html}</div>
            </div>
            <div class="v">{val:,.0f} <span style="font-size:13px;font-weight:500;color:#64748B">kg</span></div>
        </div>
        ''')
    render_html(f'<div class="tl-cards">{"".join(cards_html)}</div>')

def flow():
    steps = [
        (1, "package", "Generate", "Institutional source logging"),
        (2, "document", "Register", "Capture fiber, weight & condition"),
        (3, "category", "Classify", "Rule-based waste categorisation"),
        (4, "users", "Match", "Connect with verified recyclers"),
        (5, "truck", "Collect", "Dispatch & status tracking"),
        (6, "leaf", "Measure", "Audit verified landfill diversion")
    ]
    html_items = []
    for num, icon, title, desc in steps:
        i_html = icon_svg(icon, 16, "#1B4332")
        html_items.append(f'''
        <div class="tl-step">
            <div class="tl-step-badge">{num}</div>
            <b>{title}</b>
            <span class="desc">{desc}</span>
        </div>
        ''')
    render_html(f'<div class="tl-flow">{"".join(html_items)}</div>')

def ring(pct, label, size=160):
    inner = size - 36
    render_html(f'''
    <div class="tl-ring-wrap">
        <div style="width:{size}px;height:{size}px;border-radius:50%;background:conic-gradient(#1B4332 {pct:.1f}%,#E2E8F0 0);display:flex;align-items:center;justify-content:center">
            <div style="width:{inner}px;height:{inner}px;border-radius:50%;background:#FFFFFF;display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:700;color:#0F2E22">
                {pct:.0f}%
            </div>
        </div>
        <div class="tl-ring-caption">{label}</div>
    </div>
    ''')

def segbar(parts):
    tot = sum(v for _, v, _ in parts) or 1
    bar_segments = [f'<div style="width:{v / tot * 100:.1f}%;background:{c}" title="{l}: {v:.0f} kg"></div>' for l, v, c in parts if v > 0]
    legend_items = [
        f'<div class="tl-legend-item"><span class="tl-legend-dot" style="background:{c}"></span><span>{l}: <b>{v:.0f} kg</b> ({v/tot*100:.1f}%)</span></div>'
        for l, v, c in parts
    ]
    render_html(f'''
    <div class="tl-seg-wrap">
        <div class="tl-seg">{"".join(bar_segments)}</div>
        <div class="tl-legend">{"".join(legend_items)}</div>
    </div>
    ''')

def result_card(r):
    red = r["category"].startswith("Restricted")
    accent_col = "#DC2626" if red else "#1B4332"
    bg_col = "#FEF2F2" if red else "#F0FDF4"
    border_col = "#FCA5A5" if red else "#BBF7D0"
    icon_name = "alert_triangle" if red else "check_circle"
    i_html = icon_svg(icon_name, 20, accent_col)
    
    render_html(f'''
    <div class="tl-res" style="border-left: 4px solid {accent_col}">
        <div class="tl-res-header">
            <div style="width:32px;height:32px;border-radius:8px;background:{bg_col};border:1px solid {border_col};display:flex;align-items:center;justify-content:center">
                {i_html}
            </div>
            <div>
                <span class="tl-res-tag" style="color:{accent_col}">{r["category"]}</span>
            </div>
        </div>
        <div class="tl-res-grid">
            <div class="tl-res-field">
                <label>Recommended Destination</label>
                <b>{r["destination"]}</b>
            </div>
            <div class="tl-res-field">
                <label>Technical Rationale</label>
                <span>{r["reason"]}</span>
            </div>
            <div class="tl-res-field" style="grid-column: 1 / -1">
                <label>Required Protocol & Handling</label>
                <span>{r["action"]}</span>
            </div>
        </div>
    </div>
    ''')

def disclaimer():
    i_html = icon_svg("info", 16, "#64748B")
    render_html(f'''
    <div class="tl-disclaimer">
        <div style="min-width:16px;margin-top:1px">{i_html}</div>
        <div>
            <b>System Notice:</b> Environmental diversion figures reflect verified system records. Landfill diversion calculations do not represent automated carbon credits or certified offsets. Records designated <b>DEMO</b> are illustrative sample data for validation purposes.
        </div>
    </div>
    ''')
