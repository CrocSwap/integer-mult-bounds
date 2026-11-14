"""Complete packed fields versus integers, late overflow and selected contacts."""
from pathlib import Path
import sys,json,hashlib,subprocess,gzip
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
sys.dont_write_bytecode=True;sys.pycache_prefix=str(HERE/'_verify_unwritten_cache')
if Path(sys.pycache_prefix).exists():raise ValueError('verifier cache isolation path exists')
for pin in json.loads((HERE/'SOURCES.json').read_text())['files']:
 raw=(HERE/pin['local']).read_bytes()
 if len(raw)!=pin['bytes'] or hashlib.sha256(raw).hexdigest()!=pin['sha256']:
  raise ValueError('retained input drift: '+pin['local'])
import add as A
M=A.load('signed_add_machine',HERE/'inputs/machine.py')
def need(ok,message):
 if not ok:raise ValueError(message)
def gamma(n):
 if n<1:raise ValueError('positive header')
 return '0'*(n.bit_length()-1)+bin(n)[2:]
def header(shape):return ''.join(gamma(x) for x in shape)
def encode(xs,w):return ''.join(format(x%(1<<w),'0'+str(w)+'b') for x in xs)

def run_case(operation,w,shape=None,late=False):
 shape=shape or (1,1,1,1,w,1);f,r,p,s,width,cutoff=shape
 need(width==w,'shape width');n=2*p*s*r*(1<<(9*f));lo=-(1<<(w-1));hi=(1<<(w-1))-1
 points=sorted(x for x in {lo,lo+1,-1,0,1,hi-1,hi} if lo<=x<=hi)
 pairs=[(a,b) for a in points for b in points if lo<=(b-a if operation=='SUB' else b+a)<=hi]
 source=[pairs[i%len(pairs)][0] for i in range(n)];target=[pairs[i%len(pairs)][1] for i in range(n)]
 if late:source=[1]*(n-1)+([-1] if operation=='SUB' else [1]);target=[0]*(n-1)+[hi]
 h=header(shape);a=h+encode(source,w);b=h+encode(target,w)
 graph,_=A.compile_home(operation);state=M.initial((a,b),A.TAPES,old_history=3*len(a));before=bytes(state.tapes[0])
 if late:
  try:M.Program(graph).run(state)
  except M.Rejected:pass
  else:raise ValueError('true final overflow accepted')
  need(state.writes[0]==0 and bytes(state.tapes[0])==before,'late overflow mutated HOME')
  need(state.writes[2]>len(a)+1,'private arithmetic did not pass the initial gather')
 else:
  M.Program(graph).run(state)
  result=[b-a if operation=='SUB' else b+a for a,b in zip(source,target)]
  need(M.fields(state)==(a,h+encode(result,w)),'source/header or complete DATA result')
  M.check_retired(state)
 need(state.steps<4096*(len(a)+1),'complete linear bill')
 need(state.highs[-1]>=state.entry_highs[-1],'prior history dropped')
 return {'operation':operation,'shape':shape,'E':len(h),'F':len(a),'components':n,
         'states':len(graph.rules),'steps':state.steps,'overflow':late,'HOME_writes':state.writes[0],
         'source_sha256':hashlib.sha256(a.encode()).hexdigest(),
         'entry_head_spans':list(zip(state.entry_lows,state.entry_highs)),
         'final_head_spans':list(zip(state.lows,state.highs))}

def contacts():
 a=json.loads((HERE/'SOURCE-CONTACTS.json').read_text())
 expected=[(28041,['ADD',1526,1349,'-1',601]),(28129,['ADD',1526,728,'-1',601]),
           (28135,['ADD',1526,729,'-1',601]),(28139,['ADD',1526,730,'-1',601]),
           (28159,['ADD',1515,1526,'1',470])]
 need([(x['index'],x['event']) for x in a['events'] if x['event'][0]=='ADD']==expected,'selected contacts changed')
 need(a['canonical_word_sha256']=='91429a6b96729292a8764836e00c87a6f7cd3b76f05159033f4867f69a98d097','source pin')
 if '--source-repo' in sys.argv:
  repo=sys.argv[sys.argv.index('--source-repo')+1];pin=a['source']
  raw=subprocess.check_output(['git','show',pin['commit']+':'+pin['path']],cwd=repo)
  need(hashlib.sha256(raw).hexdigest()==pin['sha256'] and len(raw)==pin['bytes'],'source archive bytes')
  word=json.loads(gzip.decompress(raw))
  need(hashlib.sha256(json.dumps(word,separators=(',',':'),sort_keys=True).encode()).hexdigest()==a['canonical_word_sha256'],'complete canonical source word')
  need([(i,word['program'][i]) for i,_ in expected]==expected,'actual archive contacts')
  for x in a.get('contact_owned_lifetimes',{}).values():
   need(word['program'][x['init_index']]==x['init'] and word['program'][x['clear_index']]==x['clear'],'actual owned lifetime')
 return expected

def tagged_contacts():
 """Actual raw-native identities, not invented full compiler row addresses."""
 scope=('selected-7000-raw-native','local-occurrence-0')
 inp=lambda n:(scope,'native-productive-input',n)
 owned=lambda n,b,e:(scope,'native-owned-lifetime',n,b,e)
 bank=owned(1526,28037,37618);other=owned(1515,28153,39073)
 h=header((1,1,1,1,4,1));n=1024
 tests=[(28041,'SUB',(inp(1349),bank),(0,1),[1,0]),
        (28159,'ADD',(inp(0),bank,other),(1,2),[3,2,-1])]
 records=[]
 for index,op,owners,ports,values in tests:
  payloads=tuple(h+encode([v]*n,4) for v in values)
  graph,stages=A.compile_home(op,owners,ports,productive_count=1)
  generic,_=A.compile_home(op,tuple(range(len(owners))),ports,productive_count=1)
  need(graph.rules==generic.rules,'opaque native labels changed literal graph')
  state=M.initial(payloads[:2],A.TAPES)
  if len(payloads)>2:
   text='^'+'|'.join(payloads)+'|$';o=state.origins[0]
   state.tapes[0][o:o+len(text)]=bytes(M.SYMBOLS[c] for c in text)
   state.highs[0]=state.entry_highs[0]=o+len(text)-1
  # The supplied boundary is already reserved and typed. Do not append raw
  # owned zeros or claim to implement their earlier source INIT.
  M.Program(graph).run(state,start=graph.execution_start)
  expected=list(values);s,t=ports;expected[t]=values[t]-values[s] if op=='SUB' else values[t]+values[s]
  need(M.fields(state,len(owners))==tuple(h+encode([v]*n,4) for v in expected),'native-identity source/target/parked return')
  M.check_retired(state)
  records.append({'event_index':index,'operation':op,'owners':owners,'operand_indices':ports,
                  'productive_count':1,'K':len(owners),'body_entry':'already_reserved_and_typed',
                  'steps':state.steps,'tag_relabel_graph_identical':True,
                  'scope':'qualified raw-native identity; full #7423 compiler addresses are not generated'})
 return records

def controls():
 checks=[];w=4;h=header((1,1,1,1,w,1));n=1024
 source=h+encode([1]*n,w);target=h+encode([0]*n,w)
 wrong,_=A.compile_home('ADD');state=M.initial((source,target),A.TAPES);M.Program(wrong).run(state)
 need(M.fields(state)!=(source,h+encode([-1]*n,w)),'wrong sign graph escaped')
 checks.append('wrong_fixed_coefficient_sign')
 good,_=A.compile_home('SUB');program=M.Program(good)
 hs=header((1,1,1,1,w,2));ht=header((1,1,1,1,w,3))
 mismatch=M.initial((hs+encode([0]*n,w),ht+encode([0]*n,w)),A.TAPES)
 try:program.run(mismatch)
 except M.Rejected:need(mismatch.writes[0]==0,'header failure changed HOME')
 else:raise ValueError('mismatched equal-length headers accepted')
 checks.append('mismatched_equal_length_headers')
 low=-(1<<(w-1));state=M.initial((h+encode([low]*n,w),h+encode([low]*n,w)),A.TAPES)
 program.run(state);need(M.fields(state)[1]==h+encode([0]*n,w),'minimum-source cancellation rejected')
 M.check_retired(state);checks.append('minimum_source_subtraction_cancellation')
 # Literal component boundary only, not a full f2 field. The current selected
 # convention leaves exterior -1 unchanged when contextual f=2 is even.
 got={}
 for mode in ('SUB','ADD'):
  g=A.D.Graph();stages={};A.primitive(g,mode,2,'HALT',stages)
  g.start=stages['component_entry'];g.validate();s=M.initial(('0','0'),A.TAPES)
  for t,text in [(1,'^01|'),(2,'^00|'),(4,'^11')]:
   o=s.origins[t];s.tapes[t][o:o+len(text)]=bytes(M.SYMBOLS[c] for c in text)
  for t in range(1,6):s.heads[t]=s.origins[t]+1
  M.Program(g).run(s)
  o=s.origins[2];bits=''.join('_01^|$'[x] for x in s.tapes[2][o+1:o+3]);v=int(bits,2)
  got[mode]=v-4 if v>=2 else v
  need(s.heads==s.origins,'component-boundary head return')
 need(got=={'SUB':-1,'ADD':1},'even-f tensorized scalar convention escaped')
 checks.append('even_f_exterior_minus_one_not_tensor_phase_component_boundary')
 return checks

def verify():
 bound=contacts();cases=[]
 for operation in ('ADD','SUB'):
  for w in (2,3,4,5,8,17):cases.append(run_case(operation,w))
  cases.append(run_case(operation,3,shape=(1,2,2,3,3,1)))
  cases.append(run_case(operation,4,shape=(1,1,1,1,4,1<<2048)))
  for w in (2,4,8):cases.append(run_case(operation,w,late=True))
 return {'marker':'PASS_SOURCE_BOUND_SIGNED_HOME_ADD','contacts':bound,'cases':cases,'controls':controls(),
         'native_identity_fixtures':tagged_contacts(),'tapes':A.TAPES,
         'scope':'fixed ±1 source contacts, same valid Γ6 headers/common grid; producer, rank2 MOVE and complete lifetime remain outside scope',
         'history_boundary':'K_entry includes opaque exterior storage and earlier history; monitored windows do not infer it.'}

if __name__=='__main__':
 r=verify();raw=json.dumps(r,indent=2,sort_keys=True)+'\n'
 if '--write' in sys.argv:(HERE/'RESULT.json').write_text(raw)
 elif (HERE/'RESULT.json').exists():need(json.loads((HERE/'RESULT.json').read_text())==json.loads(raw),'receipt changed')
 print(raw,end='')
