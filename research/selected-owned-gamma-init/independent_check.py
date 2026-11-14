"""Independent sparse-tape/chronology check of worker B's typed INIT/CLEAR."""
from pathlib import Path
import gzip,hashlib,importlib.util,json,sys
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('reviewed_typed_init',P/'init.py')
I=importlib.util.module_from_spec(spec);sys.modules[spec.name]=I
exec(compile((P/'init.py').read_bytes(),str(P/'init.py'),'exec'),I.__dict__)

def need(ok,msg):
 if not ok:raise ValueError(msg)

def execute(g,mem,heads,start=None):
 q=g.start if start is None else start;steps=0;low=heads[:]
 while q!='HALT':
  candidates=[r for r in g.rules[q] if all(mem[t].get(heads[t],'_')==s for t,s in r.tests)]
  need(len(candidates)==1,'literal determinism/entry');r=candidates[0]
  for t,s in r.writes:mem[t][heads[t]]=s
  for t,d in r.moves:
   need(d in (-1,0,1),'unit moves');heads[t]+=d;low[t]=min(low[t],heads[t])
  q=r.target;steps+=1
  need(steps<5_000_000,'finite review budget')
 return steps,low

def gamma(n):
 s=format(n,'b');return '0'*(len(s)-1)+s

def packet(shape):
 f,r,p,s,w,c=shape;h=''.join(map(gamma,shape));V=2*p*s*r*(1<<(9*f))*w
 data=('10100111001001'*((V+13)//14))[:V]
 return h+data,h,V

def tape(text,origin):return {origin+i:s for i,s in enumerate(text)}|{origin-3:'X'}

def primitive_case(shape):
 body,h,V=packet(shape);F=len(body);orig=[5,8,11,14]
 target=''.join('1' if x=='0' else '0' for x in body)
 mem=[tape('^',orig[0]),tape('^'+body+'|',orig[1]),tape('^'+target+'|',orig[2]),tape('^',orig[3])]
 before=[dict(x) for x in mem];heads=orig[:]
 g=I.D.Graph();g.start=I.primitive(g,'INIT',2,'HALT');g.validate()
 steps,low=execute(g,mem,heads);A=sum(n.bit_length()-1 for n in shape)
 need(steps==3*A+V+2*F+20,'independent exact INIT count')
 need(steps<=4*F+8,'uniform INIT bound')
 expect='^'+h+'0'*V+'|'
 need(''.join(mem[2].get(orig[2]+j,'_') for j in range(F+2))==expect,'dirty inactive target typed zero')
 need(mem[0]==before[0] and mem[1]==before[1],'donor/home untouched')
 need(heads==orig and all(lo>=o for lo,o in zip(low,orig)),'INIT relative origins')
 need(all(s=='_' or k<=orig[3] for k,s in mem[3].items()),'prefix guide erased')
 clear=I.D.Graph();clear.start=I.primitive(clear,'CLEAR',1,'HALT');clear.validate()
 cm=[tape('^',orig[0]),tape('^'+expect[1:-1]+'|',orig[1]),tape('^',orig[2]),tape('^',orig[3])];ch=orig[:]
 csteps,_=execute(clear,cm,ch)
 need(csteps==2*F+4,'independent exact CLEAR count')
 need(''.join(cm[1].get(orig[1]+1+j,'_') for j in range(F))=='0'*F,'full header and DATA erasure')
 need(ch==orig,'CLEAR head returns')
 return {'shape':shape,'F':F,'INIT_steps':steps,'CLEAR_steps':csteps}

def cold_home():
 from collections import namedtuple
 Event=namedtuple('Event','service owners')
 owners=(('public','donor'),('public','parked'),('owned',1526,28037,37618))
 body,_,_=packet((1,1,1,1,2,1));parked=body[::-1];F=len(body)
 events=[Event('INIT',(owners[0],owners[2])),Event('CLEAR',(owners[2],))]
 g=I.compile_home(events,owners,2)
 orig=[5,8,11,14];mem=[tape('^'+body+'|'+parked+'|$',orig[0])]+[tape('^',o) for o in orig[1:]]
 heads=orig[:];steps,low=execute(g,mem,heads)
 expected='^'+body+'|'+parked+'|'+'0'*F+'|$'
 need(''.join(mem[0].get(orig[0]+j,'_') for j in range(len(expected)))==expected,'cold reservation/INIT/CLEAR HOME image')
 need(heads==orig and all(lo>=o for lo,o in zip(low,orig)),'HOME/primitive return')
 for i in range(1,4):need(all(s=='_' or k<=orig[i] for k,s in mem[i].items()),'all private cohorts retired')
 return {'steps':steps,'F':F,'K':3,'productive':2}

def inventory():
 raw=(P/'inputs/selected-native.json.gz').read_bytes()
 need(hashlib.sha256(raw).hexdigest()=='2b94953dc14a122e3ef089633f05b58ec689ec5156feb7c784ed3e137dc01883','selected archive')
 w=json.loads(gzip.decompress(raw));live={k:v for k,v in enumerate(w['initial'])};openings={};pairs=[]
 for i,e in enumerate(w['program']):
  op=e[0];a=e[1]
  if op=='INIT':
   need(a>=w['public'] and a not in live and 0 in live,'fresh owned lifetime with live public donor')
   openings[a]=(i,e[2]);live[a]=e[2]
  elif op=='CLEAR':
   need(a in openings and live[a]==e[2] and a>=w['public'],'matched owned retirement')
   start,frame=openings.pop(a);pairs.append((start,i,a,frame,e[2]));del live[a]
  elif op=='MOVE':
   need(live.get(a)==e[2] and bool(e[4])==(a>=w['public']),'MOVE exact source frame and ownership')
   live[a]=e[3]
  elif op in ('ADD','COPY'):need(live.get(a)==live.get(e[2])==e[4],'binary actual frames')
  elif op=='SCALE':need(live.get(a)==e[3],'SCALE current frame')
  else:raise ValueError('opcode')
 need(not openings and set(live)==set(range(w['public'])),'all owned lifetimes closed')
 pairs.sort();counts={}
 for row in pairs:counts[row[2]]=counts.get(row[2],0)+1
 need(len(pairs)==54 and len(counts)==51 and w['public']==1480,'54/51/1480 inventory')
 return {'events':len(w['program']),'lifetimes':len(pairs),'labels':len(counts),'distinct_historical_homes':1480+len(pairs),
         'reused':{str(k):v for k,v in counts.items() if v>1},'inventory_sha256':hashlib.sha256(json.dumps(pairs).encode()).hexdigest()}

def mutation():
 g=I.D.Graph();g.start=I.primitive(g,'CLEAR',1,'HALT')
 for q,rules in g.rules.items():
  for j,r in enumerate(rules):
   if r.writes==((1,'0'),) and (1,'1') in r.tests:rules[j]=I.D.Rule(r.tests,(),r.moves,r.target)
 mem=[{0:'^'} for _ in range(4)];mem[1]=tape('^11101|',0);heads=[0]*4
 execute(g,mem,heads)
 need(''.join(mem[1].get(1+j,'_') for j in range(5))!='00000','missing nonzero CLEAR write detected')
 return 'detected'

print(json.dumps({'status':'PASS_INDEPENDENT_TYPED_INIT_CLEAR','init_sha256':hashlib.sha256((P/'init.py').read_bytes()).hexdigest(),
 'primitive_cases':[primitive_case(s) for s in [(1,1,1,1,2,1),(1,2,1,2,3,(1<<128)+5),(1,1,1,1,1,(1<<2048)+7)]],
 'cold_home':cold_home(),'source_inventory':inventory(),'CLEAR_write_mutation':mutation()},indent=2))
