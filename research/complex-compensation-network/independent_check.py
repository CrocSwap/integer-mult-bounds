#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate integer-dyadic primitive replay. Imports no package/native code.
conorholds, with substantial OpenAI Codex assistance; no human review.
"""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def check(ok, message):
    if not ok:
        raise RuntimeError(message)


def decode(path):
    def unique(items):
        result = {}
        for key, value in items:
            check(key not in result, 'duplicate input field')
            result[key] = value
        return result
    raw = path.read_bytes()
    if path.suffix == '.gz':
        raw = gzip.decompress(raw)
    return json.loads(raw, object_pairs_hook=unique)


class IntegerRows:
    def __init__(self, size):
        self.data = [{i: 1} for i in range(size)]
        self.den = [0]*size
        self.norm = [Fraction(1) for _ in range(size)]
        self.peak = Fraction(1)
        self.real_count = 0
        self.max_denominator_power = 0

    def reduce(self, row):
        values = self.data[row]
        if not values:
            self.den[row] = 0
            return
        p = self.den[row]
        for value in values.values():
            p = min(p, (abs(value) & -abs(value)).bit_length()-1)
            if not p:
                break
        if p:
            self.data[row] = {key: value >> p for key, value in values.items()}
            self.den[row] -= p

    def mark(self, row):
        self.real_count += 2
        self.peak = max(self.peak, self.norm[row])
        self.max_denominator_power = max(self.max_denominator_power, self.den[row])

    def clear(self, row):
        self.data[row] = {}; self.den[row] = 0; self.norm[row] = Fraction(0)
        self.mark(row)

    def copy(self, target, source):
        check(target != source, 'aliased primitive copy')
        self.data[target] = self.data[source].copy(); self.den[target] = self.den[source]
        self.norm[target] = self.norm[source]; self.mark(target)

    def accumulate(self, target, source, sign=1):
        check(target != source and sign in (-1, 1), 'primitive alias/sign')
        power = max(self.den[target], self.den[source])
        left_shift = power-self.den[target]; right_shift = power-self.den[source]
        result = {key: value << left_shift for key, value in self.data[target].items()}
        for key, value in self.data[source].items():
            value = result.get(key, 0) + sign*(value << right_shift)
            if value:
                result[key] = value
            else:
                result.pop(key, None)
        self.data[target] = result; self.den[target] = power; self.reduce(target)
        self.norm[target] += self.norm[source]; self.mark(target)

    def double(self, row):
        if self.den[row]:
            self.den[row] -= 1
        else:
            self.data[row] = {key: 2*value for key, value in self.data[row].items()}
        self.norm[row] *= 2; self.mark(row)

    def halve(self, row):
        self.den[row] += 1; self.reduce(row)
        self.norm[row] /= 2; self.mark(row)

    def negate(self, row):
        self.data[row] = {key: -value for key, value in self.data[row].items()}
        self.mark(row)

    def horner(self, target, source, numerator, denominator, work, omit_first=False, omit_last=False, wrong_sign=False,
               copy_unit=False):
        check(target != source and work not in (target, source), 'coefficient work alias')
        q = Fraction(numerator, denominator)
        check(q != 0 and q.denominator & (q.denominator-1) == 0, 'dyadic coefficient')
        if copy_unit and abs(q) == 1:
            self.accumulate(target, source, 1 if q > 0 else -1)
            self.clear(work)
            return
        if copy_unit:
            self.copy(work, source)
        if not omit_first:
            if not copy_unit:
                self.clear(work)
        value = abs(q.numerator)
        for i in range(value.bit_length()-1, -1, -1):
            if i < value.bit_length()-1:
                self.double(work)
            if value & (1 << i) and not (copy_unit and i == value.bit_length()-1):
                self.accumulate(work, source)
        for _ in range(q.denominator.bit_length()-1):
            self.halve(work)
        sign = 1 if q > 0 else -1
        self.accumulate(target, work, -sign if wrong_sign else sign)
        if not omit_last:
            self.clear(work)


def role(value, logical, centres):
    check(isinstance(value, list) and len(value) == 2 and type(value[1]) is int, 'native register shape')
    tag, index = value
    if tag == 'L':
        check(0 <= index < logical, 'logical register range')
        return index
    check(tag == 'C' and 0 <= index < centres, 'private centre range')
    return logical+index


def replay(events, word, backward, copy_unit=False):
    n = 2*word['v'] + word['R']; centres = len(word['centers']); work = n+centres
    state = IntegerRows(work+1); macros = 0; paid = Counter()
    for event in events:
        tag = event[0]
        if tag in ('climb', 'center'):
            rank = event[5] if tag == 'climb' else event[4]
            check(type(rank) is int and rank > 0, 'recursive rank')
            paid[rank] += 1
        elif tag == 'scalar':
            macros += 1; gate = event[1]; op = gate[0]; target = role(gate[1], n, centres)
            if op == 'clear':
                state.clear(target)
            elif op == 'copy':
                state.copy(target, role(gate[2], n, centres))
            elif op == 'add':
                state.horner(target, role(gate[2], n, centres), gate[3], gate[4], work, copy_unit=copy_unit)
            else:
                check(op == 'scale', 'scalar opcode')
                q = Fraction(gate[2], gate[3]); a, b = abs(q.numerator), q.denominator
                check(a and not a & (a-1) and not b & (b-1), 'scale alphabet')
                power = a.bit_length()-b.bit_length()
                for _ in range(abs(power)):
                    (state.double if power >= 0 else state.halve)(target)
                if q < 0:
                    state.negate(target)
        else:
            check(tag in ('phase', 'adapter', 'residual_adapter'), 'event opcode')
    for row in range(n):
        wanted = {row: 1}
        if backward and row < word['v']:
            wanted[word['v']+row] = -1
        elif not backward and word['v'] <= row < 2*word['v']:
            wanted[row-word['v']] = 1
        check(state.den[row] == 0 and state.data[row] == wanted, 'full primitive endpoint: ' + str(row))
    check(all(not state.data[i] for i in range(n, work+1)), 'private input leaks or uncleared work')
    check(dict(paid) == {int(k): v for k, v in word['local_profile'].items()}, 'primitive paid profile')
    check(state.peak < 2**192, 'literal positive-prefix bound')
    return dict(input_columns=work+1, scalar_macros=macros, real_primitives=state.real_count,
                prefix_l1_upper=str(state.peak), maximum_reduced_denominator_power=state.max_denominator_power,
                all_dirty_helpers_restored=word['R'], private_inputs_erased=centres+1)


def make_event(gate, backward, expected_frame=0):
    if gate[0] == 'add':
        _, target, source, num, den, frame = gate
        if backward:
            target, source, num = source, target, -num
        result = ['add', ['L', target], ['L', source], num, den]
    else:
        _, target, num, den, frame = gate
        if backward:
            num, den = den, num
        result = ['scale', ['L', target], num, den]
    check(frame == expected_frame, 'literal boundary frame')
    return ['scalar', result, frame]


def work_controls():
    controls = []
    for name, flags in [('uncleared_incoming_work', {'omit_first': True}),
                        ('uncleared_final_work', {'omit_last': True}),
                        ('wrong_primitive_sign', {'wrong_sign': True})]:
        fixture = IntegerRows(3)
        fixture.horner(1, 0, -3, 4, 2, **flags)
        wanted = {0: -3, 1: 4}
        check(fixture.data[1] != wanted or fixture.den[1] != 2 or fixture.data[2], 'accepted work control')
        controls.append(name)
    fixture = IntegerRows(3); fixture.horner(1, 0, -3, 4, 2)
    check(fixture.data[0] == {0: 1} and fixture.data[1] == {0: -3, 1: 4}
          and fixture.den[1] == 2 and not fixture.data[2] and fixture.real_count == 16,
          'signed nonunit Horner fixture')
    for numerator, denominator, expected_count in [(1, 1, 4), (-1, 1, 4), (-3, 4, 14), (1, 2, 8)]:
        fixture = IntegerRows(3); fixture.horner(1, 0, numerator, denominator, 2, copy_unit=True)
        expected = Fraction(numerator, denominator)
        result = {key: Fraction(value, 1 << fixture.den[1]) for key, value in fixture.data[1].items()}
        check(result == {0: expected, 1: Fraction(1)} and not fixture.data[2] and
              fixture.real_count == expected_count, 'copy/unit arbitrary-work fixture')
    return controls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='write a fresh receipt')
    args = parser.parse_args()
    pins = decode(BASE / 'REFERENCE-PINS.json')
    for filename, digest in pins.items():
        check(hashlib.sha256((BASE / 'reference' / filename).read_bytes()).hexdigest() == digest, 'independent source hash')
    word = decode(BASE / 'reference/CANONICAL-WORD.json.gz')
    programs = decode(BASE / 'reference/LOCAL-PROGRAMS.json.gz')
    baseline_checks = decode(BASE / 'reference/LOCAL-CHECKS.json')
    baseline_replay = decode(BASE / 'reference/INDEPENDENT-LOCAL-REPLAY.json')
    replacement = decode(BASE / 'COMPENSATION.json'); cleanup = decode(BASE / 'CLEANUP.json')
    forest = decode(BASE / 'FOREST-COMPENSATION.json'); published_cleanup = decode(BASE / 'PR1119-CLEANUP.json')
    certificate = decode(BASE / 'CERTIFICATE.json')
    comparison = decode(BASE / 'COMPARISON-SOURCES.json')
    published_raw = (BASE / 'comparators/pr1979/PROGRAMS.json.gz').read_bytes()
    check(hashlib.sha256(published_raw).hexdigest() == comparison['programs_sha256'], 'independent comparison stream hash')
    published = decode(BASE / 'comparators/pr1979/PROGRAMS.json.gz')
    expected_path = BASE / 'comparators/pr1979/EXPECTED.json'
    check(hashlib.sha256(expected_path.read_bytes()).hexdigest() == comparison['files']['EXPECTED.json']['sha256'],
          'independent published invoice hash')
    published_invoice = decode(expected_path)
    changed = dict(word); changed['compensation'] = replacement
    changed['cleanup'] = cleanup
    payload = json.dumps(changed, sort_keys=True, separators=(',', ':')).encode()
    check(hashlib.sha256(payload).hexdigest() == certificate['native']['candidate_word_payload_sha256'], 'independent literal word binding')
    receipts = {}
    for orientation in ('forward', 'backward'):
        backward = orientation == 'backward'; old = programs[orientation]
        end = old.index(['phase', 'entry_adapters'])
        expected = [['phase', 'zero_frame_precondition']] + [make_event(g, backward) for g in word['precondition']+word['compensation']]
        check(old[:end] == expected, 'independent original boundary')
        new = [['phase', 'zero_frame_precondition']] + [make_event(g, backward) for g in word['precondition']+replacement] + old[end:]
        start = new.index(['phase', 'full_frame_cleanup'])+1; finish = start+len(word['cleanup'])
        check(new[start:finish] == [make_event(g, backward, 1) for g in word['cleanup']], 'independent original cleanup')
        new[start:finish] = [make_event(g, backward, 1) for g in cleanup]
        check([e for e in old if e[0] != 'scalar'] == [e for e in new if e[0] != 'scalar'], 'independent non-scalar change')
        digest = hashlib.sha256(json.dumps(new, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        check(digest == certificate['native']['orientations'][orientation]['program_sha256'], 'independent full stream binding')
        for name, events in [('baseline', old), ('candidate', new)]:
            result = replay(events, word, backward)
            if name == 'baseline':
                expected_real = baseline_checks[orientation]['real_component_primitive_bound']
                expected_macros = baseline_checks[orientation]['scalar_macros']
                expected_peak = baseline_replay['local'][orientation]['prefix_l1_upper']
            else:
                prior = certificate['native']['orientations'][orientation]
                expected_real, expected_macros, expected_peak = prior['after_real'], prior['after_macros'], prior['prefix_l1_upper']
            check((result['real_primitives'], result['scalar_macros'], result['prefix_l1_upper']) ==
                  (expected_real, expected_macros, expected_peak), 'independent full charges or precision')
            receipts[name+'_'+orientation] = result
            print('PASS independent literal primitives ' + name + ' ' + orientation, flush=True)
            modern = replay(events, word, backward, copy_unit=True)
            units = additions = 0
            for event in events:
                if event[0] == 'scalar' and event[1][0] == 'add':
                    additions += 1
                    units += int(abs(Fraction(event[1][3], event[1][4])) == 1)
            check(modern['real_primitives'] == result['real_primitives']-2*additions-2*units,
                  'copy/unit exact literal count versus independent tariff')
            receipts[name+'_copy_unit_'+orientation] = modern
            print('PASS independent copy/unit primitives ' + name + ' ' + orientation, flush=True)
        for name, panel, restoration in [('forest_current_cleanup', forest, cleanup),
                                         ('forest_published_cleanup', forest, published_cleanup),
                                         ('nonforest_published_cleanup', replacement, published_cleanup)]:
            matched = [['phase', 'zero_frame_precondition']] + [make_event(g, backward)
                       for g in word['precondition']+panel] + old[end:]
            start = matched.index(['phase', 'full_frame_cleanup'])+1
            matched[start:start+len(word['cleanup'])] = [make_event(g, backward, 1) for g in restoration]
            check([e for e in matched if e[0] != 'scalar'] == [e for e in old if e[0] != 'scalar'],
                  'independent matched-method non-scalar stream')
            digest = hashlib.sha256(json.dumps(matched, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
            prior = certificate['matched_method_comparison']['programs'][name][orientation]
            check(digest == prior['program_sha256'], 'independent matched-method stream binding')
            for modern in (False, True):
                result = replay(matched, word, backward, copy_unit=modern)
                check(result['real_primitives'] == prior['copy_unit_real' if modern else 'horner_real'] and
                      result['scalar_macros'] == prior['macros'], 'independent matched-method invoice')
                receipts[name+('_copy_unit_' if modern else '_')+orientation] = result
                print('PASS independent matched methods '+name+' '+orientation+' copy_unit='+str(modern), flush=True)
        events = published[orientation]
        check([e for e in events if e[0] != 'scalar'] == [e for e in old if e[0] != 'scalar'],
              'independent comparison non-scalar stream')
        digest = hashlib.sha256(json.dumps(events, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        prior = certificate['merged_gauge_comparison']['orientations'][orientation]
        check(digest == prior['published_program_sha256'], 'independent comparison full stream binding')
        result = replay(events, word, backward, copy_unit=True)
        invoice = published_invoice['orientations'][orientation]['all19_invoice']
        check(result['real_primitives'] == invoice['complex_primitives'] == prior['published_real'] and
              result['real_primitives']-receipts['candidate_copy_unit_'+orientation]['real_primitives'] == prior['saving_real'] and
              result['prefix_l1_upper'] == invoice['prefix_l1'], 'independent published gauge comparison')
        receipts['pr1979_copy_unit_'+orientation] = result
        print('PASS independent copy/unit primitives PR1979 ' + orientation, flush=True)
    controls = work_controls()
    out = dict(status='PASS_INDEPENDENT_INTEGER_DYADIC_NETWORK', programs=receipts,
               primitive_controls=controls, copy_unit_lowering_credit='Sagar Thakrar, PR696',
               imports_primary_or_native_code=False, frame_and_adapter_checks='Upstream native auditor only',
               selected_kappa_unchanged=True)
    if args.out:
        with args.out.open('x') as stream:
            stream.write(json.dumps(out, indent=2, sort_keys=True)+'\n')
    else:
        check(out == decode(BASE / 'INDEPENDENT.json'), 'recorded independent receipt mismatch')
    print(json.dumps(out, sort_keys=True))


if __name__ == '__main__':
    main()
