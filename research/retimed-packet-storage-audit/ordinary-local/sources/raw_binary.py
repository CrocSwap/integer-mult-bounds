"""Run the archived 36-call binary source program on fixed-head owner storage."""

from dataclasses import dataclass
from functools import cache
from itertools import chain

from compiler_cut import low_size, source_graph
from factored_frames import Frame, coordinate_word, inverse_word
from periodic import Job
from streaming_routes import CHUNK, copy_bytes, read_exact, right_route, work_tapes, write_zeros
from tagged_sources import BIT_CALLER, BIT_PIN, packed, pinned
from ternary_frames import frame_at_three, projector, transpose
from vendor.cover import row_program


@dataclass(frozen=True)
class Axis:
    basis: tuple
    column: int


def placed_job(owner, frame):
    return Job(owner, tuple(Axis(frame.word, i) for i in frame.mask))


def job_frame(job, dimension):
    first = job.axes[0]
    if isinstance(first, int):
        return Frame(dimension, (), job.axes)
    if any(axis.basis is not first.basis and axis.basis != first.basis for axis in job.axes):
        raise ValueError("The active coordinates must have one ordered whole basis")
    return Frame(dimension, first.basis, tuple(axis.column for axis in job.axes))


class Banks:
    """Keep equal-sized arbitrary fields on one backing tape and reuse retired extents."""

    def __init__(self, tape, dimension, chart_digits, groups, suffix_bytes, previous_swap):
        self.tape = tape
        self.dimension = dimension
        self.digits = chart_digits
        self.groups = groups
        self.suffix = suffix_bytes
        self.volume = (
            groups * low_size(dimension) * 3 ** ((chart_digits - 1) * dimension**2) * suffix_bytes
        )
        self.previous_swap = previous_swap
        self.capacity = 0
        self.vacant = []
        self.live = set()

    def start(self, owner):
        if owner not in self.live:
            raise ValueError("The instruction refers to a retired owner")
        self.tape.seek(owner * self.volume)

    def zero(self):
        if self.vacant:
            owner = self.vacant.pop()
        else:
            owner = self.capacity
            self.capacity += 1
        self.live.add(owner)
        self.start(owner)
        write_zeros(self.tape, self.volume)
        return owner

    def read(self, owner, target):
        self.start(owner)
        copy_bytes(self.tape, target, self.volume)

    def install(self, owner, source):
        self.start(owner)
        copy_bytes(source, self.tape, self.volume)

    def retire(self, owner, *, require_zero=False):
        self.start(owner)
        if require_zero:
            remaining = self.volume
            while remaining:
                size = min(CHUNK, remaining)
                if any(read_exact(self.tape, size)):
                    raise ArithmeticError("A private zero output contains data")
                remaining -= size
            self.start(owner)
        write_zeros(self.tape, self.volume)
        self.live.remove(owner)
        self.vacant.append(owner)

    def clone(self, owner):
        out = self.zero()
        with work_tapes(1) as (tape,):
            self.read(owner, tape)
            tape.seek(0)
            self.install(out, tape)
        return out

    def swap(self, left, right):
        with work_tapes(2) as (a, b):
            self.read(left, a)
            self.read(right, b)
            a.seek(0)
            b.seek(0)
            self.install(right, a)
            self.install(left, b)

    def xor(self, dest, source):
        with work_tapes(2) as (donor, old):
            self.read(source, donor)
            self.read(dest, old)
            donor.seek(0)
            old.seek(0)
            self.start(dest)
            remaining = self.volume
            while remaining:
                count = min(CHUNK, remaining)
                a, b = read_exact(old, count), read_exact(donor, count)
                self.tape.write(bytes(x ^ y for x, y in zip(a, b, strict=True)))
                remaining -= count

    def route(self, owner, word):
        with work_tapes(1) as (out,):
            self.start(owner)
            right_route(
                self.tape,
                out,
                self.dimension,
                self.digits,
                self.groups,
                self.suffix,
                word,
                previous_swap=self.previous_swap,
            )
            out.seek(0)
            self.install(owner, out)


class Catalogue:
    def __init__(self, dimension, columns):
        self.dimension = dimension
        self.columns = columns
        self.graph = source_graph()
        self.root = packed(pinned(BIT_CALLER, BIT_PIN))
        self.ports = self.root["ports"]
        self.body = self.root["body_rank"]
        self.ambient = 1 + self.body + self.body * self.root["stages"]
        if self.ambient * columns > dimension or columns < 1:
            raise ValueError("The complete source ambient and its columns must fit the frame")

        for name in (
            "raw_projector",
            "difference",
            "joint",
            "target",
            "head",
            "idle",
            "port_stage",
        ):
            setattr(self, name, cache(getattr(self, name)))

    def raw_projector(self, index):
        spec = self.graph["frames"][str(index)]
        return projector(transpose(spec["B"] + spec["A"]), spec["dim"])

    def extend(self, word, mask):
        f = self.columns
        lifted = []
        for op in word:
            for j in range(f):
                lifted.extend(coordinate_word((op,), lambda k: k * f + j))
        return Frame(
            self.dimension, tuple(lifted), tuple(i * f + j for i in mask for j in range(f))
        )

    def difference(self, first, last):
        frames = self.graph["frames"]
        if frames[str(first)]["dim"] > frames[str(last)]["dim"]:
            return self.difference(last, first)
        a, b = self.raw_projector(first), self.raw_projector(last)
        delta = [
            [y - x for x, y in zip(left, right, strict=True)]
            for left, right in zip(a, b, strict=True)
        ]
        basis, rank = frame_at_three(delta)
        return self.extend(row_program(basis, 3), range(rank))

    def joint(self, port):
        frames = self.graph["frames"]
        h = frames[str(self.graph["start"][port])]
        body = frames[str(self.graph["final"][self.ports + port])]
        return row_program(transpose(h["B"] + body["B"]), 3)

    def body_axes(self, stages):
        for stage in stages:
            yield from range(1 + self.body * stage, 1 + self.body * (stage + 1))

    def target(self, tag):
        kind, role, port = tag
        if kind == "root":
            stages = self.root["diagonal"][role]["stages"]
            return self.extend(self.joint(port), (0, *self.body_axes(stages)))
        if kind == "helper":
            return self.difference(self.graph["start"][port], self.graph["final"][port])
        raise ValueError("Unknown raw productive role")

    def head(self, port):
        return self.extend(self.joint(port), (0,))

    def idle(self, stages):
        return self.extend((), self.body_axes(stages))

    def port_stage(self, port, stage):
        basis = self.joint(port)
        swaps = (("swap", j + 1, dest) for j, dest in enumerate(self.body_axes((stage,))))
        word = tuple(chain(basis, swaps, inverse_word(basis)))
        return self.extend(word, ()).word


@cache
def raw_catalogue(dimension, columns):
    return Catalogue(dimension, columns)


class BinarySource:
    """Yield a paid job only after its actual owner and entrance route are ready."""

    def __init__(self, banks):
        self.banks = banks

    def fresh(self, exemplar, rank, tag):
        return Job(self.banks.zero(), tuple(range(rank)))

    def retire(self, job):
        self.banks.retire(job.owner, require_zero=True)

    def inner(self, clock, owners, catalogue):
        count = catalogue.graph["public"]
        registers = dict(enumerate(owners))
        for site, row in enumerate(catalogue.graph["program"]):
            op, dest, *args = row
            if op == "INIT":
                if dest in registers:
                    raise ValueError("The native INIT has a live destination")
                registers[dest] = self.banks.zero()
            elif op == "ADD":
                self.banks.xor(registers[dest], registers[args[0]])
            elif op == "SWAP":
                self.banks.swap(registers[dest], registers[args[0]])
            elif op == "CLEAR":
                if dest < count:
                    raise ValueError("A native private CLEAR names a public port")
                self.banks.retire(registers.pop(dest))
            elif op == "MOVE":
                frame = catalogue.difference(*args)
                yield ("move", clock, site, dest), placed_job(registers[dest], frame)
            else:
                raise ValueError("Unknown native binary opcode")
        if set(registers) != set(range(count)):
            raise ArithmeticError("The native return retained a private owner")

    def raw(self, inputs, columns):
        c = raw_catalogue(self.banks.dimension, columns)
        active, restores = {}, []
        for tag, job in inputs:
            target = c.target(tag)
            source = job_frame(job, self.banks.dimension)
            matcher = source.matcher_to(target)
            self.banks.route(job.owner, matcher)
            active[tag] = job.owner
            restores.append((job.owner, matcher))
        for clock, row in enumerate(c.root["events"]):
            op, *args = row
            if op == "LOCAL":
                stage, x, y = args
                pairs = [(active["root", x, p], active["root", y, p]) for p in range(c.ports)]
                for p, pair in enumerate(pairs):
                    matcher = c.port_stage(p, stage)
                    for owner in pair:
                        self.banks.route(owner, matcher)
                owners = (
                    [a for a, b in pairs]
                    + [b for a, b in pairs]
                    + [active["helper", clock, i] for i in range(2 * c.ports, c.graph["public"])]
                )
                yield from self.inner(clock, owners, c)
                for p, pair in enumerate(pairs):
                    back = tuple(inverse_word(c.port_stage(p, stage)))
                    for owner in pair:
                        self.banks.route(owner, back)
            elif op == "IDLE_ONE":
                x, stages = args
                frame = c.idle(tuple(stages))
                for p in range(c.ports):
                    yield (op, clock, p), placed_job(active["root", x, p], frame)
            else:
                x, y = args
                for p in range(c.ports):
                    left, right = active["root", x, p], active["root", y, p]
                    if op == "ADD":
                        self.banks.xor(left, right)
                    elif op == "SWAP":
                        self.banks.swap(left, right)
                    elif op == "QUERY":
                        borrowed = self.banks.clone(right)
                        yield (op, clock, p), placed_job(borrowed, c.head(p))
                        self.banks.xor(left, borrowed)
                        self.banks.retire(borrowed)
                    else:
                        raise ValueError("Unknown binary root opcode")
        for owner, matcher in reversed(restores):
            self.banks.route(owner, tuple(inverse_word(matcher)))
