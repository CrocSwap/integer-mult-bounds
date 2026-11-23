"""Exact all-width bucket certificate and source-local ordinary byte checks."""
from contextlib import contextmanager
from fractions import Fraction
from hashlib import sha256
from importlib import import_module
from io import BytesIO
from math import gcd
from pathlib import Path
from types import SimpleNamespace, FunctionType
import argparse
import inspect
import json
import sys


def need(ok, text):
    if not ok:
        raise AssertionError(text)


def bucket_count(q, k, j):
    return ((j + 1) * q + k - 1) // k - (j * q + k - 1) // k


def certificate():
    units = [k for k in range(2, 21) if gcd(k, 3) == 1]
    envelope = [Fraction(1)] + [Fraction(0)] * 19
    periods = []
    for k in units:
        q, power, residues = 3, 1, []
        while True:
            r = q % k
            need(r not in residues, "unit residue repeated before returning to one")
            residues.append(r)
            for j in range(k):
                count = bucket_count(q, k, j)
                first = (-q * j) % k
                inverse_count = 0 if first >= q else (q - 1 - first) // k + 1
                need(count == inverse_count, "forward/inverse bucket multiplicities differ")
                delta = bucket_count(r, k, j)
                need(delta in (0, 1) and count == q // k + delta,
                     "residue decomposition failed")
                envelope[j] = max(envelope[j], Fraction(count, q), Fraction(1, k))
            if r == 1:
                break
            q *= 3
            power += 1
        need(pow(3, power, k) == 1, "invalid period certificate")
        periods.append({"k": k, "period": power, "residues": residues})
    expected = [Fraction(1), Fraction(1, 2)] + [Fraction(1, 3)] * 12 + \
               [Fraction(1, 9)] * 4 + [Fraction(1, 19), Fraction(1, 20)]
    need(envelope == expected, "unexpected exact uniform role envelope")
    total = 2 + sum(envelope)
    need(total == Fraction(27521, 3420) and total < 9, "historical factor margin failed")
    need(Fraction(bucket_count(3, 20, 13), 3) > Fraction(1, 4),
         "undersized-bucket negative control failed")
    return envelope, {"periods": periods,
        "bucket_coefficients": [[x.numerator, x.denominator] for x in envelope],
        "whole_role_coefficient": [total.numerator, total.denominator],
        "undersized_bucket_control": "position13,k20,q3:1/3>1/4"}


class TracedFile:
    def __init__(self, raw):
        self.raw = raw
        self.high = 0
        self.clean = False

    def __enter__(self):
        return self

    def __exit__(self, *unused):
        self.raw.seek(0, 2)
        need(self.raw.tell() == 0, "source returned a nonempty work file")
        self.clean = True
        self.raw.close()

    def mark(self):
        self.high = max(self.high, self.raw.tell())

    def seek(self, *args):
        result = self.raw.seek(*args)
        self.mark()
        return result

    def tell(self):
        return self.raw.tell()

    def read(self, *args):
        result = self.raw.read(*args)
        self.mark()
        return result

    def write(self, data):
        result = self.raw.write(data)
        self.mark()
        return result

    def truncate(self, *args):
        at = self.raw.tell()
        self.raw.seek(0)
        need(not any(self.raw.read()), "source discarded dirty work bytes")
        self.raw.seek(at)
        return self.raw.truncate(*args)


@contextmanager
def spy_files():
    import streaming_routes
    original = streaming_routes.TemporaryFile
    files = []

    def factory():
        item = TracedFile(original())
        files.append(item)
        return item

    streaming_routes.TemporaryFile = factory
    try:
        yield files
    finally:
        streaming_routes.TemporaryFile = original
        need(all(f.clean for f in files), "an observed work file survived return")


def payload(size):
    return bytes((i * 43 + i // 251 + 17) % 256 for i in range(size))


def scalar_oracle(data, widths, prefix, suffix, factor):
    sides = [3 ** s for s in widths]
    whole = 3 ** sum(widths)
    result = bytearray(len(data))
    for p in range(prefix):
        for x in range(whole):
            rem, digits = x, []
            for q in reversed(sides):
                rem, digit = divmod(rem, q)
                digits.append(digit)
            destination = 0
            for q, digit in zip(sides, reversed(digits), strict=True):
                coefficient = factor.numerator * pow(factor.denominator, -1, q) % q
                destination = destination * q + coefficient * digit % q
            old, new = (p * whole + x) * suffix, (p * whole + destination) * suffix
            result[new:new + suffix] = data[old:old + suffix]
    return bytes(result)


def scalar_case(layout, prefix, suffix, factor, envelope):
    import direct_body
    from module_atoms import component_widths
    widths = list(component_widths(layout))
    size = prefix * 3 ** sum(widths) * suffix
    data, out = payload(size), BytesIO()
    with spy_files() as files:
        direct_body.scale_atom(BytesIO(data), out, layout, prefix, suffix, factor)
    need(len(files) == 22, "scale_atom work arity changed")
    need(out.getvalue() == scalar_oracle(data, widths, prefix, suffix, factor),
         "componentwise scalar permutation oracle failed")
    highs = [f.high for f in files]
    need(all(highs[i] <= size for i in (0, 1)), "whole scalar buffer exceeded input")
    for j, coefficient in enumerate(envelope):
        need(highs[j + 2] <= coefficient * size, "uniform scalar bucket bound failed")
    need(sum(highs) < 6 * size, "single-call six-volume bound failed")
    return {"layout": list(layout), "prefix": prefix, "suffix": suffix,
            "factor": [factor.numerator, factor.denominator], "volume": size,
            "role_highs": highs, "total": sum(highs)}


def source_mutant(original, old, new):
    source = inspect.getsource(original)
    need(source.count(old) == 1, "mutation source site is not unique")
    namespace = dict(original.__globals__)
    exec(compile(source.replace(old, new), original.__code__.co_filename, "exec"), namespace)
    created = namespace[original.__name__]
    replacement = FunctionType(created.__code__, original.__globals__, created.__name__,
                               created.__defaults__, created.__closure__)
    replacement.__kwdefaults__ = created.__kwdefaults__
    return replacement


def scalar_cases(envelope):
    units = [k for k in range(2, 21) if gcd(k, 3) == 1]
    records, history = [], [0] * 22
    common = 3 ** 4 * 7
    for width in range(1, 5):
        factors = [Fraction(1), Fraction(-1)]
        for k in units:
            factors.extend((Fraction(k), Fraction(1, k), Fraction(-k), Fraction(-1, k)))
        for factor in factors:
            item = scalar_case((1, width, 0, 0), 1, 7 * 3 ** (4 - width), factor, envelope)
            need(item["volume"] == common, "history witness has differing volume")
            history = [max(a, b) for a, b in zip(history, item["role_highs"], strict=True)]
            records.append(item)
    need(sum(history) > 6 * common, "history witness did not separate per-call from role-wise total")
    need(sum(history) <= Fraction(27521, 3420) * common, "uniform historical envelope failed")
    extra = [scalar_case(layout, 2, 3, factor, envelope)
             for layout in ((1, 2, 1, 1), (0, 0, 3, 1), (1, 3, 1, 1))
             for factor in (Fraction(-5, 7), Fraction(19, 20), Fraction(1))]

    import direct_body
    old = direct_body.integer_scale
    direct_body.integer_scale = source_mutant(
        old, "            for tape in runs:\n                erase(tape)",
        "            for tape in runs:\n                pass  # omitted prefix retirement")
    rejected = None
    try:
        scalar_case((1, 2, 0, 0), 3, 2, Fraction(2), envelope)
    except (AssertionError, EOFError) as error:
        rejected = str(error)
    finally:
        direct_body.integer_scale = old
    need(rejected is not None, "missing bucket erasure survived")
    return {"actual_calls": len(records) + len(extra), "common_volume": common,
            "historical_role_highs": history, "historical_total": sum(history),
            "historical_ratio": [sum(history), common],
            "largest_single_call_ratio": str(max(Fraction(r["total"], r["volume"]) for r in records)),
            "mixed_component_calls": extra, "missing_erase_control": rejected,
            "scope": "actual unchanged scalar source and actual temporary files; independent opaque-block oracle"}


class CountStream:
    def __init__(self, length=0):
        self.pos, self.length, self.high = 0, length, length

    def seek(self, pos, whence=0):
        self.pos = pos if not whence else (self.pos if whence == 1 else self.length) + pos
        need(self.pos >= 0, "negative counting-stream seek")
        self.high = max(self.high, self.pos)
        return self.pos

    def consume(self, length):
        need(0 <= length <= self.length - self.pos, "counted child overread")
        self.pos += length

    def put(self, length):
        need(length >= 0, "negative counted write")
        self.pos += length
        self.length = max(self.length, self.pos)
        self.high = max(self.high, self.pos)


def count_copy(source, target, size):
    source.consume(size)
    if target is not None:
        target.put(size)


def root_case(e, width, rank, owners, lows, highs, prefix=2, gap=3, suffix=5, mutate=False):
    import triangular_ordinary as module
    from ordinary import least_power
    volume = prefix * 3 ** (2 * e) * gap * suffix
    source, target, files, calls = CountStream(volume), CountStream(), [], []
    height = least_power(rank, (e + width - 1) // width)
    rows = owners ** (2 + height) * (lows * highs) ** max(0, height - 8)
    k = least_power(3, rows)
    extent = 3 ** k
    padded = ((extent + rows - 1) // rows) * rows
    expanded = prefix * padded * 3 ** (2 * e - k) * gap * suffix

    @contextmanager
    def count_work(arity):
        need(arity == 5, "root work arity changed")
        files.extend(CountStream() for _ in range(arity))
        yield files

    def body(src, dst, atoms, available, older, inner_gap, inner_suffix):
        declared = available * older * 3 ** (2 * atoms * width) * inner_gap * inner_suffix
        need(declared == expanded == src.length, "root child interface lost residual/padded volume")
        calls.append({"kind": "body", "volume_bits": declared.bit_length()})
        count_copy(src, dst, declared)

    def cold(src, dst, digits, p, g, s):
        declared = p * 3 ** (2 * digits) * g * s
        need(declared == volume, "root cold correction changed complete volume")
        calls.append({"kind": "cold", "volume_bits": declared.bit_length()})
        count_copy(src, dst, declared)

    core = SimpleNamespace(layout=(1, width, 0, 0), n=rank, owners=owners,
                           low=lows, high=highs, body_ordinary=body)
    originals = {name: getattr(module, name) for name in
                 ("work_tapes", "copy_bytes", "write_zeros", "cold_swap_tape")}
    module.work_tapes, module.copy_bytes = count_work, count_copy
    module.write_zeros, module.cold_swap_tape = lambda target, size: target.put(size), cold
    function = module.root_body
    if mutate:
        function = source_mutant(function, "3**r * gap * extent", "gap * extent")
    try:
        function(source, target, e, prefix, gap, suffix, core)
    finally:
        for name, original in originals.items():
            setattr(module, name, original)
    r = (e - k) % width
    wanted = [expanded, expanded, volume, volume if k else 0, volume if r else 0]
    need([f.high for f in files] == wanted, "root historical endpoint equations differ")
    need(source.pos == target.length == volume, "root wrapper did not return complete byte extent")
    need(sum(wanted) < 7 * volume, "root seven-volume bound failed")
    return {"e": e, "width": width, "rank": rank, "owners": owners,
            "lows": lows, "highs": highs, "k": k, "residual": r,
            "volume_bits": volume.bit_length(), "padding_ratio": str(Fraction(expanded, volume)),
            "historical_ratio": str(Fraction(sum(wanted), volume)), "calls": calls}


def transpose(data, side, gap, suffix, prefixes=1):
    out = bytearray(len(data))
    for p in range(prefixes):
        for x in range(side):
            for g in range(gap):
                for y in range(side):
                    old = (((p * side + x) * gap + g) * side + y) * suffix
                    new = (((p * side + y) * gap + g) * side + x) * suffix
                    out[new:new + suffix] = data[old:old + suffix]
    return bytes(out)


def rectangle_cases():
    import ordinary_carrier as module
    from ordinary import least_power
    old_stage, old_ternary = module.stage_for_width_log, module.ternary
    calls = []

    def complete_service(src, dst, digits, prefix, gap, suffix, **unused):
        need(prefix == 1, "public source stopped serializing prefix slabs")
        side = 3 ** digits
        size = side * side * gap * suffix
        data = src.read(size)
        need(len(data) == size, "padded service input is incomplete")
        dst.write(transpose(data, side, gap, suffix))
        calls.append(size)

    module.stage_for_width_log = lambda *unused: 1
    module.ternary = complete_service
    records = []
    try:
        for bits in (1, 2, 3, 5):
            for prefix in (1, 3):
                side, gap, suffix = 1 << bits, 2, 3
                size = prefix * side * side * gap * suffix
                data, out = payload(size), BytesIO()
                before = len(calls)
                with spy_files() as files:
                    module.ordinary_swap(BytesIO(data), out, bits, prefix, gap, suffix)
                need(len(files) == 2, "public rectangle role count changed")
                padded = 3 ** least_power(3, side)
                one = padded * padded * gap * suffix
                need([f.high for f in files] == [one, one], "rectangle accumulated prefix slabs")
                need(out.getvalue() == transpose(data, side, gap, suffix, prefix),
                     "rectangle plus injected complete service changed binary transpose")
                need(2 * one * prefix < 18 * size, "rectangle eighteen-volume bound failed")
                need(len(calls) - before == prefix, "rectangle service count differs from slab count")
                records.append({"bits": bits, "prefixes": prefix, "incoming_bytes": size,
                                "padded_slab_bytes": one, "role_highs": [f.high for f in files]})
    finally:
        module.stage_for_width_log, module.ternary = old_stage, old_ternary
    return {"cases": records,
            "scope": "actual wrapper and byte padding with an injected complete ternary transpose; no native service execution"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    sys.path.insert(0, str(args.runtime.resolve()))
    from upstream import install
    install()
    manifest = json.loads((root / "SOURCE-BINDINGS.json").read_text())
    for name, record in manifest["modules"].items():
        source = Path(import_module(name).__file__).read_bytes()
        need(sha256(source).hexdigest() == record["sha256"], "resolved source differs: " + name)
        need(source == (root / "sources" / record["file"]).read_bytes(), "retained source differs: " + name)
    for name, digest in manifest["retained_guidance"].items():
        need(sha256((root / "sources" / name).read_bytes()).hexdigest() == digest,
             "retained storage guidance differs: " + name)
    envelope, cert = certificate()
    scalar = scalar_cases(envelope)
    roots = [root_case(*shape) for shape in ((20, 3, 2, 2, 1, 1), (37, 4, 2, 2, 16, 27),
                                           (100, 7, 3, 3, 16, 27), (512, 2, 2, 2, 16, 27),
                                           (1025, 2, 2, 2, 16, 27), (7, 2, 2, 1, 1, 1))]
    rejected = None
    try:
        root_case(20, 3, 2, 2, 1, 1, mutate=True)
    except AssertionError as error:
        rejected = str(error)
    need(rejected and "residual/padded" in rejected, "missing root residual factor survived")
    rectangles = rectangle_cases()
    result = {"status": "PASS_DIRECT_SCALAR_AND_ROOT_BYTES",
              "source_commit": manifest["commit"], "certificate": cert, "scalar": scalar,
              "root_byte_count_cases": roots, "missing_residual_control": rejected,
              "rectangle": rectangles,
              "scope": "local fixed-role historical byte envelopes; no global census, movement or kappa claim"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(result["status"], "scalar_calls", scalar["actual_calls"],
          "historical_ratio", str(Fraction(scalar["historical_total"], scalar["common_volume"])))


if __name__ == "__main__":
    main()
