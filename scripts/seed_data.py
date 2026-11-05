"""Explicit generator; writes a new directory and never overwrites datasets."""
import csv, random, argparse
from pathlib import Path
from datetime import datetime,timedelta

def generate(target,seed=42):
    target=Path(target)
    if target.exists(): raise FileExistsError(f'{target} exists; choose a new directory')
    target.mkdir(parents=True)
    rng=random.Random(seed); start=datetime(2026,1,1)
    channels=['Paid Search','Paid Social','Email','Partner']
    campaigns=[dict(campaign_id=f'C{i:02}',campaign_name=f'{channels[i%4]} programme {i//4+1}',channel=channels[i%4],start_date='2026-01-01',end_date='2026-06-29') for i in range(12)]
    spend=[]; leads=[]; orders=[]
    for c in campaigns:
        for day in range(180):
            spend.append(dict(campaign_id=c['campaign_id'],spend_date=(start+timedelta(days=day)).date().isoformat(),spend_amount=0 if c['campaign_id']=='C10' else rng.randint(100,550)))
    for i in range(2000):
        created=start+timedelta(days=rng.randrange(180),hours=rng.randrange(24))
        campaign=rng.choice(campaigns); qualified=created+timedelta(days=rng.randint(1,12)) if rng.random()<.42 else None
        won=qualified+timedelta(days=rng.randint(1,25)) if qualified and rng.random()<[.32,.18,.44,.38][channels.index(campaign['channel'])] else None
        cutoff=datetime(2026,7,15,23,59,59)
        if qualified and qualified>cutoff: qualified=None
        if won and won>cutoff: won=None
        customer=f'U{i:04}' if won else ''
        leads.append(dict(lead_id=f'L{i:04}',campaign_id=campaign['campaign_id'] if rng.random()>.04 else '',created_at=created.isoformat(),qualified_at=qualified.isoformat() if qualified else '',won_at=won.isoformat() if won else '',customer_id=customer))
        if won:
            for j in range(1+(rng.random()<.2)):
                date=won+timedelta(days=j*7)
                if date>cutoff: continue
                gross=rng.choice([4000,6000,8000])
                orders.append(dict(order_id=f'O{i:04}-{j}',customer_id=customer,order_date=date.date().isoformat(),gross_amount=gross,refund_amount=gross if rng.random()<.06 else 0,new_customer=int(j==0)))
    for name,rows in [('campaigns',campaigns),('spend_daily',spend),('leads',leads),('orders',orders)]:
        with (target/f'{name}.csv').open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default='data/generated');p.add_argument('--seed',type=int,default=42);a=p.parse_args();generate(a.output,a.seed)
