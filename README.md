# Senate 2026 · Battle for 51

A customizable **2026 U.S. Senate election simulator** built using Python, Streamlit, Plotly, and pandas.

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

Your browser opens the dashboard. Click D / R / Uncalled on any of the 35 races to update the national chamber count, 100-seat chart, and U.S. map. Use the sidebar to reset to the *current holder* baseline or try the *rating-based* scenario. Download results as CSV.

## Assumptions

- Election Day: November 3, 2026. 35 contested seats = 33 regularly scheduled races + special elections in Ohio and Florida.
- 65 seats are not up: 31 Republican and 34 Democratic-caucus (32 Democrats plus 2 independents).
- 2026 races presently held by: 22 Republicans and 13 Democrats.
- By default each contested seat is assigned to its current holder (not a prediction).
- Rating labels are an October 6, 2026 snapshot and are not constantly refreshed.
- UI is a simplified two-caucus model: Nebraska has a notable independent candidacy not accurately modeled by the D/R switch.
- State map describes the contested Senate seat only; two senators represent each state in the real chamber.
- Uncalled seats are gray. A party only has an assured majority once it has at least 51 assigned seats. At 50-50 the Republican vice president casts the tie-breaking vote in this cycle.

## Sources

- https://www.uspresidentialelectionnews.com/2026-senate-elections/ (updated Oct. 7, 2026)
- https://www.cookpolitical.com/ratings/senate-race-ratings

No live results or web API required.
