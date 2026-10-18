"""Exact 9-pair whole-helper exchange on child 15 for gauge44-ends7-t16.

Takes the baseline PR #1104 owner map and executes an exact 9-pair whole-helper
cross-port exchange on child 15 across ports 94..111.

Eliminates all 18 remainder-11 bins into 9 remainder-20 bins and 9 remainder-2 bins,
strictly increasing conditional integer-multiplication kappa from 0.001672691689152441
to 0.001672733678608451 (+4.198945601e-8 gain).

Prepared with autonomous research assistance. Apache-2.0.
"""
import copy
import gzip
import json
from pathlib import Path

# The 9 disjoint pairs (src_port -> dst_port) on child 15:
PAIRS = [
    (94, 103), (95, 104), (96, 105), (97, 106), (98, 107),
    (99, 109), (100, 110), (101, 111), (108, 102)
]

def apply_exchanges(roles, template_path):
    template = json.loads(gzip.decompress(Path(template_path).read_bytes()))
    place = {}
    for e in template['execution_schedule'][:30]:
        if e['kind'] == 'idle_cover_sweep':
            for side, child in enumerate(e['child_indices']):
                place[child] = (e['pair'], side)

    pair15, side15 = place[15]
    V = 112

    new_roles = copy.deepcopy(roles)
    for src, dst in PAIRS:
        w9s = [r for r in new_roles if (r['owner_replica'], r['child'], r['port']) == (6, 15, src) and r['width'] == 9]
        assert len(w9s) == 1, f"Expected 1 width-9 role in (6, 15, {src}), found {len(w9s)}"
        r = w9s[0]
        r['port'] = dst
        r['copy'] = 6 * V + dst
        r['family'] = 6 * (8 * V) + (2 * pair15 + side15) * V + dst

    touched_ports = {p for pair in PAIRS for p in pair}
    for p in touched_ports:
        bin_items = [r for r in new_roles if (r['owner_replica'], r['child'], r['port']) == (6, 15, p)]
        bin_items.sort(key=lambda x: (x['width'], x['time'], x['stage'], x['replica'], x['helper']))
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
    updated = apply_exchanges(roles, template)
    raw = json.dumps(updated, separators=(',', ':')).encode('utf-8')
    owners_p.write_bytes(gzip.compress(raw, mtime=0))
    print(f"Applied 9-pair exchange to {owners_p}")

if __name__ == '__main__':
    main()
