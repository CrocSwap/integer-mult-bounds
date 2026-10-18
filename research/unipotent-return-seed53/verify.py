"""Independent matrix/accounting checks. No predecessor executable imports.

Sagar Thakrar with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import model

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return [[Fraction(i == j) for j in range(n)] for i in range(n)]


def trace(word, n):
    """All dirty basis columns, every prefix, exact instruction/read counts."""
    rows = identity(n)
    peak = Fraction(1)
    denominator = 1
    adds = scales = reads = travel = 0
    head = 0
    witness = {"after_instruction": 0, "row": 0, "coefficients": [str(x) for x in rows[0]]}
    for step, (op, dst, src, num, den) in enumerate(word, 1):
        require(0 <= dst < n and 0 <= src < n, "address out of range")
        if op == "ADD":
            require(dst != src and num in (-1, 1) and den == 1, "invalid ADD")
            rows[dst] = [x + num * y for x, y in zip(rows[dst], rows[src])]
            adds += 1
            reads += 2
            travel += abs(head - src) + abs(src - dst)
        elif op == "SCALE":
            require(src == dst and (num, den) in ((2, 1), (1, 2)), "invalid SCALE")
            rows[dst] = [x * Fraction(num, den) for x in rows[dst]]
            scales += 1
            reads += 1
            travel += abs(head - dst)
        else:
            raise ValueError("unknown instruction")
        head = dst
        row_sum = sum(abs(x) for x in rows[dst])
        if row_sum > peak:
            peak = row_sum
            witness = {"after_instruction": step, "row": dst, "coefficients": [str(x) for x in rows[dst]]}
        denominator = max(denominator, max(x.denominator for x in rows[dst]))
    return rows, {"ADD": adds, "SCALE": scales, "total": adds + scales,
                  "data_reads": reads, "data_writes": adds + scales,
                  "instruction_reads": adds + scales, "data_head_travel": travel,
                  "prefix_row_l1": str(peak), "prefix_witness": witness,
                  "max_denominator": denominator}


def direct_reader(tree):
    """Separate traversal of semantic leaves, without invoice/emitter helpers."""
    stack, leaves = [tree], []
    while stack:
        t = stack.pop()
        if isinstance(t, dict):
            leaves.append(t["reader"])
        else:
            stack.extend(t)
    return [[sum(r[i][j] for r in leaves) for j in range(len(leaves[0][0]))]
            for i in range(2)]


def expected(tree, n, source=2, drift=False):
    rows = identity(n)
    r = direct_reader(tree)
    for i in range(2):
        for j, coefficient in enumerate(r[i]):
            rows[i][source + j] += coefficient
    if drift:
        for j in range(0, len(r[0]), 2):
            rows[source + j][source + j + 1] += 1
    return rows


def digest(word):
    return hashlib.sha256(json.dumps(word, separators=(",", ":")).encode()).hexdigest()


def check_echo(tree, m, label):
    n = 2 + (model.height(tree) + 1) * 2 * m
    target = expected(tree, n)
    receipt = {"label": label, "registers": n, "depth": model.height(tree)}
    for mode in ("eager", "carry"):
        word = model.emit_echo(tree, 2, 2 + 2 * m, m, mode)
        got, bill = trace(word, n)
        require(got == target, label + " endpoint " + mode)
        require((bill["ADD"], bill["SCALE"]) == model.invoice(tree, m, mode, root=True),
                label + " recursive invoice")
        require(bill["max_denominator"] == 1, "integer-grid divisibility")
        inv, inverse_bill = trace(model.inverse(word), n)
        reverse = identity(n)
        for i in range(2):
            for j in range(2, 2 + 2 * m):
                reverse[i][j] -= target[i][j]
        require(inv == reverse, "literal inverse")
        require((inverse_bill["ADD"], inverse_bill["SCALE"]) == (bill["ADD"], bill["SCALE"]),
                "inverse invoice")
        require(inverse_bill["max_denominator"] == 1, "inverse integer-grid divisibility")
        bill["inverse_prefix_row_l1"] = inverse_bill["prefix_row_l1"]
        for program, growth in ((word, bill), (model.inverse(word), inverse_bill)):
            witness = growth["prefix_witness"]
            signs = [(Fraction(x) > 0) - (Fraction(x) < 0) for x in witness["coefficients"]]
            attained = model.execute(program[:witness["after_instruction"]], signs)[witness["row"]]
            require(attained == Fraction(growth["prefix_row_l1"]), "prefix growth witness")
        for shift in (0, 7, 53):
            vector = [Fraction((7 * j + shift) % 17 - 8, 2 ** (j % 4)) for j in range(n)]
            oracle = [sum(x * y for x, y in zip(row, vector)) for row in target]
            out = model.execute(word, vector)
            require(out == oracle, "dirty rational vector")
            require(model.execute(model.inverse(word), out) == vector, "scalar inverse")
        bill["word_sha256"] = digest(word)
        receipt[mode] = bill
    return receipt


def admission_census():
    count = 0
    # RP=QR for J direct-sum J. This check does not use the block constructor.
    for entries in itertools.product((-1, 0, 1), repeat=8):
        r = [list(entries[:4]), list(entries[4:])]
        rp = [row[:] for row in r]
        for row in rp:
            row[1] += row[0]
            row[3] += row[2]
        qr = [[x + y for x, y in zip(r[0], r[1])], r[1][:]]
        admitted = rp == qr
        structural = r[1][0] == r[1][2] == 0 and r[0][0] == r[1][1] and r[0][2] == r[1][3]
        require(admitted == structural, "intertwiner characterization")
        if admitted:
            count += 1
            children = [{"reader": r}] * 3
            word = model.emit_echo(children, 2, 6, 2, "carry")
            require(trace(word, 10)[0] == expected(children, 10), "admitted reader replay")
    return {"matrices": 3 ** 8, "admitted": count}


def power_census():
    for exponent in range(-80, 81):
        word = model.power([(0, 1)], exponent)
        got, bill = trace(word, 2)
        target = identity(2)
        target[0][1] = exponent
        require(got == target, "power lowering")
        require((bill["ADD"], bill["SCALE"]) == model.power_bill(exponent), "power price")
        require(bill["prefix_row_l1"] == str(1 + abs(exponent)), "power growth")
        require(bill["max_denominator"] == 1, "power halving exactness")
        require(trace(model.inverse(word), 2)[0][0][1] == -exponent, "power inverse")
    return 161


def unit_tariff_census():
    cases = 0
    for k in range(1, 13):
        states = range(-k, k + 1)
        for a in range(1, 6):
            for b in range(1, 4):
                costs = {t: (a + b) * abs(t) for t in states}
                for _ in range(k):
                    costs = {s: min(v + a * abs(s - t - 1) + b * abs(s - t)
                                    for t, v in costs.items()) for s in states}
                require(costs[0] == k * a, "unit-power obstruction")
                cases += 1
    return cases


def negative_controls():
    children, m = model.fixture(5, 2), 2
    work, n = 6, 10
    good = model.emit_echo(children, 2, work, m, "carry")
    oracle = expected(children, n)
    group = model.emit_group(children, work, m, "carry")
    copy = [("ADD", work + j, 2 + j, 1, 1) for j in range(4)]
    controls = {}
    variants = {
        "omit_workspace_return": group[:-len(model.power(model.pairs_at(work, m), -5)) - len(model.power([(0, 1)], -4))]
                                 + model.power([(0, 1)], -4),
        "omit_output_return": group[:-len(model.power([(0, 1)], -4))],
    }
    align = group.index(("ADD", 0, 1, 1, 1))
    variants["omit_output_alignment"] = group[:align] + group[align + 1:]
    half = next(i for i, gate in enumerate(group) if gate[0] == "SCALE" and gate[3:] == (1, 2))
    variants["omit_paid_halving"] = group[:half] + group[half + 1:]
    # Compare each corrupted canonical group before forming an echo: an echo
    # can hide a source drift that cancels in its literal inverse.
    group_target = expected(children, n, source=work)
    for name, bad in variants.items():
        require(trace(bad, n)[0] != group_target, "vacuous control: " + name)
        controls[name] = "rejected canonical child contract"
    malformed = model.fixture(5, 2)
    malformed[1]["reader"][1][0] = 1
    bad = model.emit_echo(malformed, 2, work, m, "carry")
    require(trace(bad, n)[0] != expected(malformed, n), "nonintertwiner control")
    controls["nonintertwining_reader"] = "rejected endpoint"
    for name, bad in {
        "forward_instead_of_inverse": copy + group + model.inverse(copy) + group,
        "omit_source_unload": copy + group + model.inverse(group),
    }.items():
        require(trace(bad, n)[0] != oracle, "vacuous control: " + name)
        controls[name] = "rejected endpoint"
    _, bill = trace(good, n)
    require(bill["SCALE"] > 0 and bill["ADD"] != sum(model.invoice(children, m, "carry", root=True)),
            "unpriced scale control")
    controls["omit_scale_invoice"] = "rejected complete invoice"
    return controls


def source_check():
    path = HERE / "SOURCES.json"
    if not path.exists():
        raise ValueError("missing SOURCES.json")
    sources = json.loads(path.read_text())
    root = HERE.parent.parent
    for row in sources["files"]:
        if row["usage"] == "input":
            require(hashlib.sha256((root / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                    "live source drift: " + row["path"])
    for row in sources["predecessors"]:
        raw = (HERE / row["snapshot"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "predecessor SHA256 drift")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(blob == row["git_blob"], "predecessor Git blob drift")


def build_result():
    main = model.fixture()
    nested = [model.fixture(17, 5, 53 + j) for j in range(3)]
    cases = [check_echo(main, 5, "k53_m5"), check_echo(nested, 5, "three_k17_children")]
    # Internal contract also includes the one required source drift.
    for tree in (main, nested):
        n = 2 + (model.height(tree) + 1) * 10
        for mode in ("eager", "carry"):
            word = model.emit_node(tree, 2, 12, 5, mode)
            got, bill = trace(word, n)
            require(got == expected(tree, n, drift=True), "internal typed return")
            require((bill["ADD"], bill["SCALE"]) == model.invoice(tree, 5, mode), "internal invoice")
    return {"status": "scoped construction; no new kappa", "seed": 53,
            "base": "ef5f39403610d231a0c27e8a6b4f08c10209bcd6",
            "boundary": {"eager": list(model.boundary_bill(53, 5, "eager")),
                         "carry": list(model.boundary_bill(53, 5, "carry"))},
            "power_cases": power_census(), "admission": admission_census(),
            "unit_tariff_cases": unit_tariff_census(), "echoes": cases,
            "negative_controls": negative_controls()}


def main():
    source_check()
    result = build_result()
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    require(not sys.argv[1:], "expected no arguments or --emit")
    require(result == json.loads((HERE / "RESULT.json").read_text()), "saved result mismatch")
    pilot = result["echoes"][0]
    print("PASS_UNIPOTENT_RETURN seed=53 boundary=265->135 total="
          + str(pilot["eager"]["total"]) + "->" + str(pilot["carry"]["total"])
          + " powers=161 admitted=81/6561 unit_cases=180 controls=8 no_new_kappa")


if __name__ == "__main__":
    main()
