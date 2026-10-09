"""Exact finite verification of staggered dual-paired rational-center and bit producers.

Copyright 2026 Thomas Marchand, Apache-2.0. Prepared with Google Antigravity
assistance. Builds on icekylinx's PR #104 stopped product-ring construction and
Rohan Arun's PR #107 reversed pair-star ordering. Does not formally verify the
inherited analytic or all-size tape interfaces.
"""
import argparse, hashlib, importlib.util, json, os, shlex, subprocess, sys, tempfile
from pathlib import Path
from fractions import Fraction as Q

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import stopped_product_network as parent
from stopped_product.complex import build as parent_build
from structured_bulk_assembly import assembly, js


def read(p):
    return json.loads(p.read_text())


def pins():
    assert not sys.flags.optimize, 'Assertions must remain enabled'
    for name, digest in read(HERE / 'SOURCE.json')['files'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name


def check_coarse(bit_profile, coarse_val):
    old_coarse, old_ab = parent.COARSE, parent.AB
    try:
        parent.COARSE = coarse_val
        parent.AB = (1 - parent.ATOM) * parent.COARSE + parent.ATOM * parent.OLD
        return parent.coarse_moment(bit_profile), parent.AB
    finally:
        parent.COARSE, parent.AB = old_coarse, old_ab


def exact(crow, brow=None):
    if brow is None:
        brow = read(HERE / 'bit-axis.json')
    original = parent.certificate()
    assert original['kappa'] == Q(194869, 2500000000)
    pr107_kappa = Q(read(ROOT / 'research/reversed-rational-centers/certificate.json')['kappa'])
    assert pr107_kappa == Q(7798412662809, 10**17)

    prev_net = read(ROOT / 'certificates/copied-centers-network.json')
    pinned_bit = parent.profile(read(ROOT / 'certificates/stopped-product-bit-axis.json'))
    phase = parent.profile(crow)
    bridge_pinned = parent.finite_bridge(pinned_bit, phase, crow, prev_net)

    b = Q(8801801147, 10**14)
    cm = parent.moment(phase['m'], phase['W'], phase['child_multiplicities'], b, True)
    a_pinned = min(parent.AB, (1 - parent.PHASE_STOP) * b - Q(1, 10**10))
    k_pinned = Q(16065034230003, 200000000000000000)
    asm_pinned = assembly(a_pinned, b, bridge_pinned, k_pinned, beta=parent.PHASE_STOP)
    assert len(asm_pinned['strict_constraints']) == 47 and len(asm_pinned['margins']) == 7
    assert k_pinned > pr107_kappa > original['kappa'] and a_pinned == parent.AB

    # Reject next grid points for complex-only bound.
    try:
        parent.moment(phase['m'], phase['W'], phase['child_multiplicities'], b + Q(1, 10**14), True)
    except ValueError as e:
        assert str(e) == 'Characteristic moment does not contract'
    else:
        raise AssertionError('Complex next grid was accepted')

    try:
        assembly(a_pinned, b, bridge_pinned, k_pinned + Q(1, 10**18), beta=parent.PHASE_STOP)
    except AssertionError:
        pass
    else:
        raise AssertionError('Complex-only kappa next grid was accepted')

    # Joint regenerated h=23 positive-label bit + h=24 rational-center complex refinement.
    assert brow['h'] == 23 and brow['label_source'] == 'positive'
    assert brow['R'] == brow['c'] + brow['q'] - brow['matching']
    joint_bit = parent.profile(brow)
    coarse_joint = Q(8926632362, 10**14)
    bm_joint, ab_joint = check_coarse(joint_bit, coarse_joint)
    assert ab_joint == Q(4460775859819, 50000000000000000)

    try:
        check_coarse(joint_bit, coarse_joint + Q(1, 10**14))
    except ValueError as e:
        assert str(e) == 'Both stopped-recurrence moments'
    else:
        raise AssertionError('Coarse bit next grid was accepted')

    bridge_joint = parent.finite_bridge(joint_bit, phase, crow, prev_net)
    a_joint = min(ab_joint, (1 - parent.PHASE_STOP) * b - Q(1, 10**10))
    k_joint = Q(3520093170589, 40000000000000000)
    asm_joint = assembly(a_joint, b, bridge_joint, k_joint, beta=parent.PHASE_STOP)
    assert len(asm_joint['strict_constraints']) == 47 and len(asm_joint['margins']) == 7
    assert k_joint > k_pinned and a_joint < ab_joint

    try:
        assembly(a_joint, b, bridge_joint, k_joint + Q(1, 10**18), beta=parent.PHASE_STOP)
    except AssertionError:
        pass
    else:
        raise AssertionError('Joint kappa next grid was accepted')

    expected = read(HERE / 'certificate.json')
    actual_cert = dict(
        kappa=k_pinned,
        complex_saving=b,
        bit_parameter=a_pinned,
        actual_bit_saving=parent.AB,
        profile=phase,
        bridge=bridge_pinned,
        assembly=asm_pinned,
        joint=dict(
            kappa=k_joint,
            coarse_bit_saving=coarse_joint,
            actual_bit_saving=ab_joint,
            bit_parameter=a_joint,
            complex_saving=b,
            bit_moment_gap=bm_joint['strict_gap'],
            complex_moment_gap=cm['strict_gap'],
            bit_profile=joint_bit,
            bridge=bridge_joint,
            assembly=asm_joint,
        ),
    )
    for key, value in actual_cert.items():
        assert js(value) == expected[key], key

    return dict(
        kappa_complex_only=str(k_pinned),
        kappa_joint=str(k_joint),
        complex_saving=str(b),
        coarse_bit_saving=str(coarse_joint),
        stopped_bit_saving=str(ab_joint),
        complex_moment_gap=str(cm['strict_gap']),
        bit_moment_gap=str(bm_joint['strict_gap']),
        constraints=47,
        margins=7,
        next_grid_controls=4,
    )


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def regenerate(work):
    cxx = shlex.split(os.environ.get('CXX', 'c++'))
    mc = work / 'match_complex_general'
    me = work / 'match_exported_dag'
    mp = work / 'match_positive_dag'
    subprocess.run([*cxx, '-O3', '-std=c++17',
        str(ROOT / 'scripts/endpoint_gauge/match_complex_general.cpp'), '-o', str(mc)], check=True)
    subprocess.run([*cxx, '-O3', '-std=c++17',
        str(ROOT / 'scripts/partial_swap/match_exported_dag.cpp'), '-o', str(me)], check=True)
    subprocess.run([*cxx, '-O3', '-std=c++17',
        str(ROOT / 'scripts/partial_swap/match_positive_dag.cpp'), '-o', str(mp)], check=True)

    pr107_mod = load_module('pr107_producer', ROOT / 'research/reversed-rational-centers/producer.py')
    sel_mod = load_module('staggered_complex_producer', HERE / 'producer.py')
    bit_mod = load_module('staggered_bit_producer', HERE / 'bit_producer.py')

    results = {}
    for name, builder, expected in (
        ('parent', parent_build, read(ROOT / 'certificates/stopped-product-complex-input.json')),
        ('pr107', pr107_mod.build, read(ROOT / 'research/reversed-rational-centers/producer.json')),
        ('selected_complex', sel_mod.build, read(HERE / 'producer.json')),
    ):
        prefix = work / name
        construction = builder(24, prefix, 24)
        row = json.loads(subprocess.check_output([str(mc), str(prefix) + '.bin', str(prefix) + '.labels'], text=True))
        for key in ('h', 'v', 'c', 'q', 'R', 'loss', 'histogram'):
            assert row[key] == expected[key], (name, key)
        assert construction['R'] == row['baseline_R']
        assert row['R'] == row['c'] + row['q'] - row['matched']
        results[name] = row

    # Pin the unchanged rational-center and frame validation tail against PR104's complex.py.
    tail_marker = '    for a in range(d,h):\n'
    sel_text = (HERE / 'producer.py').read_text()
    old_text = (ROOT / 'scripts/stopped_product/complex.py').read_text()
    assert tail_marker in sel_text and tail_marker in old_text
    assert sel_text.split(tail_marker, 1)[1] == old_text.split(tail_marker, 1)[1]

    # Regenerate and verify the h=23 positive-label bit producer.
    bdag = work / 'bit23.bin'
    bit_mod.build(23, bdag)
    orig_b = json.loads(subprocess.check_output([str(me), str(bdag), str(bdag) + '.links'], text=True))
    bit_mod.positive_labels(str(bdag))
    pos_b = json.loads(subprocess.check_output([str(mp), str(bdag), str(bdag) + '.positive'], text=True))
    expected_b = read(HERE / 'bit-axis.json')
    assert orig_b['matched'] == pos_b['matched'] == expected_b['matching']
    for key in ('h', 'v', 'c', 'q', 'baseline_R', 'R', 'loss', 'histogram'):
        assert pos_b[key] == expected_b[key], ('selected_bit', key)
    assert pos_b['R'] == pos_b['c'] + pos_b['q'] - pos_b['matched']
    assert pos_b['loss'] == 23 * 22 and pos_b['rank_sum'] == 23 * pos_b['R'] + 2 * pos_b['loss']
    results['selected_bit'] = pos_b
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--arithmetic-only', action='store_true')
    args = parser.parse_args()
    pins()
    receipt = exact(read(HERE / 'producer.json'), read(HERE / 'bit-axis.json'))
    if not args.arithmetic_only:
        with tempfile.TemporaryDirectory(prefix='staggered-rational-centers-') as tmp:
            regenerate(Path(tmp))
        receipt['parent_pr107_and_selected_producers_regenerated'] = True
    print(json.dumps(receipt, indent=2))
    print('PASS conditional staggered dual-paired rational-center refinement')


if __name__ == '__main__':
    main()
