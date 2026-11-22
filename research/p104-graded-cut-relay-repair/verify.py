#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run the source-bound cuts, interval price, information and repair replays."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
GRAPH = HERE / 'pinned' / 'strong-bit.json.gz'
FROZEN = {
    'dimension_cuts.py': '9ce72736838a097320b1cb213b09601273fec5fdfb40966958bcf1d9c37b8fe3',
    'DIMENSION-CUTS.json': 'ebb1a31a6e85aee298f5ad0d21168ec2d48aed0a7f52f3a0f7c5a7d2d41ba90e',
    'feedback_rigidity.py': '25c7e490ecb678e84c782c61163b61b3428a25497b2ca5b23146130dc5dc19fd',
    'FEEDBACK-RIGIDITY.json': '3a648032d227705d3440b52455450a39cd067b98daaf69ccc2c07e3ae1a58410',
    'feedback_independent.py': 'f3d3788407294b8416c138632c15f7fc73fd7a51006709c2477c84151d80dc7c',
    'FEEDBACK-INDEPENDENT.json': 'd65d2f6b6ebcf27b4f45606d8e7cc069958140ee0a353fc158357ebd16478b3f',
    'curvature.py': '60cceec9033fa8d099b343cadd4726b6099dabd9306087eb77741ad1ae332c86',
    'CURVATURE.json': 'de2d7c008b2fab2f2fbd1b5ecb1d58fe87400dd67da9adfd24639880f691b44d',
    'pinned/EFREE-CALLER.json.gz': '757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b',
    'grade_price.py': 'd1b15db0625855e18f64fecc87e037a635da3cd9413e55c22157ab5c51b6873c',
    'GRADE-PRICE.json': 'f0707455c18e4ec868b81c2eb13ea06de5facbf7c2ceda465348d7ad39d91901',
    'information.py': '5ced620536a94181430cae9d063b23475bc92c15c7d8fda55d820caa18e4a650',
    'INFORMATION.json': '6809b6ac0e96b1f0316bb5646731b89c5739f5cb8647c4f05db796071b19813d',
    'repair.py': 'e4de1ec7eb18a7203b1ac1ee2b0affb42ca0dc381289359257b43fdcb18b71ef',
    'frozen_replay.py': '4f1987e2b50696100cd4279e297a69532c6664aff08c9f449b5208a5db47d408',
    'EXACT-EDITS.json': '414622da5c258317187eabdfc5028dced7dbb2c3cc8e80d8b4f2a592ac46fdc8',
    'FROZEN-REPLAY.json': 'c36f185f66184cd1d861dcf425e855ba6d36c99269a5851042c6fc6d9c47a697',
    'REPAIR.json': '5613b070541804d66e074909d597ec18031f3a5505af861f6ff63ca03f7c8e88',
    'pinned/strong-bit.json.gz': '74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326',
}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def load_module(filename):
    spec = importlib.util.spec_from_file_location('p104_' + filename[:-3], HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def capture(call):
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        call()
    return json.loads(stream.getvalue())


def compare(result, name):
    expected = json.loads((HERE / name).read_text())
    result = json.loads(json.dumps(result))  # JSON canonicalizes integer keys.
    require(result == expected, 'receipt mismatch: ' + name)


def must_reject(call, label):
    try:
        call()
    except (AssertionError, ValueError):
        return
    raise AssertionError('negative control accepted: ' + label)


def main():
    require(not sys.flags.optimize, 'run without optimized assertions')
    for name, expected in FROZEN.items():
        require(hashlib.sha256((HERE / name).read_bytes()).hexdigest() == expected,
                'frozen bytes changed: ' + name)
    graph_bytes = GRAPH.read_bytes()
    git_object = b'blob ' + str(len(graph_bytes)).encode('ascii') + b'\0' + graph_bytes
    require(hashlib.sha1(git_object).hexdigest() == '16f8cafb1c4d139a99a62e46eb40c118e6176c34',
            'source Git blob mismatch')
    dimension = load_module('dimension_cuts.py')
    grade = load_module('grade_price.py')
    curvature = load_module('curvature.py')
    feedback = load_module('feedback_rigidity.py')
    feedback_audit = load_module('feedback_independent.py')
    information = load_module('information.py')
    repair = load_module('repair.py')
    frozen = load_module('frozen_replay.py')
    repair.HERE = GRAPH.parent

    d = dimension.check(GRAPH)
    compare(d, 'DIMENSION-CUTS.json')
    p = grade.check(GRAPH)
    compare(p, 'GRADE-PRICE.json')
    c = curvature.check(GRAPH, HERE / 'pinned/EFREE-CALLER.json.gz')
    compare(c, 'CURVATURE.json')
    q = feedback.run(GRAPH)
    compare(q, 'FEEDBACK-RIGIDITY.json')
    q2 = feedback_audit.check(GRAPH, HERE / 'FEEDBACK-RIGIDITY.json')
    compare(q2, 'FEEDBACK-INDEPENDENT.json')
    i = capture(lambda: information.main(GRAPH))
    compare(i, 'INFORMATION.json')
    r = capture(repair.main)
    compare(r, 'REPAIR.json')
    f = frozen.check(GRAPH, HERE / 'EXACT-EDITS.json')
    compare(f, 'FROZEN-REPLAY.json')
    g = frozen.source(GRAPH)
    changed_histogram = curvature.native_upward(g)
    changed_histogram[1] += 1
    changed_histogram[2] -= 2
    changed_histogram[3] += 1
    require(sum(changed_histogram.values()) == sum(curvature.native_upward(g).values())
            and sum(r*n for r,n in changed_histogram.items()) == 4750,
            'histogram corruption control changed count or rank sum')
    must_reject(lambda: curvature.validate_profiles(changed_histogram, curvature.RELAXED),
                'rank-preserving histogram corruption')
    bad_graph = dict(g)
    bad_graph['program'] = [list(row) for row in g['program']]
    bad_graph['program'][7112][3] = 0
    must_reject(lambda: curvature.ordered_contacts(bad_graph), 'changed 4+4 incidence')
    changes = json.loads((HERE / 'EXACT-EDITS.json').read_text())
    require(frozen.apply(g['program'], changes) == repair.builds(g['program'], 'exact'),
            'independent edit list differs from repair generator')

    # Confirm each independent input reader actually rejects modified source
    # bytes, not just that a digest was printed. Temporary files are discarded.
    with tempfile.TemporaryDirectory(prefix='p104-graded-source-') as tmp:
        bad = Path(tmp) / 'damaged.gz'
        raw = GRAPH.read_bytes()
        bad.write_bytes(raw[:-1] + bytes([raw[-1] ^ 1]))
        for label, reader in [('dimension', dimension.check), ('grade', grade.check),
                              ('information', information.read_graph), ('repair', repair.load),
                              ('frozen', frozen.source), ('feedback', feedback.run),
                              ('curvature', curvature.read_graph)]:
            must_reject(lambda reader=reader: reader(bad), label + ' source')
        bad_caller = Path(tmp) / 'damaged-caller.gz'
        caller = (HERE / 'pinned/EFREE-CALLER.json.gz').read_bytes()
        bad_caller.write_bytes(caller[:-1] + bytes([caller[-1] ^ 1]))
        must_reject(lambda: curvature.read_caller(bad_caller), 'caller source')
        bad_receipt = Path(tmp) / 'damaged-feedback.json'
        tampered = json.loads((HERE / 'FEEDBACK-RIGIDITY.json').read_text())
        tampered['certificate'][0]['witness_pair'][0]['shift_mask'] ^= 1
        bad_receipt.write_text(json.dumps(tampered))
        must_reject(lambda: feedback_audit.check(GRAPH, bad_receipt),
                    'feedback witness corruption')
        corrupt_changes = json.loads((HERE / 'EXACT-EDITS.json').read_text())
        corrupt_changes['edits'][0]['old'][1] += 1
        must_reject(lambda: frozen.apply(g['program'], corrupt_changes),
                    'edit anchor corruption')
    damaged = dict(d)
    damaged['upward_grade'] = d['upward_grade'] - 1
    must_reject(lambda: compare(damaged, 'DIMENSION-CUTS.json'), 'damaged receipt')
    print('PASS: source bindings; eight saturated cuts, 120 hub cuts, interval price and curvature;')
    print('      27 feedback sites and 4643 sender exclusions with independent low-pivot replay;')
    print('      sharp information bound controls; independent 630-row repair and transpose;')
    print('      damaged source, receipt, witness, edit, histogram and incidence controls;')
    print('      wrong oracle, missing ADD, and cut controls')


if __name__ == '__main__':
    main()
