import sys,json,hashlib
from pathlib import Path
import numpy as np
from scipy.stats import genextreme,beta
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--results-dir',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();r=args.results_dir;out=args.output;assert not out.exists();configs=[]
for dataset,receipt,fitname,omit in [('Plymouth','plymouth-annual.json','plymouth-fit.json',[2001,2006]),('Brest','brest-annual.json','brest-fit.json',[1857,1859,1944,1952])]:
 rows=json.loads((r/receipt).read_text())['annual'];fits=json.loads((r/fitname).read_text())['conditions']
 for f in fits:
  rr=[a for a in rows if a['maxima'] is not None and (not f['remove'] or a['year'] not in omit)];x=np.array([a['maxima'] for a in rr]);p=np.array([a['notNA']/a['n'] for a in rr]) if f['adjust'] else np.ones(len(x));mu,s,q=f['par'];mup=mu+s*(np.log(p) if q==0 else np.expm1(q*np.log(p))/q);sp=s*p**q;cdf=genextreme.cdf(x,c=-q,loc=mup,scale=sp);n=len(x);k=np.arange(1,n+1);model=k/(n+1);lo=beta.ppf(.025,k,n-k+1);hi=beta.ppf(.975,k,n-k+1);ql=genextreme.ppf(lo,c=-q,loc=mu,scale=s);qh=genextreme.ppf(hi,c=-q,loc=mu,scale=s);qm=genextreme.ppf(model,c=-q,loc=mu,scale=s);emp=np.sort(mu+(x-mup)/p**q)
  # Independent closed-form GEV quantile and beta CDF checks.
  direct=lambda a:mu-s*np.log(-np.log(a)) if q==0 else mu+s*np.expm1(-q*np.log(-np.log(a)))/q
  error=max(float(np.max(abs(direct(a)-b))) for a,b in [(lo,ql),(hi,qh),(model,qm)]);betaerr=max(float(np.max(abs(beta.cdf(lo,k,n-k+1)-.025))),float(np.max(abs(beta.cdf(hi,k,n-k+1)-.975))))
  assert error<1e-8 and betaerr<1e-10 and np.all(lo<hi) and np.all(np.diff(emp)>=0)
  configs.append({'dataset':dataset,'remove':f['remove'],'adjust':f['adjust'],'n':n,'model_uniform':model.tolist(),'empirical_uniform':np.sort(cdf).tolist(),'pp_lower':lo.tolist(),'pp_upper':hi.tolist(),'model_gev':qm.tolist(),'empirical_gev':emp.tolist(),'qq_lower':ql.tolist(),'qq_upper':qh.tolist(),'quantile_formula_error':error,'beta_roundtrip_error':betaerr})
result={'configs':configs,'level':.95,'bands':'pointwise beta order-statistic bands with fitted parameters plugged in; not simultaneous or parameter-estimation-adjusted','source':'author-profile-source/evmissing-internal.R:999-1084,1337-1360','source_sha256':'0a174202725cd2ad01050a644e03a89d3a957127a315eff156ffa0c29337f61c','new_fits':0,'rendered':False};out.write_text(json.dumps(result,indent=2)+'\n');print('verified configurations',len(configs),'max beta roundtrip',max(a['beta_roundtrip_error'] for a in configs))
