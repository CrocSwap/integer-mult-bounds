"""Independent chart choices for every active unit, ell=1 first gate.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
CORE=HERE.parent
sys.path.insert(0,str(CORE))
import freeze as Z
import palette_gauge as P
import realification_census as R
import mixed_gauge as M
import weighted_gauge as W


def options(ce,c,frame,ell,cache):
    R.need(ell==1,'First bounded screen is ell=1 only')
    basis=tuple(c['frames'][frame]);r=len(basis)
    if basis not in cache:cache[basis]=R.frame_data(ce,basis)
    F,square,K=cache[basis]
    masks=list(dict.fromkeys([0]+[1<<i for i in range(r)]+[(1<<r)-1]))
    columns=[];vectors=[]
    normal=R.tabcols(F);chart=R.tabcols(K)
    for mask in masks:
        w=R.action(chart,mask)
        actual=R.transvection(normal,w) if mask else normal
        R.need(R.compose(actual,actual)==tuple(1<<i for i in range(18)),'Symplectic inverse only')
        columns.append(actual);vectors.append(w)
    return dict(masks=masks,columns=columns,pauli_vectors=vectors)


def main():
    began=time.monotonic();frozen=R.read(CORE/'FREEZE.json')
    R.need(Z.audit()==frozen,'All completed core bytes match the old freeze')
    related=R.read(HERE/'RELATED.json')
    R.need(related['core_freeze_sha256']==sha256((CORE/'FREEZE.json').read_bytes()).hexdigest(),'Related review binds old frozen inputs')
    for row in related['files']:R.need(sha256((HERE/row['copy']).read_bytes()).hexdigest()==row['sha256'],'Exact compared related model bytes')
    ce=R.load(CORE/'sources'/R.CE,'all_units_actual_clifford')
    payload=R.read(CORE/'sources/research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz')
    g=M.graph(payload);cache={};ell=1
    terms,counts,metadata=P.cost_tables(ce,g,ell,cache,option_provider=options)
    bounds={r:W.rank_power(r) for r in range(10)}
    weights={r:int((a+b)*W.SCALE/2+W.Q(1,2)) for r,(a,b) in bounds.items()}
    before=W.net_profile(terms,[0]*g['components']);cases=[]
    print('PASS_ALL_UNIT_NATIVE_TABLES','components',g['components'],'elapsed',round(time.monotonic()-began,2),flush=True)
    for boundary,fixed in [('strict',g['strict_fixed']),('helper_free_optimistic',g['base_fixed'])]:
        assignment,solver=P.solve(terms,counts,fixed,weights,120)
        P.validate_assignment(assignment,counts,fixed)
        native=P.replay_native_prices(ce,g,ell,terms,assignment,cache,option_provider=options)
        after=W.net_profile(terms,assignment);lo,hi=W.gain_bounds(before,after,bounds)
        paid,helpers=P.profile(terms,assignment)
        row=dict(boundary=boundary,solver=solver,assignment=assignment,
                 changed_components=sum(x!=0 for x in assignment),native_replay=native,
                 moment_gain_lower=str(lo),moment_gain_upper=str(hi),genuine_positive_finite_moment=lo>0,
                 paid_profile=R.counter_data(paid),helper_profile=R.counter_data(helpers),
                 local_deficit=R.mass(paid)-R.mass(helpers)-1792,
                 net_profile_delta={str(r):after[r]-before[r] for r in sorted(set(before)|set(after)) if after[r]!=before[r]},
                 free_component_rank_histogram=dict(Counter(len(g['canonical']['frames'][f]) for i,f in g['component_frames'].items() if i not in fixed)))
        cases.append(row)
        print('PASS_ALL_UNIT_CANDIDATE_REPLAY',boundary,solver['status'],'changed',row['changed_components'],
              'gain',float(lo),float(hi),'deficit',row['local_deficit'],'elapsed',round(time.monotonic()-began,2),flush=True)
    R.need(Z.audit()==frozen,'Old core remains byte-frozen after expanded search')
    out=dict(status='PASS_ALL_ACTIVE_UNIT_PALETTE_FINITE_SEARCH',ell=ell,kappa=str(W.KAPPA),
             core_freeze_sha256=sha256((CORE/'FREEZE.json').read_bytes()).hexdigest(),
             related_sha256=sha256((HERE/'RELATED.json').read_bytes()).hexdigest(),
             script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
             frame_options=metadata,option_counts=counts,terms=terms,cases=cases,new_kappa=False,
             numerical_solver_scope='Floating MIP status is bounded evidence; exact candidate rank replay and rational gain intervals are separate.',
             physical_scope='No admitted new actual phase/compiler/restoration/all-f recursive supplier follows from a finite rank profile.',
             seconds=time.monotonic()-began)
    (HERE/'ALL-UNITS.json.gz').write_bytes(gzip.compress(json.dumps(out,sort_keys=True,separators=(',',':')).encode(),mtime=0))


if __name__=='__main__':main()
