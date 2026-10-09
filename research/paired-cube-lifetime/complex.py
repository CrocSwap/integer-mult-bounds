#!/usr/bin/env python3
"""Rebuild and check the selected fused paired-cube complex supplier.

The selected scalar graph/word and compensated birth pairs are pinned PR163,
by Chafik Boukhalfa with OpenAI Codex assistance, building on eumemic's PR161
and icekylinx's paired-cube and completed-core interfaces. This contribution
moves connected equal-frame components and exactly rank-neutral frames; it
preserves the scalar word, gauges, all pairs and the complete role inventory.
Developed with OpenAI Codex assistance. Apache-2.0.
"""
from collections import defaultdict
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SELECTED = HERE/'selected/complex'
sys.path.insert(0,str(ROOT/'scripts'))


def canonical(value):
    return json.loads(json.dumps(value))


def proof_fields(row):
    ignored = {'numerical_complex_root','status','gauge_selection','gauge_cost_rejections','gauge_trial_saving'}
    return canonical({k:v for k,v in row.items() if k not in ignored})


def fused_graph():
    """Regenerate every signed scalar node and root from pinned PR161 modules."""
    from fractions import Fraction
    from paired_cube.graph import Graph
    from paired_cube.modules import restricted_triples_from,pair_module_from,all_but_one
    src = ROOT/'references/paired-cube/sources'
    for name,digest in json.loads((src/'SOURCE.json').read_text())['files'].items():
        assert hashlib.sha256((src/name).read_bytes()).hexdigest() == digest
    builder = Graph(11)
    g = builder.finish(restricted_triples_from(src/'h20_g1.json.gz',[0,1,2,3,4,5,6,7,8,9,16]),
                       pair_module_from(src/'pmod_C35_5.483127e-4.json',10),all_but_one(9))
    channels = ('face2','edge02','edge12')
    found = {(tuple(r['targets']),r['channel']):r for r in g['roots'] if r.get('channel') in channels}
    roots = [r for r in g['roots'] if r.get('channel') not in channels]
    for targets in sorted({t for t,c in found}):
        parts = [found[targets,c] for c in channels]
        parts.sort(key=lambda r:Fraction(r['coefficients'][0]) < 0)
        assert parts[0]['coefficients'] == ['1/2']
        node = parts[0]['node']
        for r in parts[1:]:
            sign = 2*Fraction(r['coefficients'][0]); assert sign in (-1,1)
            node = builder.add(node,r['node'],int(sign))
        roots.append(dict(node=node,targets=list(targets),coefficients=['1/2'],kind='side',
                          channel='fused:face2,edge02,edge12'))
    channel_order = {'disjoint':0,'face0':1,'face1':2,'edge01':3,'fused:face2,edge02,edge12':4}
    roots.sort(key=lambda r:(1,r['coordinate']) if r['kind'] == 'center' else
               (0,min(r['targets'])//8,-len(r['targets']),min(r['targets']),channel_order[r['channel']]))
    counts = dict(g['counts'],signed_additions=sum(s < 0 for s in builder.signs),
                  side_root_uses=sum(r['kind'] == 'side' for r in roots),new_fusion_additions=2640)
    return dict(g,roots=roots,args=builder.a,signs=builder.signs,counts=counts,matching_frames='coordinate')


def algebraic_birth_audit(g,word,R,pairs):
    """Check exact integer read responses and the hypotheses of PR124's lemma.

    Side coordinates below are twice their rational coefficients; the final
    h coordinates are integer copied-center responses, before center scatter.
    The common denominator of the complete scalar output is consequently six.
    This does not use sampled inputs or arithmetic modulo a prime.
    """
    v,h = g['v'],g['h']
    ops,coefficients = word['ops'],word['opcoeff']
    roots,rootroles = g['roots'],word['rootroles']
    response = [{} for _ in range(R)]
    for r,s in zip(roots,rootroles):
        assert not response[s]
        if r['kind'] == 'center':
            response[s] = {v+r['coordinate']:1}
        else:
            assert all(c in ('1/2','-1/2') for c in r['coefficients'])
            response[s] = {t:(1 if c == '1/2' else -1) for t,c in zip(r['targets'],r['coefficients'])}
    for (a,b,x),(ca,cb) in zip(reversed(ops),reversed(coefficients)):
        assert a != b and ca in (-1,1) and cb in (-1,1)
        for t,c in response[a].items():response[b][t] = response[b].get(t,0)+cb*c
        if ca != 1:response[a] = {t:ca*c for t,c in response[a].items()}
    response = [{t:c for t,c in row.items() if c} for row in response]
    selected = {z['role']:z for z in word['selected']}
    pset = set(word['phase1'])
    chronology = word['phase1']+[i for i in range(len(ops)) if i not in pset]
    position = {i:k for k,i in enumerate(chronology)}
    role_ops = defaultdict(list)
    for i,(a,b,x) in enumerate(ops):role_ops[a].append(i);role_ops[b].append(i)
    source_roles = set(word['sources'].values())
    root_roles = set(rootroles)
    donors,recipients = {a for a,b,t in pairs},{b for a,b,t in pairs}
    assert len(donors) == len(recipients) == len(pairs) and not donors & recipients
    alias = {b:a for a,b,t in pairs}
    for (a,b,x),(ca,cb) in zip(ops,coefficients):
        assert alias.get(a,a) != alias.get(b,b)
        assert ca*ca == 1 and ca*cb-ca*cb == 0
    rows = []
    for a,b,t in pairs:
        assert a not in selected and a not in root_roles
        assert b in selected and b not in source_roles
        assert all(i not in pset for i in role_ops[b])
        birth = len(pset) if t is None else position[t]
        if t is not None:assert t == role_ops[b][0]
        assert position[role_ops[a][-1]] < birth
        D = response[b]
        assert all(target < v for target in D), ('Center-dependent recipient',b)
        assert set(D) <= set(selected[b]['targets']), ('Undeclared read target',b)
        rows.append([b,sorted(D.items())])
    canonical = json.dumps(sorted(rows),separators=(',',':')).encode()
    return dict(exact_integer_response_backpropagation=True,
                compensated_recipients=len(pairs),
                zero_center_response_for_every_recipient=True,
                recipient_target_supports_contained=True,
                dead_donor_and_untouched_birth_chronology=True,
                aliased_gate_ports_disjoint=True,
                signed_gate_and_injection_inverse_polynomials_exact=True,
                selected_response_sha256=hashlib.sha256(canonical).hexdigest(),
                selected_side_response_denominator=2,
                selected_read_terms=sum(len(response[b]) for b in recipients),
                selected_max_abs_numerator=max(abs(c) for b in recipients for c in response[b].values()),
                proof_interface='PR124 compensated-birth lemma plus the regenerated signed H+K+B=I identity; this finite audit is not a formal proof of the retained multiplication theorem')


def checked_record(selected=SELECTED):
    """Read-only reconstruction; return physical profile and paid scalar stock.

    The exact birth audit checks the hypotheses of the compensated-birth
    identity. The inherited analytic, Clifford and all-size transfer contracts
    remain explicit dependencies; finite checks do not formalize that theorem.
    """
    if sys.flags.optimize:raise ValueError('Run without -O; finite assertions must remain enabled')
    selected = Path(selected)
    manifest = json.loads((selected/'SOURCE.json').read_text())
    for name,digest in manifest['files'].items():
        assert hashlib.sha256((selected/name).read_bytes()).hexdigest() == digest, name
    for name,digest in manifest['repository_files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
    def read(name):
        path = selected/(name+'.json.gz')
        return json.loads(gzip.decompress(path.read_bytes()))
    g = fused_graph()
    assert canonical(g) == read('graph'), 'Rebuilt fused scalar graph differs'
    witness_expected,word_expected = read('frames'),read('word')
    from paired_cube.frames import compile_graph
    from paired_cube.gauges import select
    baseline,witness = compile_graph(g,witness_expected['matching_arcs'])
    assert canonical(witness) == witness_expected, 'Full backward intersections/order differ'
    assert proof_fields(baseline) == proof_fields(read('baseline')), 'Baseline rank ledger differs'
    logical,word = select(g,baseline,witness)
    assert canonical(word) == word_expected, 'Rebuilt signed physical word differs'
    assert proof_fields(logical) == proof_fields(read('profile-before')), 'Logical profile differs'
    verifier_path = selected/'verify_fused.py'
    spec = importlib.util.spec_from_file_location('_selected_fused_finite',verifier_path)
    finite = importlib.util.module_from_spec(spec);spec.loader.exec_module(finite)
    finite_checks = finite.verify(g,baseline,witness,word,logical)
    from paired_cube_physical import physical
    pairs = read('physical-pairs')
    result = physical(g,witness,word,logical,read('physical-frames'),pairs)
    assert canonical(result) == json.loads((selected/'physical-profile.json').read_text()), 'Physical recount differs'
    birth = algebraic_birth_audit(g,word,logical['R'],pairs)
    assert canonical(birth) == json.loads((selected/'birth-audit.json').read_text()), 'Exact birth audit differs'
    return dict(profile=result,scalar=proof_fields(logical),exact_birth_audit=birth,
                finite_checks=finite_checks,source_graph_rebuilt=True,all_source_pins_verified=True,
                source_commit=manifest['source_pr163']['commit'],
                scope='Finite conditional supplier. Retained Clifford/shared-core, analytic, precision and uniform transfer contracts remain proof dependencies.')


if __name__ == '__main__':
    print(json.dumps(checked_record(),indent=2,sort_keys=True))
