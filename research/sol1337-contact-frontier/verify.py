#!/usr/bin/env python3
"""Exact scoped retained-center chart obstruction. Apache-2.0.

Substantial OpenAI Codex assistance. This checks a changed contact model,
not native phases, a completed supplier or an outer multiplication theorem.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def prefixes(delta):
    return [sum(delta[r] * min(r, j) for r in range(1, 10)) for j in range(1, 10)]


def class_proof(receipt, expected_cases):
    classes = receipt['rank_delta_classes']
    need(sum(c['count'] for c in classes) == expected_cases, 'complete neighbor count')
    target = [0, 1, 0, 0, 0, 0, 0, 1, -1, 0]
    floor = prefixes(target)
    for c in classes:
        need(len(c['delta']) == 10 and c['count'] > 0, 'rank delta class')
        need(all(a >= b for a, b in zip(prefixes(c['delta']), floor)),
             'exact concave majorization of 1+7^theta-8^theta')
    # The zero-rank event count is bookkeeping and has zero paid moment.
    need(any(c['delta'][1:] == target[1:] for c in classes), 'attaining positive-loss delta')


def cut_proof(receipt):
    rows = receipt['cases']
    need(len(rows) == 1022 * 9, 'all 1022 coherent alternatives and nine prefixes')
    by_axis = {}
    for frame, axis, prefix, value, selected, unique in rows:
        need(frame == 0 and 1 <= prefix <= 9, 'one coherent identical-chart group')
        need(value == selected == 0, 'empty cut is an attaining nonnegative optimum')
        need((axis, prefix) not in by_axis, 'unique cut record')
        by_axis[axis, prefix] = unique
    axes = {axis for axis, _ in by_axis}
    need(len(axes) == 1022, 'complete coherent chart-neighbor set')
    need(all(by_axis[axis, j] in (0, 1) for axis in axes for j in range(1, 10)),
         'every integer prefix covered')
    need(all(by_axis[axis, 1] == 1 for axis in axes),
         'unique empty first-prefix minimum makes every nonempty subset strict')


def run():
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    root = HERE.parent.parent
    for row in sources['files']:
        if row['usage'] == 'input':
            need(sha256((root / row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'exact retained source: ' + row['path'])
    spec = importlib.util.spec_from_file_location('changed_center_graph', HERE / 'build_graph.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix='sol1337-contact-replay-') as tmp:
        output = Path(tmp)
        metadata = module.build(output)
        need(metadata['inputs'] == 640 and metadata['independent_center_reward'] == 0,
             'all arbitrary inputs and no false center productive credit')
        need(metadata['newly_variable_center_contacts'] == 184, 'changed owned-contact restriction')
        need(metadata['paid'] == {1:2201,2:412,3:510,4:127,5:40,8:8}, 'complete baseline invoice')
        need(metadata['helpers'] == {4:28,7:7,8:47,9:326}, 'all 408 independent helpers')
        full_meta = json.loads((output / 'graph-metadata.json').read_text())
        labels = full_meta['labels']
        selected = set(full_meta['selected'])
        need(all(labels[n][0] == 'contact' and any(r >= 632 for r in labels[n][2])
                 for n in selected), 'only formerly owned center contacts are variable')
        need(all(n not in selected for n, label in enumerate(labels)
                 if label[0] in ('entry', 'exit')), 'all 640 physical endpoint charts frozen')
        receipts = {}
        for stem, expected in [('scan_centers', 'single-contact-screen.json'),
                               ('scan_pairs', 'paired-contact-screen.json'),
                               ('scan_block_prefix', 'coherent-prefix-screen.json')]:
            binary = output / stem
            subprocess.run(['c++','-O2','-std=c++20',str(HERE / 'tools' / (stem + '.cpp')),
                            '-o',str(binary)], check=True, timeout=60, capture_output=True)
            path = output / expected
            subprocess.run([str(binary),str(output / 'center-contact-graph.txt'),str(path)],
                           check=True, timeout=60, capture_output=True)
            actual = json.loads(path.read_text())
            frozen = json.loads((HERE / expected).read_text())
            if stem == 'scan_block_prefix':
                need(actual['cases'] == frozen['cases'], 'all exact integer cut certificates regenerated')
                cut_proof(actual)
            else:
                need(actual['cases'] == frozen['cases'] and
                     actual['rank_delta_classes'] == frozen['rank_delta_classes'],
                     'all actual binary ranks and full delta classes regenerated')
                class_proof(actual,188048 if stem == 'scan_centers' else 1834488)
            receipts[stem] = actual
        controls = 0
        bad = dict(receipts['scan_centers'])
        bad['rank_delta_classes'] = [{'count':188048,'delta':[0,-1,0,0,0,0,0,0,0,0]}]
        try:
            class_proof(bad,188048)
        except ValueError:
            controls += 1
        bad = json.loads(json.dumps(receipts['scan_block_prefix']))
        bad['cases'][0][3] = -1
        try:
            cut_proof(bad)
        except ValueError:
            controls += 1
        bad = json.loads(json.dumps(receipts['scan_block_prefix']))
        bad['cases'][0][5] = 0
        try:
            cut_proof(bad)
        except ValueError:
            controls += 1
        need(controls == 3, 'negative paid delta, bad cut and false strictness reject')
        print(json.dumps(dict(status='PASS_RETAINED_CENTER_COHERENT_CHART_CEILING',
                              inputs=640,independent_helpers=408,independent_center_reward=0,
                              variable_contacts=184,single_cases=188048,paired_cases=1834488,
                              coherent_group_contacts=176,integer_prefix_cuts=9198,
                              single_pair_minimum='1+7^theta-8^theta',
                              nonempty_coherent_loss_lower_bound='2-2^theta',
                              strict_domain='0<theta<1',rejection_controls=controls,
                              new_kappa=None), sort_keys=True))


if __name__ == '__main__':
    run()
