#!/usr/bin/env python3
"""Finite tape primitives and exact production-height guards; no large rank allocation."""

from pathlib import Path
from fractions import Fraction
import json
import sys

SOURCE = (Path(sys.argv[1]).resolve() if len(sys.argv) > 1
          else Path(__file__).resolve().parent.parent / 'last-tick')
sys.path.insert(0, str(SOURCE))
from upstream import install

install()
from positive import power_le
from check_epoch_reentry import trial as epoch_trial
from strong_binary import native_word
from calibration import LAST_TICK, COMPLEX_C
from outer_budget import margins


class Tape:
    """One transition per read, write or unit head movement on a finite alphabet."""

    def __init__(self, cells, head=0):
        self.cells = list(cells) + ['_']
        self.head = head
        self.steps = 0

    def read(self):
        self.steps += 1
        return self.cells[self.head]

    def write(self, value):
        self.steps += 1
        self.cells[self.head] = value

    def move(self, delta):
        assert delta in (-1, 1)
        self.steps += 1
        self.head += delta
        assert self.head >= 0
        if self.head == len(self.cells):
            self.cells.append('_')


def home(tape):
    while tape.read() != '<':
        tape.move(-1)
    tape.move(1)


def nonzero(tape):
    while True:
        bit = tape.read()
        if bit in ('1', '#'):
            home(tape)
            return bit == '1'
        assert bit == '0'
        tape.move(1)


def decrement(tape):
    while tape.read() == '0':
        tape.write('1')
        tape.move(1)
    assert tape.read() == '1'
    tape.write('0')
    home(tape)


def rank_on_tapes(h):
    """From binary h on a counter tape, write binary 2**h on another tape."""
    bits = list(reversed(format(h, 'b')))
    counter = Tape(['<', *bits, '#'], head=1)
    rank = Tape([])
    rank.write('1')
    rank.move(1)
    while nonzero(counter):
        decrement(counter)
        rank.write('0')
        rank.move(1)
    word = ''.join(rank.cells[:rank.head])
    steps = counter.steps + rank.steps
    # The bound deliberately includes all tests, failed scans, and head returns.
    bound = 20 * (h + 1) * (len(bits) + 2)
    assert steps <= bound, (h, steps, bound)
    assert word == '1' + '0' * h
    return len(word), steps, bound


def count_power_le(base, power, ceiling):
    """Mirror the source loop while bounding each actual untruncated product."""
    value, products, max_temporary = 1, 0, 0
    assert 0 <= base <= ceiling and power > 0
    while power:
        if power & 1:
            value *= base
            products += 1
            max_temporary = max(max_temporary, value)
            assert value <= (ceiling + 1) ** 2
            if value > ceiling:
                return False, products, max_temporary
        power //= 2
        if power:
            square = base * base
            products += 1
            max_temporary = max(max_temporary, square)
            assert square <= (ceiling + 1) ** 2
            base = min(ceiling + 1, square)
    return True, products, max_temporary


def controls():
    rank_receipts = {str(h): rank_on_tapes(h) for h in range(0, 129)}
    for base in range(1, 18):
        for d in range(2, 19):
            border = base ** d
            for h in sorted({base, max(base, border - 1), max(base, border), max(base, border + 1)}):
                got, count, _ = count_power_le(base, d, h)
                assert got == (base ** d <= h) == power_le(base, d, h)
                assert count <= d.bit_length() - 1 + d.bit_count()
    d = 10**21
    assert (d.bit_length(), d.bit_count()) == (70, 29)
    stop = []
    for base, h in ((1, 2**64), (2, 2**4096), (17, 2**256), (2, 2)):
        got, count, temporary = count_power_le(base, d, h)
        assert got == power_le(base, d, h)
        stop.append({'base': base, 'h_bits': h.bit_length(), 'result': got,
                     'products': count, 'max_temporary_bits': temporary.bit_length()})
    epoch = epoch_trial()
    return {
        'rank_cases': len(rank_receipts),
        'sample_rank_cases': {k: rank_receipts[k] for k in ('0', '1', '16', '64', '128')},
        'stop_cases_d_2_to_18': 17 * 17,
        'D': d,
        'D_bits': d.bit_length(), 'D_set_bits': d.bit_count(), 'max_products': 98,
        'large_D_controls': stop,
        'nested_epoch': list(epoch),
    }


def guards():
    v, Hs = 430, [10**21 * 4**i for i in range(6)]
    assert 5**13 > 16 * 4**13 and 15**v >= 2 * 12**v
    assert 18_906**v + 104_904**v + 23_800**v < 2**(18*v)
    assert 18 * (Fraction(13, 4) + Fraction(1, 512)) < 60
    assert 512 * v <= min(Hs)
    word = native_word(v)
    targets15 = [i for i, port in enumerate(word.targets) if port.rank == 15]
    paid56 = next(i for i, port in enumerate(word.paid) if port.rank == 56)
    assert len(targets15) == 444
    assert word.target((targets15[0],) * v).rank == 15**v
    assert next(word.blocks((paid56,) * v)).rank == 12**v
    assert 134**v < 2**(8*v)
    assert (Fraction(5, 4)**v) < 2**v
    actual_g_floor = (Hs[-1] - 2 - 8*v)//v
    assert actual_g_floor == 2381395348837209302317
    assert actual_g_floor > 258*((1 << 63) - 1)
    checks = []
    for h in Hs:
        g = (13*h + 4*v - 1)//(4*v) + 2
        q = (10000*(2*h + 64) + 9961 - 1)//9961
        old = (25000*(2*h + 64) + 24903 - 1)//24903
        assert 9961*q >= 10000*(2*h + 64) and q < 3*h < 8*h
        assert q > old and g <= 4*(h + 1)
        construction = 20*(h+1)*(h.bit_length()+2)
        assert construction.bit_length() < h
        checks.append({'H': h, 'H_bits': h.bit_length(), 'G_plus_1_upper': g,
                       'G_bound_bits': g.bit_length(), 'quotient_log': q,
                       'old_quotient_understatement': q-old,
                       'binary_rank_writer_transitions_upper': construction})
    nodes = 64 + v.bit_length() + 30*v
    local = 4*nodes + 8*max(Hs).bit_length() + 512
    qnative = 1 << local.bit_length()
    slot = 19 + 2*nodes + checks[-1]['G_bound_bits']
    assert (nodes, slot, local, qnative) == (12973, 26038, 53044, 65536)
    assert slot < local < qnative
    return {'v': v, 'minimum_target_witness': '15^430', 'maximum_paid_witness': '12^430',
            'all_15_labels': len(targets15), 'largest_actual_G_strict_lower': actual_g_floor,
            'ranks': checks, 'nodes_log_upper': nodes, 'slot_log_upper': slot,
            'local_log_upper': local, 'qnative': qnative}


def signed_guard():
    p = LAST_TICK
    D = p.positive_stop_denominator
    strict, functional, positive = margins(
        p.kappa, Fraction(1, D), p.ordinary, COMPLEX_C - Fraction(10, p.complex_log)
    )
    all_margins = strict + functional + [positive]
    assert len(strict) == 54 and len(functional) == 4
    assert min(all_margins) == Fraction(1, 10 * D)
    assert all(D**2 % x.denominator == 0 for x in all_margins)
    assert all(x > 0 for x in all_margins)
    scaled_bits = max(abs(int(x * D**2)).bit_length() for x in all_margins)
    assert scaled_bits == 181 and scaled_bits < 186
    assert p.kappa * D == 3890115286594445000
    assert p.ordinary * D == 3890115286594445005
    return {'common_denominator': D**2, 'common_denominator_bits': (D**2).bit_length(),
            'kappa_numerator_over_D': int(p.kappa * D),
            'ordinary_numerator_over_D': int(p.ordinary * D),
            'strict': len(strict), 'functional': len(functional),
            'min_margin': str(min(all_margins)), 'max_scaled_numerator_bits': scaled_bits}


if __name__ == '__main__':
    result = {'finite_controls': controls(), 'exact_guards': guards(), 'signed_guards': signed_guard()}
    print(json.dumps(result, indent=2))
    print('PASS_TAPE_BRIDGE_SMALL_CONTROLS_AND_EXACT_GUARDS')
