#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact directed uniqueness bound on the inherited BIT-admissible interval.

Hao Yan (@FanPUYen), with substantial OpenAI Codex assistance. The integer
interval engine is retained unchanged through ToikY's PR7546, with its
predecessor attribution. This binds one invoice and certifies its raw root;
it does not independently establish the underlying multiplication theorem.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
ENGINE = HERE / 'retained/role902/engines/interval_gate.py'
ENGINE_SHA = '60a743d13f668ef86db4b8215b4d5d04430a671ba6f1fe06d9c1c4c3dfe86da5'
INVOICE = HERE / 'data/invoice-new.json'
INVOICE_SHA = 'fb96f912da7203a775cdddd82870823117a27e2a7f54f5f45956a651728aadd6'
BIT_CAP = Q('0.00376669')
ROOT_LOWER = Q('0.0036502223358272')
ROOT_UPPER = Q('0.0036502223358273')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def certify():
    require(not sys.flags.optimize, 'retained interval proof assertions must be enabled')
    require(hashlib.sha256(ENGINE.read_bytes()).hexdigest() == ENGINE_SHA,
            'exact retained interval source')
    require(hashlib.sha256(INVOICE.read_bytes()).hexdigest() == INVOICE_SHA,
            'exact candidate invoice bytes')
    # Execute authenticated source rather than accepting an existing .pyc.
    engine = runpy.run_path(str(ENGINE), run_name='role315_ceiling_interval')
    invoice = json.loads(INVOICE.read_bytes())
    target = {int(rank): n for rank, n in invoice['targets'].items()}
    paid = {int(rank): n for rank, n in invoice['paid'].items()}
    require(all(type(n) is int and n >= 0 for hist in (target, paid) for n in hist.values()),
            'nonnegative integer inventory')
    require(all(r > 0 for r in target.keys() | paid.keys()), 'positive ranks')
    signed = {r: target.get(r, 0) - paid.get(r, 0) for r in target.keys() | paid.keys()}
    require(sum(r * n for r, n in signed.items()) == 1424, 'rank surplus at C=0')

    # F'(C) = -sum_r c_r log(r) r^(1-C). For c_r >= 0 the
    # negative summand is largest at BIT_CAP; for c_r < 0 the
    # positive summand is largest at 0. Summing these independently
    # valid upper bounds controls every C in the entire closed interval.
    derivative_upper = (0, 0)
    for rank, count in signed.items():
        endpoint = BIT_CAP if count >= 0 else Q(0)
        term = engine['mul'](engine['power'](rank, endpoint), engine['log'](rank))
        derivative_upper = engine['add'](derivative_upper, engine['smul'](term, -count))
    scale = engine['B']
    bound = Q(derivative_upper[1], scale)
    require(bound < 0, 'strictly negative derivative upper bound on full BIT interval')
    lower = engine['moment'](signed, ROOT_LOWER)
    upper = engine['moment'](signed, ROOT_UPPER)
    require(0 < ROOT_LOWER < ROOT_UPPER < BIT_CAP, 'root bracket inside certified interval')
    require(lower[0] > 0 and upper[1] < 0, 'opposite directed root endpoint signs')

    return dict(
        status='PASS_ROLE315_FINITE_FAMILY_CEILING',
        invoice_sha256=INVOICE_SHA, interval_engine_sha256=ENGINE_SHA,
        moment='F(C) = sum_r (T_r-P_r) r^(1-C)',
        certified_interval=['0', str(BIT_CAP)],
        derivative_upper=str(bound),
        root_bracket=[str(ROOT_LOWER), str(ROOT_UPPER)],
        root_bracket_decimal=['0.0036502223358272', '0.0036502223358273'],
        moment_at_lower=[str(Q(x, scale)) for x in lower],
        moment_at_upper=[str(Q(x, scale)) for x in upper],
        unique_root_on_certified_interval=True,
        fixed_family_upper='0.0036502223358273',
        scope=('Unique raw crossing of this exact invoice on [0,0.00376669]. '
               'Together with physical.py exhaustion and the strict invoice-order proof, '
               'this bounds the fixed-scalar no-contact fusion family in that interval. '
               'It is not a global optimization bound or a standalone multiplier certificate.'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    text = json.dumps(certify(), indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(text)
    print(text, end='')


if __name__ == '__main__':
    main()
