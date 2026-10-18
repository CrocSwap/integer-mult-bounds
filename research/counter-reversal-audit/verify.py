#!/usr/bin/env python3
"""Exact finite evidence for the counter reversal audit; standard library only."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_check():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for path, pin in pins['files'].items():
        data = (ROOT / path).read_bytes()
        require(hashlib.sha256(data).hexdigest() == pin['sha256'], 'source drift: ' + path)
        blob = b'blob ' + str(len(data)).encode() + b'\0' + data
        require(hashlib.sha1(blob).hexdigest() == pin['git_blob'], 'Git blob drift: ' + path)
    return len(pins['files'])


def literal(width, value, direction, exterior):
    """Single-cell interpreter of pinned instruction; no carry-length shortcut."""
    tape = {-1: 'S', width: 'S'}
    tape.update({i: (value >> i) & 1 for i in range(width)})
    tape.update({-2-i: symbol for i, symbol in enumerate(exterior)})
    tape.update({width+1+i: symbol for i, symbol in enumerate(reversed(exterior))})
    before = tape.copy()
    head, mode, flag, count = 0, 'carry', False, 0
    while mode != 'done':
        require(-1 <= head <= width, 'head left delimited word')
        symbol = tape[head]
        if mode == 'carry':
            if symbol == 'S':
                mode, flag, head = 'rewind', True, head-1
            else:
                tape[head] = 1-symbol
                if symbol == direction:
                    head += 1
                else:
                    mode, head = 'rewind', head-1
        else:
            if symbol == 'S':
                mode, head = 'done', head+1
            else:
                head -= 1
        count += 1
        require(count <= 2*width+2, 'did not halt within physical bound')
    require(head == 0, 'head not restored')
    require(all(tape[i] == s for i, s in before.items() if i < 0 or i >= width),
            'delimiter/exterior changed')
    result = sum(tape[i] << i for i in range(width))
    return result, int(flag), count


def phi(width, value, direction):
    ones = value.bit_count()
    return ones if direction else width-ones


def summarize(width, initial, directions, table):
    value, total, wraps, jumps, runs, wrap_runs = initial, 0, 0, 0, 0, 0
    last, run_wrapped = None, False
    for d in directions:
        if d != last:
            if last is not None:
                jumps += phi(width, value, d)-phi(width, value, last)
                wrap_runs += int(run_wrapped)
            runs += 1
            run_wrapped = False
        nxt, wrap, steps = table[width, value, d]
        require(steps == 4 + 2*phi(width, value, d)-2*phi(width, nxt, d)-2*wrap,
                'one-call potential identity')
        total += steps
        wraps += wrap
        run_wrapped |= bool(wrap)
        value, last = nxt, d
    wrap_runs += int(run_wrapped)
    n = len(directions)
    if n:
        identity = (4*n + 2*phi(width, initial, directions[0])
                    - 2*phi(width, value, directions[-1]) + 2*jumps - 2*wraps)
    else:
        identity = 0
    require(total == identity, 'signed reversal identity')
    if width:
        bound = 4*n + 2*(width-1)*runs
        refined = 4*n + 2*(width-2)*runs + 2*wrap_runs
        require(total <= refined <= bound, 'run bounds')
    else:
        bound = refined = 2*n
        require(total == 2*n, 'width-zero cost')
    return dict(width=width, initial=initial, calls=n, final=value, runs=runs,
                wraps=wraps, wrap_runs=wrap_runs, signed_switch_potential=jumps,
                steps=total, refined_bound=refined, uniform_bound=bound,
                fixed_direction_bound=4*n+2*width)


def build_receipt():
    source_count = source_check()
    table, executions = {}, 0
    exteriors = [(), ('B',), (0, 1, 'S', 'B'), ('S', 'B', 1, 0)]
    for w in range(11):
        modulus = 1 << w
        for value in range(modulus):
            for d in (0, 1):
                observed = [literal(w, value, d, exterior) for exterior in exteriors]
                executions += len(exteriors)
                require(all(x == observed[0] for x in observed), 'exterior-dependent execution')
                nxt, wrap, steps = observed[0]
                require(nxt == (value + (1 if d else -1)) % modulus, 'modular value')
                require(wrap == int(value == (modulus-1 if d else 0)), 'wrap flag')
                # Independent integer valuation predicts the literal time.
                v = value if d else modulus-1-value
                k = 0
                while v & 1:
                    k, v = k+1, v >> 1
                require(steps == 2*k+2, 'literal first-completion count')
                table[w, value, d] = observed[0]
    schedules, digest = 0, hashlib.sha256()
    for w in range(8):
        for value in range(1 << w):
            for n in range(9):
                for ds in itertools.product((0, 1), repeat=n):
                    row = summarize(w, value, ds, table)
                    schedules += 1
                    digest.update(json.dumps([w, value, ds, row], sort_keys=True,
                                             separators=(',', ':')).encode() + b'\n')
    rng = random.Random(67)
    for _ in range(256):
        w = rng.randrange(11)
        value = rng.randrange(1 << w)
        ds = tuple(rng.randrange(2) for _ in range(257))
        summarize(w, value, ds, table)
    w, n = 2+67 % 5, 3+67 % 7
    ds = tuple(1-i % 2 for i in range(n))
    nonwrap = summarize(w, (1 << (w-1))-1, ds, table)
    wrapping = summarize(w, (1 << w)-1, ds, table)
    # Meaningful false-claim controls, each with an explicit witness.
    controls = {}
    def reject(name, false_statement):
        require(not false_statement, 'negative control escaped: ' + name)
        controls[name] = 'rejected'
    reject('fixed_direction_bound_applied_to_nonwrapping_reversals',
           nonwrap['steps'] <= nonwrap['fixed_direction_bound'])
    reject('fixed_direction_bound_applied_to_wrapping_reversals',
           wrapping['steps'] <= wrapping['fixed_direction_bound'])
    reject('omit_signed_switch_term', wrapping['steps'] == wrapping['steps']-2*wrapping['signed_switch_potential'])
    reject('reverse_signed_switch_term', wrapping['steps'] == wrapping['steps']-4*wrapping['signed_switch_potential'])
    reject('omit_wrap_credit', wrapping['steps'] == wrapping['steps']+2*wrapping['wraps'])
    reject('apply_nonwrapping_bound_to_wrapping_calls', wrapping['steps'] <= 4*n+2*(w-2)*n)
    reject('reduce_uniform_run_surcharge_by_one', wrapping['steps'] <= wrapping['uniform_bound']-n)
    reject('reduce_nonwrapping_run_surcharge_by_one', nonwrap['steps'] <= nonwrap['refined_bound']-n)
    single = summarize(4, 15, (1,), table)
    reject('omit_initial_run_charge', single['steps'] <= 4)
    zero = summarize(0, 0, (1, 0, 0), table)
    reject('treat_zero_width_calls_as_free', zero['steps'] == 0)
    require(wrapping['steps'] == wrapping['uniform_bound'], 'wrapping sharpness')
    require(nonwrap['steps'] == nonwrap['refined_bound'] and nonwrap['wraps'] == 0,
            'nonwrapping sharpness')
    return {'scope': 'Finite evidence; universal result is the handwritten proof, not a formal theorem',
            'source_files_checked': source_count, 'seed': 67,
            'literal_domain': {'widths': [0, 10], 'all_words_and_both_directions': True,
                               'exterior_patterns': len(exteriors), 'executions': executions},
            'schedule_domain': {'widths': [0, 7], 'lengths': [0, 8],
                                'all_words_and_direction_strings': True, 'schedules': schedules,
                                'sha256': digest.hexdigest()},
            'longer_seeded_cases': {'seed': 67, 'cases': 256, 'calls_per_case': 257,
                                    'widths': [0, 10]},
            'stopping_rule': 'Complete the stated finite domains; no adaptive search',
            'nonwrapping_witness': nonwrap, 'wrapping_witness': wrapping,
            'negative_controls': controls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='Write a receipt instead of comparing the committed one')
    args = parser.parse_args()
    receipt = build_receipt()
    if args.write:
        args.write.write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    else:
        require(receipt == json.loads((HERE / 'EXPECTED.json').read_text()), 'receipt mismatch')
    print('PASS_COUNTER_REVERSAL_AUDIT schedules={} literal_executions={} controls={}'.format(
        receipt['schedule_domain']['schedules'], receipt['literal_domain']['executions'],
        len(receipt['negative_controls'])))


if __name__ == '__main__':
    main()
