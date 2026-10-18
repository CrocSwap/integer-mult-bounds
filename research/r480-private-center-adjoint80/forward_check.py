"""Independent forward integer-dyadic verification of every omission matrix.

@Scratch-net with substantial OpenAI Codex assistance. Apache-2.0.
Imports neither Fraction, the primary checker nor repository implementation code.
"""
from collections import Counter
import gzip
import hashlib
import json
from math import gcd
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
N, LIVE, PORTS = 712, 704, 112
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def normalize(coefficients, depth):
    if not coefficients:
        return {}, 0
    while depth and all(value % 2 == 0 for value in coefficients.values()):
        coefficients = {column: value // 2 for column, value in coefficients.items()}
        depth -= 1
    return coefficients, depth


def multiply(row, numerator, depth):
    return normalize({column: value * numerator for column, value in row[0].items()}, row[1] + depth)


def sum_rows(left, right):
    depth = max(left[1], right[1])
    result = {column: value << (depth - left[1]) for column, value in left[0].items()}
    for column, value in right[0].items():
        total = result.get(column, 0) + (value << (depth - right[1]))
        if total:
            result[column] = total
        else:
            result.pop(column, None)
    return normalize(result, depth)


def rational(numerator, denominator):
    require(denominator != 0, "zero denominator")
    if denominator < 0:
        numerator, denominator = -numerator, -denominator
    divisor = gcd(numerator, denominator)
    return numerator // divisor, denominator // divisor


def text_number(numerator, depth):
    numerator, denominator = rational(numerator, 1 << depth)
    return str(numerator) if denominator == 1 else str(numerator) + "/" + str(denominator)


def decode(reg):
    kind, index = reg
    require(type(index) is int and 0 <= index < (LIVE if kind == "L" else 8), "register range")
    require(kind in ("L", "C"), "register kind")
    return index if kind == "L" else LIVE + index


def program(events):
    result = []
    for index, event in enumerate(events):
        if event[0] != "scalar":
            continue
        macro = event[1]
        kind, target = macro[0], decode(macro[1])
        source, numerator, denominator = None, 1, 1
        if kind in ("add", "copy"):
            source = decode(macro[2])
            require(source != target, "aliased macro")
        if kind == "add":
            numerator, denominator = rational(macro[3], macro[4])
        elif kind == "scale":
            numerator, denominator = rational(macro[2], macro[3])
        else:
            require(kind in ("copy", "clear"), "unknown macro")
        require(numerator != 0 and denominator & (denominator - 1) == 0, "nondyadic macro")
        result.append((index, kind, target, source, numerator, denominator.bit_length() - 1))
    return result


def forward(ops, omission=None):
    """Output coordinate -> exact row on all 712 arbitrary input columns."""
    rows = [({i: 1}, 0) for i in range(N)]
    for index, kind, target, source, numerator, depth in ops:
        if index == omission:
            continue
        if kind == "clear":
            rows[target] = ({}, 0)
        elif kind == "copy":
            rows[target] = (dict(rows[source][0]), rows[source][1])
        elif kind == "scale":
            rows[target] = multiply(rows[target], numerator, depth)
        else:
            rows[target] = sum_rows(rows[target], multiply(rows[source], numerator, depth))
    return rows


def transpose(rows):
    columns = [{} for _ in range(N)]
    for output, (coefficients, depth) in enumerate(rows):
        for input_, numerator in coefficients.items():
            columns[input_][output] = text_number(numerator, depth)
    return columns


def serialize(columns):
    return [[[output, value] for output, value in sorted(column.items())] for column in columns]


def difference(rows, before):
    return [sum_rows(after, multiply(old, -1, 0)) for after, old in zip(rows, before)]


def certificate_vector(value):
    result = {}
    for index, number in value:
        parts = number.split("/")
        numerator, denominator = rational(int(parts[0]), int(parts[1]) if len(parts) == 2 else 1)
        require(denominator & (denominator - 1) == 0, "certificate coefficient nondyadic")
        require(index not in result and 0 <= index < N and numerator, "certificate vector index")
        result[index] = (numerator, denominator.bit_length() - 1)
    return result


def verify():
    pins = json.loads((HERE / "SOURCE-PINS.json").read_bytes())
    for name, expected in pins["files"].items():
        require(digest((ROOT / name).read_bytes()) == expected, "source pin differs")
    require(digest((HERE / "BASE-SELECTED.json").read_bytes()) == pins["context_sha256"], "context differs")
    with tarfile.open(ROOT / ARCHIVE, "r:gz") as archive:
        raw = archive.extractfile("slots/local/LOCAL-PROGRAMS.json.gz").read()
        payload = gzip.decompress(raw)
        require(digest(payload) == pins["members"]["slots/local/LOCAL-PROGRAMS.json.gz"], "program payload differs")
        programs = json.loads(payload)
    cert = json.loads((HERE / "CERTIFICATE.json").read_bytes())
    require(set(cert["programs"]) == set(programs) == {"forward", "backward"}, "orientation differs")
    sites_total = 0
    for direction in ("forward", "backward"):
        ops = program(programs[direction])
        baseline = forward(ops)
        columns = transpose(baseline)
        wanted = [{i: "1"} if i < LIVE else {} for i in range(N)]
        for i in range(PORTS):
            if direction == "forward":
                wanted[i][PORTS + i] = "1"
            else:
                wanted[PORTS + i][i] = "-1"
        require(columns == wanted, "independent baseline endpoint differs")
        record = cert["programs"][direction]
        require(digest(canonical(serialize(columns))) == record["matrix_sha256"], "baseline matrix digest differs")
        site_set = {(index, kind, target - LIVE) for index, kind, target, _, _, _ in ops
                    if target >= LIVE and kind in ("clear", "copy")}
        recorded = {(f["event_index"], f["operation"], f["center"]) for f in record["faults"]}
        require(site_set == recorded and len(recorded) == len(record["faults"]), "omission coverage differs")
        classes = Counter()
        for fault in record["faults"]:
            index = fault["event_index"]
            actual = transpose(difference(forward(ops, index), baseline))
            nonzero, ordinary = any(actual), any(actual[:LIVE])
            classification = "redundant" if not nonzero else "ordinary_input_visible" if ordinary else "private_input_only"
            require(fault["classification"] == classification and fault["ordinary_inputs_detect"] == ordinary,
                    "fault classification differs")
            require(fault["defect_rank"] == int(nonzero), "fault rank differs")
            require(digest(canonical(serialize(actual))) == fault["defect_sha256"], "fault matrix digest differs")
            u, v = certificate_vector(fault["response"]), certificate_vector(fault["sensitivity"])
            factored = [{} for _ in range(N)]
            for input_, (vn, vd) in v.items():
                for output, (un, ud) in u.items():
                    factored[input_][output] = text_number(vn * un, vd + ud)
            require(actual == factored, "independent outer product differs")
            if nonzero:
                witness = fault["witness"]
                require(witness is not None and
                        [[output, value] for output, value in sorted(actual[witness["input"]].items())] ==
                        witness["output_difference"], "independent witness differs")
            else:
                require(fault["witness"] is None, "redundant site has a witness")
            classes[classification] += 1
        require(dict(sorted(classes.items())) == record["classification"] and
                record["fault_sites"] == len(site_set), "class census differs")
        sites_total += len(site_set)
    require(sites_total == 40, "total coverage differs")
    return sites_total


if __name__ == "__main__":
    verify()
    print("PASS_R480_PRIVATE_CENTER_FORWARD coordinates=712 omissions=40 exact_matrices=42 no_new_kappa")
