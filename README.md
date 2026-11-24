# TextileLoop - Closing the Loop on Textile Waste
## Run (VS Code terminal, Windows)
    py -3.11 -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    streamlit run app.py
Open http://localhost:8501 in Chrome or Edge. Works offline after install.
## Structure
app.py (entry, navigation) | database.py (schema, queries, hashing) | classification.py (rules) | impact.py (calculations) | components.py (CSS, infographics) | pages/ (9 pages) | data/ (SQLite file, created on first run)
## Notes
- First visit to Admin Panel asks you to create the admin account (stored as a salted PBKDF2 hash, nothing in source code).
- Demo data is created on first run. To reset, stop the app and delete data/textileloop.db.
## Troubleshooting
- "streamlit not recognized": activate the venv, then reinstall with pip.
- "st.navigation" error: run pip install -U streamlit.
- Port busy: streamlit run app.py --server.port 8502
