"""Generate exact rational triple certificates; no external dependencies.
Jerry Chen / @CubeJerry, substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from pathlib import Path
from types import SimpleNamespace
import json,sys,runpy
HERE=Path(__file__).resolve().parent
C=SimpleNamespace(**runpy.run_path(str(HERE/'core.py')))

def gf2_contains(smaller,larger):
 basis={}
 for value in larger:
  while value:
   pivot=value.bit_length()-1
   if pivot not in basis:basis[pivot]=value;break
   value^=basis[pivot]
 C.need(len(basis)==len(larger),'Independent frame basis')
 for value in smaller:
  for pivot in sorted(basis,reverse=True):
   if(value>>pivot)&1:value^=basis[pivot]
  if value:return False
 return True

def frame_space(vectors):
 basis={}
 for value in vectors:
  while value:
   pivot=value.bit_length()-1
   if pivot in basis:value^=basis[pivot]
   else:basis[pivot]=value;break
 C.need(len(basis)==len(vectors),'Independent relevant frame basis')
 for pivot in sorted(basis):
  for higher in basis:
   if higher>pivot and(basis[higher]>>pivot)&1:basis[higher]^=basis[pivot]
 return tuple(sorted(basis.values()))

def forward_error(word,triple,target):
 program,n=word['program'],word['public'];error=[Q(0)]*(n+word['owned_fields']);observed={}
 exports=set(triple['exports']);factor=Q(1);copy_index=0;copies=sum(e[0]=='COPY'for e in program)
 for i,entry in enumerate(program):
  operation,role=entry[:2]
  if operation=='COPY':
   if error[role]:observed[n+copies-1-copy_index]=error[role]
   copy_index+=1
  if i in exports:
   C.need(error[entry[2]]==0,'No held-source feedback before deleted export')
   error[role]-=Q(entry[3])*factor
  elif operation in('ADD','COPY'):error[role]+=Q(entry[3])*error[entry[2]]
  elif operation=='SCALE':error[role]*=Q(entry[2])
  elif operation in('INIT','CLEAR'):error[role]=Q(0)
  if triple['first']<i<triple['last']and operation=='SCALE'and role==triple['role']:factor*=Q(entry[2])
 observed.update({r:error[r]for r in range(n)if word['final'][r]!=127 and error[r]})
 C.need(observed=={k:-v for k,v in target.items()},'Exact forward combined-deletion target')

def controls():
 columns=[{0:Q(1),1:Q(2)},{1:Q(1),2:Q(3)}]
 inside={0:Q(4),1:Q(13),2:Q(15)};outside={0:Q(4),1:Q(13),2:Q(16)}
 C.need(C.span(columns,inside)[0]and C.dual(columns,inside)is None,'Positive exact span')
 C.need(not C.span(columns,outside)[0]and C.dual_ok(C.dual(columns,outside),columns,outside),'Negative exact span')
 C.need(C.span([],{})==(True,0)and C.dual([],{})is None,'Zero target admitted')
 C.need(not C.span([],{0:Q(1)})[0]and C.dual_ok(C.dual([],{0:Q(1)}),[],{0:Q(1)}),'Nonzero empty span rejected')
 return 4

def generate():
 controls_count=controls();word=C.load_word();intervals,groups,triples,writes,reads,summary=C.census(word)
 C.need(summary==dict(intervals=631,classes=523,class_sizes={1:429,2:80,3:14},triples=14,copy_zero_checks=1,public_inputs=771,endpoint_rows=800),'Complete frozen census')
 residences,after,monitors=C.suffix(word);records=[];dots=0;mutation_controls=0;topologies=0
 frame_spaces=[frame_space(frame)for frame in word['frames']]
 for triple in sorted(triples,key=lambda c:c['role']):
  role=triple['role'];frames=triple['frames'];target=C.target(word,triple,writes,after)
  C.need(all(frame_spaces.count(frame_spaces[f])==1 for f in frames),'No aliased subspace omitted from a relevant frame inventory')
  C.need(target,'Nonzero combined target')
  C.need(all(word['program'][z][0]in('SCALE','MOVE')for z in writes[role]if triple['lo']<=z<triple['hi']),'Entire-window no-feedback premise')
  C.need(all(gf2_contains(word['frames'][a],word['frames'][b])for a,b in zip(frames,frames[1:])),'Nested GF2 frame spans')
  forward_error(word,triple,target)
  allnodes=C.topology_nodes(triple,residences,(0,1,2,3,4));allcolumns=C.columns_at(allnodes,triple['moves'],5)
  C.need(C.span(allcolumns,target)[0],'Full-frame original-chronology positive control')
  # Each old export can be reinserted at its actual old cut and recipient.
  reinstated={}
  for z in triple['exports']:
   entry=word['program'][z];receiver=entry[1];response=after[z]
   candidates=[dict(v)for r,l,h,f,v in residences if r==receiver and l<=z<=h and f==entry[4]]
   C.need(response in candidates,'Original export response available at its precise residence')
   factor=Q(entry[3])
   for i in writes[role]:
    if triple['first']<i<z and word['program'][i][0]=='SCALE':factor*=Q(word['program'][i][2])
   C.add(reinstated,response,factor)
  C.need(reinstated==target,'Exact original-export reinsertion')
  witnesses=[]
  for omitted in(1,2,3):
   keep=tuple(i for i in range(5)if i!=omitted);nodes=C.topology_nodes(triple,residences,keep)
   columns=[dict(v)for v in sorted({v for l,h,k,v in nodes})]
   witness=C.dual(columns,target);C.need(witness is not None,'Maximal omission is separated')
   hit,rank=C.span(columns,target);C.need(not hit,'Independent pivot-direction span rejection')
   C.need(C.dual_ok(witness,columns,target),'All rational dual equations')
   pivot=next(iter(witness));mutated=target.copy();C.add(mutated,{pivot:Q(1)/witness[pivot]})
   C.need(not C.dual_ok({},columns,target),'Reject zero witness')
   C.need(not C.dual_ok(witness,columns+[{pivot:Q(1)}],target),'Reject added forbidden response')
   C.need(not C.dual_ok(witness,columns,mutated),'Reject altered target')
   mutation_controls+=3;dots+=len(columns)+1
   witnesses.append(dict(omitted_frame_index=omitted,retained_frame_indices=keep,column_count=len(columns),rank=rank,
                         columns_sha256=C.digest([C.vector_json(col)for col in columns]),dual=C.vector_json(witness)))
  covered=[]
  for keep in C.proper_keeps():
   omitted=next(i for i in(1,2,3)if i not in keep);maximal=tuple(i for i in range(5)if i!=omitted)
   nodes=C.topology_nodes(triple,residences,keep);maxnodes=C.topology_nodes(triple,residences,maximal)
   C.need({v for l,h,k,v in nodes}<={v for l,h,k,v in maxnodes},'Complete column-inventory inclusion')
   ranks=[sum(triple['ranks_before'][a:b])for a,b in zip(keep,keep[1:])]
   actual=[len(word['frames'][frames[b]])-len(word['frames'][frames[a]])for a,b in zip(keep,keep[1:])]
   C.need(ranks==actual,'Shared MOVEs counted once; new ranks match endpoints')
   covered.append(dict(retained_frame_indices=keep,separator_omits=omitted,ranks_after=ranks));topologies+=1
  record={k:v for k,v in triple.items()if k!='members'}
  record.update(target=C.vector_json(target),witnesses=witnesses,covered_topologies=covered,original_chronology_positive=True)
  records.append(record)
 return dict(schema_version=1,source_sha256=C.WORD_SHA,arithmetic='exact rational',census=summary,
             census_sha256=C.census_digest(intervals),residence_sha256=C.residence_digest(residences),
             residence_count=len(residences),copy_monitors=monitors,covered_topologies=topologies,
             maximal_omission_witnesses=42,rational_dot_products=dots,synthetic_controls=controls_count,
             mutation_controls=mutation_controls,forward_combined_error_checks=len(records),
             full_frame_chronological_positive_controls=len(records),triples=records)

if __name__=='__main__':
 result=generate();destination=Path(sys.argv[1])if len(sys.argv)>1 else HERE/'CERTIFICATE.json'
 destination.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print('GENERATED_TRIPLE_CERTIFICATE',json.dumps({k:v for k,v in result.items()if k!='triples'},sort_keys=True))
