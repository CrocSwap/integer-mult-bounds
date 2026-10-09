#!/usr/bin/env python3
"""Assemble the source-assisted v4 complex profile with PR189's descended bit supplier.

This script reuses PR184's research/source-assisted/global/assemble_profiles.py
(GPT-6 Astra for icekylinx, Apache-2.0) as a module: its normalize(), select()
and assemble() functions price both moments and run the unchanged 47-constraint
balanced assembly with PR184's finite bridge. Only the inputs change:

- the complex profile is this package's contract-checked profile, with the
  complex half of PR184's construction receipts checked here;
- the bit profile is the PR189 bit profile (chafreaky) after the exact 102-op
  endpoint-frame descent, read from research/paired-cube-twin-local-168/
  certificate.json, which that package's verify.py regenerates.

PR184's select() recomputes the descended bit coarse saving on its 10^-10 grid with the
bad-row allowance 10^-16 and fallback 32 m^2 per edge, the least payable atom
exponent on the 10^-12 grid, and the effective saving with the ordinary leaf
saving 384599/10^10.

Prepared by Avi Eisenberg with Claude (Anthropic) assistance. Apache-2.0.
"""
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json
import sys

PKG = Path(__file__).resolve().parent
REPO = PKG.parents[1]
SA = REPO / 'research/source-assisted'
BIT = REPO / 'research/paired-cube-twin-local-168/certificate.json'


def load_pr184():
    spec = importlib.util.spec_from_file_location('pr184_assemble_profiles', SA / 'global/assemble_profiles.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def complex_receipts(cdata):
    # The complex half of PR184's construction_receipts(), unchanged.
    checks = cdata['contract_checks']
    for name in ('all_fresh_columns_equal_identity',
                 'source_controls_at_paid_parity_frames',
                 'original_source_V_before_all_controls',
                 'controls_before_original_K', 'all_centers_in_phase1',
                 'all_target_cap_reads_in_phase2', 'target_chains_nested'):
        assert checks[name] is True, name
    assert checks['checked_source_columns'] == checks['checked_target_rows'] == cdata['v']
    assert cdata['scalar_denominator_lcm'] == '2'
    assert cdata['terminal_sink_substitutions'] == 0
    cp = Path(cdata['exact_lift_certificate_path'])
    if not cp.is_file():
        cp = REPO / cp
    assert cp.is_file(), 'The exact complex lift certificate must be present'
    assert sha256(cp.read_bytes()).hexdigest() == cdata['exact_lift_certificate_sha256']
    return dict(complex_lift_certificate_sha256=cdata['exact_lift_certificate_sha256'],
                complex_endpoint_checks=checks)


def bit_profile():
    certificate = json.loads(BIT.read_text())
    assert certificate['status'].startswith('PASS'), 'PR189 certificate status'
    row = certificate['bit']['profile']
    assert row['m'] == 72 and row['deficit_per_vertex'] == 1936
    assert row['terminal_sinks'] == 34 and row['reused_registers'] == 1760
    return row, sha256(BIT.read_bytes()).hexdigest(), certificate['bit']['coarse']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--complex', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not sys.flags.optimize, 'Assertions must remain enabled'
    if hasattr(sys, 'set_int_max_str_digits'):
        sys.set_int_max_str_digits(0)
    pr184 = load_pr184()
    cdata = json.loads(args.complex.read_text())
    row, bit_sha, pr189_coarse = bit_profile()
    c = pr184.select(pr184.normalize(cdata))
    b = pr184.select(pr184.normalize(row), True)
    # PR184's 10^-10 bit grid must not exceed PR189's own 10^-18 certificate.
    assert b['saving'] <= pr184.Q(pr189_coarse['coarse_saving'])
    out = dict(status='Exact arithmetic; construction and finite bridge are explicit proof dependencies',
               complex=c, bit=b,
               source_sha256=dict(complex=sha256(args.complex.read_bytes()).hexdigest(), bit_certificate=bit_sha),
               bit_source='research/paired-cube-twin-local-168/certificate.json bit.profile (PR189)',
               arithmetic='PR184 assemble_profiles: 32-term rational logarithm enclosure; rational exponential majorant; upward 2^120 rounding',
               construction_receipts=complex_receipts(cdata))
    out.update(pr184.assemble(c, b, REPO, SA / 'global/FINITE_BRIDGE.txt'))
    for key in ('reviewed_baseline', 'fixed_doubling_target', 'ratio_to_reviewed_baseline',
                'ratio_to_reviewed_baseline_decimal', 'doubling_achieved'):
        out.pop(key, None)
    args.output.write_text(json.dumps(pr184.serial(out), indent=2) + '\n')
    print(json.dumps(dict(kappa=str(out['kappa']), complex=str(c['saving']), bit_effective=str(b['effective_saving']))))


if __name__ == '__main__':
    main()
