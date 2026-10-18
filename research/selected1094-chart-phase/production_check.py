#!/usr/bin/env python3
"""Exercise the pinned controller's existing chart protection in isolation.

This executes two verbatim function ASTs and the verbatim chart-table equality
assertion, not the whole admission driver. Its other top-level obligations are
inherited. The independent mathematical verifier imports none of this code.
Gareth Davidson, with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import ast
from collections import Counter, defaultdict
import copy
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from algebra import canonical, convolution, digest, rebased, require
from verify import inputs, load_bytes, read

SOURCE = 'research/gauge44-slots-t16/code/audit_allcold.py'
KERNEL_SOURCE = 'research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-global/vendor531/vendor/clifford/clifford_exact.py'


def check(root):
    data, _ = inputs(root)  # Pins are checked before compiling source code.
    text = (root / SOURCE).read_text()
    tree = ast.parse(text, filename=SOURCE)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('orthobasis', 'audit')]
    require({n.name for n in functions} == {'orthobasis', 'audit'}, 'source functions')
    predicates = []
    for n in tree.body:
        if isinstance(n, ast.Assert) and isinstance(n.test, ast.Compare):
            left = n.test.left
            if (isinstance(left, ast.Subscript) and isinstance(left.value, ast.Name)
                    and left.value.id == 'r' and isinstance(left.slice, ast.Constant)
                    and left.slice.value == 'sigmas'):
                predicates.append(n)
    require(len(predicates) == 1, 'source chart equality predicate')
    template, word = data['template'], data['word']
    reg = template['local_providers']
    ns = dict(json=json, hashlib=hashlib, copy=copy, Counter=Counter, defaultdict=defaultdict,
              canon=word, parent=data['parent'], ph=data['phases'], registry=reg,
              providers={'gauge44': {'widths': reg['gauge44']['widths'], 'checks': data['checks']}},
              DATA=template['live'], PHYSICAL=template['physical'], V=word['v'],
              R=word['R'], N=2*word['v']+word['R'], CENTRES=len(word['centers']),
              M=73, T=16, HOSTED=144*word['R'], expected_provider=lambda stage, replica: 'gauge44',
              prank={entry['child']: entry['rank'] for entry in data['parent']['idle_children']},
              BASE=Path('/pinned-archive/base'))
    def sha(path):
        require(str(path).endswith('work/complex-nine-native/DATA-PHASES.json'), 'isolated source SHA request')
        return data['hosted']['source_artifacts']['work/complex-nine-native/DATA-PHASES.json']
    ns['sha'] = sha
    # optimize=0 explicitly retains the predecessor's assertions under -O.
    code = compile(ast.Module(body=functions, type_ignores=[]), SOURCE, 'exec', optimize=0)
    exec(code, ns)
    ns['bases'] = [ns['orthobasis'](p) for p in range(112)]
    original = ns['audit'](template)
    require(original['sigma_digest'] == data['hosted']['sigma_stream_sha256'], 'source positive stream')
    equality = compile(ast.Module(body=predicates, type_ignores=[]), SOURCE, 'exec', optimize=0)
    ns.update(r=original, OUT=Path('/pinned-archive/hosted'))
    def compare(charts):
        def read_charts(path):
            require(path.name == 'ACTUAL-SIGMAS.json.gz', 'isolated source chart request')
            return charts
        ns['read'] = read_charts
        exec(equality, ns)
    compare(data['sigmas'])
    witness = next(z for z in data['owners'] if z['width'] == 4)
    # Find its already source-verified chart from the original table.
    axes = data['phases']['recipes'][witness['port']]['idle_children'][witness['child']]['orthogonal_axes'][witness['offset']:witness['offset']+4]
    name, columns = next((k, v) for k, v in data['sigmas'].items() if v[:4] == axes)
    change = tuple((15 ^ (1 << i)) if i < 4 else (1 << i) for i in range(73))
    mutant = list(rebased(columns, change))
    changed = dict(data['sigmas'])
    del changed[name]
    new_name = hashlib.sha256(json.dumps(mutant, separators=(',', ':')).encode()).hexdigest()
    changed[new_name] = mutant  # The mutant carries its correct content hash.
    rejected = []
    try:
        compare(changed)
    except AssertionError:
        rejected.append('same-projector rebase with recomputed chart content hash')
    require(len(rejected) == 1, 'source chart-table guard failed')
    bad_template = copy.deepcopy(template)
    call = next(c for c in bad_template['calls'] if (c['stage'], c['replica']) == (witness['stage'], witness['replica']))
    call['owners'][224 + witness['helper']][1][-1][0] = 72
    try:
        ns['audit'](bad_template)
    except AssertionError:
        rejected.append('wrong literal spectator route')
    require(len(rejected) == 2, 'source spectator-route guard failed')
    kernel_text = (root / KERNEL_SOURCE).read_text()
    kernel_tree = ast.parse(kernel_text, filename=KERNEL_SOURCE)
    cls = next(n for n in kernel_tree.body if isinstance(n, ast.ClassDef) and n.name == 'Op')
    zero = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'zero_state')
    kernel_ns = {}
    exec(compile(ast.Module(body=[zero], type_ignores=[]), KERNEL_SOURCE, 'exec', optimize=0), kernel_ns)
    column_checks = 0
    for axes in ((1,2,4,8), (14,13,11,7), (1,2,4,8,16,32), (62,61,59,55,47,31)):
        for sign in (-1, 1):
            operation = SimpleNamespace(n=6, circuit=[('C', q, sign) for q in axes])
            wanted = convolution(axes, sign)
            for x in range(64):
                vector, denominator_bits = kernel_ns['zero_state'](operation, x)
                for y, value in enumerate(vector):
                    scaled = tuple(a * (1 << (len(axes)-denominator_bits)) for a in value)
                    require(scaled == wanted.get(x ^ y, (0,0)), 'literal source C-kernel column')
                column_checks += 1
    return dict(status='PASS_PINNED_CONTROLLER_CHART_PROTECTION',
                source=SOURCE, source_sha256=hashlib.sha256(text.encode()).hexdigest(),
                selected_functions=[n.name for n in functions],
                extracted_source_sha256=hashlib.sha256('\n\n'.join(ast.get_source_segment(text, n) for n in functions+predicates).encode()).hexdigest(),
                positive_roles=original['hosted'], positive_charts=len(original['sigmas']),
                positive_chart_stream_sha256=original['sigma_digest'], controls=rejected,
                kernel_source=KERNEL_SOURCE,
                kernel_source_sha256=hashlib.sha256((root / KERNEL_SOURCE).read_bytes()).hexdigest(),
                kernel_method_source_sha256=hashlib.sha256(ast.get_source_segment(kernel_text, zero).encode()).hexdigest(),
                source_kernel_columns=column_checks,
                scope='Verbatim orthobasis/audit functions and chart-table assertion with explicit pinned-archive context; not the top-level script, native supplier, phase wrappers, invoice or cold driver.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, default=HERE.parents[1])
    parser.add_argument('--write-expected', action='store_true')
    args = parser.parse_args()
    expected = HERE / 'PRODUCTION.json'
    if args.write_expected:
        require(not expected.exists(), 'production receipt already exists')
    result = load_bytes(canonical(check(args.source_root.resolve())))
    if args.write_expected:
        with expected.open('x') as stream:
            json.dump(result, stream, indent=2, sort_keys=True); stream.write('\n')
    else:
        require(result == read(expected), 'complete production receipt mismatch')
    print(result['status'], 'controls=2', 'receipt_sha256=' + digest(result))


if __name__ == '__main__':
    main()
