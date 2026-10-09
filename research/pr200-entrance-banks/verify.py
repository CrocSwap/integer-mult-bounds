#!/usr/bin/env python3
"""Verify PR186's completed entrance banks on PR200's physical bit word, priced against the v4 complex supplier.

Run from the repository root:

    python3 -B research/pr200-entrance-banks/verify.py [--full]

The check rebuilds every claimed number from the literal PR200 word and
compares the canonical result with certificate.json. --full first runs PR200's
own verifier. --write is authoring mode and rewrites certificate.json.
"""
from fractions import Fraction as Q
from hashlib import sha1, sha256
from pathlib import Path
import argparse
import ast
import contextlib
import json
import subprocess
import sys

if sys.flags.optimize:
    raise SystemExit('refusing -O: the checks are assertions')
sys.dont_write_bytecode = True
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BIT = REPO / 'research/paired-cube-diagonal-bit-168'
sys.path.insert(0, str(HERE))
import banks
import pricing
from banks import need

PORTED = {'banks.py': ['bank_projectors'], 'pricing.py': ['paid_moment', 'certify', 'independent_bank_moment']}


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def git_blob(path):
    data = path.read_bytes()
    return sha1(b'blob %d\0' % len(data) + data).hexdigest()


def pins():
    manifest = json.loads((HERE / 'SOURCE.json').read_text())
    need(manifest['files'], 'empty source closure')
    values = {name: digest(REPO / name) for name in manifest['files']}
    need(values == manifest['files'], 'pinned package or dependency bytes changed')
    return values


def references():
    manifest = json.loads((HERE / 'references/manifest.json').read_text())
    for name, entry in manifest['files'].items():
        need(git_blob(HERE / 'references' / name) == entry['git_blob'], 'vendored file differs from its upstream blob: ' + name)
    upstream = ast.parse((HERE / 'references/pr186/bit/prove.py').read_text())
    original = {n.name: ast.dump(n) for n in upstream.body if isinstance(n, ast.FunctionDef)}
    ported = []
    for local, names in PORTED.items():
        tree = ast.parse((HERE / local).read_text())
        mine = {n.name: ast.dump(n) for n in tree.body if isinstance(n, ast.FunctionDef)}
        for name in names:
            need(mine[name] == original[name], 'ported PR186 function differs from upstream: ' + name)
            ported.append(name)
    return dict(vendored_files=len(manifest['files']), git_blobs_verified=True, ported_pr186_functions=sorted(ported))


def literal_word():
    sys.path.insert(0, str(BIT / 'bit'))
    from word import Candidate
    from terminal import prove as prove_terminal
    word = Candidate()
    word.exact_frames()
    selection = json.loads((BIT / 'selected/bit/sinks.json').read_text())
    with contextlib.redirect_stdout(sys.stderr):
        terminal = prove_terminal(word, selection)
    row = terminal['profile']
    row['child_histogram'] = {int(k): n for k, n in row['child_histogram'].items()}
    published = json.loads((BIT / 'certificate.json').read_text())['bit']['profile']
    for key in ('R', 'W_per_vertex', 'rank_per_vertex', 'deficit_per_vertex', 'terminal_sinks', 'reused_registers', 'selected_roles'):
        need(row[key] == published[key], 'terminal word agrees with the PR200 certificate: ' + key)
    need(row['child_histogram'] == {int(k): n for k, n in published['child_histogram'].items()}, 'terminal histogram agrees with the PR200 certificate')
    sinks = {e['role'] for e in terminal['selected']}
    summary = dict(status=terminal['status'], formal=terminal['formal'], controls=terminal['controls'],
        integer_residual_bound=terminal['integer_residual_bound'], deleted_sink_roles=sorted(sinks))
    return word, row, sinks, summary


def mutations(word, row, sinks, packed, starts):
    rejected = []
    live = sorted(set(word.phys.values()) - sinks - set(starts))
    for tag, attempt in (
            ('sink role counted as a live bank chain', lambda: banks.packed_row(word, row, sinks - {min(sinks)})),
            ('live chain added to the deleted sinks', lambda: banks.packed_row(word, row, sinks | {live[0]})),
            ('corrupted packed rank mass', lambda: pricing.certify(dict(packed, rank_per_vertex=packed['rank_per_vertex'] + 1))),
            ('missing rank60 exterior', lambda: banks.packed_row(word, dict(row, child_histogram={r: n for r, n in row['child_histogram'].items() if r != 60}), sinks))):
        try:
            attempt()
        except ValueError:
            rejected.append(tag)
        else:
            raise AssertionError('mutation accepted: ' + tag)
    f = word.gauge[min(starts)]['frame']
    saved = word.C.A[f]
    word.C.A[f] = [list(a) for a in saved[:3]] + [list(word.C.B[f][0])]
    try:
        banks.gauge_charts(word, starts)
    except ValueError:
        rejected.append('wrong entrance chart residual')
    else:
        raise AssertionError('mutation accepted: wrong entrance chart residual')
    finally:
        word.C.A[f] = saved
    return rejected


def js(x):
    if isinstance(x, Q):
        return str(x)
    if isinstance(x, dict):
        return {str(k): js(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [js(v) for v in x]
    if isinstance(x, set):
        return sorted(js(v) for v in x)
    return x


def build():
    refs = references()
    word, row, sinks, terminal = literal_word()
    packed, starts = banks.packed_row(word, row, sinks)
    charts = banks.gauge_charts(word, starts)
    projectors = banks.bank_projectors()
    weighted = banks.weighted_bank_controls()
    schedule = json.loads(subprocess.run([sys.executable, '-B', str(HERE / 'references/round8/bank_schedule.py')],
        check=True, capture_output=True, text=True).stdout)
    need(schedule['status'] == 'PASS', 'round-8 bank schedule diagnostic')
    coarse = pricing.certify(packed)
    gap = pricing.independent_bank_moment(packed, coarse)
    v4 = json.loads((REPO / 'research/source-assisted-v4/certificate.json').read_text())
    composed = pricing.assemble(v4['complex_profile'], packed, coarse)
    published = json.loads((BIT / 'certificate.json').read_text())['bit']['coarse']
    unpacked = pricing.assemble(v4['complex_profile'], row, dict(coarse_saving=Q(published['coarse_saving'])))
    need(unpacked['kappa_without_leaf'] == Q(6768823, 10**10), 'unpacked PR200 reproduces PR202')
    need(unpacked['kappa'] == Q(1693287, 2500000000), 'unpacked PR200 with the finite leaf reproduces PR199')
    need(composed['kappa'] > unpacked['kappa'], 'banks raise kappa over the leafed unpacked word')
    rejected = mutations(word, row, sinks, packed, starts)
    selector_calls = 18 * ((3 * packed['W_per_vertex'] - 1) + row['R'] * 72 * (charts['max_chart_factors'] + 71))
    need(selector_calls < 2**40, 'fixed chart routing calls stay a finite selector toll')
    kappa = composed['kappa']
    return dict(status='PASS conditional finite witness', kappa=kappa, kappa_decimal=float(kappa),
        kappa_without_leaf=composed['kappa_without_leaf'], binding=composed['binding'],
        gain_over_pr202=kappa / Q(6768823, 10**10) - 1, gain_over_pr194=kappa / Q(1668581, 2500000000) - 1,
        bit=dict(profile=packed, coarse=coarse, independent_moment_gap=gap, pr184=composed['bit'], leaf_chain=composed['leaf_chain'],
            unpacked=dict(R=row['R'], W_per_vertex=row['W_per_vertex'], rank_per_vertex=row['rank_per_vertex'], maxchild=row['maxchild'])),
        complex=dict(saving=composed['complex']['saving'], source='research/source-assisted-v4/certificate.json complex_profile'),
        assembly=dict(without_leaf=composed['without_leaf'], with_leaf=composed['with_leaf']),
        banks=dict(charts=charts, projector_checks=projectors, weighted_controls=weighted, schedule_diagnostic=schedule,
            fixed_selector_calls=selector_calls),
        controls=dict(unpacked_pr200_kappa_pr202=unpacked['kappa_without_leaf'], unpacked_pr200_kappa_pr199_leaf=unpacked['kappa']),
        terminal_word=terminal, references=refs, mutations_rejected=rejected,
        scope='Finite checks of the literal PR200 word, the completed bank endpoints, exact charts and paid moments; '
              'the bank schedule, weighted compiler, routing, stage cover and all-size transfer remain the conditional '
              'contracts of PR186, the round-8 supplement and PR184.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--full', action='store_true', help='Run PR200 verify.py first')
    parser.add_argument('--write', action='store_true', help='Authoring only: rewrite certificate.json')
    args = parser.parse_args()
    before = None if args.write else pins()
    if args.full:
        subprocess.run([sys.executable, '-B', str(BIT / 'verify.py')], check=True)
    result = json.loads(json.dumps(js(build()), sort_keys=True))
    target = HERE / 'certificate.json'
    if args.write:
        target.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(result == json.loads(target.read_text()), 'canonical certificate does not reproduce')
        need(pins() == before, 'source closure changed during verification')
    print('PASS pr200-entrance-banks kappa=%s (%.10e), bit binds; %d mutations rejected' % (result['kappa'], result['kappa_decimal'], len(result['mutations_rejected'])))


if __name__ == '__main__':
    main()
