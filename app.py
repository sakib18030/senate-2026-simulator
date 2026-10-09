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

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
.stApp{background:#0c1424;color:#f5f8ff;font-family:Inter,sans-serif}
.block-container{max-width:1440px;padding-top:1rem;padding-left:1.4rem;padding-right:1.4rem}
[data-testid="stSidebar"]{display:none}
[data-testid="stMetric"]{background:#17253c;border:1px solid #293c5a;padding:12px 16px;border-radius:12px}
[data-testid="stMetricLabel"]{color:#b5c6df;font-size:.85rem}
[data-testid="stMetricValue"]{font-family:Inter,sans-serif;font-size:2.2rem;font-weight:800}
h1,h2,h3{font-family:Inter,sans-serif;letter-spacing:-.03em;text-transform:none}
h1{font-size:2.4rem!important}h2,h3{color:#f4f7ff!important}
.stButton button{border-radius:9px;border-color:#395478;font-weight:650}
[data-testid="stPlotlyChart"]{border:1px solid #243958;background:#111e32;border-radius:14px}
div[data-testid="stCaptionContainer"]{color:#9aabc5}
.broadcast-bar{color:#a9c2e6;padding:3px 0;font-size:11px;font-weight:800;letter-spacing:.12em;display:flex;justify-content:space-between}
.broadcast-title{padding:3px 0 8px;margin-bottom:7px}
.broadcast-title h1{font-family:Inter,sans-serif;font-size:2.3rem;margin:0;line-height:1.2;color:#fff}
.broadcast-title p{color:#b6c6dd;margin:5px 0 0;font-size:12px}
.section-strip{background:transparent;border-left:3px solid #4e95f5;padding:5px 11px;font-size:15px;font-weight:750;margin:12px 0 4px}
</style>""",unsafe_allow_html=True)

# Compact controls live in a collapsed expander, not a persistent sidebar.
with st.expander('⚙️ Scenario controls · polling sources · data refresh', expanded=False):
    ctl1,ctl2,ctl3=st.columns(3)
    with ctl1:
        if st.button('↺ Reset to polling snapshot',use_container_width=True):
            st.session_state.overrides={};st.session_state.rev+=1;st.rerun()
    with ctl2:
        if st.button('Clear all 35 assignments',use_container_width=True):
            st.session_state.overrides={x:None for x in races.abbr};st.session_state.rev+=1;st.rerun()
    with ctl3:
        if st.button('↻ Refresh polling CSV',use_container_width=True):
            load_polls.clear();st.rerun()
    st.caption(f'Data: {origin} · {len(polls)} of 35 races have poll rows. A GitHub CSV refresh is not an automatic polling-site feed.')
    st.caption('Polling is not an election result or forecast. Unpolled and tied races remain unassigned.')
    st.markdown('[Polling source](https://www.realclearpolling.com/latest-polls/senate) · [Race ratings](https://www.cookpolitical.com/ratings/senate-race-ratings)')

st.markdown('<div class="broadcast-bar"><span>THE SENATE RACE • 2026</span><span>POLLS + INTERACTIVE SCENARIOS</span></div>',unsafe_allow_html=True)
st.markdown('<div class="broadcast-title"><h1>BATTLE FOR 51</h1><p>NOVEMBER 3, 2026 &nbsp; | &nbsp; 35 RACES ON THE BALLOT &nbsp; | &nbsp; POLLING SNAPSHOT IS NOT AN ELECTION RESULT</p></div>',unsafe_allow_html=True)
w=winners(); R=FIXED_R+sum(x=='R' for x in w.values());D=FIXED_D+sum(x=='D' for x in w.values());U=100-R-D
x,y,z,t=st.columns(4)
x.metric('🔴 REPUBLICAN SEATS',R);y.metric('🔵 DEMOCRATIC CAUCUS',D)
z.metric('⚪ UNASSIGNED RACES',U);t.metric('🏛️ MAJORITY STATUS', 'R 51+' if R>=51 else 'D 51+' if D>=51 else 'OPEN')
st.caption(f'Assigned: {R} Republican / {D} Democratic caucus / {U} unassigned · 51 needed for outright majority')
if R>=51: st.info('The selected assignments give Republicans at least 51 seats.')
elif D>=51: st.info('The selected assignments give the Democratic caucus at least 51 seats.')
else: st.info(f'No majority assigned yet. Possible final ranges: Republican {R}–{R+U}; Democratic caucus {D}–{D+U}. The 50–50 tie-break depends on the vice president.')

st.markdown('<div class="section-strip">Election map &amp; Senate chamber</div>',unsafe_allow_html=True)
left,right=st.columns([1.75,1],gap='medium')
with left:
    st.subheader('Click a contested state')
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
                         paper_bgcolor=BG,margin=dict(l=0,r=0,t=0,b=0),height=390,dragmode=False)
    event=st.plotly_chart(mapfig,use_container_width=True,key='interactive_map',on_select='rerun',selection_mode='points')
    selected_points=event.selection.points if event else []
    for point in selected_points:
        # scattergeo is second trace, point_index matches our state list
        if point.get('curve_number')==1 and point.get('point_index') is not None:
            abbr=order[point['point_index']]
            st.session_state.selected_state=abbr
            break
    st.caption('Select a state marker to open its race details below. Only contested states are colored; gray means unassigned.')

with right:
    st.subheader('Senate chamber · 100 seats')
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
    seatfig.update_layout(height=310,paper_bgcolor=BG,plot_bgcolor=BG,margin=dict(l=0,r=0,t=0,b=0),showlegend=False,
                          xaxis=dict(visible=False,range=[-1.5,1.5],scaleanchor='y'),yaxis=dict(visible=False,range=[-.1,1.52]))
    st.plotly_chart(seatfig,use_container_width=True,key='seats_plot')
    st.caption('First 65 seats are fixed. The remaining 35 reflect poll-leader assignments or manual overrides; gray = unassigned.')

st.markdown('<div class="section-strip">Candidate profiles &amp; scenario lab</div>',unsafe_allow_html=True)
a,b=st.columns([1,1.25],gap='large')
with a:
    st.subheader('Candidate & polling desk')
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
    st.subheader('Flip the seat · scenario lab')
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
st.subheader('All 35 races · source data')
overview=races.copy();overview['poll_D%']=overview.abbr.map(polls.dem_pct.to_dict());overview['poll_R%']=overview.abbr.map(polls.rep_pct.to_dict())
overview['poll_reported']=overview.abbr.map(polls.reported_date.to_dict());overview['poll_based']=overview.abbr.map(defaults());overview['scenario']=overview.abbr.map(w)
overview['user_override']=overview.abbr.map(lambda q:'Yes' if q in st.session_state.overrides else 'No')
with st.expander('View all 35 races and polling data'):
    st.dataframe(overview.rename(columns={'state':'State','rating':'Rating','poll_D%':'Dem %','poll_R%':'Rep %','scenario':'Scenario assignment'}),hide_index=True,use_container_width=True)
st.download_button('📥 Download scenario CSV',overview.to_csv(index=False),file_name='senate_2026_v2_scenario.csv',mime='text/csv')
st.caption('© Scenario explorer · Poll snapshot entries transcribed Oct. 9, 2026 from RealClearPolling. Not a forecast or certified result. Nebraska may involve an independent; the simplified R/D assignment is not a comprehensive candidate model.')
