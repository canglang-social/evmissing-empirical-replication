"""Download exact public source versions, verify hashes, extract named data only. No R execution."""
from pathlib import Path
import urllib.request,hashlib,json,time,tarfile,bz2,math
from rdata_reader import Reader,val,attrs
root=Path(__file__).resolve().parent
specs=[('evmissing_1.0.2.tar.gz','https://cran.r-project.org/src/contrib/evmissing_1.0.2.tar.gz','d3d6477f9df384dc6a735bdd50bf6d5e9b2aa6c09ca2f7884d14be9f1c06e6b5'),('Renext_3.1-4.tar.gz','https://cran.r-project.org/src/contrib/Archive/Renext/Renext_3.1-4.tar.gz','704ee817cd7751d3683d7c484cad2960425bae937a49ad92c6007919654d6f9f')]
t0=time.monotonic();report={'status':'running','sources':[],'licence_cleared':False}
assert not (root/'sources').exists(),'fresh setup directory required'
(root/'sources').mkdir();(root/'data').mkdir()
try:
 for name,url,digest in specs:
  with urllib.request.urlopen(url,timeout=60) as response:
   data=response.read(30_000_001)
  assert len(data)<=30_000_000,'source size limit'
  actual=hashlib.sha256(data).hexdigest();assert actual==digest,('source hash mismatch',name,actual)
  (root/'sources'/name).write_bytes(data);report['sources'].append({'file':name,'url':url,'sha256':actual,'bytes':len(data)})
 with tarfile.open(root/'sources'/'Renext_3.1-4.tar.gz') as t:
  for name in ['Brest.csv','Brest_missing.csv']:
   (root/'sources'/name).write_bytes(t.extractfile('Renext/inst/Rendata/'+name).read())
 with tarfile.open(root/'sources'/'evmissing_1.0.2.tar.gz') as t:
  data=t.extractfile('evmissing/data/BrestSurgeMaxima.rda').read()
 rd=Reader(bz2.decompress(data));obj=rd.obj();assert rd.i==len(rd.b) and val(obj['tag'])=='BrestSurgeMaxima' and obj['cdr'] is None
 frame=obj['car'];columns=dict(zip(attrs(frame)['names'],val(frame)))
 assert len(columns['maxima'])==162
 rows=[{'year':1846+i,'maxima':None if math.isnan(columns['maxima'][i]) else columns['maxima'][i],'notNA':columns['notNA'][i],'n':columns['n'][i]} for i in range(162)]
 (root/'data'/'brest-annual.json').write_text(json.dumps({'annual':rows,'source':'evmissing 1.0.2 BrestSurgeMaxima; downloaded archive hash verified'},indent=2)+'\n')
 report['annual_reference_rows']=len(rows);report['status']='completed'
except Exception as e:report.update(status='stopped',error=repr(e))
finally:
 report['wall_seconds']=time.monotonic()-t0;(root/'setup-receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if report['status']!='completed':raise SystemExit(1)
