"""Exact all-T fixed-capacity packing cap for the local two-release-swap profile.

Adapted from PR3630 check_budget.py, Ross Richardson / OpenAI Codex assistance,
head bcac7fe04b9b7f7f5d3c27d620561f96c4ae5608. Its pattern basis and exact dual
are retained; local invoice changes by 2H3-2H2-2H1. PR3531's source-bound
positive-binomial engine is retained unchanged. No allocation is constructed.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import argparse,hashlib,json,tempfile,types,time
def need(ok,msg):
 if not ok:raise ValueError(msg)
HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,help='Fresh external output directory; default: temporary directory.')
args=parser.parse_args()
OUT=args.out.resolve() if args.out else Path(tempfile.mkdtemp(prefix='retiming-cap-'))
need(OUT!=HERE and HERE not in OUT.parents,'output must be outside package')
need(not args.out or not OUT.exists(),'fresh output directory required')
OUT.mkdir(parents=True,exist_ok=True)
raw=(HERE/'cap-source/binomial.py').read_bytes()
need(hashlib.sha256(raw).hexdigest()=='03eebf2be23cab07e5f9e978980fee7b17e10847da5720c3e4e0adb243e8e4fa', "failed: hashlib.sha256(raw).hexdigest()=='03eebf2be23cab07e5f9e978980fee7b17e10847da5720c3e4e0adb243e8e4fa'")
B=types.ModuleType('positive_binomial_dual');exec(compile(raw,'PR3531/binomial.py','exec'),B.__dict__)
CAPS=(8,16,32,48);WIDTHS=(4,5,6,7,8,9);CAP_TOTAL=(672,448,448,448);INVENTORY=(26,2,18,52,97,213)
L={1:2437,2:724,3:226,4:102,5:20,8:8}
PARENT_L={1:2439,2:726,3:224,4:102,5:20,8:8}
T=740;W=896*T
LITERAL_T=530
LITERAL_BEFORE={1:11757460,2:3463020,3:1102502,4:486540,5:103690,8:38160,48:202828}
LITERAL=dict(LITERAL_BEFORE)
for r,d in {1:-2,2:-2,3:2}.items():LITERAL[r]+=9*LITERAL_T*d
REALIZED=Q('0.001730394391813963415120')

def solve(a,b):
 n=len(a);z=[[Q(v) for v in row]+[Q(b[i])] for i,row in enumerate(a)]
 for j in range(n):
  k=next(k for k in range(j,n) if z[k][j]);z[j],z[k]=z[k],z[j];q=z[j][j];z[j]=[x/q for x in z[j]]
  for k in range(n):
   if k!=j:
    q=z[k][j];z[k]=[x-q*y for x,y in zip(z[k],z[j])]
 return [row[-1] for row in z]

patterns=[]
for capacity in CAPS:
 for counts in product(*(range(capacity//width+1) for width in WIDTHS)):
  used=sum(n*w for n,w in zip(counts,WIDTHS))
  if used<=capacity:patterns.append((capacity,counts,capacity-used))
need(len(patterns)==len(set(patterns))==2551, 'failed: len(patterns)==len(set(patterns))==2551')
column=lambda p:[Q(p[0]==capacity) for capacity in CAPS]+list(map(Q,p[1]))
specs=[(8,(8,),Q(672)),(16,(7,9),Q(448)),(32,(9,9,9),Q(57,4)),(32,(7,8,8,9),Q(39,2)),(32,(7,7,9,9),Q(1,4)),(32,(6,8,9,9),Q(162)),(32,(5,9,9,9),Q(18)),(32,(4,9,9,9),Q(234)),(48,(),Q(1531,4)),(48,(9,9,9,9,9),Q(261,4))]
basis=[(cap,tuple(ws.count(w) for w in WIDTHS),cap-sum(ws)) for cap,ws,n in specs];amount=[n for cap,ws,n in specs]
A=list(map(list,zip(*[column(p) for p in basis])));rhs=list(map(Q,CAP_TOTAL))+[Q(9*n) for n in INVENTORY]
need(all(p in patterns for p in basis), 'failed: all(p in patterns for p in basis)')
need([sum(a*n for a,n in zip(row,amount)) for row in A]==rhs, 'failed: [sum(a*n for a,n in zip(row,amount)) for row in A]==rhs')
need(solve(A,rhs)==amount and all(n>0 for n in amount), 'failed: solve(A,rhs)==amount and all(n>0 for n in amount)')
idle=Counter()
for p,n in zip(basis,amount):
 if p[2]:idle[p[2]]+=n*T
ideal=Counter({r:9*T*n for r,n in L.items()});ideal.update(idle)
need(all(Q(n).denominator==1 for n in ideal.values()), 'failed: all(Q(n).denominator==1 for n in ideal.values())');ideal={r:int(n) for r,n in ideal.items()}
need(sum(r*n for r,n in ideal.items())==65088*T, 'failed: sum(r*n for r,n in ideal.items())==65088*T')
need(sum(r*n for r,n in LITERAL.items())==65088*LITERAL_T, 'failed: sum(r*n for r,n in LITERAL.items())==65088*LITERAL_T')

def bracket(profile,stock,digits=24):
 scale=10**digits;a=0;c=scale//100
 need(B.moment(profile,Q(c,scale),stock)[0]>1, 'failed: B.moment(profile,Q(c,scale),stock)[0]>1')
 while c-a>1:
  m=(a+c)//2;lo,hi=B.moment(profile,Q(m,scale),stock)
  if hi<1:a=m
  elif lo>1:c=m
  else:raise ValueError('interval too wide')
 lo=Q(a,scale);hi=Q(c,scale)
 ml=B.moment(profile,lo,stock);mh=B.moment(profile,hi,stock)
 need(ml[1]<1<mh[0], 'failed: ml[1]<1<mh[0]')
 return lo,hi,ml,mh
start=time.time();LO,HI,ml,mh=bracket(ideal,W)
actuallo,actualhi,aml,amh=bracket(LITERAL,896*LITERAL_T)
need(actuallo==REALIZED, 'failed: actuallo==REALIZED')
cache={}
def f(rank,b):
 if rank==0:return Q(0),Q(0)
 if (rank,b) not in cache:cache[rank,b]=tuple(73*x for x in B.moment({rank:1},b,1))
 return cache[rank,b]
dual_symbolic=[solve(list(map(list,zip(*A))),[int(i==j) for i in range(10)]) for j in range(10)]
def coefficients(p):
 a=column(p);out=Counter({p[2]:Q(1)}) if p[2] else Counter()
 for j,bp in enumerate(basis):
  if bp[2]:out[bp[2]]-=sum(x*y for x,y in zip(a,dual_symbolic[j]))
 return {r:n for r,n in out.items() if n}
tight=[];strict=[];ch=hashlib.sha256()
for p in patterns:
 co=coefficients(p);ch.update(json.dumps([p,sorted((r,str(n)) for r,n in co.items())],separators=(',',':')).encode())
 if not co:tight.append(p);continue
 lower=sum(n*f(r,LO if n>0 else HI)[0 if n>0 else 1] for r,n in co.items())
 need(lower>0, 'failed: lower>0')
 strict.append((lower,p))
need((len(tight),len(strict))==(12,2539), 'failed: (len(tight),len(strict))==(12,2539)')
fraclow=actuallo/HI;frachigh=actualhi/LO
result={'status':'PASS_RETIMED_ALL_2551_FIXED_INVENTORY_PATTERNS','source_heads':{'PR3630':'bcac7fe04b9b7f7f5d3c27d620561f96c4ae5608','PR3531':'550a660a97308d3aeb3620ee1f4218f77e2c2742'},'source_sha256':{'binomial.py':hashlib.sha256(raw).hexdigest(),'pr3630-check_budget.py':hashlib.sha256((HERE/'cap-source/pr3630-check_budget.py').read_bytes()).hexdigest()},'local_per_call':L,'width_inventory_per_call':dict(zip(WIDTHS,INVENTORY)),'capacity_counts_per_replica':dict(zip(CAPS,CAP_TOTAL)),'ideal_idle_per_replica':{r:str(n/T) for r,n in idle.items()},'ideal_profile_at_T740':ideal,'literal_T530_profile':LITERAL,'cap_root':[str(LO),str(HI)],'cap_root_decimal':[format(float(LO),'.25f'),format(float(HI),'.25f')],'literal_root':[str(actuallo),str(actualhi)],'literal_to_cap_ratio':[str(fraclow),str(frachigh)],'literal_to_cap_ratio_float':[float(fraclow),float(frachigh)],'remaining_root_headroom':[str(LO-actualhi),str(HI-actuallo)],'remaining_root_headroom_float':[float(LO-actualhi),float(HI-actuallo)],'patterns':len(patterns),'strict':len(strict),'symbolically_zero':len(tight),'coefficient_sha256':ch.hexdigest(),'min_reduced_cost_lower':str(min(strict)[0]),'moment_at_cap_lower':list(map(str,ml)),'moment_at_cap_upper':list(map(str,mh)),'moment_at_literal_lower':list(map(str,aml)),'moment_at_literal_upper':list(map(str,amh)),'scope':'All positive integer T under same fixed capacities,widths,new local bill,dimension73,live stock896T. Chronology/family attainment unknown. Modern primitive scope uses kappa approximately b; no universal multiplication cap and no new supplier admission.','seconds':time.time()-start}
# Decimal presentation generated exactly, not through float.
def dec(q):
 return str(q.numerator//q.denominator)+'.'+str((q.numerator%q.denominator)*10**24//q.denominator).zfill(24)
result['cap_root_decimal']=[dec(LO),dec(HI)];result['literal_root_decimal']=[dec(actuallo),dec(actualhi)]
(OUT/'RETIMED-PACKING-CAP.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(result['status']);print('cap',result['cap_root_decimal']);print('literal',result['literal_root_decimal']);print('fraction',result['literal_to_cap_ratio_float']);print('headroom',result['remaining_root_headroom_float']);print('seconds',result['seconds'])
print('Fresh evidence:',OUT)
