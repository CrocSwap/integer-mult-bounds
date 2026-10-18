"""Deterministic bounded modular certificate of the #741 backward scalar map.

Ryan Haines, with substantial OpenAI Codex assistance. Apache-2.0.
No constructor, native verifier, Fraction, or external algebra library imported.
"""

import argparse
import copy
import gzip
import hashlib
import json
from math import gcd, prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = "research/complex-sw4-frame8-validation/platforms/linux/local/"
BASE = "7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261"
NATIVE, TOTAL = 728, 736


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def register(pair):
    tag, index = pair
    need((tag == "L" and 0 <= index < NATIVE) or (tag == "C" and 0 <= index < 8),
         "invalid register")
    return index if tag == "L" else NATIVE + index


def normalized(n, e):
    if not n:
        return 0, 0
    zeros = min(e, (n & -n).bit_length() - 1)
    return n >> zeros, e - zeros


def addition(a, b):
    e = max(a[1], b[1])
    return normalized((a[0] << (e - a[1])) + (b[0] << (e - b[1])), e)


def coefficient(op):
    numerator, denominator = op[3:5] if op[0] == "add" else op[2:4]
    need(numerator and denominator, "zero coefficient/denominator")
    if denominator < 0:
        numerator, denominator = -numerator, -denominator
    common = gcd(abs(numerator), denominator)
    numerator, denominator = numerator // common, denominator // common
    need(denominator & (denominator - 1) == 0, "non-dyadic denominator")
    return numerator, denominator


def scalar_ops(events):
    return [e[1] for e in events if e[0] == "scalar"]


def height_bound(ops):
    """Bound each endpoint row norm and denominator, without matrix entries."""
    norms, denominators = [(1, 0)] * TOTAL, [0] * TOTAL
    for op in ops:
        tag, target = op[0], register(op[1])
        if tag == "clear":
            norms[target], denominators[target] = (0, 0), 0
        elif tag == "copy":
            source = register(op[2])
            norms[target], denominators[target] = norms[source], denominators[source]
        else:
            need(tag in ("add", "scale"), "unknown scalar operation")
            n, d = coefficient(op)
            source = register(op[2]) if tag == "add" else target
            if tag == "add":
                need(source != target, "aliased scalar addition")
            e = d.bit_length() - 1
            p, k = norms[source]
            scaled = normalized(p * abs(n), k + e)
            numerator_twos = (abs(n) & -abs(n)).bit_length() - 1
            row_denominator = max(0, denominators[source] + e - numerator_twos)
            if tag == "add":
                norms[target] = addition(norms[target], scaled)
                denominators[target] = max(denominators[target], row_denominator)
            else:
                norms[target], denominators[target] = scaled, row_denominator
    max_denominator = max(denominators)
    # Every desired entry is 0 or +/-1, so this bounds every residual entry.
    ceil_norm = max((p + (1 << e) - 1) >> e for p, e in norms)
    residual_bound = (ceil_norm + 1) << max_denominator
    return {"denominator_exponent": max_denominator,
            "endpoint_l1_ceiling": str(ceil_norm),
            "integer_residual_bound": str(residual_bound),
            "row_denominator_sha256": digest(denominators),
            "row_envelope_sha256": digest(norms)}


def moduli_for(bound):
    result, product, k = [], 1, 5  # Seed 80 chooses Fermat index 3 + (80 % 3).
    while product <= 2 * bound:
        modulus = (1 << (1 << k)) + 1
        result.append(modulus)
        product *= modulus
        k += 1
    return result


def check_moduli(moduli, bound):
    need(moduli and all(m > 2 and m % 2 for m in moduli), "non-odd reconstruction modulus")
    need(all(gcd(a, b) == 1 for i, a in enumerate(moduli) for b in moduli[:i]),
         "moduli are not pairwise coprime")
    need(prod(moduli) > 2 * bound, "insufficient modulus product for exact reconstruction")


def replay_modulo(ops, modulus):
    rows = [{r: 1} for r in range(TOTAL)]
    inverse_cache = {}
    for op in ops:
        tag, target = op[0], register(op[1])
        if tag == "clear":
            rows[target] = {}
        elif tag == "copy":
            rows[target] = dict(rows[register(op[2])])
        else:
            n, d = coefficient(op)
            if d not in inverse_cache:
                inverse_cache[d] = pow(d, -1, modulus)
            q = (n * inverse_cache[d]) % modulus
            if tag == "scale":
                rows[target] = {c: z for c, a in rows[target].items()
                                if (z := a * q % modulus)}
            else:
                need(tag == "add", "unknown modular operation")
                source = register(op[2])
                need(source != target, "aliased modular addition")
                for col, value in rows[source].items():
                    z = (rows[target].get(col, 0) + q * value) % modulus
                    if z:
                        rows[target][col] = z
                    else:
                        rows[target].pop(col, None)
    for r in range(TOTAL):
        expected = {r: 1} if r < NATIVE else {}
        if r < 112:
            expected[r + 112] = modulus - 1
        need(rows[r] == expected, f"modular endpoint mismatch: register {r}")
    return digest([sorted(r.items()) for r in rows])


def certify(ops, moduli=None):
    bound = height_bound(ops)
    limit = int(bound["integer_residual_bound"])
    moduli = moduli_for(limit) if moduli is None else moduli
    check_moduli(moduli, limit)
    residues = [replay_modulo(ops, m) for m in moduli]
    return {"bound": bound, "moduli": [str(m) for m in moduli],
            "modulus_product": str(prod(moduli)), "residue_matrix_sha256": residues,
            "scalar_macros": len(ops), "arbitrary_input_columns": TOTAL,
            "native_columns": NATIVE, "private_center_columns": 8}


def reject(call, name):
    try:
        call()
    except ValueError:
        return name
    raise ValueError("negative control accepted: " + name)


def controls(ops, receipt):
    moduli = [int(m) for m in receipt["moduli"]]
    def append(q):
        return ops + [["add", ["L", 0], ["L", 1], q, 1]]
    result = [reject(lambda: certify(ops, [moduli[0]]), "insufficient_product"),
              reject(lambda: certify(ops, moduli + [moduli[0]]), "duplicate_modulus"),
              reject(lambda: certify(append(1), moduli), "unit_endpoint_error")]
    first_blind = append(moduli[0])
    replay_modulo(first_blind, moduli[0])
    result.append(reject(lambda: replay_modulo(first_blind, moduli[1]),
                         "first_modulus_blind_error_caught_by_next"))
    all_blind = append(prod(moduli))
    for m in moduli:
        replay_modulo(all_blind, m)
    result.append(reject(lambda: certify(all_blind, moduli),
                         "all_moduli_blind_error_caught_by_height"))
    bad = copy.deepcopy(ops)
    first_clear = next(i for i, op in enumerate(bad) if op == ["clear", ["C", 0]])
    bad.pop(first_clear)
    result.append(reject(lambda: certify(bad, moduli), "dirty_center_initial_clear"))
    result.append(reject(lambda: certify(ops + [["add", ["L", 0], ["L", 1], 1, 3]], moduli),
                         "nondyadic_denominator"))
    return result


def build():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    need(pins["base_commit"] == BASE, "base pin mismatch")
    loaded = {}
    for name, expected in pins["payload_sha256"].items():
        raw = (ROOT / name).read_bytes()
        if name.endswith(".gz"):
            raw = gzip.decompress(raw)
        need(hashlib.sha256(raw).hexdigest() == expected, "source payload changed: " + name)
        loaded[name] = json.loads(raw)
    native = loaded[PREFIX + "CANONICAL-WORD.json.gz"]
    need((native["v"], native["R"], native["h"]) == (112, 504, 9), "unexpected selected dimensions")
    events = loaded[PREFIX + "LOCAL-PROGRAMS.json.gz"]["backward"]
    ops = scalar_ops(events)
    receipt = certify(ops)
    receipt.update(schema="sw4-bounded-modular-endpoint/1", base_commit=BASE,
                   assignment_seed=80, orientation="backward", program_sha256=digest(events),
                   negative_controls=controls(ops, receipt))
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    result = build()
    if args.write:
        need(not args.write.exists(), "refusing to replace receipt")
        args.write.write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(result == json.loads((HERE / "EXPECTED.json").read_text()), "committed receipt mismatch")
    print(f"PASS_SW4_EXACT_MODULAR_ENDPOINT columns={TOTAL} moduli={len(result['moduli'])} "
          f"controls={len(result['negative_controls'])}")


if __name__ == "__main__":
    main()
