from pathlib import Path
import json,struct,hashlib,math,sys,argparse
sys.dont_write_bytecode=True
if not __debug__: raise SystemExit('Assertions required; refusing -O')
from collections import Counter
ap=argparse.ArgumentParser(); ap.add_argument('--export-dir',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); args=ap.parse_args()
X=args.export_dir.resolve(); D=args.output.resolve();D.mkdir(parents=True,exist_ok=False)
st=json.loads((X/'gen4-states.json').read_text());n=st['n'];v=st['v'];fs={int(k):x for k,x in json.loads((X/'frames.json').read_text())['frames'].items()}
rows=json.loads((Path(__file__).resolve().parents[1]/'data/retiming880.json').read_text());selected={}
for r in rows:
 if r['new_frame'] in fs and r['component'] not in selected:selected[r['component']]=r
assert len(selected)==880
roleuses=Counter(s for r in selected.values()for s in r['roles']);assert len(roleuses)==v and set(roleuses.values())=={1} and all(s<v for s in roleuses)
replacements={g:r['new_frame']for r in selected.values()for g in r['gates']};assert len(replacements)==880
raw=list(struct.iter_unpack('<6i',(X/'gen4-records.bin').read_bytes()));basepairs={(e[2],e[3])for e in raw if e[0]==0};initial={int(k):f for k,f in st['initial'].items()};final={int(k):f for k,f in st['final'].items()};state=dict(initial);out=[];pairs=set();changedpairs=set();core=0;copy=None;H=Counter();oldH=Counter()
for op,a,b,c,f,z in raw:
 if op==0 and f:oldH[f]+=1
 elif op==2:oldH[z]+=1
def sub(a,b):return fs[a]['dim']<=fs[b]['dim'] and all(sum(x*y for x,y in zip(u,w))==0 for u in fs[a]['B']for w in fs[b]['A'])
# Data roles form a closed scalar subword. Track defining integer source
# coefficients to audit both operands before and after each changed shear.
source_columns=[{i:1} for i in range(v)]
assert all(fs[initial[i]]['dim']==1 for i in range(v))
source_vectors={i:fs[initial[i]]['B'][0] for i in range(v)}
span_checks=0;span_sizes={}
def span_in_frame(coefficients,f):
 return all(all(sum(x*y for x,y in zip(source_vectors[i],w))==0 for w in fs[f]['A']) for i in coefficients)
def move(a,f):
 old=state[a]
 if old==f:return
 pair=(old,f)
 if pair not in pairs:
  if pair not in basepairs:assert sub(old,f);changedpairs.add(pair)
  pairs.add(pair)
 rank=fs[f]['dim']-fs[old]['dim'];assert rank>=0
 out.append((0,a,old,f,rank,0));state[a]=f
 if rank:H[rank]+=1
for op,a,b,c,f,z in raw:
 if op==0:continue
 if op==1:

  if core in replacements:
   binding=selected[core];assert op==1 and f==binding['old_frame'] and sorted([a,b])==sorted(binding['roles'])
   assert fs[f]['dim']==2 and fs[binding['new_frame']]['dim']==22
   assert sub(f,binding['new_frame']), 'Retimed old frame must lie inside the new frame'
   assert 0<=a<v and 0<=b<v
   for operand in (a,b):
    assert span_in_frame(source_columns[operand],f) and span_in_frame(source_columns[operand],binding['new_frame'])
    span_checks+=len(source_columns[operand])
  f=replacements.get(core,f);move(a,f);move(b,f);assert state[a]==state[b]==f
  if a<v:
   assert 0<=b<v, 'Data source roles must receive only data-source values'
   for source,value in list(source_columns[b].items()):
    value=source_columns[a].get(source,0)+c*value
    if value:source_columns[a][source]=value
    else:source_columns[a].pop(source,None)
  if core in replacements:
   assert span_in_frame(source_columns[a],f) and span_in_frame(source_columns[b],f)
   span_checks+=len(source_columns[a])+len(source_columns[b]);span_sizes[core]=len(set(source_columns[a])|set(source_columns[b]))
  out.append((op,a,b,c,f,z))
 elif op==2:
  assert copy is None and b==n;move(a,c);state[b]=f;copy=(a,b,c,f);H[z]+=1;out.append((op,a,b,c,f,z))
 else:
  assert op==3 and copy==(a,b,c,f) and state[a]==c and state[b]==f;out.append((op,a,b,c,f,z));del state[b];copy=None
 core+=1
assert copy is None and len(span_sizes)==880 and set(span_sizes.values())=={2}
assert source_columns==[{i:1}for i in range(v)]
for a in range(n):move(a,final[a])
assert state==final
def project(es):return [(op,a,b,c,z)for op,a,b,c,f,z in es if op]
assert project(raw)==project(out)
delta=Counter(H);delta.subtract(oldH);delta={r:x for r,x in delta.items()if x}
assert delta=={21:1760,2:880,1:-1760,20:-880,22:-880}
assert sum(r*x for r,x in delta.items())==0
data=b''.join(struct.pack('<6i',*e)for e in out)
(D/'COHORT249-RECORDS.bin').write_bytes(data)
(D/'COHORT249-INITIAL.json').write_text(json.dumps(st['initial'])+'\n')
(D/'COHORT249-FRAMES.json').write_text('{}\n')
(D/'COHORT249-FINAL.json').write_text(json.dumps(st['final'])+'\n')
(D/'RETIMING-SELECTION.json').write_text(json.dumps(list(selected.values()),indent=2)+'\n')
receipt=dict(old_frame_containment_explicit=True,exact_integer_source_spans=True,checked_operand_source_inclusions=span_checks,max_changed_gate_source_support=max(span_sizes.values()),status='PASS_880_DISJOINT_RETIMINGS_LITERAL_SCALAR_EQUALITY_AND_NEW_CONNECTOR_GEOMETRY',base_sha256=hashlib.sha256((X/'gen4-records.bin').read_bytes()).hexdigest(),output_sha256=hashlib.sha256(data).hexdigest(),n=n,v=v,selected_gates=len(replacements),source_roles=len(roleuses),new_frame_ids=0,changed_connector_pairs=sorted(changedpairs),paid_histogram=dict(H),local_histogram_delta=delta,rank_mass=sum(r*x for r,x in H.items()),record_count=len(out),scope='Full baseline checks and fresh five-stage replay are separate; all changed connector inclusions checked by exact integer dot products. No exponent claimed by this emitter.')
(D/'RETIMING-REPLAY.json').write_text(json.dumps(receipt,indent=2)+'\n')
print({k:v for k,v in receipt.items()if k not in ['changed_connector_pairs','paid_histogram']},flush=True)

assert receipt['output_sha256']=='2d22a9530f0b04a7a794d15077459234ef52183d6e7a70f813cfa849b79f2ebe'
(D/'249-states.json').write_text(json.dumps(st)+'\n')
