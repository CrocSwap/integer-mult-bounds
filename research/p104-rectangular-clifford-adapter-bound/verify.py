"""Replay the exact #7161 rank-one tariff and rectangular adapter controls."""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys


WORD = 'peer/research/p104-rank8-exit-funded-split/WORD.json.gz'
RESULT = 'peer/research/p104-rank8-exit-funded-split/RESULT.json'
PINS = {
    WORD: 'c1caec11ca3ee264ef03018dd91037eac10c3e28950c4c525ee1b4bf5ee210e2',
    WORD + '#decompressed': '9eff91418d838f1ffa20fe5c5975dc2c43a79b32d501fcbe30b90c50a7b11ce3',
    RESULT: '59080d75e7281b1a8c1353930917fd15869ad747ff4200948898f78f11c14089',
    'caller/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'caller/interval_gate.py': '60a743d13f668ef86db4b8215b4d5d04430a671ba6f1fe06d9c1c4c3dfe86da5',
    'gaussian/clifford_exact.py': '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962',
    'gaussian/native_verify.py': '3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38',
    'prior/owned.py': '53da0a7b551b34f3baf633083a4362570ebe694a694e2d0b6226d01c08a6ab3b',
}


def checked(root, key):
    data = (root / key).read_bytes()
    if sha256(data).hexdigest() != PINS[key]:
        raise ValueError(f'changed exact input: {key}')
    return data


def unique_object(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def verify_source_map(root, source_map):
    declared = json.loads(source_map.read_text(), object_pairs_hook=unique_object)
    scientific = {key: digest for key, digest in PINS.items() if '#' not in key}
    notice = 'PEER-NOTICE.txt'
    assert declared.keys() == scientific.keys() | {notice}
    for key, digest in scientific.items():
        assert declared[key]['sha256'] == digest, key
    assert sha256((root/notice).read_bytes()).hexdigest() == declared[notice]['sha256']


def load(root, key):
    spec = spec_from_file_location('adapter_' + Path(key).stem, root / key)
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def verify_signed_map(word, compiler, gaussian):
    event = 535
    assert word['program'][event] == ['MOVE', 1479, 3, 595, False]
    assert word['frames'][3] == [] and word['frames'][595] == [52]
    reference = gaussian.adjoint(gaussian.frame([], 9)) + gaussian.frame([52], 9)
    a = compiler.canonical_frame(9, ())
    b = compiler.canonical_frame(9, (52,))
    recipe, _ = compiler.lower_child(a.adjoint().then(b))
    assert recipe['rank'] == 1
    actual = gaussian.recipe(recipe)
    changed = deepcopy(recipe)
    changed['left']['phase'] = (changed['left']['phase'] + 1) % 4
    mutant = gaussian.recipe(changed)
    signs = Counter()
    for column in range(512):
        sign = 1 - 2 * ((column & 20).bit_count() % 2)
        expected = ({column: (1, 1), column ^ 52: (sign, -sign)}, 1)
        assert gaussian.state(actual, column) == gaussian.state(reference, column) == expected
        assert gaussian.state(mutant, column) != expected
        signs[sign] += 1
    assert signs == {-1: 256, 1: 256}
    return dict(event=event, role=1479, source=3, target=595, shift=52, sign_mask=20,
                signed_columns=512, absolute_phase_mutants_rejected=512)


def multiply(left, right):
    a, b = left
    c, d = right
    return a*c - b*d, a*d + b*c


def numerators(gaussian, rank, column):
    values, denominator = gaussian.state(gaussian.fourier(rank), column)
    shift = rank - denominator
    assert shift >= 0
    return {i: (a << shift, b << shift) for i, (a, b) in values.items()}


def projection_controls(gaussian):
    results = []
    for width in range(1, 5):
        bank = 1 << width
        low = bank - 1
        diagonal = numerators(gaussian, width, 0)
        spectator_factor = diagonal[0]
        rejected = 0
        for lane in range(2):
            for column in range(bank):
                small = numerators(gaussian, width, lane*bank + column)
                large = numerators(gaussian, 2*width, lane*bank**2 + column)
                assert len(small) == bank and len(large) == bank**2
                assert all(a*a+b*b == bank for a,b in small.values())
                assert all(a*a+b*b == bank**2 for a,b in large.values())
                assert set(large) == set(range(lane*bank**2, (lane+1)*bank**2))
                projected = {lane*bank + (i & low): v
                             for i, v in large.items() if (i // bank) % bank == 0}
                assert projected == {i: multiply(v, spectator_factor) for i,v in small.items()}
                assert projected.keys() == small.keys()
                rejected += any(projected[i] != (a << width, b << width)
                                for i, (a, b) in small.items())
        assert rejected == 2*bank
        results.append(dict(width=width, signed_columns=2*bank, rank1_support=bank,
                            rank2_support=bank**2, omitted_reciprocal_rejected=rejected,
                            reciprocal_gain_squared=bank, padding_volume_factor=bank))
    return results


def pair_ceiling(word, caller, result, owned, gate):
    _, moves, _, census = owned.scan_word(word, lambda: None, 80000)
    signed, invoice = owned.full_invoice(word, caller, result, moves)
    target = owned.TARGET
    assert target == Fraction('0.0040075385047236')
    main = (set(word['live']) | {r+112 for r in word['live']}
            | set(word['hosted']['X2']) | set(word['hosted']['Y2']))
    assert 1479 not in main and 1479 < word['public']
    calls = [(i, e[1]) for i,e in enumerate(caller['events']) if e[0] == 'J']
    assert calls[:2] == [(43,1),(137,2)] and len(calls) == 17
    classes = Counter('main' if m['role'] in main else
                      'owned' if m['role'] >= word['public'] else 'public_helper'
                      for m in moves if m['rank'] == 1)
    repetitions = len(calls)
    ideal_pairs = sum(classes.values()) * repetitions // 2
    delta = gate.sub(gate.exact(2), gate.power(2, target))
    raw = gate.moment(signed, target)
    ideal = gate.add(raw, gate.smul(delta, ideal_pairs))
    assert delta[0] > 0 and raw[1] < 0 and ideal[0] > 0
    pairs_needed = (-raw[1] + delta[1] - 1) // delta[1]
    previous = gate.add(raw, gate.smul(delta, pairs_needed-1))
    first = gate.add(raw, gate.smul(delta, pairs_needed))
    assert previous[1] < 0 < first[0]
    # Deleting the rank-one debit from the literal paid list must fail invoice binding.
    try:
        owned.full_invoice(word, caller, result, [m for m in moves if m['event'] != 535])
    except AssertionError:
        pass
    else:
        raise AssertionError('omitted paid occurrence accepted')
    return dict(census=census, invoice=invoice, rank1_native_by_owner_class=classes,
                rank1_outer_paid=invoice['P'][1] - sum(classes.values()) * repetitions,
                native_call_bindings=[{'caller_event': i, 'stage': j,
                                       'helper_owner': ['helper', i, 1479]} for i,j in calls],
                pair_price_saving=gate.show(delta), signed_raw_moment=gate.show(raw),
                ideal_pairs=ideal_pairs, ideal_raw_moment=gate.show(ideal),
                minimum_ideal_pairs_needed=pairs_needed, omitted_paid_occurrence_rejected=True)


def run(root):
    payload = {key: checked(root, key) for key in PINS if '#' not in key}
    raw = gzip.decompress(payload[WORD])
    assert sha256(raw).hexdigest() == PINS[WORD+'#decompressed']
    word, result, caller = (json.loads(p) for p in (raw, payload[RESULT], payload['caller/CALLER.json']))
    compiler = load(root, 'gaussian/clifford_exact.py')
    gaussian = load(root, 'gaussian/native_verify.py')
    owned = load(root, 'prior/owned.py')
    gate = load(root, 'caller/interval_gate.py')
    return dict(status='SCOPED_RECTANGULAR_ADAPTER_OBSTRUCTION',
                pins=PINS, target=str(owned.TARGET), seed=None,
                exact_signed_move=verify_signed_map(word,compiler,gaussian),
                destructive_projection_controls=projection_controls(gaussian),
                complete_pair_price=pair_ceiling(word,caller,result,owned,gate))


if __name__ == '__main__':
    if not __debug__ or sys.implementation.name != 'cpython' or sys.version_info[:2] != (3,12):
        raise SystemExit('Use CPython 3.12 with assertions enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inputs', type=Path)
    parser.add_argument('--expected', type=Path)
    parser.add_argument('--source-map', type=Path)
    args = parser.parse_args()
    if args.source_map is not None:
        verify_source_map(args.inputs, args.source_map)
    receipt = json.dumps(run(args.inputs), indent=2, sort_keys=True) + '\n'
    if args.expected is not None:
        if args.expected.read_bytes() != receipt.encode():
            raise ValueError('changed frozen adapter receipt')
        print('PASS_P104_RECTANGULAR_CLIFFORD_ADAPTER_BOUND')
    else:
        print(receipt, end='')
