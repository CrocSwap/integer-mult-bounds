import itertools,subprocess,json

def spans(n):
 seen={frozenset([0])};todo=list(seen)
 for s in todo:
  for x in range(1,1<<n):
   t=s|{a^x for a in s}
   if t not in seen:seen.add(t);todo.append(t)
 return sorted(seen,key=lambda s:(len(s),sorted(s)))

def decode(x):
 s={0};n=int(x,16)
 while n:
  a=n&511;n>>=9;s|={x^a for x in s}
 return frozenset(s)

def expected(D,c,d,spaces):
 pairs=[(a,b) for a in spaces for b in spaces if len(a)<=2**c and len(b)<=2**d and D<=a|b]
 return {(a,b) for a,b in pairs if not any(x<=a and y<=b and (x!=a or y!=b) for x,y in pairs)}

def run(binary):
 spaces=spans(3);cases=[]
 for mask in range(128):
  for c in range(4):
   for d in range(4):cases.append((mask,c,d))
 req='7\n1 2 3 4 5 6 7\n'+''.join(f'0 {m:x} {c} {d}\n' for m,c,d in cases)
 p=subprocess.run([binary],input=req,text=True,capture_output=True,check=True)
 if len(p.stdout.splitlines())!=len(cases):raise ValueError('incomplete output')
 for (m,c,d),line in zip(cases,p.stdout.splitlines()):
  tok=line.split();actual={(decode(a),decode(b)) for a,b in (t.split(':') for t in tok[1:])}
  want=expected({i+1 for i in range(7) if m>>i&1},c,d,spaces)
  if int(tok[0])!=len(actual) or actual!=want:raise ValueError(f'mismatch {m,c,d}, expected {want}, actual {actual}')
 return len(cases)
if __name__=='__main__':
 import sys;print('PASS independent explicit-subspace cases',run(sys.argv[1]))
