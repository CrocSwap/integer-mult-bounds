import argparse, gzip, hashlib, json
from fractions import Fraction
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--selection',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
read=lambda p:json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
u,v,steps=read(a.baseline),read(a.candidate),read(a.selection)
assert len(u['ports'])==112
V=112;N=728
P=set(range(2*V))|set(map(int,u['start_extra']))
assert len(P)==436
work=json.loads(json.dumps(u))
for q in steps:
 i=q['index'];assert work['A'][i]==q['old_operation'];work['A'][i]=q['new_operation']
assert work['A']==v['A']
assert all(u[k]==v[k] for k in u if k not in ['A','cleanup'])
def inverse(e):
 if e[0]=='add':return [e[0],e[1],e[2],-e[3],e[4],list(range(9))]
 return [e[0],e[1],e[3],e[2],list(range(9))]
def scalar(e):return e[:-1]
expected=[inverse(e) for e in reversed(v['A']+v['B']) if not V<=e[1]<2*V]
assert [scalar(e) for e in expected]==[scalar(e) for e in v['cleanup']]
assert all(e[-1]==[256,128,64,32,16,8,4,2,1] for e in v['cleanup'])
def op(e):
 if e[0]=='add':return f'0 {e[1]} {e[2]} {e[3]} {e[4]}'
 assert e[0]=='scale';return f'1 {e[1]} -1 {e[2]} {e[3]}'
lines=[f'{N} {V} {len(steps)} {len(P)}',' '.join(map(str,sorted(P)))]
for w in [u,v]:
 seq=w['A']+w['cut']+w['B']+w['precondition'];lines+=[str(len(seq))]+list(map(op,seq))
lines+=[str(len(u['A']))]+list(map(op,u['A']))
for q in steps:
 lines += [str(q['index']),op(q['new_operation']),str(len(q['cold_difference']))]
 for j,x in q['cold_difference'].items():
  z=Fraction(x);lines.append(f'{j} {z.numerator} {z.denominator}')
a.out.mkdir(parents=True,exist_ok=True)
x=('\n'.join(lines)+'\n').encode();(a.out/'coset-path-input.txt').write_bytes(x)
sha=lambda x:hashlib.sha256(x).hexdigest()
receipt={'status':'PASS_EXACT_SOURCE_BINDING_AND_LITERAL_CLEANUP','baseline_sha256':sha(a.baseline.read_bytes()),'candidate_sha256':sha(a.candidate.read_bytes()),'selection_sha256':sha(a.selection.read_bytes()),'native_input_sha256':sha(x),'moves':len(steps),'preserved_keys':[k for k in u if k not in ['A','cleanup']],'cleanup_count':len(expected),'all_cleanup_full_frame':True}
(a.out/'COSET-SOURCE-BINDING.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt))
