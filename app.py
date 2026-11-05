from pathlib import Path
from datetime import date,datetime
import pandas as pd
import plotly.express as px
import streamlit as st
from src.design import setup,hero,kpi,plot,COLORS,CHANNEL_COLORS
import html
from src.model import COLUMNS,CHANNELS,read_csv,validate,database,summary,metrics,scenario

st.set_page_config(page_title='Campaign Decisions',page_icon='📊',layout='wide')
ROOT=Path(__file__).parent
setup()
with st.sidebar:
    st.markdown('<div class="brand">campaign<span>IQ.</span></div><div class="brand-sub">Your decision workspace</div>',unsafe_allow_html=True)
    st.header('Data & reporting')
    source=st.selectbox('Dataset',['Education business · demo','Alternative demo','Upload CSV files'])
    uploads={}
    if source=='Upload CSV files':
        st.caption('UTF-8 CSV • INR • use the column templates below. Uploads stay in this session and do not replace demo files.')
        for name,cols in COLUMNS.items():
            st.download_button(f'{name} template',pd.DataFrame(columns=cols).to_csv(index=False),file_name=f'{name}.csv',key=f't_{name}')
            uploads[name]=st.file_uploader(name,type='csv',key=name)
    st.caption('Fictional data for learning and demonstration.' if source!='Upload CSV files' else 'Use the four CSV templates to prepare your data.')
try:
    if uploads:
        if not all(uploads.values()): st.info('Upload all four files to validate and analyze your dataset.');st.stop()
        tables={n:read_csv(f) for n,f in uploads.items()}
    else:
        folder=ROOT/'data'/('demo' if source.startswith('Education') else 'second_demo')
        tables={n:read_csv(folder/f'{n}.csv') for n in COLUMNS}
except Exception as exc:
    st.error(f'Unable to read CSV files: {exc}');st.stop()
errors=validate(tables)
if errors:
    st.error(f'Dataset rejected: {len(errors)} validation issues. Existing demo data is unchanged.')
    st.dataframe(pd.DataFrame({'issue':errors}),hide_index=True)
    st.stop()
minimum=date.fromisoformat(tables['spend_daily'].spend_date.min())
maximum=date.fromisoformat(tables['spend_daily'].spend_date.max())
outcome_max=max(maximum,date.fromisoformat(tables['orders'].order_date.max()) if len(tables['orders']) else maximum)
with st.sidebar:
    start=st.date_input('Acquired from',minimum)
    end=st.date_input('Acquired through',maximum)
    cutoff=st.date_input('Count results up to',outcome_max,help='Count qualifications, new customers and orders recorded by this date. Leads may convert later.')
    channels=st.multiselect('Channels',CHANNELS+['Unattributed'],default=CHANNELS+['Unattributed'])
    page=st.radio('Page',['Performance overview','Campaign comparison','Budget scenario'])
if start>end or cutoff<end:
    st.error('Select a valid reporting window and an outcome cutoff on or after its end.');st.stop()
descriptions={
    'Performance overview': 'Which channels bring customers, and what does it cost to acquire them?',
    'Campaign comparison': 'Compare the campaigns behind the numbers before deciding where to spend.',
    'Budget scenario': 'What could a different budget deliver, and what would need to hold true?'}
hero(page,descriptions[page])
intro = ('This project looks at a practical marketing question for a fictional education business: where should the next budget go? '
         'It connects campaign spending with lead quality, new customers and revenue, then explores the financial trade-offs of a proposed allocation. '
         'The aim is to turn the numbers into a recommendation a manager can understand and discuss. The demo uses synthetic data.')
if source=='Upload CSV files':
    intro='This workspace connects your campaign spending with leads, customers and revenue. Compare performance, investigate campaign outcomes and explore a budget allocation using clearly stated assumptions. Recommendations depend on the quality and completeness of your uploaded data.'
st.markdown(f'<p class="project-intro">{intro}</p>',unsafe_allow_html=True)
with st.expander('Reporting dates & selected channels'):
    st.write(f'Leads acquired: {start:%d %b %Y} to {end:%d %b %Y}. Results counted up to: {cutoff:%d %b %Y}.')
    st.write('Selected channels: '+(', '.join(channels) or 'None'))
    st.caption(f'Source: {source}. Loaded {datetime.now():%d %b %Y, %H:%M:%S} local time. Unattributed means a lead has no recorded acquisition campaign.')
if (cutoff-end).days<30:
    st.info(f'Some recent leads may still become customers. This report counts results only up to {cutoff:%d %b %Y}; later conversions are not included, so recent campaigns may look less effective than they eventually prove to be.')
with st.spinner('Calculating cohort outcomes…'):
    db=database(tables);df=summary(db,start,end,cutoff,channels)
if df[['spend','leads']].sum().sum()==0:
    st.info('No data matches these filters. Adjust the reporting window or channels.');st.stop()
def show_table(data,name):
    with st.expander('View data & export · '+name.replace('_',' ').title()):
        st.dataframe(data,hide_index=True,width='stretch')
        st.download_button('↓ Download CSV',data.to_csv(index=False),file_name=name+'.csv',key=name)
def chart(data,x,y,title,color=None):
    fig=px.bar(data,x=x,y=y,color=color,title=title,color_discrete_sequence=COLORS,color_discrete_map=CHANNEL_COLORS)
    fig.update_traces(marker_line_width=0)
    fig.update_layout(showlegend=False)
    fig.update_xaxes(tickangle=-25,automargin=True)
    if x=='case':
        fig.update_traces(marker_color=['#a2b5e2','#5878c6','#3559b8'],
                          hovertemplate='%{x}<br>Contribution: ₹%{y:,.0f}<extra></extra>')
        fig.update_xaxes(title_text='',tickangle=0,categoryorder='array',
                         categoryarray=['Lower efficiency','Base','Higher efficiency'])
        fig.update_yaxes(title_text='Contribution (INR)')
    if x=='channel':
        fig.update_xaxes(title_text='',tickmode='array',tickvals=list(data[x]),ticktext=[v.replace(' ','<br>') for v in data[x]],tickangle=0)
        fig.update_yaxes(title_text='New customers')
        fig.update_xaxes(range=[-.65,len(data)-.35])
        fig.update_layout(margin=dict(l=55,r=55,t=75,b=100))
    plot(fig)
if page=='Performance overview':
    m=metrics(df)
    labels={'spend':('Marketing spend','Investment in selected window'),'leads':('Acquired leads','New leads in this cohort'),'qualified':('Qualified leads','Qualified by outcome cutoff'),'customers':('New customers','Unique acquired customers'),'revenue':('Attributed revenue','Net of recorded refunds'),'cpl':('Cost per lead','Spend / acquired leads'),'qualification_rate':('Qualification rate','Qualified / acquired leads'),'cac':('Acquisition cost','Spend / new customers'),'roas':('Revenue / ad spend','Attributed revenue multiple')}
    for columns,keys in [(st.columns(5),['spend','leads','qualified','customers','revenue']),(st.columns(4),['cpl','qualification_rate','cac','roas'])]:
        for index,(col,key) in enumerate(zip(columns,keys)):
            val=m[key]
            display='Unavailable' if val is None else f'{val:.1%}' if key=='qualification_rate' else f'₹{val:,.0f}' if key in ['spend','revenue','cpl','cac'] else f'{val:.2f}×' if key=='roas' else f'{val:,.0f}'
            kpi(col,labels[key][0],display,labels[key][1],COLORS[index%len(COLORS)])
    st.write('')
    channel=df.groupby('channel',as_index=False)[['spend','leads','qualified','customers','revenue']].sum()
    left,right=st.columns([1.25,1])
    with left:
        chart(channel,'channel','customers','Where customers come from',color='channel')
    with right:
        spending_channels=channel[channel.spend>0].copy()
        if spending_channels.empty:
            st.info('No recorded marketing spend in this selection. There is no spending mix to display.')
        else:
            fig=px.pie(spending_channels,names='channel',values='spend',hole=.72,title='Marketing investment mix',color='channel',color_discrete_sequence=COLORS,color_discrete_map=CHANNEL_COLORS)
            fig.update_traces(textposition='inside',textinfo='percent',textfont_color='white',marker_line_color='white',marker_line_width=3)
            fig.update_layout(legend=dict(orientation='h',y=-.15,yanchor='top',x=0),margin=dict(l=20,r=20,t=70,b=130))
            plot(fig)
        excluded=channel.loc[channel.spend<=0,'channel'].tolist()
        if excluded:
            st.caption('No recorded spend: '+', '.join(excluded)+'. These categories are excluded from the spending mix; their leads and customers remain in the other reports.')
    show_table(channel,'channel_summary')
    periods=pd.period_range(start,end,freq='M');monthly=[]
    for period in periods:
        d=summary(db,max(start,period.start_time.date()),min(end,period.end_time.date()),cutoff,channels)
        monthly.append({'month':str(period),**metrics(d)})
    trend=pd.DataFrame(monthly)
    trend_plot=trend.rename(columns={'leads':'Leads','qualified':'Qualified leads','customers':'New customers'})
    fig=px.line(trend_plot,x='month',y=['Leads','Qualified leads','New customers'],markers=True,title='From leads to customers · by month',labels={'value':'People','variable':''})
    fig.update_traces(line_width=3)
    fig.update_xaxes(title_text='',tickmode='array',tickvals=trend.month.tolist(),ticktext=[pd.Period(v).strftime('%b<br>%Y') for v in trend.month],tickangle=0)
    plot(fig)
    show_table(trend,'monthly_cohorts')
elif page=='Campaign comparison':
    plot(px.scatter(df,x='spend',y='customers',size='leads',color='channel',symbol='channel',
                    color_discrete_map=CHANNEL_COLORS,
                    symbol_map={'Paid Search':'circle','Paid Social':'diamond','Email':'square','Partner':'triangle-up','Unattributed':'hexagon'},
                    category_orders={'channel':CHANNELS+['Unattributed']},
                    hover_name='campaign_name',size_max=48,
                    title='Campaign landscape · scale versus results',
                    labels={'spend':'Marketing spend (INR)','customers':'Acquired customers','channel':'Channel'})
         .update_traces(marker_opacity=.95,marker_line_width=1.5,marker_line_color='#203c80'))
    st.caption('Colour and shape identify the channel; marker size represents lead volume. Hover over a campaign for its details, or select a channel in the legend to focus the comparison.')
    show_table(df,'campaign_summary')
    selected=st.selectbox('Inspect campaign',df.campaign_id,format_func=lambda x:df.loc[df.campaign_id==x,'campaign_name'].iloc[0])
    leads=tables['leads'];detail=leads[(leads.campaign_id==selected)&(leads.created_at.str[:10]>=str(start))&(leads.created_at.str[:10]<=str(end))].copy()
    detail['qualified_by_cutoff']=(detail.qualified_at!='')&(detail.qualified_at.str[:10]<=str(cutoff))
    detail['customer_by_cutoff']=(detail.won_at!='')&(detail.won_at.str[:10]<=str(cutoff))
    show_table(detail[['lead_id','created_at','qualified_by_cutoff','customer_by_cutoff']],'lead_outcomes')
else:
    st.subheader('Budget and profitability scenarios')
    st.write('Historical CAC is held constant. Lower/higher cases change acquisitions by −20%/+20%; these are sensitivity cases, not confidence intervals. Revenue and delivery assumptions use the same customer-value horizon.')
    budget=st.number_input('Proposed marketing budget (INR)',min_value=1.,value=100000.)
    usable=[c for c in channels if c!='Unattributed']
    allocation_columns=st.columns(max(1,len(usable)))
    allocations={}
    for col,c in zip(allocation_columns,usable):
        with col:
            allocations[c]=st.number_input(f'{c} allocation (INR)',min_value=0.,value=budget/len(usable),key=f'alloc_{c}')
    revenue=st.number_input('Assumed net revenue per customer (INR)',min_value=0.,value=6000.)
    cost=st.number_input('Assumed delivery/service cost per customer (INR)',min_value=0.,value=2000.)
    st.caption('Return on marketing spend = (estimated revenue − delivery/service costs − marketing budget) / marketing budget. Fixed overhead and tax are excluded. These cost assumptions are user inputs, not inferred from orders.')
    try:
        result=scenario(df,allocations,budget,revenue,cost)
        chart(result,'case','contribution','Estimated contribution after marketing (INR)')
        show_table(result,'budget_scenarios')
        st.metric('Break-even CAC under these assumptions',f'₹{revenue-cost:,.2f}')
        st.markdown('<div class="scenario-note" style="background:#edf3ff;color:#203c80;border:1px solid #d6e2fa;border-radius:12px;padding:18px 22px;font-size:15px;line-height:1.8;margin:16px 0;">Historical attribution does not establish incremental impact. Larger budgets can face diminishing returns. Validate a proposed change with a controlled pilot before scaling.</div>',unsafe_allow_html=True)
    except ValueError as exc: st.error(str(exc))
with st.expander('Data quality & provenance'):
    st.markdown('<div style="background:#edf3ff;color:#203c80;border:1px solid #d6e2fa;border-radius:12px;padding:18px 22px;font-size:15px;line-height:1.8;margin:8px 0 16px;">Required columns, IDs, relationships, dates and monetary bounds passed validation.</div>',unsafe_allow_html=True)
    st.write({n:len(t) for n,t in tables.items()})
    st.write('Unattributed leads:',int((tables['leads'].campaign_id=='').sum()))
    linked=set(tables['leads'].customer_id)-{''}
    st.write('Orders without an acquisition lead (excluded from cohort revenue):',int((~tables['orders'].customer_id.isin(linked)).sum()))
    st.caption('The main demo uses generator seed 42; the alternative uses seed 73. A seed is a fixed starting value that recreates the same fictional data each time. It is not a performance score.')
    st.caption('Amounts are INR. Synthetic demos are not evidence of real business impact. Missing optional outcomes remain pending; no values are imputed.')
st.caption('Definitions: acquisition follows the lead’s campaign; customers are unique acquisition leads with won outcomes. Net order revenue includes refunds recorded in the source. ROAS is revenue/spend, not profit.')
