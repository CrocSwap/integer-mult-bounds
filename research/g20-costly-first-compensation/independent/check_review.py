"""Independent bounded full-word review of the 35 exceptional/tied paths."""
from pathlib import Path
from collections import Counter
import gzip,json,hashlib,importlib.util,sys
HERE=Path(__file__).resolve().parent
P=HERE.parent
C=P.parents[1]
TRACE_SHA='41617a06d3abb4b3627c354199e8a8a20f4e0955f8d08b7f79835429e6cd08b6'

def need(c,s):
 if not c:raise ValueError(s)

def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

manifest=json.loads((P/'SOURCES.json').read_text())
for entry in manifest['files']:
 if entry['usage']=='input':need(hashlib.sha256((C/entry['path']).read_bytes()).hexdigest()==entry['sha256'],'authenticated input '+entry['path'])
need(hashlib.sha256((P/'trace.py').read_bytes()).hexdigest()==TRACE_SHA,'reviewed incremental engine unchanged')
T=load(P/'trace.py','trace_reviewed')
N=load(C/'research/g20-neutral-two-step-obstruction/native_floor.py','inherited_native_floor')
word=json.loads(gzip.decompress((C/'research/g20-conjugation-admission/WORD.json.gz').read_bytes()))
records=[tuple(e) for e in word['records'] if e[0] not in ('Q','ZERO_Q')]
owned=set(word['owned'])
endpoint=[0 if i in owned else (1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(685)]
frames=json.loads(gzip.decompress((C/'research/bit-g20-contact-expansion-bound/FRAMES.json.gz').read_bytes()))
edges,nodes=N.native_graph(frames['frames']);distances=N.metric(edges,nodes)
old=json.loads(gzip.decompress((C/'research/g20-neutral-two-step-obstruction/NATIVE-ONE-STEP.json.gz').read_bytes()))
serialized=[[a,[[b,distances[a][b]]for b in sorted(distances[a])]]for a in sorted(distances)]
need(hashlib.sha256(json.dumps(serialized,separators=(',',':')).encode()).hexdigest()==old['graph']['metric_sha256'],'pinned native metric equality')

def rewrite(records,description):
 left,right,a,b,count=description;need(records[left][:3]==records[right][:3]==('ADD',a,b),'equal outer gates')
 correction={};new=[]
 for k,event in enumerate(records):
  if left<k<right:
   if event[0]!='ADD':need(event[1]not in(a,b),'no owned barrier')
   else:
    _,d,s,f=event;need((d,s)!=(b,a),'no reverse contact')
    if d==b:correction[k]=('ADD',a,s,f)
    elif s==a:correction[k]=('ADD',d,b,f)
  if k not in(left,right):
   new.append(event)
   if k in correction:new.append(correction[k])
 need(len(correction)==count,'contact count')
 return new,(left,right,a,b,correction)

def full_bill(records):
 rows=[1<<i for i in range(len(word['start']))];frame=word['start'].copy();paid=Counter();nonedges=Counter()
 def visit(role,target):
  source=frame[role]
  if source!=target:
   if rows[role]:
    need(source is not None,'nonzero initialized field')
    distance=distances[source][target];paid[distance]+=1
    if (source,target)not in edges:nonedges[source,target,distance]+=1
   frame[role]=target
 for event in records:
  op,d=event[:2]
  if op in('INIT','ERASE'):
   need(d in owned and(op!='INIT'or rows[d]==0),'owned reset')
   rows[d]=0;frame[d]=event[2]
  else:
   need(op=='ADD','ADD alphabet');s,f=event[2:]
   if rows[s]:visit(d,f);visit(s,f);rows[d]^=rows[s]
 for role,target in enumerate(word['final']):
  if role in owned:need(rows[role]==0,'owned restored')
  else:visit(role,target)
 need(rows==endpoint,'all685 endpoint columns')
 return paid,nonedges

base,_=full_bill(records)
need(base=={1:1281,2:1338,3:58,4:57,5:102,6:10},'complete baseline invoice')
receipt_path=P/'CERTIFICATE.json.gz'
receipt_bytes=gzip.decompress(receipt_path.read_bytes())
receipt=json.loads(receipt_bytes);cases=receipt['exceptions']
need(len(cases)==35,'all30exceptions and5ties')
answers=[];counts=Counter()
for case in cases:
 first,fc=rewrite(records,case['first']);final,sc=rewrite(first,case['second'])
 first_bill,_=full_bill(first);bill,nonedges=full_bill(final)
 delta=[bill[r]-base[r]for r in range(1,9)]
 old_trace=T.Trace(records,word['start'],word['final'],owned,distances)
 first_trace=T.Trace(first,word['start'],word['final'],owned,distances)
 need([first_bill[r]-base[r]for r in range(9)]==old_trace.delta(fc),'first incremental invoice')
 need([bill[r]-first_bill[r]for r in range(9)]==first_trace.delta(sc),'second incremental invoice')
 expected=case.get('raw_delta',case.get('delta'))
 need(delta==list(expected),'independent exceptional raw invoice')
 strong=delta.copy()
 for (u,v,d),n in nonedges.items():
  need(d>=2 and(u,v)not in edges,'multi-edge floor hypothesis')
  strong[0]+=n;strong[d-2]+=n;strong[d-1]-=n
 hinges=[sum(min(r,k)*n for r,n in enumerate(strong,1))for k in range(1,9)]
 need(min(hinges)>=0,'complete strengthened concave hinge proof')
 kind='strict_loss'if any(hinges)else'zero';counts[kind]+=1
 if 'strengthened_delta'in case:need(strong==case['strengthened_delta'],'strengthened receipt')
 if 'nonedge_demands'in case:need([[u,v,d,n]for(u,v,d),n in sorted(nonedges.items())]==case['nonedge_demands'],'multiplicity receipt')
 sha=hashlib.sha256(json.dumps(final,separators=(',',':')).encode()).hexdigest()
 need(sha==case['word_sha256'],'full word digest')
 answers.append({'first':case['first'],'second':case['second'],'raw_delta':delta,'nonedges':[[u,v,d,n]for(u,v,d),n in sorted(nonedges.items())],'strengthened_delta':strong,'hinges':hinges,'result':kind,'word_sha256':sha})
need(counts=={'strict_loss':30,'zero':5},'complete exception outcome counts')
result={'status':'PASS_INDEPENDENT_COSTLY_FIRST_REVIEW','trace_sha256':hashlib.sha256((P/'trace.py').read_bytes()).hexdigest(),'source_receipt_sha256':hashlib.sha256(receipt_bytes).hexdigest(),'paths':35,'counts':dict(counts),'cases':answers,'limits':'All35 exceptional/tied paths independently rewritten and fully priced; full5,114,417 pair domain not independently rerun. Native edge catalogue and metric remain authenticated inherited inputs.'}
encoded=json.dumps(result,indent=2)+'\n'
if '--emit' in sys.argv:(HERE/'REVIEW-RESULT.json').write_text(encoded)
else:need((HERE/'REVIEW-RESULT.json').read_text()==encoded,'exact independent review receipt')
print(json.dumps({k:v for k,v in result.items()if k!='cases'},indent=2))
