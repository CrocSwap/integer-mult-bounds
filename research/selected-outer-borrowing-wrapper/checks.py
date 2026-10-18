"""Complete-origin and failure fixtures. Host arithmetic is checker-only."""

from contextlib import contextmanager
from dataclasses import asdict, dataclass
from hashlib import sha256

import linear_sign
import outer
import padding
from cardinal_counts import Count
from check_runtime import Tracker, destination
from check_support import audit, no_decode
from predecessor import require
from words import Arena, Ring


def decode(count):
    return sum(bit << i for i, bit in enumerate(count.tape.cells[1:]) if bit in (0, 1))


@contextmanager
def observed(tracker, meter):
    original_tape, original_scan = padding.Tape, padding.scan_rows
    original_add, original_sign_tape = outer.add_pass, linear_sign.Tape
    original_sign, original_swap = outer.sign_address, outer.swap_chunks
    padding.Tape = linear_sign.Tape = tracker.payload

    def scan(source, output, count, width, mode):
        if mode == "zero":
            tracker.last = 0
        return original_scan(source, output, count, width, mode)

    def add(*args, **kwargs):
        if not meter["callee"]:
            meter["ADD"] += 1
        return original_add(*args, **kwargs, payload_factory=tracker.payload)

    def sign(*args, **kwargs):
        if not meter["callee"]:
            meter["sign"] += 1
        return original_sign(*args, **kwargs)

    def swap(*args, **kwargs):
        if not meter["callee"]:
            meter["chunk_swap"] += 1
        return original_swap(*args, **kwargs)

    padding.scan_rows, outer.add_pass = scan, add
    outer.sign_address, outer.swap_chunks = sign, swap
    try:
        with tracker.install(), no_decode():
            yield
    finally:
        padding.Tape, padding.scan_rows = original_tape, original_scan
        outer.add_pass, linear_sign.Tape = original_add, original_sign_tape
        outer.sign_address, outer.swap_chunks = original_sign, original_swap


def full_destination(address, p, r, a, j, z, t):
    address, tail = divmod(address, t)
    address, dr = divmod(address, j)
    address, db = divmod(address, a)
    address, dhi = divmod(address, r)
    address, spectator = divmod(address, z)
    address, hr = divmod(address, j)
    address, hb = divmod(address, a)
    prefix, hhi = divmod(address, r)
    require(prefix < p, "oracle complete source extent")
    result = prefix
    for extent, value in (
        (r, dhi),
        (a, db),
        (j, dr),
        (z, spectator),
        (r, hhi),
        (a, hb),
        (j, hr),
        (t, tail),
    ):
        result = result * extent + value
    return result


def model_callee(source, row_count, *, n, m, p, gap, suffix, ring, q):
    """Compile n literal disjoint atom swaps, not the selected GL64 supplier."""
    current = source
    try:
        for i in range(n):
            # Source H_i and target D_(n-1-i), preserving all ordered gaps.
            extents = tuple(
                Count.literal(value)
                for value in (
                    p * decode(row_count) * m**i,
                    m ** (2 * n - 2 * i - 2) * gap,
                    m**i * suffix,
                )
            )
            try:
                following = outer.swap_chunks(current, ring, q, *extents)
                current = outer.replace(current, following, source)
            finally:
                for extent in extents:
                    extent.close()
        result, current = current, None
        return result
    finally:
        if current is not None and current is not source:
            current.clear()


@dataclass(frozen=True)
class Parameters:
    q: int = 3
    w: int = 1
    n: int = 2
    k: int = 1
    ell: int = 0
    stock_value: int = 2
    p: int = 1
    z: int = 1
    t: int = 1

    def __post_init__(self):
        require(
            self.q in (2, 3)
            and 1 <= self.w <= 2
            and 1 <= self.n <= 3
            and 1 <= self.k <= 3
            and 0 <= self.ell < self.w,
            "bounded fixture digit domain",
        )
        require(
            all(1 <= x <= 2 for x in (self.p, self.z, self.t))
            and 1 <= self.stock_value <= self.q**self.k,
            "bounded fixture spectator and stock domain",
        )

    def extents(self):
        return (
            self.q**self.w,
            self.q**self.k,
            self.q**self.ell,
            self.q ** (self.w * self.n),
        )


class Fixture:
    def __init__(self, parameters, callee_factory, fail_at):
        self.spec, self.factory, self.fail_at = parameters, callee_factory, fail_at
        m, r, j, a = parameters.extents()
        self.volume = parameters.p * r * r * a * a * j * j * parameters.z * parameters.t
        require(self.volume <= 60_000, "bounded complete fixture")
        self.arena, self.indices = Arena(max(3, m.bit_length() + 1)), Arena(8)
        self.modulus, self.atoms = self.arena.input(m), self.indices.input(parameters.n)
        self.high_arena = Arena(max(3, r.bit_length() + 1))
        self.high_mod = self.high_arena.input(r)
        self.ring, self.high = Ring(self.modulus), Ring(self.high_mod)
        self.rem_arena = Arena(max(3, j.bit_length() + 1)) if parameters.ell else None
        self.rem_mod = self.rem_arena.input(j) if parameters.ell else None
        self.remainder = Ring(self.rem_mod) if parameters.ell else None
        self.counts = tuple(
            Count.literal(value)
            for value in (
                parameters.p,
                parameters.z,
                parameters.t,
                parameters.stock_value,
            )
        )
        self.snapshots = [bytes(value.tape.cells) for value in self.counts]
        self.tracker, self.calls, self.call_columns = Tracker(), [], []
        self.meter = {"callee": False, "ADD": 0, "sign": 0, "chunk_swap": 0}
        self.source = self.tracker.source(self.volume)
        self.saved, self.result = bytes(self.source.cells), None

    def callee(self, padded, rows):
        s = self.spec
        m, r, j, a = s.extents()
        self.calls.append(decode(rows))
        if self.fail_at == len(self.calls):
            raise ValueError("injected completed-callee failure")
        input_bytes, row_bytes = bytes(padded.cells), bytes(rows.tape.cells)
        self.meter["callee"] = True
        try:
            if self.factory is not None:
                returned = self.factory(padded, rows)
            else:
                returned = model_callee(
                    padded,
                    rows,
                    n=s.n,
                    m=m,
                    p=s.p,
                    gap=j * s.z * r,
                    suffix=j * s.t,
                    ring=self.ring,
                    q=s.q,
                )
        finally:
            self.meter["callee"] = False
        try:
            width = s.p * decode(rows) * a * a * j * j * s.z * r * s.t
            require(width <= 120_000, "bounded padded fixture")
            for address in range(width):
                target = destination(address, s.n, m, (1,) * s.n, j * s.z * r, j * s.t)
                require(
                    returned.origins.get(target + 1) == padded.origins.get(address + 1),
                    "each completed F has its full row-pointwise endpoint",
                )
            require(
                bytes(padded.cells) == input_bytes and padded.head == 1,
                "completed F preserves borrowed payload and head",
            )
            require(
                bytes(rows.tape.cells) == row_bytes and rows.tape.head == 1,
                "completed F preserves borrowed row count",
            )
            self.call_columns.append(width)
            return returned
        except BaseException:
            returned.clear()
            raise

    def check_result(self):
        s = self.spec
        _m, r, j, a = s.extents()
        for address in range(self.volume):
            target = full_destination(address, s.p, r, a, j, s.z, s.t)
            require(
                self.result.origins.get(target + 1) == 1 << address,
                "complete Boolean-column full-chunk interchange",
            )
            require(
                self.result.cells[target + 1] == self.saved[address + 1],
                "opaque payload endpoint",
            )
        require(
            self.tracker.live == {self.source, self.result},
            "complete owned scratch cleanup",
        )
        require(
            bytes(self.source.cells) == self.saved
            and self.source.head == self.result.head == 1,
            "borrowed source restored",
        )
        require(
            all(
                bytes(value.tape.cells) == old and value.tape.head == 1
                for value, old in zip(self.counts, self.snapshots, strict=True)
            ),
            "all input counts restored",
        )
        padded = ((r + s.stock_value - 1) // s.stock_value) * s.stock_value
        require(self.calls == [padded, padded], "two separately padded F calls")
        passes = {key: value for key, value in self.meter.items() if key != "callee"}
        require(
            passes == {"ADD": 3 * s.n, "sign": s.n, "chunk_swap": 1 + int(s.ell > 0)},
            "complete paid wrapper pass invoice",
        )
        record = asdict(s)
        for original, public in (
            ("stock_value", "stock"),
            ("p", "prefixes"),
            ("z", "spectators"),
            ("t", "suffix"),
        ):
            record[public] = record.pop(original)
        return dict(
            record,
            columns=self.volume,
            padded_calls=self.calls,
            F_columns=self.call_columns,
            wrapper_passes=passes,
            output_sha256=sha256(bytes(self.result.cells)).hexdigest(),
        )

    def run(self):
        try:
            with observed(self.tracker, self.meter):
                self.result = outer.interchange(
                    self.source,
                    self.atoms,
                    self.ring,
                    self.high,
                    self.spec.q,
                    *self.counts,
                    self.callee,
                    self.remainder,
                )
        except ValueError as error:
            if self.fail_at is None:
                raise
            require(
                str(error) == "injected completed-callee failure"
                and len(self.calls) == self.fail_at,
                "expected callee failure",
            )
            require(
                self.tracker.live == {self.source},
                "wrapper closes all work on callee failure",
            )
            require(
                bytes(self.source.cells) == self.saved and self.source.head == 1,
                "failed-call source restored",
            )
            return {"failed_at": self.fail_at, "calls": self.calls}
        require(self.fail_at is None, "expected failure actually occurred")
        return self.check_result()

    def close(self):
        if self.result is not None:
            self.result.clear()
        self.source.clear()
        for count in self.counts:
            count.close()
        self.indices.free(self.atoms)
        self.ring.close()
        self.arena.free(self.modulus)
        self.high.close()
        self.high_arena.free(self.high_mod)
        if self.remainder is not None:
            self.remainder.close()
            self.rem_arena.free(self.rem_mod)
            audit(self.rem_arena)
        for arena in (self.arena, self.high_arena, self.indices):
            audit(arena)
        require(not self.tracker.live, "fixture teardown erases all owned contents")


def case(*, callee_factory=None, fail_at=None, **parameters):
    fixture = Fixture(Parameters(**parameters), callee_factory, fail_at)
    try:
        return fixture.run()
    finally:
        fixture.close()


def run_cases():
    specifications = (
        {},
        {"n": 1},
        {"n": 3, "stock_value": 1},
        {"q": 2, "n": 2, "k": 3, "stock_value": 6},
        {"n": 1, "k": 2, "stock_value": 2, "p": 2, "z": 2, "t": 2},
        {"q": 2, "w": 2, "n": 1, "ell": 1, "k": 2, "stock_value": 3},
        {"q": 3, "w": 2, "n": 1, "ell": 1},
        {"stock_value": 3},
        {"q": 2, "w": 2, "n": 2, "ell": 1, "k": 2, "stock_value": 3},
    )
    return [case(**specification) for specification in specifications]
