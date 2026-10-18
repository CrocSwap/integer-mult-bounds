"""Independent literal whole-owner, actual native profile and exact moment check.
No emitter, optimizer, constructor, assembler or moment-engine imports.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,defaultdict
import json,gzip,hashlib,importlib.util,argparse
ap=argparse.ArgumentParser();ap.add_argument("--work",type=Path,required=True);ap.add_argument("--out",type=Path,required=True);ap.add_argument('--provider',action='append',default=[],help='PID=DIR explicit verified native artifacts; defaults to --work/PID-local');args=ap.parse_args()
P=Path(__file__).resolve().parents[1];PKG=P
load=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def need(x,msg):
 if not x:raise ValueError(msg)
s=importlib.util.spec_from_file_location('E',P/'extras/exact_intervals.py');E=importlib.util.module_from_spec(s);s.loader.exec_module(E)
spec=load(PKG/'data/SPEC.json');plan=load(PKG/'data/PLAN.json');roles=load(PKG/'data/OWNERS.json.gz');old=load(P/'comparison/PR664-SPEC.json');original_plan=load(P/'comparison/GEOMETRY.json')
need(hashlib.sha256((PKG/'data/PLAN.json').read_bytes()).hexdigest()==spec['data']['plan_sha256'],'plan pin');need(hashlib.sha256((PKG/'data/OWNERS.json.gz').read_bytes()).hexdigest()==spec['data']['owners_sha256'],'owner pin')
for key in ['order','windows','pairs','sides']:need(plan[key]==original_plan[key],'unchanged inherited physical geometry')
need(set(spec['providers'])==set(plan['provider_registry'])=={'gauge44'},'selected constructed provider')
widths_by_pid={};paid_by_pid={}
overrides=dict(x.split('=',1)for x in args.provider)
need(set(overrides)<=set(spec['providers']),'known provider overrides')
for pid in sorted(spec['providers']):
 directory=Path(overrides.get(pid,args.work/(pid+'-local')))
 canon=load(directory/'CANONICAL-WORD.json.gz');programs=load(directory/'LOCAL-PROGRAMS.json.gz')
 need((canon['v'],canon['h'],canon['R'])==(112,9,504),'actual native geometry')
 widths_by_pid[pid]=[len(canon['frames'][canon['final'][h]])-len(canon['frames'][canon['start'][h]])for h in range(224,728)]
 paid_by_pid[pid]=Counter(e[-1]for e in programs['forward']if e[0]in('climb','center'))
 need(paid_by_pid[pid]==Counter(e[-1]for e in programs['backward']if e[0]in('climb','center')),'both actual orientations')
 need(widths_by_pid[pid]==spec['providers'][pid]['complete_contract']['widths'],'actual native widths')
 need(dict(paid_by_pid[pid])=={int(k):n for k,n in spec['providers'][pid]['expected_profile'].items()},'actual native paid profile')

calls={c['time']:c for c in plan['provider_calls']};need(set(calls)==set(range(72)),'complete chronology');need(Counter(c['provider']for c in calls.values())==Counter({'gauge44':72}),'gauge44 literal dispatch');paid=sum((paid_by_pid[c['provider']]for c in calls.values()),Counter());used=defaultdict(set);families=defaultdict(set);helpers=defaultdict(set)
for r in roles:
 t=r['time'];c=calls[t];need((c['stage'],c['replica'])==(r['stage'],r['replica'])==tuple(plan['order'][t]),'ordered complete call');w=widths_by_pid[c['provider']][r['helper']];need(w==r['width'],'actual width');need(r['helper']not in helpers[t]and r['family']not in families[t],'unique helper and physical family');helpers[t].add(r['helper']);families[t].add(r['family']);need(r['family']==r['owner_replica']*896+(2*plan['pairs'][str(r['child'])]+plan['sides'][str(r['child'])])*112+r['port'],'physical family');need(r['copy']==r['owner_replica']*112+r['port'],'copy')
 key=r['owner_replica'],r['child'],r['port'];cap,window=plan['windows'][str(key[0])+','+str(key[1])];need(t in window and 0<=r['offset']<=r['offset']+w<=cap,'window and footprint');cells=set(range(r['offset'],r['offset']+w));need(not used[key]&cells,'disjoint footprints');used[key]|=cells
need(len(roles)==36288 and all(helpers[t]==set(range(504))for t in range(72)),'all helper calls');idle=Counter()
for key,(cap,window)in plan['windows'].items():
 rep,ch=map(int,key.split(','))
 for port in range(112):
  cells=used[rep,ch,port];need(cells==set(range(len(cells))),'compacted prefix')
  if len(cells)<cap:idle[cap-len(cells)]+=1
paid.update(idle);need(dict(paid)=={int(k):v for k,v in plan['profile'].items()}=={int(k):v for k,v in spec['expected']['global_profile'].items()},'independent paid profile');need(sum(r*n for r,n in paid.items())==520704,'rank mass')
costs=[]
for label,q in [('PR664',Q(old['expected']['complex_lower'])),('candidate',Q(spec['expected']['complex_lower']))]:
 lower=upper=Q(0)
 for r,n in paid.items():
  a,b=E.log(Q(73,r));lo,hi=E.exp(q*a,q*b);lower+=Q(r*n,73*7168)*lo;upper+=Q(r*n,73*7168)*hi
 need(upper<1,'strict exact moment '+label);costs.append(dict(endpoint=label,b=str(q),lower=str(lower),upper=str(upper),strict_margin_lower=str(1-upper)))
b=Q(spec['expected']['complex_lower']);need(Q(spec['expected']['kappa'])<=b/(1+b),'outer conversion');need(Q(spec['expected']['kappa'])>Q(old['expected']['kappa']),'strictly higher rate')
args.out.write_text(json.dumps(dict(status='PASS_INDEPENDENT_GAUGE44_MAP_NATIVE_PROFILE_AND_EXACT_MOMENT',calls=72,roles=36288,profile=dict(paid),idle=dict(idle),costs=costs,kappa=spec['expected']['kappa'],scope='Exact literal owners using the inherited phase-window geometry, native word widths and actual program child counts. Separate strict pipeline supplies physical chart/controller and full finite/outer admission.'),indent=2)+'\n');print('PASS independent map and exact moments',flush=True)
