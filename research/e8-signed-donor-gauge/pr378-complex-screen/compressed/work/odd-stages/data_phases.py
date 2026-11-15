"""Exact phases for compressed complex data routes and terminal correction.
All operators here are products of C_q (C_q^2=X_q) and fix |+>.
Their Fourier multipliers are i^(sum sign*parity(q.y)), represented exactly
as a Z4 quadratic polynomial. This includes the global phase, not just Paulis.
"""
import json,gzip,hashlib,random
from pathlib import Path
from clifford_exact import rank,mv,transpose,parity
H=9;M=73;K=4;L=9
def normal(terms,m=M):
 lin=[0]*m;B=[0]*m
 for q,sgn in terms:
  for i in range(m):
   if q>>i&1:lin[i]=(lin[i]+sgn)%4;B[i]^=q
 return tuple(lin),tuple(B)
def shift_adapter(actual,wanted):
 a,A=normal(actual);b,B=normal(wanted);assert A==B
 delta=[(v-u)%4 for u,v in zip(a,b)];assert all(x in (0,2) for x in delta)
 return sum((x//2)<<i for i,x in enumerate(delta))
def basis(q):
 j=0 if not(q&1) else next(i for i in range(1,H) if not(q>>i&1));w=q^(1<<j);cols=[]
 for z in range(H):
  i=j if z==0 else 0 if z==j else z;x=1<<i
  cols.append(x^w if parity(x&w) else x)
 assert cols[0]==q and all(parity(x&y)==(i==j) for i,x in enumerate(cols) for j,y in enumerate(cols))
 return cols+[1<<i for i in range(H,M)]
def rho(q,stage):
 rows=[1<<i for i in range(M)]
 if stage:
  cols=basis(q);off=H+(stage-1)*8
  for i in range(H):rows[i]=(q if q>>i&1 else 0)|sum(((cols[j+1]>>i)&1)<<(off+j) for j in range(8))
  for j in range(8):rows[off+j]=cols[j+1]
 assert transpose(rows,M)==tuple(rows) and all(mv(rows,mv(rows,1<<j))==1<<j for j in range(M))
 return tuple(rows)
def stage_frame(q,s,kind):
 terms={'P':[(q,1)],'H':[(1<<i,1) for i in range(H)],'0':[],'K':[(1<<i,1) for i in range(H)]+[(q,-1)]}[kind]
 terms += [(1<<i,1) for i in range(H,H+8*s)];d=rho(q,s)
 return [(mv(d,x),sgn) for x,sgn in terms]
def desired(q,s,kind):
 if s<0:return [(q,1)] if kind=='X' else []
 return [(1<<i,1) for i in range(H+8*s)]+([] if kind=='X' else [(q,-1)])
def diff(a,b):return [(q,-s) for q,s in a]+b
def exact_child(q,a,b):
 want=diff(a,b);lin,B=normal(want);cols=[x for x in basis(q) if mv(B,x)==x]
 assert len(cols)==rank(B) and all(mv(B,x) in (0,x) for x in basis(q))
 actual=[(x,1) for x in cols];delta=shift_adapter(actual,want)
 # Multiply the exact rank-zero translation X_delta after the child.
 a0,A=normal(actual);w0,W=normal(want)
 assert A==W and all((a0[i]+2*((delta>>i)&1))%4==w0[i] for i in range(M))
 return dict(rank=len(cols),orthogonal_axes=cols,translation_after=delta)
def run():
 c=json.load(gzip.open('work/pr361/complex/gcert1-e8-r783.json.gz'));ports=[];nonzero=0;idle=[]
 for p,q in enumerate(c['ports']):
  align=[]
  for s in range(L):
   z={}
   for name,kind,previous in [('entry_X','P',s-1),('entry_Y','0',s-1),('exit_X','H',s),('exit_Y','K',s)]:
    canon=desired(q,previous,'X' if name.endswith('X') else 'Y');raw=stage_frame(q,s,kind)
    delta=shift_adapter(canon,raw) if name.startswith('entry') else shift_adapter(raw,canon)
    z[name]=delta;nonzero+=bool(delta)
   align.append(z)
  children=[]
  for j in range(1,K):
   for side in ['X','Y']:
    children.append(exact_child(q,desired(q,-1,side),desired(q,2*j-1,side)))
    children.append(exact_child(q,desired(q,2*j-1,side),desired(q,2*j,side)))
  for j in range(1,K+1):
   for side in ['X','Y']:children.append(exact_child(q,desired(q,2*j,side),desired(q,8,side)))
  # After the signed scalar exchange, the incoming X contributes C_q^{-2}.
  # X_q is essential: C_q^2=X_q, so X_q*C_q^{-2}=I exactly.
  terminal=diff([(q,1)],desired(q,8,'Y'));lin,B=normal(terminal);full=[(1<<i,1) for i in range(M)]
  assert shift_adapter(terminal,full)==q
  assert normal(terminal)!=normal(full)
  ports.append(dict(port=p,q=q,stage_alignment=align,idle_children=children,terminal_Y_translation=q))
 # Independently evaluate the Z4 polynomial on all 512 binary arguments.
 rng=random.Random(73120);polynomial_checks=0
 for _ in range(80):
  terms=[(rng.randrange(1,1<<H),rng.choice([-1,1])) for _ in range(20)];lin,B=normal(terms,H)
  for y in range(1<<H):
   lhs=sum(s*parity(q&y) for q,s in terms)%4
   rhs=(sum(lin[i] for i in range(H) if y>>i&1)+2*sum(parity((B[i]>>(i+1))&(y>>(i+1))) for i in range(H) if y>>i&1))%4
   assert lhs==rhs;polynomial_checks+=1
 cover=[]
 for n in range(1,6):
  odd=[x for x in range(1,1<<n) if parity(x)];mats=[]
  def enum(rows):
   if len(rows)==n:mats.append(tuple(rows));return
   for x in odd:
    if all(not parity(x&y) for y in rows):enum(rows+[x])
  enum([]);nonzero_cover=0
  for g in mats:
   cols=transpose(g,n);a,A=normal([(x,1) for x in cols],n);delta=sum((((row.bit_count()-1)//2)&1)<<i for i,row in enumerate(g));nonzero_cover+=bool(delta)
   assert A==tuple(1<<i for i in range(n))
   assert all((a[i]+2*((delta>>i)&1))%4==1 for i in range(n))
  cover.append(dict(n=n,orthogonal_matrices=len(mats),nonzero_full_kernel_corrections=nonzero_cover))
 out=dict(status='PASS_EXACT_Z4_DATA_ROUTE_IDLE_AND_TERMINAL_PHASES',m=M,ports=len(ports),nonzero_stage_alignment_translations=nonzero,terminal_omission_controls_rejected=len(ports),exact_phase_polynomial_evaluations=polynomial_checks,recipes=ports,cover_correction=dict(formula='delta(g)_i = (weight(row_i(g))-1)/2 mod 2; apply X_delta(g) to EVERY final live stream in cover class g.',reason='P_g C_all P_g^-1 = C_all X_delta(g) exactly. Orthogonality cancels all quadratic cross terms; both sides fix the uniform vector.',mandatory=True,complete_small_cover_checks=cover),global_phase_argument='Every C_q and every linear address permutation fixes the uniform vector. Equality of the exact Z4 Fourier multiplier therefore fixes the scalar phase as well.',scope='All compressed data boundary operators, idle children, terminal X_q and all-live cover correction. Internal arbitrary-subspace canonical labels are checked separately.')
 Path('work/complex-nine-native/DATA-PHASES.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k!='recipes'},flush=True)
if __name__=='__main__':run()
