"""Decimal derivatives in fixed (log scale, shape) coordinates, fixed p and w."""
from decimal import Decimal as D

def evaluate(eta,q,r,xs,ps,ws,l,derivatives=True):
 s=eta.exp();E=(-q*l).exp();f=g0=g1=h00=h01=h11=D(0)
 for x,p,w in zip(xs,ps,ws):
  d=(x-r)/s;t=E+q*d
  if t<=0:raise ValueError('support')
  if q==0:
   z=d-l;ze=-d;zq=l*d-d*d/2;zee=d;zeq=-l*d+d*d;zqq=l*l*d-2*l*d*d+2*d*d*d/3
  else:
   logt=t.ln();z=logt/q
   if derivatives:
    u=(-l*E+d)/t;ze=-d/t;zq=(q*u-logt)/q**2;zee=d*E/t**2;zeq=d*(-l*E+d)/t**2;zqq=(l*l*E/t-u*u)/q-2*u/q**2+2*logt/q**3
  b=p*(-z).exp();a=1+q-b;f+=w*(eta+(1+q)*z+b-p.ln())
  if derivatives:
   g0+=w*(1+a*ze);g1+=w*(z+a*zq);h00+=w*(b*ze*ze+a*zee);h01+=w*(ze+b*ze*zq+a*zeq);h11+=w*(2*zq+b*zq*zq+a*zqq)
 return f,[g0,g1],[[h00,h01],[h01,h11]]

def local_acceptance(eta,q,r,xs,ps,ws,l,objective):
 """Local Newton checks only; independent curvature validation is separately required."""
 value,g,H=evaluate(eta,q,r,xs,ps,ws,l)
 a,b,c=H[0][0],H[0][1],H[1][1];det=a*c-b*b
 if a<=0 or det<=0:return {'pass':False,'reason':'nonpositive_hessian'}
 step=[-(c*g[0]-b*g[1])/det,-(a*g[1]-b*g[0])/det]
 predicted=-(g[0]*step[0]+g[1]*step[1])/2
 try:improvements=[value-objective(eta+k*step[0],q+k*step[1]) for k in [D(1),D('.5')]]
 except (ValueError,ArithmeticError):return {'pass':False,'reason':'infeasible_newton_step'}
 ok=0<=predicted<=D('1e-6') and all(v<=D('1e-6') for v in improvements)
 return {'pass':bool(ok),'predicted_improvement':str(predicted),'actual_improvements':list(map(str,improvements)),'step':list(map(str,step))}
