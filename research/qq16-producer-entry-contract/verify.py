#!/usr/bin/env python3
"""Source-bound exact-producer entry envelopes. Nick Petalas, Apache-2.0."""

import argparse
import gzip
import hashlib
import io
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A = (0, 7, 20, 27, 36, 46, 57, 111)
T = (21, 37, 47, 76, 81, 87, 92, 110)
U = tuple(p for p in range(112) if p not in A + T)
INPUTS = (
    "research/joint-query/certificate.json.gz",
    "research/joint-query/evidence/BRIDGE-REVIEW.md",
    "research/joint-query/evidence/CONSERVED-QQ16.md",
    "research/joint-query/evidence/JOINT-QUERY-TRANSFER.md",
    "research/qq16-finite-dyadic-format/README.md",
    "research/qq16-line-normalized-decoder/PROOF.md",
)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path, limit):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    need(len(raw) <= limit, "oversized JSON: " + str(path))
    return json.loads(raw, object_pairs_hook=unique_object)


def sources():
    pins = read_json(HERE / "SOURCES.json", 65536)
    items = [item for item in pins["files"] if item["usage"] == "input"]
    need(tuple(sorted(item["path"] for item in items)) == INPUTS, "input set")
    packet = None
    for item in items:
        with (ROOT / item["path"]).open("rb") as stream:
            raw = stream.read(1048577)
        need(len(raw) <= 1048576, "oversized source")
        need(hashlib.sha256(raw).hexdigest() == item["sha256"], "source hash")
        if item["path"].endswith(".gz"):
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
                payload = stream.read(12582913)
            need(len(payload) <= 12582912, "oversized decompressed source")
            packet = json.loads(payload, object_pairs_hook=unique_object)
    need(packet is not None, "missing producer certificate")
    return packet


def geometry(packet):
    need(tuple(packet["A_ports"]) == A and tuple(packet["T_ports"]) == T
         and tuple(packet["U_ports"]) == U, "selected port partition")
    need(len(packet["R_rows"]) == 8 and len(packet["K_rows"]) == 112, "geometry shape")
    r = [[Fraction(row.get(str(p), 0)) for p in range(112)]
         for row in packet["R_rows"]]
    k = [[Fraction(row.get(str(j), 0)) for j in range(8)]
         for row in packet["K_rows"]]
    need(all(c in (-1, 0, 1) for row in r for c in row), "R alphabet")
    need(all(k[p][j] == r[j][p] / 4 for p in range(112) for j in range(8)), "K=R*/4")
    need(all(sum(abs(c) for c in row) == 56 for row in r), "R row weight")
    need(all(sum(abs(c) for c in row) == 1 for row in k), "K row weight")
    for subset, mass in ((A, 4), (T, 4), (U, 48)):
        need(all(sum(r[i][p] * r[j][p] for p in subset) == mass * (i == j)
                 for i in range(8) for j in range(8)), "selected Gram identity")
    return r, k


@dataclass(frozen=True)
class Envelope:
    norm: Fraction
    debt: int


def denominator_bits(value):
    denominator = value.denominator
    need(denominator & (denominator - 1) == 0, "non-dyadic coefficient")
    return denominator.bit_length() - 1


def mix(coefficients, values):
    need(len(coefficients) == len(values) <= 112, "linear combination shape")
    active = [(c, v) for c, v in zip(coefficients, values, strict=True) if c]
    if not active:
        return Envelope(Fraction(0), 0)
    return Envelope(sum(abs(c) * v.norm for c, v in active),
                    max(v.debt + denominator_bits(c) for c, v in active))


def query(r, values, subset):
    # Each routed summand preserves both norm and component grid.
    return [mix([row[p] for p in subset], [values[p] for p in subset]) for row in r]


def inject(k, values, subset):
    return [mix(row, values) if p in subset else Envelope(Fraction(0), 0)
            for p, row in enumerate(k)]


def producer(r, k):
    one = Envelope(Fraction(1), 0)
    entry = [one] * 112
    full = query(r, entry, tuple(range(112)))
    old_t = inject(k, query(r, entry, T), A)
    kfull = inject(k, full, U + T)
    x1 = [mix((1, -1), (one, kfull[p])) if p in U
          else old_t[p] if p in A else kfull[p] for p in range(112)]
    y1 = [mix((1, 1), (one, x1[p])) if p in U
          else mix((1, 1, -1), (one, one, x1[p])) for p in range(112)]
    future = inject(k, query(r, y1, U + T), A)
    u = [mix((1, 1), (y1[p], future[p])) for p in range(112)]
    a = query(r, x1, T)
    b = query(r, u, tuple(range(112)))
    ku, pa, pb = inject(k, a, U), inject(k, a, T), inject(k, b, T)
    y2 = [mix((1, 1), (y1[p], ku[p])) if p in U else u[p] if p in A
          else mix((1, -1, -11), (u[p], pb[p], pa[p])) for p in range(112)]
    # X1_U-Y1_U=-Yentry_U, and selected pair sums equal their entry sums.
    x2 = [one if p in U else mix((1, 1, -1), (one, one, y2[p]))
          for p in range(112)]
    return {"x1": x1, "y1": y1, "u": u, "a": a, "b": b, "x2": x2, "y2": y2}


def format_parameters(depth, entry_fraction, entry_exponent, target_bits):
    for value in (depth, entry_fraction, entry_exponent, target_bits):
        need(type(value) is int and 0 <= value <= 4096, "parameter domain")
    need(depth >= 1, "positive tensor depth")
    # The quantified proof has no 4096 cap. This calculator bounds its inputs.
    q0 = entry_fraction + (depth + 1) // 2 + 6 + 9 * depth
    decoder_b = target_bits + 15
    reserve = decoder_b + 22 + (depth - 1).bit_length() + 73 * depth // 2
    qmax = q0 + 3 * reserve + 6
    exponent = entry_exponent + 15
    return {"Q0": q0, "B_over_H": 17628, "decoder_b": decoder_b,
            "E": exponent, "k": reserve, "Qmax": qmax, "W": qmax + exponent + 20}


def result():
    r, k = geometry(sources())
    rows = producer(r, k)
    encoded = {name: [{"norm_over_H": str(v.norm), "fractional_debt": v.debt}
                      for v in values] for name, values in rows.items()}
    maximum = max(v.norm for name in ("x2", "y2") for v in rows[name])
    debt = max(v.debt for name in ("x2", "y2") for v in rows[name])
    need(maximum == 17628 and debt == 6, "producer envelope changed")
    need(2 ** 14 < maximum < 2 ** 15, "strict original-input error margin")
    examples = [format_parameters(d, 64, 0, 64) for d in (1, 2, 3, 8)]
    return {"status": "PASS_QQ16_PRODUCER_ENTRY_CONTRACT", "rows": encoded,
            "maximum_norm_over_H": str(maximum), "logical_fractional_debt": debt,
            "physical_entry_grid_formula": "f+ceil(lambda/2)+6+9*lambda",
            "examples_depth_1_2_3_8": examples,
            "scope": "Exact producer endpoints only; no physical invoice or new kappa"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="create an absent receipt")
    args = parser.parse_args()
    actual = result()
    path = HERE / "RESULT.json"
    if args.write:
        with path.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(actual, indent=2, sort_keys=True) + "\n")
    else:
        expected = read_json(path, 131072)
        need(json.dumps(expected, sort_keys=True) == json.dumps(actual, sort_keys=True),
             "complete typed receipt mismatch")
    print(actual["status"], "B=17628H grid=f+ceil(lambda/2)+6+9lambda W_example=532 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit("FAIL_QQ16_PRODUCER_ENTRY_CONTRACT: " + str(error)) from error
