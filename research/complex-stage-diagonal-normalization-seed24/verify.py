"""Selective stage diagonal consolidation, for @woklerx with substantial
OpenAI Codex assistance. Apache-2.0. Standard library only.
"""
import argparse,ast,copy,gzip,hashlib,importlib.util,json,sys,tarfile,tempfile
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
ARCHIVE='research/community-frontier1042-audit/selected-replay.tar.gz'
CHECKER='research/complex-k492-owner-repair/code/hpe_audit_local.py'
LOWER='research/complex-dyadic-lowering/lower.py'
HORNER='research/complex-k492-owner-repair/code/hpe_emit_local.py'
REQUIRED={ARCHIVE,CHECKER,LOWER,HORNER,'research/community-frontier1042-audit/ASSEMBLY.json'}
CANONICAL='4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c'

def need(ok,msg):
 if not ok:raise ValueError(msg)
def pairs(xs):
 d={}
 for k,v in xs:need(k not in d,'duplicate JSON key');d[k]=v
 return d
def loads(raw):return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
def canonical(x):return json.dumps(json.loads(json.dumps(x)),sort_keys=True,separators=(',',':'))
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(x):return sha(canonical(x).encode())
def fsha(p):
 b=p.read_bytes()
 return sha(b if p.suffix=='.gz' else b.replace(b'\r\n',b'\n'))

def source(pins):
 need(set(pins)==REQUIRED,'required source set mismatch')
 for p,h in pins.items():need(fsha(ROOT/p)==h,'source hash mismatch')
 data={};hashes={}
 with tarfile.open(ROOT/ARCHIVE) as t:
  for name in ('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz'):
   ms=[m for m in t.getmembers() if m.name=='slots/local/'+name]
   need(len(ms)==1 and ms[0].isfile(),'unique selected archive member')
   raw=t.extractfile(ms[0]).read();decoded=gzip.decompress(raw)
   data[name]=loads(decoded);hashes[name]={'container':sha(raw),'payload':sha(decoded)}
 need(hashes['CANONICAL-WORD.json.gz']['payload']==CANONICAL,'selected canonical pin')
 c=data['CANONICAL-WORD.json.gz'];need((c['v'],c['R'],c['h'])==(112,480,9),'source geometry')
 asm=loads((ROOT/'research/community-frontier1042-audit/ASSEMBLY.json').read_bytes())
 need(Q(asm['kappa'])==Q(1672188119205421,10**18),'assembly provenance')
 return c,data['LOCAL-PROGRAMS.json.gz'],hashes

def cost(op,strong=True):
 if op[0] in ('clear','copy'):return 1
 q=Q(op[3],op[4]) if op[0]=='add' else Q(op[2],op[3]);a,b=abs(q.numerator),q.denominator
 need(a>0 and b&(b-1)==0,'nonzero dyadic required')
 if op[0]=='scale':
  need(a&(a-1)==0,'signed power-of-two scale required')
  return abs(a.bit_length()-b.bit_length())+int(q<0)
 if strong and a==b:return 2
 return (2 if strong else 3)+(a.bit_length()-1)+a.bit_count()+(b.bit_length()-1)

def stage_transform(es,selected):
 d={};out=[];removed=[]
 for i,e in enumerate(es):
  if e[0]=='scale' and e[1] in selected:
   d[e[1]]=d.get(e[1],Q(1))*Q(e[2],e[3]);removed.append(i)
  else:
   op=list(e)
   if e[0]=='add':
    q=Q(e[3],e[4])*d.get(e[2],Q(1))/d.get(e[1],Q(1));op[3:5]=[q.numerator,q.denominator]
   out.append(op)
 tail=[['scale',r,q.numerator,q.denominator] for r,q in sorted(d.items()) if q!=1]
 return out,tail,removed

def select(c):
 chosen={};ledger={}
 for phase in ('A','B'):
  es=c[phase];base=sum(cost(e) for e in es);scores=[]
  for r in sorted({e[1] for e in es if e[0]=='scale'}):
   out,tail,_=stage_transform(es,{r});delta=sum(cost(e) for e in out+tail)-base
   scores.append([r,delta])
  chosen[phase]={r for r,d in scores if d<0};ledger[phase]=scores
 return chosen,ledger

def split(events):
 parts=[]
 for e in events:
  if e[0]=='phase':parts.append([e[1],[]])
  else:need(bool(parts),'missing initial phase');parts[-1][1].append(e)
 return parts
def dual(op):
 e=copy.deepcopy(op)
 if e[0]=='add':e[1],e[2]=e[2],e[1];e[3]=-e[3]
 elif e[0]=='scale':e[2],e[3]=e[3],e[2]
 else:raise ValueError('unexpected stage primitive')
 return e

def construct(c,programs,chosen):
 forward=[];cur=c['start'].copy();replacements={};details={}
 for phase,events in split(programs['forward']):
  forward.append(['phase',phase]);out=[];d={};removed=0;changed=0;old_scales=0
  for event in events:
   if event[0]=='climb':cur[event[2]]=event[4]
   if event[0]!='scalar' or phase not in chosen:out.append(copy.deepcopy(event));continue
   op=event[1];need(op[0] in ('add','scale'),'unexpected A/B macro')
   if op[0]=='scale':old_scales+=1
   if op[0]=='scale' and op[1][1] in chosen[phase]:
    r=op[1][1];d[r]=d.get(r,Q(1))*Q(op[2],op[3]);removed+=1
   else:
    new=copy.deepcopy(event)
    if op[0]=='add':
     t,s=op[1][1],op[2][1];q=Q(op[3],op[4])*d.get(s,Q(1))/d.get(t,Q(1))
     changed+=q!=Q(op[3],op[4]);new[1][3:5]=[q.numerator,q.denominator]
    out.append(new)
  if phase in chosen:
   tail=[['scalar',['scale',['L',r],q.numerator,q.denominator],cur[r]] for r,q in sorted(d.items()) if q!=1]
   out+=tail;replacements[phase]=out
   details[phase]={'selected':sorted(chosen[phase]),'original_scales':old_scales,'removed_scales':removed,
    'boundary_scales':len(tail),'changed_ADD_coefficients':changed,'boundary_scale_events':tail}
  forward+=out
 backward=[]
 for phase,events in split(programs['backward']):
  backward.append(['phase',phase])
  if phase not in chosen:backward+=copy.deepcopy(events);continue
  original=dict(split(programs['forward']))[phase]
  expected=[['scalar',dual(e[1]),e[2]] if e[0]=='scalar' else e for e in original]
  need(events==expected,'original stage primal/dual pairing')
  backward += [['scalar',dual(e[1]),e[2]] if e[0]=='scalar' else copy.deepcopy(e) for e in replacements[phase]]
 result={'forward':forward,'backward':backward}
 for direction in result:
  need([e for e in result[direction] if e[0]!='scalar']==[e for e in programs[direction] if e[0]!='scalar'],'paid/control event changed')
 return result,details

def stage_matrix(events,n):
 rows=[{i:Q(1)} for i in range(n)]
 for event in events:
  if event[0]!='scalar':continue
  e=event[1];t=e[1][1]
  if e[0]=='scale':rows[t]={k:Q(e[2],e[3])*v for k,v in rows[t].items()}
  else:
   s=e[2][1];q=Q(e[3],e[4])
   for k,v in list(rows[s].items()):
    z=rows[t].get(k,Q(0))+q*v
    if z:rows[t][k]=z
    else:rows[t].pop(k,None)
 return [[[k,str(v)] for k,v in sorted(row.items())] for row in rows]

def load_lower():
 spec=importlib.util.spec_from_file_location('pinned_dyadic_lower',ROOT/LOWER);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 return mod.lower

def coefficient_map(ps):
 keys=[('L',0),('L',1),('W',0)];rows={r:[Q(int(i==j)) for j in range(3)] for i,r in enumerate(keys)}
 for p in ps:
  tag,t=p[:2]
  if tag=='clear':rows[t]=[Q(0)]*3
  elif tag=='copy':rows[t]=rows[p[2]].copy()
  elif tag in ('add','subtract'):
   sign=1 if tag=='add' else -1;rows[t]=[a+sign*b for a,b in zip(rows[t],rows[p[2]])]
  else:
   factor={'double':Q(2),'halve':Q(1,2),'negate':Q(-1)}[tag];rows[t]=[factor*a for a in rows[t]]
 return [rows[r] for r in keys]

def check_coefficients(programs,lower):
 qs=sorted({Q(e[1][3],e[1][4]) for events in programs.values() for e in events if e[0]=='scalar' and e[1][0]=='add'})
 for q in qs:
  ps=lower(['add',['L',0],['L',1],q.numerator,q.denominator])
  need(coefficient_map(ps)==[[1,q,0],[0,1,0],[0,0,0]],'lowered coefficient map or arbitrary private dirt')
 return len(qs)

def price_and_prefix(events,lower,n):
 norm={('L',i):Q(1) for i in range(n)};norm['W',0]=Q(1);peak=Q(1);strong=old=macros=0;maxnum=maxden=1
 for e in events:
  if e[0]!='scalar':continue
  op=e[1];macros+=1;ps=lower(op);need(len(ps)==cost(op),'independent lowering count mismatch')
  strong+=len(ps);old+=cost(op,False)
  if op[0] in ('add','scale'):
   q=Q(op[3],op[4]) if op[0]=='add' else Q(op[2],op[3]);maxnum=max(maxnum,abs(q.numerator));maxden=max(maxden,q.denominator)
  for p in ps:
   tag,t=p[:2];v=norm.get(t,Q(0))
   if tag=='clear':norm[t]=Q(0)
   elif tag=='copy':norm[t]=norm.get(p[2],Q(0))
   elif tag in ('add','subtract'):norm[t]=v+norm.get(p[2],Q(0))
   elif tag=='double':norm[t]=2*v
   elif tag=='halve':norm[t]=v/2
   elif tag=='negate':pass
   else:raise ValueError('unknown lowered primitive')
   peak=max(peak,norm.get(t,Q(0)))
  if op[0]=='add':need(norm['W',0]==0,'private coefficient work not cleared')
 ceil=(peak.numerator+peak.denominator-1)//peak.denominator
 return {'scalar_macros':macros,'strong_real_primitives':2*strong,'original_Horner_real_primitives':2*old,
  'strong_primitive_prefix_upper':str(peak),'strong_primitive_prefix_bits':ceil.bit_length(),
  'max_coefficient_numerator':maxnum,'max_coefficient_denominator':maxden,'events_sha256':digest(events)}

def retained_checker(c,programs):
 # Execute only the pinned source prefix defining local(), not its driver or mutations.
 # optimize=0 is deliberate: inherited assertions stay active under our -O invocation.
 tree=ast.parse((ROOT/CHECKER).read_text());nodes=[];stopped=False
 for node in tree.body:
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='checks' for t in node.targets):stopped=True;break
  nodes.append(node)
 need(stopped,'retained checker driver boundary missing')
 with tempfile.TemporaryDirectory(prefix='replay-',dir=HERE) as td:
  p=Path(td)
  for name,obj in [('CANONICAL-WORD',c),('LOCAL-PROGRAMS',programs)]:
   (p/(name+'.json.gz')).write_bytes(gzip.compress(canonical(obj).encode(),mtime=0))
  old=sys.argv;sys.argv=[str(ROOT/CHECKER),str(p)];env={}
  try:exec(compile(ast.Module(body=nodes,type_ignores=[]),str(ROOT/CHECKER),'exec',optimize=0),env)
  finally:sys.argv=old
  return env['local']

def identity(x):need(type(x.get('seed')) is int and x['seed']==24,'exact seed 24 required')

def controls(c,original,candidate,chosen,pins,checker,lower):
 passed=[]
 def reject(name,fn):
  try:fn()
  except (ValueError,AssertionError,KeyError):passed.append(name);return
  raise ValueError('control accepted: '+name)
 reject('missing_source_pin',lambda:source(dict(list(pins.items())[1:])))
 reject('duplicate_JSON_key',lambda:loads('{"x":1,"x":2}'))
 reject('nonfinite_JSON',lambda:loads('[Infinity]'))
 reject('floating_seed',lambda:identity({'seed':24.0}))
 # Full all-column replay rejects a dropped restoration, altered coefficient and frame.
 bad=copy.deepcopy(candidate['forward']);phases=[i for i,e in enumerate(bad) if e==['phase','centers']];i=phases[0]-1
 need(bad[i][0]=='scalar' and bad[i][1][0]=='scale','expected A boundary scale')
 bad.pop(i);reject('boundary_scale_omitted',lambda:checker(bad,False))
 bad=copy.deepcopy(candidate['forward'])
 astart=bad.index(['phase','A']);j=next(j for j in range(astart+1,len(bad)) if bad[j][0]=='scalar' and bad[j][1][0]=='add')
 bad[j][1][3]*=-1;reject('ADD_sign_changed',lambda:checker(bad,False))
 bad=copy.deepcopy(candidate['forward']);i=bad.index(['phase','centers'])-1;bad[i][2]=0
 reject('boundary_scale_wrong_frame',lambda:checker(bad,False))
 bad=copy.deepcopy(candidate['forward']);i=next(i for i,e in enumerate(bad) if e[0]=='climb');bad.pop(i)
 reject('paid_climb_omitted',lambda:checker(bad,False))
 # Missing private clear can be invisible to target values; check private output explicitly.
 ps=lower(['add',['L',0],['L',1],1,1]);need(len(ps)==2,'unit ADD cost')
 reject('unit_ADD_private_clear_omitted',lambda:need(coefficient_map(ps[:-1])==[[1,1,0],[0,1,0],[0,0,0]],'private dirt survives'))
 return passed

def build(pins):
 c,original,hashes=source(pins);n=2*c['v']+c['R'];chosen,scores=select(c);candidate,details=construct(c,original,chosen)
 mats={}
 for direction in ('forward','backward'):
  for phase in ('A','B'):
   a=stage_matrix(dict(split(original[direction]))[phase],n);b=stage_matrix(dict(split(candidate[direction]))[phase],n)
   need(a==b,'independent exact stage map mismatch');mats[direction+'_'+phase]=digest(a)
 lower=load_lower();coefficient_counts={k:check_coefficients(v,lower) for k,v in [('original',original),('candidate',candidate)]}
 checker=retained_checker(c,original);audits={};prices={}
 for label,programs in [('original',original),('candidate',candidate)]:
  audits[label]={};prices[label]={}
  for direction,back in [('forward',False),('backward',True)]:
   hist,report=checker(programs[direction],back);audits[label][direction]={'profile':dict(hist),'report':report}
   prices[label][direction]=price_and_prefix(programs[direction],lower,n)
   need(prices[label][direction]['strong_primitive_prefix_bits']<=192,'primitive prefix exceeds retained allowance')
 blanket,_=construct(c,original,{p:{e[1] for e in c[p] if e[0]=='scale'} for p in ('A','B')})
 blanket_cost=2*sum(cost(e[1]) for e in blanket['forward'] if e[0]=='scalar')
 need(blanket_cost>prices['original']['forward']['strong_real_primitives'],'blanket transform must be a priced failure control')
 ctl=controls(c,original,candidate,chosen,pins,checker,lower);ctl.append('blanket_normalization_worsens_cost')
 for direction in ('forward','backward'):
  need(prices['original'][direction]['strong_real_primitives']-prices['candidate'][direction]['strong_real_primitives']==540,'composed strong gain')
  need(prices['original'][direction]['original_Horner_real_primitives']-prices['candidate'][direction]['original_Horner_real_primitives']==340,'composed Horner gain')
 receipt={'seed':24,'base':'ba82555c64e1879e4b7decce28186f208fcb8262','selected_at_base_PR':1042,
  'source_hashes':pins,'archive_members':hashes,'selected_registers':{p:sorted(rs) for p,rs in chosen.items()},
  'single_register_scores':scores,'details':details,'stage_matrix_hashes':mats,'full_audits':audits,'full_prices':prices,
  'lowered_distinct_coefficients_checked':coefficient_counts,
  'blanket_strong_forward_cost':blanket_cost,'controls':ctl,'candidate_payload_sha256':digest(candidate)}
 return receipt,candidate

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
 pins=loads((HERE/'SOURCES.json').read_bytes());result,candidate=build(pins)
 if args.write:
  (HERE/'CERTIFICATE.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
  (HERE/'CANDIDATE-PROGRAMS.json.gz').write_bytes(gzip.compress(canonical(candidate).encode(),mtime=0))
 else:
  saved=loads((HERE/'CERTIFICATE.json').read_bytes());identity(saved);need(canonical(saved)==canonical(result),'complete receipt mismatch')
  need(gzip.decompress((HERE/'CANDIDATE-PROGRAMS.json.gz').read_bytes())==canonical(candidate).encode(),'candidate canonical payload mismatch')
 print('PASS_COMPLEX_STAGE_DIAGONAL_S24 registers=41+22 gain_real_per_orientation=540 Horner_gain=340 controls='+str(len(result['controls'])))

if __name__=='__main__':main()
