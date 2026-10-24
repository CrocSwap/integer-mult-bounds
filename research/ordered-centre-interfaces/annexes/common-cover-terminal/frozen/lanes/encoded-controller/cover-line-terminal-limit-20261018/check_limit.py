"""Check the cover-only line-cut terminal rank."""

from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / "bridge-access-20261017/cycle-cover-response-20261018/CYCLE-COVER-PROGRAMS.json"
PIN = "759f85673b0fda9ba4ff7312c18c80f8a8b72a3ad0a7b1192a8d08571d0095da"


def need(condition, label):
    if not condition:
        raise ValueError(label)


def parity(value):
    return value.bit_count() & 1


def act(columns, value):
    out = 0
    for i, column in enumerate(columns):
        if value >> i & 1:
            out ^= column
    return out


def transpose(columns):
    n = len(columns)
    return [sum(((columns[j] >> i) & 1) << j for j in range(n)) for i in range(n)]


def rank(columns):
    pivots = {}
    for value in columns:
        while value:
            i = value.bit_length() - 1
            if i in pivots:
                value ^= pivots[i]
            else:
                pivots[i] = value
                break
    return len(pivots)


def orthogonal_matrices(n, prefix=()):
    if len(prefix) == n:
        yield prefix
        return
    for vector in range(1, 1 << n):
        if parity(vector) and all(not parity(vector & other) for other in prefix):
            yield from orthogonal_matrices(n, prefix + (vector,))


def check_line(columns, q):
    v = act(columns, q)
    need(not parity(q & v), "The first target line is orthogonal to q")
    w = act(transpose(columns), q)
    need(parity(q) == parity(w) == 1 and not parity(q & w), "Two odd orthogonal terminal lines")
    block = [(q if q >> i & 1 else 0) ^ (w if w >> i & 1 else 0)
             for i in range(len(columns))]
    need(rank(block) == 2, "Exact terminal rank")


def main():
    need(sha256(SOURCE.read_bytes()).hexdigest() == PIN, "Actual cycle pin")
    tests = []
    for n in (3, 5):
        matrices = line_cases = phase_cases = 0
        for columns in orthogonal_matrices(n):
            matrices += 1
            inverse = transpose(columns)
            need([act(columns, v) for v in inverse] == [1 << i for i in range(n)], "Exact inverse")
            delta = sum((((row.bit_count() - 1) // 2) & 1) << i
                        for i, row in enumerate(inverse))
            for character in range(1 << n):
                need((act(inverse, character).bit_count() - character.bit_count()
                      - 2 * parity(delta & character)) % 4 == 0, "FULL phase is a translation")
                phase_cases += 1
            for q in range(1, 1 << n):
                if parity(q) and not parity(q & act(columns, q)):
                    check_line(columns, q)
                    line_cases += 1
        tests.append({"dimension": n, "orthogonal_matrices": matrices,
                      "line_cases": line_cases, "complete_character_checks": phase_cases})
    source = json.loads(SOURCE.read_bytes())
    for record in source["records"]:
        need(act(record["L_columns"], record["q"]) == record["v0"], "Actual initial line cut")
        check_line(record["L_columns"], record["q"])
    receipt = {
        "status": "PASS_COVER_ONLY_TERMINAL_RANK",
        "proof_sha256": sha256((HERE / "LIMIT.md").read_bytes()).hexdigest(),
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_sha256": PIN, "small_dimension_checks": tests,
        "actual_port_checks": len(source["records"]),
        "scope": "A standalone one-field Clifford terminal for a port-diagonal orthogonal cover-only response with the stated first line cut. Fused earlier operations and broader response or circuit classes remain outside the claim.",
    }
    (HERE / "CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
