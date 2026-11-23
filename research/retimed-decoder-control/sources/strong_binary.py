"""Run the 111-port binary source on the retained physical bank machine.

The catalogue initialization and the outer 36-call interpreter use the
construction of PR 7914. The inner MOVE, ADD, SWAP, INIT and CLEAR interpreter
and the complete chart constructors come from that package.
"""

from functools import cache
from hashlib import sha256
from pathlib import Path

from factored_frames import inverse_word
from powered import PoweredWord
from raw_binary import BinarySource, Catalogue, job_frame, placed_job
from tagged_sources import BIT_CALLER, BIT_PIN, binary_ports, packed, pinned


SOURCE_SHA256 = "74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326"


@cache
def graph():
    data = Path(__file__).with_name("strong-bit.json.gz").read_bytes()
    if sha256(data).hexdigest() != SOURCE_SHA256:
        raise ValueError("The 111-port binary source differs")
    return packed(data)


@cache
def caller():
    return packed(pinned(BIT_CALLER, BIT_PIN))


@cache
def native_word(power=128):
    if power not in (128, 228, 268, 285):
        raise ValueError("Select a certified binary power")
    raw = binary_ports(graph(), caller())
    floor = 16 if power == 128 else 15
    return PoweredWord(raw.ambient, raw.targets, raw.paid, power, floor, 12, 12)


class ActiveCatalogue(Catalogue):
    def __init__(self, dimension, columns):
        self.dimension = dimension
        self.columns = columns
        self.graph = graph()
        self.root = caller()
        self.ports = self.root["ports"]
        self.body = self.root["body_rank"]
        self.ambient = 1 + self.body + self.body * self.root["stages"]
        if self.ambient * columns > dimension or columns < 1:
            raise ValueError("The complete source ambient and its columns must fit the frame")


    def difference(self, first, last):
        frames = self.graph["frames"]
        if frames[str(first)]["dim"] > frames[str(last)]["dim"]:
            first, last = last, first
        word, rank = fixed_binary_charts()[0][first, last]
        return self.extend(word, range(rank))

    def joint(self, port):
        return fixed_binary_charts()[1][port]


@cache
def fixed_binary_charts():
    """Compile the eight-coordinate forms once. Lift them only on a real field."""
    from ternary_frames import frame_at_three, projector, transpose
    from vendor.cover import row_program

    data, root = graph(), caller()
    frames, starts, ends = data["frames"], data["start"], data["final"]
    projectors = {int(i): projector(transpose(f["B"] + f["A"]), f["dim"])
                  for i, f in frames.items()}
    ports = root["ports"]
    pairs = {tuple(row[2:]) for row in data["program"] if row[0] == "MOVE"}
    pairs.update(zip(starts[2*ports:], ends[2*ports:], strict=True))
    differences = {}
    for i, j in sorted(pairs):
        if frames[str(i)]["dim"] > frames[str(j)]["dim"]:
            i, j = j, i
        if (i, j) in differences:
            continue
        delta = [[y-x for x,y in zip(left,right,strict=True)]
                 for left,right in zip(projectors[i],projectors[j],strict=True)]
        basis, rank = frame_at_three(delta)
        differences[i,j] = tuple(row_program(basis,3)),rank
    joint = tuple(tuple(row_program(transpose(frames[str(starts[i])]["B"]
                  + frames[str(ends[ports+i])]["B"]),3)) for i in range(ports))
    return differences, joint


def active_catalogue(dimension, columns):
    return ActiveCatalogue(dimension, columns)


class StrongBinarySource(BinarySource):
    """Use the same literal graph for the paid jobs, true charts and owner program."""

    def raw(self, inputs, columns):
        c = active_catalogue(self.banks.dimension, columns)
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
