"""Reconstruct an exact shared-response basis and nested entrance word, with mutation controls.
Selection discovery is not trusted. No optimizer, network or third-party Python package is used.
"""
from pathlib import Path
from collections import defaultdict
import copy,gzip,json,hashlib,sys
from schur_constructor import check,rank,rewrite
from algebra_constructor import responses
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
canonical=lambda w:json.dumps(w,sort_keys=True,separators=(',',':')).encode()
out=Path(sys.argv[1]).resolve();assert not out.exists();pin=json.loads((ROOT/'BASIS-SOURCE.json').read_text());src=ROOT/'bit470/data/pre-kernel.json.gz';selpath=ROOT/'code/BASIS-SELECTION.json';assert sha(src)==pin['precursor_sha256'] and sha(selpath)==pin['selection_sha256']
w=json.loads(gzip.decompress(src.read_bytes()));entries=json.loads(selpath.read_text())['entries'];v=w['v'];assert (v,w['R'],w['h'])==(120,715,8);n=2*v+w['R'];FULL=(1<<v)-1;mask=lambda lines:sum(1<<i for i in lines);fm=[mask(f) for f in w['frames']];assert fm[0]==0 and fm[1]==FULL
dims=[rank([w['lines'][i] for i in f]) for f in w['frames']];base=check(w,dims);first={};resp=defaultdict(int)
for f,d,ss in w['D']:
 for h in ss:
  if h>=2*v:resp[h]^=1<<(d-v)
for phase in 'ABC':
 for f,d,ss in w[phase]:
  for h in [d]+ss:
   if h>=2*v and fm[f]:first.setdefault(h,fm[f])
piv={};chains=defaultdict(set);byd=defaultdict(list)
for lines,p,ds in entries:
 E=mask(lines);assert len(lines)==len(set(lines)) and E and p not in piv and p not in chains and p not in w['ret'] and 2*v<=p<n
 assert E&~first[p]==0 and w['start'][p]==0
 e=rank([w['lines'][i] for i in lines]);assert {i for i in range(v) if rank([w['lines'][j] for j in lines]+[w['lines'][i]])==e}==set(lines),'entrance is not a closed rational flat'
 z=resp[p];assert len(ds)==len(set(ds))
 for d in ds:
  assert 2*v<=d<n and d not in piv and d not in w['ret'] and E&~first[d]==0
  assert all(E&F in (E,F) for F in chains[d]),'non-nested donor entrances'
  chains[d].add(E);byd[d,E].append(p);z^=resp[d]
 assert z==0,'invalid response relation';piv[p]=E
assert not set(piv)&set(chains)
z=copy.deepcopy(w);frameids={mask(f):i for i,f in enumerate(z['frames'])}
def fid(E):
 if E not in frameids:frameids[E]=len(z['frames']);z['frames'].append([i for i in range(v) if E>>i&1]);dims.append(rank([z['lines'][i] for i in z['frames'][-1]]))
 return frameids[E]
for p,E in piv.items():z['start'][p]=fid(E)
z['D']=[[f,t,[s for s in ss if s not in piv]] for f,t,ss in z['D']]
ordered=sorted(byd,key=lambda dm:(dm[0],dims[fid(dm[1])],dm[1]))
z['A']=[[fid(E),d,sorted(byd[d,E])] for d,E in ordered]+z['A'];z['C']=z['C']+[[1,d,sorted(byd[d,E])] for d,E in ordered]
kern=check(z,dims);factors=json.loads((ROOT/'code/SELECTION473.json').read_text())['selected'];z,_=rewrite(z,factors);factored=check(z,dims)
# Recompute the packet annihilator on the actual new basis, not old row numbers.
packets=defaultdict(list)
for i,key in responses(z).items():packets[key].append(i)
removed=[]
for key,ids in sorted(packets.items()):removed+=ids if key[1]==0 else ids[:len(ids)//2*2]
expected_removed=json.loads(selpath.read_text())['deleted_A_indices'];assert removed==expected_removed
final=copy.deepcopy(z);final['A']=[g for i,g in enumerate(z['A']) if i not in set(removed)];final['C']=[[1,d,ss] for f,d,ss in reversed(final['A'])];audit=check(final,dims)
raw=canonical(final);assert hashlib.sha256(raw).hexdigest()==pin['candidate_sha256'];assert raw==(ROOT/'inputs/pre-retime/word.json').read_bytes();assert final==json.loads(gzip.decompress((ROOT/'inputs/pre-retime/word.json.gz').read_bytes()))
controls={}
for p,E in piv.items():
 donor=next((d for d,EE in ordered if EE==E and p in byd[d,EE] and resp[d]),None)
 if donor is None:controls[str(p)]='NO_NONZERO_DONOR_FOR_OMISSION_CONTROL';continue
 bad=copy.deepcopy(final);idx=next(i for i,(f,d,ss) in enumerate(bad['A']) if d==donor and f==fid(E) and p in ss);bad['A'][idx][2].remove(p)
 try:check(bad,dims)
 except AssertionError:controls[str(p)]='REJECTED_MISSING_PIVOT_CORRECTION'
 else:raise AssertionError(('vacuous correction control',p))
# A single source injection cannot replace the paired response cancellation.
single_controls={}
for i in removed:
 bad=copy.deepcopy(z);bad['A'].pop(i);bad['C']=[[1,d,ss] for f,d,ss in reversed(bad['A'])]
 try:check(bad,dims)
 except AssertionError:single_controls[str(i)]='REJECTED_SINGLE_INJECTION_DELETION'
 else:raise AssertionError(('vacuous packet control',i))
out.mkdir(parents=True);(out/'word.json').write_bytes(raw);receipt=dict(status='PASS_EXACT_BASIS_EXCHANGE_SOURCE_RECONSTRUCTION',source_sha256=pin['precursor_sha256'],selection_sha256=pin['selection_sha256'],candidate_sha256=pin['candidate_sha256'],pivots=len(piv),entrance_rank=sum(dims[final['start'][p]] for p in piv),distinct_donors=len(chains),correction_rows=len(byd),base=base,kernel=kern,factored=factored,final=audit,controls=controls,packet_controls=single_controls,scope='Finite955arbitrarydirtycolumns,rationalframes,integeroperandspans,exactresponsereconstruction. Native/physical/invoice/fullsupplierchecks separate.');(out/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
