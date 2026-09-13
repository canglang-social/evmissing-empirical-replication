"""Local profile likelihood and gradient. Inputs p and w are fixed block fractions/weights."""
import numpy as np
L=np.log(-np.log1p(-.01))
def evaluate(v,r,x,p,w):
 sigma=np.exp(v[0]);xi=v[1];d=(x-r)/sigma;E=np.exp(-xi*L);t=E+xi*d
 if not np.isfinite(sigma) or sigma<=0 or np.any(t<=0) or not np.all(np.isfinite(t)):return np.inf,np.array([np.nan,np.nan])
 if abs(xi)<.001 and np.max(np.abs(xi)*(np.abs(d)+abs(L)))<.01:
  # log(1+sum c_k xi^k) coefficients; degree eight before dividing by xi.
  import math
  c=[np.zeros_like(d),d-L]+[np.full_like(d,(-L)**k/math.factorial(k)) for k in range(2,9)]
  b=[np.zeros_like(d)]
  for n in range(1,9):b.append(c[n]-sum((k/n)*b[k]*c[n-k] for k in range(1,n)))
  z=sum(b[k]*xi**(k-1) for k in range(1,9))
  zx=sum((k-1)*b[k]*xi**(k-2) for k in range(2,9));ze=-d/t
 else:
  # Extended precision limits cancellation in the derivative numerator.
  q=np.longdouble(xi);dd=d.astype(np.longdouble);ll=np.longdouble(L)
  ee=np.exp(-q*ll);tt=ee+q*dd;zz=np.log(tt)/q
  z=np.asarray(zz,dtype=float);ze=np.asarray(-dd/tt,dtype=float)
  zx=np.asarray((q*(-ll*ee+dd)/tt-np.log(tt))/q**2,dtype=float)
 A=1+xi-p*np.exp(-z)
 return float(np.sum(w*(v[0]+(1+xi)*z+p*np.exp(-z)-np.log(p)))),np.array([np.sum(w*(1+A*ze)),np.sum(w*(z+A*zx))])
