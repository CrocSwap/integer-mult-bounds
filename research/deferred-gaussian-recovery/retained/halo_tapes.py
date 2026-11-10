"""Sequential bit-tape halo transport; no numerical halo solver is hidden here.

Only Tape's simulator backend uses positions or random-access storage.  Program
methods observe one symbol, write one symbol, or move one cell.  Python locals
in those methods range over finite alphabets/booleans, except fixed tape handles.
Fixture construction, inspection, and instrumentation are outside the machine.
"""

from collections import Counter


class Reject(ValueError):
    pass


class Tape:
    """Simulator backend. Erased cells still count toward retained backing."""

    def __init__(self, name, contents=""):
        self.name = name
        self._cells = dict(enumerate("^" + contents + "!"))
        self._head = 0
        self._high = len(contents) + 1
        self.actions = Counter()

    def read(self):
        self.actions["read"] += 1
        return self._cells.get(self._head, "_")

    def write(self, symbol):
        if len(symbol) != 1:
            raise Reject("non-symbol write")
        self.actions["write"] += 1
        self._cells[self._head] = symbol
        self._high = max(self._high, self._head)

    def move(self, direction):
        if direction not in (-1, 1):
            raise Reject("nonunit head move")
        self.actions["move"] += 1
        self._head += direction
        if self._head < 0:
            raise Reject("crossed left sentinel")
        self._high = max(self._high, self._head)

    def inspect(self):
        """Unmetered *test observer*: never called by Program or its helpers."""
        chars = []
        pos = 1
        while self._cells.get(pos) != "!":
            chars.append(self._cells.get(pos, "_"))
            pos += 1
            if pos > self._high:
                raise Reject("observer found no terminator")
        return "".join(chars)

    def bill(self):
        return {**self.actions, "retained_cells": self._high + 1}


def home(t):
    while t.read() != "^":
        t.move(-1)
    t.move(1)


def end(t):
    while t.read() != "!":
        t.move(1)


def append(t, ch):
    # Caller owns the right-end head. No length or append index is available.
    t.write(ch)
    t.move(1)
    t.write("!")


def clear(t):
    home(t)
    while t.read() != "!":
        t.write("_")
        t.move(1)
    t.write("_")
    home(t)
    t.write("!")


def copy_bits(src, dst):
    while src.read() in "01":
        append(dst, src.read())
        src.move(1)


def copy_whole(src, dst):
    home(src)
    while src.read() != "!":
        append(dst, src.read())
        src.move(1)


def clone(src, dst):
    clear(dst)
    copy_whole(src, dst)


def skip_to(t, ch):
    while t.read() != ch:
        if t.read() == "!":
            raise Reject("missing field delimiter")
        t.move(1)


def compare(a, b):
    """Equal-width unsigned binary comparison; result is a three-state value."""
    home(a)
    home(b)
    relation = "equal"
    while a.read() != "!":
        if b.read() not in "01" or a.read() not in "01":
            raise Reject("unequal or malformed comparison fields")
        if relation == "equal":
            if a.read() == "0" and b.read() == "1":
                relation = "less"
            elif a.read() == "1" and b.read() == "0":
                relation = "greater"
        a.move(1)
        b.move(1)
    if b.read() != "!":
        raise Reject("unequal comparison widths")
    return relation


def add_mod(a, b, subtract=False):
    """Binary ripple addition/subtraction, truncated to the common field width."""
    home(a)
    end(a)
    home(b)
    end(b)
    a.move(-1)
    b.move(-1)
    carry = subtract
    while a.read() != "^":
        x = a.read() == "1"
        y = b.read() == "1"
        if b.read() not in "01":
            raise Reject("unequal arithmetic widths")
        if subtract:
            y = not y
        a.write("1" if x ^ y ^ carry else "0")
        carry = (x and y) or (carry and (x or y))
        a.move(-1)
        b.move(-1)
    if b.read() != "^":
        raise Reject("unequal arithmetic widths")


def step_binary(t, down=False):
    """Modulo 2**width increment/decrement of a plain binary field."""
    home(t)
    end(t)
    t.move(-1)
    while t.read() != "^":
        old = t.read()
        t.write("0" if old == "1" else "1")
        if (old == "1") == down:
            return
        t.move(-1)


def coordinate_next(t):
    """Increment concatenated coordinate bits, skipping only schema delimiters."""
    home(t)
    end(t)
    t.move(-1)
    carrying = True
    while t.read() != "^":
        if t.read() in "01" and carrying:
            if t.read() == "0":
                t.write("1")
                carrying = False
            else:
                t.write("0")
        t.move(-1)
    return not carrying


def flatten(t, dst):
    clear(dst)
    home(t)
    while t.read() != "!":
        if t.read() in "01":
            append(dst, t.read())
        t.move(1)


class Program:
    """A fixed collection of tape roles, independent of dimension or volume."""

    def __init__(self, source, coordinates, length, width_a, width_b, returns=""):
        # Loading caller-supplied binary inputs is outside the program's bill;
        # their cells are included in retained backing from the beginning.
        self.source = Tape("source", source)
        self.x = Tape("coordinates", coordinates)
        self.L = Tape("L", length)
        self.A = Tape("A", width_a)
        self.b = Tape("b", width_b)
        self.returns = Tape("returns", returns)
        self.saved = Tape("saved")
        self.final = Tape("final")
        self.d = Tape("descriptor")
        self.faces = Tape("faces")
        self.unary = Tape("axis_index")
        self.q = Tape("core_field")
        self.r = Tape("local_field")
        self.payload = Tape("payload")
        self.kcore = Tape("key_core")
        self.kface = Tape("key_face")
        self.klocal = Tape("key_local")
        self.ksource = Tape("key_source")
        self.retkey = Tape("return_key")
        self.retval = Tape("return_value")
        self.bucket0 = Tape("radix_zero")
        self.bucket1 = Tape("radix_one")
        self.record = Tape("radix_record")
        self.passes = Tape("radix_passes")
        self.Am = Tape("A_minus_b")
        self.Ap = Tape("A_plus_b")
        self.LAm = Tape("L_minus_A_minus_b")
        self.LAp = Tape("L_minus_A_plus_b")
        self.Lb = Tape("L_minus_b")
        self.LA = Tape("L_minus_A")
        # This tuple is a fixed schema, never sized using input data.
        self.roles = (
            self.source, self.x, self.L, self.A, self.b, self.returns,
            self.saved, self.final, self.d, self.faces, self.unary, self.q,
            self.r, self.payload, self.kcore, self.kface, self.klocal,
            self.ksource, self.retkey, self.retval, self.bucket0, self.bucket1,
            self.record, self.passes, self.Am, self.Ap, self.LAm, self.LAp,
            self.Lb, self.LA,
        )
        self.phase = "input"

    def setup(self):
        clone(self.A, self.Am)
        add_mod(self.Am, self.b, subtract=True)
        clone(self.A, self.Ap)
        add_mod(self.Ap, self.b)
        clone(self.L, self.LA)
        add_mod(self.LA, self.A, subtract=True)
        clone(self.LA, self.LAm)
        add_mod(self.LAm, self.b, subtract=True)
        clone(self.LA, self.LAp)
        add_mod(self.LAp, self.b)
        clone(self.L, self.Lb)
        add_mod(self.Lb, self.b, subtract=True)

    def load_payload(self, source, dest):
        clear(dest)
        copy_bits(source, dest)
        if source.read() != "#":
            raise Reject("bad payload delimiter")
        source.move(1)

    def face_record(self, side):
        home(self.unary)
        copy_bits(self.unary, self.faces)
        append(self.faces, "0")
        append(self.faces, side)
        append(self.faces, "#")

    def build_descriptor(self):
        clear(self.d)
        clear(self.faces)
        clear(self.unary)
        clear(self.ksource)
        home(self.x)
        while self.x.read() != "&":
            append(self.d, self.x.read())
            append(self.ksource, self.x.read())
            self.x.move(1)
        append(self.d, "&")
        self.x.move(1)
        prefix = True
        while self.x.read() != "!":
            if self.x.read() != "@":
                raise Reject("bad coordinate schema")
            append(self.d, "@")
            self.x.move(1)
            while self.x.read() != "#":
                append(self.d, self.x.read())
                append(self.ksource, self.x.read())
                self.x.move(1)
            append(self.d, "#")
            self.x.move(1)
            clear(self.r)
            append(self.r, "0")
            append(self.r, "0")
            while self.x.read() != ";":
                append(self.r, self.x.read())
                append(self.ksource, self.x.read())
                self.x.move(1)
            self.x.move(1)
            copy_whole(self.r, self.d)
            append(self.d, "#")
            interior = compare(self.r, self.Am) != "less"
            interior = interior and compare(self.r, self.LAp) == "less"
            low = compare(self.r, self.b) == "less"
            high = compare(self.r, self.Lb) != "less"
            lower = compare(self.r, self.Ap) == "less"
            upper = compare(self.r, self.LAm) != "less"
            append(self.d, "1" if interior else "0")
            append(self.d, "1" if low else "0")
            append(self.d, "1" if high else "0")
            append(self.d, "1" if lower else "0")
            append(self.d, "1" if upper else "0")
            append(self.d, "e" if low or high else "n")
            append(self.d, "0")
            append(self.d, ";")
            if prefix and (lower or high):
                self.face_record("0")
            if prefix and (upper or low):
                self.face_record("1")
            prefix = prefix and interior
            end(self.unary)
            append(self.unary, "1")

    def prepare_face(self):
        # Reset old face and suffix choices; all scans are through tape cells.
        home(self.d)
        skip_to(self.d, "&")
        self.d.move(1)
        while self.d.read() != "!":
            self.d.write("@")
            skip_to(self.d, "#")
            self.d.move(1)
            skip_to(self.d, "#")
            self.d.move(1)
            self.d.move(1)
            self.d.move(1)
            self.d.move(1)
            self.d.move(1)
            self.d.move(1)
            if self.d.read() == "*":
                self.d.write("e")
            self.d.move(1)
            self.d.write("0")
            self.d.move(1)
            self.d.move(1)
        home(self.d)
        skip_to(self.d, "&")
        self.d.move(1)
        while self.faces.read() == "1":
            skip_to(self.d, ";")
            self.d.move(1)
            self.faces.move(1)
        if self.faces.read() != "0":
            raise Reject("bad face index")
        self.faces.move(1)
        self.d.write("<" if self.faces.read() == "0" else ">")
        self.faces.move(1)
        if self.faces.read() != "#":
            raise Reject("bad face delimiter")
        self.faces.move(1)
        skip_to(self.d, ";")
        self.d.move(1)
        while self.d.read() != "!":
            skip_to(self.d, ";")
            self.d.move(-1)
            self.d.move(-1)
            if self.d.read() == "e":
                self.d.write("*")
            self.d.move(1)
            self.d.move(1)
            self.d.move(1)

    def next_choice(self):
        home(self.d)
        end(self.d)
        self.d.move(-1)
        while self.d.read() != "^":
            if self.d.read() == "*":
                self.d.move(1)
                if self.d.read() == "0":
                    self.d.write("1")
                    return True
                self.d.write("0")
                self.d.move(-1)
            self.d.move(-1)
        return False

    def emit(self):
        clear(self.kcore)
        clear(self.kface)
        clear(self.klocal)
        home(self.d)
        while self.d.read() != "&":
            append(self.kcore, self.d.read())
            self.d.move(1)
        self.d.move(1)
        after = False
        side = "0"
        while self.d.read() != "!":
            marker = self.d.read()
            self.d.move(1)
            clear(self.q)
            copy_bits(self.d, self.q)
            self.d.move(1)
            clear(self.r)
            copy_bits(self.d, self.r)
            self.d.move(1)
            self.d.move(1)  # interior flag
            low = self.d.read() == "1"
            self.d.move(1)
            high = self.d.read() == "1"
            self.d.move(1)
            lower = self.d.read() == "1"
            self.d.move(1)
            upper = self.d.read() == "1"
            self.d.move(1)  # eligibility
            self.d.move(1)
            alternative = self.d.read() == "1"
            self.d.move(1)
            self.d.move(1)
            if marker == "<":
                side = "0"
                append(self.kface, "1")
                add_mod(self.r, self.b)
                if not lower:
                    if not high:
                        raise Reject("inadmissible lower face")
                    step_binary(self.q)
                    add_mod(self.r, self.L, subtract=True)
                after = True
            elif marker == ">":
                side = "1"
                append(self.kface, "1")
                add_mod(self.r, self.Ap)
                if upper:
                    add_mod(self.r, self.L, subtract=True)
                else:
                    if not low:
                        raise Reject("inadmissible upper face")
                    step_binary(self.q, down=True)
                after = True
            elif not after:
                append(self.kface, "0")
                add_mod(self.r, self.Am, subtract=True)
            else:
                append(self.kface, "0")
                add_mod(self.r, self.b)
                if alternative:
                    if low:
                        step_binary(self.q, down=True)
                        add_mod(self.r, self.L)
                    elif high:
                        step_binary(self.q)
                        add_mod(self.r, self.L, subtract=True)
                    else:
                        raise Reject("inadmissible suffix alternative")
            copy_whole(self.q, self.kcore)
            copy_whole(self.r, self.klocal)
        append(self.kface, side)
        copy_whole(self.kcore, self.saved)
        copy_whole(self.kface, self.saved)
        copy_whole(self.klocal, self.saved)
        copy_whole(self.ksource, self.saved)
        append(self.saved, "#")
        copy_whole(self.payload, self.saved)
        append(self.saved, "#")

    def gather(self):
        if self.phase != "input":
            raise Reject("gather must precede every core mutation")
        self.setup()
        home(self.source)
        end(self.saved)
        more = True
        while self.source.read() != "!":
            if not more:
                raise Reject("more payloads than coordinates")
            self.load_payload(self.source, self.payload)
            self.build_descriptor()
            home(self.faces)
            while self.faces.read() != "!":
                self.prepare_face()
                self.emit()
                while self.next_choice():
                    self.emit()
            more = coordinate_next(self.x)
        if more:
            raise Reject("fewer payloads than coordinates")
        self.phase = "saved"

    def sort(self, tape, reverse_buckets=False):
        """Stable binary LSD radix; rotate keys to expose each next digit.

        A unary pass clock is copied from the first key on tape. After exactly
        that many right rotations, the complete key is restored. No host key
        length, pass index, record array, integer key, or comparison sort occurs.
        """
        clear(self.passes)
        home(tape)
        if tape.read() == "!":
            return
        while tape.read() in "01":
            append(self.passes, "1")
            tape.move(1)
        if tape.read() != "#":
            raise Reject("bad radix key")
        home(self.passes)
        while self.passes.read() == "1":
            clear(self.bucket0)
            clear(self.bucket1)
            home(tape)
            while tape.read() != "!":
                clear(self.record)
                last = "0"
                while tape.read() in "01":
                    last = tape.read()
                    append(self.record, last)
                    tape.move(1)
                if tape.read() != "#":
                    raise Reject("bad radix key delimiter")
                append(self.record, "#")
                tape.move(1)
                copy_bits(tape, self.record)
                if tape.read() != "#":
                    raise Reject("bad radix payload delimiter")
                append(self.record, "#")
                tape.move(1)
                target = self.bucket0 if last == "0" else self.bucket1
                append(target, last)
                home(self.record)
                previous = self.record.read()
                self.record.move(1)
                while self.record.read() != "#":
                    append(target, previous)
                    previous = self.record.read()
                    self.record.move(1)
                append(target, "#")
                self.record.move(1)
                copy_bits(self.record, target)
                append(target, "#")
            clear(tape)
            if reverse_buckets:
                copy_whole(self.bucket1, tape)
                copy_whole(self.bucket0, tape)
            else:
                copy_whole(self.bucket0, tape)
                copy_whole(self.bucket1, tape)
            self.passes.write("0")
            self.passes.move(1)
        clear(self.bucket0)
        clear(self.bucket1)
        clear(self.record)
        clear(self.passes)

    def core_complement_test_double(self):
        """Physical mutation for chronology controls; not a Gaussian core."""
        if self.phase != "saved":
            raise Reject("core mutation before copies are complete")
        home(self.source)
        while self.source.read() != "!":
            if self.source.read() == "0":
                self.source.write("1")
            elif self.source.read() == "1":
                self.source.write("0")
            self.source.move(1)
        self.phase = "core"

    def pending_return(self):
        if self.returns.read() == "!":
            clear(self.retkey)
            clear(self.retval)
            return False
        self.load_payload(self.returns, self.retkey)
        self.load_payload(self.returns, self.retval)
        return True

    def discarded(self):
        home(self.x)
        skip_to(self.x, "&")
        self.x.move(1)
        boundary = False
        while self.x.read() != "!":
            skip_to(self.x, "#")
            self.x.move(1)
            clear(self.r)
            append(self.r, "0")
            append(self.r, "0")
            copy_bits(self.x, self.r)
            if compare(self.r, self.A) == "less":
                boundary = True
            if compare(self.r, self.LA) != "less":
                boundary = True
            if self.x.read() != ";":
                raise Reject("bad coordinate local field")
            self.x.move(1)
        return boundary

    def merge_returns(self):
        if self.phase != "core":
            raise Reject("return requires completed core phase")
        self.sort(self.returns)
        home(self.returns)
        pending = self.pending_return()
        home(self.source)
        clear(self.final)
        more = True
        while self.source.read() != "!":
            if not more:
                raise Reject("more core values than coordinates")
            self.load_payload(self.source, self.payload)
            flatten(self.x, self.ksource)
            boundary = self.discarded()
            relation = compare(self.retkey, self.ksource) if pending else "none"
            if boundary:
                if relation != "equal":
                    raise Reject("missing, duplicate, or misplaced boundary return")
                copy_whole(self.retval, self.final)
                pending = self.pending_return()
            else:
                if pending and relation != "greater":
                    raise Reject("duplicate or kept-row return")
                copy_whole(self.payload, self.final)
            append(self.final, "#")
            more = coordinate_next(self.x)
        if more or pending:
            raise Reject("incomplete source cube or extra return")
        self.phase = "returned"

    def erase_work(self):
        if self.phase != "returned":
            raise Reject("erase before return completion")
        # Roles remain allocated. The ledger deliberately does not reset peaks.
        for tape in self.roles:
            if tape is not self.final:
                clear(tape)
        self.phase = "erased"

    def ledger(self):
        """Observer, not part of the machine."""
        return {tape.name: tape.bill() for tape in self.roles}
