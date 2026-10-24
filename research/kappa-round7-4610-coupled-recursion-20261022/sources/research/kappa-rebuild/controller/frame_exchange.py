#!/usr/bin/env python3
"""Actual owner/phase admission for H wrappers and a same-future-query exchange.

Apache-2.0; substantial OpenAI assistance. This extends the exact phase
conventions credited in kappa-next-regime/direct-decoder/native_common.py.
The native H block is supplied by the separately certified reconstruction.
This file proves contacts and a reversible dirty-bank primitive, not a closed
global supplier or a rounded recursive induction.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NATIVE = ROOT/'research/kappa-next-regime/direct-decoder/native_common.py'
REBUILD = HERE.parent/'complex/rebuild_native.py'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def between(n, old, g, new):
    """Physical translation-permutation with exact prescribed logical g.

    All F references are commuting C_q products. Their Fourier symbols are
    i raised to the stored Z4 quadratic polynomials. An affine permutation
    contributes a linear even phase. Equality of these polynomials, including
    their zero constant, proves the whole operator, not just polar rank.
    """
    actual, wanted = n.polynomial(n.move_frame(old, g)), n.polynomial(new)
    need(actual[1] == wanted[1], 'No quadratic phase mismatch')
    delta = tuple((a-b) % 4 for a, b in zip(wanted[0], actual[0]))
    need(all(x in (0, 2) for x in delta), 'Translation repairs only even linear phase')
    shift = sum((x//2) << i for i, x in enumerate(delta))
    need(n.polynomial(n.move_frame(old, g, shift)) == wanted, 'Full Z4 phase identity')
    inv = tuple(sum(((g[j] >> i) & 1) << j for j in range(73)) for i in range(73))
    need(n.product(g, inv) == n.product(inv, g) == n.AXES, 'Orthogonal inverse')
    inverse_shift = n.act(inv, shift)
    need(n.polynomial(n.move_frame(new, inv, inverse_shift)) == n.polynomial(old),
         'Exact inverse phase and coordinate map')
    return dict(owner_columns=list(g), physical_shift=shift,
                inverse_owner_columns=list(inv), inverse_physical_shift=inverse_shift,
                global_phase_Z4=0)


def birth(n, before, future):
    need(0 <= before < future <= 8, 'Causal future-owner contact')
    return n.frame([(a, 1) for a in n.AXES[9:9+8*before]] +
                   [(a, 1) for a in n.AXES[9+8*(future-1):9+8*future]])


def contact_certificate(n, phases):
    records = {}
    # H_s is read at preY_s and postX_s. Both logical operators are D_s H D_s.
    for stage in range(9):
        pre_common = () if stage == 0 else birth(n, stage-1, stage)
        post_common = n.completed(stage)
        pre, post = [], []
        for p, recipe in enumerate(phases['recipes']):
            g = n.source_route(phases, stage, p)
            old = () if stage == 0 else n.frame(list(n.completed(stage-1))+[(recipe['q'], -1)])
            pre.append(between(n, old, g, pre_common))
            post.append(between(n, post_common, g, post_common))
        records[str(stage)] = {'preY_common': list(pre_common), 'postX_common': list(post_common),
                               'preY_views': pre, 'postX_views': post}
    return records


def rows_identity(n):
    return {i: {(i, n.AXES): Q(1)} for i in range(120)}


def exchange(n, geo, phases, rows, future):
    """Literal112 Y +8 P word; no owned field, overwrite or clearing."""
    counts = Counter()
    for p in range(112):
        rows[p] = n.routed(n.source_route(phases, future, p), rows[p]); counts['view'] += 1
    for k, a in enumerate(geo['selected']):
        for p, c in geo['L'][k].items():
            n.sparse_add(rows[a], rows[p], c); counts['half_add'] += 1
    for k, a in enumerate(geo['selected']):
        b = 112+k
        n.sparse_add(rows[a], rows[b], Q(1))
        n.sparse_add(rows[b], rows[a], Q(-1))
        n.sparse_add(rows[a], rows[b], Q(1))
        rows[b] = {key: -c for key, c in rows[b].items()}
        counts['unit_add'] += 3; counts['negate'] += 1
    for k, a in enumerate(geo['selected']):
        for p, c in geo['L'][k].items():
            n.sparse_add(rows[a], rows[p], -c); counts['half_add'] += 1
    for p in range(112):
        rows[p] = n.routed(n.source_route(phases, future, p), rows[p]); counts['view'] += 1
    return counts


def physical_witness(n, row):
    """A nonzero physical basis-column witness for a nonzero operator row."""
    for var in sorted({v for v, g in row}):
        for address in [0]+list(n.AXES):
            output = {}
            for (v, g), c in row.items():
                if v == var:
                    at = n.act(g, address)
                    output[at] = output.get(at, Q(0))+c
            output = {k: v for k, v in output.items() if v}
            if output:
                at = min(output)
                return dict(input_field=var, input_address=address, output_address=at,
                            coefficient=str(output[at]))
    raise ValueError('A formal mismatch was not promoted to a physical witness')


def run(output):
    n, h = load(NATIVE, 'rebuild_native_contacts'), load(REBUILD, 'rebuild_h_for_contacts')
    packet, phases = n.load_sources()
    geo = h.geometry(packet)
    contacts = contact_certificate(n, phases)
    original = rows_identity(n)
    first = {i: row.copy() for i, row in original.items()}
    counts = exchange(n, geo, phases, first, 2)
    # Check independent derived formula Y'=(I-EQ)Y+EP, P'=QY.
    queries = []
    for k, a in enumerate(geo['selected']):
        q = n.routed(n.source_route(phases, 2, a), original[a])
        for p, c in geo['L'][k].items():
            n.sparse_add(q, n.routed(n.source_route(phases, 2, p), original[p]), c)
        queries.append(q)
        need(first[112+k] == q, 'Actual owner-valued query output')
    for p in geo['ordinary']:
        need(first[p] == original[p], 'Ordinary Y unchanged')
    for k, a in enumerate(geo['selected']):
        delta = original[112+k].copy(); n.sparse_add(delta, queries[k], Q(-1))
        wanted = original[a].copy()
        n.sparse_add(wanted, n.routed(n.source_route(phases, 2, a), delta), Q(1))
        need(first[a] == wanted, 'Selected right-inverse insertion')
    second = {i: row.copy() for i, row in first.items()}
    exchange(n, geo, phases, second, 2)
    need(second == original, 'All120 arbitrary input fields restored by same query twice')
    wrong = {i: row.copy() for i, row in original.items()}
    exchange(n, geo, phases, wrong, 1)
    exchange(n, geo, phases, wrong, 2)
    mismatch = next(i for i in range(112,120) if wrong[i] != original[i])
    diff = wrong[mismatch].copy(); n.sparse_add(diff, original[mismatch], Q(-1))
    negative = {'output_field': mismatch, **physical_witness(n, diff)}
    # The two actual cuts are after local0 and after local1. Y is unchanged by
    # the intervening backward call, so the second identical logical exchange
    # returns every arbitrary P baseline, even when H1 does not commute with H2.
    bank_frames = [birth(n, b, 2) for b in (0,1)]
    timed = []
    for before, common in zip((0,1), bank_frames):
        views = []
        for p, recipe in enumerate(phases['recipes']):
            old = n.frame(list(n.completed(before))+[(recipe['q'], -1)])
            views.append(between(n, old, n.source_route(phases, 2, p), common))
        timed.append(dict(after_stage=before, common_frame=list(common), views=views))
    difference = n.frame(list(bank_frames[1])+[(a,-c) for a,c in bank_frames[0]])
    expected = n.frame((a,1) for a in n.AXES[9:17])
    need(n.polynomial(difference) == n.polynomial(expected), 'Bank relative operator is exactly positive rank8')
    # A direct tensor product of the eight C_e factors has no hidden phase.
    need(all(c == 1 and a in n.AXES[9:17] for a,c in difference), 'Literal rank8 child axes')
    result = dict(schema='native-future-query-and-H-wrapper-contacts-v1',
                  status='PASS_EXACT_CONTACTS_AND_DIRTY_EXCHANGE_NOT_CALLER_CLOSURE',
                  generator_sha256=digest(__file__), dependency_hashes={str(NATIVE.relative_to(ROOT)):digest(NATIVE),
                    str(REBUILD.relative_to(ROOT)):digest(REBUILD)},
                  immutable_source_pins=n.PINS,
                  H_wrapper_contacts=contacts,
                  wrapper_identity='postX(H_s) F_or_B(H_s) preY(H_s) = diag(H_s,H_s) F_or_B(I)',
                  p1_abstract_endpoint='diag(H2 H1 H0,H2 H1 H0) times signed swap; no commutation assumed',
                  timed_same_future_query=timed,
                  exchange_formula='Y_new=Y+E2(P-Q2Y), P_new=Q2Y; Q2E2=I',
                  one_exchange_counts=dict(counts),
                  one_exchange_real_scalar_allowance=counts['half_add']*10+counts['unit_add']*8+counts['negate']*2,
                  exchanged_arbitrary_input_fields=120,
                  all_arbitrary_Y_P_columns_restored=True,
                  bank_relative_child_profile={'8':8},
                  bank_target_credit='8 independent rank8 transforms only after all main cross-dependence is removed',
                  wrong_query_physical_negative_control=negative,
                  no_owned_fields=True,
                  open_obligations=['head/hole main endpoint closure','main dependence on dirty bank after intervening B',
                    'strict child hierarchy if combined with minjob6 recipe','rounded induction and precision',
                    'full mixed-job supplier and BIT premise'], no_new_kappa_claimed=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    raw=json.dumps(result, sort_keys=True, separators=(',',':')).encode()
    output.write_bytes(gzip.compress(raw,mtime=0))
    print(json.dumps({k:v for k,v in result.items() if k in ('status','one_exchange_counts',
      'one_exchange_real_scalar_allowance','wrong_query_physical_negative_control')}))
    print('phase contacts',9*112*2+2*112,'receipt',str(output),'sha256',digest(output))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=HERE/'FRAME-EXCHANGE.json.gz')
    run(parser.parse_args().out)
