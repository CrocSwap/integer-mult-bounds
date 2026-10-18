#!/usr/bin/env python3
"""Exact selected boundary phases; DLamdata with Codex assistance, Apache-2.0.
Independent phase derivation; credited exact Clifford kernel for local labels.
"""
from pathlib import Path
import gzip, hashlib, json, tarfile, types, argparse
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ARCHIVE='research/community-frontier1094-audit/selected-replay.tar.gz'
ARCHIVE_SHA='f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6'
MEMBERS={
 'phases':('candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json','c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'),
 'template':('candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz','2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760'),
 'word':('candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz','16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219'),
 'recipes':('candidate/strict/global/base/providers/gauge44/CLIFFORD-RECIPES.json','d0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731'),
 'programs':('candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz','241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a')}
M=73

def require(ok,msg):
 if not ok: raise ValueError(msg)

def digest(raw):return hashlib.sha256(raw).hexdigest()

def load():
 raw=(ROOT/ARCHIVE).read_bytes();require(digest(raw)==ARCHIVE_SHA,'archive drift')
 out={}
 with tarfile.open(ROOT/ARCHIVE,'r:gz') as tar:
  for key,(name,sha) in MEMBERS.items():
   matches=[m for m in tar.getmembers() if m.name==name]
   require(len(matches)==1 and matches[0].isfile(),'unique regular archive member')
   data=tar.extractfile(matches[0]).read();require(digest(data)==sha,'member drift '+key)
   out[key]=json.loads(gzip.decompress(data) if name.endswith('.gz') else data)
 return out

def bits(v):
 out=[]
 while v:
  b=v&-v;out.append(b.bit_length()-1);v-=b
 return out

def apply(cols,x):
 value=0
 for i in bits(x):value^=cols[i]
 return value

def route(q,basis,s):
 cols=[1<<i for i in range(M)]
 if not s:return cols
 swaps=[a^(1<<(9+8*(s-1)+j)) for j,a in enumerate(basis)]
 return [x ^ sum_xor([v for v in swaps if (v&x).bit_count()%2]) for x in cols]

def sum_xor(xs):
 value=0
 for x in xs:value^=x
 return value

def signature(lines,translation=0):
 """Exact coefficient vector: constant0, linear Z4, twice binary cross-terms."""
 linear=[0]*M;cross=[0]*M
 for axis,sign in lines:
  require(0<axis<(1<<M) and sign in (-1,1),'bad signed line')
  loc=bits(axis)
  for i in loc:
   linear[i]=(linear[i]+sign)%4
   cross[i]^=sum(1<<j for j in loc if j>i)
 for i in bits(translation):linear[i]=(linear[i]+2)%4
 return tuple(linear),tuple(cross)

def literal(lines,translation,u):
 return (sum(sign*((axis&u).bit_count()%2) for axis,sign in lines)
         +2*((translation&u).bit_count()%2))%4

def evaluate_signature(sig,u):
 linear,cross=sig
 return (sum(linear[i] for i in bits(u))+2*sum((cross[i]&u).bit_count()%2 for i in bits(u)))%4

def coordinate(lo,hi):return [(1<<i,1) for i in range(lo,hi)]

def gauges(q,s):
 if s==-1:return [(q,1)],[]
 x=coordinate(0,9+8*s)
 return x,x+[(q,-1)]

def routed(lines,cols):return [(apply(cols,a),sign) for a,sign in lines]

def check():
 d=load();p=d['phases'];g=d['template']
 require(p['m']==g['m']==M and p['ports']==len(p['recipes'])==112,'selected dimension drift')
 require(len(g['calls'])==144,'selected call count drift')
 require(g['calls'][0]['stage']==0 and g['calls'][4]['stage']==1 and g['calls'][10]['stage']==2,'call stages')
 identities=0;faults={k:0 for k in ('omit_entry','omit_exit','wrong_Y_sign','unrouted_translation')};literal_checks=0
 records=[]
 for port,r in enumerate(p['recipes']):
  q=r['q'];basis=r['idle_children'][0]['orthogonal_axes'][:8]
  require(0<q<512 and q.bit_count()%2==1,'normal')
  chart=[q]+basis
  require(len(set(chart))==9 and all((a&b).bit_count()%2==(i==j) for i,a in enumerate(chart) for j,b in enumerate(chart)),'chart')
  for s in range(9):
   cols=route(q,basis,s)
   require(all(apply(cols,apply(cols,1<<i))==1<<i for i in range(M)),'route inverse')
   require(all((a&b).bit_count()%2==(i==j) for i,a in enumerate(cols) for j,b in enumerate(cols)),'route orthogonality')
   require(apply(cols,q)==q,'route fixes q')
   if s:
    require(all(apply(cols,b)==1<<(9+8*(s-1)+j) for j,b in enumerate(basis)),'chart exchange')
   align=r['stage_alignment'][s]
   prev=gauges(q,s-1);nxt=gauges(q,s)
   ext=coordinate(9,9+8*s)
   local_entry=([(q,1)]+ext,ext)
   local_exit=(coordinate(0,9)+ext,coordinate(0,9)+ext+[(q,-1)])
   for k,label in enumerate(('X','Y')):
    ein=apply(cols,align['entry_'+label]);eout=apply(cols,align['exit_'+label])
    il=routed(prev[k],cols);ir=local_entry[k]
    ol=local_exit[k];orr=routed(nxt[k],cols)
    require(signature(il,ein)==signature(ir),'entry phase %d/%d/%s'%(port,s,label))
    require(signature(ol,eout)==signature(orr),'exit phase %d/%d/%s'%(port,s,label))
    identities+=2
    if s:
     faults['omit_entry']+=signature(il)!=signature(ir)
     faults['omit_exit']+=signature(ol)!=signature(orr)
     faults['unrouted_translation']+=signature(il,align['entry_'+label])!=signature(ir)
    if label=='Y':
     wrong=coordinate(0,9)+ext+[(q,1)]
     faults['wrong_Y_sign']+=signature(wrong,eout)!=signature(orr)
    # Independent direct character evaluation only at the needed s=0/1 boundary.
    # All coefficients at all stages were already checked above.
    if s<=1:
     tests=[0]+[1<<i for i in range(M)]+[(1<<i)|(1<<j) for i in range(M) for j in range(i+1,M)]
     sig=signature(il,ein)
     for u in tests:
      require(literal(il,ein,u)==literal(ir,0,u)==evaluate_signature(sig,u),'literal entry control')
      require(literal(ol,eout,u)==literal(orr,0,u),'literal exit control')
      literal_checks+=2
   records.append({'port':port,'stage':s,'q':q,'rho_sha256':digest(json.dumps(cols,separators=(',',':')).encode()),'entry':align['entry_X'],'exit':align['exit_X']})
 require(all(v>0 for v in faults.values()),'ineffective phase fault')
 # Authenticate the literal direction: exact scalar endpoints, no inherited verifier import.
 from fractions import Fraction as Q
 scalar_checks={}
 for orientation,program in d['programs'].items():
  if orientation not in ('forward','backward'):continue
  state={('L',i):{i:Q(1)} for i in range(704)}
  for event in program:
   if event[0]!='scalar':continue
   op=event[1];kind=op[0];dst=tuple(op[1])
   if kind=='clear':state[dst]={}
   elif kind=='copy':state[dst]=dict(state[tuple(op[2])])
   elif kind=='scale':state[dst]={i:v*Q(op[2],op[3]) for i,v in state[dst].items() if v*Q(op[2],op[3])}
   elif kind=='add':
    src=tuple(op[2]);factor=Q(op[3],op[4]);require(dst!=src,'self add')
    for i,v in state[src].items():
     value=state[dst].get(i,Q(0))+factor*v
     if value:state[dst][i]=value
     else:state[dst].pop(i,None)
   else:raise ValueError('scalar opcode')
  for i in range(704):
   want={i:Q(1)}
   if orientation=='forward' and 112<=i<224:want[i-112]=Q(1)
   if orientation=='backward' and i<112:want[i+112]=Q(-1)
   require(state['L',i]==want,'signed local endpoint '+orientation)
  require(all(not row for key,row in state.items() if key[0]!='L'),'private scalar exit')
  scalar_checks[orientation]={'events':len(program),'ordinary_rows':704,'endpoint':'(D,T+D,h)' if orientation=='forward' else '(D-T,T,h)'}
 # Bind all four exact local endpoint labels, using the explicitly credited
 # authenticated Clifford equality kernel (this is not a new kernel proof).
 kernel_path=ROOT/'research/frontier1094-recipes-exact-seed76/clifford.py'
 kernel_raw=kernel_path.read_bytes()
 require(digest(kernel_raw)=='d5e42ddabd141b7bfbd70fe13908f3c3a06aeccebeab90623596bfb1988b97fb','kernel drift')
 C=types.ModuleType('pinned_boundary_clifford');C.__file__=str(kernel_path)
 exec(compile(kernel_raw,str(kernel_path),'exec'),C.__dict__)
 word=d['word'];require((word['h'],word['v'],word['R'])==(9,112,480),'word dimensions')
 require(list(word['ports'])==[r['q'] for r in p['recipes']],'phase/word normals')
 adapters={(r['role'],r['port']):r for r in d['recipes']['endpoint_adapters']}
 label_checks=0
 for port,q in enumerate(word['ports']):
  before_x=C.canonical_frame(word['frames'][word['start'][port]])+C.adjoint(C.monomial(adapters['source',port]['left']))
  before_y=C.canonical_frame(word['frames'][word['start'][112+port]])
  after_x=C.canonical_frame(word['frames'][word['final'][port]])
  after_y=C.canonical_frame(word['frames'][word['final'][112+port]])+C.adjoint(C.monomial(adapters['target',port]['left']))
  for actual,expected in [(before_x,[('C',q,1)]),(before_y,[]),(after_x,C.fourier(9)),(after_y,[('C',q,-1)]+C.fourier(9))]:
   require(C.same_operator(actual,expected),'exact signed local endpoint label')
   label_checks+=1
 return {'status':'PASS_SELECTED_NATIVE_BOUNDARY_PHASES','archive_sha256':ARCHIVE_SHA,'members':MEMBERS,'m':M,'ports':112,'stages':9,'exact_boundary_operator_identities':identities,'direct_character_equality_checks_s0_s1':literal_checks,'rejected_fault_instances':faults,'scalar_endpoint_binding':scalar_checks,'exact_local_endpoint_label_comparisons':label_checks,'credited_clifford_kernel_sha256':digest(kernel_raw),'phase_registry_sha256':digest(json.dumps(records,sort_keys=True,separators=(',',':')).encode()),'scope':'Exact Fourier polynomial boundary phases plus scalar sign binding; inherits complete local native common-frame factorization and physical cover/view semantics.'}
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--write',type=Path);args=parser.parse_args()
 if args.write and args.write.exists():raise FileExistsError(args.write)
 result=check()
 if args.write:
  with args.write.open('x',encoding='utf-8',newline='\n') as out:out.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
 else:
  expected=json.loads((HERE/'NATIVE.json').read_bytes())
  require(json.dumps(expected,sort_keys=True)==json.dumps(result,sort_keys=True),'complete native receipt mismatch')
 print('PASS_SELECTED_NATIVE_BOUNDARY_PHASES identities=4032 determining_characters=2420992 local_labels=448')
