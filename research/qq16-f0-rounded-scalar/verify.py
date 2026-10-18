"""A correctly rounded F0 *scalar projection* counterexample.

Arham Tahir, with substantial OpenAI Codex assistance. Apache-2.0.
Native non-scalar events are explicitly omitted, not certified as identities.
"""

import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
PRECISIONS = (8, 24, 53, 113)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def unique(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, "Duplicate JSON key")
        out[key] = value
    return out


def read_json(path, limit=1_000_000):
    raw = path.read_bytes()
    need(len(raw) <= limit, "Oversized JSON")
    return json.loads(raw, object_pairs_hook=unique)


def load_events():
    pins = [row for row in read_json(PACKAGE / "SOURCES.json")["files"]
            if row["usage"] == "input"]
    need(len(pins) == 1, "Exactly one scientific input")
    pin = pins[0]
    need(pin["path"] == "research/joint-query/certificate.json.gz", "Source path")
    raw = (ROOT / pin["path"]).read_bytes()
    need(len(raw) < 1_000_000 and sha256(raw).hexdigest() == pin["sha256"],
         "Source hash mismatch")
    with gzip.GzipFile(fileobj=BytesIO(raw)) as stream:
        payload = stream.read(12_000_001)
    need(len(payload) <= 12_000_000, "Oversized source payload")
    need(sha256(payload).hexdigest() == pin["payload_sha256"], "Payload hash mismatch")
    packet = json.loads(payload, object_pairs_hook=unique)
    outer = packet["programs"]["F_0"]
    need(outer[0][:3] == ["retained_core", "forward", 0], "F0 core binding")
    events = list(packet["core_words"]["forward"])
    need(Counter(e[0] for e in outer[1:]) == {"cover_sweep": 5, "private_sweep": 8},
         "F0 wrapper shape")
    for sweep in outer[1:]:
        events.extend(sweep[2])
    counts = Counter(e[0] for e in events)
    need(counts == {"scalar": 21025, "climb": 3486, "adapter": 1090,
                    "residual_adapter": 480, "phase": 10, "native_line": 8},
         "Full projection event inventory")
    return events, dict(sorted(counts.items()))


def register(token):
    kind, at = token
    need(kind in ("L", "C") and type(at) is int, "Register kind")
    need(0 <= at < (704 if kind == "L" else 8), "Register range")
    return at + (704 if kind == "C" else 0)


def precision(value):
    """Minimum binary significand length of a nonzero dyadic rational."""
    n, d = abs(value.numerator), value.denominator
    need(d & (d - 1) == 0, "Non-dyadic state")
    return n.bit_length() - (n & -n).bit_length() + 1 if n else 0


def rn(value, bits):
    """Exact nearest-even rounding, with an unbounded binary exponent."""
    need(type(bits) is int and 2 <= bits <= 256, "Precision range")
    precision(value)
    if not value:
        return value
    sign = -1 if value < 0 else 1
    x = abs(value)
    exponent = x.numerator.bit_length() - x.denominator.bit_length()
    if x < Q(2) ** exponent:
        exponent -= 1
    quantum = Q(2) ** (exponent - bits + 1)
    scaled = x / quantum
    n, r = divmod(scaled.numerator, scaled.denominator)
    if 2 * r > scaled.denominator or (2 * r == scaled.denominator and n % 2):
        n += 1
    return sign * n * quantum


def initial(bits, dirty=True, signal=Q(1)):
    state = [Q(0)] * 712
    state[112] = signal
    state[224] = signal * (2 ** (bits + 12)) if dirty else Q(0)
    return state


def execute(events, entry, bits=None, binary64=False):
    state = list(map(float, entry)) if binary64 else entry.copy()
    faults = []
    trace = sha256()
    peak_precision = 0
    peak_at = None
    for index, event in enumerate(events):
        if event[0] != "scalar":
            need(event[0] in ("climb", "adapter", "residual_adapter", "phase", "native_line"),
                 "Unknown omitted non-scalar event")
            continue
        gate = event[1]
        at = register(gate[1])
        before = Q(state[at])
        op = gate[0]
        if op == "clear":
            need(at >= 704, "Only owned private CLEAR")
            exact = Q(0)
            actual = 0.0 if binary64 else exact
        elif op == "scale":
            coefficient = Q(gate[2], gate[3])
            need(abs(coefficient.numerator) & (abs(coefficient.numerator) - 1) == 0,
                 "SCALE power of two")
            exact = before * coefficient
            actual = state[at] * float(coefficient) if binary64 else exact
        else:
            need(op == "add", "Known scalar gate")
            source = register(gate[2])
            need(source != at, "Distinct ADD operands")
            coefficient = Q(gate[3], gate[4])
            exact = before + Q(state[source]) * coefficient
            actual = (state[at] + state[source] * float(coefficient)) if binary64 else exact
        if binary64:
            # Separate hardware multiplication and ADD must match the favorable
            # single-round completed ADD model at EVERY instruction, not just exit.
            need(Q(actual) == rn(exact, 53), "Binary64/model cut mismatch")
        elif bits is not None:
            actual = rn(exact, bits)
        count = precision(exact)
        if count > peak_precision:
            peak_precision, peak_at = count, index
        if Q(actual) != exact:
            faults.append({"event": index, "gate": gate, "before": str(before),
                           "exact": str(exact), "rounded": str(Q(actual)),
                           "error": str(Q(actual) - exact)})
        state[at] = actual
        trace.update(encoded([index, at, str(Q(actual))]) + b"\n")
    result = list(map(Q, state))
    return result, {"faults": faults, "trace_sha256": trace.hexdigest(),
                    "peak_exact_operation_precision": peak_precision,
                    "first_peak_event": peak_at,
                    "endpoint_sha256": sha256(encoded(list(map(str, result)))).hexdigest()}


def witness(events, bits):
    entry = initial(bits)
    ideal, exact_info = execute(events, entry)
    need(ideal == entry, "Exact witness endpoint, including all helpers/private fields")
    actual, rounded_info = execute(events, entry, bits)
    delta = [[i, str(a - b)] for i, (a, b) in enumerate(zip(actual, ideal)) if a != b]
    need(delta == [[112, "-1"], [114, "-1/2"], [137, "-1/2"],
                   [190, "-1/2"], [211, "-1/2"]], "Five-field data error")
    need(actual[224:704] == entry[224:704], "Every borrowed helper restores")
    need(actual[704:] == [0] * 8, "Every private output is zero")
    need([f["event"] for f in rounded_info["faults"]] == [3887, 4060],
         "Exactly two actual rounding sites")
    need(all(f["error"] == "-1/2" for f in rounded_info["faults"]), "Fault values")
    wide, wide_info = execute(events, entry, bits + 12)
    need(wide == ideal and not wide_info["faults"], "Wider exact arithmetic escape")
    clean, clean_info = execute(events, initial(bits, dirty=False), bits)
    need(clean == initial(bits, dirty=False) and not clean_info["faults"],
         "Zero-dirty control")
    need(exact_info["peak_exact_operation_precision"] == bits + 12,
         "Witness-specific exact precision")
    binary64_info = None
    if bits == 53:
        machine, binary64_info = execute(events, entry, binary64=True)
        need(machine == actual, "Native binary64 complete endpoint")
    return {"precision": bits, "dirty_exponent": bits + 12, "difference": delta,
            "ideal": exact_info, "rounded": rounded_info,
            "wide": wide_info, "clean": clean_info, "binary64": binary64_info}


def compute():
    need(sys.float_info.mant_dig == 53 and sys.float_info.radix == 2,
         "Native comparison requires binary64 Python float")
    events, inventory = load_events()
    return {"schema_version": 1, "scope": "F0 common-chart scalar projection only",
            "event_count": len(events), "inventory": inventory,
            "projection_sha256": sha256(encoded(events)).hexdigest(),
            "cases": [witness(events, bits) for bits in PRECISIONS]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Create an absent RESULT.json")
    args = parser.parse_args()
    result = compute()
    path = PACKAGE / "RESULT.json"
    if args.write:
        with path.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    else:
        need(read_json(path) == result, "Receipt mismatch")
    print("PASS_QQ16_F0_ROUNDED_SCALAR cases=4 rounding_sites=2 data_errors=5 "
          "restored_helpers=480 native_binding=UNRUN no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print("FAIL_QQ16_F0_ROUNDED_SCALAR: " + str(error), file=sys.stderr)
        raise SystemExit(1) from error
