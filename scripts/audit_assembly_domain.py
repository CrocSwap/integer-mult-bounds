#!/usr/bin/env python3
"""Arithmetic-only audit of the selected assembly's small-saving domain.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
This diagnostic never relaxes the production verifier or supplies a new network.
"""
import argparse
import ast
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = 'research/coordinated-frames-and-entrance-banks/'
PINS = {
    PACKAGE + 'arithmetic/balanced_shared.py': 'c3204e1758057f5ef10724014f38b91b8a01f6d8a3562b054263fc74795bfd90',
    PACKAGE + 'arithmetic/shared_bridge.py': 'd0729e2d12d8c038719ea6eb83b169c09660f43de2d3d2da10a6a173f5204f93',
    PACKAGE + 'arithmetic/interval_moment.py': '9d3d1d28bfb3375958995205179b171fb65c70a3792cf9f7a21ef5ee54f5460b',
    PACKAGE + 'certificate.json': '59b20818af6f850f40d18fd8206b136da504d9cbc57dbbefcba232c62f3384e6',
}
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def pinned_bytes(path, digest):
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == digest, 'Source pin mismatch: ' + str(path))
    return raw


def assembly_function(bridge_validator, requirement):
    """Compile the unchanged function body; explicitly inject its dependencies.

    No imports from inside the frozen package: discovery must not create
    __pycache__ entries in its hash-pinned inventory.
    """
    name = PACKAGE + 'arithmetic/balanced_shared.py'
    tree = ast.parse(pinned_bytes(ROOT / name, PINS[name]), filename=name)
    definitions = [node for node in tree.body
                   if isinstance(node, ast.FunctionDef) and node.name == 'assembly']
    require(len(definitions) == 1, 'Expected one pinned assembly function')
    namespace = dict(Q=Q, rational=Q, require=requirement,
                     validate_shared_bridge=bridge_validator)
    exec(compile(ast.Module(body=definitions, type_ignores=[]), name, 'exec'), namespace)
    return namespace['assembly']


def published_control():
    """Recompute the real bridge and all slacks using strict requirements."""
    name = PACKAGE + 'arithmetic/shared_bridge.py'
    namespace = {}
    exec(compile(pinned_bytes(ROOT / name, PINS[name]), name, 'exec'), namespace)
    assembly = assembly_function(namespace['validate_shared_bridge'], require)
    name = PACKAGE + 'certificate.json'
    certificate = json.loads(pinned_bytes(ROOT / name, PINS[name]))
    arithmetic = certificate['arithmetic']
    params = arithmetic['assembly']['parameters']
    result = assembly(arithmetic['bridge'], certificate['complex']['profile'],
                      Q(params['a_bit']), Q(params['kappa']),
                      beta=Q(params['beta']), h=Q(params['h']),
                      a_complex=Q(params['a_complex']))
    expected = {key: Q(value) for key, value in arithmetic['assembly']['constraints'].items()}
    require(result['constraints'] == expected, 'Published slacks changed')
    return dict(status='PASS existing published arithmetic and real numeric bridge',
                kappa=certificate['kappa'], strict_constraint_count=len(expected))


def diagnostic_case(a, b, kappa, *, beta=Q(1, 1000), backoff=Q(1, 10**8)):
    """Observe all arithmetic failures with explicitly hypothetical suppliers.

    The bridge validator is replaced by an assumed positive bridge ONLY HERE.
    The require observer records failures and continues to expose all slacks.
    Neither operation is a valid verification of a new multiplier. There is
    deliberately no 'accepted' or 'verified construction' result field.
    """
    require(all(type(v) is Q for v in (a, b, kappa, beta, backoff)),
            'Diagnostic inputs must be exact Fractions')
    require(0 < a < b < 1 and 0 < beta < 1 and 0 < backoff < Q(1, 2) and kappa > 0,
            'Outside the diagnostic input domain')
    failures = []

    def observe(ok, message):
        if not ok:
            failures.append(message)

    assumed = dict(bit_uniform=dict(ordinary_saving=a),
                   semantic=dict(C0=1, strict_literal_gap=1), rows=dict(degree_gap=1))
    assembly = assembly_function(lambda bridge, row: bridge, observe)
    result = assembly(assumed, {}, a, kappa, beta=beta, h=backoff, a_complex=b)
    slacks = result['constraints']
    require(len(slacks) == 47, 'Constraint inventory changed')
    failed = {key: str(value) for key, value in slacks.items() if value <= 0}
    # With the same hypothetical bridge, the normal fail-closed requirement
    # must reject every listed diagnostic, including equality at a boundary.
    strict = assembly_function(lambda bridge, row: bridge, require)
    try:
        strict(assumed, {}, a, kappa, beta=beta, h=backoff, a_complex=b)
    except ValueError:
        strict_rejects = True
    else:
        strict_rejects = False
    return dict(status='HYPOTHETICAL ARITHMETIC ONLY; no new construction',
                inputs={key: str(value) for key, value in
                        dict(a=a, b=b, kappa=kappa, beta=beta, backoff=backoff).items()},
                bridge_assumption='Supplier availability and bridge validity are assumed, not checked',
                strict_arithmetic_rejects_with_assumed_bridge=strict_rejects,
                failed_slacks=failed,
                other_slacks_strictly_positive=sum(value > 0 for value in slacks.values()),
                observed_requirement_failures=failures,
                gaussian_r=str(result['parameters']['alpha_squared_power']),
                balance_margin=str(result['minimum_margin']))


def audit():
    for name, digest in PINS.items():
        pinned_bytes(ROOT / name, digest)
    cases = {
        'domain_boundary': diagnostic_case(Q(1, 50), Q(1, 32), Q(19, 1000)),
        'above_small_saving_domain': diagnostic_case(Q(1, 25), Q(1, 20), Q(19, 500)),
        'larger_arithmetic_only_example': diagnostic_case(Q(3, 10), Q(31, 100), Q(23, 100)),
        'gaussian_range_control': diagnostic_case(Q(2, 5), Q(41, 100), Q(7, 25)),
        'leaf_order_control': diagnostic_case(Q(1, 25), Q(1, 20), Q(19, 500), beta=Q(1, 2)),
        'excess_kappa_control': diagnostic_case(Q(1, 25), Q(1, 20), Q(1, 25)),
    }
    return dict(status='ARITHMETIC DIAGNOSTIC; retained production domain unchanged',
                source_sha256=PINS, published_control=published_control(), cases=cases,
                scoped_bounds=dict(retained_domain_kappa='1/33',
                                   retained_gaussian_range_kappa='1/4',
                                   inequalities='Strict upper bounds, not attainable witnesses or universal lower bounds'),
                unproved=['Availability of stronger finite suppliers',
                          'Validity of bridges and all-size interfaces outside the admitted domain',
                          'Extension of interval-enclosure and cutoff ranges'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--write', type=Path)
    group.add_argument('--check', type=Path)
    args = parser.parse_args()
    report = audit()
    if args.check:
        require(json.loads(args.check.read_text()) == report, 'Diagnostic receipt differs')
        print('PASS pinned assembly-domain diagnostic; no production constraint relaxed')
    elif args.write:
        args.write.write_text(json.dumps(report, indent=2) + '\n')
    else:
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
