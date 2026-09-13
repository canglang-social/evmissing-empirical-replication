import sys
import numpy as np
from scipy.optimize import minimize,brentq
from scipy.stats import genextreme,chi2
import json,time,hashlib
from pathlib import Path
import argparse
parser=argparse.ArgumentParser();parser.add_argument('dataset',choices=['plymouth','brest']);parser.add_argument('--input',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
root=Path(__file__).parent;out=args.output;out.parent.mkdir(parents=True,exist_ok=True)
if out.exists():raise RuntimeError('Existing run receipt: do not overwrite or reset budget')
t0=time.monotonic();c0=time.process_time();calls=0
report={'dataset':args.dataset,'status':'running','conditions':[],'versions':{'numpy':np.__version__}}
import scipy
report['versions']['scipy']=scipy.__version__
def nll(par,x,p):
 global calls
 calls+=1
 if calls>200000 or time.process_time()-c0>30 or time.monotonic()-t0>60:raise RuntimeError('budget exhausted')
 mu,sigma,xi=par
 if sigma<=0 or not np.all(np.isfinite(par)):return np.inf
 y=(x-mu)/sigma;q=1+xi*y
 if np.any(q<=0):return np.inf
 z=y if abs(xi)<1e-10 else np.log1p(xi*y)/xi
 with np.errstate(over='ignore',invalid='ignore'):
  ans=np.sum(np.log(sigma)+(1+xi)*z+p*np.exp(-z)-np.log(p))
 return float(ans) if np.isfinite(ans) else np.inf
def ret(par,T):
 mu,s,xi=par;l=np.log(-np.log1p(-1/T))
 return float(mu-s*l if abs(xi)<1e-10 else mu+s*np.expm1(-xi*l)/xi)
def mu_from(r,s,xi,T):return r-ret((0,s,xi),T)
def hessian(par,x,p,factor):
 h=np.array([max(1,abs(par[0]))*1e-5,max(1,par[1])*1e-5,1e-5])*factor
 H=np.zeros((3,3));f=nll(par,x,p)
 for i in range(3):
  ei=np.eye(3)[i]*h[i];H[i,i]=(nll(par+ei,x,p)-2*f+nll(par-ei,x,p))/h[i]**2
  for j in range(i):
   ej=np.eye(3)[j]*h[j];H[i,j]=H[j,i]=(nll(par+ei+ej,x,p)-nll(par+ei-ej,x,p)-nll(par-ei+ej,x,p)+nll(par-ei-ej,x,p))/(4*h[i]*h[j])
 if np.min(np.linalg.eigvalsh(H))<=0:raise RuntimeError('nonpositive Hessian')
 return np.sqrt(np.diag(np.linalg.inv(H))).tolist()
def run():
 rows=json.loads(args.input.read_text())['annual']
 errs=[]
 for xi in [-.3,0,.25]:
  par=(120,30,xi);x=np.array([88.,120.,170.]);p=np.array([.14,.5,1.])
  muc=par[0]+par[1]*(np.log(p) if xi==0 else np.expm1(xi*np.log(p))/xi);sc=par[1]*p**xi
  expected=-np.sum(genextreme.logpdf(x,c=-xi,loc=muc,scale=sc));errs.append(abs(nll(par,x,p)-expected))
 assert max(errs)<1e-10
 report['fixed_density_max_abs_error']=max(errs)
 for remove in [False,True]:
  for adjust in [True,False]:
   rr=[r for r in rows if r['maxima'] is not None and (not remove or r['year'] not in ([2001,2006] if args.dataset=='plymouth' else [1857,1859,1944,1952]))];x=np.array([r['maxima'] for r in rr]);p=np.array([r['notNA']/r['n'] for r in rr]) if adjust else np.ones(len(rr))
   q1,med,q3=np.quantile(x,[.25,.5,.75]);s=(q3-q1)/np.log(np.log(4)/np.log(4/3));mu=med-s*np.log(1/np.log(2))
   result={'remove':remove,'adjust':adjust,'starts':[],'profiles':[]};report['conditions'].append(result)
   fits=[]
   for requested_xi in [0,-.2,.2]:
    xi=max(requested_xi,-.5*s/(max(x)-mu)) if requested_xi<0 else min(requested_xi,.5*s/(mu-min(x))) if requested_xi>0 else 0
    start=[mu,s,xi]
    if not np.isfinite(nll(start,x,p)):result['starts'].append({'start':start,'status':'invalid_support'});continue
    fit=minimize(nll,start,args=(x,p),method='Nelder-Mead',options={'maxfev':5000,'xatol':1e-8,'fatol':1e-9})
    result['starts'].append({'start':start,'par':fit.x.tolist(),'nll':float(fit.fun),'success':bool(fit.success),'nfev':fit.nfev,'message':str(fit.message)})
    if fit.success:fits.append(fit)
   if len(fits)!=3:raise RuntimeError('Not all three starts converged')
   best=min(fits,key=lambda f:f.fun)
   if max(f.fun for f in fits)-best.fun>1e-5:raise RuntimeError('material start disagreement')
   par=best.x;result['par']=par.tolist();result['nll']=float(best.fun)
   result['se']=hessian(par,x,p,1);result['se_half_step']=hessian(par,x,p,.5)
   if max(abs(np.array(result['se'])-result['se_half_step']))>1e-3:raise RuntimeError('Hessian step instability')
   for T in [25,50,100]:
    r0=ret(par,T);prof={'T':T,'estimate':r0,'evaluations':[]};result['profiles'].append(prof);target=best.fun+chi2.ppf(.95,1)/2
    def profile(r):
     def fn(v):return nll((mu_from(r,v[0],v[1],T),v[0],v[1]),x,p)
     initial=par[1:].copy()
     if not np.isfinite(fn(initial)):initial[1]=0.
     f=minimize(fn,initial,method='Nelder-Mead',options={'maxfev':5000,'xatol':1e-7,'fatol':1e-8})
     prof['evaluations'].append({'r':float(r),'nll':float(f.fun),'nuisance':f.x.tolist(),'success':bool(f.success),'nfev':f.nfev})
     if not f.success or not np.isfinite(f.fun) or f.fun<best.fun-1e-5:raise RuntimeError('profile failure or superior branch')
     return float(f.fun-target)
    if profile(r0)>=0:raise RuntimeError('profile center failure')
    ends=[]
    for direction in [-1,1]:
     step=par[1]/2
     for j in range(20):
      edge=r0+direction*step
      if profile(edge)>0:break
      step*=1.6
     else:raise RuntimeError('profile bracket unavailable')
     lo,hi=sorted([r0,edge]);v=brentq(profile,lo,hi,xtol=1e-5,maxiter=50);res=profile(v)
     if abs(res)>.001:raise RuntimeError('profile residual')
     ends.append(float(v))
    prof['interval']=ends
   print('completed',remove,adjust,result['par'],flush=True)
 report['status']='completed'
try:run()
except Exception as e:
 report['status']='stopped';report['error']=repr(e)
finally:
 report['objective_evaluations']=calls;report['cpu_seconds']=time.process_time()-c0;report['wall_seconds']=time.monotonic()-t0;report['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','objective_evaluations','cpu_seconds','wall_seconds']}));print(report.get('error',''))
