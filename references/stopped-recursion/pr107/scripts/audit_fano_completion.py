#!/usr/bin/env python3
"""Fano coding seed: nonroutable clean graph, routable dirty completions."""
from hashlib import sha256
from pathlib import Path
import json

from certify import require,verify_sources
from finite_bit_contract import physical_graph,check_routing_paths,zero_frame_candidate,inspect_candidate
from routing_smt import paths_from_port_choices
from experiments.fano_completion import FANO_EDGES,code,clean_prefix,cases,scalar_check,program_hash
from experiments.partial_routing import partial_routing

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT/'scripts/experiments/fano_routing_witnesses.json'
SOURCE = 'https://arxiv.org/abs/1609.05815'


def reachable(edges,source,target,removed=()):
    visited = {source}; todo = [source]
    while todo:
        u = todo.pop()
        if u == target: return True
        for index,(a,b) in enumerate(edges):
            if index not in removed and a == u and b not in visited:
                visited.add(b); todo.append(b)
    return False


def forced_cut_certificate(edges,pairs,first,second):
    # Pairs are ordered a->ta, b->tb, c->tc.
    require(all(reachable(edges,s,t) for s,t in pairs),'A terminal is unreachable')
    require(not reachable(edges,*pairs[0],removed=(first,)),'First edge not mandatory for a')
    require(not reachable(edges,*pairs[2],removed=(second,)),'Second edge not mandatory for c')
    require(not reachable(edges,*pairs[1],removed=(first,second)),'b bypasses the two-edge cut')
    require(first != second,'Need distinct forced edges')
    return dict(a_forced_edge=first,c_forced_edge=second,b_cut=[first,second],
                no_edge_disjoint_routing=True,
                proof='The a and c paths occupy the two distinct edges; every b path must use one of them.')


def integer_code_matrix(compact=True,edge_explicit=False):
    spec = code(compact,edge_explicit)
    values = [(1,0,0),(0,1,0),(0,0,1)]
    for args in spec['nodes']:
        values.append(tuple(sum(values[j][i] for j in args) for i in range(3)))
    return [tuple(sum(values[j][i] for j in args) for i in range(3)) for args in spec['outputs']]


def seed_checks():
    pairs = [('a','ta'),('b','tb'),('c','tc')]
    cut = forced_cut_certificate(FANO_EDGES,pairs,6,7)
    original = partial_routing(FANO_EDGES,pairs)
    require(not original['routable'] and original['path_counts'] == [1,3,1], 'Wrong seed graph')
    variants = []
    for layout,compact,edge in (('compact',True,False),('decoded',False,False),('edge',True,True)):
        M = integer_code_matrix(compact,edge)
        require(M == [(1,2,2),(2,3,2),(2,2,1)],'Wrong Fano all-plus lift')
        I = [[int(i == j) for j in range(3)] for i in range(3)]
        require([[x%2 for x in row] for row in M] == I,'Wrong characteristic-two scalar code')
        p = clean_prefix(compact,edge); W = p['W']; gates = p['gates']
        full_edges = physical_graph(W,gates); edges = [(u,v) for u,v,_ in full_edges]
        terminals = [(i,W+len(gates)+3+i) for i in range(3)]
        route = partial_routing(edges,terminals)
        require(route['routable'] == (not edge),'Unexpected clean-prefix routing')
        entry = dict(layout=layout,W=W,primitive_xors=len(gates),integer_fixed_code_matrix=M,
                     clean_GF2_code_correct=True,routing=route,program_sha256=program_hash(p))
        if edge:
            cuts = []
            for original_edge in (6,7):
                role = 6+original_edge
                write = max(i for i,g in enumerate(gates) if g['xors'][0][0] == role)
                read = min(i for i,g in enumerate(gates) if i > write and g['xors'][0][1] == role)
                cuts.append(full_edges.index((W+write,W+read,role)))
            entry['forced_cut'] = forced_cut_certificate(edges,terminals,*cuts)
        variants.append(entry)
    return dict(source_url=SOURCE,source_location='Figure 1(a), degree-two e1 path contracted',
                original_edges=[list(e) for e in FANO_EDGES],original_routing=original,
                original_forced_cut=cut,clean_realizations=variants,
                scope='The fixed all-plus code is checked over F2 and as an integer lift. This does not independently prove the literature theorem excluding every odd-characteristic code.')


def replay(name,program,fixture):
    record = fixture[name]
    require(record['program_sha256'] == program_hash(program),'Routing witness is for a different circuit')
    switches = record['switches']; gates = program['gates']; W = program['W']
    require(len(switches) == len(gates) and set(switches) <= {'0','1'},'Malformed switch witness')
    choices = [g['roles'] if bit == '0' else list(reversed(g['roles'])) for g,bit in zip(gates,switches)]
    paths = paths_from_port_choices(W,gates,choices)
    return dict(switches=switches,paths=paths,check=check_routing_paths(W,gates,paths))


def certificate():
    fixture = json.loads(FIXTURE.read_text()); records = []
    programs = list(cases())
    require(set(fixture) == {name for name,p in programs},'Missing or extra routing fixture')
    for name,p in programs:
        scalar = scalar_check(p); routing = replay(name,p,fixture)
        score = inspect_candidate(zero_frame_candidate(p['W'],p['gates']),require_deficit=False)
        require(score['deficit'] == 0,'Equality frame control changed')
        records.append(dict(name=name,scalar=scalar,routing=routing,
                            equality_control=dict(m=score['m'],s=score['s'],baseline=score['baseline'],
                                                  strict_transfer_contract=score['strict_transfer_contract']),
                            all_rational_frames_excluded=True))
    x,y,d1,d2,d3 = (1 << i for i in range(5))
    Y = y^x^d1; X = x^Y^d2; Y ^= X^d3
    require(X == y^d1^d2 and Y == x^d2^d3,'Wrong affine exchange offset formula')
    sources = ('scripts/audit_fano_completion.py','scripts/routing_smt.py',
               'scripts/experiments/fano_completion.py','scripts/experiments/partial_routing.py',
               'scripts/experiments/fano_routing_witnesses.json','docs/research/fano-completion-audit.md')
    return dict(status='FANO SEED SURVIVES EDGE STORAGE; TESTED DIRTY COMPLETIONS ARE ROUTABLE; NO NEW KAPPA',
                upstream_commit=verify_sources(),seed=seed_checks(),completed_cases=records,
                source_sha256={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},
                solver_required_for_replay=False,improved_frame_certificate_supplied=False,
                global_offset_cancellation=dict(final_X='y+d1+d2',final_Y='x+d2+d3',
                    criterion='Exact exchange iff all three offsets are equal, under these affine-shear assumptions.',
                    saved_per_invocation_XORs=dict(compact=14,decoded=19,edge=43)),
                scope='Fifteen specified completion circuits, all restoring each auxiliary role. Includes three shorter global-offset completions. Does not exclude other Fano completions or completions that permute auxiliary roles.',
                decision='Preserve the nonroutable edge-level seed; redesign completion itself before attempting matrix optimization.')


if __name__ == '__main__':
    result = certificate()
    (ROOT/'certificates/fano-completion-audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS nonroutable Fano/edge-prefix controls; 15 exact dirty completions have checked routings; no new kappa.')
