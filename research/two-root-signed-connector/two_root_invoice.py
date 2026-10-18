import json,importlib.util,re
from pathlib import Path
spec=importlib.util.spec_from_file_location('v',str(Path(__file__).with_name('two_root_verify.py')));v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
lengths=[2,3,4,5,6,7];factors={};n=0
for label,k in zip(['B0','B1','B2','A0','A1','A2'],lengths):factors[label]=list(range(n,n+k));n+=k

def inverse(word):return [(kind,f,p,q,-s) for kind,f,p,q,s in reversed(word)]
def product(fs,p,q,scratch):
 if len(fs)==1:return [('F',fs[0],p,q,1)]
 mid=len(fs)//2;w=scratch[0]
 a=product(fs[:mid],p,w,scratch[1:]);b=product(fs[mid:],w,q,scratch[1:]);return a+b+inverse(a)+inverse(b)
def compile(short):
 out=[]
 for k,i,s,r in short:
  if k=='R':out.append(('R',i,7,6,s));continue
  if k=='S':out.append(('S',i,6,6,s));continue
  p,q=(i,6+r) if k=='B' else (6+r,3+i)
  sub=product(factors[k+str(i)],p,q,[8,9,10]);out.extend(sub if s==1 else inverse(sub))
 return out
# Exact chronological predecessor words copied from the pinned READMEs.
old14=[('B',0,-1,0),('B',0,-1,0),('A',2,-1,0),('B',0,1,0),('B',1,-1,0),('A',1,-1,0),('A',2,1,0),('B',2,-1,0),('A',0,-1,0),('B',0,1,0),('B',1,1,0),('A',1,1,0),('B',2,1,0),('A',0,1,0)]
# PR1526 replaces adjacent equal B0- calls by H B0- D, on the same valid word.
old13=[('S',-1,1,0),('B',0,-1,0),('S',1,1,0)]+old14[2:]
words={'old14':compile(old14),'dyadic13':compile(old13),'two_root12':compile(v.WORD)}

def invoice(word,L,compact=False):
 pos=0;out=dict(head_moves=0,coefficient_reads=0,source_reads=0,target_reads=0,target_writes=0,multiplications=0,dyadic_ops=0,additions=0,instructions=len(word),admission_reads=(10 if compact else 11)*L+27*L*L)
 def visit(a):
  nonlocal pos
  out['head_moves']+=abs(a-pos);pos=a
 for kind,f,p,q,s in word:
  if compact:
   p=p-1 if p>=8 else p; q=q-1 if q>=8 else q
  if kind=='F':
   for a in range(L):
    for b in range(L):
     visit((10 if compact else 11)*L+f*L*L+a*L+b);visit(p*L+b);visit(q*L+a)
     for name in ('coefficient_reads','source_reads','target_reads','target_writes','multiplications','additions'):out[name]+=1
  elif kind=='R':
   for a in range(L):
    visit(p*L+a);visit(q*L+a)
    for name in ('source_reads','target_reads','target_writes','additions'):out[name]+=1
    if abs(f)==2:out['dyadic_ops']+=1
  else:
   for a in range(L):
    visit(q*L+a)
    for name in ('target_reads','target_writes','dyadic_ops'):out[name]+=1
  visit(0)
 return out
def main():
 out=dict(factor_lengths=lengths,factor_counts={k:sum(op[0]=='F' for op in w) for k,w in words.items()},literal_words=words,invoices={str(L):{k:invoice(w,L) for k,w in words.items()} for L in [1,2,3,4,8,16,32,64]})
 for L,inv in out['invoices'].items():
  inv.update({k+'_compact':invoice(w,int(L),True) for k,w in words.items() if k!='two_root12'})
 encoded=json.dumps(out,indent=2)
 encoded=re.sub(r'\[\s*"[FRS]",\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+)\s*\]',lambda m:json.dumps(json.loads(m.group(0))),encoded)
 Path(__file__).with_name('two_root_invoice.json').write_text(encoded+'\n')
 print('PASS_TWO_ROOT_INVOICE',out['factor_counts'])
if __name__=='__main__':main()
