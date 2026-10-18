#!/usr/bin/env python3
"""A fully specified finite, unrolled array-machine invoice.

Gareth Davidson (bitplane), with substantial OpenAI Codex assistance.
Apache-2.0. Counts are not a selected-supplier or wall-clock runtime claim.
"""
from collections import Counter
from model import denominator_budget, permutation, require, word_digest


def records(word, bits):
    """Each record reads old operands, writes answers, clears private work,
    and returns its data head to the left edge of cell zero.

    C: four input real components and four output real components, 12 signed
       additions and four exact halvings; eight private real registers.
    swap: four old real components; four private real registers.
    b+/b-: two old/two new real components; two signed additions, plus two
       exact halvings for b+; four private real registers.
    i/-1/-i: two old real components, one/two/one negations respectively;
       two private real registers.
    """
    n = 1 << bits
    for op in word:
        if op.kind == 'C':
            for axis in op.a:
                for j in range(n):
                    if not (j >> axis) & 1:
                        yield ('C', j, j | (1 << axis))
        elif op.kind in ('xor', 'translate'):
            for j in range(n):
                k = permutation(op, j)
                if j < k:
                    yield ('swap', j, k)
        elif op.kind in ('phase', 'global_phase'):
            mask = sum(1 << bit for bit in op.a)
            for j in range(n):
                exponent = op.power * ((j & mask).bit_count() if op.kind == 'phase' else 1)
                if exponent % 4:
                    yield ({1:'i', 2:'-1', 3:'-i'}[exponent % 4], j, 0)
        elif op.kind == 'scale_b':
            for _ in range(abs(op.power)):
                for j in range(n):
                    yield ('b+' if op.power > 0 else 'b-', j, 0)
        else:
            raise ValueError('unknown invoice operation')


def charge(word, bits):
    n = 1 << bits
    histogram = Counter()
    totals = Counter({'private_real_clears':8})  # startup, explicitly paid
    for kind, left, right in records(word, bits):
        histogram[kind] += 1
        totals['records'] += 1
        if kind in ('C', 'swap'):
            totals['real_reads'] += 4
            totals['real_writes'] += 4
            totals['complex_cell_visits'] += 4
            totals['data_head_cell_steps'] += 4*right-2*left
            totals['private_real_clears'] += 8 if kind == 'C' else 4
            if kind == 'C':
                totals['real_add_sub'] += 12
                totals['exact_halvings'] += 4
        else:
            totals['real_reads'] += 2
            totals['real_writes'] += 2
            totals['complex_cell_visits'] += 2
            totals['data_head_cell_steps'] += 2*left
            if kind in ('b+', 'b-'):
                totals['private_real_clears'] += 4
                totals['real_add_sub'] += 2
                if kind == 'b+':
                    totals['exact_halvings'] += 2
            else:
                totals['private_real_clears'] += 2
                totals['real_negations'] += 2 if kind == '-1' else 1
    record_bits = 4+2*bits
    totals['dispatches'] = totals['records']
    totals['instruction_read_bits'] = record_bits*totals['records']
    totals['instruction_head_bit_steps'] = 2*totals['instruction_read_bits']
    # Conservative width facts, without rounding or an unbounded-integer tariff.
    q = denominator_budget(word)
    growth_bits = (sum(len(op.a) for op in word if op.kind == 'C')
                   + sum(max(-op.power, 0) for op in word if op.kind == 'scale_b'))
    return {
        'word_sha256': word_digest(word),
        'address_bits': bits,
        'complex_data_cells': n,
        'native_C_children': dict(sorted(Counter(len(op.a) for op in word if op.kind == 'C').items())),
        'native_child_operand_cells': [{'width':len(op.a), 'cells':n} for op in word if op.kind == 'C'],
        'macro_count': len(word),
        'record_kind_counts': dict(sorted(histogram.items())),
        'execution_counts': dict(sorted(totals.items())),
        'record_bits': record_bits,
        'program_storage_bits': totals['records']*record_bits,
        'data_storage_formula_bits': f'2*{n}*B',
        'private_storage_formula_bits': '8*(B+2)',
        'data_access_formula_bit_actions': f"{totals['real_reads']+totals['real_writes']}*B",
        'data_head_formula_bit_steps': f"2*B*{totals['data_head_cell_steps']}+2*(2*B-1)*{totals['complex_cell_visits']}",
        'private_clear_formula_bit_actions': f"{totals['private_real_clears']}*(B+2)",
        'fractional_guard_bits_sufficient': q,
        'magnitude_growth_bits_sufficient': growth_bits,
        'signed_data_width_sufficient': f'B=p+b+{q+growth_bits+2}',
        'unpriced_terms_are_not_zero': [
            'Uniform program generation, including at least program_storage_bits descriptor writes; its control/arithmetic implementation remains to be priced.',
            'Address/dispatch control and its O(address_bits+log(program_storage_bits)) working bits.',
            'Real ADD/SUB/NEG and exact-halving implementations on the stated B+2-bit private registers.',
            'Input grid admission and output grid decoding, if required by the caller.',
            'Any selected-supplier layout, packed address-movement, hosting, or analytic-transfer obligation.',
        ],
    }


def audit_charge(word, bits, invoice):
    """Recount addresses by explicit head visits; no closed head-distance formula."""
    require(invoice['word_sha256'] == word_digest(word), 'invoice word changed')
    require(invoice['native_child_operand_cells'] ==
            [{'width':len(op.a), 'cells':1 << bits} for op in word if op.kind == 'C'],
            'child lost spectator fibers or was assigned a smaller operand volume')
    head = 0
    reads = writes = distance = visits = length = 0
    for kind, left, right in records(word, bits):
        length += 1
        operands = (left, right) if kind in ('C', 'swap') else (left,)
        for address in operands:
            distance += abs(head-address)
            head = address
            reads += 2
            visits += 1
        for address in operands:
            distance += abs(head-address)
            head = address
            writes += 2
            visits += 1
        distance += abs(head)
        head = 0
    counts = invoice['execution_counts']
    require((reads, writes, distance, visits, length) ==
            (counts['real_reads'], counts['real_writes'], counts['data_head_cell_steps'],
             counts['complex_cell_visits'], counts['records']), 'explicit access recount differs')
    require(sum(int(width)*count for width, count in invoice['native_C_children'].items()) ==
            sum(len(op.a) for op in word if op.kind == 'C'), 'recursive width invoice differs')
