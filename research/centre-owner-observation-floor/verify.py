#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact owner-local observation floor; native interpretation is conditional.
ywz65 with substantial OpenAI Codex assistance. See README for the contract.
"""
import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
MEMBERS = {
 'word': ('candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz', '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219'),
 'programs': ('candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz', '241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a'),
 'template': ('candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz', '2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760'),
 'phases': ('candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json', 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'),
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2)+'\n').encode()


def add(dst, src, coefficient=Q(1)):
    for i, v in list(src.items()):
        w = dst.get(i, Q(0)) + coefficient*v
        if w:
            dst[i] = w
        else:
            dst.pop(i, None)


def echelon(rows):
    pivots = {}
    for original in rows:
        row = dict(original)
        while row:
            k = min(row)
            if k not in pivots:
                v = row[k]
                pivots[k] = {i: q/v for i, q in row.items()}
                break
            add(row, pivots[k], -row[k])
    return pivots


def value(row, x):
    return sum((a*x.get(j, 0) for j, a in row.items()), Q(0))


def solve(matrix, rhs):
    n = len(matrix)
    a = [[Q(x) for x in row]+[Q(y)] for row, y in zip(matrix, rhs)]
    for j in range(n):
        p = next((i for i in range(j, n) if a[i][j]), None)
        need(p is not None, 'singular witness minor')
        a[p], a[j] = a[j], a[p]
        v = a[j][j]
        a[j] = [x/v for x in a[j]]
        for i in range(n):
            if i != j:
                v = a[i][j]
                a[i] = [x-v*y for x, y in zip(a[i], a[j])]
    return [row[-1] for row in a]


def replay(program):
    """Independent scalar replay; actual private pre-transport cuts."""
    rows = {('L', i): {i: Q(1)} for i in range(704)}
    cuts = {}
    for event in program:
        if event[0] == 'center':
            cuts[event[1]] = dict(rows['C', event[1]])
        elif event[0] == 'scalar':
            op = event[1]
            name, dst = op[0], tuple(op[1])
            if name == 'clear':
                rows[dst] = {}
            elif name == 'copy':
                rows[dst] = dict(rows[tuple(op[2])])
            elif name == 'scale':
                rows[dst] = {j: Q(op[2], op[3])*v for j, v in rows[dst].items()}
            elif name == 'add':
                add(rows[dst], rows[tuple(op[2])], Q(op[3], op[4]))
            else:
                raise ValueError('unknown scalar')
        else:
            need(event[0] in ('phase', 'climb', 'adapter', 'residual_adapter'), 'unknown event')
    need(set(cuts) == set(range(8)), 'eight queries')
    need(all(not row for key, row in rows.items() if key[0] == 'C'), 'private state not cleared')
    return [cuts[k] for k in range(8)], rows


def act(columns, x):
    result = 0
    for j, c in enumerate(columns):
        if x >> j & 1:
            result ^= c
    return result


def route(record):
    basis = record['idle_children'][0]['orthogonal_axes'][:8]
    local = [record['q']] + basis
    need(len(local) == 9 and all(0 < b < 512 for b in local), 'local chart shape')
    need(all((a & b).bit_count() % 2 == (i == j)
             for i, a in enumerate(local) for j, b in enumerate(local)), 'chart orthogonality')
    swap = [b ^ (1 << (9+j)) for j, b in enumerate(basis)]
    columns = tuple((1 << k) ^ act(swap, sum(((s >> k) & 1) << j for j, s in enumerate(swap))) for k in range(73))
    need(all(act(columns, act(columns, 1 << k)) == 1 << k for k in range(73)), 'route inverse')
    need(all((a & b).bit_count() % 2 == (i == j)
             for i, a in enumerate(columns) for j, b in enumerate(columns)), 'route orthogonality')
    need(act(columns, record['q']) == record['q'], 'fixed port')
    need(all(act(columns, b) == 1 << (9+j) and act(columns, 1 << (9+j)) == b
             for j, b in enumerate(basis)), 'route chart swap')
    beta = sum(((b.bit_count()-1)//2 % 2) << j for j, b in enumerate(basis))
    b_beta = act(basis, beta)
    need(record['stage_alignment'][0] == dict(entry_X=0, entry_Y=0, exit_X=0, exit_Y=0), 'stage0 translations')
    need(record['stage_alignment'][1] == dict(entry_X=record['q'] ^ b_beta,
         entry_Y=record['q'] ^ b_beta, exit_X=b_beta ^ (beta << 9), exit_Y=b_beta ^ (beta << 9)), 'stage1 translations')
    return columns


def load():
    for p in json.loads((HERE/'SOURCES.json').read_bytes())['files']:
        if p['usage'] == 'input':
            need(hashlib.sha256((ROOT/p['path']).read_bytes()).hexdigest() == p['sha256'], 'source pin: '+p['path'])
    data = {}
    with tarfile.open(ROOT/ARCHIVE) as archive:
        for key, (path, digest) in MEMBERS.items():
            entries = [m for m in archive.getmembers() if m.name == path]
            need(len(entries) == 1 and entries[0].isfile(), 'unique regular archive member')
            raw = archive.extractfile(entries[0]).read()
            need(hashlib.sha256(raw).hexdigest() == digest, 'member pin: '+path)
            data[key] = json.loads(gzip.decompress(raw) if path.endswith('.gz') else raw)
    return data


def build():
    data = load()
    programs, template = data['programs'], data['template']
    forward, end = replay(programs['forward'])
    backward, bend = replay(programs['backward'])
    R = [{p: q for p, q in row.items() if p < 112} for row in forward]
    for i in range(704):
        expected = {i: Q(1)}
        if 112 <= i < 224:
            expected[i-112] = Q(1)
        need(end['L', i] == expected, 'complete first scalar endpoint')
        expected = {i: Q(1)}
        if i < 112:
            expected[i+112] = Q(-1)
        need(bend['L', i] == expected, 'complete second scalar endpoint')
    H = []
    for row in backward:
        out = {}
        for i, q in row.items():
            add(out, {p: v for p, v in end['L', i].items() if p < 112}, q)
        H.append(out)
    need(H == [{p: q/4 for p, q in row.items()} for row in R], 'quarter identity')
    need(len(echelon(R)) == len(echelon(H)) == 8, 'source or later rank')
    calls = sorted(template['calls'], key=lambda c: c['time'])
    need([(calls[t]['time'], calls[t]['stage'], calls[t]['replica'], calls[t]['orientation']) for t in (0, 4)]
         == [(0, 0, 0, 'forward'), (4, 1, 0, 'backward')], 'selected pair')
    for c in calls[:5]:
        digest = hashlib.sha256(json.dumps(programs[c['orientation']], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        need(c['local_program_sha256'] == digest, 'program binding')
        need(len(c['owners']) == len({o[0] for o in c['owners']}) == 704, 'injective owners')
    for t, stage in ((0, 0), (4, 1)):
        need(calls[t]['owners'][:224] == [[p, [1, stage, p % 112]] for p in range(224)], 'owner/chart boundary')
    need(all(not set(range(224)) & {o[0] for o in c['owners']} for c in calls[1:4]), 'intervening data contact')
    need([e['kind'] for e in template['execution_schedule'][:5]] == ['local_cover_sweep']*5, 'intervening nonlocal event')
    need([(e['time'], e['replica'], e['stage']) for e in template['execution_schedule'][:5]]
         == [(c['time'], c['replica'], c['stage']) for c in calls[:5]], 'schedule alignment')
    routes = [route(rec) for rec in data['phases']['recipes']]
    need(len(routes) == len(set(routes)) == 112, '112 distinct owner routes')
    need([r['q'] for r in data['phases']['recipes']] == data['word']['ports'], 'port route order')
    witnesses = []
    for p in range(112):
        reduced = [{j: a for j, a in row.items() if j != p} for row in R]
        pivots = sorted(echelon(reduced))
        need(len(pivots) == 8, 'coordinate determined by old transcript')
        coeffs = solve([[row.get(j, 0) for j in pivots] for row in R], [-row.get(p, 0) for row in R])
        x = {j: q for j, q in zip(pivots, coeffs) if q}
        x[p] = Q(1)
        need(all(value(row, x) == 0 for row in R), 'old transcript kernel witness')
        response = [row.get(p, Q(0)) for row in H]
        need(any(response), 'inactive routed port')
        need(len(echelon(R + [{p: Q(1)}])) == 9, 'new owner-local dimension')
        witnesses.append(dict(port=p, kernel={str(j): str(v) for j, v in sorted(x.items())}, later_response=[str(v) for v in response]))
    quotient = [{k: row.get(p, Q(0)) for k, row in enumerate(H) if row.get(p, 0)} for p in range(112)]
    need(len(echelon(quotient)) == 8, 'aggregate quotient rank')
    # For the entire later field, input supported at ONE old owner g is
    # observed at d_p=g*rho_p^-1. Distinct rho_p give disjoint output blocks.
    single_owner_output = [{p: row[p]} for p in range(112) for row in H if row.get(p, 0)]
    need(len(echelon(single_owner_output)) == 112, 'single-owner later-field injectivity')
    basis_columns = sorted(echelon(R))
    complementary = [p for p in range(112) if p not in basis_columns]
    repaired = R + [{p: Q(1)} for p in complementary]
    need(len(complementary) == 104 and len(echelon(repaired)) == 112, '104-coordinate repair attainment')
    need(len(echelon(repaired[:-1])) == 111, '103-coordinate insufficient control')
    need(witnesses[0]['kernel'].get('0') == '1', 'local repair positive')
    need(any(Q(x) for x in witnesses[1]['later_response']), 'unread-owner repair failure')
    need(len(echelon(R + H)) == 8, 'collapsed-owner zero-cost control')
    need(len(echelon(R + [R[0]])) == 8, 'redundant observation control')
    need(len(echelon(R + [{0: Q(1)}])) == 9, 'new coordinate positive')
    controls = ['all112_omitted_owner_collisions', 'one_local_read_repairs_its_owner',
                'one_local_read_fails_at_other_owner', 'collapsed_routes_restore_quarter_identity',
                'old_row_observation_is_redundant', 'new_coordinate_increases_rank',
                '103_coordinate_repair_loses_one_dimension']
    return dict(status='PASS_CENTRE_OWNER_OBSERVATION_FLOOR', calls=[0, 4],
                model='constant payloads; D varies independently by physical cover owner; other dirt fixed',
                distinct_routes=112, old_rank_per_owner=8, old_rank_on_relevant_owners=896,
                joint_old_and_later_rank=904, extra_aggregate_scalar_minimum=8,
                extra_owner_local_scalar_minimum=112,
                single_old_owner_later_full_field_rank=112,
                whole_field_extra_scalar_coordinates_per_old_owner_minimum=104,
                sharp_repair_complementary_coordinates=complementary,
                R=[[str(row.get(j, 0)) for j in range(112)] for row in R],
                H=[[str(row.get(j, 0)) for j in range(112)] for row in H],
                route_sha256=[hashlib.sha256(canonical(list(r))).hexdigest() for r in routes],
                witnesses=witnesses, controls=controls,
                native_status='conditional on inherited common-frame/source-adapter and constant endpoint identities; not a native cold replay',
                unchanged_rank8_children_per_call=8, unchanged_centre_charge_per_call=64)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path)
    parser.add_argument('--receipt', type=Path, default=HERE/'RESULT.json')
    args = parser.parse_args()
    result = build()
    if args.write:
        with args.write.open('xb') as stream:
            stream.write(canonical(result))
    else:
        need(canonical(result) == canonical(json.loads(args.receipt.read_bytes())), 'receipt mismatch')
    print('PASS_CENTRE_OWNER_OBSERVATION_FLOOR full_field_extra_per_owner=104 one_output_owner_extra_local=112 aggregate=8 controls=7')


if __name__ == '__main__':
    main()
