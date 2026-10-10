"""Fresh dimension20 chart programs for the fixed candidate15, no upstream execution."""
from pathlib import Path
import sys
CODE=Path(__file__).resolve().parent
sys.path.insert(0,str(CODE.parent))
import support
CLOSURE=support.OUTPUT/'closure'
sys.path.insert(0,str(CODE.parent/'closure'))
import hashlib,json,gzip
from collections import Counter
import chart_construction as charts
from source_contract import SOURCE,REVIEW,HEAD,verify_inputs
ROOT=support.out('certificates','placeholder').parent
BRIDGE=support.OUTPUT/'weighted'

def run(candidate_path=None,bridge_path=None,case="weighted19"):
 assert case in("weighted19","15")
 candidate_path=Path(candidate_path)if candidate_path else (BRIDGE/'rebound-candidate19.json'if case=='weighted19'else support.HERE/'witnesses/candidate15.json');verify_inputs()
 pins=json.loads((support.HERE/'inputs.json').read_text());row=next(x for x in pins['files']if x['path']=='bank_check.py');raw=(SOURCE/'bank_check.py.txt').read_bytes()
 assert len(raw)==row['bytes'] and hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob']
 assert 'G=lambda a,b:9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)'in raw.decode()
 c=json.loads(candidate_path.read_text());assert c['source_head']==HEAD
 assert case=='15'or c['overlay_sha256']=='25a0edc8c5f399fcf536b28c4e3575aa52177bb78b6078a631acb748954f0739'
 cache=json.loads(gzip.decompress((CLOSURE/'response-cache.json.gz').read_bytes()));rows=cache['roles'];f={int(k):v for k,v in json.loads(gzip.decompress((SOURCE/'bitword/selected/bit/frames_p10.json.gz').read_bytes()))['frames'].items()}
 pivots={z['virtual_pivot']for z in c['entries']};donors={d for z in c['entries']for d in z['virtual_donors']};active=pivots|donors;lines={}
 for z in c['entries']:
  line=tuple(i for i,x in enumerate(z['basis'][0])if x)
  for role in[z['virtual_pivot']]+z['virtual_donors']:
   assert role not in lines or lines[role]==line;lines[role]=line
 programs=[];registry={};uses=[];H=Counter()
 def put(key,builder):
  if key not in registry:registry[key]=len(programs);programs.append(dict(program_id=len(programs),**builder()))
  return registry[key]
 for role in sorted(active):
  r=rows[str(role)];frame=r['first_base_use']['frame'];d=f[frame]['dim'];line=lines[role]
  pid=put(('first',frame,line),lambda:dict(kind='first_frame_quotient',frame=frame,**charts.first_frame_chart(f[frame],line)))
  uses.append(dict(kind='first_frame_quotient',role=role,stream=r['stream'],frame=frame,rank=d-1,program_id=pid))
  rank=19 if role in pivots else 1;kind='pivot_residual'if role in pivots else'donor_line_entrance'
  pid=put(('line',line,rank),lambda:dict(kind=kind,**charts.line_chart(*line,rank)))
  uses.append(dict(kind=kind,role=role,stream=r['stream'],rank=rank,program_id=pid))
  H[d]-=1
  if d>1:H[d-1]+=1
  if role in donors:H[1]+=1
 assert {k:v for k,v in H.items()if v}=={int(k):v for k,v in c['local_histogram_delta'].items()}
 maxf=max(p['count']for p in programs);assert maxf<=400
 bound=max(400,maxf)+99+100;assert bound==599
 report=dict(status='PASS_FRESH_P10_CHART_PROGRAMS',source_head=HEAD,candidate_sha256=hashlib.sha256(candidate_path.read_bytes()).hexdigest(),
  candidate_word_sha256=c.get('overlay_sha256'),dimension=20,metric='9I-J',metric_source_git_blob=row['git_blob'],exterior_formula='11*a-sum(a)',charts=len(programs),role_uses=uses,role_use_count=len(uses),
  first_quotients=len(active),pivot_residuals=len(pivots),donor_entrances=len(donors),max_factors=maxf,max_numerator=max(p['max_numerator']for p in programs),max_denominator=max(p['max_denominator']for p in programs),normalizer_bound=bound,
  factor_programs=programs,geometry_receipt_bound=False,scope='Exact rational inverse programs and first-frame inputs only. Full physical chronology, bank role assignment, scalar norms, inherited prime selection and all-size compiler admission remain separate. No all-characteristics>5 claim for dimension20 metric.')
 if bridge_path:
  b=json.loads(Path(bridge_path).read_text());paths={p['role']:p for p in b['selected_paths']};assert set(paths)==active
  if case=='15':paths={r:dict(physical=p['stream'],frames=[p['first_frame']],dimension=p['first_dimension'])for r,p in paths.items()}
  for role,p in paths.items():
   r=rows[str(role)];assert p['physical']==r['stream']and p['frames'][0]==r['first_base_use']['frame']and p['dimension']==f[p['frames'][0]]['dim']
  assert (b['overlay_sha256']==c['overlay_sha256']if case=='weighted19'else b['candidate_sha256']==report['candidate_sha256']);report.update(geometry_receipt_bound=True,bridge_receipt_sha256=hashlib.sha256(Path(bridge_path).read_bytes()).hexdigest())
 out=ROOT/(candidate_path.stem+'-charts.json');out.write_text(json.dumps(charts.base.serial(report),separators=(',',':'))+'\n')
 print(json.dumps({k:v for k,v in report.items()if k not in('factor_programs','role_uses')},indent=2));return report
if __name__=='__main__':
 if not __debug__:raise RuntimeError('Assertions required')
 run(bridge_path=BRIDGE/'transport-result.json')
