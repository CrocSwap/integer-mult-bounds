"""Source-bound forward elimination for the complete PR5221 replay."""

import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = "research/quinary-resonant-disjointness-repair/"
INPUTS = (
    SOURCE + "verify.py",
    SOURCE + "independent.py",
    SOURCE + "RESULT.json",
    SOURCE + "SOURCES.json",
    "research/boolean-disjointness-repair/PROOF.txt",
    "research/ternary-disjointness-repair/PROOF.md",
)
MAX_BYTES = 2**20
MAX_DIMENSION = 256


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_bounded(path):
    with path.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    require(len(data) <= MAX_BYTES, "source too large")
    return data


def forward_rank(matrix, p=5):
    """Return F5 rank without modifying a bounded rectangular integer matrix."""
    require(type(p) is int and p == 5, "coefficient field must be F5")
    require(isinstance(matrix, (list, tuple)), "matrix must be a sequence")
    rows = len(matrix)
    require(rows <= MAX_DIMENSION, "too many rows")
    require(all(isinstance(row, (list, tuple)) for row in matrix), "invalid row")
    cols = len(matrix[0]) if rows else 0
    require(cols <= MAX_DIMENSION, "too many columns")
    require(all(len(row) == cols for row in matrix), "ragged matrix")
    require(
        all(type(x) is int and x.bit_length() <= 64 for row in matrix for x in row),
        "entries must be bounded integers",
    )
    a = [[x % p for x in row] for row in matrix]
    rank = 0
    for col in range(cols):
        pivot = next((i for i in range(rank, rows) if a[i][col]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        inverse = pow(a[rank][col], -1, p)
        require(a[rank][col] * inverse % p == 1, "pivot inverse")
        a[rank][col:] = [x * inverse % p for x in a[rank][col:]]
        tail = a[rank][col + 1 :]
        for i in range(rank + 1, rows):
            q = a[i][col]
            if q:
                a[i][col] = 0
                a[i][col + 1 :] = [
                    (x - q * y) % p for x, y in zip(a[i][col + 1 :], tail)
                ]
        rank += 1
        if rank == rows:
            break
    return rank


def authenticate():
    manifest_bytes = read_bounded(PACKAGE / "SOURCES.json")
    manifest = json.loads(manifest_bytes)
    rows = [row for row in manifest["files"] if row["usage"] == "input"]
    require(len(rows) == len(INPUTS), "source inventory size")
    require({row["path"] for row in rows} == set(INPUTS), "source inventory")
    payloads = {}
    for row in rows:
        path = row["path"]
        data = read_bounded(ROOT / path)
        check_digest(data, row["sha256"])
        payloads[path] = data
    return payloads


def check_digest(data, expected):
    require(hashlib.sha256(data).hexdigest() == expected, "source bytes changed")


def primary_text(payloads, mode):
    require(mode in ("original", "adapted"), "unknown replay mode")
    source = payloads[SOURCE + "verify.py"].decode("utf-8")
    needle = "def rank(a,p=5):"
    require(source.count(needle) == 1, "rank definition anchor")
    if mode == "adapted":
        source = source.replace(needle, "def frozen_rank(a,p=5):", 1)
    return source


def run_complete(mode, observe=False):
    """Execute both full frozen commands and return their exact combined stdout."""
    payloads = authenticate()
    source = primary_text(payloads, mode)
    records = []
    namespace = {"__name__": "__main__", "__file__": str(ROOT / INPUTS[0])}

    def checked_rank(matrix, p=5):
        before = [list(row) for row in matrix]
        got = forward_rank(matrix, p)
        expected = namespace["frozen_rank"](matrix, p)
        require(got == expected, "reached rank disagreement")
        require(matrix == before, "reached rank input mutation")
        records.append((len(matrix), len(matrix[0]) if matrix else 0, got))
        return got

    namespace["rank"] = checked_rank if observe else forward_rank
    require(not observe or mode == "adapted", "observation requires adapted mode")
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        exec(compile(source, str(ROOT / INPUTS[0]), "exec"), namespace)
        independent = payloads[INPUTS[1]].decode("utf-8")
        second = {"__name__": "__main__", "__file__": str(ROOT / INPUTS[1])}
        exec(compile(independent, str(ROOT / INPUTS[1]), "exec"), second)
    text = output.getvalue()
    require(len(text) <= MAX_BYTES, "replay output too large")
    return text, records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("original", "adapted"), required=True)
    args = parser.parse_args()
    output, records = run_complete(args.mode)
    require(not records, "unexpected observation")
    print(output, end="")


if __name__ == "__main__":
    main()
