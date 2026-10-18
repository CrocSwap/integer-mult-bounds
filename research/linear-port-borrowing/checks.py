"""Independent exact interpreters and explicit dense-backend accounting.

No compiler or macro is imported here. The free module keeps noncommuting
factor words and distinct symbols for every initial dirty row.
Apache-2.0; substantial OpenAI Codex assistance; see NOTICE.md.
"""
from collections import Counter
from functools import lru_cache


def need(condition, message):
    if not condition:
        raise ValueError(message)


@lru_cache(None)
def ordered_trees(n, offset=0):
    if n == 1:
        return (offset,)
    result = []
    for a in range(1, n):
        for left in ordered_trees(a, offset):
            for right in ordered_trees(n-a, offset+a):
                result.append((left, right))
    for a in range(1, n-1):
        for b in range(1, n-a):
            for left in ordered_trees(a, offset):
                for middle in ordered_trees(b, offset+a):
                    for right in ordered_trees(n-a-b, offset+a+b):
                        result.append((left, middle, right))
    return tuple(result)


def check_record(record, n, rows):
    need(len(record) == 4 and all(type(x) is int for x in record),
         "integer instruction fields required")
    s, d, i, q = record
    need(0 <= s < rows and 1 <= d < rows and s != d,
         "invalid ports or protected-source write")
    need(0 <= i < n and q in (-1, 1), "invalid factor or sign")


def free_replay(word, n, rows, direction, bound, factor_norm=2):
    initial = [{((), r): 1} for r in range(rows)]
    state = [dict(row) for row in initial]
    peak_terms, peak_degree, peak_norm = 1, 0, 1
    for record in word:
        check_record(record, n, rows)
        s, d, i, q = record
        for (factors, origin), coefficient in state[s].items():
            key = ((i,)+factors, origin)
            value = state[d].get(key, 0)+q*coefficient
            if value:
                state[d][key] = value
            else:
                state[d].pop(key, None)
        need(state[0] == initial[0], "source changed at a prefix")
        # Weighted free-polynomial l1 dominates every matrix substitution.
        for row in state:
            peak_terms = max(peak_terms, len(row))
            peak_degree = max(peak_degree, max((len(k[0]) for k in row), default=0))
            peak_norm = max(peak_norm, sum(abs(c)*factor_norm**len(k[0])
                                           for k, c in row.items()))
        need(peak_norm <= bound, "prefix norm exceeds proof bound")
    expected = [dict(row) for row in initial]
    expected[1][(tuple(reversed(range(n))), 0)] = direction
    need(state == expected, "free-module product or dirty restoration failed")
    return {"peak_terms_per_row": peak_terms, "peak_factor_degree": peak_degree,
            "peak_weighted_norm": peak_norm}


def matvec(matrix, vector):
    return [sum(a*b for a, b in zip(row, vector)) for row in matrix]


def product_action(matrices, vector):
    result = list(vector)
    for matrix in matrices:
        result = matvec(matrix, result)
    return result


def dense_replay(word, matrices, initial, direction, prefix_bound):
    n, rows, length = len(matrices), len(initial), len(initial[0])
    state = [list(row) for row in initial]
    work = [0, 0, 0, 0]  # Clean scalar registers, separately charged.
    peak = max(abs(x) for row in state for x in row)
    counters = Counter()
    head, steps, greatest_address = 0, 0, 0
    coefficient_base = rows*length

    def access(address, kind):
        nonlocal head, steps, greatest_address
        steps += abs(address-head)
        head = address
        greatest_address = max(greatest_address, address)
        counters[kind] += 1

    for record in word:
        check_record(record, n, rows)
        s, d, factor, sign = record
        for i in range(length):
            work[0] = 0
            counters["zero_assignments"] += 1
            for j in range(length):
                access(s*length+j, "reads")
                work[1] = state[s][j]
                access(coefficient_base+(factor*length+i)*length+j, "reads")
                work[2] = matrices[factor][i][j]
                work[3] = work[2]*work[1]
                counters["multiplications"] += 1
                peak = max(peak, *(abs(x) for x in work))
                work[0] += work[3]
                counters["add_subtract"] += 1
                peak = max(peak, abs(work[0]))
            access(d*length+i, "reads")
            work[1] = state[d][i]+sign*work[0]
            counters["add_subtract"] += 1
            peak = max(peak, abs(work[1]))
            access(d*length+i, "writes")
            state[d][i] = work[1]
        for register in range(4):
            work[register] = 0
            counters["zero_assignments"] += 1
        need(work == [0, 0, 0, 0], "scalar work not restored")
        steps += head  # Explicit home return, even after the last call.
        head = 0
        need(state[0] == initial[0], "dense source changed at a prefix")
    expected = [list(row) for row in initial]
    image = product_action(matrices, initial[0])
    expected[1] = [y+direction*x for y, x in zip(initial[1], image)]
    need(state == expected, "dense product or dirty restoration failed")
    need(peak <= prefix_bound, "dense scalar/data precision bound failed")
    counters["head_steps_cells"] = steps
    counters["maximum_address"] = greatest_address
    counters["peak_absolute_scalar_or_data"] = peak
    counters["primitive_commands"] = sum(counters[k] for k in
        ("zero_assignments", "multiplications", "add_subtract", "reads", "writes"))
    return dict(sorted(counters.items()))


def invoice(word, n, rows, length, precision, tree_nodes, leaf_counts):
    """Closed-form counters independently checked against literal dense replay.

    No multiplication unit cost is silently assigned. Metadata is an unrolled
    read-only word; the formula explicitly includes its bit storage and reads.
    """
    calls = len(word)
    need(type(precision) is int and precision > 0, "positive precision required")
    factor_bits = max(1, (n-1).bit_length())
    port_bits = max(1, (rows-1).bit_length())
    record_bits = factor_bits+2*port_bits+1
    counts = Counter(i for s, d, i, q in word)
    need([counts[i] for i in range(n)] == leaf_counts, "leaf multiplicity bill")
    # Independent address formula: per output row, source/coeff alternating
    # accesses, then target read/write; add the paid return-to-home per leaf.
    steps = 0
    base = rows*length
    for s, d, factor, q in word:
        head = 0
        for i in range(length):
            for j in range(length):
                source = s*length+j
                coefficient = base+(factor*length+i)*length+j
                steps += abs(source-head)+abs(coefficient-source)
                head = coefficient
            target = d*length+i
            steps += abs(target-head)
            head = target
        steps += head
    accesses = calls*(2*length**2+2*length)
    address_bits = max(1, ((rows*length+n*length**2)*precision-1).bit_length())
    return {
        "calls": calls, "negative_calls": sum(q < 0 for s, d, i, q in word),
        "multiplications": calls*length**2,
        "add_subtract": calls*(length**2+length),
        "zero_assignments": calls*(length+4),
        "reads": calls*(2*length**2+length), "writes": calls*length,
        "primitive_commands": calls*(4*length**2+4*length+4),
        "head_steps_cells": steps,
        "intercell_head_steps_bits": steps*precision,
        "within_cell_head_steps_bits": 2*(precision-1)*accesses,
        "head_steps_bits": steps*precision+2*(precision-1)*accesses,
        "data_bits": rows*length*precision,
        "coefficient_bits": n*length**2*precision,
        "scalar_work_bits": 4*precision,
        "startup_scalar_zero_assignments": 4,
        "record_bits": record_bits, "program_storage_and_read_bits": calls*record_bits,
        "data_access_bits": accesses*precision,
        "address_events": accesses, "address_bits": address_bits,
        "program_forward_and_rewind_steps_bits": 2*calls*record_bits,
        "tree_nodes": tree_nodes,
        "precision_bits": precision,
    }


def nonlinear_replay(word, initial):
    state = list(initial)
    for s, d, i, q in word:
        z = state[s]
        state[d] += q*((z % 17)**2+(i+1)*(z % 7)-3)
    return state
