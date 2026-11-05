import pandas as pd
import pytest
from src.model import validate,database,summary,metrics,scenario

@pytest.fixture
def tables():
    campaigns=pd.DataFrame([['C','Test','Email','2026-01-01','2026-01-31']],columns=['campaign_id','campaign_name','channel','start_date','end_date'])
    spend=pd.DataFrame([['C','2026-01-01','1000']],columns=['campaign_id','spend_date','spend_amount'])
    leads=pd.DataFrame([[f'L{i}','C','2026-01-01T00:00:00','2026-01-02T00:00:00' if i<5 else '', '2026-01-03T00:00:00' if i<2 else '',f'U{i}' if i<2 else ''] for i in range(20)],columns=['lead_id','campaign_id','created_at','qualified_at','won_at','customer_id'])
    orders=pd.DataFrame([['O1','U0','2026-01-03','1000','0','1'],['O2','U0','2026-01-04','1000','0','0'],['O3','U1','2026-01-03','1200','200','1']],columns=['order_id','customer_id','order_date','gross_amount','refund_amount','new_customer'])
    return dict(campaigns=campaigns,spend_daily=spend,leads=leads,orders=orders)

def report(t,start='2026-01-01',end='2026-01-31',cutoff='2026-01-31'):
    return summary(database(t),start,end,cutoff,['Email'])

def test_fixture_and_multiple_orders(tables):
    assert validate(tables)==[]
    m=metrics(report(tables))
    assert [m[k] for k in ['cpl','qualification_rate','cac','roas','customers']]==[50,.25,500,3,2]

def test_zero_and_empty(tables):
    tables['spend_daily'].loc[0,'spend_amount']='0'
    assert metrics(report(tables))['roas'] is None
    assert metrics(report(tables,'2027-01-01','2027-01-31','2027-01-31'))['leads']==0

@pytest.mark.parametrize('problem',['duplicate','foreign','date','refund','customer'])
def test_reject(tables,problem):
    if problem=='duplicate': tables['leads'].loc[1,'lead_id']='L0'
    if problem=='foreign': tables['leads'].loc[1,'campaign_id']='bad'
    if problem=='date': tables['orders'].loc[0,'order_date']='bad'
    if problem=='refund': tables['orders'].loc[0,'refund_amount']='9999'
    if problem=='customer': tables['leads'].loc[1,'customer_id']='U0'
    assert validate(tables)

def test_cutoff_and_channel(tables):
    assert metrics(report(tables,'2026-01-01','2026-01-01','2026-01-01'))['customers']==0
    assert summary(database(tables),'2026-01-01','2026-01-31','2026-01-31',['Partner']).empty

def test_scenario(tables):
    history=report(tables)
    with pytest.raises(ValueError): scenario(history,{'Email':1100},1000,5000,2000)
    result=scenario(history,{'Email':1000},1000,5000,2000)
    assert result.iloc[1].customers==2
    assert result.iloc[1].contribution==5000
    assert len(pd.read_csv(__import__('io').StringIO(history.to_csv(index=False))))==1
