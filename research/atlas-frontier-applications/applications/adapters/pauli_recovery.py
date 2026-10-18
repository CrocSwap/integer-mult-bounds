#!/usr/bin/env python3
"""Exact deficiency-one binary symplectic spread/Pauli manifest recovery.
Classical finite geometry, applied as a source-independent repair certificate.
No floating point, external libraries, assumed missing class or hardware claim.
"""
import argparse,copy,hashlib,json,os,random
from pathlib import Path

def need(b,msg):
 if not b:raise ValueError(msg)
def basis(vectors):
 d={}
 for a in vectors:
  x=a
  for k in sorted(d,reverse=True):
   if x>>k&1:x^=d[k]
  if x:
   k=x.bit_length()-1
   for j in list(d):
    if d[j]>>k&1:d[j]^=x
   d[k]=x
 return [d[k]for k in sorted(d,reverse=True)]
def span(g):
 out={0}
 for v in g:out|={x^v for x in out}
 return out
def symp(a,b,n):
 m=(1<<n)-1;return (((a&m)&(b>>n)).bit_count()+((b&m)&(a>>n)).bit_count())&1

def check_partial(data):
 n=data['qubits'];need(type(n)is int and 1<=n<=10,'qubits must lie in1..10')
 classes=data['classes'];need(len(classes)==1<<n,'exact deficiency-one class count required')
 used=set();normalized=[]
 for i,g in enumerate(classes):
  need(len(g)==n and all(type(v)is int and 0<v<1<<(2*n)for v in g),'generator dimension/range')
  h=basis(g);need(len(h)==n,'dependent generators')
  need(all(symp(a,b,n)==0 for a in h for b in h),'noncommuting class')
  members=span(h)-{0};need(not used&members,'overlapping classes');used|=members;normalized.append(h)
 return n,normalized,used

def recover(data):
 n,classes,used=check_partial(data)
 holes=set(range(1,1<<(2*n)))-used
 need(len(holes)==(1<<n)-1,'hole cardinality')
 g=basis(sorted(holes));need(len(g)==n and span(g)==holes|{0},'holes do not form a subspace')
 need(all(symp(a,b,n)==0 for a in g for b in g),'hole class is not isotropic')
 # Full independent endpoint certificate: the returned class partitions all labels.
 full=classes+[g];covered=set()
 for h in full:
  s=span(h)-{0};need(not covered&s,'full partition collision');covered|=s
 need(covered==set(range(1,1<<(2*n))),'incomplete full endpoint')
 return dict(status='PASS_EXACT_UNIQUE_MISSING_PAULI_CLASS',qubits=n,hilbert_dimension=1<<n,retained_class_count=len(classes),completed_class_count=len(full),nonidentity_paulis=len(covered),missing_generators=g,missing_labels=sorted(holes),projector_recipe='For each sign vector b in{0,1}^n use 2^-n product_j(I+(-1)^b_j P(g_j)); P(x,z)=i^popcount(x&z) X^x Z^z. All outcomes are rank-one and distinct classes are mutually unbiased.',recovered_unique=True)

def mod(a,b):
 while a.bit_length()>=b.bit_length():a^=b<<(a.bit_length()-b.bit_length())
 return a
def gcd(a,b):
 while b:a,b=b,mod(a,b)
 return a
def mul(a,b,poly,n):
 s=0
 while b:
  if b&1:s^=a
  b>>=1;a<<=1
  if a>>n:a^=poly
 return s
def irreducible(poly,n):
 x=mod(2,poly);z=x
 for k in range(1,n+1):
  z=mul(z,z,poly,n)
  if k<=n//2 and gcd(z^x,poly)!=1:return False
 return z==x

def construct(n,seed):
 need(1<=n<=8,'fixture construction supports1..8qubits')
 poly=next(p for p in range((1<<n)|1,1<<(n+1),2)if irreducible(p,n))
 def tr(x):
  t=0
  for _ in range(n):t^=x;x=mul(x,x,poly,n)
  need(t in(0,1),'field trace escaped base field');return t
 G=[[tr(mul(1<<i,1<<j,poly,n))for j in range(n)]for i in range(n)]
 need(len(basis([sum(G[i][j]<<i for i in range(n))for j in range(n)]))==n,'degenerate trace pairing')
 def dual(x):return sum((sum(G[i][j]*((x>>j)&1)for j in range(n))&1)<<i for i in range(n))
 classes=[[((1<<i)|(dual(mul(m,1<<i,poly,n))<<n))for i in range(n)]for m in range(1<<n)]
 classes.append([1<<(n+i)for i in range(n)])
 rng=random.Random(seed);transvections=[rng.randrange(1,1<<(2*n))for _ in range(2*n+5)]
 def gauge(x):
  for v in transvections:
   if symp(x,v,n):x^=v
  return x
 classes=[basis([gauge(v)for v in g])for g in classes]
 return classes,dict(polynomial_binary=poly,trace_gram=G,gauge_seed=seed,gauge_transvections=transvections)

def pauli(v,n):
 x=v&((1<<n)-1);z=v>>n
 return ''.join('Y'if x>>i&1 and z>>i&1 else'X'if x>>i&1 else'Z'if z>>i&1 else'I'for i in range(n))

def fixture(out):
 need(not out.exists(),'output exists');out.mkdir(parents=True)
 n=6;classes,construction=construct(n,20261015);missing=22
 data=dict(schema='pauli-deficiency-one/1',qubits=n,classes=classes[:missing]+classes[missing+1:])
 result=recover(data);need(set(result['missing_labels'])==span(classes[missing])-{0},'wrong erased endpoint')
 # Every possible one-class erasure is recovered, in the transformed gauge.
 for k in range(len(classes)):
  d=dict(qubits=n,classes=classes[:k]+classes[k+1:]);r=recover(d)
  need(set(r['missing_labels'])==span(classes[k])-{0},'all-erasure regression')
 # Boundary dimension1 and several independently generated nontrivial dimensions.
 boundary=[]
 for m in range(1,6):
  cs,_=construct(m,441+m);recover(dict(qubits=m,classes=cs[:-1]));boundary.append(m)
 mutations={}
 bad=copy.deepcopy(data);bad['classes'].pop();mutations['two_missing']=bad
 bad=copy.deepcopy(data);bad['classes'][1]=bad['classes'][0];mutations['duplicate_class']=bad
 bad=copy.deepcopy(data);bad['classes'][0][0]=1<<(2*n);mutations['out_of_range']=bad
 bad=copy.deepcopy(data);bad['classes'][0][1]=bad['classes'][0][0];mutations['dependent_generators']=bad
 bad=copy.deepcopy(data);bad['qubits']=0;mutations['invalid_dimension']=bad
 bad=copy.deepcopy(data);g=bad['classes'][0];a=g[0];v=next(x for x in range(1,1<<(2*n))if symp(a,x,n));g[1]=v;mutations['noncommuting_class']=bad
 controls={}
 for name,bad in mutations.items():
  try:recover(bad)
  except ValueError as e:controls[name]=str(e)
  else:raise AssertionError('accepted corruption:'+name)
 result.update(all_65_erasure_positions_passed=True,boundary_dimensions_passed=boundary,negative_controls=controls,construction=construction)
 (out/'INPUT.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
 (out/'RECOVERY.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
 full=dict(qubits=n,classes=classes,projector_recipe=result['projector_recipe'])
 (out/'FULL-MEASUREMENT.json').write_text(json.dumps(full,indent=2)+'\n',encoding='utf-8',newline='\n')
 lines=['class,label,pauli']
 for k,g in enumerate(classes):
  for v in sorted(span(g)-{0}):lines.append(f'{k},{v},{pauli(v,n)}')
 (out/'PAULI-PARTITION.csv').write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
 manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in out.iterdir()if p.is_file()}
 (out/'MANIFEST.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
 print(json.dumps({k:v for k,v in result.items()if k not in('missing_labels','construction')},indent=2))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path);ap.add_argument('--out',required=True,type=Path);ap.add_argument('--make-fixture',action='store_true');a=ap.parse_args()
 lock=Path(str(a.out)+'.lock');lock.parent.mkdir(parents=True,exist_ok=True);fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
 try:
  if a.make_fixture:fixture(a.out)
  else:
   need(a.input is not None,'--input required');before=hashlib.sha256(a.input.read_bytes()).hexdigest();d=json.loads(a.input.read_text(encoding='utf-8'));r=recover(d);r['input_sha256']=before
   need(hashlib.sha256(a.input.read_bytes()).hexdigest()==before,'input changed');need(not a.out.exists(),'output exists');a.out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n');print(r['status'])
 finally:os.close(fd);lock.unlink()
if __name__=='__main__':main()
