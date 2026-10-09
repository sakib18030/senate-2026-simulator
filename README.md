# Senate 2026 · Battle for 51

[![Open the Streamlit app](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://senate-2026-midelection-simulator.streamlit.app)

**[Try the interactive dashboard](https://senate-2026-midelection-simulator.streamlit.app)** · **[Read the code walkthrough](CODE_WALKTHROUGH.md)**

An educational, interactive **2026 U.S. Senate election scenario simulator**, built with Python, Streamlit, pandas and Plotly. Explore how hypothetical outcomes in individual states change the national balance of Senate seats.

> **Important:** This is a what-if tool, **not** an election forecast, official vote count, or live polling feed. Its default scenario assigns the 35 contested seats to their current holding parties. Race ratings and polling percentages are dated snapshots. User selections are hypothetical.

## What the project demonstrates

- A **100-seat Senate semicircle** that updates as seats are assigned Republican, Democratic-caucus or uncalled.
- A **U.S. state map** showing selected outcomes in states with 2026 Senate races, with state abbreviations.
- A **seat breakdown** showing each party's fixed seats, assigned seats in 2026 contests, and scenario total.
- **Seven highlighted races** — Alaska, Iowa, Kansas, Maine, Michigan, Ohio and Texas — with candidate names, available portraits and dated polling comparisons.
- **All 35 2026 races** editable from the lower "Flip the races" section; sidebar filters, scenario reset and CSV export.
- A public demo deployed through **Streamlit Community Cloud**, connected to this GitHub repository.

## How to try it

1. Open the [live dashboard](https://senate-2026-midelection-simulator.streamlit.app).
2. Start with the **current-holder baseline** (53 Republican / 47 Democratic-caucus seats). This is a starting assumption, not a predicted result.
3. Select a highlighted state in **State Election Details**. Read the candidate information and dated polling snapshot, then choose **Republican wins**, **Democrat wins**, or **Uncalled**.
4. Watch the chamber graphic, map, and party totals respond. The displayed polling percentages do **not** change when you choose a hypothetical winner.
5. Scroll to **Flip the races** to explore all 35 contests. Use sidebar filters to narrow the list; reset to current holders or apply the rating-based scenario at any time.
6. Download the scenario as a CSV.

## How the seat calculations work

Of 100 Senate seats, **65 are not up for election**: 31 Republican seats and 34 Democratic-caucus seats (including independents who caucus with Democrats). The other **35 seats** are represented by editable election scenarios.

```python
republican_total = 31 + number_of_contests_assigned_R
democratic_caucus_total = 34 + number_of_contests_assigned_D
uncalled = 35 - number_of_contests_assigned_R - number_of_contests_assigned_D
```

Assigning one contested seat to the opposite party changes both party totals appropriately. The model labels 51 seats as an outright majority and separately describes a 50–50 tie. It is **not** a probabilistic prediction.

## Technology

| Part | Implementation |
| --- | --- |
| App interface, buttons and state | Python + Streamlit |
| Election and scenario data | pandas |
| Senate seating, polling bars and state map | Plotly |
| Layout refinements | CSS/HTML embedded in Streamlit |
| Source control | GitHub |
| Public hosting | Streamlit Community Cloud |

### Run locally (optional)

Python 3.10+ is recommended. In a terminal in this repository:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

No API key is required. Candidate photos may depend on internet access to external image hosts; placeholders are shown if they cannot be retrieved. The hosted version can be used without installing Python locally.

## Data, methodology and limitations

- **Election roster and baseline:** The 2026 race roster is stored in `RACES` within `app.py`. The baseline assumes all 35 contested seats stay with their current holding parties until a visitor changes a selection.
- **Race ratings:** October 6, 2026 snapshot from the [Cook Political Report](https://www.cookpolitical.com/ratings/senate-race-ratings). Labels can change and should not be mistaken for results.
- **Polling:** Values are manually entered in the `POLLING` dictionary, with dates and source links on the dashboard. They **do not update automatically** and must be checked against the original poll pages before being described as current or verified.
- **Candidate portraits:** Retrieved from Wikipedia/Wikimedia where available. Attribution shown in the app is only a starting point; verify the specific image's creator/license and reuse permissions before publishing screenshots or repurposing images.
- **Map:** Colors represent the selected outcome for the contested Senate seat **only**, not both senators from that state and not presidential preferences. States without 2026 Senate races remain neutral. The state map displays outcomes; races are changed through the controls.
- **Simplifications:** The scenario model supports Republican, Democratic-caucus and uncalled assignments. It does not fully model independents (particularly Nebraska), ranked-choice election rules, third-party candidates, uncertainty, poll aggregation methodology, or probabilities.

For an annotated guide to the code, including the shared `st.session_state.winners` data flow and examples, read **[CODE_WALKTHROUGH.md](CODE_WALKTHROUGH.md)**.

## Portfolio and project history

- **Live demo:** https://senate-2026-midelection-simulator.streamlit.app
- **Source code:** https://github.com/sakib18030/senate-2026-simulator
- **Release snapshots:** Open the repository's **Releases** page to save a stable tagged version, e.g. `v1.0.0`.
- **Screenshots and short demo video:** Recommended for a portfolio and CV, alongside the live link and GitHub source.

This project was developed iteratively with AI-assisted coding and debugging support. The repository owner can use the code walkthrough to review and explain the implementation. Data verification and testing are ongoing.
