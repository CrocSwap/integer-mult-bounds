"""Reproduce stale certification, then exercise the frozen admission boundary."""
from copy import deepcopy
from dataclasses import FrozenInstanceError
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import admission as a


def need(condition, label):
    if not condition:
        raise ValueError(label)


def expected_coefficients(left, right, digit_bits, size):
    """Independent schoolbook convolution, only used as a test oracle."""
    radix = 1 << digit_bits
    ld, rd = [], []
    while left:
        left, r = divmod(left, radix)
        ld.append(r)
    while right:
        right, r = divmod(right, radix)
        rd.append(r)
    out = [0] * size
    for i, x in enumerate(ld):
        for j, y in enumerate(rd):
            out[i + j] += x * y
    return out


def verify():
    original = a._SOURCE["pipeline"]
    interval = a._SOURCE["intervals"].Interval
    line = a.new_line(5, 8, 5)
    certificate = original.uniform_certificate([line], 4)
    baseline, _ = original.multiply(1, 1, [line], 4)
    need(baseline == 1, "original baseline")
    good = deepcopy(line)
    prepared = a.prepare([line], 4)
    fingerprint = prepared.fingerprint
    line.compression = [[x * 2 for x in row] for row in line.compression]
    stale = original.uniform_certificate([line], 4)
    wrong, record = original.multiply(1, 1, [line], 4, input_bits=4)
    need(stale == certificate and wrong == 8 and record["coefficients"] == [8, 0, 0, 0, 0]
         and F(*record["error_radius"]) < F(1, 2), "exact original-code stale-cache witness")
    rejected = []

    def reject(label, action, fragment):
        try:
            action()
        except (ValueError, FrozenInstanceError) as exc:
            need(fragment in str(exc), "wrong rejection for " + label + ": " + str(exc))
            rejected.append(label)
        else:
            raise ValueError("unexpected admission: " + label)

    reject("doubled compression", lambda: a.prepare([line]), "operator certificate")
    need(prepared.multiply(1, 1)[0] == 1, "snapshot isolates doubled compression")
    line.expansion[0][0] = interval.rational(123, line.bits)
    line.selector[:] = [0] * line.s
    line.s, line.t, line.alpha, line.p, line.bits, line.gamma = 99, 99, 99, 99, 99, 99
    line.operator_error, line.uniform_error = F(123), F(456)
    disposable = prepared.certificate
    disposable["max_input_bits"] = 100000
    disposable["source_shape"][0] = 99
    need(prepared.fingerprint == fingerprint and prepared.certificate == certificate,
         "all original-state and returned-certificate mutations isolated")
    reject("frozen top-level assignment", lambda: setattr(prepared, "_digit_bits", 63), "cannot assign")
    reject("frozen line assignment", lambda: setattr(prepared._snapshots[0], "gamma", 0), "cannot assign")
    reject("too-wide input", lambda: prepared.multiply(1 << 12, 1), "input width")
    reject("too-wide declaration", lambda: prepared.multiply(1, 1, input_bits=13), "input width")
    reject("too-small declaration", lambda: prepared.multiply(3, 1, input_bits=1), "input width")
    reject("negative integer", lambda: prepared.multiply(-1, 1), "nonnegative integer")
    reject("boolean integer", lambda: prepared.multiply(True, 1), "nonnegative integer")

    def bad(label, change, fragment):
        item = deepcopy(good)
        change(item)
        reject(label, lambda: a.prepare([item]), fragment)

    bad("fake fresh caches", lambda z: (setattr(z, "operator_error", F(0)),
        setattr(z, "uniform_error", F(0)), setattr(z, "compression",
        [[x * 2 for x in row] for row in z.compression])), "operator certificate")
    bad("rescale change", lambda z: setattr(z, "gamma", z.gamma - 1), "rescale binding")
    bad("selector change", lambda z: z.selector.__setitem__(1, 0), "selector binding")
    bad("missing matrix row", lambda z: z.expansion.pop(), "matrix rows")
    bad("missing matrix column", lambda z: z.compression[0].pop(), "matrix columns")
    bad("interval precision change", lambda z: z.expansion[0].__setitem__(0,
        interval(0, 1, z.bits - 1)), "interval domain")
    reject("reversed interval at source constructor", lambda: interval(1, 0, good.bits),
           "interval order/precision")
    bad("wrong interval type", lambda z: z.expansion[0].__setitem__(0, (0, 0, z.bits)), "interval type")
    bad("noncontracting map", lambda z: z.expansion[0].__setitem__(0,
        interval.rational(2, z.bits)), "map contraction")
    bad("boolean parameter", lambda z: setattr(z, "s", True), "integer")
    bad("invalid alpha", lambda z: setattr(z, "alpha", 2), "alpha/theta")
    bad("invalid working guard", lambda z: setattr(z, "bits", z.p + 10), "enclosure guard")
    reject("empty tensor", lambda: a.prepare([]), "nonempty")
    reject("repeated source axis", lambda: a.prepare([good, good]), "coprime")
    reject("boolean digit width", lambda: a.prepare([good], True), "positive digit bits")
    reject("insufficient recovery margin", lambda: a.prepare([good], 200), "exact-recovery")

    # This is not an original-byte allowlist: (-B) FFT (-A) is the same
    # exact composite, and symmetric inward rounding preserves this execution.
    rebased = deepcopy(good)
    rebased.expansion = [[-x for x in row] for row in rebased.expansion]
    rebased.compression = [[-x for x in row] for row in rebased.compression]
    rebased.operator_error = F(123)
    rebased.uniform_error = F(456)
    alternate = a.prepare([rebased])
    need(alternate.fingerprint != fingerprint, "distinct admitted matrix state")
    false_cache = deepcopy(good)
    false_cache.operator_error = false_cache.uniform_error = F(0)
    recertified = a.prepare([false_cache])
    need(recertified.certificate == certificate and recertified.fingerprint == fingerprint,
         "irrelevant cache values cannot affect admission")

    pairs = [(x, y) for x in range(8) for y in range(8)]
    pairs += [(0, 4095), (1, 4095), (4095, 4095), (255, 256), (2730, 1365), (2048, 2048)]
    executions = 0

    def check(obj, cases):
        nonlocal executions
        config = obj.certificate
        size = 1
        for s in config["source_shape"]:
            size *= s
        for left, right in cases:
            result, receipt = obj.multiply(left, right)
            need(result == left * right, "integer product oracle")
            need(receipt["coefficients"] == expected_coefficients(left, right, config["digit_bits"], size),
                 "coefficient convolution oracle")
            need(F(*receipt["error_radius"]) <= F(*config["error_radius"]) < F(1, 2),
                 "admitted uniform recovery radius")
            executions += 1

    check(prepared, pairs)
    check(alternate, pairs[-6:])
    check(recertified, pairs[-6:])
    low = a.prepare([a.new_line(5, 8, 4, precision=128, bits=320)])
    check(low, pairs[-6:])
    tensor = a.prepare([good, a.new_line(7, 16, 5)])
    check(tensor, [(1, 1), ((1 << 72) - 1, (1 << 72) - 1), (0x123456789abcdef, 0xfedcba987654321)])
    bad_grid = a.new_line(7, 16, 4, precision=128, bits=320)
    reject("inconsistent tensor grid", lambda: a.prepare([good, bad_grid]), "common grid")
    return {"source_head": a.SOURCE_HEAD, "stale_cache_witness": {
                "baseline": baseline, "after_mutation": wrong, "true_product": 1,
                "certificate_unchanged": stale == certificate,
                "accepted_error_radius": record["error_radius"], "coefficients": record["coefficients"]},
            "snapshot_fingerprint": fingerprint, "original_certificate": certificate,
            "equivalent_rebase_fingerprint": alternate.fingerprint,
            "checked_products": executions, "negative_controls": rejected,
            "positive_cases": ["original", "post-admission data mutation isolation",
                "returned certificate mutation isolation", "fresh paired sign rebase",
                "ignored incoming fake caches", "second precision", "two-axis tensor"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="intentionally replace result.json")
    args = parser.parse_args()
    result = verify()
    path = Path(__file__).with_name("result.json")
    if args.write:
        path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    else:
        need(json.loads(path.read_text(encoding="utf-8")) == result, "frozen result mismatch")
    print("PASS_GAUSSIAN_PREPARED_STATE_ADMISSION products=" + str(result["checked_products"]) +
          " rejecting_controls=" + str(len(result["negative_controls"])))


if __name__ == "__main__":
    main()
