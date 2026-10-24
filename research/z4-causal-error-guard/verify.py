"""Causal relative-ADD error bound for the unchanged persistent z4 word.

Produced by Nick Petalas. Apache-2.0.
The word emitter is Cinna Davis's PR1391, retained by PR1410.
The local error model and impulse interpretation are from ywz65 / PR2502.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCALE = 1 << 32
WIDTH = 56
MAX_RECORDS = 2048


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def check_sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for row in manifest["files"]:
        if row["usage"] == "input":
            raw = (ROOT / row["path"]).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == row["sha256"],
                    "source drift: " + row["path"])


def load_word():
    # Only construct the predecessor's word. Its verifier is never invoked.
    path = ROOT / "research/z4-persistent-pair-seed57/inputs/PR1391-verify.py"
    spec = importlib.util.spec_from_file_location("pinned_pr1391", path)
    require(spec is not None and spec.loader is not None, "emitter loader")
    emitter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(emitter)
    body = emitter.lift_word(
        emitter.batch_word([0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 0],
                           blocks=(0, 1, 2, 0, 1) * 2),
        list(range(8)) + list(range(32, 56)))
    word = ([('ADD', 32 + i, 8 + i, 1) for i in range(24)] + body
            + [('ADD', 32 + i, 8 + i, -1) for i in range(24)]
            + emitter.inverse_word(body))
    old = json.loads((ROOT / "research/z4-persistent-pair-seed57/RESULT.json").read_text())
    raw = json.dumps(word, separators=(",", ":"), ensure_ascii=True).encode()
    require(hashlib.sha256(raw).hexdigest() == old["ten_child_joint"]["word_sha256"],
            "joint word source identity")
    return word


def validate_word(word, width, q):
    require(type(width) is int and 1 <= width <= WIDTH, "width bound")
    require(type(q) is int and 0 <= q <= 32, "guard bound")
    require(1 <= len(word) <= MAX_RECORDS, "record bound")
    for gate in word:
        require(len(gate) == 4, "gate arity")
        kind, dst, src, sign = gate
        require(type(dst) is int and 0 <= dst < width, "destination")
        if kind == "ADD":
            require(type(src) is int and 0 <= src < width and src != dst,
                    "ADD source")
            require(type(sign) is int and sign in (-1, 1), "ADD sign")
        else:
            require(kind == "NEG" and src is None and sign == 0, "exact NEG")


def combine(left, right, sign):
    result = dict(left)
    for key, value in right.items():
        result[key] = result.get(key, 0) + sign * value
        if result[key] == 0:
            del result[key]
    return result


def weighted(row, bounds):
    return sum(abs(value) * bounds[index] for index, value in row.items())


def causal_bound(word, width, q):
    validate_word(word, width, q)
    divisor = 1 << q
    inputs = [{i: 1} for i in range(width)]
    impulses = [{} for _ in range(width)]
    bounds, weights, cut_bounds = [], [], []
    peak = {"numerator": 0, "cut": 0, "row": 0}
    for cut, (kind, dst, src, sign) in enumerate(word, 1):
        if kind == "ADD":
            a = sum(map(abs, inputs[dst].values())) + sum(map(abs, inputs[src].values()))
            feedback = weighted(impulses[dst], bounds) + weighted(impulses[src], bounds)
            bounds.append(SCALE * a + (feedback + divisor - 1) // divisor)
            weights.append(a)
            inputs[dst] = combine(inputs[dst], inputs[src], sign)
            impulses[dst] = combine(impulses[dst], impulses[src], sign)
            impulses[dst][len(bounds) - 1] = 1
        else:
            inputs[dst] = {i: -v for i, v in inputs[dst].items()}
            impulses[dst] = {i: -v for i, v in impulses[dst].items()}
        value = weighted(impulses[dst], bounds)
        cut_bounds.append(value)
        if value > peak["numerator"]:
            peak = {"numerator": value, "cut": cut, "row": dst}
    report = {"q": q, "scale": SCALE, "records": len(word), "adds": len(bounds),
              "word_sha256": digest(word), "beta_sha256": digest(bounds),
              "weights_sha256": digest(weights), "cut_bounds_sha256": digest(cut_bounds),
              "peak": peak, "certifies": peak["numerator"] <= SCALE * divisor}
    return report, bounds, weights, cut_bounds


def adjoint(word, cut, row, width):
    # Reverse a single covector; do not reuse forward coefficient arithmetic.
    covector = [0] * width
    covector[row] = 1
    errors = []
    for kind, dst, src, sign in reversed(word[:cut]):
        if kind == "ADD":
            errors.append(covector[dst])
            covector[src] += sign * covector[dst]
        else:
            covector[dst] = -covector[dst]
    errors.reverse()
    return sum(map(abs, covector)), errors


def backward_check(word, width, report, bounds, weights, cut_bounds):
    count = 0
    divisor = 1 << report["q"]
    for cut, (kind, dst, src, _) in enumerate(word, 1):
        if kind == "ADD":
            ad, gd = adjoint(word, cut - 1, dst, width)
            ass, gs = adjoint(word, cut - 1, src, width)
            require(len(gd) == count and len(gs) == count, "causal indexing")
            feedback = sum((abs(gd[j]) + abs(gs[j])) * bounds[j] for j in range(count))
            require(weights[count] == ad + ass, "backward source norm")
            require(bounds[count] == SCALE * (ad + ass)
                    + (feedback + divisor - 1) // divisor, "backward causal recurrence")
            count += 1
        _, coefficients = adjoint(word, cut, dst, width)
        require(len(coefficients) == count, "post-gate event count")
        value = sum(abs(coefficients[j]) * bounds[j] for j in range(count))
        require(value == cut_bounds[cut - 1], "backward all-cut bound")
    require(count == len(bounds), "complete ADD coverage")
    require(max(cut_bounds) == report["peak"]["numerator"], "complete cut coverage")
    return {"add_recurrences": count, "changed_rows": len(word),
            "adjoint_traversals": 2 * count + len(word)}


def controls():
    cancel = [("ADD", 0, 1, 1), ("ADD", 0, 1, -1)]
    report, bounds, weights, cuts = causal_bound(cancel, 2, 3)
    require(weights == [2, 3] and bounds == [2 * SCALE, 13 * SCALE // 4], "tiny exact recurrence")
    require(report["peak"]["numerator"] == 21 * SCALE // 4, "tiny all-cut bound")
    backward_check(cancel, 2, report, bounds, weights, cuts)
    rejected = []
    for name, bad in [("omit_prior_error", [2 * SCALE, 3 * SCALE]),
                      ("understate_error", [2 * SCALE, 13 * SCALE // 4 - 1])]:
        try:
            backward_check(cancel, 2, report, bad, weights, cuts)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("accepted mutant: " + name)
    neg = [("ADD", 0, 1, 1), ("NEG", 0, None, 0), ("ADD", 0, 1, 1)]
    r, b, a, c = causal_bound(neg, 2, 3)
    backward_check(neg, 2, r, b, a, c)
    require(adjoint(neg, 3, 0, 2)[1] == [-1, 1], "NEG impulse sign")
    for name, bad in [("alias_source", [("ADD", 0, 0, 1)]),
                      ("unknown_operation", [("SCALE", 0, None, 0)]),
                      ("out_of_range", [("NEG", 2, None, 0)])]:
        try:
            causal_bound(bad, 2, 3)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("accepted invalid word: " + name)
    require(not causal_bound(cancel, 2, 2)[0]["certifies"], "insufficient guard control")
    return {"tiny_bound": "21/4", "tiny_guard": 3, "rejected": rejected,
            "negative_guard_control": 2, "NEG_impulses": [-1, 1]}


def result():
    check_sources()
    word = load_word()
    report, bounds, weights, cuts = causal_bound(word, WIDTH, 13)
    require(report["certifies"], "13-bit forward guard not certified")
    require(report["peak"]["numerator"] < 7029 * SCALE, "announced upper bound")
    return {"schema_version": 1, "claim_type": "scoped proof with exact finite corroboration",
            "forward": report, "backward": backward_check(word, WIDTH, report, bounds, weights, cuts),
            "controls": controls()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    actual = result()
    source_names = ["verify.py", "SOURCES.json", "VERIFY.json", "TASK.json", "README.md", "PROOF.md"]
    actual["package_sha256"] = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                                for name in source_names}
    if args.write_receipt:
        with args.write_receipt.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(actual, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((HERE / "RESULT.json").read_text())
        require(canonical(actual) == canonical(expected), "receipt mismatch")
    print("PASS_Z4_CAUSAL_ERROR_GUARD q=13 upper_C<7029 allowance=8192")
    print("PASS_BACKWARD_CAUSAL_CHECK", "adds=" + str(actual["backward"]["add_recurrences"]),
          "cuts=" + str(actual["backward"]["changed_rows"]))


if __name__ == "__main__":
    main()
