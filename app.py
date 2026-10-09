import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title='Senate 2026 | Battle for 51', page_icon='🗳️', layout='wide')

RED, BLUE, GRAY, GOLD = '#ef5b63', '#478cf4', '#8c97aa', '#ffcb66'
BG = '#0b1020'
FIXED_R, FIXED_D = 31, 34  # fixed Democratic caucus includes 2 independents

# Incumbent party reflects which caucus currently holds the seat, not the 2026 winner.
# Ratings are snapshots, not election results. Source link displayed in the sidebar.
RACES = [
 ('AL','Alabama','R','Solid R'),('AK','Alaska','R','Toss-up'),
 ('AR','Arkansas','R','Solid R'),('CO','Colorado','D','Solid D'),
 ('DE','Delaware','D','Solid D'),('FL','Florida · special','R','Solid R'),
 ('GA','Georgia','D','Likely D'),('ID','Idaho','R','Solid R'),
 ('IL','Illinois','D','Solid D'),('IA','Iowa','R','Toss-up'),
 ('KS','Kansas','R','Toss-up'),('KY','Kentucky','R','Solid R'),
 ('LA','Louisiana','R','Solid R'),('ME','Maine','R','Toss-up'),
 ('MA','Massachusetts','D','Solid D'),('MI','Michigan','D','Toss-up'),
 ('MN','Minnesota','D','Likely D'),('MS','Mississippi','R','Solid R'),
 ('MT','Montana','R','Solid R'),('NE','Nebraska','R','Likely R'),
 ('NH','New Hampshire','D','Lean D'),('NJ','New Jersey','D','Solid D'),
 ('NM','New Mexico','D','Solid D'),('NC','North Carolina','R','Likely D'),
 ('OH','Ohio · special','R','Toss-up'),('OK','Oklahoma','R','Solid R'),
 ('OR','Oregon','D','Solid D'),('RI','Rhode Island','D','Solid D'),
 ('SC','South Carolina','R','Likely R'),('SD','South Dakota','R','Solid R'),
 ('TN','Tennessee','R','Solid R'),('TX','Texas','R','Toss-up'),
 ('VA','Virginia','D','Solid D'),('WV','West Virginia','R','Solid R'),
 ('WY','Wyoming','R','Solid R'),
]
RACES = pd.DataFrame(RACES, columns=['abbr','state','holder','rating'])
SWING_STATES = ["AK", "IA", "KS", "ME", "MI", "OH", "TX"]
assert len(RACES) == 35 and (RACES.holder=='R').sum() == 22 and (RACES.holder=='D').sum() == 13
assert (RACES.rating == 'Toss-up').sum() == 7

if 'winners' not in st.session_state:
    st.session_state.winners = {r.abbr: r.holder for r in RACES.itertuples()}
if 'revision' not in st.session_state:
    st.session_state.revision = 0

def set_winner(abbr, party):
    st.session_state.winners[abbr] = party

def reset(mode):
    st.session_state.winners = {
        r.abbr: (r.holder if mode=='Current holders' else ('D' if r.rating.endswith('D') else 'R' if r.rating.endswith('R') else None))
        for r in RACES.itertuples()
    }
    st.session_state.revision += 1

st.markdown('''<style>
.stApp {background: #0b1020; color: #edf2ff}
[data-testid="stMetric"] {background:#141e34;border:1px solid #263651;padding:14px;border-radius:14px}
[data-testid="stMetricLabel"] {color:#a9b8d0}
h1,h2,h3 {letter-spacing:-.035em}
.block-container {padding-top:1.4rem}
.stButton button {border-radius:10px}
</style>''', unsafe_allow_html=True)

with st.sidebar:
    st.header('⚙️ Scenario controls')
    if st.button('↺ Reset to current seat holders', use_container_width=True): reset('Current holders')
    if st.button('↗ Apply rating-based scenario', use_container_width=True): reset('Ratings')
    st.caption('Rating scenario assigns favored races and leaves toss-ups uncalled. Ratings reflect an October 6, 2026 snapshot, not actual results.')
    st.divider()
    show_filter = st.selectbox('Race list', ['All 35 races','Seven toss-ups','Other competitive races','Safe / solid races'])
    st.caption('Fixed baseline: 31 R + 34 Democratic-caucus seats (including 2 independents). The 35 contests are editable.')
    st.markdown('**Sources**')
    st.markdown('[2026 election guide (Oct. 7)](https://www.uspresidentialelectionnews.com/2026-senate-elections/)')
    st.markdown('[Cook Political Report ratings](https://www.cookpolitical.com/ratings/senate-race-ratings)')
    st.caption('Educational scenario builder, not a forecast or live election result. Nebraska has a prominent independent candidate; this simplified model uses only R/D/uncalled, so interpret that race cautiously.')

st.title('🗳️ Senate 2026 · Battle for 51')
st.caption('November 3, 2026 election · Change any of the 35 contests and watch the 100-seat chamber respond.')

winners = st.session_state.winners
r_win = sum(v=='R' for v in winners.values())
d_win = sum(v=='D' for v in winners.values())
uncalled = 35-r_win-d_win
R = FIXED_R+r_win
D = FIXED_D+d_win

a,b,c,d = st.columns(4)
a.metric('🔴 Republican seats', R, delta=f'{R-53:+d} vs current', delta_color='off')
b.metric('🔵 Democratic caucus', D, delta=f'{D-47:+d} vs current', delta_color='off')
c.metric('⚪ Uncalled seats', uncalled)
d.metric('🏛️ Senate control', 'Republicans' if R>=51 else 'Democrats' if D>=51 else 'Republicans (VP tie)' if R==50 and D==50 else 'Not yet decided')

if R>=51: st.info(f'Republicans have at least 51 seats in this scenario. Democrats could finish with at most {D+uncalled}.')
elif D>=51: st.info(f'Democrats have at least 51 seats in this scenario. Republicans could finish with at most {R+uncalled}.')
elif R==50 and D==50: st.info('50–50 tie: Republican Vice President JD Vance would break organizational ties under the current administration.')
else: st.info(f'No outright majority assigned yet. Possible Republican total: {R}–{R+uncalled}; Democratic-caucus total: {D}–{D+uncalled}.')

left, right = st.columns([1.18,1], gap='large')
with left:
    st.subheader('100 Senate seats')
    # Semi-circle seating visualization. Fixed = 65, contested = 35.
    xs, ys, colors, labels, outlines = [],[],[],[],[]
    all_seats = [('R','Fixed Republican')]*FIXED_R + [('D','Fixed Democratic caucus')]*FIXED_D
    all_seats += [(winners[row.abbr], row.state + ' · 2026 election') for row in RACES.itertuples()]
    index=0
    for ring, count in [(0,36),(1,33),(2,31)]:
        radius=1.0 + ring*0.26
        for i in range(count):
            theta=math.pi - (i+.5)*math.pi/count
            party, label = all_seats[index]
            xs.append(radius*math.cos(theta));ys.append(radius*math.sin(theta))
            colors.append(RED if party=='R' else BLUE if party=='D' else GRAY)
            labels.append(label + ' · '+ ('Republican' if party=='R' else 'Democratic caucus' if party=='D' else 'Uncalled'))
            outlines.append('#263651' if index <65 else '#e0e8ff')
            index+=1
    fig=go.Figure(go.Scatter(x=xs,y=ys,mode='markers',marker=dict(size=16,color=colors,line=dict(width=1,color='#63728c')),text=labels,hovertemplate='%{text}<extra></extra>'))
    fig.update_layout(height=315,margin=dict(l=5,r=5,t=5,b=5),paper_bgcolor=BG,plot_bgcolor=BG,showlegend=False,xaxis=dict(visible=False,range=[-1.55,1.55],scaleanchor='y'),yaxis=dict(visible=False,range=[-.12,1.48]))
    st.plotly_chart(fig, use_container_width=True)
    st.caption('100 dots = 100 seats. First 65 are locked; 35 reflect your selections. Blue includes independents caucusing with Democrats.')
with right:
    st.subheader('U.S. map · contested races')
    # 2026 elections are one seat per state; the other senator is represented by the fixed baseline.
    map_data=RACES.copy()
    map_data['winner']=map_data.abbr.map(winners)
    map_data['z']=map_data.winner.map({'D':0,'R':1}).fillna(.5)
    map_data['hover']=map_data.apply(lambda row: f"{row['state']}<br>Held by: {row['holder']} · Rating: {row['rating']}<br>Selected: {row['winner'] or 'Uncalled'}",axis=1)
    map_fig=go.Figure(go.Choropleth(locations=map_data.abbr,locationmode='USA-states',z=map_data.z,zmin=0,zmax=1,colorscale=[[0,BLUE],[.499,BLUE],[.5,GRAY],[.501,RED],[1,RED]],showscale=False,text=map_data['hover'],hovertemplate='%{text}<extra></extra>',marker_line_color='#10182b',marker_line_width=1.1))
    map_fig.update_layout(geo=dict(scope='usa',bgcolor=BG,showlakes=False,showland=True,landcolor='#30394c'),paper_bgcolor=BG,margin=dict(l=0,r=0,t=0,b=0),height=315)
    st.plotly_chart(map_fig,use_container_width=True)
    st.caption('Colored states show the *contested Senate seat only*, not both senators or presidential preference. Gray indicates uncalled. Click the state controls below to change colors.')

# STATE ELECTION DETAILS
st.subheader("🗳️ State Election Details")
st.caption("Explore a 2026 Senate race and test its outcome.")

state_names = {
    row.abbr: row.state
    for row in RACES.itertuples()
}


selected_state = st.selectbox(
    "Choose a state",
    options=SWING_STATES,
    format_func=lambda abbr: state_names[abbr],
    index=SWING_STATES.index("ME"),
)


race = RACES.set_index("abbr").loc[selected_state]
current_choice = st.session_state.winners[selected_state]

st.markdown(f"### {race['state']}")

# Candidate profiles — 2026 highlighted Senate races
CANDIDATES = {
    "AK": {"R": "Dan Sullivan", "D": "Mary Peltola"},
    "IA": {"R": "Ashley Hinson", "D": "Josh Turek"},
    "KS": {"R": "Roger Marshall", "D": "Adam Hamilton"},
    "ME": {"R": "Susan Collins", "D": "Troy Jackson"},
    "MI": {"R": "Mike Rogers", "D": "Abdul El-Sayed"},
    "OH": {"R": "Jon Husted", "D": "Sherrod Brown"},
    "TX": {"R": "Ken Paxton", "D": "James Talarico"},
}

@st.cache_data(ttl=86400, show_spinner=False)
def candidate_photo(name):
    """Try to fetch a Wikipedia portrait, if available."""
 
 
    # Verified Wikimedia Commons image for Adam Hamilton
    if name == "Adam Hamilton":
        return (
            "https://commons.wikimedia.org/wiki/Special:FilePath/"
            "Adam_Hamilton_on_the_Courage_to_Preach_%28cropped_2%29.png"
        )

    import json
    import urllib.parse
    import urllib.request

    params = urllib.parse.urlencode({
        "action": "query",
        "format": "json",
        "prop": "pageimages",
        "piprop": "thumbnail",
        "pithumbsize": 350,
        "redirects": 1,
        "titles": name,
    })

    url = "https://en.wikipedia.org/w/api.php?" + params

    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "SenateSimulatorPortfolio/1.0"}
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            data = json.load(response)

        for page in data["query"]["pages"].values():
            if page.get("title", "").lower() == name.lower():
                return page.get("thumbnail", {}).get("source")
    except Exception:
        pass

    return None


if selected_state in CANDIDATES:
    candidates = CANDIDATES[selected_state]

 
    st.markdown("#### Meet the Candidates")

    col1, col2 = st.columns(2, gap="small")

    for column, party, color in [
        (col1, "R", "#ef5b63"),
        (col2, "D", "#478cf4"),
    ]:
        with column:
            name = candidates[party]

            st.markdown(
                f"<h4 style='color:{color}; margin-bottom:8px;'>"
                f"{'🔴 Republican' if party == 'R' else '🔵 Democrat'}"
                "</h4>",
                unsafe_allow_html=True,
            )

            photo = candidate_photo(name)

            
if name == "Adam Hamilton":
    st.caption(
        "Photo: Western Pennsylvania Conference – UMC "
        "via Wikimedia Commons · CC BY 4.0"
    )
    st.markdown(
        "[Image source and license]"
        "(https://commons.wikimedia.org/wiki/"
        "File:Adam_Hamilton_on_the_Courage_to_Preach_"
        "(cropped_2).png)"
    )
else:
    st.caption("Image: Wikipedia / Wikimedia")

            st.markdown(f"### {name}")


else:
    st.info(
        "Candidate profiles for this state "
        "will be added in a future update."
    )





# Published polling snapshot
# Percentages are measurements, not election results.
POLLING = {
    "ME": {
        "R": 47.3,
        "D": 48.3,
        "source": "RealClearPolling average",
        "dates": "September 14 – October 5, 2026",
        "url": "https://www.realclearpolling.com/polls/senate/general/2026/collins-vs-jackson",
    },
 
    "AK": {
        "R": 47.3,
        "D": 48.5,
        "source": "RealClearPolling head-to-head average",
        "dates": "September 14 – October 3, 2026",
        "url": "https://www.realclearpolling.com/polls/senate/general/2026/alaska/peltola-vs-sullivan",
    },
 
    "IA": {
        "R": 45.3,
        "D": 45.8,
        "source": "RealClearPolling average",
        "dates": "September 9 – October 6, 2026",
        "url": "https://www.realclearpolling.com/elections/senate/2026/iowa",
    },

    "KS": {
        "R": 45.6,
        "D": 45.4,
        "source": "RealClearPolling average",
        "dates": "September 8 – October 4, 2026",
        "url": "https://www.realclearpolling.com/polls/senate/general/2026/kansas/marshall-vs-hamilton",
    },

    "MI": {
        "R": 44.9,
        "D": 48.1,
        "source": "RealClearPolling average",
        "dates": "September 15 – October 6, 2026",
        "url": "https://www.realclearpolling.com/polls/senate/general/2026/michigan/rogers-vs-el-sayed",
    },

    "OH": {
        "R": 44.2,
        "D": 47.3,
        "source": "RealClearPolling average",
        "dates": "September 1 – October 6, 2026",
        "url": "https://www.realclearpolling.com/polls/senate/special-election/2026/ohio/husted-vs-brown",
    },

    "TX": {
        "R": 45.3,
        "D": 48.1,
        "source": "RealClearPolling average",
        "dates": "September 12 – October 5, 2026",
        "url": "https://www.realclearpolling.com/elections/senate/2026/texas",
    },


}

st.markdown("#### 📊 Current Polling")

poll = POLLING.get(selected_state)


if poll:
    republican_pct = poll["R"]
    democrat_pct = poll["D"]
    other_pct = max(
        0, 100 - republican_pct - democrat_pct
    )

    # Candidate names from the existing profiles
    names = CANDIDATES.get(
        selected_state,
        {"R": "Republican", "D": "Democrat"}
    )

    st.markdown("##### Polling Snapshot")

    # Compact polling metrics
    left_poll, right_poll = st.columns(2, gap="small")

    with left_poll:
        st.metric(
            f"🔴 {names['R']} (R)",
            f"{republican_pct:.1f}%"
        )

    with right_poll:
        st.metric(
            f"🔵 {names['D']} (D)",
            f"{democrat_pct:.1f}%"
        )

    # Compact red-blue comparison bar
    polling_fig = go.Figure()

    for label, value, color in [
        ("Republican", republican_pct, "#ef5b63"),
        ("Democrat", democrat_pct, "#478cf4"),
        ("Other / undecided", other_pct, "#8c97aa"),
    ]:
        polling_fig.add_trace(
            go.Bar(
                y=["Polling"],
                x=[value],
                name=label,
                orientation="h",
                marker_color=color,
                hovertemplate=(
                    f"{label}: {value:.1f}%<extra></extra>"
                ),
                showlegend=False,
            )
        )

    polling_fig.update_layout(
        barmode="stack",
        height=85,
        margin=dict(l=0, r=0, t=5, b=5),
        paper_bgcolor="#0b1020",
        plot_bgcolor="#0b1020",
        xaxis=dict(
            range=[0, 100],
            visible=False,
            fixedrange=True,
        ),
        yaxis=dict(
            visible=False,
            fixedrange=True,
        ),
        bargap=0.55,
    )

    st.plotly_chart(
        polling_fig,
        use_container_width=True,
        config={"displayModeBar": False},
    )

    st.caption(
        "🔴 Republican   |   🔵 Democrat   |   "
        "⚪ Other / undecided"
    )

    # Source and polling dates
    st.caption(
        f"📅 {poll['dates']}  |  "
        f"📊 {poll['source']}"
    )

    st.markdown(
        f"🔗 [View polling source]({poll['url']})"
    )


else:
    st.info(
        "No verified polling snapshot loaded "
        "for this state yet."
    )

st.caption(
    "Polling is separate from your hypothetical "
    "Senate election scenario."
)

st.write(f"**Race rating:** {race['rating']}")
st.write(
    "**Current scenario:** "
    + {"R": "Republican", "D": "Democratic", None: "Uncalled"}[current_choice]
)

left, middle, right = st.columns(3)

def update_selected_race(party):
    st.session_state.winners[selected_state] = party
    st.session_state.revision += 1

with left:
    if st.button("🔴 Republican wins", use_container_width=True):
        update_selected_race("R")
        st.rerun()

with middle:
    if st.button("🔵 Democrat wins", use_container_width=True):
        update_selected_race("D")
        st.rerun()

with right:
    if st.button("⚪ Uncalled", use_container_width=True):
        update_selected_race(None)
        st.rerun()

st.divider()

st.subheader('🎛️ Flip the races')
st.caption('Select 🔵 D, 🔴 R, or ⚪ uncalled for each state. Every selection recalculates the Senate above.')


race_df = RACES.copy()

if show_filter == 'Seven toss-ups':
    race_df = race_df[race_df.rating == 'Toss-up']
elif show_filter == 'Other competitive races':
    race_df = race_df[
        race_df.rating.str.contains('Lean|Likely')
    ]
elif show_filter == 'Safe / solid races':
    race_df = race_df[
        race_df.rating.str.startswith('Solid')
    ]

# Place closest races first, followed by lean/likely/solid.
priority={'Toss-up':0,'Lean D':1,'Lean R':1,'Likely D':2,'Likely R':2,'Solid D':3,'Solid R':3}
race_df=race_df.assign(priority=race_df.rating.map(priority)).sort_values(['priority','state'])

for row in race_df.itertuples():
    l, m, r=st.columns([3.5,2,1.5],vertical_alignment='center')
    with l:
        st.markdown(f"**{row.state}** &nbsp; ` {row.rating} `")
        st.caption(f'Currently held: {"Republican" if row.holder=="R" else "Democratic"}')
    with m:
        selected=st.segmented_control(f'{row.abbr} winner',options=['D','R','Uncalled'],default='Uncalled' if winners[row.abbr] is None else winners[row.abbr],format_func=lambda p: {'D':'🔵 D','R':'🔴 R','Uncalled':'⚪ ?'}[p],key=f'choice_{row.abbr}_{st.session_state.revision}',label_visibility='collapsed')
        new=None if selected=='Uncalled' else selected
        if selected is not None and new!=winners[row.abbr]:
            set_winner(row.abbr,new)
            st.rerun()
    with r:
        initial=row.holder
        selected_party=winners[row.abbr]
        if selected_party is None: st.caption('Not assigned')
        elif selected_party!=initial: st.markdown('**↔ FLIPPED**')
        else: st.caption('Seat retained')
    st.divider()

st.subheader('📥 Export your scenario')
export=RACES.copy()
export['scenario_winner']=export.abbr.map(winners).fillna('Uncalled')
export['seat_flipped']=export.apply(lambda x: x.scenario_winner not in ('Uncalled',x.holder),axis=1)
st.download_button('Download scenario CSV',export.to_csv(index=False),file_name='senate_2026_scenario.csv',mime='text/csv')
st.caption('This first version models the post-election party/caucus balance, not candidate-specific probabilities or formal calls. Data snapshot: Oct. 7, 2026.')
