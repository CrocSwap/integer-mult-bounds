"""Power-free signed residues in the retained compact ADD compiler.

The new adapter was produced by Nick Petalas. Apache-2.0.
CubeJerry's authenticated compiler, Builder and lifecycle stay unchanged.
"""
import ast
from collections import deque
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from types import ModuleType, SimpleNamespace
import sys

PACKAGE = Path(__file__).resolve().parent
REPOSITORY = PACKAGE.parents[1]
PREFIX = "research/compact-rounded-add/"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def source_bytes(relative):
    rows = json.loads((PACKAGE / "SOURCES.json").read_text())["files"]
    matches = [row for row in rows if row["path"] == relative]
    need(len(matches) == 1, "one declared source")
    data = (REPOSITORY / relative).read_bytes()
    need(len(data) <= 2_000_000, "bounded authenticated source")
    need(hashlib.sha256(data).hexdigest() == matches[0]["sha256"], "source hash")
    return data


def module_from_source(relative, name):
    data = source_bytes(relative)
    module = ModuleType(name)
    module.__file__ = str(REPOSITORY / relative)
    sys.modules[name] = module
    exec(compile(data, relative, "exec"), module.__dict__)
    return module


def definitions(relative, name, names, dependencies):
    """Load exact named definitions with explicit construction dependencies."""
    tree = ast.parse(source_bytes(relative), filename=relative)
    selected = [node for node in tree.body
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names]
    need({node.name for node in selected} == set(names), "complete definition selection")
    need(len(selected) == len(names), "unique definition selection")
    module = ModuleType(name)
    module.__file__ = str(REPOSITORY / relative)
    module.__dict__.update(dependencies)
    sys.modules[name] = module
    exec(compile(ast.Module(body=selected, type_ignores=[]), relative, "exec"),
         module.__dict__)
    return module


BASE = definitions(PREFIX + "vendor/exact_scalar_tables.py", "residue_builder",
                   ("need", "Builder"), {"deque": deque})


class BoundedBuilder(BASE.Builder):
    """Fail explicitly before either construction collection exceeds its cap."""

    def request(self, key):
        need(key in self.claimed or len(self.claimed) < 500_000, "construction-state cap")
        return super().request(key)

    def emit(self, *row):
        need(len(self.rows) < 2_000_000, "construction-row cap")
        super().emit(*row)


class ReverseBuilder(BoundedBuilder):
    """Splice the new finite phase at one exact construction-time edge."""

    def __init__(self, odd, twos, mutant=None):
        super().__init__()
        self.odd, self.twos, self.mutant = odd, twos, mutant
        self.reverse_pending = deque()
        self.replacement_edges = 0
        self.reverse_rows = self.reverse_states = 0

    def request(self, key):
        if key[0].startswith("reverse-"):
            if key not in self.claimed:
                self.claimed.add(key)
                self.reverse_pending.append(key)
                need(len(self.reverse_pending) <= 8 * self.odd + 2, "finite new phase")
            return key
        return super().request(key)

    def goto(self, key):
        if (key[0] == "rewind" and key[1][0] == "residue"):
            _, initial, power, sign, parity = key[1]
            need((initial, power, sign) == (0, 1 % self.odd, 2), "exact entry edge")
            self.replacement_edges += 1
            for residue in range(self.odd):
                super().request(("drop", self.twos, -residue, parity))
            key = ("reverse-start", parity)
        super().goto(key)

    def emit_reverse(self, key):
        odd = self.odd
        tag, *arguments = key
        reject = ("reject",)
        if tag == "reverse-start":
            parity, = arguments
            self.emit("move", 2, -1)
            cases = {s: ("reverse-digit", 0 if self.mutant == "unsigned" else -s % odd,
                         s, parity) for s in (0, 1)}
            self.branch(2, cases, reject)
        elif tag == "reverse-digit":
            residue, bit, parity = arguments
            multiplier = 1 if self.mutant == "missing-double" else 2
            following = (multiplier * residue + bit) % odd
            self.emit("move", 2, -1)
            self.goto(("reverse-scan", following, parity))
        elif tag == "reverse-scan":
            residue, parity = arguments
            cases = {bit: ("reverse-digit", residue, bit, parity) for bit in (0, 1)}
            cases[6] = ("reverse-end", residue, parity)
            self.branch(2, cases, reject)
        elif tag == "reverse-end":
            residue, parity = arguments
            self.emit("move", 2, 1)
            self.goto(("drop", self.twos, -residue, parity))
        else:
            raise ValueError("unknown reverse phase")

    def finish(self):
        need(not self.pending, "inherited phase complete")
        start = len(self.rows)
        for _ in range(8 * self.odd + 2):
            if not self.reverse_pending:
                break
            key = self.reverse_pending.popleft()
            self.mark(key)
            self.emit_reverse(key)
            self.reverse_states += 1
        need(not self.reverse_pending and not self.pending, "closed replacement graph")
        self.reverse_rows = len(self.rows) - start
        need(self.reverse_rows <= 14 * self.odd + 4, "linear residue-row bound")
        return super().finish()


def compile_add(coefficient, *, baseline=False, mutant=None):
    need(isinstance(coefficient, (int, str, Fraction)), "exact rational coefficient")
    need(mutant in (None, "unsigned", "missing-double"), "known construction control")
    q = Fraction(coefficient)
    need(max(abs(q.numerator).bit_length(), q.denominator.bit_length()) <= 24,
         "bounded executable coefficient length")
    odd, twos = q.denominator, 0
    for _ in range(24):
        if odd % 2:
            break
        odd //= 2
        twos += 1
    need(odd <= 125, "retained executable odd-divisor domain")
    builders = []

    def factory():
        builder = BoundedBuilder() if baseline else ReverseBuilder(odd, twos, mutant)
        builders.append(builder)
        return builder

    module = definitions(PREFIX + "tables.py", "residue_compiler_instance",
                         ("compile_compact",),
                         {"Fraction": Fraction, "need": need,
                          "B": SimpleNamespace(Builder=factory)})
    table, receipt = module.compile_compact(q)
    need(len(builders) == 1, "one private construction")
    builder = builders[0]
    if not baseline:
        receipt.update(reverse_rows=builder.reverse_rows,
                       reverse_states=builder.reverse_states,
                       replacement_edges=builder.replacement_edges,
                       phase_entries={parity: builder.labels[("reverse-start", parity)]
                                      for parity in (0, 1)} if odd > 1 else {},
                       phase_exits={pc: key for key, pc in builder.labels.items()
                                    if key[0] == "drop" and key[1] == twos})
        need(builder.replacement_edges == (2 if odd > 1 else 0), "both component parities")
        need(not any(key[0] in ("residue", "res-digit", "res-done")
                     for key in builder.labels), "old residue phase absent")
    return table, receipt


def physical_fixture():
    machine = module_from_source(PREFIX + "vendor/machine.py", "residue_machine")
    names = ("RowCounter", "Tape", "encode_symbols", "symbols", "decode", "execute")
    return definitions(PREFIX + "vendor/physical_fixture.py", "residue_fixture", names,
                       {"need": need, "M": machine, "SimpleNamespace": SimpleNamespace})
