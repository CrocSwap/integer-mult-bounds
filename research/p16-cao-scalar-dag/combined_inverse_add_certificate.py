#!/usr/bin/env python3
"""Remove a maximal nonoverlapping subset of exact commuting inverse ADD pairs.

Run against Cao #4610 source snapshot; recompiles both orientations with
the original synthesize(), and requires exact all-632-column literal
replay and owner restoration. This improves *scalar instruction count*,
not kappa unless complete recursive rank profile improves too.
"""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import gzip,json,sys
HERE=Path(__file__).resolve().parent
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else HERE.parents[2]
sys.path.insert(0,str(ROOT/'research/warp-interface-20261022'))
import warp_merge as W
sys.path.insert(0,str(HERE))
from inverse_add_dag_search import operand,commute_with_pair,paid
F=W.F

def run():
    source=ROOT/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
    original=json.loads(gzip.decompress(source.read_bytes()))
    c=original['canonical']
    program={d:[deepcopy(e) for e in v if e[0]!='climb']
             for d,v in original['programs'].items()}
    f,b=program['forward'],program['backward']
    assert len(f)==len(b)
    proposals=[]
    for right,e in enumerate(f):
        second=operand(e)
        if second is None:continue
        dst,src,coef=second
        for left in range(max(0,right-160),right):
            first=operand(f[left])
            if first is None or first[:2]!=(dst,src) or first[2]!=-coef:continue
            if any(not commute_with_pair(f[k],src[1],dst[1])
                   for k in range(left+1,right)):continue
            inv1,inv2=operand(b[left]),operand(b[right])
            if inv1 is None or inv2 is None or inv1[:2]!=inv2[:2] or inv1[2]!=-inv2[2]:
                continue
            if any(not commute_with_pair(b[k],inv1[1][1],inv1[0][1])
                   for k in range(left+1,right)):continue
            proposals.append((left,right))
    # Select disjoint closed intervals. The algebraic identity for each
    # deletion then survives simultaneous elimination without relying on
    # possibly overlapping commutation arguments.
    proposals.sort(key=lambda p:(p[1]-p[0],p[0]))
    active=set();chosen=[]
    for left,right in proposals:
        if any(k in active for k in range(left,right+1)):continue
        chosen.append((left,right));active.update(range(left,right+1))
    assert chosen and len(set(k for a,b in chosen for k in (a,b)))==2*len(chosen)
    rejected={i for a,b in chosen for i in (a,b)}
    modified={}
    for d,events in program.items():
        kept=[deepcopy(event) for i,event in enumerate(events) if i not in rejected]
        modified[d]=W.synthesize(c,kept)
    a,b=paid(modified['forward']),paid(modified['backward'])
    old=paid(original['programs']['forward'])
    assert a==b==old,('paid_tariff_changed',dict(a),dict(b),dict(old))
    # Preserve every native Clifford chart trajectory and all owned operations.
    def role_edge_trace(word):
        return [(e[2],e[3],e[4],e[5]) for e in word if e[0]=='climb']
    def non_scalar_trace(word):
        return [e for e in word if e[0] in ('warp','center','adapter','residual_adapter','phase')]
    assert all(role_edge_trace(modified[d])==role_edge_trace(original['programs'][d])
               for d in modified), 'Chronological paid chart trajectories changed'
    assert all(non_scalar_trace(modified[d])==non_scalar_trace(original['programs'][d])
               for d in modified), 'Native warp, owner, adapter or phase changed'
    V=F.load(ROOT/'research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py','dag_all_columns')
    X=F.load(ROOT/'research/kappa-rebuild/complex/native_extensions.py','dag_all_native')
    literal={}
    for d in ('forward','backward'):
        rows,r=X.literal_replay(V,c,modified[d],d=='backward')
        assert all(rows['L',i]==V.expected(('L',i),[],d=='backward',False)
                   for i in range(632))
        assert r['arbitrary_owned_C0_cleared'] and r['scalar_frames_checked']
        rebound=deepcopy(c)
        rebound['R']=len(c['start'])-2*c['v']
        rebound['local_profile']={int(k):v for k,v in r['paid_profile'].items()}
        second=V.replay(modified[d],rebound,[],d=='backward',False)
        assert second['all_scalar_frames_checked']
        assert second['paid_profile']==r['paid_profile']
        assert not second['mismatch_examples']
        literal[d]={'event_count':len(modified[d]),
                    'real_scalar_allowance':r['real_scalar_allowance'],
                    'paid_profile':r['paid_profile'],
                    'paid_rank_mass':r['paid_rank_mass']}
    assert literal['forward']['real_scalar_allowance']<158120
    assert literal['backward']['real_scalar_allowance']<158168
    # Deliberately remove just one of the inverse ADD pair, and ensure the
    # exact all-column interpreter does not silently accept the wrong operator.
    lone=chosen[0][0]
    false_word=W.synthesize(c,[deepcopy(e) for i,e in enumerate(program['forward'])
                               if i!=lone])
    rejected=False
    try:
        false_rows,check=X.literal_replay(V,c,false_word,False)
        rejected=any(false_rows['L',i]!=V.expected(('L',i),[],False,False)
                     for i in range(632))
    except (AssertionError,ValueError):
        rejected=True
    assert rejected,'Unpaired deliberate wrong ADD did not fail'
    # Patch has no mutable binary or trust in discovery / solver output.
    (HERE/'SCALAR_CANCEL_PATCH.json').write_text(json.dumps({
      'source':'20bb93cd990d2ff683e4d0fc56b87a42cd5d3296',
      'removed_raw_scalar_event_pairs':chosen,
      'precondition':'Frozen Cao round3 word; unchanged native frames and warps',
      'original_native_payload':json.loads((ROOT/'research/kappa-round3-warp-20261022/ACTUAL-WORD-FREEZE.json').read_text())['canonical_payload_sha256']
    },sort_keys=True,indent=2)+'\\n')
    def native_pairs(p):
        return {(e[3],e[4],e[-1]) for e in p if e[0]=='climb'}
    same_pairs={d:native_pairs(modified[d])==native_pairs(original['programs'][d])
                for d in modified}
    report={'status':'PASS_DUAL_632_NATIVE_SCALAR_CANCEL',
        'source_pin':'20bb93cd990d2ff683e4d0fc56b87a42cd5d3296',
        'proposed_valid_pair_count':len(proposals),
        'simultaneously_removed_inverse_pairs':len(chosen),
        'removed_ADD_instructions':2*len(chosen),
        'selected_raw_event_intervals':chosen,
        'source_forward_scalar_allowance':158120,
        'source_backward_scalar_allowance':158168,
        'native_paid_histogram_unchanged':True,
        'same_native_climb_pair_sets':same_pairs,
        'dual_literal_checks':literal,
        'negative_control_one_unpaired_add_rejected':rejected,
        'two_independent_632_column_interpreters_each_orientation':True,
        'new_kappa':False,
        'required_next_checks':'Full absolute-phase native audit, whole controller and uniform compiler at changed scalar word.'}
    (HERE/'COMBINED_SCALAR_CANCEL_RECEIPT.json').write_text(
        json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('PASS_CAO_DUAL_632_SCALAR_CANCELLATION',
          'removed_pairs',len(chosen),
          'forward_scalar_allowance',literal['forward']['real_scalar_allowance'],
          'backward_scalar_allowance',literal['backward']['real_scalar_allowance'],
          'native_pairs_preserved',same_pairs)
if __name__=='__main__':run()
