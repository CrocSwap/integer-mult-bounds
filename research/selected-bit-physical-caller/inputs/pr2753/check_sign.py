"""Independent address/permutation and physical-head test for linear sign."""
from hashlib import sha256
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bootstrap
from cardinal_counts import Count
from check_support import Origins, audit, bits, no_decode
from words import Arena, Ring, Word

import linear_sign as candidate


def control_scaling():
    """Meter actual control tapes on complete fibres with B=S=1.

    These are finite measurements, not a substitute for the loop charge.
    The separate 3B setup invariant detects the old padded-counter issue.
    """
    rows = []
    def traffic(meter): return meter.reads + meter.writes + meter.moves
    for modulus in (3,9,27,81,243):
        arena=Arena(modulus.bit_length()+1);m=arena.input(modulus);ring=Ring(m)
        one=Count.literal(1);before=one.marginal();suffix=one.marginal();one.close()
        origins=Origins();source=origins.source(modulus)
        counters=[];original_counter=candidate.Counter;original_tape=candidate.Tape
        def observed(value):
            result=original_counter(value);counters.append(result);return result
        candidate.Counter=observed;candidate.Tape=origins.factory
        meters=(arena.meter,before.tape.meter,suffix.tape.meter)
        started=sum(map(traffic,meters))
        try:
            with no_decode():output=candidate.sign_address(source,ring,3,before,suffix)
            steps=sum(map(traffic,meters))-started+sum(traffic(counter.tape.meter) for counter in counters)
            assert steps <= 512*modulus
            assert [output.origins[i+1] for i in range(modulus)] == [(-i)%modulus for i in range(modulus)]
            rows.append({'modulus':modulus,'volume':modulus,'control_tape_steps':steps})
            output.clear();source.clear()
        finally:
            candidate.Counter=original_counter;candidate.Tape=original_tape
            before.close();suffix.close();ring.close();arena.free(m)
        audit(arena)
    return {'measured_family':rows,'finite_assertion':'control reads+writes+moves <=512V in these five cases',
            'scope':'all Counter tapes, residue arena, and before/suffix tapes; source/output payload tapes excluded'}


def run():
    rows = []
    digest = sha256()
    for modulus in (2, 3, 9, 25):
        for before in (1, 2, 5):
            for suffix in (1, 2, 7):
                volume = before * modulus * suffix
                arena = Arena(modulus.bit_length() + 1)
                m = arena.input(modulus)
                ring = Ring(m)
                b0, s0 = Count.literal(before), Count.literal(suffix)
                b, s = b0.marginal(), s0.marginal()
                b0.close(); s0.close()
                origins = Origins()
                source = origins.source(volume)
                initial = bytes(source.cells)
                old = candidate.Tape
                candidate.Tape = origins.factory
                old_counter = candidate.Counter
                residue_counter_setups = []
                def observed_counter(value):
                    # Distinguish full residue-word copies from canonical
                    # spectator counters without decoding any numerical value.
                    if isinstance(value,Word): residue_counter_setups.append(value.slot)
                    return old_counter(value)
                candidate.Counter = observed_counter
                moves = source.meter.moves
                try:
                    with no_decode():
                        result = candidate.sign_address(source, ring, 3, b, s)
                    # In an output address [outer][x][inner], the unique
                    # input provenance must be [outer][-x mod M][inner].
                    wanted = []
                    for address in range(volume):
                        block, inner = divmod(address, suffix)
                        outer, x = divmod(block, modulus)
                        wanted.append((outer * modulus + (-x) % modulus) * suffix + inner)
                    actual = [result.origins[i + 1] for i in range(volume)]
                    assert actual == wanted
                    assert len(bits(result)) == volume
                    assert bytes(source.cells) == initial
                    assert source.head == result.head == 1
                    assert all(bits(result)[i] == initial[wanted[i] + 1] for i in range(volume))
                    # Count the actual unit source-head moves, including the
                    # complete final rewind. Each outer block moves (5M-8)S,
                    # then the successful and final cleanup rewinds add V+4.
                    physical_moves = source.meter.moves - moves
                    assert physical_moves == (6 * modulus - 8) * before * suffix + 4
                    assert physical_moves <= 6 * volume
                    # Only the two long forward skips and the nonzero-slice
                    # loop may copy a residue-width counter per outer block.
                    # Rebuilding a padded numeral-two counter for every slice
                    # would hide Theta(V log M) control work at suffix=1.
                    assert len(residue_counter_setups) == 3 * before
                    audit(arena, (m, ring.one))
                    result.clear(); source.clear()
                    assert not origins.live
                    rows.append([modulus, before, suffix, volume, physical_moves])
                    digest.update(json.dumps(actual).encode())
                finally:
                    candidate.Tape = old
                    candidate.Counter = old_counter
                    b.close(); s.close(); ring.close(); arena.free(m)
                audit(arena)
    rejected = []
    for label, length in (('truncated_input',11),('overlong_input',13),('non_bit_input',12)):
        arena = Arena(3); m = arena.input(3); ring = Ring(m)
        b0, s0 = Count.literal(2), Count.literal(2)
        b, s = b0.marginal(), s0.marginal(); b0.close(); s0.close()
        origins = Origins(); source = origins.source(length)
        if label == 'non_bit_input': source.cells[5] = 3
        original = bytes(source.cells); old = candidate.Tape; candidate.Tape = origins.factory
        try:
            try:
                with no_decode(): candidate.sign_address(source,ring,3,b,s)
            except ValueError:
                rejected.append(label)
            else: raise AssertionError('malformed sign source accepted')
            assert origins.live == {source}, 'failed sign output retained'
            assert bytes(source.cells) == original and source.head == 1
            audit(arena,(m,ring.one)); source.clear()
        finally:
            candidate.Tape = old
            b.close(); s.close(); ring.close(); arena.free(m)
        audit(arena)
    return {'status': 'PASS_LINEAR_SIGN_INDEPENDENT', 'cases': len(rows),
        'addresses': sum(row[3] for row in rows), 'source_move_bound': '6V',
        'exact_source_moves': '(6M-8)BS+4', 'digest': digest.hexdigest(),
        'moduli': [2, 3, 9, 25], 'host_numeric_decode': False,
        'residue_width_counter_setups':'3B; no per-slice padded numeral-two counter',
        'control_scaling':control_scaling(),
        'malformed_input_controls':rejected}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
