#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Optional comparison with a local, hash-pinned checkout of PR #2828.

The independent verifier never imports the reference. This adapter executes it
only after checking every external file recorded in SOURCES.json.
"""
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

import gaps as G
import profiles as P
from verify import HERE, profile_digest, require


def import_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(root):
    source = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))['audited_reference']
    for name, expected in source['sha256'].items():
        require(sha256((root / name).read_bytes()).hexdigest() == expected,
                'reference source mismatch: ' + name)
    directory = root / 'research/ut4-fifteen-call-five-b'
    census = import_file('pinned_five_b_reference', directory / 'census.py')
    predecessor, _ = census.load()
    independent = json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8'))

    tables = census.build_three_role_tables(predecessor, tuple(P.RANK))
    for case, (_, _, at, ct, joint) in tables.items():
        def single_rows(table):
            return sorted([k, s, w, used, count]
                          for k, values in table.items() for s, terms in values.items()
                          for w, used, count in terms)
        joint_rows = sorted([*state, q, count]
                            for state, terms in joint.items() for q, count in terms)
        actual = {
            'a_single_sha256': sha256(G.canonical(single_rows(at))).hexdigest(),
            'c_single_sha256': sha256(G.canonical(single_rows(ct))).hexdigest(),
            'joint_sha256': sha256(G.canonical(joint_rows)).hexdigest(),
            'joint_states': len(joint_rows),
            'joint_words': sum(row[-1] for row in joint_rows),
        }
        require(actual == independent['gap_tables'][case], 'gap table mismatch: ' + case)

    # Observe every original active-profile pair, without replacing its search.
    # Other splits are also visited: retain the rank<=5 subdomain and deduplicate.
    observed = set()
    original = census.eval_base_2role

    def observe(predecessor, middle, a_gaps, c_gaps):
        def prefix(increments):
            result, running = [], 0
            for value in increments[:5]:
                running ^= value
                result.append(running)
            return tuple(result)
        if sum(P.RANK[x] for x in a_gaps) <= 5 and sum(P.RANK[x] for x in c_gaps) <= 5:
            observed.add((tuple(middle), prefix(a_gaps), prefix(c_gaps)))
        return original(predecessor, middle, a_gaps, c_gaps)

    census.eval_base_2role = observe
    replay = census.run(predecessor)
    expected = json.loads((directory / 'RESULT.json').read_text(encoding='utf-8'))
    # The adapter must not change any field returned by the original census.
    for field, value in json.loads(json.dumps(replay)).items():
        require(value == expected[field], 'reference census drift: ' + field)
    require(len(observed) == 5664, 'reference profile-set size')
    require(profile_digest(observed) == independent['profile_set_sha256'],
            'reference profile-set mismatch')
    for field, value in independent['statistics'].items():
        require(value == replay['domains']['5,5,5'][field], 'reference count: ' + field)
    print('PASS_PINNED_PR2828_COMPARISON profile_set=' + profile_digest(observed) +
          ' orientations=2 gap_words_each=2798629')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reference_root', type=Path, help='root of an exact PR2828 checkout/export')
    run(parser.parse_args().reference_root.resolve())
