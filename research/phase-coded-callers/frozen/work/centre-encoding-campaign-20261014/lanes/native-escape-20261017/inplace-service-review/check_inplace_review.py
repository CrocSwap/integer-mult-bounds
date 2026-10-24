"""Review the literal one-bank translation inverse without producer code."""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import json
import shutil

HERE = Path(__file__).resolve().parent
LANE = HERE.parent
PRODUCER = LANE / "owner-review/inplace-translation-service"
PINS = {
    "program": (PRODUCER / "INPLACE-PROGRAM.json.gz", "e4015617dbb55c2e943eb7762766e9854b6e7d61fbccd905dbfbfcb9cc338a8b"),
    "interface": (LANE.parent / "new-core-transfer-20261017/INTERFACE.json", "c6ca09711622ce4ad236f78cc28c03b6c46808a9d91cfc1722ff4fe371f38746"),
    "phase_ledger": (LANE.parent.parent / "upstream-refresh-20261017/pr3251/research/adaptive-kernel-demotion/inputs/DATA-PHASES.json", "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"),
    "spectrum": (LANE / "owner-review/centre-schur-probe/SCHUR-PROBE.json", "ebff70f4ff3d28c345080a4d7b1d90cd952a6208b7f6449037b96dbf3531c024"),
    "views": (LANE.parent / "bridge-access-20261017/BRIDGE-PROGRAMS.json.gz", "1da2f6a6058661f19e971bb31f1823585f01c2494dca813e208af45aea7a582f"),
    "producer_proof": (PRODUCER / "INPLACE-SERVICE.md", "46adf0f78165489bd87401fc781b4a5d9505c4998c068800c72dfbc780dd49c6"),
    "producer_receipt": (PRODUCER / "INPLACE-SERVICE.json", "9e568a68279c6aa126d25a593baa9775f39646977968a0391732cae538fea2d8"),
    "producer_checker": (PRODUCER / "check_inplace_service.py", "ec38a9db9d7542eb076def53d8df4af2ede586cc110835014ca1ab8219cc4e56"),
    "odd_grid": (LANE.parent / "independent-review-20261017/odd-grid-a8-20261017/A8-ODD-GRID.md", "e0210105ba6c6246f1f84c8ce2d92cfd07aa6cc8a161ca27d7fcc8e0183cfb01"),
    "stream_source": (LANE.parents[3] / "upstream/build/sections/02-streams.tex", "606c80db61cad13aa0c3b6060dc4b88dbbe7ac60cdd831aa93f28d908fd09dab"),
    "layer_source": (LANE.parents[3] / "upstream/build/sections/05-layers.tex", "20cfc8d12099d4e4ed9e3e7eeb6162edd9b6e0e076f24693364cd24377252594"),
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def read(key):
    path, digest = PINS[key]
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == digest, "Source hash: " + key)
    if path.suffix in (".json", ".gz"):
        return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)
    return raw.decode()


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    return [[sum(x * y for x, y in zip(row, column)) for column in zip(*b)] for row in a]


def invoice(word):
    count = Counter()
    for kind, selector, target, *args in word:
        need(0 <= target <= 8, "Only eight live fields and C0")
        count[kind] += 1
        if kind == "TRANSLATE":
            need(selector is None and target == 8, "Only the scratch is translated")
            count["translation_maps"] += 1
        elif kind == "DIVIDE_ODD":
            need(selector is None and target < 8 and args == [2145], "One uniform odd division")
            count["real_odd_division_scans"] += 2
        else:
            need(kind in {"ADD", "NEG", "SCALE2", "COPY", "CLEAR"}, "Declared scalar operation")
            price = 8 if kind == "ADD" else 2
            count["scalar_primitives"] += price
            count["conditional_scalar_primitives" if selector is not None else "uniform_scalar_primitives"] += price
            if selector is not None:
                count["conditional_complex_instructions"] += 1
        if kind == "SCALE2":
            need(args[0] in (-1, 1), "Unit binary scale")
            count["halve" if args[0] < 0 else "double"] += 1
    return dict(count)


need(shutil.disk_usage(HERE).free >= 3 * 2**30, "At least 3 GiB free")
loaded = {key: read(key) for key in PINS}
program, interface, ledger, spectrum = [loaded[key] for key in ("program", "interface", "phase_ledger", "spectrum")]
producer = loaded["producer_receipt"]
need(producer["checker_sha256"] == PINS["producer_checker"][1], "Producer checker pin")
need(producer["payload_compressed_sha256"] == PINS["program"][1], "Producer payload pin")
need(program["live_fields"] == list(range(8)) and program["owned"] == 8, "One-bank ownership")
selected = [0, 7, 20, 27, 36, 46, 57, 111]
need(program["selected_ports"] == selected, "Actual selected minor")
ordinary = [p for p in range(112) if p not in selected]
R = [[F(row.get(str(p), 0)) for p in range(112)] for row in interface["R"]]
B = [[sum(R[i][a] * R[i][p] for i in range(8)) / 4 for p in ordinary] for a in selected]
q = [ledger["recipes"][p]["q"] for p in ordinary]
need(multiply(B, list(map(list, zip(*B)))) == [[13 * x for x in row] for row in identity(8)], "Actual BD=13I")
matrices = []
for mode in range(512):
    matrix = [[sum(B[i][p] * B[j][p] * (-1 if (mode & q[p]).bit_count() % 2 else 1)
                   for p in range(104)) for j in range(8)] for i in range(8)]
    need(all(x.denominator == 1 for row in matrix for x in row), "Integral mode matrix")
    matrices.append([[int(x) for x in row] for row in matrix])

selectors = {key: frozenset(values) for key, values in program["selectors"].items()}
need(all(len(values) == len(program["selectors"][key]) and values <= set(range(512))
         for key, values in selectors.items()), "Canonical selector table")
for bit in range(9):
    need(selectors["bit_" + str(bit)] == {mode for mode in range(512) if mode >> bit & 1}, "First-copy sign selector")
mode_word = program["mode_word"]
need(mode_word[-8:] == [["DIVIDE_ODD", None, i, 2145] for i in range(8)], "Only final uniform odd divisions")
need(all(g[0] != "DIVIDE_ODD" for g in mode_word[:-8]), "One odd-height increment")
maximum, maximum_coefficient, final_maximum = 1, 1, F(0)
numerators = []
active_operations = 0
for mode in range(512):
    state = identity(9)
    for kind, selector, target, *args in mode_word[:-8]:
        if selector is not None and mode not in selectors[selector]:
            continue
        active_operations += 1
        if kind == "ADD":
            source, coefficient = args
            need(source != target and coefficient in (-1, 1), "Unit ADD on distinct fields")
            state[target] = [a + coefficient * b for a, b in zip(state[target], state[source])]
        elif kind == "NEG":
            state[target] = [-x for x in state[target]]
        elif kind == "SCALE2":
            if args == [1]:
                state[target] = [2 * x for x in state[target]]
            else:
                need(args == [-1] and all(x % 2 == 0 for x in state[target]), "No new mode denominator")
                state[target] = [x // 2 for x in state[target]]
        elif kind == "COPY":
            need(target == 8 and 0 <= args[0] < 8, "Copy overwrites only owned C0")
            state[target] = state[args[0]][:]
        else:
            need(kind == "CLEAR" and target == 8 and not args, "Only owned C0 is cleared")
            state[target] = [0] * 9
        maximum = max(maximum, sum(map(abs, state[target])))
        maximum_coefficient = max(maximum_coefficient, *map(abs, state[target]))
    need(not any(state[8]) and not any(row[8] for row in state[:8]), "Arbitrary scratch is removed and cleared")
    result = [row[:8] for row in state[:8]]
    expected = [[2145 * x for x in row] for row in identity(8)]
    need(multiply(result, matrices[mode]) == expected == multiply(matrices[mode], result), "Both exact mode inverse orders")
    numerators.append(result)
    final_maximum = max(final_maximum, *(F(sum(map(abs, row)), 2145) for row in result))

# The local pair replay includes both arbitrary scratch records.
pair_checks = 0
for name, word in program["walsh_words"].items():
    step = 6 if name == "forward" else 5
    need(len(word) == 72 * step, "Nine Walsh directions on each live field")
    seen = set()
    for start in range(0, len(word), step):
        gates = word[start:start + step]
        target = gates[0][3]
        shift = gates[1][3]
        need(shift in [1 << bit for bit in range(9)] and target < 8, "One simultaneous generator")
        bit = shift.bit_length() - 1
        expected = [["COPY", None, 8, target], ["TRANSLATE", None, 8, shift],
                    ["NEG", "bit_" + str(bit), target], ["ADD", None, target, 8, 1]]
        if name == "forward":
            expected.append(["SCALE2", None, target, -1])
        expected.append(["CLEAR", None, 8])
        need(gates == expected and (target, bit) not in seen, "Literal Walsh block")
        seen.add((target, bit))
        state = [[F(x) for x in row] for row in identity(4)]
        state[2:4] = [state[0][:], state[1][:]]
        state[2], state[3] = state[3], state[2]
        state[1] = [-x for x in state[1]]
        state[0] = [x + y for x, y in zip(state[0], state[2])]
        state[1] = [x + y for x, y in zip(state[1], state[3])]
        if name == "forward":
            state[:2] = [[x / 2 for x in row] for row in state[:2]]
        state[2:4] = [[F(0)] * 4 for _ in range(2)]
        scale = F(1, 2) if name == "forward" else F(1)
        need(state == [[scale, scale, 0, 0], [scale, -scale, 0, 0], [0] * 4, [0] * 4], "Walsh map and arbitrary scratch columns")
        pair_checks += 1

need(program["body"] == program["walsh_words"]["forward"] + mode_word + program["walsh_words"]["inverse"], "Complete program order")
kernel = {(delta, i, j): F(c) for delta, i, j, c in spectrum["kernels"]["inverse"]["entries"]}
for i in range(8):
    for j in range(8):
        values = [numerators[mode][i][j] for mode in range(512)]
        block = 1
        while block < 512:
            for start in range(0, 512, 2 * block):
                for offset in range(block):
                    a, b = values[start + offset], values[start + block + offset]
                    values[start + offset], values[start + block + offset] = a + b, a - b
            block *= 2
        need(all(F(value, 512 * 2145) == kernel.get((delta, i, j), 0)
                 for delta, value in enumerate(values)), "All inverse translation coefficients")

counts = invoice(program["body"])
need(counts["translation_maps"] == 144 and counts["real_odd_division_scans"] == 16, "Complete non-scalar invoice")
need(counts["uniform_scalar_primitives"] == 2080 and counts["conditional_scalar_primitives"] == 110284, "Complete scalar invoice")
need(counts["conditional_complex_instructions"] == 23345, "Conditional scan count")
need(counts == producer["counts"]["complete"], "All invoice entries agree")
need(maximum == 462848 and final_maximum == 1, "Exact prefix and final norms")

# Check the full quadratic phase at each actual completed level s.
actual_views = {(v["stage"], v["port"]): v for v in loaded["views"]["views"]
                if v["side"] == "X" and v["port"] in selected}
need(len(actual_views) == 64, "All selected completed views")
need({(v["stage"], v["port"]): v for v in program["completed_views"]} == actual_views, "Literal source views")
for (stage, port), view in actual_views.items():
    rho, delta = view["route_columns"], view["translation_after_route"]
    dimension = 9 + 8 * stage
    mask = (1 << dimension) - 1
    need(delta & ~mask == 0, "View translation lies in completed coordinates")
    need(all(rho[j] == 1 << j for j in range(dimension, 73)), "View fixes future coordinates")
    for j in range(73):
        need(((rho[j] & mask).bit_count() + 2 * ((delta >> j) & 1) - (j < dimension)) % 4 == 0,
             "Completed-level linear phase")
        for k in range(j):
            need((-2 * (rho[j] & rho[k] & mask).bit_count()) % 4 == 0, "Completed-level quadratic phase")
    for j in range(73):
        image = 0
        for k in range(73):
            if rho[j] >> k & 1:
                image ^= rho[k]
        need(image == 1 << j, "View route is an involution")
for stage in range(1, 9):
    expected = {"enter": [["VIEW", i, stage, selected[i], False] for i in range(8)],
                "leave": [["VIEW", i, stage, selected[i], True] for i in reversed(range(8))]}
    need(program["stage_wrappers"][str(stage)] == expected, "All entry and inverse exit views")

receipt = {
    "status": "PASS_INDEPENDENT_INPLACE_TRANSLATION_INVERSE",
    "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
    "sources": {k: {"path": str(p), "sha256": h} for k, (p, h) in PINS.items()},
    "mode_inverse_orders": 1024, "mode_input_columns": 9,
    "active_mode_operations": active_operations, "walsh_pair_blocks": pair_checks,
    "inverse_kernel_coefficients": 32768, "counts": counts,
    "maximum_mode_prefix_row_norm": maximum,
    "maximum_mode_prefix_coefficient": maximum_coefficient,
    "maximum_completed_mode_row_norm": str(final_maximum),
    "mode_extra_dyadic_bits": 0, "full_word_extra_dyadic_bits": 9,
    "odd_height_increase": 1, "owned_fields": 1,
    "arbitrary_owned_input_removed": True, "owned_output_zero": True,
    "completed_level_full_phase_checks": 64,
    "scope": "Literal one-bank inverse, conditional-scan backend proof, and inherited completed-view contract. No global lease, full decoder, supplier, or kappa claim.",
}
(HERE / "REVIEW.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
print(receipt["status"])
print(json.dumps({"modes": 512, "prefix_norm": maximum, "native_children": 0, "owned_fields": 1}))
