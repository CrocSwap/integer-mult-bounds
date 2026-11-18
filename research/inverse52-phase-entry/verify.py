"""Check the complete phase-entry interface. Ali Romman, with Codex. Apache-2.0."""

from collections import Counter
from hashlib import sha1, sha256
import importlib.util
from itertools import product
import json
from pathlib import Path
import subprocess
import sys

from interface import PHASES, describe, prefix, weights

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sources():
    pins = json.loads((ROOT / 'SOURCE-PINS.json').read_text())
    require(len(pins) == 29, 'source count')
    for pin in pins:
        raw = (ROOT / pin['retained_path']).read_bytes()
        require(sha256(raw).hexdigest() == pin['sha256'], 'source digest')
        require(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
                == pin['git_blob'], 'source Git blob')
    domain = load('inverse6096', 'retained/inverse-domain/verify.py')
    columns = json.loads((ROOT / 'retained/NORMALIZERS.json').read_text())['mode_columns']
    manifest = json.loads((ROOT / 'retained/inverse-domain/SOURCES.json').read_text())
    original = next(row for row in manifest['files'] if row['path'].endswith('/NORMALIZERS.json'))
    domain.authenticate((ROOT / 'retained/NORMALIZERS.json').read_bytes(), original)
    groups = domain.verify_basis(columns)
    for a, b in product(range(52), repeat=2):
        owner = domain.owner_for_pair(a, b, columns, groups)
        require(max(map(abs, owner)) <= 1, 'actual bounded owner witness')
        require(tuple(sum(x * y for x, y in zip(col, owner, strict=True)) % 52
                      for col in columns[:2]) == (a, b), 'actual residue pair')
    require((columns[0][0], columns[1][0]) == (1, 1), 'minimal source witness')
    return load('graph6072', 'retained/runtime-core/retained/paired-residue-sampler/verify.py')


def backend_inventory(graph):
    lookup, tables = {}, {}
    mask = (1 << 156) - 1
    for c, d in product(range(1, 13), repeat=2):
        _, counts, table, _ = graph.make(c, d)
        states = [(phase, node) for phase, count in enumerate(counts) for node in range(count)]
        starts = []
        words = [0] * 4
        cursor = 0
        for count in counts:
            starts.append(cursor)
            emitted = Counter(target - 312 for row in table[cursor:cursor + count]
                              for target in row if target >= 312)
            require(all(value == 1 for value in emitted.values()), 'one leaf per digit')
            words = [(word << 1) | emitted.get(i, 0) for i, word in enumerate(words)]
            cursor += count
        for phase in range(156):
            divisions = [divmod(word * 169, mask) for word in words]
            require(all(remainder == 0 for _, remainder in divisions), 'periodic digit rational')
            residues = tuple(value for value, _ in divisions)
            require(residues not in lookup, 'distinct backend phase signatures')
            require(sum(residues) == 169 * counts[phase], 'complete live pool')
            lookup[residues] = (c, d, PHASES[phase], phase)
            words = [((word << 1) & mask) | (word >> 155) for word in words]
        tables[c, d] = counts, table, states, starts
    require(len(lookup) == 22464, 'complete backend inventory')
    return lookup, tables


def prefix_check(a, b, description):
    records = [(coins, prefix(a, b, coins)) for coins in product((0, 1), repeat=4)]
    completed = Counter(row['label'] for _, row in records if row['label'] is not None)
    survivors = [(coins, row['node']) for coins, row in records if row['label'] is None]
    require([completed[i] for i in range(4)] == [16 * value // 2704 for value in weights(a, b)],
            'complete four-coin outcome counts')
    require([node for _, node in survivors] == list(range(description['roots'])),
            'complete ordered entry nodes')
    parents = sorted({coins[:3] for coins, row in records if row['used'] == 4})
    original = weights(a, b)
    warm_count = 8 - sum(8 * value // 2704 for value in original)
    require(len(parents) == warm_count, 'third-depth live count')
    digit_count = 2 * warm_count - description['roots']
    for coins, node in survivors:
        child = node + digit_count
        require(child % 2 == coins[3] and child // 2 == parents.index(coins[:3]),
                'entry-specific inverse')
    return len(survivors)


def tail_check(a, b, description, tables):
    c, d, offset = description['c'], description['d'], description['phase_index']
    counts, table, states, starts = tables[c, d]
    original = weights(a, b)
    powers = 16
    checked = 0
    for step in range(156):
        phase = (offset + step) % 156
        live = powers - sum(powers * value // 2704 for value in original)
        require(live == counts[phase], 'tail live pool')
        leaves = [i for i, value in enumerate(original)
                  if 2 * powers * value // 2704 - 2 * (powers * value // 2704)]
        for node in range(live):
            for coin in (0, 1):
                child = 2 * node + coin
                target = table[starts[phase] + node][coin]
                if child < len(leaves):
                    require(target == 312 + leaves[child], 'ordered tail label')
                else:
                    require(target < 312 and states[target] ==
                            ((phase + 1) % 156, child - len(leaves)), 'tail continuation')
                checked += 1
        powers *= 2
    require(checked == 624, 'complete shifted tail period')
    return checked


def collision_check(tables):
    description = describe(1, 1)
    require(description['phase'] == 120 and description['c'] == description['d'] == 10,
            'literal source entry')
    counts, table, states, starts = tables[10, 10]
    previous = PHASES.index(60)
    require(counts[previous] == 2, 'cyclic predecessor pool')
    target = table[starts[previous] + 1][1]
    require(target < 312 and states[target] == (description['phase_index'], 0), 'cyclic edge')
    require(prefix(1, 1, (1, 1, 1, 1)) == dict(label=None, node=0, used=4), 'warm entry edge')
    first = dict(mode='prefix', phase=8, node=0, coin=1)
    cyclic = dict(mode='tail', phase=60, node=1, coin=1)
    after = dict(phase=120, node=0, coin=1, done=False)
    require((first['phase'], first['node']) != (cyclic['phase'], cyclic['node']),
            'distinct physical packet values')
    require(tuple(value % 169 for value in weights(1, 1)) != (9, 30, 30, 100),
            'false phase-one reset control')
    return dict(original_pair=[1, 1], core_pair=[10, 10], first=first, cyclic=cyclic,
                common_output=after, retained_original_parameters=True,
                scope='Two autonomous transition modes cannot merge these packets with zero workspace. A separate boundary protocol can distinguish them.')


def collect():
    graph = sources()
    lookup, tables = backend_inventory(graph)
    rows, counts, roots, offsets = [], Counter(), Counter(), Counter()
    tail_edges = entry_nodes = 0
    for a, b in product(range(52), repeat=2):
        row = describe(a, b)
        actual = lookup.get(tuple(row['tail']))
        if row['kind'] == 'core':
            require(actual == (row['c'], row['d'], row['phase'], row['phase_index']),
                    'formula and exhaustive backend lookup')
            require(row['phase_index'] % 12 == 4, 'phase offset class')
            tail_edges += tail_check(a, b, row, tables)
            offsets[row['phase_index']] += 1
        else:
            require(actual is None, 'false existing-core embedding')
        number = prefix_check(a, b, row)
        entry_nodes += number if row['kind'] == 'core' else 0
        counts[row['kind']] += 1
        roots[row['roots']] += 1
        rows.append(row)
    for bad in [(-1, 0), (52, 0), (1, 52), (True, 1)]:
        try:
            describe(*bad)
        except ValueError:
            continue
        raise ValueError('invalid residue accepted')
    require(counts == {'core': 2304, 'endpoint': 96, 'mixed': 288, 'dyadic': 16},
            'complete interface classes')
    require((tail_edges, entry_nodes) == (1437696, 4428), 'complete edge and entry coverage')
    mode = ['-O'] if sys.flags.optimize else []
    replay = subprocess.run([sys.executable, '-W', 'error', *mode, '-B',
                             str(ROOT / 'retained/runtime-core/verify.py')],
                            check=True, capture_output=True, text=True, timeout=60)
    require('PASS_RUNTIME_PAIRED_DDG_ARITHMETIC' in replay.stdout, 'unchanged circuit replay')
    return dict(schema_version=1, actual_residue_pairs=2704, bounded_owner_witnesses=2704,
                backend_phase_signatures=len(lookup), classifications=dict(sorted(counts.items())),
                distinct_core_entries=len({(row['c'], row['d'], row['phase']) for row in rows
                                           if row['kind'] == 'core'}),
                root_counts={str(k): v for k, v in sorted(roots.items())},
                phase_offsets={str(k): v for k, v in sorted(offsets.items())},
                literal_four_coin_prefixes=2704 * 16, tail_edges=tail_edges,
                core_entry_inverse_checks=entry_nodes, collision=collision_check(tables),
                source_receipt=replay.stdout.strip().splitlines(), pairs=rows)


def main():
    result = collect()
    require(result == json.loads((ROOT / 'RESULT.json').read_text()), 'interface certificate')
    print('PASS_INVERSE52_PHASE_ENTRY')
    print('2704 actual pairs; 2304 pairs with a unique core entry; 96 endpoint tails; 288 mixed tails; 16 dyadic pairs')
    print(f"22464 backend phase signatures; 43264 literal prefixes; {result['tail_edges']} tail edges")
    print(f"{result['core_entry_inverse_checks']} entry inverse checks; explicit first-entry/period-return collision")


if __name__ == '__main__':
    main()
