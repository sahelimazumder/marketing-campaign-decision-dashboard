"""Validated data contract, SQLite reporting and pure business calculations."""
import sqlite3
from datetime import datetime
from decimal import Decimal, InvalidOperation
import pandas as pd

COLUMNS = {
 'campaigns': ['campaign_id','campaign_name','channel','start_date','end_date'],
 'spend_daily': ['campaign_id','spend_date','spend_amount'],
 'leads': ['lead_id','campaign_id','created_at','qualified_at','won_at','customer_id'],
 'orders': ['order_id','customer_id','order_date','gross_amount','refund_amount','new_customer']}
CHANNELS = ['Paid Search','Paid Social','Email','Partner']

def read_csv(source):
    return pd.read_csv(source, dtype=str, keep_default_na=False, encoding='utf-8').fillna('')

def validate(tables):
    errors = []
    for name, cols in COLUMNS.items():
        if name not in tables or set(cols) - set(tables[name].columns):
            errors.append(f'{name}: missing table or required columns: {cols}')
    if errors: return errors
    for name, frame in tables.items():
        if name not in COLUMNS: continue
        keys = ['campaign_id','spend_date'] if name == 'spend_daily' else [COLUMNS[name][0]]
        for idx, row in frame.iterrows():
            prefix = f'{name}, CSV row {idx+2}: '
            nullable = {'campaign_id','qualified_at','won_at','customer_id'} if name == 'leads' else set()
            for col in COLUMNS[name]:
                value = str(row[col])
                if not value and col not in nullable: errors.append(prefix+f'{col} is required')
                if value and (col.endswith('_date') or col in ['created_at','qualified_at','won_at']):
                    try:
                        if col.endswith('_date'): datetime.strptime(value,'%Y-%m-%d')
                        else:
                            dt = datetime.fromisoformat(value)
                            if dt.tzinfo: raise ValueError('Use timezone-naive timestamps consistently')
                    except ValueError: errors.append(prefix+f'invalid ISO date/time in {col}')
                if col in ['spend_amount','gross_amount','refund_amount']:
                    try:
                        amount = Decimal(value)
                        if not amount.is_finite() or amount < 0 or amount != amount.quantize(Decimal('.01')): raise ValueError()
                    except (InvalidOperation, ValueError): errors.append(prefix+f'{col} must be nonnegative INR with at most two decimals')
            if name == 'campaigns':
                if row.channel not in CHANNELS: errors.append(prefix+'unsupported channel')
                if row.start_date > row.end_date: errors.append(prefix+'campaign dates reversed')
            if name == 'orders':
                if row.new_customer not in ['0','1']: errors.append(prefix+'new_customer must be 0 or 1')
                try:
                    if Decimal(row.refund_amount)>Decimal(row.gross_amount): errors.append(prefix+'refund exceeds gross')
                except InvalidOperation: pass
        duplicate = frame.duplicated(keys, keep=False)
        for idx in frame.index[duplicate]: errors.append(f'{name}, CSV row {idx+2}: duplicate primary key')
    campaigns = set(tables['campaigns'].campaign_id)
    for name in ['leads','spend_daily']:
        for idx, row in tables[name].iterrows():
            if row.campaign_id and row.campaign_id not in campaigns: errors.append(f'{name}, CSV row {idx+2}: unknown campaign_id')
    leads = tables['leads']
    linked = leads[leads.customer_id!='']
    if linked.customer_id.duplicated().any(): errors.append('leads: each customer must have exactly one acquisition lead')
    for idx,row in leads.iterrows():
        if bool(row.won_at) != bool(row.customer_id): errors.append(f'leads, CSV row {idx+2}: won_at and customer_id must be supplied together')
        for col in ['qualified_at','won_at']:
            if row[col] and row[col]<row.created_at: errors.append(f'leads, CSV row {idx+2}: {col} precedes acquisition')
    return errors

def database(tables):
    db = sqlite3.connect(':memory:')
    for name, frame in tables.items():
        if name not in COLUMNS: continue
        data = frame[COLUMNS[name]].copy()
        for col in ['spend_amount','gross_amount','refund_amount']:
            if col in data: data[col] = data[col].map(lambda x:int(Decimal(str(x))*100))
        data.to_sql(name,db,index=False,if_exists='fail')
    db.executescript('''
    CREATE TABLE report_window (start_date TEXT, end_date TEXT, cutoff TEXT);
    CREATE VIEW campaign_summary_v1 AS
    WITH cohort AS (
      SELECT l.* FROM leads l, report_window w
      WHERE substr(l.created_at,1,10) BETWEEN w.start_date AND w.end_date
    ), s AS (
      SELECT campaign_id, SUM(spend_amount) spend FROM spend_daily, report_window w
      WHERE spend_date BETWEEN w.start_date AND w.end_date GROUP BY campaign_id
    ), outcomes AS (
      SELECT c.campaign_id,COUNT(*) leads,
      SUM(CASE WHEN qualified_at != '' AND substr(qualified_at,1,10)<=w.cutoff THEN 1 ELSE 0 END) qualified,
      SUM(CASE WHEN won_at != '' AND substr(won_at,1,10)<=w.cutoff THEN 1 ELSE 0 END) customers
      FROM cohort c, report_window w GROUP BY c.campaign_id
    ), revenue AS (
      SELECT c.campaign_id,SUM(o.gross_amount-o.refund_amount) revenue
      FROM cohort c JOIN orders o ON o.customer_id=c.customer_id, report_window w
      WHERE c.customer_id!='' AND c.won_at!='' AND substr(c.won_at,1,10)<=w.cutoff
      AND o.order_date BETWEEN substr(c.won_at,1,10) AND w.cutoff GROUP BY c.campaign_id
    ), all_campaigns AS (
      SELECT campaign_id,campaign_name,channel FROM campaigns
      UNION ALL SELECT '', 'Unattributed', 'Unattributed'
    )
    SELECT a.*,COALESCE(s.spend,0)/100.0 spend,COALESCE(l.leads,0) leads,
    COALESCE(l.qualified,0) qualified,COALESCE(l.customers,0) customers,
    COALESCE(r.revenue,0)/100.0 revenue
    FROM all_campaigns a LEFT JOIN s USING(campaign_id)
    LEFT JOIN outcomes l USING(campaign_id) LEFT JOIN revenue r USING(campaign_id);
    ''')
    return db

def summary(db,start,end,cutoff,channels):
    if start>end or cutoff<end: raise ValueError('Outcome cutoff must be on or after the reporting window')
    db.execute('DELETE FROM report_window')
    db.execute('INSERT INTO report_window VALUES (?,?,?)',(str(start),str(end),str(cutoff)))
    df=pd.read_sql_query('SELECT * FROM campaign_summary_v1',db)
    df=df[df.channel.isin(channels)].copy()
    for metric,num,den in [('cpl','spend','leads'),('qualification_rate','qualified','leads'),('cac','spend','customers'),('roas','revenue','spend')]:
        df[metric]=df[num]/df[den].replace(0,float('nan'))
    return df

def metrics(df):
    totals=df[['spend','leads','qualified','customers','revenue']].sum().to_dict()
    for metric,num,den in [('cpl','spend','leads'),('qualification_rate','qualified','leads'),('cac','spend','customers'),('roas','revenue','spend')]:
        totals[metric]=totals[num]/totals[den] if totals[den] else None
    return totals

def scenario(history,allocations,budget,revenue_per_customer,delivery_cost):
    if budget<=0 or any(v<0 for v in allocations.values()) or abs(sum(allocations.values())-budget)>.01:
        raise ValueError('Allocations must be nonnegative and sum to the positive proposed budget')
    customers=0
    for channel,amount in allocations.items():
        row=history[history.channel==channel]
        if amount:
            if row.empty or row.customers.sum()<=0 or row.spend.sum()<=0:
                raise ValueError(f'{channel}: no usable historical CAC; no estimate available')
            customers+=amount/(row.spend.sum()/row.customers.sum())
    rows=[]
    for label,factor in [('Lower efficiency',.8),('Base',1),('Higher efficiency',1.2)]:
        count=customers*factor
        revenue=count*revenue_per_customer
        contribution=revenue-count*delivery_cost-budget
        rows.append(dict(case=label,customers=count,revenue=revenue,contribution=contribution,return_on_marketing_spend=contribution/budget))
    return pd.DataFrame(rows)
