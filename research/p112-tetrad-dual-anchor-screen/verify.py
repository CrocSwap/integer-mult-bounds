#!/usr/bin/env python3
"""Exact source-bound screen for reversible integer kernel frames on P112 tetrads."""
from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
D_EVEN_SUM = [
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [-1, -1, -1, 2],
]


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_module(name: str, path: Path):
    spec = spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "cannot load " + str(path))
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_source_pins() -> dict[str, str]:
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    result = {}
    for item in manifest["files"]:
        raw = (ROOT / item["path"]).read_bytes()
        digest = sha256(raw).hexdigest()
        need(digest == item["sha256"], "source hash changed: " + item["path"])
        result[item["path"]] = digest
    return result


def dot(a: list[int], b: list[int]) -> int:
    return sum(x * y for x, y in zip(a, b))


def transpose(a: list[list[int]]) -> list[list[int]]:
    return [list(row) for row in zip(*a)]


def matmul(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    need(bool(a) and bool(b) and len(a[0]) == len(b), "matrix product shape")
    return [[sum(a[i][k] * b[k][j] for k in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]


def determinant(matrix: list[list[int]]) -> int:
    """Fraction-free Bareiss determinant, including row-pivot sign."""
    n = len(matrix)
    need(n > 0 and all(len(row) == n for row in matrix), "determinant shape")
    a = [row[:] for row in matrix]
    sign, previous = 1, 1
    for col in range(n - 1):
        pivot_row = next((r for r in range(col, n) if a[r][col]), None)
        if pivot_row is None:
            return 0
        if pivot_row != col:
            a[col], a[pivot_row] = a[pivot_row], a[col]
            sign = -sign
        pivot = a[col][col]
        for i in range(col + 1, n):
            for j in range(col + 1, n):
                numerator = a[i][j] * pivot - a[i][col] * a[col][j]
                need(numerator % previous == 0, "Bareiss division was not exact")
                a[i][j] = numerator // previous
            a[i][col] = 0
        previous = pivot
    return sign * a[n - 1][n - 1]


def identity(n: int) -> list[list[int]]:
    return [[int(i == j) for j in range(n)] for i in range(n)]


def apply_row_op_matrix(matrix: list[list[int]], op: tuple) -> None:
    kind = op[0]
    if kind == "add":
        _, target, source, sign = op
        matrix[target] = [x + sign * y for x, y in zip(matrix[target], matrix[source])]
    elif kind == "swap":
        _, i, j = op
        matrix[i], matrix[j] = matrix[j], matrix[i]
    elif kind == "neg":
        _, i = op
        matrix[i] = [-x for x in matrix[i]]
    else:
        raise ValueError("unknown row operation")


def inverse_row_op(op: tuple) -> tuple:
    if op[0] == "add":
        return ("add", op[1], op[2], -op[3])
    return op


def reduce_to_identity(matrix: list[list[int]]) -> list[tuple]:
    """Synthesize a reversible integer row-operation word from matrix to I."""
    a = [row[:] for row in matrix]
    n = len(a)
    ops: list[tuple] = []

    def swap(i: int, j: int) -> None:
        a[i], a[j] = a[j], a[i]
        ops.append(("swap", i, j))

    def add(i: int, j: int, coefficient: int) -> None:
        if coefficient == 0:
            return
        sign = 1 if coefficient > 0 else -1
        for _ in range(abs(coefficient)):
            a[i] = [x + sign * y for x, y in zip(a[i], a[j])]
            ops.append(("add", i, j, sign))

    def negate(i: int) -> None:
        a[i] = [-x for x in a[i]]
        ops.append(("neg", i))

    for col in range(n):
        candidates = [i for i in range(col, n) if a[i][col]]
        need(bool(candidates), "unimodular matrix lost a pivot")
        pivot = min(candidates, key=lambda i: abs(a[i][col]))
        if pivot != col:
            swap(pivot, col)
        for i in range(col + 1, n):
            while a[i][col]:
                quotient = a[i][col] // a[col][col]
                add(i, col, -quotient)
                if a[i][col]:
                    swap(i, col)
        if a[col][col] < 0:
            negate(col)
        need(a[col][col] == 1, "non-unit pivot in a claimed unimodular matrix")
        for i in range(col):
            add(i, col, -a[i][col])

    need(a == identity(n), "integer row reduction did not reach identity")
    return ops


def apply_row_ops_vector(vector: list[int], ops: list[tuple]) -> list[int]:
    values = vector[:]
    for op in ops:
        if op[0] == "add":
            _, target, source, sign = op
            values[target] += sign * values[source]
        elif op[0] == "swap":
            _, i, j = op
            values[i], values[j] = values[j], values[i]
        elif op[0] == "neg":
            values[op[1]] = -values[op[1]]
        else:
            raise ValueError("unknown vector operation")
    return values


def rank_two(rows: list[list[int]]) -> int:
    """Exact rank of two short integer rows, using nonzero 2x2 minors."""
    need(len(rows) == 2 and len(rows[0]) == len(rows[1]), "rank input shape")
    if any(rows[0][i] * rows[1][j] != rows[0][j] * rows[1][i]
           for i in range(len(rows[0])) for j in range(i + 1, len(rows[0]))):
        return 2
    return int(any(rows[0]) or any(rows[1]))


def extended_complex_ceiling(engine, profile, centre, unpaid, grid=Q(1, 10**12)):
    """Find a certified complex moment root beyond ceiling.ceiling's 0.05 cap."""
    lo, hi = Q(0), Q(1, 20)
    while engine.relax(profile, 73, 896, 9, centre, hi,
                       R=51, unpaid=unpaid)[0] <= 1:
        hi *= 2
        need(hi <= Q(1, 10), "extended complex root escaped the checked exp range")
    while hi - lo > grid:
        mid = (lo + hi) / 2
        moment = engine.relax(profile, 73, 896, 9, centre, mid,
                              R=51, unpaid=unpaid)
        if moment[1] < 1:
            lo = mid
        elif moment[0] > 1:
            hi = mid
        else:
            raise ValueError("complex moment interval did not separate the root")
    return lo, hi


def main() -> None:
    pins = check_source_pins()
    geometry = load_module(
        "p112_geometry", ROOT / "research/p112-tetrad-local-decoder/verify.py")
    selected = load_module(
        "selected_p112_route", ROOT / "research/selected-p112-tetrad-rank32-route/verify.py")
    ceiling = load_module(
        "complex_ceiling", ROOT / "research/complex-local-word-ceiling/ceiling.py")
    bit_verify = load_module(
        "bit_revision3_verify", ROOT / "research/bit-revision3-levers-seed03/verify.py")
    bit_levers = load_module(
        "bit_revision3_levers", ROOT / "research/bit-revision3-levers-seed03/levers.py")

    selected_record = json.loads((ROOT / "certificates/selected-result.json").read_text())
    need(selected_record["kappa"] == "836330098538459/500000000000000000",
         "selected result changed")
    word, _ = selected.load_word()
    # This positive control binds the port permutation and the full P112 parity
    # graph before using the local tetrad partition.
    selected.build_bound_decoder(word)

    roots, frame = geometry.roots_and_frame()
    live = sorted(set(roots) - set(frame))
    need(len(live) == 112, "P112 live root count")
    gram = [[geometry.dot(x, y) // 4 for y in live] for x in live]
    pairing_labels = [
        sum(((value + 1) % 2) << j for j, value in enumerate(row))
        for row in gram
    ]
    pairing_masks_by_port = [0] * 112
    for root_i, port_i in enumerate(selected.ROOT_TO_PORT):
        mapped = 0
        for root_j, port_j in enumerate(selected.ROOT_TO_PORT):
            if pairing_labels[root_i] >> root_j & 1:
                mapped |= 1 << port_j
        pairing_masks_by_port[port_i] = mapped

    classes: dict[tuple[tuple[int, ...], int], list[tuple[int, list[int]]]] = defaultdict(list)
    for root_index, root in enumerate(live):
        coordinates = [geometry.dot(root, f) // 4 for f in frame]
        tetrad = tuple(j for j, value in enumerate(coordinates) if value)
        need(len(tetrad) == 4 and all(coordinates[j] in (-1, 1) for j in tetrad),
             "root is not a signed tetrad row")
        parity = sum(coordinates[j] < 0 for j in tetrad) % 2
        classes[tetrad, parity].append((root_index, coordinates))

    tetrads = sorted({t for t, _ in classes})
    need(len(tetrads) == 14, "tetrad block count")
    records = []
    all_ports = []
    all_flip_count = 0
    total_adds = total_swaps = total_negations = 0
    dirty_trials = 0
    original_decoder_profile: Counter[int] = Counter()
    fused_decoder_profile: Counter[int] = Counter()
    fused_decoder_matrix = [[0] * 112 for _ in range(112)]
    expected_fused_decoder_matrix = [[0] * 112 for _ in range(112)]
    for tetrad in tetrads:
        even, odd = classes[tetrad, 0], classes[tetrad, 1]
        need(len(even) == len(odd) == 4, "four-frame class size")
        coords = list(tetrad)
        e0 = [[v[j] for j in coords] for _, v in even]
        e1 = [[v[j] for j in coords] for _, v in odd]

        # Each class is an orthogonal four-frame, hence an invertible Hadamard matrix.
        for group in (e0, e1):
            for i, a in enumerate(group):
                for j, b in enumerate(group):
                    need(dot(a, b) == (4 if i == j else 0), "four-frame orthogonality")
            need(abs(determinant(group)) == 16, "four-frame determinant")

        uniform_even = [sum(v[j] for v in e0) for j in range(4)]
        uniform_odd = [sum(v[j] for v in e1) for j in range(4)]
        need(uniform_even == uniform_odd, "uniform class sums should coincide")
        need(sum(x * x for x in uniform_even) == 16, "uniform anchor norm")

        # Keep the earlier signed-anchor lead and its exact Gram control.
        first_signed_form = None
        for row in range(4):
            signed_odd = [sum((-1 if k == row else 1) * e1[k][j] for k in range(4))
                          for j in range(4)]
            need(rank_two([uniform_even, signed_odd]) == 2,
                 "one-sign-flip form must be independent")
            gram = [[dot(uniform_even, uniform_even), dot(uniform_even, signed_odd)],
                    [dot(signed_odd, uniform_even), dot(signed_odd, signed_odd)]]
            need(gram == [[16, 8], [8, 16]], "signed-anchor Gram matrix")
            if first_signed_form is None:
                first_signed_form = signed_odd
            all_flip_count += 1

        # E stacks two signed Hadamard frames. Its update K=E E^T has rank four.
        e = e0 + e1
        k = matmul(e, transpose(e))
        p = matmul(e0, transpose(e1))
        pd = matmul(p, D_EVEN_SUM)
        need(all(value % 4 == 0 for row in pd for value in row),
             "even-sum lattice did not clear the half-integral transition")
        n_top = [[-(value // 4) for value in row] for row in pd]
        kernel_columns = n_top + [row[:] for row in D_EVEN_SUM]
        kernel_rows = transpose(kernel_columns)
        complement = (0, 5, 6, 7)
        u = kernel_rows + [identity(8)[i] for i in complement]
        need(len(u) == 8 and len(u[0]) == 8, "basis transform shape")
        need(determinant(u) == -1, "integer kernel rows lack a unimodular completion")
        need(matmul(u, k)[:4] == [[0] * 8 for _ in range(4)],
             "first four transformed outputs change under the P112 update")

        # Fuse U into the decoder's output coefficient vectors instead of
        # executing the reversible row word on every live family role. The
        # original four tetrad terms are the columns of E E^T; composing U
        # on their output side gives (U E) E^T = U K exactly.
        u_e = matmul(u, e)
        need(u_e[:4] == [[0] * 4 for _ in range(4)],
             "kernel coefficient rows do not annihilate the update factors")
        block_root_indices = [i for i, _ in even + odd]
        block_ports = [selected.ROOT_TO_PORT[i] for i in block_root_indices]
        transformed_block = matmul(u, k)
        decoder_costs = []
        original_costs = []
        for column in range(4):
            d = [row[column] for row in u_e]
            t = [row[column] for row in e]
            d_support = [block_ports[i] for i, value in enumerate(d) if value]
            t_support = [block_ports[i] for i, value in enumerate(t) if value]
            t_mask = sum(1 << port for port in t_support)
            decoder_cost = selected.rank2(
                [pairing_masks_by_port[port] & t_mask for port in d_support])
            decoder_costs.append(decoder_cost)
            fused_decoder_profile[decoder_cost] += 1

            original_support = t_support
            original_mask = t_mask
            original_cost = selected.rank2(
                [pairing_masks_by_port[port] & original_mask
                 for port in original_support])
            original_costs.append(original_cost)
            original_decoder_profile[original_cost] += 1

            for i, d_value in enumerate(d):
                for j, t_value in enumerate(t):
                    fused_decoder_matrix[block_ports[i]][block_ports[j]] += (
                        d_value * t_value)
        for i, port_i in enumerate(block_ports):
            for j, port_j in enumerate(block_ports):
                expected_fused_decoder_matrix[port_i][port_j] = transformed_block[i][j]
        need(decoder_costs == [1] * 4,
             "composed output coefficients no longer have rank-one copy cost")
        need(original_costs == [2] * 4,
             "original selected tetrad terms no longer have rank-two copy cost")

        # The exact word transforms every arbitrary dirty output vector reversibly.
        reduction = reduce_to_identity(u)
        forward = [inverse_row_op(op) for op in reversed(reduction)]
        rebuilt = identity(8)
        for op in forward:
            apply_row_op_matrix(rebuilt, op)
        need(rebuilt == u, "synthesized reversible word does not equal U")
        adds = sum(op[0] == "add" for op in forward)
        swaps = sum(op[0] == "swap" for op in forward)
        negations = sum(op[0] == "neg" for op in forward)
        need((adds, swaps, negations) == (21, 2, 1),
             "reversible basis word cost changed")
        total_adds += adds
        total_swaps += swaps
        total_negations += negations

        dirty = [13, -5, 0, 21, -34, 8, 3, -11]
        changed = apply_row_ops_vector(dirty, forward)
        restored = apply_row_ops_vector(changed, reduction)
        need(restored == dirty, "dirty output restoration failed")
        dx = matmul(k, [[2], [-3], [5], [7], [-1], [4], [0], [6]])
        updated = [dirty[i] + dx[i][0] for i in range(8)]
        need(apply_row_ops_vector(updated, forward)[:4] == changed[:4],
             "kernel outputs are not invariant under an arbitrary update")
        dirty_trials += 1

        ports = sorted(selected.ROOT_TO_PORT[i] for i, _ in even + odd)
        need(len(ports) == 8 and len(set(ports)) == 8, "mapped port block")
        all_ports.extend(ports)
        records.append({
            "frame_coordinates": coords,
            "ports": ports,
            "uniform_class_sum": uniform_even,
            "first_single_sign_flip_form": first_signed_form,
            "kernel_rank": 4,
            "unimodular_determinant": -1,
            "forward_word": {"adds": adds, "swaps": swaps, "negations": negations},
        })

    need(len(all_ports) == 112 and sorted(all_ports) == list(range(112)),
         "mapped tetrads do not partition selected ports")
    need(all_flip_count == 56, "all one-row sign flips were not checked")
    need((total_adds, total_swaps, total_negations, dirty_trials) == (294, 28, 14, 14),
         "global reversible transform invoice changed")
    need(fused_decoder_matrix == expected_fused_decoder_matrix,
         "composed decoder terms do not equal the source-bound U K matrices")
    need(dict(original_decoder_profile) == {2: 56},
         "source-bound original decoder terms are not rank two")
    need(dict(fused_decoder_profile) == {1: 56},
         "fused output-coefficient terms are not rank one")

    # Charge every forward ADD, swap and negation as a rank-1 unit. If the old
    # output basis must be restored, charge the same invoice a second time.
    base_profile = {1: 192, 2: 56, 32: 166}
    per_direction_overcharge = 14 * (21 + 2 + 1)
    budget_cases = {}
    for name, directions in (("basis_accepted", 1), ("basis_then_original_restored", 2)):
        extra = directions * per_direction_overcharge
        profile = dict(base_profile)
        profile[1] += extra
        moment = ceiling.relax(
            profile, 73, 896, 9, 112, Q(1, 99), R=51, unpaid=2)
        a_cap = ceiling.ceiling(profile, 73, 896, 9, 112, R=51, unpaid=2)[1]
        kappa_cap = a_cap / (1 + a_cap)
        budget_cases[name] = {
            "profile_per_call": {str(r): n for r, n in sorted(profile.items())},
            "charged_transform_rank1_units": extra,
            "moment_at_a_1_over_99": [str(moment[0]), str(moment[1])],
            "a_ceiling_upper": str(a_cap),
            "kappa_ceiling_upper": str(kappa_cap),
            "kappa_ceiling_decimal": format(float(kappa_cap), ".15g"),
        }
    need(Q(budget_cases["basis_accepted"]["kappa_ceiling_upper"]) > Q(1, 100),
         "one-way basis-change relaxation no longer clears kappa=0.01")
    need(Q(budget_cases["basis_then_original_restored"]["kappa_ceiling_upper"]) < Q(1, 100),
         "restored-basis control should fall below kappa=0.01")
    need(Q(budget_cases["basis_accepted"]["moment_at_a_1_over_99"][1]) < 1,
         "one-way target moment should pass")
    need(Q(budget_cases["basis_then_original_restored"]["moment_at_a_1_over_99"][0]) > 1,
         "restored-basis target moment should fail")

    # Target-specific screen: relax the complex one-unpaid law only on the
    # tetrad blocks whose transformed outputs are accepted. Each 8-port block
    # exposes four invariant combinations; eight families repeat per port, so
    # k transformed blocks correspond to the hypothetical average u=1+k/28.
    # The selected bit side is priced independently at its existing u=1 law,
    # with all local mass ideally represented by rank-8 children.
    target_a = Q(3, 997)  # kappa = a/(1+a) equals 0.003 at this point
    partial_cases = []
    for blocks in range(15):
        profile = {1: 192 + 24 * blocks, 2: 56, 32: 166}
        unpaid = Q(1) + Q(blocks, 28)
        moment = ceiling.relax(
            profile, 73, 896, 9, 112, target_a, R=51, unpaid=unpaid)
        partial_cases.append({
            "transformed_tetrads": blocks,
            "unpaid_average": str(unpaid),
            "profile_per_call": {str(r): n for r, n in sorted(profile.items())},
            "moment_at_target": [str(moment[0]), str(moment[1])],
            "passes_target": moment[1] < 1,
        })
    need(all(Q(partial_cases[k + 1]["moment_at_target"][1]) <
             Q(partial_cases[k]["moment_at_target"][0]) for k in range(14)),
         "partial tetrad moment should decrease strictly with block count")
    first_partial_pass = next(
        row["transformed_tetrads"] for row in partial_cases if row["passes_target"])
    need(first_partial_pass == 10, "target screen should first pass at ten transformed tetrads")
    complex_partial = partial_cases[first_partial_pass]
    complex_profile = {int(r): n for r, n in complex_partial["profile_per_call"].items()}
    complex_root = ceiling.ceiling(
        complex_profile, 73, 896, 9, 112, grid=Q(1, 10 ** 12),
        R=51, unpaid=Q(complex_partial["unpaid_average"]))
    complex_kappa_cap = complex_root[1] / (1 + complex_root[1])
    need(Q(complex_partial["moment_at_target"][1]) < 1,
         "ten-block complex profile should pass the target moment")
    need(complex_root[0] > target_a and complex_kappa_cap > Q(3, 1000),
         "ten-block complex ideal cap should exceed kappa=0.003")
    need(Q(partial_cases[9]["moment_at_target"][0]) > 1,
         "nine-block complex boundary control should fail")

    # The u=1+k/28 coverage gain counts four invariant combinations for
    # each of the eight live family roles attached to every port. The word
    # above transforms one eight-value vector, so a direct role-by-role
    # realization repeats its 24 operations eight times per tetrad. Keep the
    # single-vector calculation as an optimistic lower-cost screen, and price
    # this explicit repeated-word implementation separately.
    roles_per_port = Q(896, 112)
    need(roles_per_port == 8, "selected complex role multiplicity changed")
    role_scaled_cases = []
    for blocks in range(15):
        unpaid = Q(1) + Q(blocks, 28)
        profile = {1: 192 + 24 * int(roles_per_port) * blocks, 2: 56, 32: 166}
        local_mass = sum(rank * count for rank, count in profile.items())
        total_mass = (73 - unpaid) * Q(896, 9) + 112
        case = {
            "transformed_tetrads": blocks,
            "unpaid_average": str(unpaid),
            "profile_per_call": {str(r): n for r, n in sorted(profile.items())},
            "local_mass": str(local_mass),
            "coverage_mass": str(total_mass),
            "mass_feasible": local_mass <= total_mass,
        }
        if case["mass_feasible"]:
            moment = ceiling.relax(
                profile, 73, 896, 9, 112, target_a, R=51, unpaid=unpaid)
            case["moment_at_target"] = [str(moment[0]), str(moment[1])]
            case["passes_target"] = moment[1] < 1
        else:
            case["excess_local_mass"] = str(local_mass - total_mass)
            case["passes_target"] = False
        role_scaled_cases.append(case)
    feasible_role_scaled = [row for row in role_scaled_cases if row["mass_feasible"]]
    need(feasible_role_scaled[-1]["transformed_tetrads"] == 8,
         "role-repeated word should fit the coverage mass through eight blocks")
    need(role_scaled_cases[9]["mass_feasible"] is False,
         "role-repeated nine-block profile should exceed the coverage mass")
    need(all(not row["passes_target"] for row in feasible_role_scaled),
         "direct role-repeated transform unexpectedly passes the target")
    need(Q(feasible_role_scaled[-1]["moment_at_target"][0]) > 1,
         "eight role-repeated blocks should fail the target even at the lower interval endpoint")

    # Coefficient-map fusion composes U into the four existing decoder terms
    # per tetrad. Their copy ranks change from 2 to 1, so both the local profile
    # and the center charge decrease by four per transformed block. This is an
    # exact coefficient-level screen; no physical consumer is implied.
    fused_partial_cases = []
    for blocks in range(15):
        unpaid = Q(1) + Q(blocks, 28)
        profile = {1: 192 + 4 * blocks, 2: 56 - 4 * blocks, 32: 166}
        center_charge = 112 - 4 * blocks
        moment = ceiling.relax(
            profile, 73, 896, 9, center_charge, target_a, R=51, unpaid=unpaid)
        fused_partial_cases.append({
            "transformed_tetrads": blocks,
            "unpaid_average": str(unpaid),
            "centre_charge": center_charge,
            "profile_per_call": {str(r): n for r, n in sorted(profile.items())},
            "moment_at_target": [str(moment[0]), str(moment[1])],
            "passes_target": moment[1] < 1,
        })
    first_fused_pass = next(
        row["transformed_tetrads"] for row in fused_partial_cases if row["passes_target"])
    need(first_fused_pass == 5,
         "coefficient-fused target should first pass at five tetrads")
    need(Q(fused_partial_cases[4]["moment_at_target"][0]) > 1,
         "four fused tetrads should fail the target")
    fused_target = fused_partial_cases[first_fused_pass]
    fused_profile = {int(r): n for r, n in fused_target["profile_per_call"].items()}
    fused_root = ceiling.ceiling(
        fused_profile, 73, 896, 9, fused_target["centre_charge"],
        grid=Q(1, 10 ** 12), R=51, unpaid=Q(fused_target["unpaid_average"]))
    fused_kappa_cap = fused_root[1] / (1 + fused_root[1])
    need(fused_root[0] > target_a and fused_kappa_cap > Q(3, 1000),
         "coefficient-fused complex relaxation should clear kappa=0.003")
    fused_joint_blocks = 9
    fused_joint_target = fused_partial_cases[fused_joint_blocks]
    fused_joint_profile = {
        int(r): n for r, n in fused_joint_target["profile_per_call"].items()}
    fused_joint_root = ceiling.ceiling(
        fused_joint_profile, 73, 896, 9, fused_joint_target["centre_charge"],
        grid=Q(1, 10 ** 12), R=51, unpaid=Q(fused_joint_target["unpaid_average"]))
    fused_joint_complex_cap = fused_joint_root[1] / (1 + fused_joint_root[1])
    fused_eight_root = ceiling.ceiling(
        {int(r): n for r, n in fused_partial_cases[8]["profile_per_call"].items()},
        73, 896, 9, fused_partial_cases[8]["centre_charge"],
        grid=Q(1, 10 ** 12), R=51,
        unpaid=Q(fused_partial_cases[8]["unpaid_average"]))

    bit_binding, bit_assembly, bit_expected, bit_word = bit_verify.bind()
    bit_local, _, bit_copies = bit_verify.replay(bit_word, bit_expected)
    bit_mass = sum(rank * count for rank, count in bit_local.items())
    bit_live = bit_expected["nine"]["bit"]["live"]
    bit_width = Q(bit_live, 9 * 32)
    bit_copy_charge = sum(rank * count for rank, count in bit_copies.items())
    need((bit_mass, bit_live, bit_copy_charge) == (5129, 28416, 63),
         "selected bit local profile or copy charge changed")
    bit_noncopy = dict(bit_local)
    for rank, count in bit_copies.items():
        bit_noncopy[rank] -= count
        if not bit_noncopy[rank]:
            del bit_noncopy[rank]
    bit_noncopy_mass = sum(rank * count for rank, count in bit_noncopy.items())
    bit_rank32_children, bit_rank32_remainder = divmod(bit_noncopy_mass, 32)
    need((bit_noncopy_mass, bit_rank32_children, bit_rank32_remainder, bit_copies)
         == (5066, 158, 10, {7: 9}),
         "bit rank-32 integer repacking inputs changed")
    bit_rank32_profile = {7: 9, 32: bit_rank32_children}
    bit_rank32_histogram = bit_levers.relaxed(
        bit_rank32_profile, 64, bit_width, bit_copy_charge, 45, unpaid=1)
    bit_rank32_moment = bit_levers.bill(
        bit_rank32_histogram, 64, bit_width, target_a, surcharge=True)
    bit_rank32_root = bit_levers.root(
        bit_rank32_histogram, 64, bit_width, surcharge=True,
        tol=Q(1, 10 ** 12))
    bit_rank32_kappa_cap = bit_rank32_root[1] / (1 + bit_rank32_root[1])
    need(bit_rank32_moment[1] < 1 and bit_rank32_root[0] > target_a,
         "integer rank-32 bit local profile should pass kappa=0.003")
    need(fused_eight_root[1] / (1 + fused_eight_root[1]) < bit_rank32_kappa_cap
         < fused_joint_complex_cap,
         "nine fused tetrads should be the first complex profile to reach the bit cap")
    fused_joint_kappa_cap = min(fused_joint_complex_cap, bit_rank32_kappa_cap)

    # Expand the ideal local-child rank cap to the largest ranks allowed by the
    # exact scalar cost models (r < m). For fixed paid mass and a > 0, the
    # per-mass moment decreases with r, so greedy full-size children plus the
    # best legal remainder give the minimum moment under this relaxed cap.
    complex_rank_cap = 72
    complex_rank72_count, complex_rank72_remainder = divmod(166 * 32, complex_rank_cap)
    complex_rank72_profile = {
        1: 192 + 4 * 14,
        complex_rank_cap: complex_rank72_count,
        complex_rank72_remainder: 1,
    }
    complex_rank72_centre = 112 - 4 * 14
    complex_rank72_unpaid = Q(1) + Q(14, 28)
    need((complex_rank72_count, complex_rank72_remainder,
          complex_rank72_profile, complex_rank72_centre, complex_rank72_unpaid)
         == (73, 56, {1: 248, 72: 73, 56: 1}, 56, Q(3, 2)),
         "complex maximum-rank repacking changed")
    complex_rank72_moment = ceiling.relax(
        complex_rank72_profile, 73, 896, 9, complex_rank72_centre,
        target_a, R=51, unpaid=complex_rank72_unpaid)
    complex_rank72_root = extended_complex_ceiling(
        ceiling, complex_rank72_profile, complex_rank72_centre, complex_rank72_unpaid)
    complex_rank72_kappa_cap = complex_rank72_root[1] / (1 + complex_rank72_root[1])
    need(complex_rank72_moment[1] < 1 and complex_rank72_root[0] > target_a,
         "complex maximum-rank envelope should pass kappa=0.003")

    # The rank-72 profile reaches the target at three fused tetrads; two fail.
    rank72_two_profile = {1: 192 + 4 * 2, 2: 56 - 4 * 2, 72: 73, 56: 1}
    rank72_three_profile = {1: 192 + 4 * 3, 2: 56 - 4 * 3, 72: 73, 56: 1}
    rank72_two_moment = ceiling.relax(
        rank72_two_profile, 73, 896, 9, 112 - 4 * 2, target_a,
        R=51, unpaid=Q(1) + Q(2, 28))
    rank72_three_moment = ceiling.relax(
        rank72_three_profile, 73, 896, 9, 112 - 4 * 3, target_a,
        R=51, unpaid=Q(1) + Q(3, 28))
    rank72_three_root = extended_complex_ceiling(
        ceiling, rank72_three_profile, 112 - 4 * 3, Q(1) + Q(3, 28))
    rank72_three_kappa_cap = rank72_three_root[1] / (1 + rank72_three_root[1])
    need(rank72_two_moment[0] > 1 and rank72_three_moment[1] < 1
         and rank72_three_root[0] > target_a,
         "rank-72 fused profile should first pass at three tetrads")

    bit_rank_cap = 63
    bit_rank63_count, bit_rank63_remainder = divmod(bit_noncopy_mass, bit_rank_cap)
    bit_rank63_profile = {7: 9, bit_rank_cap: bit_rank63_count}
    need((bit_rank63_count, bit_rank63_remainder, bit_rank63_profile)
         == (80, 26, {7: 9, 63: 80})
         and bit_rank63_remainder < 45,
         "bit maximum-rank repacking changed")
    bit_rank63_histogram = bit_levers.relaxed(
        bit_rank63_profile, 64, bit_width, bit_copy_charge, 45, unpaid=1)
    bit_rank63_moment = bit_levers.bill(
        bit_rank63_histogram, 64, bit_width, target_a, surcharge=True)
    bit_rank63_root = bit_levers.root(
        bit_rank63_histogram, 64, bit_width, surcharge=True,
        tol=Q(1, 10**12), top=Q(1, 2))
    bit_rank63_kappa_cap = bit_rank63_root[1] / (1 + bit_rank63_root[1])
    need(bit_rank63_moment[1] < 1 and bit_rank63_root[0] > target_a,
         "bit maximum-rank envelope should pass kappa=0.003")
    rank_cap_joint_kappa_cap = min(complex_rank72_kappa_cap, bit_rank63_kappa_cap)
    rank_cap_first_joint_kappa_cap = min(rank72_three_kappa_cap, bit_rank63_kappa_cap)
    need(complex_rank72_kappa_cap < bit_rank63_kappa_cap
         and rank_cap_joint_kappa_cap > Q(3, 1000)
         and rank_cap_first_joint_kappa_cap > Q(3, 1000),
         "maximum-rank joint relaxation should clear kappa=0.003")

    bit_profile = {8: Q(bit_mass, 8)}
    bit_histogram = bit_levers.relaxed(
        bit_profile, 64, bit_width, bit_copy_charge, 45, unpaid=1)
    bit_moment = bit_levers.bill(
        bit_histogram, 64, bit_width, target_a, surcharge=True)
    bit_root = bit_levers.root(
        bit_histogram, 64, bit_width, surcharge=True, tol=Q(1, 10 ** 12))
    bit_kappa_cap = bit_root[1] / (1 + bit_root[1])
    need(bit_moment[1] < 1 and bit_root[0] > target_a,
         "selected bit rank-8 ideal profile should pass kappa=0.003")

    # Remove the fractional local-child count from the target screen. Keeping
    # 641 rank-8 children uses 5128 of the selected 5129 local rank-mass units;
    # the last unit is left in the rank-45 idle relaxation. Then price the
    # exact rank-1-equivalent overhead each side can absorb at the target.
    bit_integer_profile = {8: 641}
    bit_integer_histogram = bit_levers.relaxed(
        bit_integer_profile, 64, bit_width, bit_copy_charge, 45, unpaid=1)
    bit_integer_moment = bit_levers.bill(
        bit_integer_histogram, 64, bit_width, target_a, surcharge=True)
    bit_integer_root = bit_levers.root(
        bit_integer_histogram, 64, bit_width, surcharge=True, tol=Q(1, 10 ** 12))
    bit_integer_kappa_cap = bit_integer_root[1] / (1 + bit_integer_root[1])
    need(bit_integer_moment[1] < 1 and bit_integer_root[0] > target_a,
         "integer rank-8 local profile should pass kappa=0.003")

    def bit_rank1_overhead(count):
        hist = bit_levers.relaxed(
            {8: 641, 1: count}, 64, bit_width, bit_copy_charge, 45, unpaid=1)
        return bit_levers.bill(hist, 64, bit_width, target_a, surcharge=True)

    bit_overhead_pass = bit_rank1_overhead(195)
    bit_overhead_fail = bit_rank1_overhead(196)
    need(bit_overhead_pass[1] < 1 and bit_overhead_fail[0] > 1,
         "bit rank-1 overhead boundary should be 195/196")

    def complex_rank1_overhead(count):
        profile = dict(complex_profile)
        profile[1] += count
        return ceiling.relax(
            profile, 73, 896, 9, 112, target_a, R=51,
            unpaid=Q(complex_partial["unpaid_average"]))

    complex_overhead_pass = complex_rank1_overhead(132)
    complex_overhead_fail = complex_rank1_overhead(133)
    need(complex_overhead_pass[1] < 1 and complex_overhead_fail[0] > 1,
         "complex rank-1 overhead boundary should be 132/133")

    target_003 = {
        "target_a": str(target_a),
        "target_kappa_under_retained_conversion": "3/1000",
        "complex_partial_tetrad_screen": {
            "transformed_tetrads": first_partial_pass,
            "total_tetrads": len(records),
            "unpaid_average": complex_partial["unpaid_average"],
            "transform_rank1_overcharge": 24 * first_partial_pass,
            "cost_model": "one eight-value row word, before repeating across the eight live family roles per port",
            "profile_per_call": complex_partial["profile_per_call"],
            "moment_at_target": complex_partial["moment_at_target"],
            "a_ceiling_bracket": [str(complex_root[0]), str(complex_root[1])],
            "kappa_ceiling_upper": str(complex_kappa_cap),
            "partial_boundaries": {
                "nine_block_moment_at_target": partial_cases[9]["moment_at_target"],
                "ten_block_moment_at_target": partial_cases[10]["moment_at_target"],
            },
            "all_block_counts": partial_cases,
        },
        "complex_role_repeated_word_screen": {
            "roles_per_port": int(roles_per_port),
            "operations_per_role_per_tetrad": 24,
            "rank1_equivalent_charge_per_tetrad": 24 * int(roles_per_port),
            "maximum_mass_feasible_tetrads": feasible_role_scaled[-1]["transformed_tetrads"],
            "maximum_feasible_case": feasible_role_scaled[-1],
            "next_case": role_scaled_cases[9],
            "all_block_counts": role_scaled_cases,
            "scope": "Exact invoice for applying this synthesized row word independently on each live family role; alternative fused implementations remain open.",
        },
        "complex_fused_coefficient_map_screen": {
            "total_tetrads": len(records),
            "coefficient_identity": "D_new = U K = (U E) E^T",
            "decoder_term_copy_profile_original": {
                str(r): n for r, n in sorted(original_decoder_profile.items())},
            "decoder_term_copy_profile_fused_all_blocks": {
                str(r): n for r, n in sorted(fused_decoder_profile.items())},
            "decoder_term_copy_mass_original": sum(
                r * n for r, n in original_decoder_profile.items()),
            "decoder_term_copy_mass_fused_all_blocks": sum(
                r * n for r, n in fused_decoder_profile.items()),
            "runtime_row_operations_added_to_profile": 0,
            "first_target_pass": {
                "transformed_tetrads": first_fused_pass,
                "profile_per_call": fused_target["profile_per_call"],
                "unpaid_average": fused_target["unpaid_average"],
                "centre_charge": fused_target["centre_charge"],
                "moment_at_target": fused_target["moment_at_target"],
                "a_ceiling_bracket": [str(fused_root[0]), str(fused_root[1])],
                "kappa_ceiling_upper": str(fused_kappa_cap),
            },
            "first_count_reaching_bit_cap": {
                "transformed_tetrads": fused_joint_blocks,
                "profile_per_call": fused_joint_target["profile_per_call"],
                "unpaid_average": fused_joint_target["unpaid_average"],
                "centre_charge": fused_joint_target["centre_charge"],
                "moment_at_target": fused_joint_target["moment_at_target"],
                "a_ceiling_bracket": [str(fused_joint_root[0]), str(fused_joint_root[1])],
                "complex_kappa_ceiling": str(fused_joint_complex_cap),
                "previous_count_complex_kappa_ceiling": str(
                    fused_eight_root[1] / (1 + fused_eight_root[1])),
            },
            "partial_boundaries": {
                "four_block_moment_at_target": fused_partial_cases[4]["moment_at_target"],
                "five_block_moment_at_target": fused_partial_cases[5]["moment_at_target"],
            },
            "all_block_counts": fused_partial_cases,
            "scope": "Source-bound coefficient-map composition and exact copy-rank repricing; no selected chronological caller or physical supplier is claimed.",
        },
        "bit_rank8_shape_screen": {
            "coverage_unpaid": 1,
            "copy_charge": bit_copy_charge,
            "local_mass": bit_mass,
            "profile_per_call": {"8": str(bit_profile[8])},
            "idle_cap": 45,
            "surcharge_included": True,
            "moment_at_target": [str(bit_moment[0]), str(bit_moment[1])],
            "a_ceiling_bracket": [str(bit_root[0]), str(bit_root[1])],
            "kappa_ceiling_upper": str(bit_kappa_cap),
            "bit_binding": bit_binding,
            "assembly_sha256": sha256((ROOT / bit_binding["assembly"]).read_bytes()).hexdigest(),
        },
        "integer_bit_rank8_screen": {
            "coverage_unpaid": 1,
            "copy_charge": bit_copy_charge,
            "local_profile_per_call": {"8": 641},
            "integer_local_mass": 5128,
            "remaining_local_mass": 1,
            "idle_rank": 45,
            "moment_at_target": [str(bit_integer_moment[0]), str(bit_integer_moment[1])],
            "a_ceiling_bracket": [str(bit_integer_root[0]), str(bit_integer_root[1])],
            "kappa_ceiling_upper": str(bit_integer_kappa_cap),
        },
        "bit_rank32_local_screen": {
            "coverage_unpaid": 1,
            "copy_charge": bit_copy_charge,
            "profile_per_call": {str(r): n for r, n in sorted(bit_rank32_profile.items())},
            "noncopy_mass": bit_noncopy_mass,
            "rank32_children": bit_rank32_children,
            "idle_local_rank_mass": bit_rank32_remainder,
            "idle_rank_cap": 45,
            "inherited_surcharge_included": True,
            "moment_at_target": [str(bit_rank32_moment[0]), str(bit_rank32_moment[1])],
            "a_ceiling_bracket": [str(bit_rank32_root[0]), str(bit_rank32_root[1])],
            "kappa_ceiling_upper": str(bit_rank32_kappa_cap),
        },
        "rank1_equivalent_overhead_at_target": {
            "bit": {
                "maximum_passing_per_call": 195,
                "pass_moment": [str(bit_overhead_pass[0]), str(bit_overhead_pass[1])],
                "next_failing_per_call": 196,
                "fail_moment": [str(bit_overhead_fail[0]), str(bit_overhead_fail[1])],
                "inherited_surcharge_included": True,
            },
            "complex": {
                "maximum_passing_per_call": 132,
                "pass_moment": [str(complex_overhead_pass[0]), str(complex_overhead_pass[1])],
                "next_failing_per_call": 133,
                "fail_moment": [str(complex_overhead_fail[0]), str(complex_overhead_fail[1])],
                "unpaid_average": complex_partial["unpaid_average"],
            },
        },
        "joint_ideal_kappa_ceiling": str(min(complex_kappa_cap, bit_integer_kappa_cap)),
        "fused_first_pass_joint_ideal_kappa_ceiling": str(
            min(fused_kappa_cap, bit_rank32_kappa_cap)),
        "fused_joint_ideal_kappa_ceiling": str(fused_joint_kappa_cap),
        "fused_joint_minimum_tetrads": fused_joint_blocks,
        "maximum_local_rank_envelope": {
            "assumption": "Local child ranks may be any integer below the parent dimension; remainder children retain the halving rank cap.",
            "packing_rule": "At fixed paid mass and positive a, use the largest allowed local rank first; put a remainder in idle only when its rank is no larger than the idle cap.",
            "complex": {
                "local_rank_cap": complex_rank_cap,
                "profile_per_call": {str(r): n for r, n in sorted(complex_rank72_profile.items())},
                "local_mass": sum(r * n for r, n in complex_rank72_profile.items()),
                "centre_charge": complex_rank72_centre,
                "unpaid_average": str(complex_rank72_unpaid),
                "idle_rank_cap": 51,
                "moment_at_target": [str(complex_rank72_moment[0]), str(complex_rank72_moment[1])],
                "a_ceiling_bracket": [str(complex_rank72_root[0]), str(complex_rank72_root[1])],
                "kappa_ceiling_upper": str(complex_rank72_kappa_cap),
                "rank72_children": complex_rank72_count,
                "rank56_remainder_child": 1,
                "first_passing_tetrads": 3,
                "two_tetrad_moment": [str(rank72_two_moment[0]), str(rank72_two_moment[1])],
                "three_tetrad_moment": [str(rank72_three_moment[0]), str(rank72_three_moment[1])],
                "three_tetrad_kappa_ceiling": str(rank72_three_kappa_cap),
            },
            "bit": {
                "local_rank_cap": bit_rank_cap,
                "profile_per_call": {str(r): n for r, n in sorted(bit_rank63_profile.items())},
                "local_mass": sum(r * n for r, n in bit_rank63_profile.items()),
                "unpacked_local_mass_to_idle": bit_rank63_remainder,
                "copy_charge": bit_copy_charge,
                "idle_rank_cap": 45,
                "inherited_surcharge_included": True,
                "moment_at_target": [str(bit_rank63_moment[0]), str(bit_rank63_moment[1])],
                "a_ceiling_bracket": [str(bit_rank63_root[0]), str(bit_rank63_root[1])],
                "kappa_ceiling_upper": str(bit_rank63_kappa_cap),
            },
            "first_joint_ideal_kappa_ceiling": str(rank_cap_first_joint_kappa_cap),
            "full_fusion_joint_ideal_kappa_ceiling": str(rank_cap_joint_kappa_cap),
            "selected_kappa_unchanged": selected_record["decimal"],
            "scope": "Sensitivity envelope only: neither near-full-rank child profile nor transformed consumer has a physical supplier or complete invoice.",
        },
        "status": "coefficient_fused_ideal_screen_clears_target_but_no_supplier_or_new_kappa",
    }
    need(Q(target_003["joint_ideal_kappa_ceiling"]) > Q(3, 1000),
         "joint ideal target screen should exceed kappa=0.003")
    need(Q(target_003["fused_first_pass_joint_ideal_kappa_ceiling"]) > Q(3, 1000)
         and Q(target_003["fused_joint_ideal_kappa_ceiling"]) > Q(3, 1000),
         "coefficient-fused two-side profiles should exceed kappa=0.003")

    # A duplicate port remains a failing bijection control.
    bad_ports = list(range(112))
    bad_ports[1] = bad_ports[0]
    need(len(set(bad_ports)) != 112, "duplicate-port control should fail")

    receipt = {
        "status": "PASS_P112_TETRAD_UNIMODULAR_KERNEL_SCREEN",
        "selected_kappa_unchanged": selected_record["decimal"],
        "tetrads": len(records),
        "mapped_ports": len(all_ports),
        "one_sign_flip_cases": all_flip_count,
        "kernel_outputs_per_block": 4,
        "forward_word_per_block": {"adds": 21, "swaps": 2, "negations": 1},
        "forward_totals": {"adds": total_adds, "swaps": total_swaps,
                            "negations": total_negations},
        "rank1_overcharge_per_direction": per_direction_overcharge,
        "budget_cases": budget_cases,
        "target_003_joint_screen": target_003,
        "scope": "local reversible output-basis witness and target-specific two-side ideal budget screen; no caller, family coverage, supplier, or new kappa",
        "source_sha256": pins,
        "blocks": records,
    }
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    print("PASS_P112_TETRAD_UNIMODULAR_KERNEL_SCREEN blocks=14 kernel_outputs=56 "
          "target003_unscaled_blocks=10 fused_first_pass=%d fused_joint_blocks=%d "
          "fused_complex_kappa_cap=%.15g fused_joint_ideal_kappa_cap=%.15g "
          "max_rank_first_pass=3 max_rank_joint_ideal_kappa_cap=%.15g no_new_kappa" %
          (first_fused_pass, fused_joint_blocks, float(fused_kappa_cap),
           float(fused_joint_kappa_cap), float(rank_cap_joint_kappa_cap)))


if __name__ == "__main__":
    main()
