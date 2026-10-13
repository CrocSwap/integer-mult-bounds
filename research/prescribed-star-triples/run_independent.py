#!/usr/bin/env python3
"""Exhaustive 8-label decoder search, independent of four-block optimization.

By default compare the computed result with INDEPENDENT.json, without writing
into the source directory. --output writes a new receipt and refuses overwrite.
Only the Python standard library and a C++17 compiler (CXX, default c++) are used.
Prepared for DLamdata with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import collections
import itertools
import json
import os
import pathlib
import shlex
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def edges(p):
    return [(u, v) for u in range(2*p) for v in range(u+1, 2*p)
            if u//2 != v//2]


def canonical(targets):
    """Minimize first-occurrence pair/sign renaming over all edge presentations."""
    best = None
    for order in itertools.permutations(targets):
        for reverse in itertools.product(range(2), repeat=3):
            pairs, flat = {}, []
            for (a, b), flip in zip(order, reverse):
                for v in ((b, a) if flip else (a, b)):
                    pair, sign = divmod(v, 2)
                    if pair not in pairs:
                        pairs[pair] = (len(pairs), sign)
                    index, first_sign = pairs[pair]
                    flat.append(2*index + (sign ^ first_sign))
            candidate = tuple(flat)
            if best is None or candidate < best:
                best = candidate
    return tuple(zip(best[::2], best[1::2]))


def orbits(p):
    counts = collections.Counter(canonical(t)
                                 for t in itertools.combinations(edges(p), 3))
    return sorted(counts.items())


def basis(rows):
    pivots = {}
    for row in rows:
        while row:
            index = row.bit_length() - 1
            if index not in pivots:
                pivots[index] = row
                break
            row ^= pivots[index]
    return pivots


def contains(pivots, row):
    while row:
        index = row.bit_length() - 1
        if index not in pivots:
            return False
        row ^= pivots[index]
    return True


def direct_decodes(p, targets, deleted, constant=False):
    """Literal incidence-row Gaussian elimination, with unrestricted survivors."""
    surviving = [e for e in edges(p) if e not in deleted]
    if any(e not in surviving for e in targets):
        return False
    rows = [sum(1 << j for j, e in enumerate(surviving) if v in e)
            for v in range(2*p)]
    if constant:
        rows.append((1 << len(surviving)) - 1)
    pivots = basis(rows)
    return all(contains(pivots, 1 << surviving.index(e)) for e in targets)


def exhaustive_deletions(p, targets, constant=False):
    other = [e for e in edges(p) if e not in targets]
    for count in range(len(other) + 1):
        for deleted in itertools.combinations(other, count):
            if direct_decodes(p, targets, set(deleted), constant):
                return count
    return None


def label_witness_valid(p, targets, labels, deleted):
    """Validate the supplied three coefficient rows, including their target rank."""
    if len(labels) != 2*p or any(x not in range(8) for x in labels):
        return False
    if not all(labels[u] ^ labels[v] == 1 << j
               for j, (u, v) in enumerate(targets)):
        return False
    return all(e in targets or e in deleted or labels[e[0]] == labels[e[1]]
               for e in edges(p))


def scan(binary, p, representatives):
    data = f'{p} {len(representatives)}\n' + ''.join(
        ' '.join(str(v) for e in t for v in e) + '\n'
        for t, _ in representatives)
    process = subprocess.run([str(binary)], input=data, text=True,
                             capture_output=True, check=True)
    lines = process.stdout.splitlines()
    require(len(lines) == len(representatives), 'C++ output coverage mismatch')
    records, restore_checks = [], 0
    for line, (targets, multiplicity) in zip(lines, representatives):
        values = list(map(int, line.split()))
        require(len(values) >= 4, 'Truncated C++ result')
        pp, index, optimum, count, *labels = values
        require(pp == p and index == len(records), 'C++ result index mismatch')
        record = {'targets': targets, 'orbit_size': multiplicity,
                  'deletions': None if optimum < 0 else optimum,
                  'assignments': count}
        if optimum >= 0:
            deleted = [e for e in edges(p)
                       if e not in targets and labels[e[0]] != labels[e[1]]]
            require(len(deleted) == optimum, 'Witness deletion count mismatch')
            require(count == 8**(2*p-4), 'Incomplete label enumeration')
            require(label_witness_valid(p, targets, labels, set(deleted)),
                    'Invalid normalized decoder witness')
            require(direct_decodes(p, targets, set(deleted)),
                    'Direct binary rowspace rejects witness')
            # Rank-bad coefficient rows must not pass the witness validator.
            require(not label_witness_valid(p, targets, [0]*(2*p), set(deleted)),
                    'Rank-zero decoder control was accepted')
            # Restoring any one deleted port drops below the proved optimum.
            for edge in deleted:
                require(not direct_decodes(p, targets, set(deleted) - {edge}),
                        'One fewer deletion still decodes')
                restore_checks += 1
            record.update(labels=labels, deleted=deleted)
        else:
            require(optimum == -1 and count == 0 and not labels,
                    'Malformed infeasible result')
            require(not direct_decodes(p, targets, set(edges(p))-set(targets)),
                    'Impossible target set decodes when isolated')
        records.append(record)
    return {'p': p, 'orbits': len(representatives),
            'target_triples': sum(n for _, n in representatives),
            'restored_port_negative_controls': restore_checks,
            'records': records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--p', nargs='+', type=int, default=[2, 3, 4, 5, 6])
    destination = parser.add_mutually_exclusive_group()
    destination.add_argument('--check', type=pathlib.Path, default=None,
                             help='Compare with this receipt (default INDEPENDENT.json)')
    destination.add_argument('--output', type=pathlib.Path,
                             help='Write a new receipt; refuse to overwrite')
    args = parser.parse_args()
    require(args.p == sorted(set(args.p)) and all(2 <= p <= 6 for p in args.p),
            '--p must be distinct increasing integers in 2..6')
    if args.output:
        require(not args.output.exists(), 'Refusing to overwrite output receipt')
    compiler = shlex.split(os.environ.get('CXX', 'c++'))
    require(bool(compiler), 'CXX must name a compiler')
    result = {
        'schema': 1,
        'method': 'All normalized F2^3 vertex labels with three fixed unit target differences; no four-block restriction',
        'cases': [],
    }
    with tempfile.TemporaryDirectory(prefix='prescribed-star-independent-') as scratch:
        binary = pathlib.Path(scratch) / 'label_scan'
        subprocess.run(compiler + ['-O3', '-std=c++17', str(HERE/'label_scan.cpp'),
                                   '-o', str(binary)], check=True)
        for p in args.p:
            case = scan(binary, p, orbits(p))
            result['cases'].append(case)
            histogram = collections.Counter(str(r['deletions']) for r in case['records'])
            print(f'p={p}: {case["orbits"]} orbits, {case["target_triples"]} triples; '
                  f'orbit budgets {dict(histogram)}', flush=True)
    # Separate brute-force deletion masks, covering every p=2 and p=3 target set.
    direct_checks = {}
    for case in result['cases']:
        p = case['p']
        if p > 3:
            continue
        lookup = {tuple(tuple(e) for e in r['targets']): r['deletions']
                  for r in case['records']}
        count = 0
        for targets in itertools.combinations(edges(p), 3):
            require(exhaustive_deletions(p, targets) == lookup[canonical(targets)],
                    'Deletion-mask search disagrees with 8-label optimizer')
            count += 1
        direct_checks[str(p)] = count
    result['all_target_direct_deletion_checks'] = direct_checks
    triangle = ((0, 2), (0, 4), (2, 4))
    no_global = exhaustive_deletions(3, triangle)
    global_sum = exhaustive_deletions(3, triangle, True)
    require(no_global is None and global_sum == 5, 'Constant-row control failed')
    result['constant_row_control'] = {
        'p': 3, 'targets': triangle, 'nonempty_only': no_global,
        'empty_star_allowed': global_sum,
    }
    encoded = json.dumps(result, indent=2) + '\n'
    if args.output:
        with args.output.open('x') as out:
            out.write(encoded)
        print(f'Wrote {args.output}')
    else:
        receipt = args.check or HERE/'INDEPENDENT.json'
        require(json.loads(receipt.read_text()) == json.loads(encoded),
                f'Computed evidence differs from {receipt}')
        print(f'Checked {receipt.name}')
    print('PASS: complete coefficient enumeration, direct rowspaces, deletion masks, '
          'rank-zero and restored-port controls, empty-star distinction.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        sys.exit(1)
