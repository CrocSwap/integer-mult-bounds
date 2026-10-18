#!/usr/bin/env python3
"""Exact joint-order audit. Helper checks adapted from Curtis Dransfield PR863.
Apache-2.0. Substantial AI assistance: OpenAI Codex.
"""
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

from circuit import JointTies, tied_channels, recurrence_cost
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
    if isinstance(c, JointTies):
        require(additions <= recurrence_cost(c.h,c.root_split,c.flips), 'exceeded recurrence')
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
    from itertools import permutations
    pins=check_pins()
    h=22
    expected=expected_map(h)
    ties=tied_channels(h,11)
    require(ties == [(0,0),(1,1),(2,2),(3,3)], 'tie domain changed')
    initial=[]
    for mask in range(16):
        flips=tuple(c for i,c in enumerate(ties) if mask>>i&1)
        c=JointTies(h,11,flips)
        initial.append(dict(mask=mask,flips=flips,**verify_dag(c,expected)))
    require(min(r['additions'] for r in initial)==30708, 'initial negative result changed')
    require(all(r['dag_sha256']==initial[r['mask']&6]['dag_sha256'] for r in initial),
            'extreme tied channel changes DAG')
    rows=[]
    choices=((1,1),(2,2))
    for order in permutations(range(4)):
        for mask in range(4):
            flips=tuple(c for i,c in enumerate(choices) if mask>>i&1)
            c=JointTies(h,11,flips,order)
            rows.append(dict(order=order,flips=flips,mask=mask,
                unshared_addition_bound=recurrence_cost(h,11,flips),
                **verify_dag(c,expected)))
    best_count=min(r['additions'] for r in rows)
    nominees=[r for r in rows if r['additions']==best_count]
    winner=nominees[25%len(nominees)]
    require(best_count==30698 and len(nominees)==6,'bounded winner changed')
    require(winner['order']==(1,2,3,0) and winner['flips']==((1,1),),'seed selection changed')
    base=DisjointTensor(h)
    prior=JointTies(h,11,((1,1),))
    best=JointTies(h,11,winner['flips'],winner['order'])
    base_checked=verify_dag(base,expected)
    prior_checked=verify_dag(prior,expected)
    require(prior_checked['dag_sha256']=='739862c655afb421cd2a19ba5bfa3cb06d6fa4acf57b9390ab6353d839c45f8b',
            'PR863 pinned comparator drift')
    require(initial[0]['dag_sha256']==base_checked['dag_sha256'],'no-flip adapter drift')
    bills=[invoice(c) for c in (base,prior,best)]
    d=prior.additions-best.additions
    require(d==10,'marginal role saving changed')
    require(bills[1]['three_stage_scalar_bound']-bills[2]['three_stage_scalar_bound']
        ==24*comb(h,3)**2*d,'incomplete marginal scalar invoice')
    # Every dirty helper is restored by signed cancellation. Dense controls
    # supplement the written all-input linear algebra; they are not a proof.
    dirty=dirty_check(best)
    from independent import run_cases
    recipes=[((0,1,2,3),()),((0,1,2,3),((1,1),)),
             (winner['order'],winner['flips']),((0,1,2,3),choices)]
    independent=run_cases(recipes)
    for recipe,result in zip(recipes,independent):
        c=JointTies(h,11,recipe[1],recipe[0])
        checked=verify_dag(c,expected)
        require(checked['nodes_only_sha256']==result['nodes_only_sha256'],'independent DAG differs')
        require(checked['output_support_sha256']==result['output_support_sha256'],'independent map differs')
        require(checked['additions']==result['additions'],'independent count differs')
    small=[]
    for small_h in (8,10):
        c=JointTies(small_h,small_h//2,((1,1),),winner['order'])
        checked=verify_dag(c,expected_map(small_h))
        rebuilt=run_cases([(winner['order'],winner['flips'])],h=small_h,root_split=small_h//2)[0]
        require(checked['nodes_only_sha256']==rebuilt['nodes_only_sha256'],'small independent DAG differs')
        require(checked['output_support_sha256']==rebuilt['output_support_sha256'],'small independent map differs')
        small.append(dict(h=small_h,dag=checked,independent=rebuilt,frames=c.verify_frames(exact_bases=True)))
    return canonical(dict(status='FINITE HISTORICAL COMPLEX CIRCUIT CONSTRUCTION; NO NEW KAPPA',
        base_commit=pins['base_commit'],assignment_seed=25,
        selected_kappa_at_base='1661960547713947/1000000000000000000',
        predecessor=dict(pr=863,head='6c0ed3975fda8f0190b34f1b1bbedb33a925d339'),
        initial_tie_only=dict(ties=ties,labeled_cases=16,best_additions=30708,
            result='No extra saving beyond PR863 in this complete simultaneous-tie class',cases=initial),
        domain=dict(h=22,root_split=11,root_j_orders=24,tie_choices=4,labeled_cases=96,
            descendants='unchanged inherited planner',ordered_points='0..21',
            seed_selection='index 25 modulo number of minimum-count nominees',
            stopping_rule='complete these 96 recipes; no point permutations, descendant changes or further h scan'),
        search=rows,unique_dags=len({r['dag_sha256'] for r in rows}),winner=winner,
        baseline=base_checked,prior=prior_checked,marginal_helper_roles_saved=d,
        total_helper_roles_saved=base.additions-best.additions,
        baseline_invoice=bills[0],prior_invoice=bills[1],improved_invoice=bills[2],
        frames=best.verify_frames(),small_exact_phase_controls=small,
        independent_reconstruction=independent,full_h22_dense_dirty_controls=dirty,
        coefficient_positions_covered=(16+96)*len(expected)**2,
        scope='Historical h22 finite map, embedding and full invoice; no selected-supplier integration or all-size multiplication theorem.'))

def main():
    require(sys.version_info >= (3,10), 'Python 3.10+ is required for inherited frame checks')
    parser=argparse.ArgumentParser()
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    result=certificate()
    path=HERE/'CERTIFICATE.json'
    encoded=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.write: path.write_text(encoded,encoding='utf-8')
    else: require(json.loads(path.read_text(encoding='utf-8'))==result,'certificate differs')
    print('PASS_JOINT_ROOT_ORDERS recipes=96 additions=30708->30698 roles_saved=10 no_new_kappa')

if __name__=='__main__': main()
