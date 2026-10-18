#!/usr/bin/env python3
"""Reconstruct the literal owner map from pinned PR639 and recorded changes.
Chi Zhao, with substantial OpenAI Codex assistance. Apache-2.0.
No solver, floating objective, or Python assertions are used for admission.
"""
import argparse
from collections import Counter, defaultdict
import copy
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def key(row):
    return row['time'], row['helper']


def validate(rows, template):
    roles = set()
    families = defaultdict(set)
    occupied = defaultdict(set)
    registry = template['provider_registry']
    calls = template['provider_calls']
    for row in rows:
        t, helper = key(row)
        require(isinstance(t, int) and 0 <= t < len(calls), 'invalid time')
        call = calls[t]
        require(call['time'] == t, 'call order mismatch')
        widths = registry[call['provider']]['widths']
        require(isinstance(helper, int) and 0 <= helper < len(widths), 'invalid helper')
        require((t, helper) not in roles, 'duplicate role')
        roles.add((t, helper))
        stage, replica = template['order'][t]
        require((row['stage'], row['replica']) == (stage, replica), 'role chronology mismatch')
        require((call['stage'], call['replica']) == (stage, replica), 'call chronology mismatch')
        owner, child, port = row['owner_replica'], row['child'], row['port']
        require(isinstance(port, int) and 0 <= port < 112, 'invalid port')
        win_key = f'{owner},{child}'
        require(win_key in template['windows'], 'invalid owner window')
        cap, eligible = template['windows'][win_key]
        require(t in eligible, 'time outside owner window')
        require(row['width'] == widths[helper], 'helper width mismatch')
        family = owner * 896 + (2 * template['pairs'][str(child)] + template['sides'][str(child)]) * 112 + port
        require(row['family'] == family and row['copy'] == owner * 112 + port, 'owner identity mismatch')
        require(family not in families[t], 'physical family reused in call')
        families[t].add(family)
        off, width = row['offset'], row['width']
        require(isinstance(off, int) and off >= 0 and off + width <= cap, 'interval exceeds owner')
        cells = set(range(off, off + width))
        index = (owner, child, port)
        require(not occupied[index] & cells, 'overlapping intervals')
        occupied[index].update(cells)
    expected = {(t, h) for t, call in enumerate(calls)
                for h in range(len(registry[call['provider']]['widths']))}
    require(roles == expected, 'missing or extra role')
    idle = Counter()
    for win_key, (cap, _) in template['windows'].items():
        owner, child = map(int, win_key.split(','))
        for port in range(112):
            cells = occupied[owner, child, port]
            require(cells == set(range(len(cells))), 'owner intervals are not compacted')
            if len(cells) < cap:
                idle[cap - len(cells)] += 1
    profile = Counter()
    for call in calls:
        profile.update({int(r): n for r, n in registry[call['provider']]['actual_paid_profile'].items()})
    profile.update(idle)
    require(dict(profile) == {int(r): n for r, n in template['profile'].items()}, 'paid profile mismatch')
    require(sum(r * n for r, n in profile.items()) == template['rank_mass'] == 520704, 'rank mass mismatch')
    require(73 * template['live'] - template['rank_mass'] == template['deficit'] == 2560, 'deficit mismatch')
    return dict(roles=len(roles), idle_profile=dict(sorted(idle.items())),
                profile=dict(sorted(profile.items())), rank_mass=520704,
                dispatch=dict(Counter(c['provider'] for c in calls)))


def negative_controls(rows, template):
    mutations = [('duplicate', lambda r: r.append(copy.deepcopy(r[0]))),
                 ('width', lambda r: r[0].update(width=r[0]['width'] + 1)),
                 ('offset', lambda r: r[0].update(offset=1000)),
                 ('family', lambda r: r[0].update(family=-1))]
    for name, mutate in mutations:
        bad = copy.deepcopy(rows)
        mutate(bad)
        try:
            validate(bad, template)
        except ValueError:
            continue
        raise ValueError(f'negative control unexpectedly accepted: {name}')
    return [name for name, _ in mutations]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-data', type=Path, required=True,
                        help='data directory of exact pinned PR639 package')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--negative-controls', action='store_true')
    args = parser.parse_args()
    source = json.loads((HERE / 'SOURCE.json').read_text())
    base_plan = (args.base_data / 'PLAN.json').read_bytes()
    base_owners = (args.base_data / 'OWNERS.json.gz').read_bytes()
    require(sha(base_plan) == source['base']['plan_sha256'], 'base plan pin mismatch')
    require(sha(base_owners) == source['base']['owners_sha256'], 'base owners pin mismatch')
    moves_data = (HERE / 'OWNER-MOVES.json.gz').read_bytes()
    template_data = (HERE / 'OWNER-TEMPLATE.json').read_bytes()
    require(sha(moves_data) == source['moves_sha256'], 'moves pin mismatch')
    require(sha(template_data) == source['template_sha256'], 'template pin mismatch')
    original = json.loads(gzip.decompress(base_owners))
    rows = {key(row): row for row in original}
    require(len(rows) == len(original) == source['roles'], 'base role inventory mismatch')
    moves = json.loads(gzip.decompress(moves_data))
    require(len(moves) == source['changed_literal_rows'], 'move count mismatch')
    require(len({key(row) for row in moves}) == len(moves), 'duplicate recorded move')
    for row in moves:
        require(key(row) in rows, 'move refers to absent base role')
        rows[key(row)] = row
    rows = [rows[k] for k in sorted(rows)]
    template = json.loads(template_data)
    receipt = validate(rows, template)
    if args.negative_controls:
        receipt['rejected_controls'] = negative_controls(rows, template)
    payload = json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()
    require(sha(payload) == source['target_owners_content_sha256'], 'reconstructed payload mismatch')
    data = gzip.compress(payload, compresslevel=9, mtime=0)
    data = data[:9] + b'\xff' + data[10:]
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'OWNERS.json.gz').write_bytes(data)
    receipt.update(status='PASS_LITERAL_OWNER_EXPORT', owners_sha256=sha(data),
                   owners_content_sha256=sha(payload),
                   published_owners_sha256=source['target_owners_sha256'],
                   scope='Owner structure only; full native supplier and exact assembly replay remain required.')
    (args.out / 'EXPORT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, sort_keys=True))


if __name__ == '__main__':
    main()
