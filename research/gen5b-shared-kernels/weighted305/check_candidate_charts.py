"""Fresh exact charts for a bounded PR305 shared-kernel candidate.
Our authored rational constructors are reused; upstream JSON is inert.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter
from pathlib import Path
import hashlib,json
import chart_construction as charts
import reproduce_pr305 as base

def run(candidate_path,bridge,literal_stock):
    base.verify_sources();raw=Path(candidate_path).read_bytes();candidate=json.loads(raw)
    assert bridge['head']==candidate['source_head']==base.HEAD
    assert bridge['all_column_formal_composition_forward_inverse'] and bridge['omitted_setup_and_restore_rejected'] and bridge['final_full_endpoints_checked']
    w=base.read('gen5bit/selected/bit/word_p12.json.gz');frames=base.read('gen5bit/selected/bit/frames_p12.json.gz')['frames']
    removed={b for a,b in w['pairs']};recipient={a:b for a,b in w['pairs']}
    regs=sorted(set(range(17160))-removed);physical={r:3520+i for i,r in enumerate(regs)}
    entries=candidate['entries'];pivots={e['virtual_pivot']for e in entries};donors={r for e in entries for r in e['virtual_donors']};active=pivots|donors
    assert len(pivots)==len(entries)==bridge['selected_pivots'] and len(donors)==bridge['selected_distinct_donors']
    assert not pivots&donors and len(active)==bridge['selected_streams']
    lines={}
    for e in entries:
        assert e['rank']==1 and len(e['basis'])==1
        vector=e['basis'][0];nonzero=[i for i,x in enumerate(vector)if x]
        assert len(nonzero)==2 and sorted(vector[i]for i in nonzero)==[-1,1]
        line=tuple(sorted(nonzero))
        for r in[e['virtual_pivot']]+e['virtual_donors']:
            assert r not in lines or lines[r]==line;lines[r]=line
        assert physical[e['virtual_pivot']]==e['pivot'] and [physical[r]for r in e['virtual_donors']]==e['donors']
    owners={r:r for r in active}
    for r in active:
        if r in recipient:owners[recipient[r]]=r
    phase=set(w['phase1']);order=w['phase1']+[i for i in range(len(w['ops']))if i not in phase];first={}
    for index in order:
        for role in w['ops'][index][:2]:
            if role in owners:first.setdefault(owners[role],w['op_frame'][index])
    for role,frame in zip(w['rootroles'],w['root_frame']):
        if role in owners:first.setdefault(owners[role],frame)
    assert set(first)==active
    paths={p['role']:p for p in bridge['selected_paths']};assert set(paths)==active
    programs=[];uses=[];registry={};H=Counter()
    def put(key,builder):
        if key not in registry:
            registry[key]=len(programs);programs.append(dict(program_id=len(programs),**builder()))
        return registry[key]
    for role in sorted(active):
        p=paths[role];frame_id=first[role];frame=frames[str(frame_id)];d=frame['dim'];line=lines[role]
        assert p['first_frame']==frame_id and p['first_dimension']==d and p['stream']==physical[role]
        assert p['kernel_kind']==('pivot'if role in pivots else'donor')
        vector=p['entrance_basis'][0]
        assert tuple(i for i,x in enumerate(vector)if x)==line and sorted(x for x in vector if x)==[-1,1]
        pid=put(('first',frame_id,line),lambda:dict(kind='first_frame_quotient',frame=frame_id,**charts.first_frame_chart(frame,list(line))))
        uses.append(dict(kind='first_frame_quotient',role=role,stream=physical[role],frame=frame_id,rank=d-1,program_id=pid))
        rank=23 if role in pivots else 1;kind='pivot_residual'if role in pivots else'donor_line_entrance'
        pid=put(('line',line,rank),lambda:dict(kind=kind,**charts.line_chart(*line,rank)))
        uses.append(dict(kind=kind,role=role,stream=physical[role],rank=rank,program_id=pid))
        H[d]-=1
        if d>1:H[d-1]+=1
        if role in donors:H[1]+=1
    assert base.clean(H)==dict(base.histogram(bridge['local_histogram_delta']))
    assert Counter(u['kind']for u in uses)==dict(first_frame_quotient=len(active),pivot_residual=len(pivots),donor_line_entrance=len(donors))
    assert all(programs[u['program_id']]['residual_rank']==u['rank']for u in uses)
    pins=base.read('expected/kernel-pins.json');largest=max(p['count']for p in programs);bound=max(pins['max_chart_factors'],largest)+119+120
    assert pins['max_chart_factors']==576 and bound==815
    assert literal_stock==pins['literal_stock']-5*len(pivots)//2 and len(pivots)%2==0
    selector=600*((literal_stock-1)+pins['physical_R']*120*bound);assert selector<2**40
    return dict(status='PASS_PR305_BOUNDED_CANDIDATE_CHANGED_CHARTS',source_head=base.HEAD,
        candidate_sha256=hashlib.sha256(raw).hexdigest(),charts=len(programs),final12_charts=0,
        first_frame_quotient_demands=len(active),pivot_residual_demands=len(pivots),donor_line_entrance_demands=len(donors),
        role_chart_uses=uses,max_changed_chart_factors=largest,max_factor_numerator=max(p['max_numerator']for p in programs),
        max_factor_denominator=max(p['max_denominator']for p in programs),combined_normalizer_factor_bound=bound,
        literal_stock=literal_stock,selector_calls_bound=selector,local_histogram_delta=base.clean(H),factor_programs=programs,
        scope='All changed first-frame, rank23 pivot residual and rank1 donor entrance charts are exactly constructed, factored, inverse-replayed and bound to fresh selected_paths. No final12 charts; unchanged chart/compiler contracts remain inherited.')
