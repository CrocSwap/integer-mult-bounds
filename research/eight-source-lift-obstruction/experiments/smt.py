import sys,json,time
sys.path.insert(0,str(__import__('pathlib').Path(__file__).parent/'deps'))
import z3
n=8;L=28
s=z3.Solver();s.set(timeout=180000)
q=[z3.BitVec('q'+str(i),n) for i in range(L)]+[z3.BitVecVal(0,n)]
s.add(q[0]==0)
edges=[[q[t]^q[t+1]==(1<<j) for j in range(n)] for t in range(L)]
for es in edges:s.add(z3.Or(es))
for j in range(n):s.add(z3.PbEq([(edges[t][j],1) for t in range(L)],4 if j<6 else 2))
# Rotate to an occurrence of the distinguished twice-used coordinate 6.
s.add(edges[0][6])
# Six frequent coordinates can be renamed by first occurrence.
for j in range(1,6):
 for t in range(L):s.add(z3.Implies(edges[t][j],z3.Or([edges[k][j-1] for k in range(t)])))
for d in range(1,1<<n):
 s.add(z3.Or([q[i]^q[j]==d for i in range(L) for j in range(i) if ((i-j)&1)==(d.bit_count()&1)]))
print('built',flush=True);start=time.monotonic();r=s.check()
out={'status':str(r),'seconds':time.monotonic()-start,'version':z3.get_version_string()}
if r==z3.sat:
 m=s.model();states=[m.eval(x).as_long() for x in q[:-1]]+[0]
 out['word']=[(states[t]^states[t+1]).bit_length()-1 for t in range(L)]
else:out['reason']=s.reason_unknown() if r==z3.unknown else 'UNSAT in solver; independent proof certificate not checked'
print(json.dumps(out),flush=True)
