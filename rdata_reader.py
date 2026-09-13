"""Restricted data-only XDR reader; rejects unsupported R types. No R evaluation."""
import bz2, struct, tarfile, json, math, datetime, calendar, hashlib
from pathlib import Path
class Reader:
 def __init__(self,b):
  assert b[:7]==b'RDX3\nX\n';self.b=b;self.i=7;self.refs=[]
  self.header=[self.num() for _ in range(3)];self.encoding=self.take(self.num()).decode()
 def take(self,n):
  assert n>=0 and self.i+n<=len(self.b)
  x=self.b[self.i:self.i+n];self.i+=n;return x
 def num(self):return struct.unpack('>i',self.take(4))[0]
 def obj(self):
  flag=self.num();typ=flag&255
  if typ==254:return None
  if typ==255:
   idx=flag>>8
   if not idx:idx=self.num()
   return self.refs[idx-1]
  if typ==1:
   x={'type':1,'value':self.obj()};self.refs.append(x);return x
  if typ==9:
   n=self.num();return {'type':9,'value':None if n==-1 else self.take(n).decode(self.encoding)}
  attr=None;tag=None
  if typ==2:
   if flag&512:attr=self.obj()
   if flag&1024:tag=self.obj()
   return {'type':2,'attr':attr,'tag':tag,'car':self.obj(),'cdr':self.obj()}
  if typ==238:
   info=self.obj();state=self.obj();at=self.obj()
   assert val(info['car'])=='compact_intseq' and val(info['cdr']['car'])=='base'
   n,start,step=state['value'];assert n==int(n) and 0<=n<1000000
   return {'type':13,'value':[int(start+i*step) for i in range(int(n))],'attr':at}
  if typ not in (10,13,14,16,19):raise ValueError((typ,self.i))
  n=self.num();assert 0<=n<1000000
  if typ in (10,13):v=[float('nan') if x==-2147483648 else x for x in struct.unpack('>'+str(n)+'i',self.take(4*n))]
  elif typ==14:v=list(struct.unpack('>'+str(n)+'d',self.take(8*n)))
  else:v=[self.obj() for _ in range(n)]
  if flag&512:attr=self.obj()
  return {'type':typ,'value':v,'attr':attr}
def val(o):
 if o is None:return None
 if o['type']==1:return val(o['value'])
 if o['type'] in (16,19):return [val(x) for x in o['value']]
 return o['value']
def attrs(o):
 d={};o=o.get('attr')
 while o is not None:d[val(o['tag'])]=val(o['car']);o=o['cdr']
 return d
