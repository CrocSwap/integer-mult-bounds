#!/usr/bin/env python3
"""Reproduce a bounded contraction search and complete historical invoice."""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from math import comb
from pathlib import Path
import argparse
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def require(value, message):
    if not value:
        raise ValueError(message)

def check_pins():
    pins = json.loads((HERE/'SOURCE-PINS.json').read_text())
    for path, digest in pins['sha256'].items():
        require(sha256((ROOT/path).read_bytes()).hexdigest() == digest,
                'source pin mismatch: '+path)
    return pins

from circuit import RootContraction, feasible_channels, recurrence_cost
from experiments.disjoint_tensor import DisjointTensor, complex_counts, scalar_program
from complex_compression import LeaveOneCircuit, invoke, matching, saving_bounds
from general_network_guard import guard


def expected_map(h):
    triples = [sum(1 << x for x in t) for t in combinations(range(h), 3)]
    return {t:sum(1 << i for i,s in enumerate(triples) if not s&t) for t in triples}


def verify_dag(c, expected):
    """Check complete integer coefficients, not just parity or nonzero count."""
    require(set(c.outputs) == set(expected), 'output domain mismatch')
    for node in sorted(c.active):
        args = c.args[node]
        if args:
            a,b = args
            require(a in c.active and b in c.active and 0 < a < node and 0 < b < node,
                    'non-topological or missing input')
            require(c.support[a] & c.support[b] == 0, 'overlapping addition')
            require(c.support[node] == c.support[a] | c.support[b], 'wrong node support')
        else:
            require(c.support[node] == 1 << (node-1), 'wrong source support')
    for t,node in c.outputs.items():
        require(c.support[node] == expected[t], 'wrong output coefficients')
    additions = sum(c.args[n] is not None for n in c.active)
    require(additions == c.additions, 'addition count mismatch')
    if isinstance(c, RootContraction):
        require(additions <= recurrence_cost(c.h,c.root_split,c.flip), 'exceeded recurrence')
    code = c.compile()
    require(code['roles'] == additions+len(expected), 'role count mismatch')
    require(set(code['sources']) == set(c.inputs), 'source domain mismatch')
    values = [0]*code['roles']
    for s,slot in code['sources'].items():
        values[slot] = 1 << c.inputs.index(s)
    for node,ins,outs in code['gates']:
        require(len(set(ins))==len(ins) and set(ins)&set(outs)=={ins[0]}, 'bad gate slots')
        for slot in ins[1:]:
            require(not values[ins[0]] & values[slot], 'embedding overlaps supports')
            values[ins[0]] |= values[slot]
        for slot in outs[1:]:
            require(values[slot] == 0, 'fanout destination not fresh')
            values[slot] = values[ins[0]]
    require(set(code['outputs']) == set(expected), 'compiled output domain mismatch')
    for t,slot in code['outputs'].items():
        require(values[slot] == expected[t], 'compiled coefficient mismatch')
    payload = {'nodes':[[n,c.args[n],str(c.support[n])] for n in sorted(c.active)],
               'outputs':sorted(c.outputs.items())}
    digest = sha256(json.dumps(payload,separators=(',',':')).encode()).hexdigest()
    nodes_digest = sha256(json.dumps(payload['nodes'],separators=(',',':')).encode()).hexdigest()
    output_digest = sha256()
    width = (len(c.inputs)+7)//8
    for t in c.inputs:
        output_digest.update(c.support[c.outputs[t]].to_bytes(width,'little'))
    support_digest = sha256(json.dumps([str(c.support[n]) for n in sorted(c.active)],
                                      separators=(',',':')).encode()).hexdigest()
    return dict(additions=additions,roles=code['roles'],dag_sha256=digest,nodes_only_sha256=nodes_digest,
                output_support_sha256=output_digest.hexdigest(),
                ordered_support_sha256=support_digest,coefficient_entries=len(expected)**2,
                all_integer_coefficients_and_embedding_verified=True)


def invoice(c):
    code = scalar_program(c)
    n = complex_counts(c.h,c.additions+len(c.outputs))
    M = sum(len(ins)+len(outs)-2 for ins,outs in code['gates'])
    C,J = len(code['sources']),len(code['outputs'])
    v=n['v']; h=c.h
    require(M == 2*c.additions+comb(h,2)*2*LeaveOneCircuit(h-2).additions,'mixer count')
    require(C == J == 4*v,'source access/injection count')
    per_call = 4*M+2*C+4*J+18*v
    steps=3*v*v*per_call
    E=64*(n['W']+n['m']+1)**3
    slack=E-(4*steps+8*n['s']+8*n['W']+8*n['m'])
    require(slack>0,'insufficient scalar guard')
    lo,hi=saving_bounds(n)
    labels,pi=matching(h)
    require(all(any(i not in s and i not in labels[j] for i in range(h))
                for s,j in zip(labels,pi)),'join residual missing')
    return dict(counts=n,mixer_additions=M,source_accesses=C,weighted_injections=J,
                complete_signed_invocation_bound=per_call,three_stage_invocations=3*v*v,
                three_stage_scalar_bound=steps,E=E,node_charge_slack=slack,
                complex_saving_interval=[lo,hi],
                stopped_guard=guard(n['m'],n['s'],E,Q(1,100),Q(1,1000),Q(5)),
                matching_sha256=sha256(json.dumps(pi).encode()).hexdigest())


def dirty_check(c, cases=4):
    """Dense dyadic controls; not a full independent-column proof."""
    code=scalar_program(c); v=len(c.inputs); count=0
    for inverse in (False,True):
        for case in range(cases):
            banks=[[Q(((i+1)*(case+37)+j*13)%47-23,16)
                    for i in range(size)]
                   for j,size in enumerate([v,v,code['roles'],c.h+1])]
            old=[list(bank) for bank in banks]
            invoke(*banks,code,inverse=inverse)
            require(banks[0]==old[0] and banks[2:]==old[2:],'dirty source/scratch not restored')
            sign=-1 if inverse else 1
            require(banks[1]==[b+sign*a for a,b in zip(old[0],old[1])],'wrong signed map')
            count+=1
    return count


def canonical(value):
    if isinstance(value,Q): return str(value)
    if isinstance(value,dict): return {k:canonical(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)): return [canonical(v) for v in value]
    return value


def certificate():
    pins=check_pins(); h=22; expected=expected_map(h)
    baseline=DisjointTensor(h); baseline_checked=verify_dag(baseline,expected)
    rows=[]
    for left in range(1,h//2+1):
        for flip in [None,*feasible_channels(h,left)]:
            c=RootContraction(h,left,flip)
            rows.append(dict(root_split=left,flip=flip,
                             unshared_addition_bound=recurrence_cost(h,left,flip),
                             **verify_dag(c,expected)))
    require(len(rows)==154,'search coverage changed')
    winner=min(rows,key=lambda r:r['additions'])
    require(winner['root_split']==11 and winner['flip']==(1,1) and winner['additions']==30708,
            'winning recipe changed')
    control=next(r for r in rows if r['root_split']==11 and r['flip'] is None)
    require(control['dag_sha256']==baseline_checked['dag_sha256'],'baseline adapter drift')
    best=RootContraction(h,11,(1,1))
    old_invoice,new_invoice=invoice(baseline),invoice(best)
    saving=baseline.additions-best.additions
    require(old_invoice['three_stage_scalar_bound']-new_invoice['three_stage_scalar_bound']
            ==24*comb(h,3)**2*saving,'incomplete scalar saving')
    from independent_check import independent_check
    independent=independent_check()
    for result in independent['results']:
        rebuilt=RootContraction(result['h'],result['root_split'],result['flip'])
        checked=verify_dag(rebuilt,expected_map(result['h']))
        require(checked['nodes_only_sha256']==result['dag_sha256'], 'independent DAG differs')
        require(checked['output_support_sha256']==result['output_support_sha256'], 'independent map differs')
        require(checked['additions']==result['additions'], 'independent count differs')
    small=[]
    for small_h in (8,10):
        c=RootContraction(small_h,small_h//2,(1,1))
        small.append(dict(h=small_h,dag=verify_dag(c,expected_map(small_h)),
                          frames=c.verify_frames(exact_bases=True)))
    return canonical(dict(status='FINITE HISTORICAL COMPLEX CIRCUIT IMPROVEMENT; NO NEW KAPPA',
        base_commit=pins['base_commit'],assignment_seed=37,
        selected_kappa_at_base='1661634653669567/1000000000000000000',
        domain=dict(h=22,root_split_sizes=list(range(1,12)),maximum_flipped_channels=1,
                    descendant_plans='inherited without changes',labeled_cases=154,
                    unique_dags=len({r['dag_sha256'] for r in rows}),
                    stopping_rule='complete this finite domain; no multiple flips or further h scan'),
        baseline=baseline_checked,search=rows,winner=winner,helper_roles_saved=saving,
        baseline_invoice=old_invoice,improved_invoice=new_invoice,
        frames={'baseline':baseline.verify_frames(),'improved':best.verify_frames()},
        small_exact_phase_controls=small,independent_reconstruction=independent,full_h22_dense_dirty_controls=dirty_check(best),
        scope='Full finite h22 side map and embedding; inherited phase enclosure and signed invocation algebra; finite dense dirty controls are not a proof of the all-size multiplication theorem.'))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true')
    args=parser.parse_args(); result=certificate();path=HERE/'CERTIFICATE.json'
    if args.write: path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else: require(json.loads(path.read_text())==result,'certificate differs')
    print('PASS: 154 cases; 31,929 -> 30,708 additions; 1,221 paid roles saved; no new kappa.')

if __name__=='__main__': main()
