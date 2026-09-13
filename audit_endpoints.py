import sys,json,time,hashlib
from decimal import Decimal as D,localcontext
from general_curvature import evaluate as precise,local_acceptance
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.stats import chi2,genextreme
import gev_profile_math as math
import argparse
parser=argparse.ArgumentParser();parser.add_argument('dataset',choices=['plymouth','brest']);parser.add_argument('--input',type=Path,required=True);parser.add_argument('--fit',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--resume',type=Path);args=parser.parse_args()
root=Path(__file__).parent;out=args.output
if out.exists():raise RuntimeError('no retry')
fit=json.loads(args.fit.read_text());annual=json.loads(args.input.read_text())['annual'];t0=time.monotonic();c0=time.process_time();calls=0;report={'status':'running','checks':[]}
prior_calls=prior_cpu=prior_wall=0;done=set()
if args.resume:
 prior=json.loads(args.resume.read_text());assert args.dataset=='brest' and prior['status']=='stopped' and prior.get('error')=="RuntimeError('cap')" and len(prior['checks'])==42 and all(c['pass'] for c in prior['checks'])
 report['checks']=prior['checks'];done={(c['condition'],c['T'],c['side'],c['start_index']) for c in prior['checks']};prior_calls=prior['objective_evaluations'];prior_cpu=prior['cpu_seconds'];prior_wall=prior['wall_seconds'];report['prior_receipt_sha256']=hashlib.sha256(args.resume.read_bytes()).hexdigest()
def count():
 global calls
 calls+=1
 if calls>(1000 if args.resume else 5000) or time.process_time()-c0>(3 if args.resume else 15) or time.monotonic()-t0>(10 if args.resume else 30):raise RuntimeError('cap')
def obj(v,r):
 count();return math.evaluate(v,r,x,p,w)
def sup(v,r):
 s=np.exp(v[0]);xi=v[1];d=(x-r)/s;E=np.exp(-xi*math.L);return E+xi*d-1e-10
def jac(v,r):
 s=np.exp(v[0]);xi=v[1];d=(x-r)/s;E=np.exp(-xi*math.L);return np.column_stack([-xi*d,-math.L*E+d])
def curvature(v, r):
    with localcontext() as ctx:
        ctx.prec = 80
        eta, q = map(lambda a: D(str(a)), v)
        rd = D(str(r))
        ld = (-(D(1)-D(1)/D(str(T))).ln()).ln()
        xs = list(map(lambda a: D(str(a)), x))
        ps = list(map(lambda a: D(str(a)), p))
        ws = list(map(lambda a: D(str(a)), w))

        def f(a, b):
            count()
            return precise(a, b, rd, xs, ps, ws, ld, False)[0]
        count()
        val, g, Hd = precise(eta, q, rd, xs, ps, ws, ld)
        H = np.array(Hd, dtype=float)
        try:
            C = np.linalg.cholesky(H)
        except np.linalg.LinAlgError:
            return {'pass': False, 'reason': 'nonpositive_hessian'}
        checks = []
        for h in [D('1e-10'), D('5e-11')]:
            a = (f(eta + h, q) - 2 * val + f(eta - h, q)) / h ** 2
            b = (f(eta, q + h) - 2 * val + f(eta, q - h)) / h ** 2
            c = (f(eta + h, q + h) - f(eta + h, q - h) - f(eta - h, q + h) + f(eta - h, q - h)) / (4 * h * h)
            diff = np.array([[float(a - Hd[0][0]), float(c - Hd[0][1])], [float(c - Hd[1][0]), float(b - Hd[1][1])]])
            white = np.linalg.solve(C, np.linalg.solve(C, diff).T).T
            checks.append(float(np.linalg.norm(white, 2)))
        count()
        local = local_acceptance(eta, q, rd, xs, ps, ws, ld, f)
        return {'pass': bool(local['pass'] and max(checks) <= 0.001), 'scaled_curvature_errors': checks, 'local': local, 'gradient': list(map(str, g)), 'hessian': [[str(a) for a in row] for row in Hd]}
try:
 for ci,condition in enumerate(fit['conditions']):
  rows=[r for r in annual if r['maxima'] is not None and (not condition['remove'] or r['year'] not in ([2001,2006] if args.dataset=='plymouth' else [1857,1859,1944,1952]))];x=np.array([r['maxima'] for r in rows]);p=np.array([r['notNA']/r['n'] for r in rows]) if condition['adjust'] else np.ones(len(x));w=np.ones(len(x));threshold=condition['nll']+chi2.ppf(.95,1)/2
  for prof in condition['profiles']:
   T=prof['T'];math.L=np.log(-np.log1p(-1/T))
   for side,r in zip(['lower','upper'],prof['interval']):
    near=min(prof['evaluations'],key=lambda q:abs(q['r']-r));a=near['nuisance'];g=[max(condition['par'][1],abs(r-np.median(x))/4),0.]
    for index,start in enumerate([a,g]):
     if (ci,T,side,index) in done:continue
     v=np.array([np.log(start[0]),start[1]]);assert np.all(sup(v,r)>0)
     o=minimize(lambda v:obj(v,r),v,jac=True,method='SLSQP',constraints=[{'type':'ineq','fun':lambda v:sup(v,r),'jac':lambda v:jac(v,r)}],options={'ftol':1e-12,'maxiter':500})
     val,grad=obj(o.x,r);s=np.exp(o.x[0]);xi=o.x[1];mu=r+s*math.L if xi==0 else r-s*np.expm1(-xi*math.L)/xi;mus=mu+s*np.log(p) if xi==0 else mu+s*np.expm1(xi*np.log(p))/xi;count();ind=float(-np.sum(genextreme.logpdf(x,c=-xi,loc=mus,scale=s*p**xi)));minimum=float(np.min(sup(o.x,r)+1e-10));local=curvature(o.x,r);passed=bool(abs(val-threshold)<=.001 and abs(val-near['nll'])<=1e-4 and local['pass'] and minimum>1e-6 and abs(val-ind)<=1e-7)
     report['checks'].append({'condition':ci,'start_log_scale_shape':v.tolist(),'local_curvature':local,'T':T,'side':side,'endpoint':r,'start_index':index,'returned_parameters':{'sigma':float(s),'xi':float(xi),'mu':float(mu)},'nll':val,'threshold_residual':val-threshold,'gradient_max':float(max(abs(grad))),'independent_density_error':abs(val-ind),'min_support':minimum,'pass':passed,'success_flag':bool(o.success),'message':str(o.message)})
 report['status']='passed' if len(report['checks'])==48 and all(c['pass'] for c in report['checks']) else 'failed'
except Exception as e:report['status']='stopped';report['error']=repr(e)
finally:
 report['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();report['cumulative_resources']={'calls':prior_calls+calls,'cpu_seconds':prior_cpu+time.process_time()-c0,'wall_seconds':prior_wall+time.monotonic()-t0};report.update(cpu_seconds=time.process_time()-c0,wall_seconds=time.monotonic()-t0,objective_evaluations=calls);out.write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='checks'}));print('checks',len(report['checks']),'failed',[c for c in report['checks'] if not c['pass']])
