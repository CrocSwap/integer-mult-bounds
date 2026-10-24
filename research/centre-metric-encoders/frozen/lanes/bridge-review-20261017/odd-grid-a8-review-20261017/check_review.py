"""Review the odd-grid factors with integer-grid basis columns."""

from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
import json
from math import gcd, lcm
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
SOURCE = LANES / "independent-review-20261017/odd-grid-a8-20261017"
INTERFACE = LANES / "new-core-transfer-20261017/INTERFACE.json"
INTERFACE_PIN = "c6ca09711622ce4ad236f78cc28c03b6c46808a9d91cfc1722ff4fe371f38746"
FREEZES = {
    "FREEZE-A8-ODD-GRID.json": "97f00c72bc3baeb4ce3ca91b91d9e46d7978d7ec502bee77845f5484731bb086",
    "FREEZE-MINOR-FACTORS.json": "de05cc545581deadbe855e6ae214c9cda79a6b20add92948d066a95756ed4219",
}
C = 112
N = 113


def require(ok, message):
    if not ok:
        raise ValueError(message)


def split(n):
    t = 0
    while n % 2 == 0:
        n //= 2
        t += 1
    return t, n


def sources():
    for name, digest in FREEZES.items():
        raw = (SOURCE / name).read_bytes()
        require(sha256(raw).hexdigest() == digest, name)
        data = json.loads(raw)
        for path, pin in data["files"].items():
            content = (SOURCE / path).read_bytes()
            if isinstance(pin, dict):
                require(len(content) == pin["bytes"], path + " byte count")
                pin = pin["sha256"]
            require(sha256(content).hexdigest() == pin, path)
    require(sha256(INTERFACE.read_bytes()).hexdigest() == INTERFACE_PIN, "Actual R pin")
    pins = json.loads((SOURCE / "SOURCE-PINS.json").read_text())
    for item in pins["sources"]:
        raw = (SOURCE / item["local_copy"]).read_bytes()
        require(sha256(raw).hexdigest() == item["sha256"], "Model source SHA256")
        require(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == item["git_blob"], "Model Git blob")
    pr_pins = json.loads((SOURCE / "sources/GITHUB-PINS.json").read_text())
    for item in pr_pins:
        raw = (SOURCE / "sources" / item["local"]).read_bytes()
        require(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == item["git_blob"], "Pinned PR Git blob")
    rows = json.loads(INTERFACE.read_text())["R"]
    r = [[Fraction(row.get(str(p), 0)) for p in range(112)] for row in rows]
    require(len(r) == 8 and all(x in (-1, 0, 1) for row in r for x in row), "Signed unit R")
    r = [[int(x) for x in row] for row in r]
    require(all(sum(x != 0 for x in row) == 56 for row in r), "Actual row support")
    report = json.loads((SOURCE / "MINOR-FACTORS.json").read_text())
    minors = report["minors"]
    require(len(minors) == 14 and sorted(p for minor in minors for p in minor) == list(range(112)), "Complete minor partition")
    for minor in minors:
        require(len(minor) == 8, "Eight columns per minor")
        for i in range(8):
            require(sum(r[i][p] != 0 for p in minor) == 4, "Four signed units per minor row")
            for j in range(8):
                require(sum(r[i][p] * r[j][p] for p in minor) == (4 if i == j else 0), "Actual minor Gram 4I")
    g = [[sum(r[i][p] * r[i][q] for i in range(8)) for q in range(112)] for p in range(112)]
    return r, g, minors, report, pins, pr_pins


def endpoint(g, selected, kind, denominator):
    ordinary = set(range(112)) - selected
    k = len(selected) // 8
    out = [[0] * N for _ in range(N)]
    for p in range(112):
        out[p][p] = denominator * (-1 if kind.startswith("content") and p in selected else 1)
        for q in range(112):
            if kind == "H":
                coefficient = Fraction(-g[p][q], 4) if p in ordinary and q in ordinary else 0
            elif kind == "inverse":
                coefficient = Fraction(g[p][q], 4 * (k - 13)) if p in ordinary and q in ordinary else 0
            elif kind == "fused":
                coefficient = Fraction(g[p][q], 4 * (k - 13)) if q in ordinary else 0
            elif kind == "content":
                coefficient = Fraction(g[p][q], 4 * (k - 13))
            else:
                sign = (-1 if p in selected else 1) * (-1 if q in selected else 1)
                coefficient = Fraction(sign * g[p][q], 4 * (k - 1))
            value = denominator * coefficient
            require(Fraction(value).denominator == 1, "Endpoint fits the chosen integer grid")
            out[p][q] += int(value)
    return out


def execute(word, denominator, odd, clear_count):
    state = [[denominator if i == j else 0 for j in range(N)] for i in range(N)]
    counts = Counter()
    old_cost = 0
    max_norm_numerator = denominator
    binary_height = 0
    odd_denominator = 1
    divisions = []
    changed_coefficients = 0
    for position, event in enumerate(word):
        kind, target = event[:2]
        require(0 <= target < N, "Declared target")
        counts[kind] += 1
        if kind == "clear":
            require(target == C, "Only the owned accumulator is cleared")
            state[C] = [0] * N
            old_cost += 2
        elif kind == "add":
            source, coefficient = event[2], Fraction(event[3])
            require(0 <= source < N and source != target and coefficient in (-1, 1), "Distinct unit ADD")
            sign = int(coefficient)
            state[target] = [a + sign * b for a, b in zip(state[target], state[source])]
            old_cost += 8
        elif kind == "scale":
            q = Fraction(event[2])
            require(target == C or q == -1, "Only signs on data")
            require(abs(q.numerator) == 1 and q.denominator & (q.denominator - 1) == 0, "Signed binary SCALE")
            require(all(v % q.denominator == 0 for v in state[target]), "Exact binary scale on every encoded basis column")
            state[target] = [v // q.denominator * q.numerator for v in state[target]]
            old_cost += 2 * ((q.denominator.bit_length() - 1) + (q.numerator < 0))
        else:
            require(kind == "divide_odd" and target == C and event[2] == odd and odd > 1, "Distinct fixed odd-division opcode")
            before_odd = lcm(*(split(denominator // gcd(abs(v), denominator))[1] for v in state[C]))
            require(before_odd == 1, "The complete query cancels prior local odd denominators")
            require(all(v % odd == 0 for v in state[C]), "Every encoded basis numerator is divisible at the scan")
            state[C] = [v // odd for v in state[C]]
            divisions.append(position)
        max_norm_numerator = max(max_norm_numerator, sum(abs(v) for v in state[target]))
        for v in state[target]:
            if not v:
                continue
            binary, local_odd = split(denominator // gcd(abs(v), denominator))
            binary_height = max(binary_height, binary)
            odd_denominator = lcm(odd_denominator, local_odd)
            require(odd % local_odd == 0, "At most one stated odd denominator at every prefix")
            changed_coefficients += 1
    if word:
        require(counts["clear"] == clear_count and not any(state[C]), "Owned C0 clears and final zero")
        require(all(row[C] == 0 for row in state), "No output depends on initial owned C0")
    return state, {
        "old_real_primitives": old_cost,
        "real_odd_scans": 2 * len(divisions),
        "events": dict(counts),
        "additional_binary_height": binary_height,
        "prefix_odd_denominator_divides": odd_denominator,
        "max_row_l1": str(Fraction(max_norm_numerator, denominator)),
        "encoded_coefficient_checks": changed_coefficients,
        "division_sites": divisions,
    }


def compare(receipt, producer, baseline=False):
    fields = {
        "old_real_primitives": "old_real_primitives",
        "real_odd_scans": "real_division_by_3_scans" if baseline else "real_odd_scans",
        "additional_binary_height": "binary_height" if baseline else "additional_binary_height",
        "max_row_l1": "max_coefficient_row_l1" if baseline else "max_row_l1",
        "events": "event_counts" if baseline else "events",
    }
    for ours, theirs in fields.items():
        require(receipt[ours] == producer[theirs], "Independent receipt field " + ours)


def factor_checks(g, minors, family):
    words = json.loads((SOURCE / "A8-ODD-GRID-WORDS.json").read_text())
    reports = json.loads((SOURCE / "A8-ODD-GRID.json").read_text())
    selected = set(minors[0])
    baseline = {}
    for name, kind in [("H", "H"), ("H_inverse", "inverse"), ("H_inverse_fused_upper", "fused")]:
        den, odd = (4, 1) if kind == "H" else (48, 3)
        actual, receipt = execute(words[name], den, odd, 16)
        require(actual == endpoint(g, selected, kind, den), "A8 full basis endpoint")
        compare(receipt, reports["local_factors"][name], True)
        require(receipt["old_real_primitives"] == {"H": 6720, "inverse": 6752, "fused": 7008}[kind], "A8 baseline invoice")
        baseline[name] = receipt
    all_words = json.loads((SOURCE / "MINOR-FACTOR-WORDS.json").read_text())
    all_receipts, controls = {}, 0
    for k in range(15):
        selected = set(p for minor in minors[:k] for p in minor)
        if k == 13:
            ordinary = set(range(112)) - selected
            require(all(g[p][q] == (4 if p == q else 0) for p in ordinary for q in ordinary), "H13 is zero on all ordinary fields")
            continue
        case = {}
        for kind, word in all_words[str(k)].items():
            den = 4 if kind == "H" else 4 * abs(k - (1 if kind == "content_inverse" else 13))
            if not word:
                require(k == 14 and kind in ["H", "inverse", "fused"], "Only the empty ordinary identities")
                den = 1
            binary, odd = split(den)
            actual, receipt = execute(word, den, odd, 9)
            want = endpoint(g, selected, kind, den)
            if not word:
                want[C][C] = den
            require(actual == want, "Family full basis endpoint: " + str(k) + " " + kind)
            compare(receipt, family["cases"][str(k)][kind])
            closed_cost = {
                "H": 7218 - 512 * k,
                "inverse": 7186 - 512 * k + 16 * binary,
                "fused": 7186 - 256 * k + 16 * binary,
                "content": 7186 + 16 * k + 16 * binary,
                "content_inverse": 7186 + 16 * k + 16 * binary,
            }[kind] if word else 0
            require(receipt["old_real_primitives"] == closed_cost
                    and receipt["real_odd_scans"] == (16 if word and odd > 1 else 0), "Independent closed invoice")
            if word:
                require(receipt["additional_binary_height"] <= 5, "Uniform binary height")
                require(Fraction(receipt["max_row_l1"]) <= 6328, "Uniform prefix norm")
                first_scatter = next(i for i, e in enumerate(word) if e[0] == "add" and e[1] != C)
                wrong = [list(e) for e in word]
                wrong[first_scatter][3] = str(-Fraction(wrong[first_scatter][3]))
                try:
                    bad, _ = execute(wrong, den, odd, 9)
                except ValueError as error:
                    require(str(error) in {
                        "Exact binary scale on every encoded basis column",
                        "The complete query cancels prior local odd denominators",
                        "Every encoded basis numerator is divisible at the scan",
                        "At most one stated odd denominator at every prefix"}, "Expected mutation rejection")
                else:
                    require(bad != want, "Wrong scatter changes the exact endpoint")
                controls += 1
            case[kind] = receipt
        predicted = family["cases"][str(k)]["predicted_local"]
        require(predicted["balanced_F_old"] == 164514 + 416 * k + 14 + case["H"]["old_real_primitives"]
                and predicted["balanced_B_old"] == 164514 + 208 * k + 14 + case["inverse"]["old_real_primitives"]
                and predicted["fused_B_old"] == 164514 + 208 * k + 14 + case["fused"]["old_real_primitives"],
                "Conditional local assembly sums")
        all_receipts[str(k)] = case
    require(sum(len(c) for c in all_receipts.values()) == 69 and controls == 66, "All factor and mutation cases")
    return baseline, all_receipts, controls


def structural_checks(r, g, minors):
    a = set(minors[0])
    e = [-1 if p in a else 1 for p in range(112)]
    for i in range(8):
        for j in range(8):
            require(sum(r[i][p] * r[j][p] for p in range(112) if p not in a) == (52 if i == j else 0), "Actual A8 Gram 52I")
            require(sum(r[i][p] * e[p] * r[j][p] for p in range(112)) == (48 if i == j else 0), "R E K=12I")
    # Multiply the scaled projector independently as dense integer matrices.
    projector = [[48 * (p == q) - e[p] * g[p][q] for q in range(112)] for p in range(112)]
    columns = list(zip(*projector))
    require(all(sum(x * y for x, y in zip(row, col)) == 48 * projector[p][q]
                for p, row in enumerate(projector) for q, col in enumerate(columns)), "E A8 is a projector over Q")
    require(sum(projector[p][p] for p in range(112)) == 48 * 104, "Projector trace and rank 104")
    for p in range(112):
        for i in range(8):
            require(sum(projector[p][q] * e[q] * r[i][q] for q in range(112)) == 0, "Its kernel is the independent eight-channel E K image")
    return {"R_U_R_U_transpose": "52 I8", "R_E_K": "12 I8", "A8_rank": 104, "A8_nullity": 8,
            "ordinary_singular_k": 13, "content_singular_k": 1, "minor_Gram_checks": 14 * 64}


def bit_scan(number, width, odd, inverse):
    source = number % (1 << width)
    carry = 0
    output = 0
    for i in range(width):
        bit = (source >> i) & 1
        if inverse:
            value = (bit - carry) & 1
            carry = (carry + odd * value - bit) // 2
        else:
            value, carry = (odd * bit + carry) & 1, (odd * bit + carry) // 2
        require(0 <= carry < odd, "Finite scan carry bound")
        output |= value << i
    input_sign = (source >> (width - 1)) & 1
    output_sign = (output >> (width - 1)) & 1
    valid = carry == (odd * output_sign - input_sign if inverse else odd * input_sign - output_sign)
    return valid, output - (1 << width) * output_sign


def scan_checks():
    odds = [3, 5, 7, 9, 11, 13]
    results = []
    for odd in odds:
        count = 0
        for width in range(1, 13):
            modulus = 1 << width
            inverse_modulus = pow(odd, -1, modulus)
            lo, hi = -modulus // 2, modulus // 2
            for number in range(lo, hi):
                valid, quotient = bit_scan(number, width, odd, True)
                require(quotient % modulus == (number * inverse_modulus) % modulus, "Independent modular quotient")
                require(valid == (number % odd == 0) and (not valid or quotient * odd == number), "Signed exact division at all tested inputs")
                good, product = bit_scan(number, width, odd, False)
                require(good == (lo <= number * odd < hi) and (not good or product == number * odd), "Signed multiplication and guard test")
                count += 1
        require(not bit_scan(1, 12, odd, True)[0], "Unconverted finest-grid numerator fails")
        results.append({"odd": odd, "signed_inputs": count, "directions": 2})
    require(lcm(*odds) == 45045 and 45045 < 2**16 and 45045 == 3 * 3 * 5 * 7 * 11 * 13, "Uniform root divisor and six scans")
    return results


def recursive_grid_check(depth, odd):
    scale = odd ** (depth + 1)
    rows = [[scale, 0], [0, scale]]
    peak_height = 0
    calls = 0

    def visit(remaining):
        nonlocal peak_height, calls, rows
        calls += 1
        saved = [list(r) for r in rows]
        rows[0] = [a + b for a, b in zip(rows[0], rows[1])]
        require(all(v % odd == 0 for v in rows[0]), "Active-chain grid divisibility")
        rows[0] = [v // odd for v in rows[0]]
        for row in rows:
            for v in row:
                d, h = scale // gcd(abs(v), scale), 0
                while d > 1:
                    require(d % odd == 0, "Fixture denominator power")
                    d //= odd
                    h += 1
                peak_height = max(peak_height, h)
        if remaining:
            visit(remaining - 1)
            visit(remaining - 1)
        rows[0] = [odd * a - b for a, b in zip(rows[0], rows[1])]
        require(rows == saved, "Every complete child restores both arbitrary columns")

    visit(depth)
    require(rows == [[scale, 0], [0, scale]] and peak_height == depth + 1, "Dyadic outer endpoint and depth-only height")
    # Three completed rational children defeat a depth-one height budget.
    wrong = odd**2
    for _ in range(2):
        require(wrong % odd == 0, "Rational-endpoint control setup")
        wrong //= odd
    require(wrong % odd != 0, "Completed rational children require another bound")
    return {"recursive_edges": depth, "completed_nodes": calls, "odd": odd, "maximum_height": peak_height}


def main():
    r, g, minors, family, pins, pr_pins = sources()
    structural = structural_checks(r, g, minors)
    baseline, factors, mutations = factor_checks(g, minors, family)
    scans = scan_checks()
    recursive = [recursive_grid_check(depth, odd) for depth in range(6) for odd in [3, 45045]]
    out = {"status": "PASS_INDEPENDENT_ODD_GRID_AND_MINOR_FACTORS", "source_freezes": FREEZES,
           "interface_sha256": INTERFACE_PIN, "model_sources": pins["sources"], "pinned_pr_sources": pr_pins,
           "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
           "method": "Dense integer-grid basis replay, exact divisibility at every opcode, independent formula endpoints, and dense projector multiplication. No producer module is imported.",
           "formal_input_columns": 113, "structural": structural, "A8_baseline": baseline,
           "minor_factors": factors, "wrong_scatter_controls": mutations,
           "signed_scan_checks": scans, "recursive_grid_fixtures": recursive,
           "proof_scope": "The source-backed active-chain proof covers general recursion. The fixtures check the invariant and its necessary hypotheses.",
           "limits": ["Only common-frame scalar factors are reviewed here", "No new native recipe or H1 child is inserted by these words", "Complete local transfer is a separate review", "Binary guard constants, hosting, final dyadic endpoint and full supplier moment remain separate"]}
    (HERE / "REVIEW.json").write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    print(out["status"])
    print(json.dumps({"factors": 69, "A8_baselines": 3, "columns": 113, "mutations": mutations,
                      "signed_scan_inputs": sum(s["signed_inputs"] for s in scans), "recursive_fixtures": len(recursive)}, sort_keys=True))


if __name__ == "__main__":
    main()
