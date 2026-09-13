from rdata_reader import Reader,val,attrs
import bz2,tarfile,json,math,datetime,calendar,hashlib
from pathlib import Path
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();assert not args.output.exists();args.output.parent.mkdir(parents=True,exist_ok=True)
root=Path(__file__).parent/'sources'
t=tarfile.open(root/'evmissing_1.0.2.tar.gz');objects={};receipts={}
for name in ['PlymouthOzone','PlymouthOzoneMaxima']:
 compressed=t.extractfile('evmissing/data/'+name+'.rda').read();r=Reader(bz2.decompress(compressed));o=r.obj();assert r.i==len(r.b) and o['cdr'] is None and val(o['tag'])==name
 df=o['car'];a=attrs(df);assert a['class']==['data.frame'];cols=dict(zip(a['names'],val(df)));assert len({len(v) for v in cols.values()})==1
 objects[name]=cols;receipts[name]={'compressed_sha256':hashlib.sha256(compressed).hexdigest(),'rows':len(next(iter(cols.values()))),'columns':a['names'],'attributes':a,'column_attributes':[attrs(x) for x in df['value']]}
raw=objects['PlymouthOzone'];annual=objects['PlymouthOzoneMaxima'];rows=[];dates=[]
for d,y,x in zip(raw['Date'],raw['Year'],raw['Ozone']):
 assert d==int(d);dt=datetime.date(1970,1,1)+datetime.timedelta(days=d);assert dt.year==y;dates.append(dt)
assert dates==[datetime.date(1998,1,1)+datetime.timedelta(days=i) for i in range(len(dates))]
assert dates[-1]==datetime.date(2024,12,31)
for i,y in enumerate(range(1998,2025)):
 xs=[x for yy,x in zip(raw['Year'],raw['Ozone']) if yy==y and not math.isnan(x)]
 row={'year':y,'maxima':max(xs),'notNA':len(xs),'n':365+calendar.isleap(y),'block':i+1}
 for k in ['maxima','notNA','n','block']:assert row[k]==annual[k][i],(y,k,row[k],annual[k][i])
 rows.append(row)
report={'receipts':receipts,'all_27_annual_rows_match':True,'date_grid_complete':True,'missing_days':sum(math.isnan(x) for x in raw['Ozone']),'annual':rows}
args.output.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'rows':len(dates),'annual_match':True,'missing_days':report['missing_days'],'special_years':[x for x in rows if x['year'] in [2001,2006]]}))
