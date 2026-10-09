# Code Walkthrough: Senate 2026 · Battle for 51

**Start here if you are learning the code or reviewing this project as an interviewer.**

This is an educational Streamlit application. The file `app.py` provides both the user interface and the simulation logic. The project uses **Python, Streamlit, pandas and Plotly**; the only dependency list is in `requirements.txt`.

## 1. Project files

| File | Purpose |
| --- | --- |
| `app.py` | All election data structures, scenario calculations, visualizations and interactive UI |
| `requirements.txt` | Python dependencies: Streamlit, Plotly, pandas |
| `README.md` | User-facing project summary, setup, sources and limitations |
| `CODE_WALKTHROUGH.md` | This explanation of how the code works |

The project is deployed from the `main` branch on Streamlit Community Cloud. When a new GitHub commit is deployed, the live application reflects those changes.

## 2. Election data: `RACES` and `SWING_STATES`

At the beginning of `app.py`, `RACES` lists the **35 Senate contests** represented in the November 2026 election model. Each entry includes a two-letter state abbreviation, state name, party/caucus currently holding the seat and a dated race rating.

`RACES` becomes a pandas DataFrame. `SWING_STATES` is a separate list containing `AK`, `IA`, `KS`, `ME`, `MI`, `OH` and `TX`.

**Why two lists?** The 7-state list limits the *candidate-detail selector*, but the lower **Flip the races** section still works with all **35 races**. No contests disappear from the 100-seat calculation.

## 3. Persistent interactive state: `st.session_state.winners`

Streamlit reruns a script when an input changes. A regular local variable would be reset on each rerun. The application therefore stores every selected outcome in:

```python
st.session_state.winners
```

It is a dictionary mapping state codes to `'R'`, `'D'`, or `None` for an uncalled seat. On the first visit, it is initialized using the party currently holding each contested seat.

`set_winner(abbr, party)` updates an election outcome. `reset(mode)` either restores current holders or applies the dated ratings scenario. A `revision` counter helps the lower segmented controls synchronize after the top buttons or reset changes.

**Key design principle:** The map, chamber, counters and controls are not separate simulations. They all refer to the same `winners` dictionary.

## 4. The Senate seat math

The application uses a **fixed baseline**:

```python
FIXED_R, FIXED_D = 31, 34
```

The 34 Democratic-caucus baseline includes two independents who caucus with Democrats.

For 35 editable contests:

```python
r_win = sum(v == 'R' for v in winners.values())
d_win = sum(v == 'D' for v in winners.values())
uncalled = 35 - r_win - d_win
R = FIXED_R + r_win
D = FIXED_D + d_win
```

Example: With the default 53 R / 47 Democratic-caucus baseline, switching **Texas** from Republican to Democratic in the scenario produces **52 R / 48 Democratic-caucus**, with the same 100-seat total. The underlying 31 and 34 fixed seats do not change.

When some races are uncalled, `R + D + uncalled == 100`.

A 51-seat count is treated as an outright majority; the app labels a 50–50 tie separately. These totals are **hypothetical outcomes**, not an election prediction.

## 5. Summary cards

The top Republican and Democratic cards show:

- Fixed seats (31 or 34)
- Contested seats assigned to the caucus by the current scenario
- Total seats = fixed + assigned

The additional cards show uncalled seats and the majority-control status. Their displayed figures update whenever the shared selection state changes.

## 6. The 100-seat semicircle

Plotly's `go.Scatter` draws each seat as a colored dot.

The code constructs 100 seats: first the 65 fixed seats, then the 35 current selections. It positions dots on three semicircular rings using `math.pi`, `math.cos`, and `math.sin`. Dot colors are **red**, **blue** or **gray** (uncalled); hover labels describe each seat. Chart margins and axis ranges keep the full semicircle visible.

The dot display shows the distribution of seats in a stylized chamber diagram rather than physical assigned Senate seating.

## 7. U.S. map

Plotly `go.Choropleth` colors states with a 2026 race according to their *selected scenario outcome*: blue for D, red for R, gray for uncalled. The map also overlays state abbreviations, including labels for states without a 2026 Senate contest (such as AZ).

**Important:** The map describes only the Senate seat being contested, not the state's overall party alignment, both senators, or presidential preference. For clarity, the on-screen controls are used to assign winners; map clicks do not currently flip races.

## 8. The seven candidate profile panels

`CANDIDATES` stores paired candidate names for the seven highlighted races. The selected state determines which pair is shown.

`candidate_photo(name)` attempts to obtain a portrait from the candidate's relevant Wikipedia page, with a specific Wikimedia source for Adam Hamilton. It caches results using `@st.cache_data` and returns a placeholder if an image cannot be loaded. The profile layout uses compact HTML/CSS inside Streamlit.

**Photo caveat:** Image reuse rights are determined file-by-file; a Wikipedia photo is not automatically free of restrictions. Before publication outside the live app, confirm the file page's license and proper attribution.

## 9. Polling snapshot (not live)

The `POLLING` dictionary stores manually entered head-to-head polling percentages, a source name, a polling date range and a link. Plotly `go.Bar` renders the compact polling comparison.

**The polling numbers are not connected to the seat-assignment logic.** Selecting a hypothetical winner changes `winners`, not `POLLING`. This avoids representing a user-made scenario as a real change in survey support.

The current polling values require independent validation and maintenance. The dashboard is **not** a live polling feed, automated aggregator, probabilistic model, or official election-results service.

## 10. Two ways to flip a race

**Upper section:** The seven featured states have buttons for Republican, Democrat or Uncalled. The button callback modifies `st.session_state.winners[selected_state]` and asks Streamlit to rerun.

**Lower section:** All 35 races have segmented controls. Sidebar filters select which races are currently displayed; they do *not* remove races from the simulation. The controls use the same `winners` data, so an upper-panel change and lower-panel change affect the same outcome.

**Scenario reset:** A sidebar button can reset all states to their current holders or use the rating-based scenario. Both reset actions update the shared state.

## 11. Exporting a scenario

Near the bottom, a copy of `RACES` becomes an export table with `scenario_winner` and `seat_flipped` columns. `st.download_button` offers it as a CSV. This lets a reviewer recreate or analyze the selected hypothetical outcomes.

## 12. Test these behaviors

1. At default settings, the total is **53 Republican + 47 Democratic-caucus = 100**.
2. Change one Republican-held race to Democratic: the Republican total decreases by one and the Democratic-caucus total increases by one.
3. Mark a race Uncalled: assigned seats decline by one while the uncalled count increases by one.
4. Confirm **31 R and 34 Democratic-caucus fixed seats never change**.
5. Change a highlighted state's outcome using the upper controls and verify the lower control shows the same selection.
6. Use **All 35 races** in the sidebar to confirm all states remain editable.
7. Export CSV and check the selected party codes.
8. Verify candidate photo identities, polling source links and fieldwork dates before showcasing the project.

## 13. What the code demonstrates professionally

The project illustrates **interactive UI programming**, **state management**, **data modeling with pandas**, **custom visualizations with Plotly**, **debugging**, **GitHub version control**, and **cloud deployment**. It can be extended to include better validation, unit tests, a structured data file, polling-history charts or a properly licensed automated polling data feed.

For interviews, a good explanation is: *"I separated the 65 fixed Senate seats from the 35 scenario-controlled seats. Every user action changes one shared Python dictionary. I recompute the national totals and redraw the state map and Senate semicircle from that state. I show dated poll snapshots for context, but I keep them separate from hypothetical seat outcomes."*

The app was developed iteratively with AI coding assistance. Reviewing this walkthrough and demonstrating how to change a race is a practical way to understand, maintain, and describe the project.
