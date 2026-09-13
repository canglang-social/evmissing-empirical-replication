"""One fresh, sequential aggregation -> fit -> endpoint audit chain."""
import argparse,subprocess,sys,json,time,hashlib
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,required=True);args=ap.parse_args();dest=args.output_dir.resolve();assert not dest.exists(),'fresh directory required';dest.mkdir(parents=True);root=Path(__file__).resolve().parent;t0=time.monotonic();report={'status':'running','stages':[],'new_simulation_datasets':0}
def save():
 report['wall_seconds']=time.monotonic()-t0;tmp=dest/'receipt.tmp';tmp.write_text(json.dumps(report,indent=2)+'\n');tmp.replace(dest/'receipt.json')
try:
 for dataset in ['plymouth','brest']:
  annual=dest/f'{dataset}-annual.json';fit=dest/f'{dataset}-fit.json';audit=dest/f'{dataset}-audit.json'
  stages=[('aggregate',[f'aggregate_{dataset}.py','--output',str(annual)],annual),('fit',['replay.py',dataset,'--input',str(annual),'--output',str(fit)],fit),('audit',['audit_endpoints.py',dataset,'--input',str(annual),'--fit',str(fit),'--output',str(audit)],audit)]
  for name,cmd,out in stages:
   remaining=120-(time.monotonic()-t0)
   if remaining<=0:raise RuntimeError('120-second chain cap')
   result=subprocess.run([sys.executable,str(root/cmd[0]),*cmd[1:]],capture_output=True,text=True,timeout=min(60,remaining));(dest/f'{dataset}-{name}.log').write_text(result.stdout+'\n'+result.stderr);record={'dataset':dataset,'stage':name,'exit_code':result.returncode};report['stages'].append(record);save()
   if result.returncode:raise RuntimeError('process failure')
   data=json.loads(out.read_text())
   if name=='fit' and data['status']!='completed':raise RuntimeError('fit incomplete')
   if name=='audit' and (data['status']!='passed' or len(data['checks'])!=48):raise RuntimeError('audit incomplete')
   record['output_sha256']=hashlib.sha256(out.read_bytes()).hexdigest();record['status']='passed';save()
 report['status']='completed'
except Exception as exc:report['status']='stopped';report['error']=repr(exc)
finally:save();print(json.dumps(report))
if report['status']!='completed':sys.exit(1)
