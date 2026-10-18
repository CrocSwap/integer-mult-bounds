"""Literal allocations and occupied cells over the closed adapter call."""
from types import SimpleNamespace

from oracle import need, reference


class Census:
    def __init__(self, modules, arenas, bounds):
        self.modules, self.arenas, self.bounds = modules, arenas, bounds
        self.entry = [len(a.live) for a in arenas]
        self.peak, self.scans = list(self.entry), 0
        self.zero = modules.words.Arena.zero

    def scan(self, arena):
        w = self.modules.words
        occupied = sum(c not in (w.LEFT, w.BLANK)
                       for word in (*arena.words, arena.template) for c in word.cells)
        need(occupied == (len(arena.live) + 1) * (arena.bits + 1), "literal occupied cells")
        self.scans += 1

    def allocate(self, arena):
        word = self.zero(arena)
        need(arena in self.arenas, "closed arena inventory")
        i = self.arenas.index(arena)
        live = len(arena.live)
        need(live <= self.entry[i] + self.bounds[i], "closed adapter word budget")
        if live > self.peak[i]:
            self.peak[i] = live
            if live & (live - 1) == 0 or live >= self.entry[i] + self.bounds[i] - 10:
                self.scan(arena)
        return word

    def __enter__(self):
        for arena in self.arenas:
            need(arena.template.head == 1 and all(arena.words[s].head == 1 for s in arena.live),
                 "entry numerical heads")
            self.scan(arena)
        self.modules.words.Arena.zero = lambda arena: self.allocate(arena)
        return self

    def __exit__(self, *_exception):
        self.modules.words.Arena.zero = self.zero


def fixture(modules, kind, rank, modulus, depth, branch, reverse, borrowed, history="U"):
    need(modulus in (3, 9) and 0 <= depth <= 4 and borrowed in (3, 7), "bounded fixture")
    low, plan, ref, scalar, reverse = reference(kind, rank, modulus, branch, reverse)
    w, records = modules.words, modules.records
    root_size = 64 ** (depth + 1)
    residues = w.Arena(modulus.bit_length() + 1, 65536)
    indices = w.Arena(root_size.bit_length() + 1, 256)
    mod = residues.literal(modulus)
    ring = w.Ring(mod)
    identity = tuple(tuple(int(i == j) for j in range(64)) for i in range(64))
    fallback_low = reference("fallback", 1, modulus, "shear")[0]
    specs = {0: SimpleNamespace(code=0, good=False, low=fallback_low,
                               template=SimpleNamespace(q=3, rank=1, preparation=identity))}
    code = int(kind == "good")
    if code:
        specs[code] = SimpleNamespace(code=code, good=True, low=low,
                                     template=SimpleNamespace(q=3, rank=rank, preparation=identity))
    need(history in ("U", "P"), "bounded ancestor alphabet")
    events = [(2 if history == "U" else 1, 0, 1, 0, 0, 0)] * depth
    program = records.Program.fixture(indices, residues, root_size, 2, events)
    high = [[0] * 64 for _ in range(64)]
    fields = records.Fields.fixture(indices, residues, [(0, high)] * depth + [(code, high)])
    residents = [residues.literal(i % modulus) for i in range(borrowed)]
    index_residents = [indices.literal(i) for i in range(borrowed)]
    coordinate = indices.zero()
    request = SimpleNamespace(kind="adapter", coordinate=coordinate, reference=ref,
                              reverse_adapter=reverse)
    # Unit resets give one. For these Pair headers, diagonal[0]=2 and
    # permutation[0]=0, so the identical parent weights cancel to give two.
    weight = 1 if depth and history == "U" else 2
    if kind == "fallback":
        perm = ref.permutation
        numerator = weight if perm[ref.first] < 64 else 1
        denominator = weight if perm[ref.second] < 64 else 1
        expected = scalar * numerator * pow(denominator, -1, modulus) % modulus
    else:
        expected = scalar
    if reverse:
        expected = -expected % modulus
    return SimpleNamespace(**locals())


def saved_state(case):
    return tuple({s: bytes(a.words[s].cells) for s in a.live}
                 for a in (case.residues, case.indices))


def preserved(case, saved, tapes):
    need(saved_state(case) == saved, "all borrowed values and exact live ownership")
    need((bytes(case.program.tape.cells), bytes(case.fields.tape.cells)) == tapes, "immutable input tapes")
    need(case.program.tape.head == case.fields.tape.head == 1, "restored input tape heads")
    for arena in (case.residues, case.indices):
        need(arena.template.head == 1 and all(arena.words[s].head == 1 for s in arena.live),
             "restored numerical heads")


def run_case(modules, kind, rank=1, modulus=3, depth=0, branch="head", reverse=False,
             borrowed=3, history="U", bounds=(37672, 22), repeats=1, mutate=None):
    need(repeats in (1, 2), "bounded repetitions")
    case = fixture(modules, kind, rank, modulus, depth, branch, reverse, borrowed, history)
    saved = saved_state(case)
    tapes = bytes(case.program.tape.cells), bytes(case.fields.tape.cells)
    try:
        if mutate is not None:
            mutate(case)
        with Census(modules, (case.residues, case.indices), bounds) as meter:
            for _ in range(repeats):
                result = modules.numeric.selected_coefficient(case.plan, case.ring, case.indices,
                         case.program, case.fields, case.specs, case.code, case.request)
                actual = result.inspect()
                need(actual == case.expected,
                     f"independent adapter coefficient {kind}/{rank}/{modulus}/{branch}: {actual}!={case.expected}")
                case.residues.free(result)
                preserved(case, saved, tapes)
            for arena in meter.arenas:
                meter.scan(arena)
        return {"kind": kind, "rank": rank, "modulus": modulus, "depth": depth,
                "branch": branch, "reverse": reverse, "borrowed": borrowed,
                "history": history, "repeats": repeats,
                "coefficient": case.expected, "entry": meter.entry,
                "extra": [a - b for a, b in zip(meter.peak, meter.entry, strict=True)],
                "cell_scans": meter.scans}
    finally:
        case.residues.rollback(set(saved[0]))
        case.indices.rollback(set(saved[1]))
        case.program.tape.clear()
        case.fields.tape.clear()
        case.residues.rollback(set())
        case.indices.rollback(set())
        need(not case.residues.live and not case.indices.live, "fixture erasure")


def failure_case(modules, kind, rank=1, bounds=(37672, 22), mutate=None, depth=0, history="U"):
    case = fixture(modules, kind, rank, 3, depth, "head" if kind == "good" else "shear",
                   False, 3, history)
    saved = saved_state(case)
    tapes = bytes(case.program.tape.cells), bytes(case.fields.tape.cells)
    try:
        if mutate is not None:
            mutate(case)
        failed = False
        with Census(modules, (case.residues, case.indices), bounds):
            try:
                modules.numeric.selected_coefficient(case.plan, case.ring, case.indices,
                    case.program, case.fields, case.specs, case.code, case.request)
            except ValueError:
                failed = True
        need(failed, "actual source must reject")
        # This is before fixture teardown. It checks the source wrapper's own
        # rollback, including failures before selected_page returns its tuple.
        preserved(case, saved, tapes)
    finally:
        case.residues.rollback(set())
        case.indices.rollback(set())
        case.program.tape.clear()
        case.fields.tape.clear()
