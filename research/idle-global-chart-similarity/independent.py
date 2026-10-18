#!/usr/bin/env python3
"""Independent primitive/cut replay and complete Boolean-quadratic trace sums.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
Physical event semantics and the inverse row/column strategy are transcribed
from the Gonzalo-Mier/PR3199-lineage interpreter and Ross Richardson's PR3275
independent verifier. No operator routine from either verifier or the current
primary cut model is imported. Only authenticated canonical data parsing and
context preparation are reused. Every amplitude computation is exact.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE = "463113d675af7410ac91d53a4fed51ec6494eb9a"
BITS = 73
ZERO = (0, 0)
ONE = (1, 0)
CHARACTERS = (0, 1, 2, 3, 16, 17, 33554432, 33554448, 33554449,
              (1 << BITS) - 1)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def plus(a, b):
    return a[0] + b[0], a[1] + b[1]


def times(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def turn(a, exponent):
    return (a, (-a[1], a[0]), (-a[0], -a[1]), (a[1], -a[0]))[exponent % 4]


def bits(mask):
    while mask:
        value = mask & -mask
        yield value.bit_length() - 1
        mask ^= value


def unit(size=8):
    return [[ONE if row == column else ZERO for column in range(size)]
            for row in range(size)]


def product(left, right):
    require(len(left[0]) == len(right), "matrix product dimensions")
    answer = [[ZERO for _ in right[0]] for _ in left]
    for row, entries in enumerate(left):
        for middle, value in enumerate(entries):
            if value != ZERO:
                for column, other in enumerate(right[middle]):
                    if other != ZERO:
                        answer[row][column] = plus(answer[row][column], times(value, other))
    return answer


def gaussian_power(value, exponent):
    answer = ONE
    while exponent:
        if exponent % 2:
            answer = times(answer, value)
        value = times(value, value)
        exponent //= 2
    return answer


def fourth_power(matrix):
    square = product(matrix, matrix)
    return product(square, square)


def first_difference(left, right):
    for row, entries in enumerate(left):
        for column, value in enumerate(entries):
            if value != right[row][column]:
                return {"row": row, "column": column, "actual": list(value),
                        "expected": list(right[row][column])}
    return None


def authenticate_context():
    manifest_path = PACKAGE / "SOURCES.json"
    require(manifest_path.is_file() and not manifest_path.is_symlink(), "missing/linked source manifest")
    manifest = json.loads(manifest_path.read_bytes())
    require(manifest["base_commit"] == BASE, "base pin")
    bound = {}
    for record in manifest["files"]:
        if record["usage"] != "input":
            continue
        path = ROOT / record["path"]
        require(path.is_file() and not path.is_symlink(), "missing/linked input " + record["path"])
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == record["sha256"], "source SHA256 " + record["path"])
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw,
                            usedforsecurity=False).hexdigest()
        require(blob == record["git_blob"], "source Git blob " + record["path"])
        bound[record["path"]] = raw
    relative = "research/idle-star-paired-axis-census/verify.py"
    require(relative in bound, "canonical data-parser binding")
    path = ROOT / relative
    retained = types.ModuleType("canonical_data_parser_exact_bytes")
    retained.__file__ = str(path)
    # The exact authenticated immutable bytes execute, with historical asserts
    # enabled. No normal import or bytecode cache can substitute another source.
    exec(compile(bound[relative], str(path), "exec", optimize=0), retained.__dict__)
    retained.authenticate()
    vendor = retained.PACKAGE / "vendor"
    base = retained.decode(retained.read_bytes(vendor / "BASE-FILL.json.gz"))["rows"]
    journal = retained.decode(retained.read_bytes(vendor / "EXCHANGE.json"))
    rows = retained.project_all_ports(base, retained.journal_edits(base, journal))
    allocation = ROOT / "research/rank7-joint-endframes/allocation"
    order0 = retained.decode(retained.read_bytes(allocation / "ORDER.json"))
    order = [[stage, owner + 74 * replica] for stage, owner in order0 for replica in range(10)]
    dispatch = {(stage, owner): tag for stage, owner, tag in
                retained.decode(retained.read_bytes(allocation / "DISPATCH.json"))}
    providers = retained.decode(retained.read_bytes(vendor / "PROVIDERS.json"))
    plan = retained.decode(retained.read_bytes(allocation / "vendor/PLAN.json.gz"))
    template = retained.decode(retained.read_bytes(allocation / "vendor/TEMPLATE.json.gz"))
    recipes = retained.decode(retained.read_bytes(ROOT / "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"))["recipes"]
    context = retained.prepare_port(0, rows[0], order, dispatch, providers, plan, template, recipes)
    return context, retained.TOTAL_ROWS, hashlib.sha256(bound[relative]).hexdigest()


# A phase is q(x) = sum a_j x_j + 2 sum_(j<k) b_jk x_j x_k mod4.
# The representation uses a tuple of all linear coefficients and upper-row
# bitsets; it is canonical as a function on binary inputs. No constant occurs
# in the circuit phases. Gaussian-sum elimination accumulates constants in
# its external Gaussian-integer multiplier instead.
def zero_phase(n=BITS):
    return (bytes(n), (0,) * n)


@lru_cache(maxsize=None)
def phase_add(left, right):
    return (bytes((a + b) % 4 for a, b in zip(left[0], right[0], strict=True)),
            tuple(a ^ b for a, b in zip(left[1], right[1], strict=True)))


@lru_cache(maxsize=None)
def phase_negate(phase):
    return (bytes((-a) % 4 for a in phase[0]), phase[1])


def parity_phase(mask, exponent=1, n=BITS):
    exponent %= 4
    linear = [0] * n
    edges = [0] * n
    for index in bits(mask):
        require(index < n, "phase address range")
        linear[index] = exponent
        if exponent % 2:
            edges[index] = mask & ~((1 << (index + 1)) - 1)
    return bytes(linear), tuple(edges)


def population_phase(mask, exponent=1, n=BITS):
    linear = [0] * n
    for index in bits(mask):
        linear[index] = exponent % 4
    return bytes(linear), (0,) * n


def axes_phase(axes):
    result = zero_phase()
    for axis in axes:
        result = phase_add(result, parity_phase(axis))
    return result


def phase_value(phase, character):
    linear, edges = phase
    exponent = sum(linear[index] for index in bits(character))
    exponent += 2 * sum((edges[index] & character).bit_count() for index in bits(character))
    return exponent % 4


@lru_cache(maxsize=None)
def gaussian_sum(phase):
    """Exact sum over every binary address, by one- or two-variable sums.

    For odd a, sum_t i^(a*t+2*t*L)=(1+i^a)*i^(-a*L).
    When all linear coefficients are even, an edge (u,v) gives
    sum_(s,t) (-1)^(s*t+U*s+V*t)=2*(-1)^(U*V).
    Both identities follow by their two or four literal input values.
    These substitutions eliminate all variables without sampling addresses.
    """
    linear = list(phase[0])
    n = len(linear)
    adjacency = [0] * n
    for left, row in enumerate(phase[1]):
        for right in bits(row):
            adjacency[left] ^= 1 << right
            adjacency[right] ^= 1 << left
    live = (1 << n) - 1
    factor = ONE
    while live:
        odd = next((index for index in bits(live) if linear[index] % 2), None)
        if odd is not None:
            coefficient = linear[odd]
            neighbors = adjacency[odd] & live
            factor = times(factor, plus(ONE, turn(ONE, coefficient)))
            # -a*parity(neighbors) has coefficients -a and all pair
            # coefficients 2, since a is odd.
            for index in bits(neighbors):
                linear[index] = (linear[index] - coefficient) % 4
                for other in bits(neighbors & ~((1 << (index + 1)) - 1)):
                    adjacency[index] ^= 1 << other
                    adjacency[other] ^= 1 << index
                adjacency[index] &= ~(1 << odd)
            live &= ~(1 << odd)
            continue
        left = next(bits(live))
        neighbors = adjacency[left] & live
        if not neighbors:
            if linear[left] == 2:
                return ZERO
            require(linear[left] == 0, "even isolated coefficient")
            factor = (2 * factor[0], 2 * factor[1])
            live &= ~(1 << left)
            continue
        right = next(bits(neighbors))
        remaining = live & ~(1 << left) & ~(1 << right)
        u = adjacency[left] & remaining
        v = adjacency[right] & remaining
        u0, v0 = linear[left] // 2, linear[right] // 2
        if u0 and v0:
            factor = (-factor[0], -factor[1])
        factor = (2 * factor[0], 2 * factor[1])
        linear_toggle = (v if u0 else 0) ^ (u if v0 else 0) ^ (u & v)
        for index in bits(linear_toggle):
            linear[index] ^= 2
        for index in bits(remaining):
            higher = remaining & ~((1 << (index + 1)) - 1)
            toggles = ((v & higher) if (u >> index) & 1 else 0) ^ ((u & higher) if (v >> index) & 1 else 0)
            for other in bits(toggles):
                adjacency[index] ^= 1 << other
                adjacency[other] ^= 1 << index
            adjacency[index] &= ~(1 << left) & ~(1 << right)
        live = remaining
    return factor


@lru_cache(maxsize=None)
def component_sum(phase):
    """Independent oracle: factor components and enumerate each in full.

    Every source trace phase has quadratic connected components of at most
    three bits; all73-bit summation then factors into these finite sums and
    independent one-bit sums. The size guard is an explicit algorithm domain,
    rather than an incomplete enumeration of any large connected component.
    """
    n = len(phase[0])
    adjacency = [0] * n
    for left, row in enumerate(phase[1]):
        for right in bits(row):
            adjacency[left] |= 1 << right
            adjacency[right] |= 1 << left
    unvisited = (1 << n) - 1
    answer = ONE
    sizes = []
    while unvisited:
        seed = unvisited & -unvisited
        unvisited ^= seed
        pending, component = seed, 0
        while pending:
            current = pending & -pending
            pending ^= current
            component |= current
            index = current.bit_length() - 1
            fresh = adjacency[index] & unvisited
            unvisited ^= fresh
            pending |= fresh
        indices = tuple(bits(component))
        require(len(indices) <= 12, "quadratic component exceeds exhaustive oracle domain")
        sizes.append(len(indices))
        subtotal = ZERO
        for pattern in range(1 << len(indices)):
            address = sum(1 << index for offset, index in enumerate(indices) if (pattern >> offset) & 1)
            subtotal = plus(subtotal, turn(ONE, phase_value(phase, address)))
        answer = times(answer, subtotal)
    return answer, tuple(sizes)


def literal_word(context, residual):
    """Independent transcription to phase, shear, and signed-exchange gates."""
    recipe = context["recipe"]
    q = parity_phase(recipe["q"])
    local = {event["stage"]: event for event in context["template"]["recipe"]
             if event["kind"] == "local"}
    stages = {}
    current = None
    for event in context["template"]["execution_schedule"]:
        kind = event["kind"]
        if kind in {"bank_padding_cover_sweep", "translate_every_live_family"}:
            continue
        if kind == "local_cover_sweep":
            current = event["stage"]
            require(current not in stages, "unique local stage")
            stages[current] = []
        require(current is not None, "event after stage boundary")
        stages[current].append(event)
    require(set(stages) == set(local) == set(range(9)), "complete local chronology")
    operations, sites = [], {}

    def phase(stream, exponent, label):
        operations.append(("phase", stream, exponent, 0, label))

    def shear(destination, source, coefficient, label):
        require(destination != source and coefficient in {-1, 1}, "literal source shear")
        operations.append(("add", destination, source, coefficient, label))

    for time, (stage, owner) in enumerate(context["order"]):
        for index, (stream, axes) in enumerate(context["hosts"].get(time, ())):
            phase(stream, axes_phase(tuple(axes)), f"host:{time}:{index}")
        if owner != 0:
            continue
        for event in stages[stage]:
            kind = event["kind"]
            if kind == "local_cover_sweep":
                item = local[stage]
                x, y = 2 * item["pair"], 2 * item["pair"] + 1
                if stage == 0:
                    entering = (q, zero_phase())
                else:
                    low = population_phase((1 << (9 + 8 * (stage - 1))) - 1)
                    entering = (low, phase_add(low, phase_negate(q)))
                phase(x, phase_negate(entering[0]), f"local-enter:{stage}:X")
                phase(y, phase_negate(entering[1]), f"local-enter:{stage}:Y")
                if item["reverse"]:
                    shear(x, y, -1, f"local-source:{stage}")
                else:
                    shear(y, x, 1, f"local-source:{stage}")
                low = population_phase((1 << (9 + 8 * stage)) - 1)
                phase(x, low, f"local-exit:{stage}:X")
                phase(y, phase_add(low, phase_negate(q)), f"local-exit:{stage}:Y")
            elif kind == "idle_cover_sweep":
                for side, child in enumerate(event["child_indices"]):
                    require(child not in sites, "unique residual site")
                    stream = 2 * event["pair"] + side
                    sites[child] = len(operations)
                    phase(stream, axes_phase(tuple(residual[child])), f"residual:{child}")
                    translation = recipe["idle_children"][child]["translation_after"]
                    phase(stream, parity_phase(translation, 2), f"idle-translation:{child}")
            elif kind == "bridge":
                destination, source, coefficient = event["dst"], event["src"], event["coefficient"]
                shear(2 * destination, 2 * source, coefficient, f"bridge:{stage}:X:{destination}:{source}")
                shear(2 * source + 1, 2 * destination + 1, -coefficient, f"bridge:{stage}:Y:{source}:{destination}")
            elif kind == "terminal_Y_translations":
                for pair in event["pairs"]:
                    phase(2 * pair + 1, phase_add(q, q), f"terminal-translation:{pair}")
            elif kind == "terminal":
                for pair in range(event["pairs"]):
                    operations.append(("exchange", 2 * pair, 2 * pair + 1, 0, f"terminal-exchange:{pair}"))
            else:
                raise ValueError("unhandled literal event " + kind)
    require(set(sites) == set(range(20)), "all twenty residual cuts")
    return operations, sites


def apply_numeric(matrix, operation, character, inverse=False, on_right=False):
    kind, destination, source, coefficient, _ = operation
    if kind == "phase":
        power = phase_value(source, character) * (-1 if inverse else 1)
        if on_right:
            for row in matrix:
                row[destination] = turn(row[destination], power)
        else:
            matrix[destination] = [turn(value, power) for value in matrix[destination]]
    elif kind == "add":
        coefficient *= -1 if inverse else 1
        if on_right:
            # M(I+c e_d e_s^T): column_s += c column_d.
            for row in matrix:
                value = row[destination]
                row[source] = plus(row[source], (coefficient * value[0], coefficient * value[1]))
        else:
            matrix[destination] = [plus(a, (coefficient * b[0], coefficient * b[1]))
                                   for a, b in zip(matrix[destination], matrix[source], strict=True)]
    elif kind == "exchange":
        if on_right:
            for row in matrix:
                x, y = row[destination], row[source]
                row[destination], row[source] = (y, (-x[0], -x[1])) if inverse else ((-y[0], -y[1]), x)
        else:
            x, y = matrix[destination], matrix[source]
            matrix[destination], matrix[source] = ([(-a, -b) for a, b in y], x) if inverse else (y, [(-a, -b) for a, b in x])
    else:
        raise ValueError("unknown primitive")


def required_numeric(operations, cut, character, wrong_prefix_order=False):
    answer = [[turn(value, character.bit_count()) for value in row] for row in unit()]
    for operation in reversed(operations[cut + 1:]):
        apply_numeric(answer, operation, character, inverse=True)
    prefix = operations[:cut]
    for operation in reversed(prefix) if wrong_prefix_order else prefix:
        apply_numeric(answer, operation, character, inverse=True, on_right=True)
    return answer


def forward_numeric(operations, character, cut=None, replacement=None):
    answer = unit()
    for index, operation in enumerate(operations):
        if index == cut:
            answer = product(replacement, answer)
        else:
            apply_numeric(answer, operation, character)
    return answer


def poly_add(left, right, coefficient=1):
    result = dict(left)
    for phase, value in right.items():
        value = result.get(phase, 0) + coefficient * value
        if value:
            result[phase] = value
        else:
            result.pop(phase, None)
    return result


def poly_phase(poly, phase):
    return {phase_add(key, phase): value for key, value in poly.items()}


def poly_product(left, right):
    result = {}
    for key, value in left.items():
        for other, weight in right.items():
            combined = phase_add(key, other)
            result[combined] = result.get(combined, 0) + value * weight
    return {key: value for key, value in result.items() if value}


def apply_polynomial(matrix, operation, inverse=False, on_right=False):
    kind, destination, source, coefficient, _ = operation
    if kind == "phase":
        phase = phase_negate(source) if inverse else source
        if on_right:
            for row in matrix:
                row[destination] = poly_phase(row[destination], phase)
        else:
            matrix[destination] = [poly_phase(poly, phase) for poly in matrix[destination]]
    elif kind == "add":
        coefficient *= -1 if inverse else 1
        if on_right:
            for row in matrix:
                row[source] = poly_add(row[source], row[destination], coefficient)
        else:
            matrix[destination] = [poly_add(a, b, coefficient)
                                   for a, b in zip(matrix[destination], matrix[source], strict=True)]
    elif kind == "exchange":
        if on_right:
            for row in matrix:
                x, y = row[destination], row[source]
                row[destination], row[source] = (y, {key: -value for key, value in x.items()}) if inverse else ({key: -value for key, value in y.items()}, x)
        else:
            x, y = matrix[destination], matrix[source]
            matrix[destination], matrix[source] = ([{key: -value for key, value in p.items()} for p in y], x) if inverse else (y, [{key: -value for key, value in p.items()} for p in x])
    else:
        raise ValueError("unknown symbolic primitive")


def polynomial_product(left, right):
    answer = [[{} for _ in range(8)] for _ in range(8)]
    for row in range(8):
        for middle in range(8):
            if left[row][middle]:
                for column in range(8):
                    if right[middle][column]:
                        answer[row][column] = poly_add(answer[row][column], poly_product(left[row][middle], right[middle][column]))
    return answer


def target_polynomial():
    scalar = population_phase((1 << BITS) - 1)
    return [[{scalar: 1} if row == column else {} for column in range(8)] for row in range(8)]


def forward_polynomial(operations, cut=None, replacement=None):
    zero = zero_phase()
    answer = [[{zero: 1} if row == column else {} for column in range(8)] for row in range(8)]
    for index, operation in enumerate(operations):
        if index == cut:
            answer = polynomial_product(replacement, answer)
        else:
            apply_polynomial(answer, operation)
    return answer


def required_polynomial(operations, cut):
    answer = target_polynomial()
    for operation in reversed(operations[cut + 1:]):
        apply_polynomial(answer, operation, inverse=True)
    for operation in operations[:cut]:
        apply_polynomial(answer, operation, inverse=True, on_right=True)
    return answer


def evaluate_polynomial_matrix(matrix, character):
    answer = []
    for row in matrix:
        output = []
        for poly in row:
            value = ZERO
            for phase, coefficient in poly.items():
                value = plus(value, turn((coefficient, 0), phase_value(phase, character)))
            output.append(value)
        answer.append(output)
    return answer


def integrate_polynomial(polynomial):
    answer = ZERO
    for phase, coefficient in polynomial.items():
        value, _ = component_sum(phase)
        require(value == gaussian_sum(phase), "component enumeration and quadratic elimination agreement")
        answer = plus(answer, (coefficient * value[0], coefficient * value[1]))
    return answer


def equal_every_address(actual, expected):
    """Coefficientwise equality from a complete nonnegative squared norm.

    Distinct canonical phase functions need not be linearly independent under
    addition. Empty formal differences suffice, but any remaining expression
    is tested by summing its squared absolute value over the full address set.
    A zero sum of these nonnegative numbers forces every coefficient value0.
    """
    for row in range(8):
        for column in range(8):
            difference = poly_add(actual[row][column], expected[row][column], -1)
            conjugate = {phase_negate(phase): coefficient for phase, coefficient in difference.items()}
            norm = integrate_polynomial(poly_product(difference, conjugate))
            require(norm == ZERO, "complete all-address operator mismatch")


def integrated_trace(matrix):
    polynomial = {}
    for index in range(8):
        polynomial = poly_add(polynomial, matrix[index][index])
    return integrate_polynomial(polynomial), polynomial


def integrated_square_trace(matrix):
    polynomial = {}
    for row in range(8):
        for middle in range(8):
            polynomial = poly_add(polynomial, poly_product(matrix[row][middle], matrix[middle][row]))
    return integrate_polynomial(polynomial), polynomial


def native_trace_pair(rank, direction, phase_power, address_bits=BITS, streams=8):
    dimension = 1 << address_bits
    require(0 <= rank <= address_bits and direction in {-1, 1}, "native rank/direction")
    scale = 1 << (address_bits - rank)
    active_first = gaussian_power((1, direction), rank)
    active_first = (scale * active_first[0], scale * active_first[1])
    active_second = (dimension, 0) if rank == 0 else ZERO
    background = ((streams - 1) * dimension, 0)
    return plus(background, turn(active_first, phase_power)), plus(background, turn(active_second, 2 * phase_power))


def candidate_comparison(trace, trace_square, rank):
    candidates = []
    matches = []
    for direction in (-1, 1):
        for power in range(4):
            first, second = native_trace_pair(rank, direction, power)
            item = {"direction": direction, "active_phase_power": power,
                    "trace": list(first), "trace_squared": list(second)}
            candidates.append(item)
            if (trace, trace_square) == (first, second):
                matches.append(item)
    return candidates, matches


def phase_record(phase, coefficient):
    total, component_sizes = component_sum(phase)
    require(total == gaussian_sum(phase), "independent phase-sum agreement")
    return {"coefficient": coefficient, "linear": list(phase[0]), "quadratic_upper_rows": list(phase[1]),
            "all_address_sum": list(total), "quadratic_component_sizes": list(component_sizes)}


def reject_named(call, message):
    rejected = None
    try:
        call()
    except ValueError as error:
        rejected = str(error)
    require(rejected == message, "named rejection absent: " + message)


def check_fourth(matrix):
    require(fourth_power(matrix) == unit(len(matrix)), "fourth-power invariant")


def quadratic_controls():
    # Exhaust all mod4 linear and Boolean quadratic forms through dimension3;
    # dimension4 nontrivial edge/odd fixtures exercise larger elimination paths.
    count = 0
    for n in range(4):
        positions = list(itertools.combinations(range(n), 2))
        for linear in itertools.product(range(4), repeat=n):
            for pattern in range(1 << len(positions)):
                rows = [0] * n
                for index, (left, right) in enumerate(positions):
                    if (pattern >> index) & 1:
                        rows[left] |= 1 << right
                phase = (bytes(linear), tuple(rows))
                direct = ZERO
                for character in range(1 << n):
                    direct = plus(direct, turn(ONE, phase_value(phase, character)))
                require(gaussian_sum(phase) == direct, "complete small quadratic sum")
                require(component_sum(phase)[0] == direct, "complete component quadratic sum")
                count += 1
    for axis in range(1, 16):
        phase = parity_phase(axis, n=4)
        for character in range(16):
            require(phase_value(phase, character) == ((axis & character).bit_count() % 2), "parity-to-quadratic identity")
        require(gaussian_sum(phase) == component_sum(phase)[0] == (8, 8),
                "complete four-bit parity phase sum")
    return {"exhaustive_forms_through_dimension3": count, "dimension4_nonzero_parity_forms": 15,
            "address_domain_of_main_sums": 1 << BITS}


def cross_character_positive_control():
    # Two streams and two address bits, in address-major coordinates. A rank2
    # native tensor has active eigenvalues1,i,i,-1. An explicit global
    # permutation moves its two i eigenlines into the two-dimensional
    # character0 fiber, producing a rank-two defect there.
    diagonal = [ONE, ONE, (0, 1), ONE, (0, 1), ONE, (-1, 0), ONE]
    native = [[diagonal[row] if row == column else ZERO for column in range(8)] for row in range(8)]
    permutation = [2, 4, 0, 1, 3, 5, 6, 7]
    chart = [[ONE if column == permutation[row] else ZERO for column in range(8)] for row in range(8)]
    inverse_chart = [list(row) for row in zip(*chart, strict=True)]
    conjugate = product(chart, product(native, inverse_chart))
    require(conjugate[0][0] == conjugate[1][1] == (0, 1), "two nonidentity phases in one character")
    check_fourth(conjugate)
    require(product(conjugate, conjugate) != unit(), "nontrivial square control")
    before = sum(product(native, native)[j][j][0] for j in range(8))
    after = sum(product(conjugate, conjugate)[j][j][0] for j in range(8))
    require(before == after == 4, "global square trace survives cross-character chart")
    determinant = times((-1, 1), (-1, 1))
    require(determinant == (0, -2), "old per-character rank-two witness appears in legal chart")
    # Rank0 is a real boundary of the granted active-phase freedom. A phase i
    # on one rank0 active stream gives square trace6N in eight streams, so a
    # square-trace-only rejection at6N would be unsound. The first trace is
    # (7+i)N and the complete trace pair must accept it.
    rank_zero_pair = native_trace_pair(0, 1, 1)
    require(rank_zero_pair == ((7 * (1 << BITS), 1 << BITS), (6 * (1 << BITS), 0)),
            "rank-zero phase must be admitted")
    _, matches = candidate_comparison(*rank_zero_pair, 0)
    require(matches, "rank-zero phase accepted by full trace pair")
    # A genuinely broader middle alphabet changes the invariant. The action
    # i*Z_v, v nonzero, has active eigenvalues+i,-i on equal address halves,
    # so its pair is(7N,6N). It is not a pure scalar times any native C_r;
    # this control records a spectral reopening, not a completed cut repair.
    active = ((0, 1), (0, -1))
    active_first = plus(active[0], active[1])
    active_second = plus(times(active[0], active[0]), times(active[1], active[1]))
    small_pair = plus((14, 0), active_first), plus((14, 0), active_second)
    require(small_pair == ((14, 0), (12, 0)), "signed address-translation spectral control")
    _, pure_matches = candidate_comparison(((7 * (1 << BITS)), 0), ((6 * (1 << BITS)), 0), 0)
    require(not pure_matches, "expanded translation alphabet differs from pure native rankzero")
    bad = unit(2)
    bad[0][1] = ONE
    reject_named(lambda: check_fourth(bad), "fourth-power invariant")
    return {"streams": 2, "address_bits": 2, "native_rank": 2,
            "permutation_rows": permutation, "legitimate_conjugacy_accepted": True,
            "old_character0_defect_minor": list(determinant), "global_square_trace": [4, 0],
            "rank_zero_active_i_trace_pair_accepted": [list(value) for value in rank_zero_pair],
            "expanded_i_times_nonzero_translation_trace_pair": [[7 * (1 << BITS), 0], [6 * (1 << BITS), 0]],
            "expanded_translation_control_claims_cut_realization": False,
            "nonsemisimple_shear_rejected_by_fourth_power": True}


def literal_sensitivity_controls(baseline, sites):
    character = 1
    target = [[turn(value, 1) for value in row] for row in unit()]
    translation = next(index for index, operation in enumerate(baseline)
                       if operation[4].startswith("idle-translation:")
                       and phase_value(operation[2], character))
    omitted = forward_numeric(baseline[:translation] + baseline[translation + 1:], character)
    require(omitted != target, "active separate translation omission must fail")
    bridge = next(index for index, operation in enumerate(baseline)
                  if operation[4].startswith("bridge:"))
    changed = list(baseline)
    kind, destination, source, coefficient, label = changed[bridge]
    changed[bridge] = kind, destination, source, -coefficient, label
    wrong_source = forward_numeric(changed, character)
    require(wrong_source != target, "literal bridge-sign mutation must fail")
    correct = required_numeric(baseline, sites[12], character)
    require(forward_numeric(baseline, character, sites[12], correct) == target, "correct inverse order completes")
    wrong = required_numeric(baseline, sites[12], character, wrong_prefix_order=True)
    wrong_order = forward_numeric(baseline, character, sites[12], wrong)
    require(wrong_order != target, "noncommuting reversed-prefix mutation must fail")
    return {"character": character,
            "omitted_translation": {"label": baseline[translation][4], "difference": first_difference(omitted, target)},
            "changed_bridge_sign": {"label": baseline[bridge][4], "difference": first_difference(wrong_source, target)},
            "reversed_prefix_inverse_order": {"site": 12, "difference": first_difference(wrong_order, target)},
            "target_global_i_phase": True}


def run():
    context, rows, parser_hash = authenticate_context()
    original = {child: list(axes) for child, axes in context["residual"].items()}
    require([len(original[j]) for j in (10, 12)] == [48, 48], "literal old ranks")
    require(original[10].count(16) == 1 and 16 not in original[12], "literal transfer axis")
    moved = {child: list(axes) for child, axes in original.items()}
    moved[10].remove(16)
    moved[12].append(16)
    for child in range(20):
        combined = context["hosted_axes"].get(child, []) + moved[child]
        require(all(((left & right).bit_count() % 2) == int(i == j)
                    for i, left in enumerate(combined) for j, right in enumerate(combined)),
                "complete moved child orthonormality")
    operations, sites = literal_word(context, moved)
    baseline, baseline_sites = literal_word(context, original)
    require(sites == baseline_sites, "unchanged cut positions")
    equal_every_address(forward_polynomial(baseline), target_polynomial())
    fourth_witnesses = {}
    checks = 0
    for character in CHARACTERS:
        target = [[turn(value, character.bit_count()) for value in row] for row in unit()]
        require(forward_numeric(baseline, character) == target, "unchanged word exact target")
        for child in range(20):
            cut = sites[child]
            required = required_numeric(operations, cut, character)
            require(forward_numeric(operations, character, cut, required) == target, "cut completion all eight columns")
            literal = unit()
            apply_numeric(literal, baseline[cut], character)
            require(required_numeric(baseline, cut, character) == literal, "unchanged cut equals native child")
            difference = first_difference(fourth_power(required), unit())
            if difference and child not in fourth_witnesses:
                fourth_witnesses[child] = {"character": character, **difference}
            checks += 1
    global_traces = {}
    for child in range(20):
        matrix = required_polynomial(operations, sites[child])
        equal_every_address(forward_polynomial(operations, sites[child], matrix), target_polynomial())
        for character in CHARACTERS:
            require(evaluate_polynomial_matrix(matrix, character) == required_numeric(operations, sites[child], character),
                    "polynomial and numeric complete cut operator")
        first, first_polynomial = integrated_trace(matrix)
        second, second_polynomial = integrated_square_trace(matrix)
        candidates, matches = candidate_comparison(first, second, len(moved[child]))
        delta_first = plus(first, (-7 * (1 << BITS), 0))
        delta_second = plus(second, (-7 * (1 << BITS), 0))
        rank_zero_relation = times(delta_first, delta_first) == ((1 << BITS) * delta_second[0], (1 << BITS) * delta_second[1])
        global_traces[child] = {"native_rank": len(moved[child]), "trace_R": list(first),
                                "trace_R_squared": list(second),
                                "candidate_trace_pairs": candidates, "matching_candidates": matches,
                                "first_trace_terms": [phase_record(phase, coefficient) for phase, coefficient in sorted(first_polynomial.items())],
                                "square_trace_terms": [phase_record(phase, coefficient) for phase, coefficient in sorted(second_polynomial.items())],
                                "operator_terms": sum(len(poly) for row in matrix for poly in row),
                                "first_trace_terms_count": len(first_polynomial),
                                "square_trace_terms_count": len(second_polynomial),
                                "rank_zero_any_scalar_trace_relation": rank_zero_relation,
                                "excluded_for_every_native_rank_and_nonzero_scalar": second != (7 * (1 << BITS), 0) and not rank_zero_relation,
                                "excluded_by_trace_pair": not matches}
    excluded = [child for child in range(20) if global_traces[child]["excluded_by_trace_pair"]]
    maximum_component = max(size for entry in global_traces.values()
                            for field in ("first_trace_terms", "square_trace_terms")
                            for term in entry[field] for size in term["quadratic_component_sizes"])
    require(maximum_component <= 3, "source trace quadratic components at most3 bits")
    return {"status": "PASS_INDEPENDENT_GLOBAL_TRACE_PAIR_SCREEN", "base_commit": BASE,
            "source_manifest_sha256": hashlib.sha256((PACKAGE / "SOURCES.json").read_bytes()).hexdigest(),
            "canonical_parser_sha256": parser_hash, "authenticated_fill_rows": rows,
            "owner_replica": 0, "port": 0, "transfer": {"axis": 16, "donor": 10, "receiver": 12,
                "old_ranks": [48, 48], "candidate_ranks": [47, 49]},
            "sites": 20, "all_arbitrary_input_columns": 8, "address_bits": BITS,
            "primitive_operations": len(operations), "sample_characters": list(CHARACTERS),
            "finite_cut_completion_checks": checks, "finite_fourth_power_witnesses": fourth_witnesses,
            "complete_baseline_operator_columns": 8, "complete_cut_operator_checks": 20,
            "max_source_trace_quadratic_component_bits": maximum_component,
            "finite_fourth_power_surviving_sites": sorted(set(range(20)) - set(fourth_witnesses)),
            "global_square_traces": global_traces,
            "globally_excluded_sites": excluded, "globally_surviving_sites": sorted(set(range(20)) - set(excluded)),
            "middle_child_alphabet": "One pure scalar times C_r or its inverse on fixed active stream volumeN; all original separate translations fixed. Address-dependent phases such as iZ_v are a different alphabet and are not excluded.",
            "quadratic_sum_controls": quadratic_controls(), "global_conjugacy_control": cross_character_positive_control(),
            "literal_sensitivity_controls": literal_sensitivity_controls(baseline, baseline_sites),
            "new_kappa": None,
            "coverage": "All20 literal cuts/all8 arbitrary stream columns. Numeric powers cover only the listed characters. First and square traces are complete sums over all2^73 address characters via factorization over quadratic connected components (each at most3bits in source traces), independently checked by one-/two-variable Gaussian elimination; no sampled inference. Allactual moved-site ranks, both directions and allfour fourth-root active phases are compared. Every site also fails the necessary pair for every native rank0..73 and arbitrary nonzero active scalar. Dirty restored spectators add the same identity trace to both endpoints.",
            "independence": "No parent cut_model.py or retained operator routine imported. Canonical parser/context only; independently transcribed primitive chronology, Gaussian-integer inverse row/column cuts, canonical quadratic phases, exhaustive component-factorized exact sums and one-/two-variable Gaussian sums. Historical primitive strategy credited to PR3275."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = json.loads(json.dumps(run()))
    if arguments.output:
        with arguments.output.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        fixed = PACKAGE / "INDEPENDENT.json"
        require(fixed.is_file() and not fixed.is_symlink(), "missing fixed independent receipt")
        require(result == json.loads(fixed.read_bytes()), "independent fixed receipt mismatch")
    print("PASS_INDEPENDENT_GLOBAL_TRACE_PAIR sites=20 full_address_domain=2^73 no_new_kappa")


if __name__ == "__main__":
    main()
