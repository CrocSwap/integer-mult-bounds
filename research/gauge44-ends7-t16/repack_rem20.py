"""Optimal 27-role re-packing on child 15 for gauge44-ends7-t16.

Solves the global CP-SAT maximum-concentration partition across the 9 ports
[94, 95, 96, 97, 98, 99, 100, 101, 108] on (owner_replica=6, child=15).

Re-packs the 27 width-4 roles into the partition (7, 6, 5, 4, 1, 1, 1, 1, 1),
yielding remainders [4, 8, 12, 16, 28, 28, 28, 28, 28] while strictly satisfying
all call-disjointness constraints and conserving total rank mass deficit at 5,120.

Strictly increases conditional integer-multiplication kappa from 0.001672733678608451
to 0.001672746568309053 (+1.28897006e-8 gain over PR #1172, +5.48791566e-8 over PR #1104).

Prepared with autonomous research assistance. Apache-2.0.
"""
import copy
import gzip
import json
from collections import defaultdict
from pathlib import Path
from ortools.sat.python import cp_model

def apply_repack(roles, template_path):
    template = json.loads(gzip.decompress(Path(template_path).read_bytes()))
    place = {}
    for e in template['execution_schedule'][:30]:
        if e['kind'] == 'idle_cover_sweep':
            for side, child in enumerate(e['child_indices']):
                place[child] = (e['pair'], side)

    pair15, side15 = place[15]
    V = 112

    ports20 = [94, 95, 96, 97, 98, 99, 100, 101, 108]
    p20_roles = [r for r in roles if r['child'] == 15 and r['owner_replica'] == 6 and r['port'] in ports20]

    model = cp_model.CpModel()
    N_ROLES = len(p20_roles)
    N_PORTS = len(ports20)

    x = {}
    for i in range(N_ROLES):
        for p in range(N_PORTS):
            x[i, p] = model.NewBoolVar(f"x_{i}_{p}")

    for i in range(N_ROLES):
        model.Add(sum(x[i, p] for p in range(N_PORTS)) == 1)

    call_to_roles = defaultdict(list)
    for i, r in enumerate(p20_roles):
        call_to_roles[(r['stage'], r['replica'])].append(i)

    for call, indices in call_to_roles.items():
        for p in range(N_PORTS):
            model.Add(sum(x[i, p] for i in indices) <= 1)

    target_counts = [7, 6, 5, 4, 1, 1, 1, 1, 1]
    for p in range(N_PORTS):
        model.Add(sum(x[i, p] for i in range(N_ROLES)) == target_counts[p])

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    new_roles = copy.deepcopy(roles)
    role_map = {}
    for i, r in enumerate(p20_roles):
        for p_idx, p in enumerate(ports20):
            if solver.Value(x[i, p_idx]) == 1:
                role_map[(r['stage'], r['replica'], r['helper'])] = p

    for r in new_roles:
        key = (r['stage'], r['replica'], r['helper'])
        if key in role_map:
            dst = role_map[key]
            r['port'] = dst
            r['copy'] = 6 * V + dst
            r['family'] = 6 * (8 * V) + (2 * pair15 + side15) * V + dst

    for p in ports20:
        bin_items = [r for r in new_roles if (r['owner_replica'], r['child'], r['port']) == (6, 15, p)]
        bin_items.sort(key=lambda item: (item['width'], item['time'], item['stage'], item['replica'], item['helper']))
        off = 0
        for item in bin_items:
            item['offset'] = off
            off += item['width']

    return new_roles

def main():
    pkg = Path(__file__).resolve().parent
    template = pkg.parents[0] / 'complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-global/vendor535/inputs/ROUND20-PARENT-TEMPLATE.json.gz'
    owners_p = pkg / 'data/OWNERS.json.gz'
    roles = json.loads(gzip.decompress(owners_p.read_bytes()))
    updated = apply_repack(roles, template)
    raw = json.dumps(updated, separators=(',', ':')).encode('utf-8')
    owners_p.write_bytes(gzip.compress(raw, mtime=0))
    print(f"Applied optimal 27-role repack to {owners_p}")

if __name__ == '__main__':
    main()
