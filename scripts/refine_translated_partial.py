#!/usr/bin/env python3
"""Refine the exact parameters of PR21's unchanged translated construction.

Dominik Scholz, with substantial OpenAI Codex assistance. Apache-2.0.
The mathematical construction and its conditional interfaces are due to the
authors credited in research/translated-partial/README.md and NOTICE.
"""
from dataclasses import replace
from difflib import unified_diff
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'research/translated-partial'
sys.path.insert(0, str(SOURCE))
spec = importlib.util.spec_from_file_location('translated_partial', SOURCE / 'verify.py')
translated = importlib.util.module_from_spec(spec)
spec.loader.exec_module(translated)
from certify import require
from prepare_layers import serializable

BASE_COMMIT = '5ba6cf0bfb68f2be8d15610e7972207c50254d6a'
BIT_SAVING = Q(2284609773, 200000000000000)
KAPPA = Q(57114918, 10**13)
GRID = Q(1, 10**15)


def envelope(saving, counts, rows):
    """The retained rational upper envelope, also evaluated outside contraction."""
    result = Q(0)
    for width, count in sorted(rows.items()):
        u = saving * translated.retained.log_upper(Q(counts['m'], width))
        require(0 <= u < 1, 'Exponential enclosure outside range')
        result += Q(count * width, counts['W'] * counts['m']) * (
            1 + u + u*u / (2 * (1-u/3)))
    return result


def certificate():
    # Recompute the entire dependency certificate before changing any parameters.
    baseline = translated.certificate(SOURCE / 'producer-certificate.json')
    require(json.loads(json.dumps(serializable(baseline))) ==
            json.loads((SOURCE / 'certificate.json').read_text()),
            'Pinned PR21 certificate changed')
    bit = translated.bit_certificate(BIT_SAVING)
    tau = 1-BIT_SAVING
    p = replace(translated.parameters(), tau=tau, epsilon=1/(2+BIT_SAVING),
                lam=tau+Q(1, 10**20), lamp=tau+Q(2, 10**20), kappa=KAPPA)
    assembly = translated.assembly(p)
    counts, rows = translated.bit_counts()
    upper = envelope(BIT_SAVING+GRID, counts, rows)
    require(envelope(BIT_SAVING, counts, rows) == bit['moment_upper'],
            'Search envelope differs from the retained certificate')
    require(upper >= 1, 'Next grid point still satisfies this envelope')
    require(bit['strict_gap'] > Q(1, 10**17), 'Bit gap lower bound')
    require(assembly['minimum_margin'] == BIT_SAVING/(2+BIT_SAVING)-p.delta,
            'Unexpected limiting assembly margin')
    require(assembly['absorption_gap'] > Q(1, 10**14), 'Absorption gap lower bound')
    require(KAPPA > translated.KAPPA, 'No improvement over PR21')
    rejected = []
    for name, check in (
        ('next_bit_grid_point', lambda: translated.bit_certificate(BIT_SAVING+GRID)),
        ('kappa_above_assembly_margin', lambda: translated.assembly(
            replace(p, kappa=assembly['minimum_margin']+GRID))),
    ):
        try:
            check()
        except (AssertionError, ValueError):
            rejected.append(name)
        else:
            raise AssertionError('Negative control accepted: '+name)
    paths = [Path(__file__), SOURCE / 'certificate.json',
             ROOT / 'notes/translated-partial-assembly.tex',
             ROOT / 'docs/research/translated-partial-refinement.md']
    return dict(
        status='CONDITIONAL PARAMETER REFINEMENT; NOT FORMAL VERIFICATION',
        baseline_commit=BASE_COMMIT,
        baseline_kappa=translated.KAPPA,
        improvement_ratio=KAPPA/translated.KAPPA,
        bit=bit, complex=baseline['complex'], assembly=assembly,
        grid_bracket=dict(step=GRID, accepted=BIT_SAVING,
                          rejected=BIT_SAVING+GRID, rejected_moment_upper=upper,
                          scope='Ceiling of the retained sufficient rational envelope only; '
                                'not an impossibility result for the exact moment or other constructions.'),
        negative_controls=rejected,
        source_sha256={str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest()
                       for path in paths},
        scope='Same finite networks, bases, precision guard, analytic and fixed-tape '
              'hypotheses as PR21. Only bit saving and final assembly parameters change.')


def proof_patch():
    """Patch PR21's pinned assembly source; leave the historical note unchanged."""
    name = 'notes/translated-partial-assembly.tex'
    original = (ROOT / name).read_text()
    updated = original
    replacements = [
        (r'\frac{5499}{10^9}=5.499', r'\frac{57114918}{10^{13}}=5.7114918'),
        (r'\frac{11}{10^6}', r'\frac{2284609773}{200000000000000}'),
        (r'\frac{159}{10^{10}}', r'\frac{1}{10^{17}}'),
        (r'\frac{1000000}{2000011}', r'\frac{200000000000000}{400002284609773}'),
        (r'\frac{11}{2000011}', r'\frac{2284609773}{400002284609773}'),
        (r'\frac{5499}{10^9}', r'\frac{57114918}{10^{13}}'),
        (r'\frac9{10^{10}}', r'\frac1{10^{14}}'),
    ]
    for old, new in replacements:
        require(old in updated, 'Pinned assembly text changed: '+old)
        updated = updated.replace(old, new)
    return ''.join(unified_diff(original.splitlines(keepends=True),
                                updated.splitlines(keepends=True),
                                fromfile='a/'+name, tofile='b/'+name))


def main():
    result = certificate()
    (ROOT / 'certificates/translated-partial-refinement.json').write_text(
        json.dumps(serializable(result), indent=2, sort_keys=True)+'\n')
    (ROOT / 'patches/translated-partial-refinement.patch').write_text(proof_patch())
    print('PASS conditional kappa='+str(KAPPA)+'; bit saving='+str(BIT_SAVING))
    print('29 strict constraints, 7 strict margins, 2 rejected negative controls')
    print('Bit moment gap > 1e-17; final absorption gap > 1e-14')


if __name__ == '__main__':
    main()
