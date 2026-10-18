#!/usr/bin/env python3
"""Offline exact replay; Python 3.10+, standard library. Apache-2.0.
Ross Richardson, with substantial OpenAI Codex assistance.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import model as m


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def one_root():
    """Six labelled signed moves; all 6! orders, no predecessor code."""
    moves = [(j, sign) for j in range(3) for sign in (-1, 1)]
    histogram = Counter()
    records = []
    all_positive = 0
    for word in itertools.permutations(moves):
        q = [0, 0, 0]
        vertices = [tuple(q)]
        for j, sign in word:
            q[j] += sign
            vertices.append(tuple(q))
        differences = {tuple(b[j] - a[j] for j in range(3)) for a in vertices for b in vertices}
        mask = sum((1 << i) for i, row in enumerate(m.TARGET) if row in differences)
        histogram[mask] += 1
        all_positive += (1, 1, 1) in differences
        records.append([list(x) for x in sorted(differences)])
    m.require(sum(histogram.values()) == 720, 'complete six-move census')
    m.require(histogram[7] == 0, 'one-root obstruction')
    m.require(all_positive > 0, 'attainable one-root positive control')
    return {'paths': 720, 'cover_masks': dict(sorted(histogram.items())),
            'all_positive_row_paths': all_positive,
            'ordered_differences_sha256': hashlib.sha256(canonical(records)).hexdigest()}


def coupling_shape(heights, enforce_source=True, enforce_reader=True):
    """Formal two-parameter coefficients, not numerical height samples.

    B means the first then second source call into w. A means the first
    then second output call from z. R advances the prescribed root path.
    Fixed order chooses one sign for each pair; reversing either pair can
    only negate the cross coefficient, so zero is unaffected.
    """
    n = len(heights) - 1
    words = sorted(set(itertools.permutations('BBAA' + 'R' * n)))
    admitted = nonzero = 0
    for word in words:
        stage = bcount = acount = 0
        bheight = aheight = None
        active = 0
        total = [0, 0]
        z_coefficient = [0, 0]
        valid = True
        for event in word:
            h = heights[stage]
            if event == 'R':
                for j in range(2):
                    z_coefficient[j] += (heights[stage+1][j] - h[j]) * active
                stage += 1
            elif event == 'B':
                if bcount == 0:
                    bheight, active = h, 1
                else:
                    if enforce_source and h != bheight:
                        valid = False
                    active = 0
                bcount += 1
            else:
                if acount == 0:
                    aheight = h
                elif enforce_reader and h != aheight:
                    valid = False
                for j in range(2):
                    total[j] += (1 if acount == 0 else -1) * z_coefficient[j]
                acount += 1
        if valid:
            admitted += 1
            nonzero += total != [0, 0]
    return {'event_orders': len(words), 'admitted': admitted, 'nonzero': nonzero}


def short_transfer_lemma():
    z, a, b = (0, 0), (1, 0), (0, 1)
    shapes = [[z], [z, a, z], [z, a, b, z]]
    results = [coupling_shape(shape) for shape in shapes]
    m.require(all(x['nonzero'] == 0 for x in results), 'short-transfer cross coupling')
    four = coupling_shape([z, a, z, a, z])
    m.require(four['nonzero'] > 0, 'four-transfer coupling positive control')
    # Dropping either restoration condition invalidates the zero-coupling lemma.
    bad_source = coupling_shape([z, a, z], enforce_source=False)
    bad_reader = coupling_shape([z, a, z], enforce_reader=False)
    m.require(bad_source['nonzero'] > 0 and bad_reader['nonzero'] > 0, 'hypothesis sensitivity')
    return {'shapes_0_2_3': results, 'four_transfer_positive': four,
            'unrestored_source_negative': bad_source, 'uncancelled_reader_negative': bad_reader}


def controls(word):
    count = 0
    for k in range(len(word)):
        m.require(m.symbolic(word[:k] + word[k+1:]) != m.expected(), 'omission control ' + str(k))
        count += 1
        bad = word[:]
        kind, op, sign, root = bad[k]
        bad[k] = kind, op, -sign, root
        m.require(m.symbolic(bad) != m.expected(), 'sign control ' + str(k))
        count += 1
    for k, event in enumerate(word):
        kind, op, sign, root = event
        if kind == 'R':
            continue
        bad = word[:]
        bad[k] = kind, op, sign, 1-root
        m.require(m.symbolic(bad) != m.expected(), 'port control ' + str(k))
        count += 1
    return count


def result():
    for word in (m.WORD, m.PREDECESSOR):
        m.require(m.symbolic(word) == m.expected(), 'short free map')
        m.require(m.symbolic(word + m.inverse(word)) == m.symbolic([]), 'short inverse')
        expanded = m.expand(word)
        m.require(m.expanded_symbolic(expanded) == m.expanded_expected(), 'expanded free map')
        m.require(m.expanded_symbolic(expanded + m.leaf_inverse(expanded)) == m.expanded_symbolic([]), 'expanded inverse')
    new, old = m.invoice(m.WORD), m.invoice(m.PREDECESSOR)
    delta = [x-y for x, y in zip(new['head_moves_coefficients_L0_through_L4'], old['head_moves_coefficients_L0_through_L4'])]
    m.require(delta == [4, -20, -4, -24, 0], 'paid head-move delta')
    return {'status': 'PASS_SIGNED_CONNECTOR_FOUR_TRANSFERS', 'seed': 32,
            'word': m.WORD, 'predecessor_word': m.PREDECESSOR, 'target': m.TARGET,
            'candidate': new, 'predecessor': old, 'candidate_minus_predecessor_head_polynomial': delta,
            'one_root_census': one_root(), 'short_transfer_lemma': short_transfer_lemma(),
            'semantic_controls': controls(m.WORD),
            'expanded_word': m.expand(m.WORD), 'predecessor_expanded_word': m.expand(m.PREDECESSOR),
            'no_new_kappa': True}


def check_sources():
    source = json.loads((HERE / 'SOURCES.json').read_text())
    for entry in source['retained_files']:
        path = HERE / entry['local']
        m.require(hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256'], 'source pin ' + entry['local'])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--record', action='store_true', help='explicitly regenerate this package certificate')
    ap.add_argument('--search', action='store_true', help='also replay the C++ discovery experiment; needs a C++17 compiler')
    args = ap.parse_args()
    check_sources()
    receipt = result()
    if args.record:
        (HERE / 'CERTIFICATE.json').write_text(json.dumps(receipt, indent=2) + '\n')
    m.require(canonical(receipt) == canonical(json.loads((HERE / 'CERTIFICATE.json').read_text())), 'complete certificate equality')
    p = subprocess.run([sys.executable, '-I', '-O', '-B', str(HERE / 'independent.py')], capture_output=True, text=True)
    m.require(p.returncode == 0, 'independent checker rejected:\n' + p.stdout + p.stderr)
    print(p.stdout.strip())
    if args.search:
        import shutil
        import tempfile
        compiler = shutil.which('clang++') or shutil.which('g++')
        m.require(compiler, 'C++17 compiler unavailable')
        with tempfile.TemporaryDirectory(prefix='connector-search-') as tmp:
            exe = str(Path(tmp) / 'search')
            subprocess.run([compiler, '-std=c++17', '-O3', '-Wall', '-Wextra', '-pedantic', str(HERE / 'search.cpp'), '-o', exe], check=True, timeout=60)
            run = subprocess.run([exe, '5'], check=True, capture_output=True, text=True, timeout=300)
            m.require(run.stderr == (HERE / 'DISCOVERY.txt').read_text(), 'discovery coverage')
            m.require(json.loads(run.stdout) == {'transfers': 4, 'word': [list(x) for x in m.WORD]}, 'discovery witness')
        print('PASS_DISCOVERY_REPLAY complete_through=3 first_four_transfer_witness=1')
    print('PASS_SIGNED_CONNECTOR_FOUR_TRANSFERS queries=12 transfers=4 minimum_one_way=4 factor_calls=300 controls=' + str(receipt['semantic_controls']) + ' no_new_kappa')


if __name__ == '__main__':
    main()
