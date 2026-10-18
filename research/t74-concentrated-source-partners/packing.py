#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Read the exact authenticated PR2673 owner fill and priority order.

No owner, offset or chronology edit is performed here. The changed local words
use a width-preserving compact-helper permutation downstream; verify.py checks
all physical windows, distinct families, capacities and contiguous prefixes.

Credits: Jeremy Kothe / jeremykothe2 (AI assistance), PR2673, for the offset
search and owner fill; themilkman216 / mcorrigan (OpenAI Codex), PR2621, for
priority reordering; Philippe Van Velzen / philippeVV, PR2559, for evacuation;
zxv, PR2530, for source-partner aliases and realization flows. This adapter was
prepared by Mason Hale with OpenAI Codex. Retain all predecessor notices.
"""
import argparse
import json
from pathlib import Path

from common import HERE, check_inputs, read, require

SOURCE = HERE / 'inputs/pr2673'
HEAD = '45aadf0fc7f0dedfb0df959479a20cc1c7be4917'
OFFSETS = (-10, -1, -5, -8, 1, 0, 0, 0, 0)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def generate():
    """Return the complete unchanged PR2673 (fill, order) after source checks."""
    pin = read(HERE / 'PREDECESSORS.json')['hosting_source']
    require(pin['pr'] == 2673 and pin['commit'] == HEAD, 'Wrong hosting predecessor')
    check_inputs()
    fill, order = read(SOURCE / 'FILL.json.gz'), read(SOURCE / 'ORDER.json')
    require(fill['columns'] == ['time', 'helper', 'owner_replica', 'child', 'port', 'offset'], 'Fill columns')
    require(fill['dispatch_overrides'] == [], 'Unexpected dispatch override')
    require(len(fill['rows']) == 281052, 'Role count')
    keys = set()
    for row in fill['rows']:
        require(len(row) == 6 and all(type(x) is int for x in row), 'Noninteger source row')
        key = tuple(row[:2])
        require(key not in keys, 'Duplicate source role')
        keys.add(key)
    require(keys == {(t, h) for t in range(666) for h in range(422)}, 'Complete role inventory')
    require(all(len(c) == 2 and all(type(x) is int for x in c) for c in order), 'Noninteger call')
    expected = sorted([[stage, replica] for stage in range(9) for replica in range(74)],
                      key=lambda c: (8*c[0] + 2*c[1] + OFFSETS[c[0]], c[0], c[1]))
    require(order == expected, 'Exact credited PR2673 priority order')
    require(all([s for s, r in order if r == replica] == list(range(9))
                for replica in range(74)), 'Per-replica stage chronology')
    return fill, order


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    fill, _ = generate()
    args.out.mkdir(parents=True, exist_ok=False)
    for name in ('FILL.json.gz', 'ORDER.json'):
        (args.out / name).write_bytes((SOURCE / name).read_bytes())
    print('PASS_AUTHENTICATED_PR2673_HOSTING_INPUTS', len(fill['rows']),
          'roles, unchanged source fill and order', flush=True)


if __name__ == '__main__':
    main()
