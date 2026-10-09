import io
import math
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Senate 2026 | Polling & Scenarios", page_icon="🗳️", layout="wide")
RED, BLUE, GRAY, GOLD, BG = '#EF626C', '#4D93F6', '#8592A7', '#FFC76B', '#0B1020'
FIXED_R, FIXED_D = 31, 34
# Current holders and dated ratings are context, never replacements for a measured poll.
RACES = [
 ('AL','Alabama','R','Solid R'),('AK','Alaska','R','Toss-up'),('AR','Arkansas','R','Solid R'),
 ('CO','Colorado','D','Solid D'),('DE','Delaware','D','Solid D'),('FL','Florida · special','R','Solid R'),
 ('GA','Georgia','D','Likely D'),('ID','Idaho','R','Solid R'),('IL','Illinois','D','Solid D'),
 ('IA','Iowa','R','Toss-up'),('KS','Kansas','R','Toss-up'),('KY','Kentucky','R','Solid R'),
 ('LA','Louisiana','R','Solid R'),('ME','Maine','R','Toss-up'),('MA','Massachusetts','D','Solid D'),
 ('MI','Michigan','D','Toss-up'),('MN','Minnesota','D','Likely D'),('MS','Mississippi','R','Solid R'),
 ('MT','Montana','R','Solid R'),('NE','Nebraska','R','Likely R'),('NH','New Hampshire','D','Lean D'),
 ('NJ','New Jersey','D','Solid D'),('NM','New Mexico','D','Solid D'),('NC','North Carolina','R','Likely D'),
 ('OH','Ohio · special','R','Toss-up'),('OK','Oklahoma','R','Solid R'),('OR','Oregon','D','Solid D'),
 ('RI','Rhode Island','D','Solid D'),('SC','South Carolina','R','Likely R'),('SD','South Dakota','R','Solid R'),
 ('TN','Tennessee','R','Solid R'),('TX','Texas','R','Toss-up'),('VA','Virginia','D','Solid D'),
 ('WV','West Virginia','R','Solid R'),('WY','Wyoming','R','Solid R')]
races=pd.DataFrame(RACES,columns=['abbr','state','holder','rating'])
assert len(races)==35 and (races.holder=='R').sum()==22 and (races.holder=='D').sum()==13
ROOT=Path(__file__).parent
# This URL points to YOUR OWN editable GitHub CSV. Streamlit refreshes it every hour.
REMOTE='https://raw.githubusercontent.com/sakib18030/senate-2026-simulator/main/polls.csv'
@st.cache_data(ttl=3600,show_spinner=False)
def load_polls():
    try:
        import urllib.request
        with urllib.request.urlopen(REMOTE,timeout=5) as reply:
            raw=reply.read()
        df=pd.read_csv(io.BytesIO(raw))
        location='GitHub polls.csv (hourly check)'
    except Exception:
        df=pd.read_csv(ROOT/'polls.csv')
        location='Bundled polls.csv (fallback)'
    required={'state','dem_candidate','rep_candidate','dem_pct','rep_pct','pollster','reported_date','source_url'}
    if not required.issubset(df.columns):
        st.error('Polling CSV is missing required columns. Using bundled snapshot.')
        df=pd.read_csv(ROOT/'polls.csv'); location='Bundled polls.csv'
    df=df[df.state.isin(races.abbr)].drop_duplicates('state',keep='first').copy()
    for col in ('dem_pct','rep_pct'):
        df[col]=pd.to_numeric(df[col],errors='coerce')
        df.loc[~df[col].between(0,100),col]=float('nan')
    return df.set_index('state'),location
polls, origin=load_polls()

def poll_state(abbr):
    if abbr not in polls.index: return None
    p=polls.loc[abbr]
    if pd.isna(p.dem_pct) or pd.isna(p.rep_pct): return None
    if p.dem_pct==p.rep_pct: return None
    return 'D' if p.dem_pct>p.rep_pct else 'R'

def defaults(): return {r.abbr:poll_state(r.abbr) for r in races.itertuples()}
if 'overrides' not in st.session_state: st.session_state.overrides={}
if 'selected_state' not in st.session_state: st.session_state.selected_state='ME'
if 'rev' not in st.session_state: st.session_state.rev=0
if 'last_map_index' not in st.session_state: st.session_state.last_map_index=None

def winners():
    w=defaults()
    w.update(st.session_state.overrides)
    return w

def color(p): return {'R':RED,'D':BLUE,None:GRAY}[p]

st.markdown('''<style>
.stApp{background:#0b1020;color:#eaf0fe}
[data-testid="stMetric"]{background:#152139;border:1px solid #2a3955;padding:15px;border-radius:14px}
[data-testid="stMetricLabel"]{color:#a9b8d0}
.stButton button{border-radius:10px}h1,h2,h3{letter-spacing:-.035em}
.block-container{padding-top:1.5rem}
</style>''',unsafe_allow_html=True)

with st.sidebar:
    st.markdown('### ⚙️ Scenario lab')
    if st.button('↺ Reset all to polling snapshot',use_container_width=True):
        st.session_state.overrides={};st.session_state.rev+=1;st.rerun()
    if st.button('Clear all contested seat assignments',use_container_width=True):
        st.session_state.overrides={x:None for x in races.abbr};st.session_state.rev+=1;st.rerun()
    st.caption('**Baseline:** 31 fixed R + 34 fixed Democratic-caucus seats. 35 contests are editable.')
    st.info('Polling is a measurement, not a declared result or a validated probability forecast. Unpolled and tied races remain unassigned.')
    st.markdown('**Data status**')
    st.caption(origin)
    st.caption(f'{len(polls)}/35 races have poll rows. Latest refresh checks GitHub approximately hourly; updating polls.csv is required when new polls are published.')
    if st.button('Check data source now',use_container_width=True):
        load_polls.clear();st.rerun()
    st.markdown('[Polling source: RealClearPolling](https://www.realclearpolling.com/latest-polls/senate)')
    st.markdown('[Race ratings: Cook Political Report](https://www.cookpolitical.com/ratings/senate-race-ratings)')
    st.caption('The bundled snapshot was transcribed on Oct. 9, 2026. Race ratings are an Oct. 6 snapshot. Source availability and republication rights should be checked before using automated feeds.')

st.title('🗳️ Senate 2026 · The Race for Control')
st.caption('November 3, 2026 · Polling snapshot + your own what-if scenarios · Educational visualization')
w=winners(); R=FIXED_R+sum(x=='R' for x in w.values());D=FIXED_D+sum(x=='D' for x in w.values());U=100-R-D
x,y,z,t=st.columns(4)
x.metric('🔴 Republican assigned',R);y.metric('🔵 Democratic caucus assigned',D)
z.metric('⚪ Unassigned races',U);t.metric('🏛️ Chamber', 'R guaranteed' if R>=51 else 'D guaranteed' if D>=51 else 'Not determined')
st.progress(R/100,text=f'Assigned totals: {R} R / {D} D / {U} unassigned • 51 needed for an outright majority')
if R>=51: st.info('The selected assignments give Republicans at least 51 seats.')
elif D>=51: st.info('The selected assignments give the Democratic caucus at least 51 seats.')
else: st.info(f'No majority assigned yet. Possible final ranges: Republican {R}–{R+U}; Democratic caucus {D}–{D+U}. The 50–50 tie-break depends on the vice president.')

left,right=st.columns([1.05,1.15],gap='large')
with left:
    st.subheader('100-seat Senate chamber')
    all_seats=[('R','Fixed R')]*FIXED_R+[('D','Fixed Democratic caucus')]*FIXED_D+[(w[r.abbr],r.state) for r in races.itertuples()]
    pts=[];i=0
    for ring,n in enumerate([36,33,31]):
        radius=1+ring*.26
        for j in range(n):
            theta=math.pi-(j+.5)*math.pi/n
            party,label=all_seats[i]
            pts.append((radius*math.cos(theta),radius*math.sin(theta),color(party),f'{label} · {party or "Unassigned"}', '#f5f7ff' if i>=65 else '#263851'))
            i+=1
    seatfig=go.Figure(go.Scatter(x=[q[0] for q in pts],y=[q[1] for q in pts],mode='markers',
                  marker={'color':[q[2] for q in pts],'size':15,'line':{'width':1,'color':'#576783'}},
                  text=[q[3] for q in pts],hovertemplate='%{text}<extra></extra>'))
    seatfig.update_layout(height=330,paper_bgcolor=BG,plot_bgcolor=BG,margin=dict(l=0,r=0,t=0,b=0),showlegend=False,
                          xaxis=dict(visible=False,range=[-1.5,1.5],scaleanchor='y'),yaxis=dict(visible=False,range=[-.1,1.52]))
    st.plotly_chart(seatfig,use_container_width=True,key='seats_plot')
    st.caption('First 65 seats are fixed. The remaining 35 reflect poll-leader assignments or manual overrides; gray = unassigned.')
with right:
    st.subheader('Map · select a contested state')
    md=races.copy();md['selected']=md.abbr.map(w);md['value']=md.selected.map({'D':0,'R':1}).fillna(.5)
    md['details']=md.apply(lambda r:f'{r.state}<br>Poll-based assignment: {poll_state(r.abbr) or "None"}<br>Scenario: {r.selected or "Unassigned"}<br>{r.rating}',axis=1)
    mapfig=go.Figure(go.Choropleth(locations=md.abbr,locationmode='USA-states',z=md.value,
             zmin=0,zmax=1,colorscale=[[0,BLUE],[.499,BLUE],[.5,GRAY],[.501,RED],[1,RED]],
             marker_line_color='#0b1020',marker_line_width=1.2,showscale=False,text=md.details,hovertemplate='%{text}<extra></extra>'))
    # Scattergeo overlays create point-selection targets on the state map.
    centers={'AL':(-86.8,32.6),'AK':(-151.5,64.5),'AR':(-92.4,34.9),'CO':(-105.5,39.1),
    'DE':(-75.45,39),'FL':(-82.2,28.1),'GA':(-83.4,32.5),'ID':(-114.4,44.3),'IL':(-89,40),
    'IA':(-93.5,42.1),'KS':(-98.3,38.5),'KY':(-84.8,37.8),'LA':(-91.9,31),'ME':(-69.2,45.3),
    'MA':(-71.9,42.3),'MI':(-85.5,44.3),'MN':(-94.5,46.3),'MS':(-89.7,32.8),
    'MT':(-110.5,47),'NE':(-99.7,41.5),'NH':(-71.6,43.8),'NJ':(-74.6,40.1),'NM':(-106,34.4),
    'NC':(-79.8,35.6),'OH':(-82.8,40.3),'OK':(-97.3,35.6),'OR':(-120,44),'RI':(-71.5,41.6),
    'SC':(-80.8,33.8),'SD':(-100.2,44.5),'TN':(-86,35.8),'TX':(-99,31),'VA':(-78.5,37.5),
    'WV':(-80.6,38.6),'WY':(-107.5,43)}
    order=list(md.abbr)
    mapfig.add_trace(go.Scattergeo(lon=[centers[s][0] for s in order],lat=[centers[s][1] for s in order],
          customdata=order,mode='markers',marker=dict(size=13,color='rgba(255,255,255,.12)',line=dict(color='#f2f3f5',width=.9)),
          text=order,hovertemplate='Select %{text} to edit<extra></extra>',showlegend=False))
    mapfig.update_layout(geo=dict(scope='usa',bgcolor=BG,showland=True,landcolor='#30394c',showlakes=False),
                         paper_bgcolor=BG,margin=dict(l=0,r=0,t=0,b=0),height=330,dragmode=False)
    event=st.plotly_chart(mapfig,use_container_width=True,key='interactive_map',on_select='rerun',selection_mode='points')
    selected_points=event.selection.points if event else []
    for point in selected_points:
        # scattergeo is second trace, point_index matches our state list
        if point.get('curve_number')==1 and point.get('point_index') is not None:
            abbr=order[point['point_index']]
            st.session_state.selected_state=abbr
            break
    st.caption('Select a state marker to open its race details below. Only contested states are colored; gray means unassigned.')

st.divider()
a,b=st.columns([1,1.25],gap='large')
with a:
    st.subheader('🔎 Race explorer')
    opt=list(races.abbr)
    current=st.session_state.selected_state
    state=st.selectbox('Choose one of the 35 contested seats',opt,index=opt.index(current) if current in opt else 0,
                       format_func=lambda abbr: f'{races.set_index("abbr").loc[abbr,"state"]} ({abbr})')
    st.session_state.selected_state=state
    race=races.set_index('abbr').loc[state]
    st.caption(f'Current holder: {race.holder} · Rating: {race.rating} (dated Oct. 6)')
    if state in polls.index:
        p=polls.loc[state]
        st.markdown(f'**{p.pollster}** · reported {p.reported_date}')
        c1,c2=st.columns(2)
        for col, name,score,shade,imgcol in [(c1,p.dem_candidate,p.dem_pct,BLUE,'image_dem'),(c2,p.rep_candidate,p.rep_pct,RED,'image_rep')]:
            with col:
                img=p.get(imgcol,'')
                if pd.notna(img) and str(img).startswith('https://'): st.image(img,width=110)
                else: st.markdown('#### 👤')
                st.markdown(f'**{name}**');st.markdown(f'<span style="color:{shade};font-size:23px">{score:g}%</span>',unsafe_allow_html=True)
        st.progress(min(1,float(p.dem_pct)/100),text=f'D {p.dem_pct:g}%')
        st.progress(min(1,float(p.rep_pct)/100),text=f'R {p.rep_pct:g}%')
        st.markdown(f'[Original poll listing]({p.source_url})')
        st.caption('Single latest listed survey in the dataset, **not** a polling average. Other / undecided voters are not shown as a candidate.')
    else: st.warning('No verified polling entry loaded for this race. Its baseline assignment is uncalled.')
with b:
    st.subheader('🎛️ What-if controls')
    baseline=poll_state(state); current=w[state]
    st.caption(f'Poll snapshot assigns: {baseline or "Unassigned (missing data or tie)"}. Your choice does not alter the underlying poll numbers.')
    options=['Poll snapshot','Democratic win','Republican win','Unassigned']
    existing=st.session_state.overrides.get(state,'BASE')
    idx={'BASE':0,'D':1,'R':2,None:3}[existing]
    choice=st.radio('Assign the outcome for this state',options,index=idx,horizontal=False,key=f'assign_{state}_{st.session_state.rev}')
    new={'Poll snapshot':'BASE','Democratic win':'D','Republican win':'R','Unassigned':None}[choice]
    if new!=existing:
        if new=='BASE':st.session_state.overrides.pop(state,None)
        else:st.session_state.overrides[state]=new
        st.rerun()
    st.markdown('**Scenario changes**')
    if not st.session_state.overrides:st.caption('No manual overrides. Displaying the current polling snapshot.')
    else:
        for s,p in sorted(st.session_state.overrides.items()): st.caption(f'{s}: {p or "Unassigned"}')
    st.markdown('**Path to 51**')
    st.write(f'Republicans need **{max(0,51-R)}** more assigned seats for 51. Democratic caucus needs **{max(0,51-D)}** more.')
    st.caption('These are scenario arithmetic totals, not statistical estimates of winning.')

st.divider()
st.subheader('All 35 races · overview')
overview=races.copy();overview['poll_D%']=overview.abbr.map(polls.dem_pct.to_dict());overview['poll_R%']=overview.abbr.map(polls.rep_pct.to_dict())
overview['poll_reported']=overview.abbr.map(polls.reported_date.to_dict());overview['poll_based']=overview.abbr.map(defaults());overview['scenario']=overview.abbr.map(w)
overview['user_override']=overview.abbr.map(lambda q:'Yes' if q in st.session_state.overrides else 'No')
st.dataframe(overview.rename(columns={'state':'State','rating':'Rating','poll_D%':'Dem %','poll_R%':'Rep %','scenario':'Scenario assignment'}),hide_index=True,use_container_width=True)
st.download_button('📥 Download scenario CSV',overview.to_csv(index=False),file_name='senate_2026_v2_scenario.csv',mime='text/csv')
st.caption('© Scenario explorer · Poll snapshot entries transcribed Oct. 9, 2026 from RealClearPolling. Not a forecast or certified result. Nebraska may involve an independent; the simplified R/D assignment is not a comprehensive candidate model.')
