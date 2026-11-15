#!/usr/bin/env python3
"""Independent reverse/dual audit of the fixed-history coframe-zero screen.

Hao Yan (@FanPUYen), with substantial OpenAI Codex assistance. Apache-2.0.
Source-native authors retain the credit in NOTICE and inputs/*NOTICE.

This imports no producer checker.  It enumerates observation TIMES using only
the ownership/chart tape, then propagates all those output functionals backwards
as bit-vector columns.  Least-pivot column elimination produces nine explicit
right-kernel witnesses with identity new-input coordinates.  A separate XOR
check verifies each witness against every observation, without trusting rank.
"""
from pathlib import Path
from hashlib import sha256
import json, gzip

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'inputs/BIT-NATIVE-WORD.json.gz'
EXPECTED = HERE / 'EXPECTED.json'
EXPECTED_SHA = 'cd4d86385e464b69579159af4c67bdde03c357190dffd4a54c01d175a194fdb7'
SOURCE_SHA = '51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78'
OWNERS = tuple(range(770, 779))


def require(condition, label):
    if not condition:
        raise ValueError(label)


def bits(value):
    while value:
        bit = value & -value
        yield bit.bit_length() - 1
        value ^= bit


def column_basis(columns):
    """Column elimination on observation-space vectors, carrying input indices."""
    basis = {}
    for index, column in enumerate(columns):
        combination = 1 << index
        while column:
            pivot = (column & -column).bit_length() - 1
            if pivot not in basis:
                basis[pivot] = (column, combination)
                break
            vector, provenance = basis[pivot]
            column ^= vector
            combination ^= provenance
    return basis


def solve(basis, vector):
    combination = 0
    while vector:
        pivot = (vector & -vector).bit_length() - 1
        require(pivot in basis, 'new-input observation column is in old-input column image')
        column, provenance = basis[pivot]
        vector ^= column
        combination ^= provenance
    return combination


def xor_columns(columns, indices):
    result = 0
    for index in indices:
        result ^= columns[index]
    return result


def authenticated_word(raw):
    require(sha256(raw).hexdigest() == SOURCE_SHA, 'exact immutable BIT word')
    return json.loads(gzip.decompress(raw))


def audit():
    raw = SOURCE.read_bytes()
    word = authenticated_word(raw)
    program, n = word['program'], word['public']
    total = n + word['owned_fields']
    require(n == 659 and total == 896, 'source register inventory')
    require(word['frames']['0']['dim'] == 0, 'coframe zero is empty frame')
    chart = list(word['start']) + [None] * word['owned_fields']
    active, initializations, retirements = set(), {}, {}
    observation_plan = []
    initial_observations = [(i, r) for i, r in enumerate(r for r, f in enumerate(chart) if f == 0)]
    observation_count = len(initial_observations)
    initial_count = observation_count
    other_clears = []
    descending = []
    for event_index, event in enumerate(program):
        op, register = event[:2]
        if op == 'INIT':
            require(register >= n and register not in active, 'fresh owned lifetime')
            active.add(register)
            chart[register] = event[2]
            initializations[register] = initializations.get(register, 0) + 1
        elif op == 'CLEAR':
            require(register in active and chart[register] == event[2], 'CLEAR at live chart')
            retirements[register] = retirements.get(register, 0) + 1
            if register not in OWNERS:
                active.remove(register)
                chart[register] = None
                other_clears.append((event_index, register))
        elif op == 'ADD':
            require(len(event) == 4 and register != event[2], 'binary ADD syntax')
            require(chart[register] is not None and chart[register] == chart[event[2]] == event[3], 'coframed ADD')
        elif op == 'MOVE':
            require(chart[register] == event[2], 'MOVE source chart')
            chart[register] = event[3]
            if register in OWNERS:
                descending.append((register, event[2], event[3]))
        elif op == 'SWAP':
            require(chart[register] is not None and chart[event[2]] is not None, 'live SWAP')
            chart[register], chart[event[2]] = chart[event[2]], chart[register]
        else:
            raise ValueError('unknown source opcode ' + op)
        observations = []
        for referenced in (event[1:3] if op in ('ADD', 'SWAP') else event[1:2]):
            if chart[referenced] == 0:
                observations.append((observation_count, referenced))
                observation_count += 1
        observation_plan.append(observations)
    require(active == set(OWNERS), 'only nine promoted fields retained')
    require(all(initializations[r] == retirements[r] == 1 for r in OWNERS), 'each promoted field occurs once')
    require(descending == [(r, 510 + r - 770, 0) for r in OWNERS], 'exact nine descending moves')
    for owner in OWNERS:
        references = [event for event in program
                      if owner in (event[1:3] if event[0] in ('ADD', 'SWAP') else event[1:2])]
        require(references[-1] == ['CLEAR', owner, 0], 'original CLEAR is the last access to promoted owner')
    require(all(word['frames'][str(a)]['dim'] - word['frames'][str(b)]['dim'] == 7
                for _, a, b in descending), 'all nine descending ranks are seven')
    require(observation_count == 39848 and initial_count == 524, 'all post-event plus initial observations')

    # Add final-register outputs, then pre-CLEAR contents of other owned fields.
    endpoint_offset = observation_count
    clear_offset = endpoint_offset + total
    clear_outputs = {event: clear_offset + i for i, (event, _) in enumerate(other_clears)}
    adjoints = [1 << (endpoint_offset + r) for r in range(total)]
    new_columns = {}
    for event_index in reversed(range(len(program))):
        for output, register in observation_plan[event_index]:
            adjoints[register] ^= 1 << output
        op, register, *tail = program[event_index]
        if op == 'ADD':
            adjoints[tail[0]] ^= adjoints[register]
        elif op == 'SWAP':
            adjoints[register], adjoints[tail[0]] = adjoints[tail[0]], adjoints[register]
        elif op == 'INIT':
            if register in OWNERS:
                require(register not in new_columns, 'unique fresh input injection')
                new_columns[register] = adjoints[register]
            adjoints[register] = 0
        elif op == 'CLEAR' and register not in OWNERS:
            adjoints[register] = 1 << clear_outputs[event_index]
    for output, register in initial_observations:
        adjoints[register] ^= 1 << output
    require(not any(adjoints[n:]), 'no uninitialized old owned input')
    mask = (1 << observation_count) - 1
    old_columns = [column & mask for column in adjoints[:n]]
    h_columns = [new_columns[r] & mask for r in OWNERS]
    old_basis = column_basis(old_columns)
    rank_old = len(old_basis)
    rank_full = len(column_basis(old_columns + h_columns))
    require(rank_old == rank_full == 533, 'independent column ranks')
    witnesses = []
    for index, column in enumerate(h_columns):
        combination = solve(old_basis, column)
        support = list(bits(combination))
        require(xor_columns(old_columns, support) ^ column == 0,
                'direct kernel verification against all observations')
        witnesses.append(dict(promoted_owner=OWNERS[index], old_input_support=support,
                              new_input_coordinate=index,
                              identity_new_block=True, all_observation_pairings_zero=True))

    # Independently execute the nine concrete input differences simultaneously.
    # This verifies the displayed witnesses against the tape, without either
    # the reverse propagation or an elimination/rank calculation.
    values = [0] * total
    for index, witness in enumerate(witnesses):
        for old_input in witness['old_input_support']:
            values[old_input] ^= 1 << index
    current = list(word['start']) + [None] * word['owned_fields']
    require(all(values[r] == 0 for r, f in enumerate(current) if f == 0),
            'concrete witness vanishes at every initial coframe-zero field')
    for event in program:
        op, register = event[:2]
        if op == 'ADD':
            values[register] ^= values[event[2]]
        elif op == 'SWAP':
            values[register], values[event[2]] = values[event[2]], values[register]
            current[register], current[event[2]] = current[event[2]], current[register]
        elif op == 'MOVE':
            current[register] = event[3]
        elif op == 'INIT':
            values[register] = 1 << OWNERS.index(register) if register in OWNERS else 0
            current[register] = event[2]
        elif op == 'CLEAR' and register not in OWNERS:
            values[register], current[register] = 0, None
        for referenced in (event[1:3] if op in ('ADD', 'SWAP') else event[1:2]):
            if current[referenced] == 0:
                require(values[referenced] == 0, 'concrete forward witness coframe-zero invariant')
    require(all(values[r] == 0 for r in OWNERS), 'final promoted fields indistinguishable under witnesses')

    # These nine verified annihilators (u_j,e_j) imply V intersection H=0:
    # a pure new-input vector in V must pair to zero with every e_j.
    public_mask = (1 << n) - 1
    leak_counts = {r: ((new_columns[r] >> endpoint_offset) & public_mask).bit_count() for r in OWNERS}
    require(leak_counts == dict(zip(OWNERS, [63, 55, 55, 55, 63, 63, 55, 55, 63])), 'final public contamination')
    require(all(new_columns[r] >> clear_offset == 0 for r in OWNERS), 'no new-input coefficients erased elsewhere')
    terminal_h = [[(new_columns[source] >> (endpoint_offset + destination)) & 1
                   for source in OWNERS] for destination in OWNERS]
    require(terminal_h == [[int(i == j) for j in range(9)] for i in range(9)], 'retained helper new-input block identity')

    # Meaningful controls: a mixed new-input stock vector changes the joint
    # answer even though no single new-input basis vector becomes available.
    extra = 1 << observation_count
    mixed_h = [column ^ extra if index < 2 else column for index, column in enumerate(h_columns)]
    mixed_rank = len(column_basis(old_columns + mixed_h))
    require(mixed_rank == 534, 'joint h0+h1 stock makes intersection dimension one')
    individual_still_absent = []
    for index in range(9):
        augmented = list(mixed_h)
        augmented[index] ^= extra << 1
        individual_still_absent.append(len(column_basis(old_columns + augmented)) == mixed_rank + 1)
    require(all(individual_still_absent), 'joint control invisible to singleton membership checks')
    all_h_available = [column ^ (extra << index) for index, column in enumerate(h_columns)]
    full_stock_rank = len(column_basis(old_columns + all_h_available))
    require(full_stock_rank - rank_old == 9, 'positive control: nine granted pure inputs give full new-input space')
    wrong_support = witnesses[0]['old_input_support'][:]
    marker = initial_observations[0][1]
    changed = set(wrong_support) ^ {marker}
    require(xor_columns(old_columns, changed) ^ h_columns[0] != 0, 'altered dual rejected')
    tampered = bytes([raw[0] ^ 1]) + raw[1:]
    try:
        authenticated_word(tampered)
    except ValueError as error:
        require(str(error) == 'exact immutable BIT word', 'corruption rejected by source authentication')
    else:
        raise ValueError('corrupt source accepted')

    report = dict(status='PASS_INDEPENDENT_REVERSE_DUAL_FIXED_HISTORY_SCREEN',
                  source_sha256=SOURCE_SHA, promoted=list(OWNERS), descending_rank=7,
                  initial_chart0_observations=initial_count,
                  post_instruction_chart0_observations=observation_count-initial_count,
                  total_observations=observation_count, old_input_columns=n, new_input_columns=9,
                  old_column_rank=rank_old, full_column_rank=rank_full,
                  joint_pure_new_input_intersection_dimension=0,
                  dual_kernel_witnesses=witnesses, direct_forward_witness_invariant=True,
                  interleaved_chart0_linear_gate_obstruction='See PROOF.md; uses the verified zero-at-every-chart0-contact invariant.',
                  public_output_leak_counts=leak_counts,
                  other_clear_count=len(other_clears), other_clear_new_input_leaks=0,
                  terminal_promoted_new_input_block=terminal_h,
                  hypothetical_native_extra_H7_targets=9,
                  hypothetical_36_call_target_credit='36 * 9 * 7^(1-C), if the independent-output contract were supplied',
                  controls=dict(mixed_joint_stock_intersection_dimension=1,
                                mixed_stock_all_singleton_inputs_still_absent=individual_still_absent,
                                granted_all_nine_inputs_intersection_dimension=9,
                                altered_dual_rejected=True, corrupt_source_rejected=True),
                  scope='The original chart trace and all original nonzero-frame operators are fixed. The verified input-difference invariant excludes final or interleaved additional linear gates confined to chart0, with identically initialized extra scratch. Different coframes, additional address maps, altered nonzero-frame operators, extra observations outside chart0, or a changed input/output contract are outside the proof. The ideal H7 credits are hypothetical only.')
    return report


def main():
    report = audit()
    expected_raw = EXPECTED.read_bytes()
    require(sha256(expected_raw).hexdigest() == EXPECTED_SHA, 'exact expected receipt bytes')
    require(json.loads(json.dumps(report)) == json.loads(expected_raw),
            'complete expected receipt comparison (JSON integer-key normalization)')
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
