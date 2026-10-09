# Senate 2026 — Interactive Polling & Scenario Simulator (Version 2)

A Python / Streamlit / Plotly dashboard showing 65 fixed U.S. Senate seats, 35 contested elections, a **dated polling snapshot**, and editable hypothetical election outcomes.

## Deploy on Streamlit Community Cloud

Upload `app.py`, `requirements.txt`, `polls.csv`, and this `README.md` to the root of your public GitHub repository (`sakib18030/senate-2026-simulator`). Streamlit auto-redeploys when code changes are committed. **All four files are needed.**

## Data refresh

The app checks the repository's `polls.csv` hourly and falls back to the bundled local copy if it cannot load the remote file. **Poll numbers do not automatically scrape a third-party polling service.** Update `polls.csv` in GitHub when new published polls arrive, providing source URLs and reported dates. Use the “Check data source now” sidebar button to bypass the cache. A proper licensed automated feed could be connected later.

For each poll, supply `state` (2-letter postal code), `dem_candidate`, `rep_candidate`, `dem_pct`, `rep_pct`, `pollster`, `reported_date` (YYYY-MM-DD), `source_url`, and optional `image_dem` and `image_rep` direct `https://` image URLs (only use photos you are permitted to reproduce). Missing values mean the race is unassigned. A poll tie also stays unassigned.

**Important:** `polls.csv` contains *single published poll results*, not a weighted polling average. It currently covers only a subset of the 35 contested elections; other races remain unassigned. The map is a scenario visualization, **not a prediction of election winners**. Candidate profiles shown are tied to specific surveys, not necessarily a complete candidate list in multiparty races.

## Source links
- https://www.realclearpolling.com/latest-polls/senate
- https://www.cookpolitical.com/ratings/senate-race-ratings
- https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart

## Run locally (optional)

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Roadmap

- Add more individually verified poll entries and authorized candidate photo URLs.
- Add poll history and separate multiple-poll average rather than overwriting the latest survey.
- Improve state clicking UX, scenario comparison, and independent/third-party candidate handling.
