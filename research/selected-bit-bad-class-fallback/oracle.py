#!/usr/bin/env python3
"""Independent exact consumer for bad-class fallback plans.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.

This module never imports the compiler.  It executes chronological words on
individual standard-basis inputs, so every input column is checked.  The
repeated-field consumer executes the reversal in F_A literally; spectators are
separate input columns, rather than initially zero scratch space.

Primality of q is an external mathematical premise.  This consumer uses gcd
against q**w for every inversion and proves the supplied instance directly;
it does not infer a universal local-ring theorem from finite examples.
"""

from math import gcd


class OracleError(ValueError):
    """A specific, independently checked obligation failed."""


def _require(condition, obligation):
    if not condition:
        raise OracleError(obligation)


def _integer(value, obligation):
    _require(type(value) is int, obligation)
    return value


def _matrix(matrix, size, modulus):
    _require(len(matrix) == size, "matrix row count")
    result = []
    for row in matrix:
        _require(len(row) == size, "matrix column count")
        result.append([_integer(x, "integer matrix coefficient") % modulus
                       for x in row])
    return result


def _op(operation, size, modulus, alphabet=None):
    _require(isinstance(operation, (list, tuple)) and operation,
             "operation encoding")
    kind = operation[0]
    arity = {"swap": 3, "add": 4, "pair": 4, "sign": 3,
             "lower": 4, "weighted_swap": 4}
    _require(kind in arity, "operation alphabet")
    _require(alphabet is None or kind in alphabet, "stage operation alphabet")
    _require(len(operation) == arity[kind], "operation arity")
    i = _integer(operation[1], "integer destination")
    _require(0 <= i < size, "destination range")
    if kind == "sign":
        c = _integer(operation[2], "integer sign")
        _require(c == -1, "fixed sign must be -1")
        return kind, i, None, c % modulus
    j = _integer(operation[2], "integer source")
    _require(0 <= j < size and i != j, "distinct coordinate range")
    c = 1 if kind == "swap" else _integer(operation[3], "integer coefficient") % modulus
    if kind in {"pair", "weighted_swap"}:
        _require(gcd(c, modulus) == 1, "only units may be inverted")
    if kind == "lower":
        _require(i > j, "lower-addition coordinate order")
    return kind, i, j, c


def _prepare(operations, size, modulus, alphabet=None):
    result = []
    for raw in operations:
        kind, i, j, c = _op(raw, size, modulus, alphabet)
        inverse = pow(c, -1, modulus) if kind in {"pair", "weighted_swap"} else None
        result.append((kind, i, j, c, inverse))
    return result


def _execute_prepared(vector, prepared, modulus):
    state = [x % modulus for x in vector]
    for kind, i, j, c, inverse in prepared:
        if kind == "swap":
            state[i], state[j] = state[j], state[i]
        elif kind in {"add", "lower"}:
            if c:
                state[i] = (state[i] + c * state[j]) % modulus
        elif kind == "pair":
            state[i] = c * state[i] % modulus
            state[j] = inverse * state[j] % modulus
        elif kind == "weighted_swap":
            old_i, old_j = state[i], state[j]
            state[i] = c * old_j % modulus
            state[j] = inverse * old_i % modulus
        elif kind == "sign":
            state[i] = -state[i] % modulus
    return state


def execute(vector, operations, modulus, *, alphabet=None):
    """Direct scalar value semantics, with chronological left action."""
    return _execute_prepared(vector, _prepare(operations, len(vector), modulus, alphabet),
                             modulus)


def operator(operations, size, modulus, *, alphabet=None):
    """Complete operator assembled from separately executed basis inputs."""
    columns = []
    prepared = _prepare(operations, size, modulus, alphabet)
    for column in range(size):
        vector = [0] * size
        vector[column] = 1
        columns.append(_execute_prepared(vector, prepared, modulus))
    return [[columns[column][row] for column in range(size)]
            for row in range(size)]


def _assert_operator(matrix, operations, modulus, label, alphabet):
    size = len(matrix)
    prepared = _prepare(operations, size, modulus, alphabet)
    for column in range(size):
        vector = [0] * size
        vector[column] = 1
        observed = _execute_prepared(vector, prepared, modulus)
        for row, value in enumerate(observed):
            _require(value == matrix[row][column],
                     f"{label} operator coefficient ({row},{column}): "
                     f"{value} != {matrix[row][column]}")


def _pivot_positions(matrix, modulus):
    """Independent Schur-complement calculation, only clearing below pivots.

    The constructor may clear above pivots immediately or in a separate pass;
    that presentation does not enter this first-unit current-row check.
    Returned positions are the current array indices before each swap.
    """
    residual = [row[:] for row in matrix]
    chosen = []
    for k in range(len(matrix)):
        candidates = [r for r in range(k, len(matrix))
                      if gcd(residual[r][k], modulus) == 1]
        _require(candidates, "unit pivot exists")
        pivot = candidates[0]
        chosen.append(pivot)
        residual[k], residual[pivot] = residual[pivot], residual[k]
        inverse = pow(residual[k][k], -1, modulus)
        for row in range(k + 1, len(matrix)):
            multiplier = residual[row][k] * inverse % modulus
            # A nonzero q-multiple is retained, even though its low digit is 0.
            if multiplier:
                residual[row] = [(x - multiplier * y) % modulus
                                 for x, y in zip(residual[row], residual[k])]
    return chosen


def _reversed_call(state, head, data, weights, modulus):
    """F_A(H,D)=(A C D, C A^-1 H) on disjoint explicit atom lists."""
    _require(len(head) == len(data) == len(weights), "child dimensions")
    _require(len(set(head + data)) == len(head) + len(data),
             "child coordinate disjointness")
    old_h = [state[i] for i in head]
    old_d = [state[i] for i in data]
    for t, (h, d) in enumerate(zip(head, data)):
        opposite = len(head) - 1 - t
        _require(gcd(weights[t], modulus) == 1, "child head unit")
        _require(gcd(weights[opposite], modulus) == 1, "child data unit")
        state[h] = weights[t] * old_d[opposite] % modulus
        state[d] = pow(weights[opposite], -1, modulus) * old_h[opposite] % modulus


def _field_op(raw, fields, modulus, atoms):
    """Admit scalar or per-atom descriptors without reversing the descriptor."""
    if (isinstance(raw, (list, tuple)) and len(raw) == 4
            and raw[0] in {"lower", "weighted_swap"}
            and isinstance(raw[3], (list, tuple))):
        _require(len(raw[3]) == atoms, "coefficient descriptor dimension")
        weights = [_integer(x, "integer atom coefficient") % modulus for x in raw[3]]
        kind, i, j, _ = _op([raw[0], raw[1], raw[2], weights[0]],
                            fields, modulus, {"lower", "weighted_swap", "sign"})
        if kind == "weighted_swap":
            _require(all(gcd(x, modulus) == 1 for x in weights),
                     "every atom weight is a unit")
        return kind, i, j, weights
    kind, i, j, c = _op(raw, fields, modulus,
                        {"lower", "weighted_swap", "sign"})
    return kind, i, j, [c] * atoms


def _orientations(orientations, fields):
    if orientations is None:
        return [1] * fields
    _require(len(orientations) == fields and
             all(type(x) is int and x in {-1, 1} for x in orientations),
             "active field orientations")
    return list(orientations)


def execute_fields(vector, operations, modulus, fields, atoms,
                   *, field_positions=None, orientations=None, omit_tail_reversal=False):
    """Execute supplied lower word through literal reversed children.

    Extra coordinates are complete spectator fields.  Logical atom j occupies
    physical atom j for orientation +1 and atoms-1-j for orientation -1.
    Oppositely oriented fields need one F_A; equally oriented fields use the
    literal R_tail F_A R_tail.  The optional defective branch exists solely
    for the test that detects an omitted tail reversal.
    """
    _require(type(atoms) is int and atoms >= 1, "positive atom count")
    _require(len(vector) >= fields * atoms and len(vector) % atoms == 0,
             "complete fields")
    if field_positions is None:
        field_positions = list(range(fields))
    _require(len(field_positions) == fields and len(set(field_positions)) == fields
             and all(type(p) is int and 0 <= p < len(vector) // atoms
                     for p in field_positions), "active complete field placement")
    orientations = _orientations(orientations, fields)
    state = [x % modulus for x in vector]
    for raw in operations:
        kind, i, j, weights = _field_op(raw, fields, modulus, atoms)
        physical_i = field_positions[i]
        first = list(range(physical_i * atoms, (physical_i + 1) * atoms))
        if kind == "sign":
            for index in first:
                state[index] = -state[index] % modulus
        elif kind == "lower":
            physical_j = field_positions[j]
            _require(physical_i > physical_j, "physical later-target addition")
            for logical_atom in range(atoms):
                target_atom = logical_atom if orientations[i] == 1 else atoms - 1 - logical_atom
                source_atom = logical_atom if orientations[j] == 1 else atoms - 1 - logical_atom
                target = physical_i * atoms + target_atom
                source = physical_j * atoms + source_atom
                state[target] = (state[target] + weights[logical_atom] * state[source]) % modulus
        else:
            physical_j = field_positions[j]
            second = list(range(physical_j * atoms, (physical_j + 1) * atoms))
            half = atoms // 2
            left = second[:half]
            right = second[atoms - half:] if half else []
            same_orientation = orientations[i] == orientations[j]
            physical_weights = weights if orientations[i] == 1 else weights[::-1]
            if same_orientation and half and not omit_tail_reversal:
                _reversed_call(state, left, right, [1] * half, modulus)
            _reversed_call(state, first, second, physical_weights, modulus)
            if same_orientation and half:
                _reversed_call(state, left, right, [1] * half, modulus)
    return state


def audit_fields(matrix, operations, modulus, *, atoms, spectator_fields=2,
                 matrices_by_atom=None, field_positions=None, orientations=None,
                 omit_tail_reversal=False):
    """Check logical atom matrices plus identity on every spectator coefficient."""
    fields = len(matrix)
    _require(type(atoms) is int and atoms >= 1, "positive atom count")
    if matrices_by_atom is None:
        matrices_by_atom = [_matrix(matrix, fields, modulus)] * atoms
    else:
        _require(len(matrices_by_atom) == atoms, "target atom matrix count")
        matrices_by_atom = [_matrix(item, fields, modulus) for item in matrices_by_atom]
    _require(type(spectator_fields) is int and spectator_fields >= 1,
             "at least one arbitrary complete spectator field")
    size = (fields + spectator_fields) * atoms
    if field_positions is None:
        field_positions = list(range(fields))
    _require(len(field_positions) == fields and len(set(field_positions)) == fields
             and all(type(p) is int and 0 <= p < fields + spectator_fields
                     for p in field_positions), "active complete field placement")
    logical = {physical: active for active, physical in enumerate(field_positions)}
    orientations = _orientations(orientations, fields)
    for column in range(size):
        vector = [0] * size
        vector[column] = 1
        observed = execute_fields(vector, operations, modulus, fields, atoms,
                                  field_positions=field_positions,
                                  orientations=orientations,
                                  omit_tail_reversal=omit_tail_reversal)
        source_physical, source_atom = divmod(column, atoms)
        source_field = logical.get(source_physical)
        for row, value in enumerate(observed):
            output_physical, output_atom = divmod(row, atoms)
            output_field = logical.get(output_physical)
            expected = 0
            if source_field is not None and output_field is not None:
                source_logical_atom = (source_atom if orientations[source_field] == 1
                                       else atoms - 1 - source_atom)
                output_logical_atom = (output_atom if orientations[output_field] == 1
                                       else atoms - 1 - output_atom)
                if source_logical_atom == output_logical_atom:
                    expected = matrices_by_atom[source_logical_atom][output_field][source_field]
            elif source_field is None and row == column:
                expected = 1
            _require(value == expected,
                     f"repeated-field operator coefficient ({row},{column}), "
                     f"atoms={atoms}: {value} != {expected}")
    weighted = sum(raw[0] == "weighted_swap" for raw in operations)
    same_orientation = sum(raw[0] == "weighted_swap" and
                           orientations[raw[1]] == orientations[raw[2]]
                           for raw in operations)
    histogram = {str(atoms): weighted}
    if atoms >= 2 and same_orientation:
        histogram[str(atoms // 2)] = 2 * same_orientation
    return {"atoms": atoms, "spectator_fields": spectator_fields,
            "active_field_positions": field_positions,
            "orientations": orientations,
            "basis_columns": size, "coefficients_checked": size * size,
            "same_orientation_swaps": same_orientation,
            "opposite_orientation_swaps": weighted - same_orientation,
            "reversed_children": sum(histogram.values()),
            "child_width_histogram": histogram}


def audit_plan(matrix, plan, *, atoms=None, spectator_fields=2):
    """Consume a supplied plan; do not regenerate it or trust cost claims."""
    q = _integer(plan["q"], "integer q")
    w = _integer(plan["w"], "integer w")
    _require(q >= 2 and w >= 1, "ring parameters")
    modulus = q ** w
    size = _integer(plan["N"], "integer dimension")
    m = _integer(plan["m"], "integer block count")
    _require(m >= 1 and size == 2 * m, "N=2m")
    source = _matrix(matrix, size, modulus)
    reductions = plan["reductions"]
    operations = plan["operations"]
    lower = plan["lowered_operations"]
    pivots = plan["pivots"]
    _require(pivots == _pivot_positions(source, modulus), "first-unit current-row pivots")
    diagonal = [_integer(x, "integer diagonal") % modulus
                for x in plan["diagonal"]]
    _require(len(diagonal) == size, "diagonal dimension")
    product = 1
    for x in diagonal:
        _require(gcd(x, modulus) == 1, "diagonal unit")
        product = product * x % modulus
    declared_sign = _integer(plan["diagonal_sign"], "integer diagonal sign") % modulus
    _require(product == declared_sign and product in {1, (-1) % modulus},
             "diagonal product is declared fixed sign")
    prepared_reductions = _prepare(reductions, size, modulus, {"swap", "add"})
    for column in range(size):
        observed = _execute_prepared([source[r][column] for r in range(size)],
                                    prepared_reductions, modulus)
        expected = [diagonal[column] if r == column else 0 for r in range(size)]
        _require(observed == expected, f"reduction column {column} reaches diagonal")
    _assert_operator(source, operations, modulus, "compiled",
                     {"swap", "add", "pair", "sign"})
    _assert_operator(source, lower, modulus, "lowered",
                     {"lower", "weighted_swap", "sign"})
    additions = sum(raw[0] == "add" for raw in reductions)
    swaps = sum(raw[0] == "swap" for raw in reductions)
    _require(additions <= size * (size - 1), "reduction addition allowance")
    _require(swaps <= size, "reduction swap allowance")
    low_additions = sum(raw[0] == "lower" for raw in lower)
    weighted = sum(raw[0] == "weighted_swap" for raw in lower)
    signs = sum(raw[0] == "sign" for raw in lower)
    _require(low_additions <= size * (size - 1), "paid additive adapter allowance")
    _require(signs <= 1, "fixed sign allowance")
    allowance = 6 * size * (size - 1) + 3 * size + 6 * (size - 1)
    _require(3 * weighted <= allowance, "actual conservative child allowance")
    _require(allowance < 32 * m * m, "32m^2 child inequality")
    report = {"modulus": modulus, "N": size, "m": m,
              "scalar_coefficients_checked": 3 * size * size,
              "reduction_additions": additions, "reduction_swaps": swaps,
              "lower_additions": low_additions, "weighted_swaps": weighted,
              "conservative_reversed_children": 3 * weighted,
              "symbolic_child_allowance": allowance,
              "primality": "external premise, not certified by this oracle"}
    if atoms is not None:
        report["fields"] = audit_fields(source, lower, modulus, atoms=atoms,
                                        spectator_fields=spectator_fields)
    return report


def audit_template(plan):
    """Separate fixed-slot obligation; identity elisions fail this contract.

    Scalar operator equality intentionally permits equivalent presentations.
    This stronger check concerns the declared compiler skeleton needed for
    batching every high lift and all diagonal weights of a low class.
    """
    size = plan["N"]
    _require(type(size) is int and size >= 2 and size % 2 == 0,
             "template dimension")
    _require(len(plan["pivots"]) == size, "template complete pivot list")
    reductions = plan["reductions"]
    cursor = 0
    for k, pivot in enumerate(plan["pivots"]):
        if pivot != k:
            _require(cursor < len(reductions) and
                     reductions[cursor] == ["swap", k, pivot],
                     "template pivot swap slot")
            cursor += 1
        for i in range(size):
            if i == k:
                continue
            _require(cursor < len(reductions) and
                     reductions[cursor][:3] == ["add", i, k],
                     "template complete shear slots")
            cursor += 1
    _require(cursor == len(reductions), "template reduction exhaustion")
    pairs = plan["operations"][:size - 1]
    _require(len(pairs) == size - 1 and
             all(op[:3] == ["pair", i, size - 1] for i, op in enumerate(pairs)),
             "template all diagonal pair slots")
    return {"shear_slots": size * (size - 1), "pair_slots": size - 1}


def audit_weighted_block(matrix, weights_by_atom, block, *, spectator_fields=3,
                         field_positions=None, orientations=None):
    """Derive B_j M B_j^-1 directly from inputs, then audit supplied fields.

    In particular, the target is not trusted merely because the compiler
    returned it as block['matrices_by_atom'].
    """
    q = _integer(block["q"], "integer q")
    w = _integer(block["w"], "integer w")
    _require(q >= 2 and w >= 1, "ring parameters")
    modulus = q ** w
    size = _integer(block["N"], "integer dimension")
    source = _matrix(matrix, size, modulus)
    atoms = len(weights_by_atom)
    _require(atoms >= 1 and block["atoms"] == atoms, "weighted block atom count")
    targets = []
    for weights in weights_by_atom:
        _require(len(weights) == size, "ancestor weight dimensions")
        for x in weights:
            _require(type(x) is int and gcd(x, modulus) == 1, "ancestor unit weight")
        inverse = [pow(x, -1, modulus) for x in weights]
        targets.append([[weights[i] * source[i][j] * inverse[j] % modulus
                         for j in range(size)] for i in range(size)])
    _require(block["matrices_by_atom"] == targets, "independent weighted target binding")
    _require(len(block["plans"]) == atoms, "weighted column plan count")
    topology = None
    for target, plan in zip(targets, block["plans"]):
        _require(plan["q"] == q and plan["w"] == w, "weighted ring binding")
        audit_plan(target, plan)
        audit_template(plan)
        current = [tuple(op[:3]) for op in plan["lowered_operations"]]
        if topology is None:
            topology = current
        _require(current == topology, "common weighted instruction topology")
        _require(plan["pivots"] == block["pivots"], "common weighted pivot itinerary")
    _require([tuple(op[:3]) for op in block["lowered_operations"]] == topology,
             "emitted block instruction topology")
    return audit_fields(source, block["lowered_operations"], modulus, atoms=atoms,
                        spectator_fields=spectator_fields, field_positions=field_positions,
                        orientations=orientations,
                        matrices_by_atom=targets)


def bad_chart_operator(m, rank, q, w):
    """Construct the bad chart through independent vector conjugations.

    G embeds [[q,q-1],[1,1]] on axes 0,rank, with integer inverse
    [[1,1-q],[-1,q]].  P0 projects onto the first rank coordinates.
    The canonical residual exchanges head i and reversed tail i for i<rank.
    We compute G P0 G^-1 and QG D_P0 QG^-1 on each basis input, where
    QG=diag(G,C_m G C_m).  No projector-entry or residual-block formula from
    the compiler is used.  The explicit invertible conjugacy witnesses split
    rank rank, rather than merely checking idempotence.

    This construction is integral and needs no primality test.  Its entry q
    is nonzero modulo q**w exactly when w>=2; the fallback's universal
    local-ring guarantee retains the separate prime-q premise.
    """
    _require(type(m) is int and m >= 2 and type(rank) is int and 1 <= rank < m,
             "bad chart dimensions")
    _require(type(q) is int and q >= 2 and type(w) is int and w >= 1,
             "bad chart ring parameters")
    modulus = q ** w

    def two_coordinates(vector, first, second, inverse):
        a, b = vector[first], vector[second]
        if inverse:
            vector[first] = (a + (1 - q) * b) % modulus
            vector[second] = (-a + q * b) % modulus
        else:
            vector[first] = (q * a + (q - 1) * b) % modulus
            vector[second] = (a + b) % modulus

    projector_columns = []
    for column in range(m):
        state = [0] * m
        state[column] = 1
        two_coordinates(state, 0, rank, True)
        for coordinate in range(rank, m):
            state[coordinate] = 0
        two_coordinates(state, 0, rank, False)
        projector_columns.append(state)

    residual_columns = []
    for column in range(2 * m):
        state = [0] * (2 * m)
        state[column] = 1
        two_coordinates(state, 0, rank, True)
        two_coordinates(state, 2 * m - 1, 2 * m - 1 - rank, True)
        for active in range(rank):
            tail = 2 * m - 1 - active
            state[active], state[tail] = state[tail], state[active]
        two_coordinates(state, 0, rank, False)
        two_coordinates(state, 2 * m - 1, 2 * m - 1 - rank, False)
        residual_columns.append(state)

    return {
        "projector": [[projector_columns[j][i] for j in range(m)]
                      for i in range(m)],
        "residual": [[residual_columns[j][i] for j in range(2 * m)]
                     for i in range(2 * m)],
        "split_rank": rank,
        "dimension": m,
        "modulus": modulus,
    }
