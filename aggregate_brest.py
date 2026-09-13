"""Reconstruct annual inputs from distributed processed-event CSVs; no gauge preprocessing."""
import argparse,csv,datetime as dt,calendar,json,hashlib
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();assert not args.output.exists();args.output.parent.mkdir(parents=True,exist_ok=True)
r=Path(__file__).parent;s=r/'sources'
events=list(csv.DictReader((s/'Brest.csv').open(),delimiter=';'));missing=list(csv.DictReader((s/'Brest_missing.csv').open(),delimiter=';'));days=set()
for row in missing:
 a=dt.date.fromisoformat(row['start']);b=dt.date.fromisoformat(row['end']);assert a<=b
 days.update(a+dt.timedelta(days=i) for i in range((b-a).days+1))
rows=[]
for i,year in enumerate(range(1846,2008)):
 values=[float(row['surge']) for row in events if dt.date.fromisoformat(row['date']).year==year];n=365+calendar.isleap(year);start=dt.date(year,1,1);absent=sum(start+dt.timedelta(days=j) in days for j in range(n));rows.append({'year':year,'maxima':max(values) if values else None,'notNA':n-absent,'n':n})
expected=json.loads((r/'data'/'brest-annual.json').read_text())['annual'];assert len(rows)==len(expected)==162
for row,old in zip(rows,expected):assert all(row[k]==old[k] for k in row),(row,old)
args.output.write_text(json.dumps({'annual':rows,'status':'all_162_rows_match','scope':'processed events, inclusive missing-day intervals; 1846-2007','sources':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [s/'Brest.csv',s/'Brest_missing.csv']}},indent=2)+'\n');print('all 162 annual rows match')
