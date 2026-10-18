"""Literal four-symbol tape controllers; no transition sees a tape position.

Prepared for commdata2338, with substantial OpenAI Codex assistance.
Apache-2.0. Push/pop tables are read from the credited, pinned Lean sources.
Python dictionaries and trace instrumentation implement the *simulator*, not
the tape machine's cost model. Only table transitions and dispatch are charged.
"""
from dataclasses import dataclass, field
from itertools import product
import re


BLANK, SEP, ZERO, ONE = "_", "|", "0", "1"
SYMBOLS = (BLANK, SEP, ZERO, ONE)
BIT = (ZERO, ONE)
PUSH_MODES = ("copy", "rewind", "done")
POP_MODES = ("enterDelimiter", "enterPayload", "copyPark", "copyOutput",
             "rewindOutput", "done")
STAY = (None, 0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def split_tuple(text):
    require(text.startswith("⟨") and text.endswith("⟩"), "unsupported Lean tuple")
    pieces, start, depth = [], 1, 0
    for i, char in enumerate(text[1:-1], 1):
        if char in "⟨({":
            depth += 1
        elif char in "⟩)}":
            depth -= 1
        elif char == "," and depth == 0:
            pieces.append(text[start:i].strip())
            start = i + 1
        require(depth >= 0, "unbalanced Lean tuple")
    require(depth == 0, "unbalanced Lean tuple")
    pieces.append(text[start:-1].strip())
    return pieces


def parse_action(text, bit):
    if text == "{}":
        return STAY
    write, move = split_tuple(text)
    writes = {"none": None, "some .blank": BLANK, "some .separator": SEP,
              "some (.bit b)": bit}
    moves = {".stay": 0, ".left": -1, ".right": 1}
    require(write in writes and move in moves, "unsupported Lean action")
    require(write != "some (.bit b)" or bit in BIT, "unbound Lean bit")
    return writes[write], moves[move]


def parse_instruction_table(source, modes, arguments, tape_count):
    """Parse precisely the small literal-match grammar in the two source tables.

    Reject unknown syntax, missing/duplicate arms, and incomplete tables. This
    is a source extractor, not a Lean elaborator or a kernel proof checker.
    """
    require(source.count("def instruction (") == 1, "ambiguous instruction source")
    body = source.split("def instruction (", 1)[1].split("\ndef machineStep", 1)[0]
    require(body.count(":=\n") == 1, "unsupported instruction header")
    header, body = body.split(":=\n", 1)
    require(": Instruction" in header, "wrong instruction return type")
    cases, mode, target = {}, None, None
    for line in body.splitlines():
        if not line.strip() or line.strip() == "match mode with":
            continue
        arm = re.fullmatch(r"( +)\| \.([A-Za-z]+)(?: (b|_))? => (.+)", line)
        require(arm is not None, "unsupported instruction syntax: " + line)
        indent, tag, variable, rhs = arm.groups()
        if len(indent) == 2:
            require(tag in modes and tag not in cases and variable is None,
                    "unknown or duplicate mode")
            mode = tag
            if rhs.startswith("match "):
                target = rhs.removeprefix("match ").removesuffix(" with")
                require(rhs == f"match {target} with" and target in arguments,
                        "unknown matched argument")
                cases[mode] = (target, {})
            else:
                target = None
                cases[mode] = (None, rhs)
        else:
            require(len(indent) == 6 and mode is not None and target is not None,
                    "unexpected nested match")
            require(tag in ("bit", "blank", "separator"), "unknown symbol pattern")
            require((tag == "bit") == (variable in ("b", "_")), "bad bit pattern")
            branches = cases[mode][1]
            require(tag not in branches, "duplicate symbol pattern")
            branches[tag] = rhs
    require(set(cases) == set(modes), "incomplete mode inventory")
    table = {}
    for mode in modes:
        target, branches = cases[mode]
        if target is not None:
            require(set(branches) == {"bit", "blank", "separator"},
                    "incomplete symbol inventory")
        for symbols in product(SYMBOLS, repeat=len(arguments)):
            bit = None
            if target is None:
                rhs = branches
            else:
                symbol = symbols[arguments.index(target)]
                tag = "bit" if symbol in BIT else "blank" if symbol == BLANK else "separator"
                rhs = branches[tag]
                bit = symbol if symbol in BIT else None
            parts = split_tuple(rhs)
            next_mode = parts[0].removeprefix(".")
            require(parts[0] == "." + next_mode and next_mode in modes,
                    "unknown destination mode")
            require(len(parts) == tape_count + 1, "wrong tape arity")
            table[(mode, *symbols)] = (next_mode, tuple(parse_action(p, bit) for p in parts[1:]))
    return table


def reference_push(mode, source):
    """Separately transcribed rules, compared with every extracted table row."""
    if mode == "copy" and source in BIT:
        return "copy", ((BLANK, 1), (source, 1))
    if mode == "copy" and source == BLANK:
        return "rewind", ((None, -1), (SEP, 1))
    if mode == "rewind" and source == BLANK:
        return "rewind", ((None, -1), STAY)
    if mode == "rewind" and source == SEP:
        return "done", ((None, 1), STAY)
    return "done", (STAY, STAY)


def reference_pop(mode, park, temp, out):
    if mode == "enterDelimiter":
        return "enterPayload", ((None, -1), STAY, STAY)
    if mode == "enterPayload":
        return "copyPark", ((BLANK, -1), STAY, STAY)
    if mode == "copyPark" and park in BIT:
        return mode, ((BLANK, -1), (park, 1), STAY)
    if mode == "copyPark" and park == SEP:
        return "copyOutput", ((None, 1), (None, -1), STAY)
    if mode == "copyOutput" and temp in BIT:
        return mode, (STAY, (BLANK, -1), (temp, 1))
    if mode == "copyOutput" and temp == SEP:
        return "rewindOutput", (STAY, (None, 1), (None, -1))
    if mode == "rewindOutput" and out in BIT:
        return mode, (STAY, STAY, (None, -1))
    if mode == "rewindOutput" and out == SEP:
        return "done", (STAY, STAY, (None, 1))
    return "done", (STAY, STAY, STAY)


def move_instruction(mode, source, destination):
    """Move a marked stream into empty marked work; return both heads to zero."""
    if mode == "copy":
        if source in BIT and destination == BLANK:
            return mode, ((BLANK, 1), (source, 1))
        if source == destination == BLANK:
            return "rewind", ((None, -1), (None, -1))
    elif mode == "rewind":
        if source == BLANK and destination in BIT:
            return mode, ((None, -1), (None, -1))
        if source == destination == SEP:
            return "done", ((None, 1), (None, 1))
    elif mode == "done":
        return mode, (STAY, STAY)
    raise ValueError("move interface violation")


@dataclass
class Tape:
    cells: dict = field(default_factory=dict)
    head: int = 0
    # Diagnostics: these do not occur in the finite-control transition rules.
    visits: list = field(default_factory=list)
    writes: list = field(default_factory=list)

    @classmethod
    def marked(cls, bits=()):
        require(all(b in BIT for b in bits), "nonbit payload")
        return cls({-1: SEP, **dict(enumerate(bits))})

    @classmethod
    def stack(cls, ancestor=(), origin=0):
        require(all(s in SYMBOLS for s in ancestor), "unknown ancestor symbol")
        cells = {origin - 1: SEP}
        cells.update({origin - 2 - i: s for i, s in enumerate(ancestor) if s != BLANK})
        return cls(cells, origin)

    def read(self):
        self.visits.append(self.head)
        return self.cells.get(self.head, BLANK)

    def perform(self, action):
        symbol, delta = action
        require(delta in (-1, 0, 1), "nonunit move")
        if symbol is not None:
            require(symbol in SYMBOLS, "unknown written symbol")
            self.writes.append(self.head)
            if symbol == BLANK:
                self.cells.pop(self.head, None)
            else:
                self.cells[self.head] = symbol
        self.head += delta
        # Include a final moved-to head even if the next phase does not read it.
        self.visits.append(self.head)

    def snapshot(self):
        return self.head, tuple(sorted(self.cells.items()))

    def bits(self):
        require(self.head == 0 and self.cells.get(-1) == SEP, "bad marked origin")
        require(all(k >= -1 for k in self.cells), "unexpected work exterior")
        length = max(self.cells) + 1
        result = tuple(self.cells.get(i, BLANK) for i in range(length))
        require(all(b in BIT for b in result), "noncontiguous bit payload")
        return result


def run_table(table, mode, tapes, observed, max_steps=None):
    count = 0
    while mode != "done":
        require(max_steps is None or count < max_steps, "primitive did not halt within test cap")
        symbols = tuple(t.read() for t in tapes)
        mode, actions = table[(mode, *(symbols[i] for i in observed))]
        for tape, action in zip(tapes, actions, strict=True):
            tape.perform(action)
        count += 1
    return count


def run_move(source, destination, max_steps=None):
    mode, count = "copy", 0
    while mode != "done":
        require(max_steps is None or count < max_steps, "move did not halt within test cap")
        mode, actions = move_instruction(mode, source.read(), destination.read())
        source.perform(actions[0])
        destination.perform(actions[1])
        count += 1
    return count


@dataclass
class Workspace:
    roles: list
    parking: Tape
    io: Tape = field(default_factory=Tape.marked)
    temporary: Tape = field(default_factory=Tape.marked)


def invoice(lengths, active):
    require(len(lengths) >= 2 and 0 <= active < len(lengths), "invalid fixed role set")
    require(all(n >= 0 for n in lengths), "negative length")
    return 5 * sum(lengths) - lengths[active] + 9 * len(lengths) - 2


def boundary_program(width, active):
    """Compile-time finite phase list; independent of all tape data and sizes.

    A phase state is its literal list index together with the primitive mode.
    Each done mode makes one stationary transition to the next phase; the
    child's done mode does the same. The final dispatch enters wrapper done.
    """
    require(width >= 2 and 0 <= active < width, "invalid fixed role set")
    inactive = tuple(i for i in range(width) if i != active)
    return (tuple(("push", i) for i in inactive) +
            (("move_in", active), ("child", active), ("move_out", active)) +
            tuple(("pop", i) for i in reversed(inactive)))


def boundary(work, active, child, push, pop, *, check_contract=True,
             restore_in_push_order=False):
    """One finite fixed-W boundary, with a child callback standing for a machine.

    Each completed primitive costs one dispatch transition; child return costs
    one more. A concrete fixed W/active choice specializes the finite register
    selectors. Diagnostics/contract comparisons are external test instrumentation.
    The callback's own transitions are excluded from this wrapper's invoice.
    """
    count, dispatch = 0, 0
    program = boundary_program(len(work.roles), active)
    if restore_in_push_order:  # Deliberate mutation used by a negative control.
        before, pops = program[:len(work.roles) + 2], program[len(work.roles) + 2:]
        program = before + tuple(reversed(pops))
    if check_contract:
        require(work.io.bits() == work.temporary.bits() == (), "unclean entry work")
    for phase, i in program:
        if phase == "push":
            count += run_table(push, "copy", [work.roles[i], work.parking], (0,))
        elif phase == "move_in":
            count += run_move(work.roles[i], work.io)
        elif phase == "child":
            if check_contract:
                require(all(t.bits() == () for t in work.roles), "child entry roles not empty")
                parked = work.parking.snapshot()
                child_length = len(work.io.bits())
            child(work)
            if check_contract:
                require(work.parking.snapshot() == parked, "child changed parking contents/head")
                require(all(t.bits() == () for t in work.roles), "child left dirty role work")
                require(work.temporary.bits() == (), "child left dirty temporary")
                require(len(work.io.bits()) == child_length, "child changed active length")
        elif phase == "move_out":
            count += run_move(work.io, work.roles[i])
        elif phase == "pop":
            count += run_table(pop, "enterDelimiter",
                               [work.parking, work.temporary, work.roles[i]], (0, 1, 2))
        else:
            raise ValueError("unknown compiled phase")
        # One explicit stationary control transition per completed phase.
        dispatch += 1
    return {"primitive": count, "dispatch": dispatch, "total": count + dispatch}


def flip_child(work):
    """Literal two-mode length-preserving child; does not access parking/work."""
    mode = "forward"
    while mode != "done":
        symbol = work.io.read()
        if mode == "forward" and symbol in BIT:
            work.io.perform((ONE if symbol == ZERO else ZERO, 1))
        elif mode == "forward" and symbol == BLANK:
            work.io.perform((None, -1))
            mode = "back"
        elif mode == "back" and symbol in BIT:
            work.io.perform((None, -1))
        elif mode == "back" and symbol == SEP:
            work.io.perform((None, 1))
            mode = "done"
        else:
            raise ValueError("flip child interface violation")
