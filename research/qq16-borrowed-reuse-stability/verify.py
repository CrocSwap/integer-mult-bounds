"""Independent QQ16 borrowed-write audit and exact reuse witnesses. Apache-2.0."""

import argparse
import hashlib
import json
import re
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVENTS = 2463
PORTS = 112
LIMIT = 1 << 18
OPCODES = {
    "add",
    "checkpoint",
    "clear",
    "current_map",
    "history_boundary",
    "line",
    "private_begin",
    "private_end",
    "stage",
}
SOURCE_PATHS = {
    "sources/WORD.json",
    "sources/PR2540-PROOF.md",
    "sources/PR2628-PROOF.md",
}
BORROWED = tuple(f"{side}{p}" for side in "XY" for p in range(PORTS))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_bytes(path):
    with path.open("rb") as stream:
        data = stream.read(LIMIT + 1)
    require(len(data) <= LIMIT, "file capacity exceeded")
    return data


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def load_word(package):
    sources = json.loads(read_bytes(package / "SOURCES.json"))
    rows = sources["predecessors"]
    require(len(rows) == 3, "three exact predecessor files required")
    require(
        {r["local_path"] for r in rows} == SOURCE_PATHS, "source inventory mismatch"
    )
    for row in rows:
        data = read_bytes(package / row["local_path"])
        require(
            hashlib.sha256(data).hexdigest() == row["sha256"], "source SHA256 drift"
        )
        blob = b"blob " + str(len(data)).encode("ascii") + b"\0" + data
        require(
            hashlib.sha1(blob).hexdigest() == row["git_blob"], "source Git blob drift"
        )
    return json.loads(read_bytes(package / "sources/WORD.json"))


def valid_field(name):
    require(isinstance(name, str), "field name must be text")
    pattern = r"[XYRZW](?:0|[1-9][0-9]?|10[0-9]|11[01])|C|[FG][0-7]"
    require(re.fullmatch(pattern, name) is not None, "field outside source namespace")
    return name


def write_target(event):
    op = event["op"]
    if op == "add":
        valid_field(event["src"])
        coefficient = event["coefficient"]
        require(
            isinstance(coefficient, str) and len(coefficient) <= 8,
            "coefficient encoding",
        )
        require(abs(Fraction(coefficient)) <= 1, "coefficient outside actual word")
        return valid_field(event["dst"])
    if op in {"clear", "current_map", "line", "stage"}:
        return valid_field(event["field"])
    if op in {"private_begin", "private_end"}:
        fields = event["fields"]
        require(isinstance(fields, list) and 1 <= len(fields) <= 16, "private capacity")
        for name in fields:
            require(valid_field(name) not in BORROWED, "borrowed private lifetime")
    return None


def audit_word(word):
    require(
        isinstance(word, list) and len(word) == EVENTS,
        "complete 2463-event word required",
    )
    writes = {name: [] for name in BORROWED}
    histories = []
    for i, event in enumerate(word):
        require(
            isinstance(event, dict) and event.get("op") in OPCODES, "unsupported opcode"
        )
        if event["op"] == "history_boundary":
            histories.append(i)
        target = write_target(event)
        if target in writes:
            require(
                event["op"] == "line" and target.startswith("Y"),
                "non-native borrowed write",
            )
            require(
                type(event["port"]) is int and event["port"] == int(target[1:]),
                "wrong line label",
            )
            require(
                type(event["sign"]) is int and event["sign"] in {-1, 1}, "line sign"
            )
            writes[target].append((i, event["sign"], event["port"]))
    require(histories == [32], "source temporal boundary mismatch")
    pairs = []
    for p in range(PORTS):
        require(writes[f"X{p}"] == [], "borrowed X must be read-only")
        pair = writes[f"Y{p}"]
        require(
            len(pair) == 2 and [x[1] for x in pair] == [1, -1],
            "missing native inverse pair",
        )
        require(pair[0][0] > histories[0], "borrowed pair before current entry")
        pairs.append([f"Y{p}", pair[0][0], pair[1][0], p])
    return {
        "events": len(word),
        "history_event": 32,
        "read_only_X": PORTS,
        "restored_Y_pairs": PORTS,
        "borrowed_native_writes": 2 * PORTS,
        "borrowed_other_writes": 0,
        "pairs": pairs,
    }


def execute_constant(word, current, bias):
    """Literal full word on the common invariant constant-vector subspace."""
    values = {event["src"]: Fraction(0) for event in word[:32] if event["op"] == "add"}
    private = set()
    for event in word:
        op = event["op"]
        if op == "history_boundary":
            values.update(current)
        elif op == "clear":
            values[event["field"]] = Fraction(0)
        elif op == "add":
            values[event["dst"]] += (
                Fraction(event["coefficient"]) * values[event["src"]]
            )
        elif op == "line":
            name = event["field"]
            values[name] *= 1 + bias
        elif op in {"stage", "current_map"}:
            require(event["field"] in values, "initialized constant native input")
        elif op == "private_begin":
            require(not private, "overlapping private lifetimes")
            private = set(event["fields"])
        elif op == "private_end":
            require(private == set(event["fields"]), "private retirement mismatch")
            for name in private:
                require(values.pop(name) == 0, "private cleanup")
            private = set()
        else:
            require(op == "checkpoint", "literal opcode coverage")
    require(not private, "private lifetime leak")
    return {name: values[name] for name in BORROWED}


def line(vector, sign, bias):
    """Exact Gaussian-rational C or C^-1 on a nonconstant two-point orbit."""
    a, b = vector
    mean = tuple((a[j] + b[j]) / 2 for j in range(2))
    diff = tuple(sign * (a[j] - b[j]) / 2 for j in range(2))
    first = (mean[0] - diff[1], mean[1] + diff[0])
    second = (mean[0] + diff[1], mean[1] - diff[0])
    return tuple(tuple((1 + bias) * x for x in value) for value in (first, second))


def check_fixtures(word):
    equalities = 0
    initial = {name: Fraction((i % 7) - 3, 3) for i, name in enumerate(BORROWED)}
    for bias in (Fraction(0), Fraction(1, 16), Fraction(1, 256)):
        current = initial
        for n in range(1, 18):
            current = execute_constant(word, current, bias)
            for name in BORROWED:
                power = 0 if name.startswith("X") else 2 * n
                require(
                    current[name] == initial[name] * (1 + bias) ** power,
                    "reuse witness mismatch",
                )
                equalities += 1
    vector = ((Fraction(1), Fraction(2)), (Fraction(-3), Fraction(4)))
    for bias in (Fraction(0), Fraction(1, 16), Fraction(1, 256)):
        result = line(line(vector, 1, bias), -1, bias)
        expected = tuple(tuple(x * (1 + bias) ** 2 for x in value) for value in vector)
        require(result == expected, "nonconstant Gaussian native pair")
        equalities += 4
    return equalities


def check_controls(word):
    controls = []
    first = next(i for i, event in enumerate(word) if event["op"] == "line")
    inverse = next(
        i
        for i in range(first + 1, EVENTS)
        if word[i].get("field") == word[first]["field"] and word[i]["op"] == "line"
    )
    mutations = [
        (inverse, {"op": "checkpoint", "name": "omitted_inverse"}),
        (inverse, dict(word[inverse], sign=1)),
        (inverse, dict(word[inverse], port=2)),
        (first, {"op": "clear", "field": "Y1"}),
        (first, {"op": "add", "dst": "X1", "src": "Y1", "coefficient": "1"}),
        (first, dict(word[first], port=True)),
        (first, {"op": "unknown"}),
    ]
    for index, event in mutations:
        mutant = list(word)
        mutant[index] = event
        try:
            audit_word(mutant)
        except ValueError as error:
            controls.append(str(error))
        else:
            raise ValueError("semantic mutation was accepted")
    return len(controls)


def check_precision():
    cases = 0
    for bits in range(9):
        target = Fraction(1, 1 << bits)
        for uses in (1, 2, 3, 7, 16, 32):
            u = target / (4 * uses)
            drift = (1 + u) ** (2 * uses) - 1
            require(drift <= target, "horizon allowance failed")
            cases += 1
    # Bernoulli gives a strict failure without materializing a million-factor power.
    uses = (1 << 20) + 1
    for bits in range(9):
        u = Fraction(1, 1 << (bits + 21))
        require(
            2 * uses * u > Fraction(1, 1 << bits), "fixed local guard failure witness"
        )
        cases += 1
    return cases


def verify(package):
    word = load_word(package)
    result = audit_word(word)
    result["constant_word_equalities_and_gaussian_components"] = check_fixtures(word)
    result["semantic_controls_rejected"] = check_controls(word)
    result["precision_cases"] = check_precision()
    result["source_opcodes"] = dict(sorted(Counter(e["op"] for e in word).items()))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=HERE)
    parser.add_argument(
        "--write", type=Path, help="create an absent external result file"
    )
    args = parser.parse_args()
    result = verify(args.package)
    if args.write is not None:
        with args.write.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    else:
        expected = json.loads(read_bytes(args.package / "RESULT.json"))
        require(canonical(result) == canonical(expected), "typed result receipt drift")
    print(
        "PASS_QQ16_BORROWED_REUSE pairs=112 X_read_only=112 "
        f"equalities={result['constant_word_equalities_and_gaussian_components']} "
        f"controls={result['semantic_controls_rejected']} no_new_kappa"
    )


if __name__ == "__main__":
    main()
