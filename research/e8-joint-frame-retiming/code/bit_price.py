"""Exact price of the emitted bit program; no histogram supplied by discovery."""
import json,importlib.util
from fractions import Fraction as Q
from pathlib import Path

def load(name):
 p=Path('work/pr361/code/engines')/(name+'.py');sp=importlib.util.spec_from_file_location('price_'+name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
p=Path('bit426-source-centres/global');g=json.loads((p/'GLOBAL.json').read_text());a=json.loads((p/'AUDIT.json').read_text())
assert a['template_sha256']==g['template_sha256']
H={int(r):n for r,n in a['profile'].items()};m,W=g['m'],g['live']
M,B=load('moment'),load('base_two_moment');root=M.certify(H,m,W,True);lo,hi=Q(root['lower']),Q(root['upper'])
fb=32*m*m*sum(H.values())
def other(x):
 l,u=B.moment(m,W,list(H.items()),x);a,b=B.moment(m,W,[(1,fb)],x);return l+a/10**16,u+b/10**16
assert other(lo)[1]<1<other(hi)[0]
root.update(source_template_sha256=g['template_sha256'],two_exact_engines=True)
Path('BIT-PRICE.json').write_text(json.dumps(root,indent=2)+'\n')
print('PASS two rational bit moments',root['lower'])
