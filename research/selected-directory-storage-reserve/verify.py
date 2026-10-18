#!/usr/bin/env python3
"""Source-bound exact serialization and numerical reserve evidence."""
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from source import load
from model import need, code_bits, field_cells, directory_cells, reserve


def literal_field(code, digits, bits, word_bits):
    # Independent of retained append/read helpers. Literal source alphabet:
    # bit 0/1; WORD_END=5; RECORD_END=6; initial LEFT=2.
    out = [(code >> i) & 1 for i in range(bits)] + [5]
    for value in digits:
        out.extend((value >> i) & 1 for i in range(word_bits))
        out.append(5)
    out.append(6)
    return bytes(out)


def producer_case(source, q, m, w, h, count, requests):
    words, records = source['words'], source['records']
    directory = source['directory']
    codes = source['low_codes'].LowCodes(q, m, requests)
    arena = words.Arena((q**w).bit_length()+1)
    modulus = arena.input(q**w)
    ring = words.Ring(modulus)
    context = directory.Context(ring, codes)
    indices = words.Arena(max(2, h.bit_length()+1))
    old_fields = indices.input(h)
    old_count = source['counts'].Count.literal(count)
    cap = q**(w-1)
    prefixes = []
    for position in range(count):
        # Positions 0 and 2 are identical but must both remain present.
        prefix = b''.join(literal_field((position % 2+field) % codes.limit,
                         [(position % 2+field+k) % cap for k in range(m*m)],
                         codes.bits, arena.bits) for field in range(h))
        prefixes.append(prefix)
    old = records.Tape()
    for symbol in b''.join(prefixes):
        old.append(symbol)
    old.rewind()
    before = bytes(old.cells)
    protected = set(arena.live)
    output, emitted = directory.produce(old, old_fields, old_count, 1, context)
    expected = bytearray([2])
    for prefix in prefixes:
        for digits in product(range(cap), repeat=m*m):
            expected.extend(prefix)
            expected.extend(literal_field(1, digits, codes.bits, arena.bits))
    actual = bytes(output.cells)
    need(actual == expected, 'complete independently serialized output')
    need(actual[0] == 2 and actual[-1] == 6, 'LEFT and terminal field marker')
    need(len(actual) == directory_cells(q, m, w, h, count, requests), 'exact physical extent')
    need(codes.bits == code_bits(q, m, requests), 'source minimal code width')
    need(bytes(old.cells) == before and old.head == 1, 'old source preserved and rewound')
    need(arena.live == protected, 'producer numerical scratch restored')
    expected_count = source['counts'].Count.literal(count*cap**(m*m))
    need(emitted.equals(expected_count), 'actual returned count')
    expected_count.close()
    emitted.close()
    old_count.close()
    context.close()
    ring.close()
    arena.free(modulus)
    indices.free(old_fields)
    need(not arena.live and not indices.live, 'fixture-owned numerical words released')
    return {'q': q, 'm': m, 'w': w, 'h': h, 'positions': count,
            'requests': requests, 'code_bits': codes.bits,
            'records': count*cap**(m*m), 'directory_cells': len(actual),
            'sha256': sha256(actual).hexdigest()}


def rejected(fn, name):
    try:
        fn()
    except ValueError:
        return name
    raise ValueError('ineffective rejection: '+name)


def run():
    source = load()  # Verify all retained bytes before their first import.
    cases = [(3, 1, 1, 0, 3, 1), (3, 1, 2, 2, 3, 7),
             (3, 1, 4, 1, 2, 28278), (5, 1, 3, 2, 2, 3),
             (3, 2, 2, 1, 2, 2), (5, 2, 2, 2, 1, 7),
             (3, 3, 1, 1, 3, 1), (3, 64, 1, 1, 2, 28278)]
    rows = [producer_case(source, *case) for case in cases]
    # Arithmetic fixtures only: no primality claim or huge-q GL execution.
    arithmetic = []
    for q in (2**80, 2**80+1, 2**81-1, 2**127-1):
        for m in (1, 8, 64):
            for w in (1, 2, 7, 32):
                for h in (0, 20051*w//17-1):
                    arithmetic.append(reserve(q, m, w, h, 28278))
    need(8300*20051*81 < 17*2**30, 'uniform strict constant')
    need(8211 < 108*81, 'field majorant strict constant')
    q = 2**80
    minimal = code_bits(q, 64, 28278)
    controls = []
    tiny = directory_cells(3, 64, 1, 0, 1, 28278)
    need((tiny << 130) >= 3**2, 'tiny-q countermodel')
    controls.append('tiny_q_defeats_fraction')
    field = field_cells(q, 64, 1, 28278)
    need(((1+field) << 130) >= 1, 'header-only countermodel')
    controls.append('header_only_defeats_fraction')
    need(((1+(q*q+1)*field) << 130) >= q*q, 'unbounded-depth countermodel')
    controls.append('unbounded_depth_defeats_fraction')
    need(((1+q*q+64*64*(q.bit_length()+2)+2) << 130) >= q*q,
         'padded-code countermodel')
    controls.append('arbitrary_padding_defeats_fraction')
    for name, kwargs in [
        ('reject_small_q', {'q': 3}), ('reject_header_only', {'fibre_bits': 1}),
        ('reject_deep_history', {'frozen': q*q}),
        ('reject_padding', {'compiled_bits': minimal+1}),
        ('reject_vocabulary_overflow', {'requests': 28279}),
        ('reject_boolean_width', {'width': True}),
        ('reject_boolean_dimension', {'dimension': True}),
        ('reject_nonpositive_body', {'body_dimension': 0})]:
        args = dict(q=q, dimension=64, width=1, frozen=0, requests=28278)
        args.update(kwargs)
        controls.append(rejected(lambda args=args: reserve(**args), name))
    row = rows[1]
    field_count = row['records']*(row['h']+1)
    actual = row['directory_cells']
    for name, wrong in [('omit_left', actual-1),
                        ('omit_code_delimiters', actual-field_count),
                        ('omit_matrix_delimiters', actual-field_count*row['m']**2),
                        ('deduplicate_positions', 1+(actual-1)*2//3)]:
        need(wrong != actual, 'effective serialized undercount: '+name)
        controls.append(name)
    return {'schema_version': 1, 'producer_cases': rows,
            'total_checked_symbols': sum(row['directory_cells'] for row in rows),
            'arithmetic_cases': len(arithmetic),
            'arithmetic_certificate_digest': sha256(json.dumps(arithmetic, sort_keys=True).encode()).hexdigest(),
            'directory_cell_shift': 130, 'encoding_shift': 128,
            'parking_cell_shift': 127, 'parking_encoding_shift': 125,
            'controls': controls}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


if __name__ == '__main__':
    result = run()
    if sys.argv[1:] == ['--write']:
        (HERE/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    else:
        need(not sys.argv[1:], 'usage: verify.py [--write]')
        need(canonical(result) == canonical(json.loads((HERE/'RESULT.json').read_text(encoding='utf-8'))),
             'typed complete receipt mismatch')
    print('PASS_SELECTED_DIRECTORY_RESERVE producer_cases={} symbols={} arithmetic={} controls={}'.format(
        len(result['producer_cases']), result['total_checked_symbols'],
        result['arithmetic_cases'], len(result['controls'])))
