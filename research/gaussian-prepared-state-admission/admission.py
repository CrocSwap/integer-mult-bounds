"""Frozen prepared-state boundary for the pinned PR2313 dense reference.

Not a sandbox against hostile Python reflection or an independent Gaussian proof.
Only copied data, freshly certified against the pinned implementation, is reused.
"""
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from math import gcd
import builtins
import hashlib
import json
import sys
import types

ROOT = Path(__file__).resolve().parent
SOURCE_HEAD = "190637e62401516c72b267859c0dd51cac607f6d"


def require(condition, label):
    if not condition:
        raise ValueError(label)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def load_source():
    """Check all retained vendor bytes before executing any of them.

    Local import resolution avoids collisions with ambient modules called
    'intervals' or 'gaussian'; it does not rewrite the pinned source bytes.
    """
    manifest = json.loads((ROOT / "SOURCES.json").read_text(encoding="utf-8"))
    blobs = {}
    for entry in manifest["snapshots"]:
        if entry["path"].startswith("vendor/"):
            require(entry["commit"] == SOURCE_HEAD, "source head")
            data = (ROOT / entry["path"]).read_bytes()
            require(hashlib.sha256(data).hexdigest() == entry["sha256"], "source sha256")
            blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            require(blob == entry["git_blob"], "source git blob")
            blobs[Path(entry["path"]).name] = data
    require(set(blobs) == {"intervals.py", "gaussian.py", "pipeline.py", "PROOF.md"},
            "complete source set")
    modules = {}

    def local_import(name, globals=None, locals=None, fromlist=(), level=0):
        if level == 0 and name in modules:
            return modules[name]
        return builtins.__import__(name, globals, locals, fromlist, level)

    for name in ("intervals", "gaussian", "pipeline"):
        module = types.ModuleType("_gaussian_admission_2313_" + name)
        module.__file__ = str(ROOT / "vendor" / (name + ".py"))
        module.__dict__["__builtins__"] = {**vars(builtins), "__import__": local_import}
        sys.modules[module.__name__] = module  # dataclass module lookup
        exec(compile(blobs[name + ".py"], module.__file__, "exec", optimize=0), module.__dict__)
        modules[name] = module
    return modules


_SOURCE = load_source()


def new_line(s, t, alpha, precision=256, bits=448):
    """Construct the original mutable reference input for admission."""
    return _SOURCE["gaussian"].GaussianLine(s, t, alpha, precision, bits)


def _integer(value, label):
    require(type(value) is int, label + " integer")
    return value


def _sequence(value, label):
    require(type(value) in (tuple, list), label + " sequence")
    return tuple(value)


def _matrix(matrix, rows, columns, bits):
    matrix = _sequence(matrix, "matrix")
    require(len(matrix) == rows, "matrix rows")
    frozen = []
    interval = _SOURCE["intervals"].Interval
    for row in matrix:
        row = _sequence(row, "matrix row")
        require(len(row) == columns, "matrix columns")
        out = []
        for item in row:
            require(type(item) is interval, "source interval type")
            lo, hi, q = (_integer(getattr(item, key), "interval " + key)
                         for key in ("lo", "hi", "bits"))
            require(lo <= hi and q == bits, "interval domain")
            out.append((lo, hi, q))
        require(sum(max(abs(lo), abs(hi)) for lo, hi, _ in out) < (1 << bits),
                "fresh map contraction")
        frozen.append(tuple(out))
    return tuple(frozen)


@dataclass(frozen=True, slots=True)
class LineSnapshot:
    s: int
    t: int
    alpha: int
    p: int
    bits: int
    gamma: int
    selector: tuple
    expansion: tuple
    compression: tuple
    operator_error: Fraction | None = None
    uniform_error: Fraction | None = None

    def materialize(self):
        """Private, disposable original-class state, never returned by the API."""
        original = _SOURCE["gaussian"].GaussianLine
        line = original.__new__(original)
        for key in ("s", "t", "alpha", "p", "bits", "gamma"):
            setattr(line, key, getattr(self, key))
        line.selector = list(self.selector)
        interval = _SOURCE["intervals"].Interval
        for key in ("expansion", "compression"):
            setattr(line, key, [[interval(*entry) for entry in row]
                               for row in getattr(self, key)])
        line.operator_error = self.operator_error
        line.uniform_error = self.uniform_error
        return line


def _capture(line):
    """Capture runtime-relevant data; incoming caches and methods are not used."""
    require(type(line) is _SOURCE["gaussian"].GaussianLine, "original line type")
    s, t, alpha, p, bits, gamma = (_integer(getattr(line, key), key)
                                  for key in ("s", "t", "alpha", "p", "bits", "gamma"))
    require(p > 100 and 2 <= s < t < (1 << p) and gcd(s, t) == 1, "resampling domain")
    require(alpha >= 2 and alpha * alpha < p and
            Fraction(t - s, s) > Fraction(p, alpha**4), "alpha/theta domain")
    require(t & (t - 1) == 0, "power-of-two target")
    require(bits > p + 2 * alpha**2 + 32, "working enclosure guard")
    require(gamma == 2 * alpha**2, "rescale binding")
    selector = _sequence(line.selector, "selector")
    require(all(type(k) is int for k in selector) and
            selector == tuple((2 * t * j + s) // (2 * s) for j in range(s)), "selector binding")
    snapshot = LineSnapshot(s, t, alpha, p, bits, gamma, selector,
                            _matrix(line.expansion, t, s, bits),
                            _matrix(line.compression, s, s, bits))
    private = snapshot.materialize()
    private.certify_operator()  # always recompute; incoming cached bounds are irrelevant
    return LineSnapshot(s, t, alpha, p, bits, gamma, selector,
                        snapshot.expansion, snapshot.compression,
                        private.operator_error, private.uniform_error)


@dataclass(frozen=True, slots=True, init=False)
class PreparedMultiplier:
    """An admitted object is constructed only by prepare(), under normal API use."""
    _snapshots: tuple
    _digit_bits: int
    _certificate: bytes
    _fingerprint: str

    @property
    def certificate(self):
        return json.loads(self._certificate)  # caller gets a disposable copy

    @property
    def fingerprint(self):
        return self._fingerprint

    def multiply(self, left, right, *, input_bits=None):
        for value in (left, right):
            require(type(value) is int and value >= 0, "nonnegative integer input")
        needed = max(1, left.bit_length(), right.bit_length())
        if input_bits is None:
            input_bits = needed
        require(type(input_bits) is int and needed <= input_bits <= self.certificate["max_input_bits"],
                "admitted binary input width")
        return _SOURCE["pipeline"].multiply(left, right,
                    [item.materialize() for item in self._snapshots],
                    self._digit_bits, input_bits=input_bits)


def prepare(lines, digit_bits=4):
    """Admit copied data once, reuse exactly those certified snapshots thereafter."""
    require(type(digit_bits) is int and digit_bits > 0, "positive digit bits")
    snapshots = tuple(_capture(line) for line in _sequence(lines, "lines"))
    certificate = _SOURCE["pipeline"].uniform_certificate(
        [item.materialize() for item in snapshots], digit_bits)
    state = {"source_head": SOURCE_HEAD, "digit_bits": digit_bits, "lines": []}
    for item in snapshots:
        state["lines"].append({key: ([value.numerator, value.denominator]
                              if isinstance(value, Fraction) else value)
                              for key in item.__slots__ for value in [getattr(item, key)]})
    result = object.__new__(PreparedMultiplier)
    for key, value in (("_snapshots", snapshots), ("_digit_bits", digit_bits),
                       ("_certificate", canonical(certificate)),
                       ("_fingerprint", hashlib.sha256(canonical(state)).hexdigest())):
        object.__setattr__(result, key, value)
    return result
