# SPDX-License-Identifier: Apache-2.0
# Derived from Jeremy Kothe / Philippe Van Velzen / Tekalign owner verifier.
# Parameter extension with substantial OpenAI Codex assistance.
"""Borrow-word owner witness: literal verification of the shipped exact fill (new/borrow-fill/FILL.json.gz) and emission of
OWNERS/ORDER/DISPATCH/PROFILE/RESULT for lift_parent.py.  The helper count per call is R' = 480-k and the per-call widths come from
new/BORROW-PROVIDERS.json; the same windows, bins and distinct-family rules as the pinned PR1297 owner construction are checked
literally (no window, bin, helper or family rule is relaxed).  Idle remainders are whatever the exact bins leave (ranks priced
exactly by the profile).  The fill itself is found offline by new/borrow-fill/solve_fill.py (not rerun here) and only verified.
"""
import argparse,collections,gzip,importlib.util,json
from pathlib import Path
assert __debug__, 'Assertions are required'
F=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();P=args.out.resolve();P.mkdir(parents=True,exist_ok=False)
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def dump(p,x):
 b=json.dumps(x,sort_keys=True,separators=(',',':')).encode();z=bytearray(gzip.compress(b,mtime=0));z[9]=255;p.write_bytes(bytes(z) if p.suffix=='.gz' else b)
plan=read(F/'inputs/PLAN.json');parent=read(F/'inputs/GLOBAL-TEMPLATE.json.gz');T=plan['T']
OF=F/'new/borrow-fill/ORDER.json'
assert OF.exists(), 'explicit candidate order required'
if OF.exists():   # a free complete invocation order (666 calls; windows are recomputed from it below) with its explicit dispatch
 order=read(OF);dispatch={(s,r):pid for s,r,pid in read(F/'new/borrow-fill/DISPATCH.json')}
 Tnew=1+max(r for s,r in order)
 assert type(Tnew) is int and Tnew>0
 assert len(order)==9*Tnew and sorted(map(tuple,order))==[(s,r) for s in range(9) for r in range(Tnew)],'order must cover every actual source replica and stage exactly once'
 assert set(dispatch)==set(map(tuple,order)),'complete provider dispatch'
else:
 order=[[s,r+T*g] for s,r in plan['order'] for g in range(2)]
 dispatch={(s,r+T*g):pid for s,r,pid in read(F/'inputs/DISPATCH.json') for g in range(2)}
source=F/'vendor/build_parent.py';sp=importlib.util.spec_from_file_location('windows',source);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);windows,schedule=mod.actual_windows(parent,order)
prov=read(F/'new/BORROW-PROVIDERS.json');widths={p:d['widths'] for p,d in prov.items()};paid={p:{int(k):v for k,v in d['actual_paid_profile'].items()} for p,d in prov.items()}
R=len(next(iter(widths.values())));assert all(len(w)==R for w in widths.values()) and set(widths)==set(dispatch.values())
fill=read(F/'new/borrow-fill/FILL.json.gz');assert fill['columns']==['time','helper','owner_replica','child','port','offset']
for s_,r_,p_ in fill['dispatch_overrides']:dispatch[s_,r_]=p_   # the single gauge44->extra provider upgrade of the pinned fill
pairs,sides=plan['pairs'],plan['sides']
at={tuple(x):i for i,x in enumerate(order)}
roles=[]
for time,helper,rep,child,port,offset in fill['rows']:
 stage,replica=order[time];w=widths[dispatch[stage,replica]][helper]
 roles.append(dict(stage=stage,replica=replica,time=time,helper=helper,width=w,owner_replica=rep,child=child,port=port,offset=offset,copy=112*rep+port,family=rep*896+(2*pairs[str(child)]+sides[str(child)])*112+port))
assert len(roles)==len(order)*R,(len(roles),len(order)*R)
helpers=collections.defaultdict(set);fams=collections.defaultdict(set);used=collections.defaultdict(set)
for z in roles:
 call=(z['stage'],z['replica']);rep,child,port=z['owner_replica'],z['child'],z['port']
 cap,allowed=windows[f'{rep},{child}']
 assert z['time'] in allowed and 0<=port<112 and 0<=z['helper']<R
 assert z['helper'] not in helpers[call] and z['family'] not in fams[call]
 helpers[call].add(z['helper']);fams[call].add(z['family'])
 cells=set(range(z['offset'],z['offset']+z['width']));assert z['offset']>=0 and z['offset']+z['width']<=cap and not used[rep,child,port]&cells
 used[rep,child,port]|=cells
assert set(helpers)==set(map(tuple,order)) and all(s==set(range(R)) for s in helpers.values())
idle=collections.Counter()
for key,(cap,times) in windows.items():
 r,ch=map(int,key.split(','))
 for port in range(112):
  c=used[r,ch,port];assert c==set(range(len(c))),'gap in pending prefix'
  if cap-len(c):idle[cap-len(c)]+=1
H=collections.Counter(idle)
for sr in order:
 for r,n in paid[dispatch[tuple(sr)]].items():H[int(r)]+=n
assert 73*(896*Tnew)-sum(r*n for r,n in H.items())==320*Tnew,'rank-mass deficit'
roles.sort(key=lambda r:(r['time'],r['helper']))
dump(P/'OWNERS.json.gz',roles);dump(P/'ORDER.json',order);dump(P/'DISPATCH.json',[[s,r,dispatch[s,r]] for s,r in order]);dump(P/'PROFILE.json',dict(sorted(H.items())))
dump(P/'RESULT.json',dict(status='PASS_EXACT_BORROW_WORD_REPLICA_OWNER_FILL',roles=len(roles),helpers_per_call=R,dispatch=dict(collections.Counter(dispatch.values())),idle=dict(sorted(idle.items())),scope='Literal strict windows, bin capacities, per-call helper widths and distinct physical families verified for the shipped fill; local programs are the borrow words; full parent binding, finite invoice and global admission run separately.'))
print('PASS_OWNER_VERIFY',dict(idle),dict(sorted(H.items())),flush=True)
