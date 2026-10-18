#!/usr/bin/env python3
"""Exact finite checks of the subset dirt cut; stdlib, no predecessor imports.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
This stage is a partial lemma check, not a forest-optimality certificate.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_bindings():
    package = Path(__file__).resolve().parent
    root = package.parent.parent
    source_file = package / 'SOURCES.json'
    sources = json.loads(source_file.read_text())
    bound = {'SOURCES.json': hashlib.sha256(source_file.read_bytes()).hexdigest()}
    for item in sources['files']:
        if item['usage'] == 'input':
            data = (root / item['path']).read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            require(digest == item['sha256'], 'changed source: ' + item['path'])
            bound[item['path']] = digest
    return bound


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            bit = row.bit_length() - 1
            if bit in pivots:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                break
    return len(pivots)


def span(rows):
    values = {0}
    for row in rows:
        values |= {value ^ row for value in tuple(values)}
    return values


def evaluate(q, word):
    rows = [1 << i for i in range(q)]
    common = [0] * q
    for gate in word:
        if gate[0] == 'P':
            common[gate[1]] ^= 1
        else:
            _, dst, src = gate
            require(dst != src, 'ADD aliases')
            rows[dst] ^= rows[src]
            common[dst] ^= common[src]
    return rows, common


def endpoint(q, word):
    rows, common = evaluate(q, word)
    return rows == [1 << i for i in range(q)] and common == [1] * q


def cut_result():
    domains = []
    for q in range(1, 5):
        invertible = prefix_cuts = crossing_checks = 0
        for matrix in itertools.product(range(1, 1 << q), repeat=q):
            if rank(matrix) != q:
                continue
            invertible += 1
            for subset in range(1, (1 << q) - 1):
                inside = [i for i in range(q) if subset >> i & 1]
                if any(matrix[i] & ~subset for i in inside):
                    continue
                # An invertible full prefix makes these |S| rows independent.
                original_span = span(matrix[i] for i in inside)
                coordinate_span = {v for v in range(1 << q) if not v & ~subset}
                require(original_span == coordinate_span, 'bad cut precondition')
                prefix_cuts += 1
                for dst in inside:
                    for src in range(q):
                        if subset >> src & 1:
                            continue
                        changed = list(matrix)
                        changed[dst] ^= changed[src]
                        require(rank(changed) == q, 'ADD lost full invertibility')
                        require(span(changed[i] for i in inside) != coordinate_span,
                                'one incoming ADD preserved the subset dirt span')
                        crossing_checks += 1
        expected = [1, 6, 168, 20160][q - 1]
        require(invertible == expected, 'incomplete invertible-matrix domain')
        domains.append({'q': q, 'GL_count': invertible,
                        'eligible_prefix_cuts': prefix_cuts,
                        'unique_incoming_checks': crossing_checks})
    return {'status': 'PASS_FINITE_SUBSET_DIRT_CUT', 'source_bindings': source_bindings(),
            'domains': domains, 'scope': 'All invertible binary prefixes q<=4 and all eligible proper nonempty subsets; each unique incoming ADD changes the dirt span. No all-q proof or unrestricted tariff optimum is certified by this finite stage.'}


def control_result(cut_path):
    cut = json.loads(cut_path.read_text())
    require(cut['status'] == 'PASS_FINITE_SUBSET_DIRT_CUT', 'missing positive cut check')
    require(cut['source_bindings'] == source_bindings(), 'stale source cut evidence')
    proper_chain = [('A', 2, 1), ('A', 1, 0), ('P', 0),
                    ('A', 1, 0), ('A', 2, 1)]
    require(endpoint(3, proper_chain), 'child-first echo failed')
    require(evaluate(3, proper_chain + list(reversed(proper_chain))) ==
            ([1, 2, 4], [0, 0, 0]), 'literal inverse failed')
    one_wave = [('P', 0), ('A', 1, 0)]
    require(evaluate(2, one_wave)[1] == [1, 1], 'clean-map control not activating')
    require(not endpoint(2, one_wave), 'clean-only acceptance concealed dirt')
    wrong_order = [('A', 1, 0), ('A', 2, 1), ('P', 0),
                   ('A', 2, 1), ('A', 1, 0)]
    require(evaluate(3, wrong_order)[0] == [1, 2, 4], 'order control not restored')
    require(not endpoint(3, wrong_order), 'wrong preparation order accepted')
    require(not endpoint(3, proper_chain[:-1]), 'omitted return gate accepted')
    singular_prefix = [1, 1]
    require(rank(singular_prefix) < 2, 'singular-prefix control not activating')
    # Outside source lies in S span only after dropping the invertibility premise.
    require(singular_prefix[1] in span([singular_prefix[0]]),
            'noninvertible boundary did not break the necessary premise')
    return {'status': 'PASS_SUBSET_CUT_DEFECT_CONTROLS',
            'cut_sha256': hashlib.sha256(cut_path.read_bytes()).hexdigest(),
            'source_bindings': source_bindings(),
            'positive_controls': ['three-row child-first chain', 'exact literal inverse'],
            'rejected_defects': ['clean common coefficients with unrestored dirt',
                                 'parent-first preparation with restored dirt but wrong common output',
                                 'omitted return ADD', 'singular prefix violates invertibility premise'],
            'scope': 'Finite semantic controls for the partial cut and forest echo; forest-cost optimality remains to be proved and independently checked.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['cut', 'controls'])
    parser.add_argument('--cut-input', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    require(not args.output.exists(), 'output already exists; evidence is immutable')
    if args.stage == 'cut':
        result = cut_result()
    else:
        require(args.cut_input is not None, 'controls need the completed cut boundary')
        result = control_result(args.cut_input)
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(result['status'])


if __name__ == '__main__':
    main()
