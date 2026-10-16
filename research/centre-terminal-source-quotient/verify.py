#!/usr/bin/env python3
"""Source-only terminal quotient for the selected time0/time10 centre ablation."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import model as m
Q=m.Q

def restrict(rows, columns):
    return {i:{j:q for j,q in row.items() if j in columns} for i,row in rows.items()
            if any(j in columns for j in row)}

def witness(matrix, size):
    _,columns=m.rank(matrix.values())
    columns=columns[:size]
    transpose=[{i:row.get(j,Q(0)) for i,row in matrix.items() if row.get(j)} for j in columns]
    _,rows=m.rank(transpose)
    rows=rows[:size]
    minor=[[matrix[i].get(j,Q(0)) for j in columns] for i in rows]
    _,det=m.inverse(minor)
    m.require(det and len(rows)==len(columns)==size,'lower minor')
    return {'rows':rows,'columns':columns,'determinant':str(det),
            'minor':[[str(q) for q in row] for row in minor]}

def experiment():
    data=m.load()
    calls,owners,positions,normal,muted=m.setup(data)
    universe=set().union(*map(set,owners))
    full,cuts=m.run(calls,owners,normal,muted,universe)
    ablated,_=m.run(calls,owners,normal,muted,universe,(0,10))
    error=m.difference(full,ablated)
    d=set(owners[0][:112]);dt=set(owners[0][:224])
    ed=restrict(error,d); edt=restrict(error,dt)
    m.require([m.rank(x.values())[0] for x in (ed,edt,error)]==[8,16,16],'terminal ranks')
    p=[{j:q for j,q in row.items() if j in d} for row in cuts[0]]
    m.require(m.rank(p)[0]==8,'first cut rank')
    m.require(all(not any(j in d for j in row) for row in cuts[10]),'second original D cut nonzero')
    _,columns=m.rank(p)
    inv,det=m.inverse([[row.get(j,Q(0)) for j in columns] for row in p])
    factor={}
    for owner,row in ed.items():
        factor[owner]={k:sum(row.get(j,Q(0))*inv[t][k] for t,j in enumerate(columns)) for k in range(8)}
        factor[owner]={k:q for k,q in factor[owner].items() if q}
        rebuilt=m.evaluate(factor[owner],dict(enumerate(p)))
        m.require(rebuilt==row,'terminal factorization does not hold')
    # The lower certificate is an actual terminal-output minor, not a cut-rank substitution.
    lower=witness(ed,8); lower16=witness(edt,16)
    naive={}
    panels=[]
    for i in (0,10):
        scatter=normal[calls[i]['orientation']][2]
        panels.append({owners[i][r] for r in scatter})
        for role,row in scatter.items():
            addition=m.evaluate(row,dict(enumerate(cuts[i])))
            m.plus(naive.setdefault(owners[i][role],{}),addition)
    naive=restrict(naive,d)
    gap=m.difference({i:ed.get(i,{}) for i in universe},{i:naive.get(i,{}) for i in universe})
    m.require(gap,'naive scatter control ineffective')
    out=min(gap);inp=min(gap[out])
    # All eleven calls are retained. Omitting b1 changes the causal endpoint repair.
    skipped,_=m.run(calls,owners,normal,muted,universe,(),(4,))
    skipped_a,_=m.run(calls,owners,normal,muted,universe,(0,10),(4,))
    m.require(restrict(m.difference(skipped,skipped_a),d)!=ed,'missing b1 control ineffective')
    only_first,_=m.run(calls,owners,normal,muted,universe,(0,))
    m.require(restrict(m.difference(full,only_first),d)!=ed,'single ablation control ineffective')
    bad={i:dict(row) for i,row in factor.items()}
    owner=next(i for i in bad if bad[i]); channel=next(iter(bad[owner]))
    bad[owner][channel]=-bad[owner][channel]
    m.require(m.evaluate(bad[owner],dict(enumerate(p)))!=ed[owner],'wrong repair sign control')
    events=data['global']['execution_schedule'][:positions[-1]+1]
    omitted=Counter(e['kind'] for e in events if e['kind']!='local_cover_sweep')
    literal=Counter()
    for i in (0,10):literal.update(normal[calls[i]['orientation']][3])
    return {
        'scope':'Scalar identity-frame, local-call-only prefix; final state immediately after selected time10 call.',
        'calls':[{k:c[k] for k in ('time','stage','replica','orientation')} for c in calls],
        'owners':len(universe),'roles_per_call':704,'ablated_calls':[0,10],
        'omitted_schedule_events':dict(sorted(omitted.items())),
        'source_columns':sorted(d),'fixed_dirt_columns':len(universe-d),
        'terminal_nonzero_output_rows':len(ed),'full_residual_output_rows':len(error),
        'terminal_rank_source_only':8,'terminal_rank_source_and_target':16,'terminal_rank_all_owners':16,
        'first_centre_source_maps':m.encode(dict(enumerate(p))),
        'source_minor_columns':columns,'source_minor_determinant':str(det),
        'terminal_repair_from_first_centres':m.encode(factor),
        'terminal_lower_minor':lower,'variable_target_lower_minor':lower16,
        'source_terminal_matrix_sha256':m.digest(json.dumps(m.encode(ed),sort_keys=True).encode()),
        'all_owner_terminal_matrix_sha256':m.digest(json.dumps(m.encode(error),sort_keys=True).encode()),
        'scatter_panel_sizes':[len(x) for x in panels], 'scatter_panel_overlap':len(panels[0]&panels[1]),
        'naive_scatter_control':{'input_owner':inp,'output_owner':out,'terminal_coefficient':str(ed.get(out,{}).get(inp,0)),
                                 'naive_coefficient':str(naive.get(out,{}).get(inp,0))},
        'literal_two_phase_bill':dict(sorted(literal.items())),
        'controls':['naive summed scatter differs','omitting intervening b1 differs','ablating only first call differs',
                    'wrong repair sign differs','varying target values raises rank to16'],
        'no_native_lift_or_physical_saving_claim':True,
    }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    result=experiment()
    encoded=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.write:(HERE/'RESULT.json').write_text(encoded,encoding='utf-8',newline='\n')
    else:
        expected=json.loads((HERE/'RESULT.json').read_text())
        m.require(json.dumps(result,sort_keys=True)==json.dumps(expected,sort_keys=True),'typed receipt mismatch')
    print('PASS_CENTRE_TERMINAL_SOURCE_QUOTIENT calls=11 source_rank=8 variable_target_rank=16 outputs=224 controls=5')

if __name__=='__main__':main()
