# SPDX-License-Identifier: Apache-2.0
"""Literal source-to-event binding without importing the retained transporter/emitter.

Prepared with substantial OpenAI Codex assistance. The frozen construction and
native compiler are credited dependencies, not new constructions here.
"""
from fractions import Fraction
import json

FULL = (256, 128, 64, 32, 16, 8, 4, 2, 1)
PHASES = ("zero_frame_precondition", "entry_adapters", "A", "centers", "B",
          "cleanup_tail", "final", "exit_adapters", "full_frame_cleanup", "done")


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def identical(left, right):
    return json.dumps(left, sort_keys=True, separators=(",", ":")) == json.dumps(right, sort_keys=True, separators=(",", ":"))


def basis(vectors):
    require(type(vectors) in (list, tuple), "frame sequence")
    require(len(vectors) <= 512 and all(type(x) is int and 0 <= x < 512 for x in vectors),
            "nine-axis frame domain")
    rows = list(vectors)
    pivot = 0
    for bit in range(8, -1, -1):
        found = next((j for j in range(pivot, len(rows)) if rows[j] >> bit & 1), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        for j in range(len(rows)):
            if j != pivot and rows[j] >> bit & 1:
                rows[j] ^= rows[pivot]
        pivot += 1
    return tuple(rows[:pivot])


def role(index, kept):
    require(type(index) is int and 0 <= index < 1408, "original role domain")
    private = index >= 704
    original = index - 704 if private else index
    require(original in kept, "removed original role used")
    return ("Z" if private else "L") + str(original)


def metadata(word):
    require(word["kind"] == "BORROW-WORD", "source word kind")
    report = word["report"]
    require((report["v"], report["h"], report["R"]) == (112, 9, 480), "source domain")
    removed = word["removed"]
    require(len(removed) == len(set(removed)) == 72 and
            all(type(r) is int and 224 <= r < 704 for r in removed), "removed roles")
    kept = sorted(set(range(704)) - set(removed))
    require(len(kept) == 632 and len(word["ports"]) == 112, "kept/port domain")
    start = {"L" + str(r): () for r in kept}
    for r, port in enumerate(word["ports"]):
        start["L" + str(r)] = basis([port])
    for r, frame in word["start_extra"].items():
        start[role(int(r), kept)] = basis(frame)
    final = {"L" + str(r): FULL for r in kept}
    for t, port in enumerate(word["ports"]):
        final["L" + str(112 + t)] = basis([x for x in range(1, 512)
                                         if (x & port).bit_count() % 2 == 0])
    for r, frame in word["helper_final"].items():
        final[role(int(r), kept)] = basis(frame)
    private = {"Z" + str(r) for r in map(int, word["helper_final"])}
    require(len(private) == 91 and private == {"Z" + r[1:] for r in final
            if int(r[1:]) >= 224 and final[r] != FULL}, "private role inventory")
    return kept, start, final, private


def scalar(gate, kept, backward):
    tag = gate[0]
    require(tag in ("add", "scale"), "source scalar kind")
    require(len(gate) == (6 if tag == "add" else 5), "source scalar shape")
    if tag == "add":
        target, source = role(gate[1], kept), role(gate[2], kept)
        q = Fraction(gate[3], gate[4])
        if backward:
            target, source, q = source, target, -q
        require(target != source and q != 0, "nontrivial distinct shear")
        return [tag, target, source, q.numerator, q.denominator]
    q = Fraction(gate[2], gate[3])
    require(q != 0, "nonzero scale")
    if backward:
        q = 1 / q
    return [tag, role(gate[1], kept), q.numerator, q.denominator]


class SourceTrace:
    def __init__(self, word, backward):
        self.word, self.backward = word, backward
        self.kept, self.start, self.final, self.private = metadata(word)
        self.current = dict(self.start)
        self.events = []
        self.phase = None

    def mark(self, phase):
        self.phase = phase
        self.events.append(["phase", phase])

    def climb(self, r, frame):
        old = self.current[r]
        if old != frame:
            require(basis(old + frame) == frame and len(frame) > len(old), "source monotone climb")
            self.events.append(["climb", self.phase, r, old, frame, len(frame) - len(old)])
            self.current[r] = frame

    def warp(self, r, op, old, new):
        require(type(op) is int and op != 0, "warp signed operator")
        if r.startswith("L"):
            require(self.current[r] == old, "source warp entrance")
            self.current[r] = new
        else:
            require(r in self.private and old == new == FULL, "private warp chart")
        self.events.append(["warp", r, op, old, new])

    def gate(self, gate, allow_climb):
        if gate[0] == "warp":
            require(len(gate) in (4, 5), "source warp shape")
            old, new = (FULL, FULL) if len(gate) == 4 else (basis(gate[3]), basis(gate[4]))
            require(len(gate) != 4 or basis(gate[3]) == FULL, "cleanup warp declared FULL")
            self.warp(role(gate[1], self.kept), gate[2], old, new)
            return
        op = scalar(gate, self.kept, self.backward)
        frame = basis(gate[-1])
        registers = op[1:3] if op[0] == "add" else op[1:2]
        # Climb order follows original source operands, even in the dual stream.
        original = [role(gate[1], self.kept)]
        if gate[0] == "add":
            original.append(role(gate[2], self.kept))
        for r in original:
            if r.startswith("L"):
                if allow_climb:
                    self.climb(r, frame)
                require(self.current[r] == frame, "source scalar common chart")
            else:
                require(r in self.private and frame == FULL, "source private scalar chart")
        require(len(registers) == len(original), "orientation register arity")
        self.events.append(["scalar", op, frame])

    def zero_phase(self):
        self.mark("zero_frame_precondition")
        for term in self.word["initial_corrections"]:
            q = Fraction(term["coefficient"])
            s = role(term["source"], self.kept)
            require(self.current[s] == (), "correction source starts at zero")
            for op in reversed(term["operator_word"]):
                self.warp(s, op, (), ())
            gate = ["add", term["target"], term["source"], q.numerator, q.denominator, []]
            self.gate(gate, False)
            for op in term["operator_word"]:
                self.warp(s, -op, (), ())
        for gate in self.word["precondition"] + self.word["compensation"]:
            self.gate(gate, False)

    def entries(self):
        self.mark("entry_adapters")
        self.hpe = {r for r in self.final if int(r[1:]) >= 224 and self.final[r] != FULL}
        self.wrapped = self.hpe | {r for r in self.start if int(r[1:]) >= 224 and self.start[r]}
        for number in self.kept:
            r = "L" + str(number)
            if r in self.wrapped:
                event = ["residual_adapter", "pre", r, self.start[r]]
                self.events.append(event + ([self.final[r]] if r in self.hpe else []))
            else:
                self.events.append(["adapter", "old_to_new", r, self.start[r]])

    def centers(self):
        self.mark("centers")
        levels = {112 + int(t): basis(f) for t, f in self.word["target_levels"].items()}
        require(all(self.current["L" + str(r)] == levels.get(r, ())
                    for r in range(112, 224)), "target chart at center cut")
        for k, (center, cf) in enumerate(zip(self.word["centers"], self.word["center_frames"])):
            cf, cr = basis(cf), "C" + str(k)
            require(self.current["L" + str(center)] == cf, "center source chart")
            terms = [g for g in self.word["cut"] if g[2] == center]
            lower = {levels.get(g[1], ()) for g in terms} - {cf}
            require(len({len(f) for f in lower}) == len(lower), "center path has unique dimensions")
            path = [cf] + sorted(lower, key=len, reverse=True)
            require(all(basis(high + low) == high for high, low in zip(path, path[1:])), "nested center path")
            if self.backward:
                self.events.append(["scalar", ["clear", cr], path[-1]])
                for j in range(len(path) - 1, -1, -1):
                    for g in terms:
                        if levels.get(g[1], ()) == path[j]:
                            self.events.append(["scalar", ["add", cr, "L" + str(g[1]), g[3], g[4]], path[j]])
                    if j:
                        self.events.append(["center", cr, path[j], path[j - 1], len(path[j - 1]) - len(path[j])])
                self.events.append(["scalar", ["add", "L" + str(center), cr, -1, 1], cf])
            else:
                self.events.extend([["scalar", ["clear", cr], cf],
                                    ["scalar", ["copy", cr, "L" + str(center)], cf]])
                for j, frame in enumerate(path):
                    if j:
                        self.events.append(["center", cr, path[j - 1], frame, len(path[j - 1]) - len(frame)])
                    for g in terms:
                        if levels.get(g[1], ()) == frame:
                            self.events.append(["scalar", ["add", "L" + str(g[1]), cr, g[3], g[4]], frame])
            self.events.append(["scalar", ["clear", cr], path[-1] if not self.backward else cf])

    def main_body(self):
        self.mark("A")
        for gate in self.word["A"]:
            self.gate(gate, True)
        self.centers()
        self.mark("B")
        placed = {}
        for number, (position, lender, columns, old, new) in enumerate(self.word["warps"], 1):
            require(type(position) is int and 0 <= position <= len(self.word["B"]), "warp position")
            placed.setdefault(position, []).append((lender, number, old, new))
            require(len(columns) == 9, "warp matrix dimension")
        for position in range(len(self.word["B"]) + 1):
            for lender, number, old, new in placed.get(position, []):
                self.warp(role(lender, self.kept), number, basis(old), basis(new))
            if position < len(self.word["B"]):
                self.gate(self.word["B"][position], True)
        self.mark("cleanup_tail")
        for gate in self.word["restore"]:
            self.gate(gate, True)
        self.mark("final")
        for number in self.kept:
            r = "L" + str(number)
            self.climb(r, self.final[r])

    def finish(self):
        self.mark("exit_adapters")
        for number in self.kept:
            r = "L" + str(number)
            if r not in self.hpe:
                self.events.append(["adapter", "new_to_old", r, self.final[r]])
        self.mark("full_frame_cleanup")
        for r in sorted(self.private, key=lambda r: int(r[1:])):
            self.events.append(["zero_buffer", "alloc", r])
        for gate in self.word["cleanup"]:
            require(basis(gate[-1]) == FULL, "cleanup declared FULL chart")
            operands = gate[1:3] if gate[0] == "add" else gate[1:2]
            require(all(number >= 704 or self.final[role(number, self.kept)] == FULL
                        for number in operands), "cleanup L operand has FULL terminal chart")
            self.gate(gate, False)
        for r in sorted(self.private, key=lambda r: int(r[1:])):
            self.events.append(["zero_buffer", "free", r])
        for number in self.kept:
            r = "L" + str(number)
            if r in self.wrapped:
                event = ["residual_adapter", "post", r, self.start[r]]
                self.events.append(event + ([self.final[r]] if r in self.hpe else []))
        self.mark("done")


def expected(word, backward):
    for field in ("precondition", "compensation", "A", "cut", "B", "restore", "cleanup"):
        require(type(word[field]) is list and len(word[field]) <= 10000, "source section capacity")
    require(len(word["initial_corrections"]) <= 704 and len(word["warps"]) <= 512, "auxiliary source capacity")
    trace = SourceTrace(word, backward)
    trace.zero_phase()
    trace.entries()
    trace.main_body()
    trace.finish()
    require(len(trace.events) <= 100000, "expected event capacity")
    return trace.events


def actual_scalar(op, role_function):
    require(type(op) is list and op and op[0] in ("add", "scale", "copy", "clear"), "actual scalar kind")
    count = 2 if op[0] in ("add", "copy") else 1
    sizes = {"add": 5, "scale": 4, "copy": 3, "clear": 2}
    require(len(op) == sizes[op[0]], "actual scalar arity")
    result = [op[0], *[role_function(x) for x in op[1:1 + count]]]
    if op[0] in ("add", "scale"):
        a, b = op[-2:]
        require(type(a) is int and type(b) is int and a != 0 and b != 0, "actual rational scalar")
        q = Fraction(a, b)
        result += [q.numerator, q.denominator]
    return result


def normalized(canonical, stream, kept):
    require(len(stream) <= 100000 and len(canonical["frames"]) <= 4096, "actual event/frame capacity")
    frames = canonical["frames"]
    def f(i):
        require(type(i) is int and 0 <= i < len(frames), "actual frame ID")
        value = tuple(frames[i])
        require(value == basis(value), "actual ordered frame is canonical")
        return value
    def r(value):
        require(type(value) is list and len(value) == 2, "actual role schema")
        tag, i = value
        require(type(i) is int and tag in ("L", "Z", "C"), "actual role namespace")
        require(0 <= i < (len(kept) if tag != "C" else 112), "actual compact role range")
        return tag + str(i if tag == "C" else kept[i])
    out = []
    for event in stream:
        require(type(event) is list and event, "actual event sequence")
        tag = event[0]
        lengths = {"phase": (2,), "scalar": (3,), "climb": (6,), "center": (5,),
                   "warp": (5,), "adapter": (4,), "residual_adapter": (4, 5), "zero_buffer": (3,)}
        require(tag in lengths and len(event) in lengths[tag], "actual event shape")
        if tag == "phase":
            require(len(event) == 2 and event[1] in PHASES, "actual phase")
            out.append(event)
        elif tag == "scalar":
            out.append([tag, actual_scalar(event[1], r), f(event[2])])
        elif tag == "climb":
            require(type(event[5]) is int, "actual climb rank type")
            out.append([tag, event[1], r(["L", event[2]]), f(event[3]), f(event[4]), event[5]])
        elif tag == "center":
            require(type(event[4]) is int, "actual center rank type")
            out.append([tag, r(["C", event[1]]), f(event[2]), f(event[3]), event[4]])
        elif tag == "warp":
            require(type(event[2]) is int and event[2] != 0, "actual warp operator type")
            out.append([tag, r(event[1]), event[2], f(event[3]), f(event[4])])
        elif tag in ("adapter", "residual_adapter"):
            out.append([tag, event[1], r(["L", event[2]]), *[f(x) for x in event[3:]]])
        elif tag == "zero_buffer":
            out.append([tag, event[1], r(["Z", event[2]])])
        else:
            raise ValueError("unknown actual event tag")
    return out


def bind_metadata(word, canonical):
    kept, start, final, private = metadata(word)
    require(canonical["h"] == 9 and canonical["v"] == 112 and canonical["R"] == 408, "canonical domain")
    require(canonical["helper_origin"] == kept[224:], "literal role compaction")
    frames = canonical["frames"]
    def frame(index):
        require(type(index) is int and 0 <= index < len(frames), "metadata frame ID")
        result = tuple(frames[index])
        require(result == basis(result), "metadata ordered frame")
        return result
    require(canonical["ports"] == word["ports"], "source-bound ports")
    require([frame(i) for i in canonical["start"]] == [start["L" + str(r)] for r in kept], "source-bound entrance frames")
    require([frame(i) for i in canonical["final"]] == [final["L" + str(r)] for r in kept], "source-bound terminal frames")
    require(["Z" + str(kept[r]) for r in canonical["zero_buffers"]] == sorted(private, key=lambda r: int(r[1:])), "source-bound zero buffers")
    require([kept[r] for r in canonical["centers"]] == word["centers"], "source-bound centers")
    require([frame(f) for f in canonical["center_frames"]] == [basis(f) for f in word["center_frames"]], "source-bound center frames")
    require({k: frame(v) for k, v in canonical["target_levels"].items()} ==
            {k: basis(v) for k, v in word["target_levels"].items()}, "source-bound target levels")
    require(len(canonical["warps"]) == len(word["warps"]), "complete source warp table")
    for number, ((position, lender, columns, old, new), row) in enumerate(zip(word["warps"], canonical["warps"]), 1):
        require(all(type(x) is int for x in columns) and len(columns) == 9 and len(basis(columns)) == 9, "invertible source warp")
        actual = [row["op"], row["B_pos"], kept[row["lender"]], row["G_columns"], frame(row["from_frame"]), frame(row["to_frame"])]
        require(identical(actual, [number, position, lender, columns, basis(old), basis(new)]), "source-bound warp matrix/operator")
    return kept, start, final, private


def bind(word, canonical, stream, backward):
    kept, start, final, private = bind_metadata(word, canonical)
    actual = normalized(canonical, stream, kept)
    reference = expected(word, backward)
    require(len(actual) == len(reference), "complete source event count")
    for i, (left, right) in enumerate(zip(actual, reference)):
        require(identical(left, right), "complete source event mismatch at " + str(i))
    return actual, {"kept": kept, "start": start, "final": final, "private": private}
