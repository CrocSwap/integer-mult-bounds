#!/usr/bin/env python3
"""Source-bound same-contract replay of the peer MOVE retiming after #7003.

Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
"""
from argparse import ArgumentParser
from collections import Counter
from copy import deepcopy
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREVIOUS = HERE.parent / 'shared-wire-stop-fusion'
VENDOR = HERE.parent / 'shared-wire-split-composition'
EXPORT_SHA = 'd8539c9f4d7625bb9f3d2f6f5603cda407696dda73f7d36f6bf6677b55c5e8ac'
EXPECTED_WORD = '311069e5faeef999a0b3f2fd8ae9c256b67b40a368998c5c31cd38a500f385e3'
LOCAL_DELTA = {1: -1, 4: -1, 5: 1}
if not __debug__:
    raise RuntimeError('Run without -O; assertions are proof checks.')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj
    spec.loader.exec_module(obj)
    return obj


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw)


def authenticate():
    # The local replay commit and published #7003 have the same Git tree.
    # This manifest authenticates the exported proof-relevant files in that tree.
    raw = (HERE / 'BASELINE-EXPORT.json').read_bytes()
    assert sha256(raw).hexdigest() == EXPORT_SHA
    sources = json.loads(raw)
    assert sources['commit'] == '300d26d0c03830af44785318e359965f4ef3b432'
    for item in sources['files']:
        path = ROOT / item['path']
        assert path.resolve().is_relative_to(ROOT)
        contents = path.read_bytes()
        assert len(contents) == item['size'] and sha256(contents).hexdigest() == item['sha256'], path


def signed_delta(after, before):
    out = Counter(after)
    out.subtract(before)
    return {r: n for r, n in sorted(out.items()) if n}


def chart_replay(word):
    c = load('peer_clifford', VENDOR / 'frozen/clifford_exact.py')
    v = load('peer_native', VENDOR / 'frozen/native_verify.py')
    a, b = 3, 1048
    frames = word['frames']
    ca, cb = (c.canonical_frame(9, tuple(frames[i])) for i in (a, b))
    recipe, _ = c.lower_child(ca.adjoint().then(cb))
    expected = v.adjoint(v.frame(frames[a], 9)) + v.frame(frames[b], 9)
    actual = v.recipe(recipe)
    assert recipe['rank'] == 5
    v.equal(actual, expected, 'Exact signed Pauli and phase')
    for column in range(512):
        assert v.state(actual, column) == v.state(expected, column), column
    broken = deepcopy(recipe)
    broken['left']['phase'] = (broken['left']['phase'] + 1) % 4
    try:
        v.equal(v.recipe(broken), expected, 'Wrong absolute phase')
    except ValueError:
        pass
    else:
        raise AssertionError('Wrong phase accepted')
    return {'pair': [a, b], 'rank': 5, 'exact_columns': 512, 'wrong_phase_rejected': True}


def price_audit(previous, baseline, invoice, source_gate):
    primary = load('peer_primary_price', VENDOR / 'interval_gate.py')
    audit = load('peer_independent_price', PREVIOUS / 'audit_price.py')
    old_lo, old_hi = source_gate['raw_bracket']
    gate, gain = previous.certify_price(primary, baseline, invoice, {
        'raw_lower': old_lo, 'raw_upper': old_hi,
        'numeric_BIT_price': source_gate['BIT_pin'], 'claim': source_gate['claim'],
    })
    intervals = {}
    diagnostics = {}
    for label, row in [('baseline', baseline), ('candidate', invoice)]:
        hist = Counter(row['T'])
        hist.subtract(row['P'])
        diagnostic, interval, _ = audit.crossing(hist)
        diagnostics[label] = diagnostic
        intervals[label] = interval
    claim = Q(gate['claim'])
    assert intervals['baseline'][1] < claim < intervals['candidate'][0]
    baseline_hist = Counter(baseline['T'])
    baseline_hist.subtract(baseline['P'])
    assert audit.raw_margin(baseline_hist, claim)[1] < 0
    with localcontext() as ctx:
        ctx.prec = 75
        show = lambda v: str(Decimal(v.numerator) / Decimal(v.denominator))
        bounds = {label: [show(v) for v in interval] for label, interval in intervals.items()}
        exact_claim = show(claim)
        exact_gain = show(Q(gain['claim_gain']))
    return gate, gain, {'crossing_intervals': bounds, 'diagnostic_crossings': diagnostics,
                        'claim_decimal': exact_claim, 'gain_decimal': exact_gain,
                        'baseline_rejects_new_claim': True}


def command(*args):
    subprocess.run([sys.executable, '-I', '-B', *map(str, args)], check=True)


def certify():
    authenticate()
    source_builder = load('peer_source_build', PREVIOUS / 'build_candidate.py')
    previous = load('peer_source_verify', PREVIOUS / 'verify.py')
    audit = load('peer_source_audit', PREVIOUS / 'audit_native.py')
    build = load('peer_build', HERE / 'build_candidate.py')
    independent = load('peer_independent', VENDOR / 'independent.py')
    precision = load('peer_precision', VENDOR / 'precision_replay.py')
    previous.authenticate()
    old = read(VENDOR / 'data/final.json.gz')
    spaces = [source_builder.span(basis) for basis in old['frames']]
    history, _, _ = source_builder.inventory(old, spaces)
    baseline, _, _ = source_builder.place(old, read(PREVIOUS / 'EDITS.json'), spaces, history)
    source_result = read(PREVIOUS / 'RESULT.json')
    assert sha256(build.canonical(baseline)).hexdigest() == build.SOURCE_SHA == source_result['candidate_canonical_sha256']
    word, tagged, checked = build.edit(baseline)
    raw = build.canonical(word)
    assert sha256(raw).hexdigest() == EXPECTED_WORD
    # The literal same-contract motion type and chart map already appear in #7003.
    assert ['MOVE', 671, 3, 1048, False] in baseline['program']
    old_replay, old_grid = audit.replay(baseline, list(enumerate(baseline['program'])), checked)
    new_replay, new_grid = audit.replay(word, tagged, checked)
    assert old_replay == new_replay, 'All endpoints, shifted ADD source rows and owned traces agree'
    assert all(old_grid[k] == new_grid[k] for k in old_grid.keys() - {'opcodes', 'paid'})
    assert new_grid['odd_grid_lcm'] == 1125 and new_grid['owned_peak'] == 43
    assert signed_delta(new_grid['opcodes'], old_grid['opcodes']) == {'MOVE': -1}
    assert signed_delta(new_grid['paid'], old_grid['paid']) == LOCAL_DELTA
    assert signed_delta(build.histogram(word), build.histogram(baseline)) == LOCAL_DELTA
    old_native = independent.native(baseline)
    native = independent.native(word)
    assert not old_native['bad_inputs'] and not native['bad_inputs']
    assert all(old_native[k] == native[k] for k in old_native.keys() - {'events', 'paid'})
    assert old_native['events'] - native['events'] == 1
    assert signed_delta(native['paid'], old_native['paid']) == LOCAL_DELTA
    moved_at = next(i for i, (original, _) in enumerate(tagged) if original == build.ADD)
    assert independent.native(word, mutant=moved_at)['bad_inputs'], 'Changed scalar rejected'

    caller = read(VENDOR / 'data/caller.json')
    manifest = read(VENDOR / 'INDEPENDENT-SOURCES.json')
    previous.bit_binding(independent, manifest)
    caller_audit = independent.caller(caller)
    assert not caller_audit['bad_outputs'] and caller_audit == source_result['caller']
    old_invoice = independent.invoices(baseline, caller, old_native)
    invoice = independent.invoices(word, caller, native)
    for key in ('T', 'P'):
        assert {str(r): n for r, n in old_invoice[key].items()} == source_result['invoice'][key]
    assert old_invoice['T'] == invoice['T'] and old_invoice['S'] == invoice['S'] == 1520
    assert old_invoice['empty_root_credits'] == invoice['empty_root_credits'] == 0
    complete_delta = {r: 18 * n for r, n in LOCAL_DELTA.items()}
    assert signed_delta(invoice['P'], old_invoice['P']) == complete_delta
    old_ordinary = independent.ordinary(baseline, caller, old_native)
    ordinary = independent.ordinary(word, caller, native)
    assert old_ordinary == source_result['ordinary']
    assert ordinary['conservative_total'] == old_ordinary['conservative_total'] - 18000 < 10**9
    gate, gain, price = price_audit(previous, old_invoice, invoice, source_result['gate'])
    precision_result = precision.run(word, caller, gate, manifest)
    chart = chart_replay(word)

    with TemporaryDirectory(prefix='p104-peer-move-') as temporary:
        path = Path(temporary) / 'word.json.gz'
        path.write_bytes(gzip.compress(raw, mtime=0))
        command(VENDOR / 'frozen/verify_host3_odd.py', path, '1125')
        command(VENDOR / 'frozen/physical.py', path, VENDOR / 'frozen/clifford_exact.py', '1000000009', '11')

    return {'status': 'PASS_PEER_MOVE_RETIMING', 'source_head': build.SOURCE_HEAD,
            'candidate_canonical_sha256': EXPECTED_WORD, 'local_paid_delta': LOCAL_DELTA,
            'complete_paid_delta': complete_delta, 'scalar_source_versions': sorted(checked),
            'native': native, 'grid': new_grid, 'chart': chart, 'caller': caller_audit,
            'invoice': invoice, 'ordinary': ordinary, 'gate': gate, 'gain': gain,
            'independent_price': price, 'precision': precision_result,
            'controls': {'changed_scalar_rejected': True, 'old_invoice_rejects_claim': True,
                         'changed_phase_rejected': True, 'insufficient_grid_rejected': True}}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='Generate a fresh receipt at this unused path')
    args = parser.parse_args()
    result = certify()
    encoded = json.dumps(result, indent=2) + '\n'
    if args.out:
        with args.out.open('x') as stream:
            stream.write(encoded)
    else:
        assert json.loads(encoded) == read(HERE / 'RESULT.json'), 'Frozen replay receipt differs'
    print(result['status'], result['independent_price']['claim_decimal'], result['independent_price']['gain_decimal'])


if __name__ == '__main__':
    main()
