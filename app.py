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

st.subheader('🎛️ Flip the races')
st.caption('Select 🔵 D, 🔴 R, or ⚪ uncalled for each state. Every selection recalculates the Senate above.')

race_df=RACES.copy()
if show_filter=='Seven toss-ups': race_df=race_df[race_df.rating=='Toss-up']
elif show_filter=='Other competitive races': race_df=race_df[race_df.rating.str.contains('Lean|Likely')]
elif show_filter=='Safe / solid races': race_df=race_df[race_df.rating.str.startswith('Solid')]
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
