from pathlib import Path
import gzip,json,hashlib,copy
r=Path.cwd();a=r/'r715-hierarchy-baseline-rebuild/WORD.json.gz';b=r/'source463-review/data/R715_FP_final.json.gz';x=json.loads(gzip.decompress(a.read_bytes()));y=json.loads(gzip.decompress(b.read_bytes()));changes=[]
assert x.keys()==y.keys()
for k in x:
 if x[k]==y[k]:continue
 assert k in ('D','A','B','C') and len(x[k])==len(y[k])
 for i,(g,h) in enumerate(zip(x[k],y[k])):
  if g==h:continue
  assert g[:2]==h[:2] and sorted(g[2])==sorted(h[2]) and len(set(g[2]))==len(g[2]) and g[1] not in g[2]
  changes.append(dict(phase=k,gate=i,frame=g[0],destination=g[1],actual=g[2],reference=h[2],justification='Additions share one destination and frame and read distinct unchanged operands; they commute.'))
assert len(changes)==2
result=dict(status='PASS_PINNED_WORD_UP_TO_WITHIN_GATE_OPERAND_ORDER',R=x['R'],actual_sha256=hashlib.sha256(gzip.decompress(a.read_bytes())).hexdigest(),reference_sha256=hashlib.sha256(gzip.decompress(b.read_bytes())).hexdigest(),differences=changes,all_other_fields_identical=True,scope='The first strict byte/object equality failed at two source-list orderings only. This explicit algebraic equivalence does not relabel the first run as exact-byte success. Future candidates need fresh complete finite and native checks.')
(r/'r715-hierarchy-baseline-rebuild/ORDER-EQUIVALENCE.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
