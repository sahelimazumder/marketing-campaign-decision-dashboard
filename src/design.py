"""Shared presentation styles. Business calculations live in model.py."""
import html
import streamlit as st
import plotly.io as pio
import plotly.graph_objects as go

COLORS=['#142b70','#3055b5','#6385d0','#9db5e7','#d1ddf4']
CHANNEL_COLORS=dict(zip(['Paid Search','Paid Social','Email','Partner','Unattributed'],COLORS))
def setup():
    pio.templates['campaign']=go.layout.Template(layout=dict(
        colorway=COLORS,paper_bgcolor='white',plot_bgcolor='white',
        font=dict(family='Arial, sans-serif',color='#475569',size=12),
        title=dict(font=dict(size=18,color='#0f172a'),x=0),
        margin=dict(l=45,r=35,t=75,b=110),height=430,
        xaxis=dict(showgrid=False,zeroline=False,automargin=True,title_standoff=18,title_font=dict(size=12)),
        yaxis=dict(gridcolor='#edf2f7',zeroline=False,automargin=True,title_standoff=16,title_font=dict(size=12)),
        legend=dict(orientation='h',y=1.02,x=0,yanchor='bottom',title_text='',font=dict(size=11)),
        hoverlabel=dict(bgcolor='#0f172a',font_color='white'),
        barcornerradius=7))
    pio.templates.default='campaign'
    st.markdown('''<style>
    .stApp {background:#f4f7fb;color:#0f172a;}
    .block-container {max-width:1500px;padding-top:2rem;padding-bottom:3rem;}
    header[data-testid="stHeader"] {background:rgba(244,247,251,.95);}
    [data-testid="stSidebar"] {background:#13264e;}
    [data-testid="stSidebar"] * {color:#e2e8f0;}
    [data-testid="stSidebar"] input {color:#0f172a;}
    [data-testid="stSidebar"] [data-baseweb="select"] * {color:#e2e8f0;}
    [data-testid="stSidebar"] [data-baseweb="select"] > div {background:#203861;}
    [data-testid="stSidebar"] [data-baseweb="input"] {background:#203861;}
    [data-testid="stSidebar"] input {color:#e2e8f0;}
    [data-testid="stAlert"] p {color:#254578;}
    [data-testid="stExpander"] summary p {color:#334155;}
    [data-testid="stSidebar"] h2 {font-size:1.05rem;letter-spacing:.02em;}
    [data-testid="stSidebar"] label {font-size:.82rem;}
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {opacity:.7;}
    .stApp {font-family:'Segoe UI',Arial,sans-serif;color:#182c57;}
    h1,h2,h3 {font-family:'Times New Roman',Georgia,serif !important;letter-spacing:-.015em;color:#203c80 !important;}
    .hero h1 {color:white !important;}
    [data-testid="stSidebar"] h2 {color:#edf2ff !important;}
    [data-testid="stWidgetLabel"] p {color:#243e76;}
    [data-testid="stMain"] [data-baseweb="input"],
    [data-testid="stMain"] [data-baseweb="base-input"],
    [data-testid="stMain"] [data-baseweb="select"] > div,
    [data-testid="stNumberInputContainer"] {background:#edf2fc !important;border-color:#cad6f2 !important;color:#203c80 !important;}
    [data-testid="stMain"] input {background:#edf2fc !important;color:#203c80 !important;}
    [data-testid="stMain"] [data-testid="stNumberInput"] button {background:#e3ebfb !important;color:#3559b8 !important;border-color:#cad6f2 !important;}
    [data-baseweb="tag"] {background:#dbe5fc !important;border:1px solid #a7bced !important;}
    [data-baseweb="tag"] *,[data-baseweb="tag"] span {color:#213e88 !important;fill:#213e88 !important;}
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="input"],
    [data-testid="stSidebar"] [data-baseweb="base-input"] {background:#203b75 !important;border-color:#4665a2 !important;}
    [data-testid="stSidebar"] input {background:#203b75 !important;}
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {color:#dfe8ff !important;}
    [data-testid="stSidebar"] input {background:#edf2fc !important;color:#203c80 !important;}
    [data-testid="stSidebar"] [data-baseweb="input"],
    [data-testid="stSidebar"] [data-baseweb="base-input"] {background:#edf2fc !important;color:#203c80 !important;}
    [data-testid="stSidebar"] [data-testid="stDateInput"] [role="spinbutton"],
    [data-testid="stSidebar"] [data-testid="stDateInput"] [role="group"] *,
    [data-testid="stSidebar"] [data-testid="stDateInput"] span,
    [data-testid="stSidebar"] [data-testid="stDateInput"] svg {color:#203c80 !important;fill:#203c80 !important;}
    [data-testid="stSidebar"] [role="radio"][aria-checked="true"] {background:#5878c6 !important;border-color:#a2b5e2 !important;}
    [data-testid="stAlert"] {background:#e8eefc !important;color:#243e76 !important;border-color:#cad6f2 !important;}
    [data-testid="stAlert"] svg {fill:#3559b8 !important;color:#3559b8 !important;}
    .brand {font-size:1.6rem;font-weight:800;letter-spacing:-.06em;color:white;margin:0 0 3px;}
    .brand span {color:#b5c9f1;}
    .brand-sub {font-size:.7rem;text-transform:uppercase;letter-spacing:.18em;color:#94a3b8;margin-bottom:24px;}
    .hero {background:linear-gradient(115deg,#233e86,#5273c4);border-radius:20px;padding:28px 32px;margin-bottom:20px;color:white;position:relative;overflow:hidden;}
    .hero:after {content:'';position:absolute;width:240px;height:240px;border:40px solid #ffffff08;border-radius:50%;right:-40px;top:-90px;pointer-events:none;}
    .eyebrow {font-size:11px;letter-spacing:.19em;font-weight:700;color:#c4d5f5;text-transform:uppercase;margin-bottom:10px;}
    .hero h1 {font-size:2.05rem;color:white;margin:0;padding:0 0 10px;line-height:1.2;}
    .hero p {color:#c3d4e3;margin:0;font-size:.95rem;max-width:760px;}
    .kpi {background:white;border:1px solid #e6edf5;border-radius:15px;padding:19px 20px;min-height:132px;box-shadow:0 4px 15px #0f172a03;border-top:3px solid #3657a6;margin-bottom:10px;}
    .kpi-label {color:#64748b;font-size:12px;font-weight:600;letter-spacing:.02em;}
    .kpi-value {font-size:clamp(20px,2vw,30px);font-weight:750;letter-spacing:-.05em;color:#10243b;margin:8px 0 2px;line-height:1.2;}
    .kpi-note {color:#64748b;font-size:11px;}
    .project-intro {font-size:15px;line-height:1.8;color:#475569;margin:0 0 22px;max-width:1000px;}
    .scenario-note {background:#edf3ff;color:#203c80;border:1px solid #d6e2fa;border-radius:12px;padding:18px 22px;font-size:15px;line-height:1.8;margin:16px 0;}
    .context {font-size:12px;color:#64748b;margin:0 0 12px;line-height:1.9;}
    .pill {display:inline-block;background:#e8eef9;color:#3657a6;border-radius:20px;padding:3px 10px;font-size:11px;font-weight:700;margin-right:10px;}
    [data-testid="stPlotlyChart"] {background:white;border:1px solid #e6edf5;border-radius:16px;padding:0;box-sizing:border-box;overflow:visible;}
    [data-testid="stExpander"] {background:white;border:1px solid #e6edf5;border-radius:12px;}
    [data-testid="stDataFrame"] {border-radius:12px;overflow:hidden;}
    .stDownloadButton button {border-radius:9px;border:1px solid #d9e3ee;font-size:12px;background:white;color:#24425a;}
    [data-testid="stMetric"] {background:white;border-radius:12px;padding:18px;border:1px solid #e6edf5;}
    @media(max-width:1100px){
      [data-testid="stMain"] [data-testid="stHorizontalBlock"] {flex-wrap:wrap;}
      [data-testid="stMain"] [data-testid="stColumn"] {min-width:min(185px,100%);flex:1 1 185px;}
      [data-testid="stMain"] [data-testid="stColumn"]:has([data-testid="stPlotlyChart"]) {min-width:min(340px,100%);flex:1 1 340px;}
      .hero{padding:22px;}.hero h1{font-size:1.6rem;}.kpi-value{font-size:25px;}
    }
    </style>''',unsafe_allow_html=True)

def hero(title,description):
    st.markdown(f'<div class="hero"><div class="eyebrow">Marketing decisions / Portfolio project</div><h1>{html.escape(title)}</h1><p>{html.escape(description)}</p></div>',unsafe_allow_html=True)

def kpi(column,label,value,note,accent='#3559b8'):
    column.markdown(f'<div class="kpi" style="border-top-color:{accent}"><div class="kpi-label">{html.escape(label)}</div><div class="kpi-value">{html.escape(value)}</div><div class="kpi-note">{html.escape(note)}</div></div>',unsafe_allow_html=True)

def plot(fig):
    # Place titles relative to the whole card, with a consistent inset.
    fig.update_layout(title=dict(x=.055,xref='container',xanchor='left',y=.94,yref='container',yanchor='top',
                                 font=dict(family='Times New Roman, Georgia, serif',color='#203c80',size=21)),
                      margin=dict(t=95,l=60,r=45,b=max(100,fig.layout.margin.b or 0)),height=450)
    fig.update_layout(paper_bgcolor='white',plot_bgcolor='white',
                      font=dict(color='#425a87',family='Segoe UI, Arial, sans-serif',size=12),
                      legend_font_color='#425a87',colorway=COLORS)
    fig.update_xaxes(showgrid=False,zeroline=False,automargin=True,tickfont_color='#475569',title_font_color='#475569')
    fig.update_yaxes(gridcolor='#edf2f7',zeroline=False,automargin=True,tickfont_color='#475569',title_font_color='#475569')
    st.plotly_chart(fig,width='stretch',theme=None,config={'displayModeBar':False,'scrollZoom':False})
