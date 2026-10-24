#!/usr/bin/env python3
"""Fresh 5387 literal preparation audit; imports only our own pure arithmetic.

Construction/refinement credit Dugongue and Ali Romman; review Chris R /
Clear1nsight, substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip, json, time
import check_precision as independent

HERE=Path(__file__).resolve().parent
CAP=HERE.parent/'09-capsule-cold/capsule-5387-v1'
PKG=CAP/'snapshot/research/eight-owned-relations'

def main():
    start=time.monotonic()
    w=json.loads(gzip.decompress((PKG/'WORD.json.gz').read_bytes()))
    r=json.loads((PKG/'RELATIONS.json').read_bytes())
    piv,rows=independent.rref(r['sites'])
    assert piv==[225,227,229,230,241,245,257,261]
    declared=[{int(i):Q(q) for i,q in row.items()} for row in r['rows']]
    assert piv==r['pivots'] and rows==declared
    expected=[]; prep=[]
    for p,row in zip(piv,rows):
        assert not (set(row)&(set(piv)-{p}))
        expected.append(['scalar',['clear',['L',p]],0]);mass=Q(0);hh=0
        for i,q in sorted(row.items()):
            if i==p:continue
            expected.append(['scalar',['add',['L',p],['L',i],(-q).numerator,q.denominator],0])
            mass+=abs(q);hh+=independent.height(q,True)
        prep.append(dict(pivot=p,adds=len(row)-1,row_l1=str(mass),max_denominator=max(q.denominator for q in row.values()),height=hh))
    assert w['programs']['backward'][:len(expected)]==expected
    audits={d:independent.scalar_audit(w['programs'][d]) for d in ('forward','backward')}
    assert max(Q(p['row_l1']) for p in prep)==9
    assert max(p['max_denominator'] for p in prep)==2
    assert audits['backward']['events']['zero_retag']==8
    result=dict(schema=1,status='PASS_FRESH_5387_PREPARATION_AND_SCALAR_GRAMMAR',
      candidate_head='b1ab650d36f59e5be682a813145b7c67e219e341',
      capsule_manifest_sha256=sha256((CAP/'IMMUTABLE-MANIFEST.json').read_bytes()).hexdigest(),
      files={n:sha256((PKG/n).read_bytes()).hexdigest() for n in ('WORD.json.gz','RELATIONS.json','SOURCES.json')},
      pivots=piv,preparation=prep,preparation_events=len(expected),preparation_adds=sum(x['adds'] for x in prep),
      max_preparation_l1=9,max_preparation_denominator=2,input_magnitude_extra_bits=4,
      local=audits,raw_full_local_owned_banks=274,
      changed_owned_pivot={'removed':288,'added':261},
      changed_last_site=dict(source_role=r['sites'][-1]['role'],snapshot=r['sites'][-1]['snapshot'],zero=r['sites'][-1]['zeros']),
      new_N='2^409549000000000000',new_G='fold over entire freshly prepared completed/split/compiled physical word; never reuse5383G',
      seconds=time.monotonic()-start,
      scope='No candidate evaluator imports. Exact physical endpoint and final funded arithmetic are separate gates; new N supplied only after role04 certification.')
    (HERE/'LIGHT-ARITHMETIC-5387.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],preparation_adds=result['preparation_adds'],seconds=result['seconds'])))

if __name__=='__main__':main()
