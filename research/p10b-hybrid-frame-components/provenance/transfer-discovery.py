"""Physical-role/source-bound transport of PR340's pinned frame assignment.

Selection and method: Rohan Arun with Anthropic Claude assistance, PR340
head695e703731491f81aa22d51b2def850afd7519c0. Independent adaptation to the
six-direct/four-cache hybrid and exact discovery checks: OpenAI Codex.
"""
import sys,pathlib,json,pickle,hashlib,collections
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parent
source=(ROOT/'search.py').read_text();prefix=source[:source.index('interval_cache={}')]
exec(compile(prefix,str(ROOT/'search.py'),'exec'),globals())
UP=pathlib.Path('/private/tmp/p10b-sinkaware022-w3-fresh-20261010/joint-final/final')
CUR=pathlib.Path('/private/tmp/p10b-hybrid023-w3-fresh-20261010/joint-final/final')
U=pickle.load(open(UP/'data.pkl','rb'))
assert hashlib.sha256(U['records']).hexdigest()==pr['input_raw_sha256']
ureg=json.loads((UP/'regs.json').read_text());creg=json.loads((CUR/'regs.json').read_text())
uword=array('i');uword.frombytes(U['records'])
def basis_hash(rows):return hashlib.sha256(json.dumps([list(r) for r in rows],separators=(',',':')).encode()).hexdigest()
ubhash={f:basis_hash(rows) for f,rows in U['B'].items()};cbhash={f:basis_hash(rows) for f,rows in D['B'].items()}
def role(a,regs):return ('data',a) if a<2*v else ('helper',regs[a-2*v]) if a<2*v+len(regs) else ('temporary',0)
def key(row,regs,bhash):
    op,a,b,c,f,z=row
    return (role(a,regs),role(b,regs),c,z,bhash[f])
ukeys=defaultdict(list);ckeys=defaultdict(list)
for k in range(len(uword)//6):
    row=uword[6*k:6*k+6]
    if row[0]==1:ukeys[key(row,ureg,ubhash)].append(k)
for k in gates:ckeys[key(old[6*k:6*k+6],creg,cbhash)].append(k)
for k in list(selected):setframe(k,old[6*k+4])
bindings=[];misses=[]
for entry in pr['entries']:
    k=entry['record'];row=uword[6*k:6*k+6];assert list(row[j] for j in (1,2,3,5))==entry['scalar'];assert ubhash[row[4]]==entry['old_basis_sha256']
    ky=key(row,ureg,ubhash);src=ukeys[ky];dst=ckeys[ky]
    if len(src)!=len(dst):misses.append(dict(upstream_record=k,reason='occurrence-count-mismatch',before=len(src),after=len(dst)));continue
    newk=dst[src.index(k)];assert newk not in fixed
    g=register(entry['new_basis']);assert nondeg(g)
    if not spanok(g,needs[newk]):misses.append(dict(upstream_record=k,record=newk,reason='source-span-mismatch'));continue
    setframe(newk,g);bindings.append(dict(upstream_record=k,record=newk,physical_key=ky,source_occurrence=src.index(k),source_occurrence_count=len(src)))
print('transport',len(bindings),'misses',len(misses),flush=True)
violations=[]
for r in initial:
    prev=initial[r];pk=None
    for p,f in enumerate(chain[r]+[final[r]]):
        if not sub(prev,f):violations.append(dict(register=r,physical=role(r,creg),previous=pk,next=owner[r][p] if p<len(owner[r]) else None,previous_frame=prev,next_frame=f))
        prev=f;pk=owner[r][p] if p<len(owner[r]) else None
(ROOT/'transfer-combined-mapping.json').write_text(json.dumps(dict(bindings=bindings,misses=misses,violations=violations),indent=1)+'\n')
# Combine only the separately admitted seed's missing changes, leaving
# transported assignments intact where the two selectors differ.
for e in seed['entries']:
    if e['record'] not in selected:setframe(e['record'],register(e['new_basis']))
violations=[]
for r in initial:
    prev=initial[r];pk=None
    for p,f in enumerate(chain[r]+[final[r]]):
        if not sub(prev,f):violations.append(dict(register=r,previous=pk,next=owner[r][p] if p<len(owner[r]) else None))
        prev=f;pk=owner[r][p] if p<len(owner[r]) else None
pruned=[]
while violations:
    bad={x[field] for x in violations for field in ('previous','next') if x[field] in selected}
    assert bad
    pruned.extend(sorted(bad))
    for k in bad:setframe(k,old[6*k+4])
    violations=[]
    for r in initial:
        prev=initial[r];pk=None
        for p,f in enumerate(chain[r]+[final[r]]):
            if not sub(prev,f):violations.append(dict(register=r,previous=pk,next=owner[r][p] if p<len(owner[r]) else None))
            prev=f;pk=owner[r][p] if p<len(owner[r]) else None
print('pruned',len(pruned),'retained',len(selected),flush=True)
(ROOT/'transfer-combined-pruning.json').write_text(json.dumps(dict(pruned=pruned,retained=sorted(selected),reason='Revert both selected endpoints of every failed joint chain edge until all chains nest; source spans rechecked separately.'),indent=1)+'\n')
H=hist();L=sum(LN[d]*c for d,c in H.items());delta=Counter(H);delta.subtract(H0)
entries=[]
for k in sorted(selected):
    op,a,b,c,f,z=old[6*k:6*k+6];g=selected[k]
    if sub(f,g) and sub(g,f):continue
    entries.append(dict(record=k,scalar=[a,b,c,z],category=D['cats'][z],old_dimension=dimf[f],old_basis_sha256=basis_hash(B[f]),new_basis=[list(map(int,r)) for r in B[g]],new_dimension=dimf[g],constructed=g not in original_ids))
result=dict(source_record_count=N,selected_gate_count=len(entries),local_delta={str(d):c for d,c in sorted(delta.items()) if c},removed_calls=sum(H0.values())-sum(H.values()),dL_local=L-L0,moves=dict(transported_pr340=len(entries)),new_frames=len({e['new_basis'].__repr__() for e in entries if e['constructed']}),entries=entries,seed_phi_delta=seedL-L0)
(ROOT/'transfer-combined-search.json').write_text(json.dumps(result,indent=1)+'\n')
print('PASS_TRANSPORT_EXACT_SPANS_NESTING_FIXED_ENDPOINTS',len(entries),'delta',result['local_delta'],'phi',result['dL_local'],'extra',L-seedL,flush=True)
