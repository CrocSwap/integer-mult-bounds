# SPDX-License-Identifier: Apache-2.0
"""Check a joint cheap-edge obstruction for the named P104 423 profile."""

import argparse
import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BUDGET = 232
BROAD = 191
GEOMETRY = 'research/p104-endpoint-saturation/geometry.py'
WORD = 'research/p104-native-channel/inputs/LOWRANK-WITNESS.json'
FIXTURE = 'research/p104-native-channel/inputs/P104-FIXTURE.json'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    result = dict(pairs)
    require(len(result) == len(pairs), 'duplicate JSON key')
    return result


def read_json(path):
    require(path.stat().st_size <= 2_000_000, 'JSON size bound')
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


class AuthenticatedLoader(importlib.machinery.SourceFileLoader):
    """Compile only the already authenticated source, never a bytecode cache."""

    def __init__(self, raw):
        super().__init__('p104_pinned_geometry', str(ROOT / GEOMETRY))
        self.raw = raw

    def get_code(self, fullname):
        require(fullname == self.name, 'fixed geometry module')
        return self.source_to_code(self.raw, self.path)


def load_geometry(raw):
    loader = AuthenticatedLoader(raw)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module.__dict__


def inputs():
    manifest = read_json(PACKAGE / 'SOURCES.json')
    records = manifest['files']
    require(len(records) <= 8, 'source record bound')
    data = {}
    for row in records:
        if row['usage'] != 'input':
            continue
        name = row['path']
        require(name in {GEOMETRY, WORD, FIXTURE} and name not in data,
                'exact input inventory')
        path = ROOT / name
        require(path.stat().st_size <= 2_000_000, 'source size bound')
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'input SHA256')
        data[name] = raw
    require(set(data) == {GEOMETRY, WORD, FIXTURE}, 'three authenticated inputs')
    return (load_geometry(data[GEOMETRY]), json.loads(data[WORD], object_pairs_hook=unique),
            json.loads(data[FIXTURE], object_pairs_hook=unique))


def classes(endpoints):
    require(len(endpoints) == 104, '104 endpoints')
    require(all(24 <= b < d <= 2 * b <= 60 for d, b in endpoints),
            'proper capacity domain')
    groups = [[i for i, pair in enumerate(endpoints) if pair == (36, 24)],
              [i for i, pair in enumerate(endpoints) if pair == (45, 30)]]
    groups.append([i for i in range(104) if i not in groups[0] + groups[1]])
    require([len(g) for g in groups] == [12, 8, 84], 'three endpoint classes')
    require(all(endpoints[i][0] - endpoints[i][1] >= 16 for i in groups[2]),
            'R gap at least sixteen')
    return groups


def degree_facts(arrival, departure, ag, dg):
    require(len(arrival) == len(departure) == 104, 'incidence dimensions')
    mutual = {(s, t) for s in range(104) for t in departure[s] if s in arrival[t]}
    pp_row = max(sum((s, t) in mutual for t in ag[0]) for s in dg[0])
    pp_column = max(sum((s, t) in mutual for s in dg[0]) for t in ag[0])
    qp_row = max(sum((s, t) in mutual for t in ag[0]) for s in dg[1])
    pq_column = max(sum((s, t) in mutual for s in dg[0]) for t in ag[1])
    qq = sum((s, t) in mutual for s in dg[1] for t in ag[1])
    require(pp_row <= 4 and pp_column <= 4, 'P-P degree at most four')
    require(qp_row <= 6 and pq_column <= 6, 'Q-P degree at most six per Q')
    require(qq == 0, 'no Q-Q mutual residual edges')
    return {'mutual_edges': len(mutual), 'pp_row_max': pp_row,
            'pp_column_max': pp_column, 'qp_row_max': qp_row,
            'pq_column_max': pq_column, 'qq_edges': qq}


def reconstruct():
    module, word, fixture = inputs()
    paths = module['paths'](word)
    ports = module['ports'](fixture)
    (arrival, normals), (departure, labels) = module['endpoint_data'](paths, ports)
    ae = module['census'](arrival, normals)
    de = module['census'](departure, labels)
    ag, dg = classes(ae), classes(de)
    a = [{s for s in range(104) if labels[s] in row} for row in arrival]
    d = [{t for t in range(104) if normals[t] in row} for row in departure]
    facts = degree_facts(a, d, ag, dg)
    require(facts['mutual_edges'] == 4368, 'literal mutual incidence census')
    encoded = json.dumps([list(map(sorted, a)), list(map(sorted, d))],
                         separators=(',', ':')).encode()
    return {'arrival_endpoints': [list(row) for row in ae],
            'departure_endpoints': [list(row) for row in de],
            'arrival_classes': ag, 'departure_classes': dg,
            'incidence_sha256': hashlib.sha256(encoded).hexdigest(), **facts}


def states():
    """Overapproximate endpoint counts with seventeen missing broad slots."""
    result = []
    deficit = 2 * 104 - BROAD
    require(deficit == 17, 'named broad count')
    for z in range(deficit // 2 + 1):
        for p in range(13):
            for q in range(9):
                r = deficit - z - p - q
                if not 0 <= r <= 84 or z > p + q + r:
                    continue
                lower = 12 * p + 15 * q + 16 * r + 24 * z
                if lower <= BUDGET:
                    result.append([p, q, r, z, lower])
    require(len(result) == 34, 'complete relaxed state count')
    return result


def overlap_cap(left, right, pp=4, qp=6):
    p, q, r, _, _ = left
    a, b, c, _, _ = right
    return ((p + q + r) * c + (a + b + c) * r - r * c
            + pp * min(p, a) + qp * (q + b))


def joint_certificate(candidates):
    require(len(candidates) == 34, 'bounded pair census')
    minimum, witness = 10_000, None
    for left in candidates:
        for right in candidates:
            overlap = overlap_cap(left, right)
            lower = left[4] + right[4] - overlap
            if lower < minimum:
                minimum = lower
                witness = {'departure': left, 'arrival': right, 'overlap_cap': overlap}
    require(minimum == 235 and minimum > BUDGET, 'joint cheap union contradiction')
    return {'states': candidates, 'pairs_checked': len(candidates) ** 2,
            'minimum_conditional_union_bound': minimum,
            'cheap_budget': BUDGET, 'contradiction': minimum - BUDGET,
            'attaining_relaxed_pair': witness}


def calculate():
    return {'geometry': reconstruct(), 'certificate': joint_certificate(states()),
            'profile': {'cheap': BUDGET, 'unit': 180, 'skip_dimension_three': 11},
            'scope': 'Reject named profile in frozen X-only monotone model; no supplier or kappa'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    result = calculate()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        require(json.dumps(result, sort_keys=True) == json.dumps(
            read_json(PACKAGE / 'RESULT.json'), sort_keys=True), 'typed receipt equality')
        print('PASS_P104_JOINT_ENDPOINT cheap=232 broad=191 bound=235 states=34 pairs=1156')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(f'FAIL_P104_JOINT_ENDPOINT: {error}') from error
