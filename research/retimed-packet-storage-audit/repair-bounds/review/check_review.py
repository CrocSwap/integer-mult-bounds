"""Independent exact arithmetic and source-executed repair-storage review.

No author checker, meter or allocation implementation is imported.  The
universal result is proved in SHARP-REPAIR.md; these finite checks corroborate
its source binding, boundary cases and failure detection.
"""
from fractions import Fraction
from hashlib import sha256
from importlib import import_module
from pathlib import Path
import argparse
import json
import sys


def require(ok, message):
    if not ok:
        raise AssertionError(message)


class ObservedFile:
    """Transparent observer without author-supplied capacity predictions."""
    def __init__(self, stream):
        self.stream = stream
        self.high = 0
        self.erased_on_close = False

    def __enter__(self):
        return self

    def __exit__(self, *unused):
        self.stream.seek(0, 2)
        require(self.stream.tell() == 0, "repair scratch not truncated on return")
        self.erased_on_close = True
        self.stream.close()

    def mark(self):
        self.high = max(self.high, self.stream.tell())

    def seek(self, *args):
        result = self.stream.seek(*args)
        self.mark()
        return result

    def tell(self):
        return self.stream.tell()

    def read(self, *args):
        result = self.stream.read(*args)
        self.mark()
        return result

    def write(self, value):
        result = self.stream.write(value)
        self.mark()
        return result

    def truncate(self, *args):
        # Check the actual pre-truncation bytes independently of the source's
        # zeroing implementation. A stale dirty tail is a review failure.
        where = self.stream.tell()
        self.stream.seek(0)
        require(not any(self.stream.read()), "dirty repair scratch was discarded")
        self.stream.seek(where)
        return self.stream.truncate(*args)


def repair_case(remaining, suffix, component, pattern, malformed=False):
    import spool
    from compact_columns import Columns

    total_bits = remaining + suffix
    arena = spool.Arena(total_bits, component)
    field = arena.field()
    volume = field.count * field.record
    data = bytes((37 * i + i // 127 + 11) % 256 for i in range(volume))
    field.stream.write(data)
    groups = 1 << remaining
    payload = (2 * component) << suffix
    tag = max(1, (remaining + 7) // 8)
    # Both callbacks are fixed pure functions of the address.
    good_index = (lambda i: False) if pattern == "all_bad" else (
        (lambda i: True) if pattern == "all_good" else lambda i: i % 3 == 0)
    holes = [i for i in range(groups) if not good_index(i)]
    good = lambda address: good_index(address >> suffix)
    key = (lambda address: 0) if malformed else lambda address: address
    streams = []
    original = spool.TemporaryFile

    def observe():
        observed = ObservedFile(original())
        streams.append(observed)
        return observed

    spool.TemporaryFile = observe
    error = None
    try:
        columns = Columns(1, 0, 1, 0, 0, 0, suffix, spool.cold_swap)
        try:
            columns.repair(field, good, key)
        except ArithmeticError as exc:
            error = str(exc)
        require(len(streams) == 4, "repair site arity changed")
        require(all(s.erased_on_close for s in streams), "unclosed scratch")
        peaks = [s.high for s in streams]
        if malformed:
            require(error and "true holes" in error, "malformed labels were not rejected")
            require(peaks[1] > (groups // 2) * (payload + tag),
                    "malformed-key control did not violate the distinct-label cap")
            return {"status": "REJECTED_MALFORMED_KEY", "error": error,
                    "observed_peaks": peaks,
                    "note": "No pre-validation bound is asserted for arbitrary malformed keys."}
        require(error is None, "valid repair failed")
        e = len(holes)
        if remaining:
            zero_max = max(sum(not (i >> bit) & 1 for i in holes)
                           for bit in range(remaining))
            one_max = max(sum((i >> bit) & 1 for i in holes)
                          for bit in range(remaining))
        else:
            zero_max = one_max = 0
        oracle = [e * (payload + tag), zero_max * (payload + tag),
                  one_max * (payload + tag), (groups - e) * payload]
        require(peaks == oracle, "independent label-count endpoint oracle disagrees")
        field.stream.seek(0)
        require(field.stream.read(volume) == data, "identity repair changed payload")
        require(arena.live == 1, "repair replacement was retained")
        total = 2 * volume + sum(peaks)
        bound = 4 * volume + 2 * groups * tag
        require(total <= bound, "sharp generic bound failed")
        if tag <= payload:
            require(total <= 6 * volume, "production-premise six-volume bound failed")
        if pattern == "all_bad" and remaining:
            require(total == bound, "all-bad equality witness failed")
        if not remaining:
            require(total == 3 * volume + e * tag, "zero-bit boundary failed")
        return {"remaining": remaining, "suffix": suffix, "component": component,
                "pattern": pattern, "groups": groups, "errors": e,
                "field_bytes": volume, "tag_bytes": tag, "payload_bytes": payload,
                "observed_peaks": peaks, "total_with_fields": total,
                "sharp_bound": bound, "tag_dominance": tag <= payload}
    finally:
        spool.TemporaryFile = original
        # A malformed generic call allocates its replacement before rejecting.
        # Close the test arena directly; no successful-return lifecycle claim
        # is made for that rejected call.
        if malformed:
            arena.tape.seek(0)
            spool.zero_bytes(arena.tape, arena.high * arena.extent)
            arena.tape.close()
        else:
            field.retire()
            arena.close()


def installed_key_cases():
    """Capture the actual row callback; enumerate only its small address map.

    Payload operations are deliberately replaced by no-ops. This checks
    the literal callback and placement validation, not numerical row action.
    """
    from compact_columns import Columns

    class AddressOnlyField:
        def __init__(self, bits):
            self.ambient_bits = bits

        def swap(self, *unused):
            pass

        def rotate(self, *unused):
            pass

    class Capture(Columns):
        def repair(self, field, good, key):
            self.saved_good = good
            self.saved_key = key

    records = []
    for count, window in ((2, 1), (2, 2), (3, 1)):
        for suffix in (0, 2):
            for mode in ("constant", "source_before", "source_after"):
                digit = 1
                ctl = (count - 1) * digit
                back, cursor = suffix, suffix + ctl
                if mode == "source_before":
                    xbase, ybase = cursor, cursor + count * window
                    cursor += 2 * count * window
                elif mode == "source_after":
                    ybase, xbase = cursor, cursor + count * window
                    cursor += 2 * count * window
                else:
                    ybase, xbase = cursor, None
                    cursor += count * window
                front_t, front_u = cursor, cursor + ctl
                ambient = cursor + 2 * ctl
                columns = Capture(window, 0, digit, front_u, front_t, back, suffix, None)
                ys = tuple(ybase + window * i for i in range(count))
                xs = None if xbase is None else tuple(xbase + window * i for i in range(count))
                columns.row(AddressOnlyField(ambient), ys, xs)
                m = 1 << (ambient - suffix)
                images = [columns.saved_key(i << suffix) for i in range(m)]
                require(all(0 <= value < 1 << ambient and value % (1 << suffix) == 0
                            for value in images), "actual key left its complete grouped field")
                require(len(set(images)) == m, "actual validated row key is not injective")
                records.append({"columns": count, "window": window, "suffix": suffix,
                                "mode": mode, "ambient": ambient, "labels": m})
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(args.runtime.resolve()))
    from upstream import install
    install()
    pins = json.loads((root / "SOURCE-BINDINGS.json").read_text())
    for name, record in pins["resolved_modules"].items():
        source = Path(import_module(name).__file__).read_bytes()
        require(sha256(source).hexdigest() == record["sha256"], "changed source: " + name)
        require(source == (root / "sources" / record["file"]).read_bytes(),
                "snapshot differs: " + name)

    # Exact independent arithmetic for the written historical route proof.
    route_coefficient = 5 + Fraction(20, 81) + Fraction(47, 48)
    require(route_coefficient < 7, "route's final rational margin is nonpositive")
    require(Fraction(32, 3) + 5 == Fraction(47, 3), "route role aggregation differs")
    require(3 + Fraction(7, 3) + Fraction(1, 3) == Fraction(17, 3),
            "unit scaler's historical, not simultaneous, role sum differs")
    rational_cases = 0
    for m in (1, 2, 4, 8, 16, 32, 256):
        for e in range(m + 1):
            for a in (1, 2, 7, 16):
                for t in (1, a, a + 1, 3 * a):
                    scratch = (m - e) * a + e * (a + t)
                    if m > 1:
                        scratch += 2 * min(e, m // 2) * (a + t)
                    require(scratch + 2 * m * a <= 4 * m * a + 2 * m * t,
                            "label-count algebra failed")
                    if t <= a:
                        require(scratch + 2 * m * a <= 6 * m * a,
                                "tag-dominant algebra failed")
                    rational_cases += 1
    cases = []
    for remaining in (0, 1, 2, 4, 8, 9):
        for suffix, component in ((0, 1), (1, 1), (2, 3)):
            for pattern in ("all_bad", "all_good", "mixed"):
                cases.append(repair_case(remaining, suffix, component, pattern))
    boundary17 = repair_case(17, 0, 1, "all_bad")
    require(boundary17["total_with_fields"] == 7 * boundary17["field_bytes"],
            "the 17-bit example must not be labelled an 8V counterexample")
    malformed = repair_case(4, 0, 1, "all_bad", malformed=True)
    installed_keys = installed_key_cases()
    historical = []
    for remaining, expected_volumes in ((9, 7), (4, 6)):
        bad = repair_case(remaining, 0, 1, "all_bad")
        good = repair_case(remaining, 0, 1, "all_good")
        peaks = [max(a, b) for a, b in zip(bad['observed_peaks'], good['observed_peaks'], strict=True)]
        volume = bad['field_bytes']
        total = 2 * volume + sum(peaks)
        require(total == expected_volumes * volume, 'varying-call historical boundary failed')
        historical.append({'remaining': remaining, 'tag_bytes': bad['tag_bytes'],
                           'payload_bytes': bad['payload_bytes'], 'field_bytes': volume,
                           'rolewise_historical_peaks': peaks, 'total_with_fields': total,
                           'total_volumes': expected_volumes,
                           'scope': 'actual generic all-bad/all-good pair; not a production-header fixture'})
    m33, a33, t33 = 1 << 33, 2, 5
    symbolic33 = {"remaining": 33, "suffix": 0, "component": 1,
                  "groups": m33, "field_bytes": m33 * a33,
                  "exact_total": 4 * m33 * a33 + 2 * m33 * t33,
                  "execution_status": "NOT_EXECUTED; exact all-bad family formula"}
    require(symbolic33["exact_total"] == 9 * symbolic33["field_bytes"],
            "symbolic generic counterexample arithmetic failed")
    report = {"status": "PASS_INDEPENDENT_RETIMED_BYTES_REVIEW",
              "source_commit": pins["commit"], "source_module_count": len(pins["resolved_modules"]),
              "route_coefficient": [route_coefficient.numerator, route_coefficient.denominator],
              "algebra_cases": rational_cases, "actual_repair_cases": cases,
              "boundary17": boundary17, "malformed_key_control": malformed,
              "actual_key_enumerations": installed_keys,
              "varying_call_historical_controls": historical,
              "symbolic33": symbolic33,
              "scope": "Independent source reading, exact algebra and label-count oracle; no complete stage census or movement proof."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(report["status"], "actual_cases", len(cases) + 5, "algebra_cases", rational_cases)


if __name__ == "__main__":
    main()
