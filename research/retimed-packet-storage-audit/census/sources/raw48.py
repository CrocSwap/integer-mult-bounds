"""Run the mixed 48-call word on independent fixed-grid Gaussian fields."""

from fractions import Fraction
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import gzip
import json
import sys


def read_json(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def source_module(path, name):
    spec = spec_from_file_location(name, path)
    obj = module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


class Artifacts:
    def __init__(self, grade):
        from tagged_sources import PINS

        grade = Path(grade)
        directory = grade / "retained"
        for relative, expected in PINS.items():
            if sha256((directory / relative).read_bytes()).hexdigest() != expected:
                raise ValueError("The raw word source bytes differ")
        data = directory / "data"
        self.graph = read_json(data / "complex.json.gz")
        self.layout = read_json(data / "layout.json.gz")
        atlas = read_json(grade / "complex-atlas.json.gz")
        with (grade / "RESULT.json").open() as source:
            receipt = json.load(source)["complex"]
        canonical = json.dumps(atlas, sort_keys=True, separators=(",", ":")).encode()
        if sha256(canonical).hexdigest() != receipt["atlas_sha256"]:
            raise ValueError("The nine-axis true Clifford catalogue differs")
        basis = read_json(data / "CALLER-PHASE-BASES.json")["by_q"]
        self.contacts = [contact(q, tuple(basis[str(q)])) for q in self.layout["ports"]]
        self.factors = {
            (a, b): (r["rank"], monomial(r["right"]), monomial(r["left"]))
            for a, b, r in atlas["pairs"]
        }
        self.port = [(monomial(l), monomial(r)) for _, l, r in atlas["ports"]]
        mixed = source_module(directory / "mixed_caller.py", "raw48_mixed")
        prior = sys.modules.get("mixed_caller")
        sys.modules["mixed_caller"] = mixed
        try:
            closed = source_module(directory / "closed_caller.py", "raw48_closed")
            caller = read_json(data / "CALLER.json.gz")
            self.words, self.roots = closed.templates(caller), closed.placement(caller)
        finally:
            if prior is None:
                del sys.modules["mixed_caller"]
            else:
                sys.modules["mixed_caller"] = prior
        bindings, self.offsets, _ = mixed.layout_bindings(self.words, self.roots, self.layout, 48)
        self.instructions = lambda: mixed.instructions(
            self.words, self.roots, bindings, self.offsets
        )
        self.moves = {i: (a, b) for i, a, b in self.graph["moves"]}
        self.forms = {
            i: tuple((j, Fraction(c)) for j, c in terms) for i, terms in self.graph["forms"]
        }
        hosted = self.layout["hosted"]
        pair = dict(
            zip(hosted["Dports"], zip(hosted["X2"], hosted["Y2"], strict=True), strict=True)
        )
        self.regs = [(x, x + 112) + pair.get(i, ()) for i, x in enumerate(self.layout["live"])]
        self.main = set(j for regs in self.regs for j in regs)
        self.odd = grade / "retained" / "grade14-audit.json"
        grid = read_json(self.odd)["basis_grid"]
        self.odd = grid["product_grid"] >> grid["dyadic_height"]


def linear(rows):
    work = list(rows)
    record = []
    for j in range(len(work)):
        choice = next((i for i in range(j, len(work)) if work[i] >> j & 1), None)
        if choice is None:
            raise ValueError("Singular slot matrix")
        if j != choice:
            work[j], work[choice] = work[choice], work[j]
            record.extend((("ROW", j, choice), ("ROW", choice, j), ("ROW", j, choice)))
        for i in range(len(work)):
            if i != j and work[i] >> j & 1:
                work[i] ^= work[j]
                record.append(("ROW", i, j))
    return tuple(reversed(record))


def monomial(r):
    n = len(r["matrix_rows"])
    return (
        tuple(("S", i, q) for i, q in enumerate(r["linear_Z4"]) if q)
        + tuple(
            ("CZ", i, j)
            for i, row in enumerate(r["quadratic_rows"])
            for j in range(i + 1, n)
            if row >> j & 1
        )
        + linear(r["matrix_rows"])
        + tuple(("NOT", i) for i in range(n) if r["offset"] >> i & 1)
        + (("I", r["phase"]),)
    )


def contact(q, basis):
    ortho = (q,) + basis
    if len(ortho) != 9 or any(
        (v & w).bit_count() % 2 != (i == j)
        for i, v in enumerate(ortho)
        for j, w in enumerate(ortho)
    ):
        raise ValueError("The true port requires a nine-dimensional orthogonal frame")
    cols = (q,) + tuple(1 << j for j in range(9, 17)) + basis
    rows = tuple(sum(((c >> i) & 1) << j for j, c in enumerate(cols)) for i in range(17))
    physical = (0,) + tuple(range(9, 17))
    delta = tuple(
        ("NOT", axis)
        for axis, v in zip(physical, ortho, strict=True)
        if (v.bit_count() - 1) % 4 == 2
    )
    return linear(rows), delta


class ComplexRaw:
    """Indices in Job.axes denote complete groups of 'bundle' adjacent windows.

    Supply the positive-rank frame with a common 153*columns eligible slots,
    a genuine dirty-control Columns object, and a store mapping owner tags
    to Field. The active region starts at bit 'low' counted from the LSB.
    """

    def __init__(self, artifacts, fields, columns, *, low, bundle, slots):
        from periodic import Job

        self.Job, self.art, self.fields, self.columns = Job, artifacts, fields, columns
        self.low, self.bundle, self.slots = low, bundle, slots
        self.cursor = 0

    def scratch(self, field):
        token = (self, self.cursor)
        self.cursor += 1
        self.fields[token] = field
        return token

    def fresh(self, exemplar, width, tag):
        field = self.fields[exemplar.owner].blank()
        field.clear()
        return self.Job(self.scratch(field), tuple(range(width)))

    def retire(self, job):
        self.fields.pop(job.owner).retire()

    def positions(self, axis, cols):
        k = self.columns.window
        first = self.low + self.columns.offset + axis * cols * self.bundle * k
        return range(first, first + cols * self.bundle * k, k)

    def align(self, field, job, canonical):
        if len(job.axes) != len(canonical) or len(set(job.axes)) != len(job.axes):
            raise ValueError("The external source lost distinct positive axes")
        at, where, swaps = {}, {}, []
        size = self.bundle * self.columns.window
        for dest, src in zip(canonical, job.axes, strict=True):
            if not 0 <= src < self.slots or not 0 <= dest < self.slots:
                raise ValueError("The native source left the real slot range")
            pos = where.get(src, src)
            if dest == pos:
                continue
            displaced = at.get(dest, dest)
            field.swap(self.low + dest * size, self.low + pos * size, size, self.columns.swap)
            swaps.append((dest, pos))
            at[dest], at[pos] = src, displaced
            where[src], where[displaced] = dest, pos
        return swaps

    def unalign(self, field, route):
        size = self.bundle * self.columns.window
        for l, r in reversed(route):
            field.swap(self.low + l * size, self.low + r * size, size, self.columns.swap)

    def chart(self, field, tape, axes, cols, inverse=False):
        sites = [self.positions(a, cols) for a in axes]
        for ins in reversed(tape) if inverse else tape:
            op, *s = ins
            if op == "ROW":
                self.columns.row(field, sites[s[0]], sites[s[1]])
            elif op == "NOT":
                self.columns.row(field, sites[s[0]])
            elif op == "I":
                phase = s[0] * cols * self.bundle * (-1 if inverse else 1)
                if phase % 4:
                    field.phase(lambda _: phase, self.columns.suffix)
            elif op == "S":
                sign = s[1] * (-1 if inverse else 1)
                field.phase(
                    lambda x: sign * sum((x >> i) & 1 for i in sites[s[0]]), self.columns.suffix
                )
            elif op == "CZ":
                field.phase(
                    lambda x: (
                        2
                        * sum(
                            (x >> i) & (x >> j) & 1
                            for i, j in zip(sites[s[0]], sites[s[1]], strict=True)
                        )
                    ),
                    self.columns.suffix,
                )
            else:
                raise ValueError("Unknown monomial record")

    @staticmethod
    def axis_list(cols, axes):
        return tuple(axis * cols + j for axis in axes for j in range(cols))

    def head_flip(self, field, cols):
        self.columns.row(field, self.positions(0, cols))

    def raw(self, productive, cols):
        if 153 * cols > self.slots:
            raise ValueError("Missing complete ambient for a mixed raw invocation")
        jobs = dict(productive)
        if len(jobs) != len(productive) or len({j.owner for j in jobs.values()}) != len(jobs):
            raise ValueError("Each productive source requires a distinct owner and label")
        a = self.art
        root, roots = {}, []
        for (kind, root_id), visits in a.roots.items():
            for i, (sign, entries) in enumerate(a.words[kind][1]):
                reg = a.offsets[kind, root_id] + i
                job = jobs[("root", kind, root_id, reg, sign)]
                colors = [visits[j][0] % 16 for j in entries]
                coords = (0,) + tuple(9 + 8 * c + j for c in colors for j in range(8))
                field = self.fields[job.owner]
                route = self.align(field, job, self.axis_list(cols, coords))
                field.scale(2025)
                root[reg] = field
                roots.append((reg, job, sign, route))
        for clock, row in enumerate(a.instructions()):
            op = row[0]
            if op == "PORT_VIEWS":
                continue
            if op == "NATIVE":
                yield from self.graph(clock, row[1], row[2], row[3], jobs, root, cols)
                continue
            dest = row[1]
            field = root[dest]
            if op == "SWAP":
                root[dest], root[row[2]] = root[row[2]], field
            elif op == "ADD":
                field.scale_add(root[row[2]], *map(Fraction, row[3]))
            elif op == "SCALE":
                field.scale(*map(Fraction, row[2]))
            elif op == "LAMBDA":
                shifted = field.copy()
                self.head_flip(shifted, cols)
                field.scale(Fraction(1, 2), Fraction(row[2], 2))
                field.scale_add(shifted, Fraction(1, 2), Fraction(-row[2], 2))
                shifted.retire()
            elif op == "QUERY":
                num = self.scratch(root[row[2]].copy())
                job = self.Job(num, self.axis_list(cols, (0,)))
                yield (op, clock, dest), job
                returned = self.fields[num]
                if row[3] == -1:
                    self.head_flip(returned, cols)
                field.scale_add(returned)
                self.retire(job)
            elif op in ("IDLE_ONE", "IDLE_ODD"):
                colors = row[2]
                coords = ((0,) if op == "IDLE_ODD" else ()) + tuple(
                    9 + 8 * c + j for c in colors for j in range(8)
                )
                num = self.scratch(field)
                yield (op, clock, dest), self.Job(num, self.axis_list(cols, coords))
                returned = self.fields.pop(num)
                if returned is not field:
                    field.replace(returned)
                if op == "IDLE_ODD" and row[3] == -1:
                    self.head_flip(field, cols)
            else:
                raise ValueError("Unknown true caller opcode")
        # Transfers to the external owners use separately staged full fields.
        outs = [(job, root[reg].copy(), sign, route) for reg, job, sign, route in roots]
        for job, field, sign, route in outs:
            field.scale(Fraction(1, 2025))
            if sign == -1:
                self.head_flip(field, cols)
            self.unalign(field, route)
            self.fields[job.owner].replace(field)

    def graph(self, clock, call, color, regs, jobs, root, cols):
        a = self.art
        g = a.graph
        centers = tuple(range(9))
        contact_set = centers + tuple(range(9 + 8 * color, 17 + 8 * color))
        terminals, held, plans = {}, {}, {}
        for p, (natives, bound) in enumerate(zip(a.regs, regs, strict=True)):
            move, correct = a.contacts[p]
            for k, (i, reg) in enumerate(zip(natives, bound, strict=True)):
                field = root[reg].copy()
                self.chart(field, move, contact_set, cols)
                if k % 2 == 0:
                    self.chart(field, a.port[p][0], centers, cols)
                held[~i] = field
                terminals[i] = root[reg]
                plans[i] = ("main", p, k)
        for i, (before, after) in enumerate(zip(g["initial"], g["final"], strict=True)):
            if i in a.main:
                continue
            tag = ("helper", clock, call, a.layout["source_labels"][i])
            job = jobs[tag]
            field = self.fields[job.owner].copy()
            rank, right, left = a.factors[before, after]
            route = self.align(field, job, self.axis_list(cols, range(rank)))
            self.chart(field, right, centers, cols, inverse=True)
            held[~i] = field
            terminals[i] = self.fields[job.owner]
            plans[i] = ("helper", left, route)
        for field in held.values():
            field.scale(a.odd)
        sample = next(iter(held.values()))
        for node in g["schedule"]:
            value = sample.blank()
            value.clear()
            for donor, c in a.forms[node]:
                value.scale_add(held[donor], c)
            if node in a.moves:
                rank, right, left = a.factors[a.moves[node]]
                self.chart(value, right, centers, cols)
                token = self.scratch(value)
                yield (
                    ("return", clock, call, node),
                    self.Job(token, self.axis_list(cols, range(rank))),
                )
                value = self.fields.pop(token)
                self.chart(value, left, centers, cols)
            held[node] = value
        for i, dest in terminals.items():
            value = held.pop(g["first_output"] + i)
            value.scale(Fraction(1, a.odd))
            mode, arg, last = plans[i]
            if mode == "main":
                p = arg
                if last % 2:
                    self.chart(value, a.port[p][1], centers, cols)
                move, correct = a.contacts[p]
                self.chart(value, move, contact_set, cols, inverse=True)
                self.chart(value, correct, contact_set, cols)
            else:
                self.chart(value, arg, centers, cols, inverse=True)
                self.unalign(value, last)
            dest.replace(value)
        for field in held.values():
            field.retire()
