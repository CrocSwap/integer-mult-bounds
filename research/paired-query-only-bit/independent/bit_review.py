#!/usr/bin/env python3
"""Independent reverse GF(2) native/caller and fixed-grid moment arithmetic."""
from pathlib import Path
from collections import Counter
from fractions import Fraction as F
import json,gzip,hashlib,argparse
import importlib.util
_spec=importlib.util.spec_from_file_location('independent_intervals',Path(__file__).with_name('interval_gate.py'));G=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(G)
if not __debug__: raise RuntimeError('Run without -O; assertions are proof checks.')
B=Path(__file__).resolve().parents[2];D=B/'workers/d'
read=lambda p:json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
ap=argparse.ArgumentParser();ap.add_argument('--efree',action='store_true');ap.add_argument('--package',default=str(D));ap.add_argument('--out');args=ap.parse_args();D=Path(args.package);callfile='EFREE-CALLER.json.gz' if args.efree else 'CALLER.json.gz';resultfile='EFREE-RESULT.json' if args.efree else 'RESULT.json';outname='bit-efree-review.json' if args.efree else 'bit-review.json'
w=read(D/callfile);n=read(D/'retained/inputs/BIT-NATIVE-WORD.json.gz');record=read(D/resultfile)
adj=[1<<r if r<n['public'] else 0 for r in range(n['public']+n['owned_fields'])]
for e in reversed(n['program']):
 if e[0]=='ADD':adj[e[2]]^=adj[e[1]]
 elif e[0]=='MOVE':pass
 elif e[0]=='SWAP':adj[e[1]],adj[e[2]]=adj[e[2]],adj[e[1]]
 elif e[0] in ('INIT','CLEAR'):adj[e[1]]=0
 else:raise AssertionError(e[0])
expected=[(1<<r)^((1<<(r+111)) if r<111 else 0) for r in range(n['public'])]
assert adj[:n['public']]==expected
# Every exponent stays in its 8-bit lane even with repeated powers.
degree=Counter()
for event in w['events']:
 if event[0]=='LOCAL':degree[event[1]]+=1
 elif event[0]=='IDLE_ONE':degree.update(event[2])
assert degree and max(degree.values())<256
# Unrestricted D powers in F2[q,D]/(q²-1), not q=1 specialization.
def shift(s,q=0,m=0):return {(r,k^q,a+m) for r,k,a in s}
def replay(c):
 a=[{(r,0,0)} for r in range(c['roles'])]
 for e in reversed(c['events']):
  op=e[0]
  if op=='ADD':a[e[2]]^=a[e[1]]
  elif op=='SWAP':a[e[1]],a[e[2]]=a[e[2]],a[e[1]]
  elif op=='QUERY':a[e[2]]^=shift(a[e[1]],q=1)
  elif op=='IDLE_ONE':a[e[1]]=shift(a[e[1]],m=sum(1<<(8*(s-1)) for s in e[2]))
  elif op=='LOCAL':
   _,s,x,y=e;mon=1<<(8*(s-1));a[x]=shift(a[x],m=mon);a[y]=shift(a[y],m=mon);a[x]^=shift(a[y],q=1)
  else:raise AssertionError(op)
 ex=[{(r,d['q'],sum(1<<(8*(s-1)) for s in d['stages']))} for r,d in enumerate(c['diagonal'])]
 return [r for r in range(c['roles']) if a[r]!=ex[r]]
assert not replay(w)
controls={}
for op in ('LOCAL','QUERY','IDLE_ONE','ADD','SWAP'):
 c=json.loads(json.dumps(w));idx=next(i for i,e in enumerate(c['events']) if e[0]==op);del c['events'][idx];bad=replay(c);assert bad;controls[op]={'deleted':idx,'bad_input_rows':bad}
c=json.loads(json.dumps(w));next(e for e in c['events'] if e[0]=='QUERY')[0]='ADD';assert replay(c);controls['QUERY_without_q']=replay(c)
dims={int(k):v['dim'] for k,v in n['frames'].items()};paid=Counter(abs(dims[e[3]]-dims[e[2]]) for e in n['program'] if e[0]=='MOVE');helpers=Counter(dims[n['final'][r]]-dims[n['start'][r]] for r in range(222,n['public']))
calls=sum(e[0]=='LOCAL' for e in w['events']);assert calls==(36 if args.efree else 18)
T=Counter({r:calls*c for r,c in helpers.items()});P=Counter({r:calls*c for r,c in paid.items()})
for d in w['diagonal']:T[d['q']+7*len(d['stages'])]+=111
for e in w['events']:
 if e[0]=='QUERY':P[1]+=111
 elif e[0]=='IDLE_ONE':P[7*len(e[2])]+=111
assert dict(T)=={int(r):c for r,c in record['targets'].items()} and dict(P)=={int(r):c for r,c in record['paid'].items()}
assert sum(r*(T[r]-P[r]) for r in T.keys()|P.keys())==(1506 if args.efree else 753)
if args.efree:
 assert 1 not in T and all(d['stages'] for d in w['diagonal'])
 old=read(D/'RESULT.json' if (D/'RESULT.json').exists() else D/'data/6834_result.json')
 for r in T.keys()|{int(x) for x in old['targets']}:assert T[r]==2*old['targets'].get(str(r),0)-(222 if r==1 else 0)
 for r in P.keys()|{int(x) for x in old['paid']}:assert P[r]==2*old['paid'].get(str(r),0)-(222 if r==1 else 0)
raw=F('.00385253');lo=F('.0038525393934');hi=F('.0038525393935')
margins={str(k):G.sub(G.moment(T,k),G.moment(P,k)) for k in (raw,lo,hi)}
assert margins[str(raw)][0]>0 and margins[str(lo)][0]>0 and margins[str(hi)][1]<0
def exppos(x):return G.div(G.exact(1),G.expminus(x))
def shifted(hist,offset):
 s=(0,0)
 for r,c in hist.items():
  fac=exppos(G.smul(G.log(r),offset)) if offset>0 else G.expminus(G.smul(G.log(r),-offset))
  s=G.add(s,G.smul(G.mul(G.power(r,raw),fac),c))
 return s
u=F(1,5);target=G.moment(T,raw)
alpha=G.div(G.moment(P,raw),target)
gamma=G.div(shifted(P,u),G.mul(exppos(G.smul(G.log(15),u)),target))
lam=G.div(G.mul(exppos(G.smul(G.log(16),u)),shifted(T,-u)),target)
upper=[F(v[1],G.B) for v in (alpha,gamma,lam)];aa,gg,ll=upper
norm=1/(1+768*(1-aa))+2*gg**768+ll**768;assert norm<1
fac=G.exact(1);z=exppos(G.smul(G.log(127),raw));power=768
while power:
 if power&1:fac=G.mul(fac,z)
 power//=2
 if power:z=G.mul(z,z)
eta=G.div(G.exact(1-raw),fac);theta=F(42,43);p=1
assert 15**43<16**42 and not 15**42<16**41
while theta**p>=F(eta[0],G.B) or F(fac[1],G.B)>=2**p:p+=1
assert p==610 and theta**609>=F(eta[1],G.B)
H=293160000000000;assert(H+1)**p<2**29316 and(H-10**10+1)**p>=2**29315
covered=raw-2*F(1,10**10);bootstrap=[]
if args.efree:
 selected=read(D/'data/selected_claim.json');previous=F(selected['admitted_BIT_saving']);assert previous==F('.0034')
 selected_pins={'selected_claim.json':'9cee8a1304fa893be3d3b641eda42fdd9b2fd6a5ac2124fb891de7a1a5e8d92e','selected_record.json':'9b8d0eea95b3bf0dfcb7938a732a6439b87a2685dec2a5ab9e525b3b34debbfa','selected_review.md':'8bd158b8ef68202000f167b9b78db0b31531b5b067b5cbd91b5bf35f3ddd1ab6'}
 for filename,digest in selected_pins.items():assert hashlib.sha256((D/'data'/filename).read_bytes()).hexdigest()==digest
 assert read(D/'data/selected_record.json')['certificate_sha256']==selected_pins['selected_claim.json']
 admissions=(F('.0038507'),F('.00385248'))
else:previous=F('.00376669');admissions=(F('.00385218'),F('.00385252'))
for stepindex,admitted in enumerate(admissions):
 cap=(1-F(1,250))*covered+F(1,250)*previous;assert previous<admitted<cap and F(1,250)>cap
 assert cap==F(record['ordinary_bootstrap'][stepindex]['envelope']) and admitted==F(record['ordinary_bootstrap'][stepindex]['admitted'])
 bootstrap.append({'previous':str(previous),'admitted':str(admitted),'envelope':str(cap),'margin':str(cap-admitted)});previous=admitted
ops=Counter(e[0] for e in w['events']);ports=w['ports'];roles=w['roles'];ambient=w['ambient_rank']
basis=ports*8*(ops['ADD']+3*ops['SWAP']);visible=calls*10**7+basis+256*ports*(calls+ops['QUERY']+roles)
routecount=4*(sum(T.values())+sum(P.values()))+8*ports*calls+8*ports*ops['IDLE_ONE'];routes=8*(10*ambient*ambient+10*ambient)*routecount
owned=calls*n['owned_fields']+2*ports*roles*len(w['events'])+16*ports*(calls+ops['QUERY']+roles)
assert visible+routes<10**12 and owned<10**7
assert visible==record['ordinary_visible_records'] and routes==record['whole_job_route_records'] and owned==record['owned_bank_bound']
assert previous==F(record['ordinary_admitted'])
out=dict(reviewed_result_sha256=hashlib.sha256((D/resultfile).read_bytes()).hexdigest(),ordinary=dict(visible=visible,routes=routes,total=visible+routes,owned_bank=owned),status='INDEPENDENT_BIT_REVIEW_PASS',caller_sha256=hashlib.sha256((D/callfile).read_bytes()).hexdigest(),native_sha256=hashlib.sha256((D/'retained/inputs/BIT-NATIVE-WORD.json.gz').read_bytes()).hexdigest(),native_exact_input_rows=659,caller_exact_input_rows=w['roles'],native_calls=calls,paid=dict(sorted(P.items())),targets=dict(sorted(T.items())),rank_surplus=(1506 if args.efree else 753),margins={k:G.value(v) for k,v in margins.items()},finite_ratios=[G.value(v) for v in (alpha,gamma,lam)],normalized_upper_float=float(norm),LP=p,H=H,bootstrap=bootstrap,controls=controls,scope='Exact scalar operator and arithmetic; no chart-provider/tape implementation or tariff re-admission; Efree caller removes empty q-only credits and bootstraps only selected .0034; five foundational framework premises remain.')
if args.out!='-':(Path(args.out) if args.out else B/'workers/e'/outname).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
