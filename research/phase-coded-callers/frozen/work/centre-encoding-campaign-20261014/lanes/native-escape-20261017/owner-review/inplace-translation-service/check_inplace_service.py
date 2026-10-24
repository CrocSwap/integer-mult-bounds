"""Emit and check an in-place inverse of the centre translation operator."""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import json
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
PROBE = HERE.parent / "centre-schur-probe"
A = [0, 7, 20, 27, 36, 46, 57, 111]
U_PORTS = [p for p in range(112) if p not in A]
I = [[int(i == j) for j in range(8)] for i in range(8)]
C0 = 8
BACKEND = {
    "upstream/build/sections/02-streams.tex": "606c80db61cad13aa0c3b6060dc4b88dbbe7ac60cdd831aa93f28d908fd09dab",
    "upstream/build/sections/05-layers.tex": "20cfc8d12099d4e4ed9e3e7eeb6162edd9b6e0e076f24693364cd24377252594",
}


def need(ok, label):
    if not ok:
        raise ValueError(label)


def read_pin(path, digest):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == digest, "Source pin: " + str(path))
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def multiply(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(8)) for j in range(8)] for i in range(8)]


def row_gate(a, gate):
    kind, target = gate[:2]
    if kind == "ADD_INTEGER":
        source, coefficient = gate[2:]
        a[target] = [x + coefficient * y for x, y in zip(a[target], a[source])]
    elif kind == "SWAP":
        a[target], a[gate[2]] = a[gate[2]], a[target]
    else:
        need(kind == "NEG", "Integer row gate")
        a[target] = [-x for x in a[target]]


def smith(a):
    a = [row[:] for row in a]
    left, right = [row[:] for row in I], [row[:] for row in I]
    row_ops, column_ops = [], []

    def row(gate):
        row_gate(a, gate)
        row_gate(left, gate)
        row_ops.append(gate)

    def column(gate):
        for matrix in (a, right):
            transposed = list(map(list, zip(*matrix)))
            row_gate(transposed, gate)
            matrix[:] = list(map(list, zip(*transposed)))
        column_ops.append(gate)

    for k in range(8):
        candidates = [(abs(a[i][j]), i, j) for i in range(k, 8) for j in range(k, 8) if a[i][j]]
        need(candidates, "Full rank pivot")
        _, i, j = min(candidates)
        if i != k:
            row(["SWAP", i, k])
        if j != k:
            column(["SWAP", j, k])
        while True:
            for i in range(k + 1, 8):
                if a[i][k]:
                    quotient = a[i][k] // a[k][k]
                    if quotient:
                        row(["ADD_INTEGER", i, k, -quotient])
                    if a[i][k]:
                        row(["SWAP", i, k])
                        break
            else:
                for j in range(k + 1, 8):
                    if a[k][j]:
                        quotient = a[k][j] // a[k][k]
                        if quotient:
                            column(["ADD_INTEGER", j, k, -quotient])
                        if a[k][j]:
                            column(["SWAP", j, k])
                            break
                else:
                    bad = next(((i, j) for i in range(k + 1, 8) for j in range(k + 1, 8)
                                if a[i][j] % a[k][k]), None)
                    if bad is None:
                        break
                    row(["ADD_INTEGER", k, bad[0], 1])
        if a[k][k] < 0:
            row(["NEG", k])
    diagonal = [a[k][k] for k in range(8)]
    need(all(a[i][j] == (diagonal[i] if i == j else 0) for i in range(8) for j in range(8)), "Smith diagonal")
    need(all(diagonal[i + 1] % diagonal[i] == 0 for i in range(7)), "Smith divisor chain")
    vector_right = []
    for gate in reversed(column_ops):
        if gate[0] == "ADD_INTEGER":
            vector_right.append([gate[0], gate[2], gate[1], gate[3]])
        else:
            vector_right.append(gate[:])
    check = [row[:] for row in I]
    for gate in vector_right:
        row_gate(check, gate)
    need(check == right, "Column factor vector order")
    return dict(left=left, right=right, diagonal=diagonal, left_word=row_ops, right_word=vector_right)


def load_data():
    probe = read_pin(PROBE / "SCHUR-PROBE.json", "ebff70f4ff3d28c345080a4d7b1d90cd952a6208b7f6449037b96dbf3531c024")
    sources = {key: read_pin(Path(pin["path"]), pin["sha256"]) for key, pin in probe["source_pins"].items()}
    rows = [{int(p): int(c) for p, c in row.items()} for row in sources["interface"]["R"]]
    q = [recipe["q"] for recipe in sources["phases"]["recipes"]]
    b2 = {}
    for p in U_PORTS:
        products = [sum(row.get(a, 0) * row.get(p, 0) for row in rows) for a in A]
        need(all(x % 2 == 0 for x in products), "Integral doubled B column")
        b2[p] = [x // 2 for x in products]
    matrices = []
    for chi in range(512):
        numerator = [[sum((-1 if (q[p] & chi).bit_count() % 2 else 1) * b2[p][i] * b2[p][j]
                          for p in U_PORTS) for j in range(8)] for i in range(8)]
        need(all(x % 4 == 0 for row in numerator for x in row), "Integral actual character matrix")
        matrices.append([[x // 4 for x in row] for row in numerator])
    inverse_kernel = {(delta, i, j): F(value) for delta, i, j, value in probe["kernels"]["inverse"]["entries"]}
    inverse_entries = [[[(delta, value) for (delta, row, column), value in inverse_kernel.items()
                        if row == i and column == j] for j in range(8)] for i in range(8)]
    inverses = []
    for chi in range(512):
        matrix = [[sum(value * (-1 if (delta & chi).bit_count() % 2 else 1)
                       for delta, value in inverse_entries[i][j])
                   for j in range(8)] for i in range(8)]
        need(multiply(matrix, matrices[chi]) == multiply(matrices[chi], matrix) == I, "Actual inverse in both orders")
        inverses.append(matrix)
    return probe, sources, matrices, inverses


def expand_row(gate, selector):
    kind, target = gate[:2]
    if kind == "NEG":
        return [["NEG", selector, target]]
    source = gate[2]
    if kind == "SWAP":
        return [["ADD", selector, target, source, 1], ["ADD", selector, source, target, -1],
                ["ADD", selector, target, source, 1], ["NEG", selector, source]]
    need(kind == "ADD_INTEGER" and target != source and gate[3], "Integer ADD input")
    coefficient = gate[3]
    length = abs(coefficient).bit_length() - 1
    word = []
    for bit in range(length + 1):
        if (abs(coefficient) >> bit) & 1:
            word.append(["ADD", selector, target, source, 1 if coefficient > 0 else -1])
        if bit < length:
            word.append(["SCALE2", selector, source, 1])
    word += [["SCALE2", selector, source, -1] for _ in range(length)]
    return word


def walsh_word(inverse):
    word = []
    for target in range(8):
        for bit in (reversed(range(9)) if inverse else range(9)):
            word += [["COPY", None, C0, target], ["TRANSLATE", None, C0, 1 << bit],
                     ["NEG", "bit_" + str(bit), target], ["ADD", None, target, C0, 1]]
            if not inverse:
                word.append(["SCALE2", None, target, -1])
            word.append(["CLEAR", None, C0])
    return word


def build_mode_word(classes, lookup, selectors):
    word = []
    for item in classes:
        label = "class_" + str(item["index"])
        selectors[label] = [chi for chi, (index, sign) in enumerate(lookup) if index == item["index"]]
        for gate in item["left_word"]:
            word += expand_row(gate, label)
    for target in range(8):
        multipliers = [2145 // classes[index]["diagonal"][target] for index, sign in lookup]
        word.append(["COPY", None, C0, target])
        for bit in range(1, max(multipliers).bit_length()):
            word.append(["SCALE2", None, C0, 1])
            label = "diagonal_" + str(target) + "_" + str(bit)
            selectors[label] = [chi for chi, value in enumerate(multipliers) if ((value - 1) >> bit) & 1]
            if selectors[label]:
                word.append(["ADD", label, target, C0, 1])
        word.append(["CLEAR", None, C0])
    for item in classes:
        for gate in item["right_word"]:
            word += expand_row(gate, "class_" + str(item["index"]))
    selectors["negative"] = [chi for chi, (index, sign) in enumerate(lookup) if sign < 0]
    word += [["NEG", "negative", target] for target in range(8)]
    word += [["DIVIDE_ODD", None, target, 2145] for target in range(8)]
    return word


def invoice(word):
    count = Counter()
    for gate in word:
        kind, selector = gate[:2]
        count[kind] += 1
        if kind == "TRANSLATE":
            count["translation_maps"] += 1
        elif kind == "DIVIDE_ODD":
            count["real_odd_division_scans"] += 2
        else:
            price = 8 if kind == "ADD" else 2
            need(kind in ("ADD", "COPY", "CLEAR", "SCALE2", "NEG"), "Priced scalar gate")
            category = "uniform_scalar_primitives" if selector is None else "conditional_scalar_primitives"
            count[category] += price
            if selector is not None:
                count["conditional_complex_instructions"] += 1
            count["scalar_primitives"] += price
        if kind == "SCALE2":
            count["double" if gate[3] == 1 else "halve"] += 1
    return dict(count)


def check_modes(word, selectors, inverses):
    membership = {key: set(values) for key, values in selectors.items()}
    maximum, final_maximum = F(1), F(0)
    maximum_integer = 0
    maximum_dyadic_denominator_exponent = 0
    for chi in range(512):
        state = [[F(c) for c in row] + [F(0)] for row in I] + [[F(0)] * 8 + [F(1)]]
        for gate in word:
            kind, selector, target = gate[:3]
            if selector is not None and chi not in membership[selector]:
                continue
            need(0 <= target <= C0, "Only live bank and owned field")
            if kind == "ADD":
                source, coefficient = gate[3:]
                need(source != target and coefficient in (-1, 1), "Literal unit ADD")
                state[target] = [x + coefficient * y for x, y in zip(state[target], state[source])]
            elif kind == "SCALE2":
                need(gate[3] in (-1, 1), "One power-of-two step")
                state[target] = [x * F(2) ** gate[3] for x in state[target]]
            elif kind == "NEG":
                state[target] = [-x for x in state[target]]
            elif kind == "COPY":
                need(target == C0 and gate[3] < 8, "Copy into one owned field")
                state[target] = state[gate[3]][:]
            elif kind == "CLEAR":
                need(target == C0, "Only the owned field is cleared")
                state[target] = [F(0)] * 9
            else:
                need(kind == "DIVIDE_ODD" and target < 8 and gate[3] == 2145, "One common output division")
                state[target] = [x / 2145 for x in state[target]]
            maximum = max(maximum, sum(map(abs, state[target])))
            if kind != "DIVIDE_ODD":
                for value in state[target]:
                    need(value.denominator == 1, "Integral mode prefix before the final divisions")
                    if value.denominator & (value.denominator - 1) == 0:
                        maximum_dyadic_denominator_exponent = max(maximum_dyadic_denominator_exponent, value.denominator.bit_length() - 1)
                        maximum_integer = max(maximum_integer, abs(value.numerator))
        need(state[:8] == [row + [F(0)] for row in inverses[chi]] and not any(state[C0]), "Exact emitted character inverse and zero owned output")
        final_maximum = max(final_maximum, *(sum(map(abs, row)) for row in state[:8]))
    return dict(maximum_intermediate_row_one_norm=str(maximum), maximum_final_row_one_norm=str(final_maximum),
                maximum_dyadic_denominator_exponent=maximum_dyadic_denominator_exponent,
                maximum_intermediate_dyadic_numerator=maximum_integer)


def pair_matrix(inverse):
    rows = [[F(1), F(0)], [F(0), F(1)]]
    copied = [row[:] for row in rows]
    copied.reverse()
    rows[1] = [-x for x in rows[1]]
    rows = [[x + y for x, y in zip(row, copy)] for row, copy in zip(rows, copied)]
    return rows if inverse else [[x / 2 for x in row] for row in rows]


def check_walsh(words):
    forward, inverse = pair_matrix(False), pair_matrix(True)
    need(forward == [[F(1, 2), F(1, 2)], [F(1, 2), F(-1, 2)]], "Exact H0 pair")
    need(inverse == [[1, 1], [1, -1]], "Exact inverse pair")
    for a, b in ((forward, inverse), (inverse, forward)):
        need([[sum(a[i][k] * b[k][j] for k in range(2)) for j in range(2)] for i in range(2)] == [[1, 0], [0, 1]], "Both pair inverse orders")
    for name, word in words.items():
        step_size = 6 if name == "forward" else 5
        need(len(word) == 72 * step_size, "All eight fields and nine directions")
        for offset in range(0, len(word), step_size):
            gates = word[offset:offset + step_size]
            target, shift = gates[0][3], gates[1][3]
            bit = shift.bit_length() - 1
            want = [["COPY", None, C0, target], ["TRANSLATE", None, C0, shift],
                    ["NEG", "bit_" + str(bit), target], ["ADD", None, target, C0, 1]]
            if name == "forward":
                want.append(["SCALE2", None, target, -1])
            want.append(["CLEAR", None, C0])
            need(gates == want and shift == 1 << bit, "Literal pair order")
    for j in range(9):
        for k in range(9):
            need(((1 << k) >> j) & 1 == int(j == k), "First-copy selector duality")


def check_counter():
    cases, visits = 0, 0
    for copies in (1, 2, 3, 7):
        positions = [copies * bit for bit in range(9)]
        width = positions[-1] + 2
        marks = {position: bit for bit, position in enumerate(positions)}
        starts = [0] + [max(0, (1 << position) - 17) for position in positions]
        for start in starts:
            bits = [(start >> bit) & 1 for bit in range(width)]
            mode = sum(bits[position] << bit for bit, position in enumerate(positions))
            local_visits = 0
            for value in range(start, start + 65):
                need(mode == sum(((value >> position) & 1) << bit for bit, position in enumerate(positions)), "Marked counter mode")
                if value == start + 64:
                    break
                position = 0
                while True:
                    bits[position] ^= 1
                    local_visits += 1
                    if position in marks:
                        mode ^= 1 << marks[position]
                    if bits[position]:
                        break
                    position += 1
            need(local_visits <= 128 + width, "Amortized counter visits")
            visits += local_visits
            cases += 1
    return dict(cases=cases, checked_addresses=65 * cases, carry_bit_visits=visits,
                scope="Finite checks of the marked-counter recurrence. The linear bound follows from the binary carry proof.")


def check_walsh_kernel(inverses, probe):
    expected = {(delta, i, j): F(value) for delta, i, j, value in probe["kernels"]["inverse"]["entries"]}
    for i in range(8):
        for j in range(8):
            values = [matrix[i][j] / 512 for matrix in inverses]
            for bit in reversed(range(9)):
                copied = values[:]
                values = [(-copied[h] if (h >> bit) & 1 else copied[h]) + copied[h ^ (1 << bit)]
                          for h in range(512)]
            need(values == [expected.get((delta, i, j), F(0)) for delta in range(512)], "Literal inverse Walsh reconstructs the complete kernel")


def act(columns, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= columns[bit.bit_length() - 1]
        vector ^= bit
    return result


def check_views(sources):
    views = [v for v in sources["views"]["views"] if v["side"] == "X" and v["port"] in A]
    need({(v["stage"], v["port"]) for v in views} == {(s, p) for s in range(1, 9) for p in A}, "All selected completed views")
    for view in views:
        rho, delta = view["route_columns"], view["translation_after_route"]
        transpose = [sum(((v >> i) & 1) << j for j, v in enumerate(rho)) for i in range(73)]
        need([act(rho, x) for x in rho] == [1 << i for i in range(73)] and rho == transpose, "Actual orthogonal involution")
        need(act(rho, delta) == view["translation_before_route"], "Actual route then translation")
        linear = [(v.bit_count() + 2 * ((delta >> i) & 1) - 1) % 4 for i, v in enumerate(transpose)]
        quadratic = [(-2 * (a & b).bit_count()) % 4 for i, a in enumerate(transpose) for b in transpose[i + 1:]]
        need(not any(linear + quadratic), "Completed FULL phase endpoint")
    wrappers = {str(stage): dict(enter=[["VIEW", row, stage, A[row], False] for row in range(8)],
                                leave=[["VIEW", row, stage, A[row], True] for row in reversed(range(8))])
                for stage in range(1, 9)}
    return views, wrappers


def main():
    need(shutil.disk_usage(HERE).free >= 3 * 2**30, "At least 3 GiB free")
    probe, sources, matrices, inverses = load_data()
    for path, digest in BACKEND.items():
        need(sha256((ROOT / path).read_bytes()).hexdigest() == digest, "Exact stream source pin")
    classes, lookup = {}, []
    for matrix in matrices:
        first = next(value for row in matrix for value in row if value)
        sign = 1 if first > 0 else -1
        key = tuple(sign * value for row in matrix for value in row)
        if key not in classes:
            canonical = [list(key[i:i + 8]) for i in range(0, 64, 8)]
            factor = smith(canonical)
            diagonal = [[factor["diagonal"][i] * I[i][j] for j in range(8)] for i in range(8)]
            need(multiply(multiply(factor["left"], canonical), factor["right"]) == diagonal, "Actual Smith factors")
            need(all(2145 % d == 0 for d in factor["diagonal"]), "No new odd divisor")
            classes[key] = dict(index=len(classes), matrix=canonical, **factor)
        lookup.append([classes[key]["index"], sign])
    classes = list(classes.values())
    need(len(classes) == 172, "All actual sign classes")
    selectors = {"bit_" + str(bit): [chi for chi in range(512) if (chi >> bit) & 1] for bit in range(9)}
    mode_word = build_mode_word(classes, lookup, selectors)
    mode_bounds = check_modes(mode_word, selectors, inverses)
    walsh_words = dict(forward=walsh_word(False), inverse=walsh_word(True))
    check_walsh(walsh_words)
    check_walsh_kernel(inverses, probe)
    counter = check_counter()
    try:
        check_modes([gate for gate in mode_word if gate[0] != "DIVIDE_ODD"], selectors, inverses)
    except ValueError as error:
        need(str(error) == "Exact emitted character inverse and zero owned output", "Expected control failure")
    else:
        raise ValueError("Missing odd division must fail")
    views, wrappers = check_views(sources)
    body = walsh_words["forward"] + mode_word + walsh_words["inverse"]
    counts = {name: invoice(word) for name, word in dict(walsh_forward=walsh_words["forward"], mode=mode_word,
                                                       walsh_inverse=walsh_words["inverse"], complete=body).items()}
    need(counts["walsh_forward"]["uniform_scalar_primitives"] == 1008, "Forward uniform invoice")
    need(counts["walsh_inverse"]["uniform_scalar_primitives"] == 864, "Inverse uniform invoice")
    need(counts["complete"]["translation_maps"] == 144, "Complete translation invoice")
    need(counts["complete"]["real_odd_division_scans"] == 16, "One division per complex output")
    payload = dict(schema="inplace-centre-translation-inverse-v1", selected_ports=A, live_fields=list(range(8)), owned=C0,
                   selectors=selectors, classes=classes, mode_lookup=lookup, walsh_words=walsh_words,
                   mode_word=mode_word, body=body, stage_wrappers=wrappers, completed_views=views,
                   instruction_order="Each instruction is [operation, selector, target, arguments]. A null selector means all addresses.",
                   translation_rule="Repeat the nine-bit shift in every tensor copy. Leave the other coordinates unchanged.",
                   selector_rule="The selector table uses the nine first-copy address bits. These bits are held in a finite control register.",
                   view_rule="Enter by route then translation. Leave by inverse translation then inverse route.")
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    program_path = HERE / "INPLACE-PROGRAM.json.gz"
    program_path.write_bytes(gzip.compress(raw, mtime=0))
    receipt = dict(status="PASS_INPLACE_TRANSLATION_INVERSE", source_pins=probe["source_pins"], backend_source_pins=BACKEND,
                   source_probe_sha256="ebff70f4ff3d28c345080a4d7b1d90cd952a6208b7f6449037b96dbf3531c024",
                   checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(), counts=counts, mode_bounds=mode_bounds,
                   payload_raw_sha256=sha256(raw).hexdigest(), payload_compressed_sha256=sha256(program_path.read_bytes()).hexdigest(),
                   classes=len(classes), diagonal_types=dict(Counter(str(x["diagonal"]) for x in classes)),
                   maximum_integer_add=max(abs(gate[3]) for x in classes for gate in x["left_word"] + x["right_word"] if gate[0] == "ADD_INTEGER"),
                   smith_row_column_gates=sum(len(x["left_word"]) + len(x["right_word"]) for x in classes),
                   all_width_operator="W^-1 diag(T_chi^-1) W = T^-1, with simultaneous shifts and first-copy selectors.",
                   all_width_prefix_row_norm_bound=str(max(F(2), F(mode_bounds["maximum_intermediate_row_one_norm"]),
                                                          512 * F(mode_bounds["maximum_final_row_one_norm"]))),
                   native_children=0, completed_view_maps_per_call=16, owned_fields=1, owned_arbitrary_input=True,
                   owned_output_zero=True, arbitrary_live_fields=8, other_fields_unchanged=True,
                   mode_replay_formal_input_columns=9,
                   maximum_odd_height_increase=1, conditional_backend="Direct in-place marked-counter scans; no array split.",
                   marked_counter_checks=counter, missing_odd_division_control=True,
                   extra_dyadic_fractional_bits=9, inverse_walsh_kernel_entries_checked=32768,
                   exact_character_word_checks=512, character_inverse_orders_checked=1024, completed_views_checked=64,
                   scope="One completed selected bank, one owned field, explicit conditional scans, and the fixed 2145 odd grid. No global lease or decoder claim.")
    for path, digest in BACKEND.items():
        need(sha256((ROOT / path).read_bytes()).hexdigest() == digest, "Stream source unchanged")
    for key, pin in probe["source_pins"].items():
        need(sha256(Path(pin["path"]).read_bytes()).hexdigest() == pin["sha256"], "Source unchanged: " + key)
    (HERE / "INPLACE-SERVICE.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(receipt["status"])
    print(json.dumps(dict(counts=counts, mode_bounds=mode_bounds, prefix_bound=receipt["all_width_prefix_row_norm_bound"]), sort_keys=True))


if __name__ == "__main__":
    main()
