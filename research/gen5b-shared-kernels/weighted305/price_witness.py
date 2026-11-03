"""Bounded PR305 witness pricing from first-frame data, without upstream code.

Only the two prescribed candidate files may be supplied by the coordinator.
No relation search is performed. Geometry is an explicit separate obligation.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
from collections import Counter
import hashlib,json,sys
import reproduce_pr305 as base
from price_candidate import price

def witness_delta(path):
    raw=Path(path).read_bytes();c=json.loads(raw);assert c['source_head']==base.HEAD
    w=base.read('gen5bit/selected/bit/word_p12.json.gz');frames=base.read('gen5bit/selected/bit/frames_p12.json.gz')['frames']
    removed={b for a,b in w['pairs']};recipients=dict(w['pairs']);regs=sorted(set(range(17160))-removed)
    physical={r:3520+i for i,r in enumerate(regs)}
    entries=c['entries'];pivots={e['virtual_pivot']for e in entries};donors={r for e in entries for r in e['virtual_donors']};active=pivots|donors
    assert len(pivots)==len(entries) and not pivots&donors
    for e in entries:
        assert e['rank']==1 and len(e['basis'])==1
        assert physical[e['virtual_pivot']]==e['pivot'] and [physical[r]for r in e['virtual_donors']]==e['donors']
    kernel=base.read('kernel-selection.json');occupied=set()
    for row in kernel['pairs']+kernel['families']:
        occupied.add(row.get('pivot',row.get('a')));occupied.update(row.get('donors',[row.get('b')]))
    assert not {physical[r]for r in active}&occupied
    gauges={x['role']for x in w['gauges']};sources=set(w['sources'].values())
    assert not active&(gauges|sources)
    assert not active&{row['role']for row in base.read('sink-selection.json')['sinks']}
    owners={r:r for r in active}
    for r in active:
        if r in recipients:owners[recipients[r]]=r
    phase=set(w['phase1']);order=w['phase1']+[i for i in range(len(w['ops']))if i not in phase];first={}
    for i in order:
        for role in w['ops'][i][:2]:
            if role in owners:first.setdefault(owners[role],w['op_frame'][i])
    for role,frame in zip(w['rootroles'],w['root_frame']):
        if role in owners:first.setdefault(owners[role],frame)
    assert set(first)==active
    H=Counter()
    for r,frame in first.items():
        d=frames[str(frame)]['dim'];assert d>0;H[d]-=1
        if d>1:H[d-1]+=1
        if r in donors:H[1]+=1
    assert base.mass(H)==-len(pivots)
    return base.clean(H),dict(candidate_sha256=hashlib.sha256(raw).hexdigest(),pivots=len(pivots),distinct_donors=len(donors),active_roles=len(active),aliased_roles=sum(r in recipients for r in active),setup_pairs=sum(len(e['donors'])for e in entries))

def run(path,label):
    h,w=witness_delta(path);n=w['pivots']
    r=price(h,{24:-n,23:n},{23:n},label=label)
    r.update(source_head=base.HEAD,candidate_sha256=w['candidate_sha256'],witness_counts=w)
    out=Path(__file__).with_name(label+'-provisional-receipt.json');out.write_text(json.dumps(base.ae.serial(r),indent=2)+'\n')
    return r

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    r=run(sys.argv[1],sys.argv[2]);print(json.dumps(base.ae.serial({k:r[k]for k in ('label','candidate_sha256','witness_counts','local_histogram_delta','literal_stock','calls','rank_mass')}|{'kappa':r['assembly']['kappa_decimal'],'improvement_percent':base.ex.dec(r['improvement_percent'])}),indent=2))
