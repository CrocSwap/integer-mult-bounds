"""Exact frame projectors and independent decoding of fresh R715 rank120 records.
Adapted from PR386/436/443 audit; chafreaky with OpenAI Codex. Apache-2.0.
"""
import gzip,hashlib,json,struct,sys
from pathlib import Path
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'e8-r740-replica32/code'))
from bank_routes import validate_isometries

def local_audit(par):
 read=lambda p:json.loads(p.read_text())
 raw=(par/'records/249-records.bin').read_bytes();records=list(struct.iter_unpack('<6i',raw))
 fs=read(par/'records/frames.json')['frames'];state=read(par/'records/249-states.json')
 lg=read(par/'cout/legality.json');cc=read(par/'cout/columns.json')
 assert lg['status'].startswith('PASS') and cc['status'].startswith('PASS')
 assert lg['copies']==lg['erasures']==9 and cc['formal_columns_checked']==1195
 I=S.eye(8);proj={};dims={}
 for key,f in fs.items():
  k=int(key);B=S.Matrix(f['B']) if f['B'] else S.zeros(0,8)
  P=B.T*(B*B.T).inv()*B if B.rows else S.zeros(8)
  assert P.T==P and P*P==P and P.trace()==f['dim'];proj[k]=P;dims[k]=f['dim']
 pairs={}
 for op,x,y,c,r,z in records:
  if op==0 and (y,c) not in pairs:
   D=proj[c]-proj[y]
   assert proj[c]*proj[y]==proj[y] and proj[y]*proj[c]==proj[y]
   assert D*D==D and D.trace()==r and (I-proj[y])-(I-proj[c])==D;pairs[y,c]=r
 streams={}
 for rev in (False,True):
  es=[]
  for op,x,y,c,f,z in (reversed(records) if rev else records):
   if op==0:es.append([0,x,c if rev else y,y if rev else c,f,int(rev)])
   elif op==1:es.append([1,x,y,-c if rev else c,f,int(rev)])
   elif op==(3 if rev else 2):es.append([2,x,y,c,f,abs(dims[c]-dims[f]),int(rev)])
   else:es.append([3,x,y,c,f,z,int(rev)])
  streams['reverse' if rev else 'forward']=es
 word=json.loads(gzip.decompress((ROOT/'data/word.json.gz').read_bytes()))
 initial=[state['initial'][str(i)] for i in range(955)];assert initial==word['start']
 iso=read(ROOT/'data/residual-isometries.json')
 assert validate_isometries(iso,word['frames'],word['lines'],dims)==set(initial[240:]) and len(iso)==11
 rank=sum(dims[f] for f in initial[240:]);assert rank==120
 expected=dict(local_programs=streams,residual_isometries=iso,entrance_rank_total=rank,
 source_record_sha256=hashlib.sha256(raw).hexdigest(),bit_operator='D_U exchanges the two address halves on projector U; D_I D_P = D_(I-P) exactly.')
 result=dict(status='PASS_EXACT_R715_RANK120_LOCAL_PROJECTORS',source_frames=len(proj),nested_and_reflected_pairs=len(pairs),residual_isometries=len(iso),entrance_rank=rank)
 return expected,result
