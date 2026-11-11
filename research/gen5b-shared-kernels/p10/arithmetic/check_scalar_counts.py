"""Independent odd-coefficient initial-prefix and inherited-kernel scalar invoice counts."""
from collections import Counter
from pathlib import Path
import hashlib,json
import reproduce_p10 as b
support=b.support
HERE=support.out('arithmetic','placeholder').parent
PARAM=support.OUTPUT/'matching'
BRIDGE=support.OUTPUT/'weighted'
CERT=support.OUTPUT/'certificates'
CLOSURE=support.HERE/'witnesses'

def run():
    original=b.read('bitword/selected/bit/word_p10.json.gz');graph=b.read('bitword/selected/bit/graph_p10.json')
    newraw=(PARAM/'word_weighted892.json').read_bytes();new=json.loads(newraw)
    changed=[k for k in original if original[k]!=new[k]];assert set(changed)=={'pairs','reads'}
    gauge={x['role'] for x in original['gauges']};phase=set(original['phase1']);order=original['phase1']+[i for i in range(len(original['ops'])) if i not in phase]
    adj=[Counter() for _ in range(9120)]
    for root,role in zip(graph['roots'],original['rootroles']):adj[role].update(root['targets'])
    for i in reversed(order):
        dst,src,_=original['ops'][i];adj[src].update(adj[dst])
    coefficient=Counter()
    for role in range(9120):
        if role not in gauge:coefficient.update(abs(c) for c in adj[role].values() if c%2)
    assert sum(coefficient.values())==300560
    maps=[]
    for word in (original,new):
        removed={z for a,z in word['pairs']};roles=sorted(set(range(9120))-removed);maps.append({1920+i:r for i,r in enumerate(roles)})
    kernel=b.read('kernel-selection.json');entries=kernel['pairs']+kernel['families'];pivots=[e.get('pivot',e.get('a')) for e in entries]
    assert len(set(pivots))==len(pivots)==775
    old=Counter();rebased=Counter()
    for pivot in pivots:
        assert maps[0][pivot]==maps[1][pivot] and maps[0][pivot] not in gauge
        old.update(abs(c) for c in adj[maps[0][pivot]].values() if c%2)
        rebased.update(abs(c) for c in adj[maps[1][pivot]].values() if c%2)
    assert old==rebased
    setups=sum(len(e.get('donors',[e.get('b')])) for e in entries);assert setups==1157
    candidate_raw=(BRIDGE/'rebound-candidate19.json').read_bytes();candidate=json.loads(candidate_raw);newremoved=Counter()
    for e in candidate['entries']:
        role=maps[1][e['pivot']];assert role==e['virtual_pivot'] and role not in gauge
        newremoved.update(abs(c) for c in adj[role].values() if c%2)
    pairs=sum(len(e['donors']) for e in candidate['entries']);assert pairs==58
    scalar=next(x for x in json.loads((PARAM/'scalar_and_seams892.json').read_text()).items() if x[0]=='scalar_adds')[1];assert scalar==355400
    # Identical virtual operations/adjoints and targets imply the same raw
    # odd-coefficient histogram; target/restore/sink/reorder count transport
    # remains bound to the corresponding independent chronology receipts.
    pins=b.pins();net=2*pairs-sum(newremoved.values());netunits=2*pairs-sum(c*n for c,n in newremoved.items())
    return dict(status='PASS_INDEPENDENT_WEIGHTED892_SCALAR_COUNT_INVARIANCE',source_head=b.HEAD,candidate_word_sha256=hashlib.sha256(newraw).hexdigest(),rebound_candidate_sha256=hashlib.sha256(candidate_raw).hexdigest(),changed_base_fields=changed,
        plain_prefix_adds=sum(coefficient.values()),plain_prefix_unit_adds=sum(c*n for c,n in coefficient.items()),plain_prefix_coefficient_histogram=dict(coefficient),
        inherited_kernel_entries=775,inherited_removed_adds_old=sum(old.values()),inherited_removed_adds_new=sum(rebased.values()),inherited_removed_unit_adds_old=sum(c*n for c,n in old.items()),inherited_removed_unit_adds_new=sum(c*n for c,n in rebased.items()),inherited_setup_pairs=setups,
        raw_base_odd_ADDs=355400,raw_base_unit_ADDs=357320,raw_base_count_change=0,inherited_transcript_base_final_weighted_ADDs=pins['weighted_scalar_events'],inherited_transcript_base_final_unit_ADDs=pins['literal_unit_additions'],
        fixed19_setup_pairs=pairs,fixed19_gross_added_ADDs=2*pairs,fixed19_removed_reads=sum(newremoved.values()),fixed19_removed_unit_reads=sum(c*n for c,n in newremoved.items()),fixed19_removed_coefficient_histogram=dict(newremoved),
        net_local_weighted_delta=net,net_local_unit_delta=netunits,post_fixed19_weighted_ADDs=pins['weighted_scalar_events']+net,post_fixed19_unit_ADDs=pins['literal_unit_additions']+netunits,
        conservative_invoice_weighted_ADDs=pins['weighted_scalar_events']+2*pairs,conservative_invoice_unit_ADDs=pins['literal_unit_additions']+2*pairs,
        scope='Exact initial-prefix compensation and kernel scalar counts from fixed virtual adjoints; unchanged remaining transcript scalar counts require the separately checked target/restore/sink/reorder transport. Conservative finite bill gives removed new reads no credit.')
if __name__=='__main__':
    r=run();(HERE/'weighted892-scalar-count-contract.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
