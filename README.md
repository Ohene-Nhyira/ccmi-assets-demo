# CCMI House Ledger — no-database demo

This is a visual prototype with fictional sample data. No Baserow, Supabase, API keys, tables, or secrets are required. Data is stored only in Streamlit session state and may reset when the browser is refreshed or the session ends. Do not enter real personal or confidential information.

## Deploy in a browser
1. Create a GitHub repository.
2. Upload app.py and requirements.txt to its root.
3. Create .streamlit/config.toml and paste the supplied theme configuration there. Keep the dot in .streamlit.
4. In Streamlit Community Cloud, create an app from the repository, choose the main branch and app.py as the entrypoint, and deploy. No secrets are needed.
5. Open the generated app address.

## Run locally (optional)
python -m pip install -r requirements.txt
streamlit run app.py

## Try the demo
Overview -> Asset Register -> add JPC-MIC-002 -> Issue & Return -> issue it -> Receive a return -> return it damaged -> Maintenance -> complete a repair -> Reports -> download a CSV.

The theme uses purple, lavender and white. Test with sample data only. Each browser session has its own data; users are not sharing a live database. The app has no verified approvals or authentication. The activity feed is illustrative, not an audit-grade log.
