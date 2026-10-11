from pathlib import Path
from collections import Counter,defaultdict
import json,gzip,hashlib,importlib.util
O=Path(__file__).resolve().parent;R=O.parents[2];P=R/'experiments/architecture/complex-direct8-eleven451';rd=lambda p:json.loads(p.read_text());gz=lambda p:json.loads(gzip.decompress(p.read_bytes()));sp=importlib.util.spec_from_file_location('independent_phase89',O/'source_complex_chart.py');a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a);a.M=89
t=gz(P/'hosted/GLOBAL-TEMPLATE.json.gz');old=gz(P/'split-centres/GLOBAL-TEMPLATE.json.gz');ph=rd(P/'hosted/DATA-PHASES.json');sig=rd(P/'geometry-audit/HOSTED-SIGMA.json');g=rd(P/'hosted/GLOBAL.json');assert t['local_programs']==old['local_programs'];assert(t['m'],t['replicas'],len(t['calls']))==(89,8,88)
loc={e['stage']:(i,e)for i,e in enumerate(t['execution_schedule'])if e['kind']=='local'};idle={e['idx']:(i,e)for i,e in enumerate(t['execution_schedule'])if e['kind']=='idle'};used=defaultdict(list);lookup={};seen=defaultdict(set);routes=sig['routes'];slots=set(map(tuple,t['hosting']['slots']));assert len(routes)==len(slots)==6160
for ch,copy,off,w,s,h,B,tr in routes:
 assert(ch,copy,off,w,s,h)in slots and w==9 and len(B)==89 and a.orthogonal(B);assert a.compose(a.transpose(B),B)==a.identity();side,port=divmod(copy,120);stop,e=idle[ch];start,le=loc[s];assert start<stop and le['pair']!=e['pair']
 for ev in t['execution_schedule'][start+1:stop]:
  if ev['kind']=='local':assert ev['pair']!=e['pair']
  elif ev['kind']=='bridge':assert e['pair']not in [ev['src'],ev['dst']]
  elif ev['kind']=='idle':pass # all C_axis and X translations commute; actual phase polys checked below.
  else:raise AssertionError(ev)
 child=ph['recipes'][port]['idle_children'][e['phase_children'][side]];sel=child['orthogonal_axes'][off:off+w];assert B[:9]==sel and tr==child['translation_after'];assert not set(sel)&set(used[ch,copy]);used[ch,copy]+=sel
 key=s,e['pair'],side,port;assert tuple(B)not in seen[key];seen[key].add(tuple(B));assert(s,h)not in lookup;lookup[s,h]=ch,copy,off,w
H=Counter();phasecount=0
for e in t['idle_children']:
 copy=e['side']*120+e['port'];child=ph['recipes'][e['port']]['idle_children'][e['phase_child']];axes=child['orthogonal_axes'];host=used[e['idle'],copy];rest=[v for v in axes if v not in host];assert Counter(host)+Counter(rest)==Counter(axes);assert len(rest)==e['rank'];assert a.phase(host+rest,e['translation_after'])==a.phase(axes,child['translation_after']);H[len(rest)]+=8 if rest else 0;phasecount+=1
owners=0
for c in t['calls']:
 assert c['orientation']==('backward'if c['stage']%2 else'forward');lc=g['source_local_checks'][c['orientation']]
 for rank,n in lc['paid_profile'].items():H[int(rank)]+=n
 for h,(family,route)in enumerate(c['owners'][240:]):
  ch,copy,off,w=lookup[c['stage'],h];side,port=divmod(copy,120);e=idle[ch][1];assert route==[3,ch,off,w];assert family==c['replica']*1200+(2*e['pair']+side)*120+port;owners+=1
H.pop(0,None);assert dict(H)=={int(k):v for k,v in g['profile'].items()};assert owners==49280 and phasecount==3120;mass=sum(r*n for r,n in H.items());assert 89*g['live']-mass==3264
out={'status':'PASS_INDEPENDENT_COMPLEX451_ALL_SELECTED89_SIGMA_PHASE_WINDOWS_OWNER_PROFILE','slots':6160,'owner_instances':owners,'all89_columns':True,'phase_instances':phasecount,'phase_identity':'ExactZ4 degree2 characterpolynomials includingtranslations; inverse negatespolynomials. EveryC_axis/Xtranslation commutes, so interveningidle factors safe in retained commonchart interface.','paid_profile':dict(H),'mass':mass,'deficit':3264,'scope':'Wholehelper onefamily hosting only. Fullselectedorthogonalgeometry rightaction injection and finitephase identities; generalizedcommonchart/Clifford/allsizecompiler interfaces conditional.','sources':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [P/'hosted/GLOBAL-TEMPLATE.json.gz',P/'hosted/DATA-PHASES.json',P/'geometry-audit/HOSTED-SIGMA.json']}};(O/'COMPLEX451-GEOMETRY.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
