"""Bind the selected PR4610 local provider to exact native circuits.

The source word and recipes are data. No source evaluator is imported.
Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path

from check_witness import need
from quadratic import inverse_circuit, rank

HERE = Path(__file__).resolve().parent
N, D, PERSISTENT, OWNED = 9, 512, 632, 632


def read_inputs():
    manifest = json.loads((HERE / "provider/SOURCES.json").read_bytes())
    objects = {}
    for item in manifest["inputs"]:
        raw = (HERE / "provider" / item["file"]).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == item["sha256"], "Provider source bytes: " + item["file"])
        payload = gzip.decompress(raw) if item["file"].endswith(".gz") else raw
        objects[item["name"]] = ([json.loads(line) for line in payload.splitlines()]
                                 if ".jsonl" in item["file"] else json.loads(payload))
    return manifest, objects


def transpose(rows):
    return [sum(((row >> j) & 1) << k for k, row in enumerate(rows)) for j in range(N)]


def inverse(rows):
    work = [v | (1 << (N+j)) for j, v in enumerate(rows)]
    for j in range(N):
        pivot = next((k for k in range(j, N) if work[k] >> j & 1), None)
        need(pivot is not None, "Invertible native address map")
        work[j], work[pivot] = work[pivot], work[j]
        for k in range(N):
            if k != j and work[k] >> j & 1:
                work[k] ^= work[j]
    return [v >> N for v in work]


def native_map(columns):
    rows = transpose(columns)
    inverse_columns = transpose(inverse(rows))
    quadratic = [(1 << j) ^ sum(((a & b).bit_count() % 2) << k
                                for k, b in enumerate(inverse_columns))
                 for j, a in enumerate(inverse_columns)]
    return [["P", rows], ["D", quadratic, [(quadratic[j] >> j) & 1 for j in range(N)]]]


def conjugate(circuit):
    out = []
    for gate in circuit:
        if gate[0] == "D":
            out.append(["D", gate[1], [(-a) % 4 for a in gate[2]]])
        elif gate[0] in ("C", "phase"):
            out.append(list(gate[:-1]) + [-gate[-1]])
        else:
            out.append(gate)
    return out


def normalizer(rec):
    need(set(rec) == {"matrix_rows", "quadratic_rows", "linear_Z4", "offset", "phase"},
         "Complete monomial recipe")
    need(type(rec["phase"]) is int and 0 <= rec["phase"] < 4, "Canonical native phase")
    return [["D", rec["quadratic_rows"], rec["linear_Z4"]],
            ["P", rec["matrix_rows"]], ["X", rec["offset"]], ["phase", rec["phase"]]]


def recipe(rec):
    need(set(rec) == {"left", "right", "rank"}, "Complete paid recipe")
    r = rec["rank"]
    need(type(r) is int and 0 <= r <= N, "Recipe rank")
    if not r:
        need(rec["right"] is None, "Rank-zero recipe shape")
        return normalizer(rec["left"])
    return normalizer(rec["right"]) + [["C", 1 << j, 1] for j in range(r)] + normalizer(rec["left"])


class Provider:
    def __init__(self, word):
        self.word = word
        self.c = word["canonical"]
        c = self.c
        need(c["h"] == N and c["v"] == 112 and len(c["start"]) == len(c["final"]) == PERSISTENT,
             "Complete selected local boundary")
        need(set(word["programs"]) == {"forward", "backward"}, "Both provider directions")
        need(all(len(u) <= N and all(type(x) is int and 0 < x < D for x in u)
                 and rank(u) == len(u) for u in c["frames"]), "Independent native frame bases")
        self.maps = {row["op"]: native_map(row["G_columns"]) for row in c["warps"]}
        need(set(self.maps) == set(range(1, 73)) and len(c["warps"]) == 72, "All 72 native maps")

    @lru_cache(None)
    def frame(self, index):
        basis = self.c["frames"][index]
        r = len(basis)
        if not r:
            return []
        if r == N:
            return [["C", 1 << j, 1] for j in range(N)]
        extended = []
        for v in basis + [1 << j for j in range(N)]:
            if rank(extended + [v]) > len(extended):
                extended.append(v)
        change = native_map(extended)
        return inverse_circuit(N, change) + [["C", 1 << j, 1] for j in range(r)] + change

    def edge(self, a, b, direction):
        circuit = inverse_circuit(N, self.frame(a)) + self.frame(b)
        return conjugate(circuit) if direction == "backward" else circuit

    def warp(self, signed, a, b, direction):
        middle = self.maps[abs(signed)]
        if signed < 0:
            middle = inverse_circuit(N, middle)
        circuit = inverse_circuit(N, self.frame(a)) + middle + self.frame(b)
        return conjugate(circuit) if direction == "backward" else circuit

    def old_frame(self, role, entrance):
        if role >= 224:
            return self.frame(self.c["start" if entrance else "final"][role])
        if entrance:
            return [["C", self.c["ports"][role], 1]] if role < 112 else []
        return self.frame(1) if role < 112 else [["C", self.c["ports"][role-112], -1]] + self.frame(1)

    def audit_word(self, direction):
        """Check every event, frame contact, owned lifetime and paid charge."""
        c, program = self.c, self.word["programs"][direction]
        current = list(c["start"]) + [None]
        live, paid, counts, adapters, pairs, warps = False, Counter(), Counter(), {}, {}, set()
        contacts = {r: [] for r in range(224)}
        for j, event in enumerate(program):
            kind = event[0]
            counts[kind] += 1
            if kind in ("climb", "center"):
                if kind == "climb":
                    _, _, target, a, b, r = event
                    need(0 <= target < PERSISTENT and not live, "Persistent climb at a closed owned cut")
                    need(len(c["frames"][b]) > len(c["frames"][a]), "Ascending persistent edge")
                else:
                    _, target, a, b, r = event
                    need(target == 0 and live, "Live owned center")
                    target = OWNED
                u, v = c["frames"][a], c["frames"][b]
                need(current[target] == a and r == abs(len(u)-len(v)) > 0
                     and rank(u+v) == max(len(u), len(v)), "Chronological nested paid edge")
                current[target] = b
                if target < 224:
                    contacts[target].append(j)
                paid[r] += 1
                pairs[a, b] = r
            elif kind == "warp":
                _, register, signed, a, b = event
                target = role(register)
                if target < 224:
                    contacts[target].append(j)
                need(current[target] == a and abs(signed) in self.maps, "Chronological signed warp")
                rows = transpose(next(row["G_columns"] for row in c["warps"] if row["op"] == abs(signed)))
                if signed < 0:
                    rows = inverse(rows)
                mapped = [sum(((v & row).bit_count() % 2) << k for k, row in enumerate(rows))
                          for v in c["frames"][a]]
                need(rank(mapped+c["frames"][b]) == len(mapped) == len(c["frames"][b]),
                     "Actual signed warp transports its source subspace")
                current[target] = b
                warps.add((signed, a, b))
            elif kind == "scalar":
                gate, f = event[1:]
                target = role(gate[1])
                if target < 224:
                    contacts[target].append(j)
                op = gate[0]
                if op in ("clear", "copy"):
                    need(target == OWNED, "Only owned storage can be overwritten")
                if op == "clear":
                    live = False
                    current[target] = f
                    continue
                need(current[target] == f, "Scalar receiver frame")
                if op in ("add", "copy"):
                    source = role(gate[2])
                    if source < 224:
                        contacts[source].append(j)
                    need(source != target and current[source] == f, "Scalar source frame")
                    need(source != OWNED or live, "Owned source is initialized")
                    if op == "copy":
                        need(not live, "Copy starts an owned lifetime")
                        live = True
                    else:
                        q = Q(gate[3], gate[4])
                        need(q and q.denominator & (q.denominator-1) == 0, "Nonzero dyadic shear")
                        if target == OWNED:
                            live = True
                else:
                    need(op == "scale", "Known scalar operation")
                    q = Q(gate[2], gate[3])
                    a = abs(q.numerator)
                    need(a and a & (a-1) == 0 and q.denominator & (q.denominator-1) == 0,
                         "Invertible dyadic scale")
            elif kind == "adapter":
                _, side, target, f = event
                need(0 <= target < 224 and side in ("old_to_new", "new_to_old"), "Main adapter domain")
                entrance = side == "old_to_new"
                need(f == c["start" if entrance else "final"][target], "Exact main adapter boundary")
                need(current[target] == f or self.old_frame(target, entrance) == self.frame(f),
                     "A moved adapter must be exactly the identity")
                need((side, target) not in adapters, "No repeated main adapter")
                adapters[side, target] = j
            else:
                need(kind == "phase", "Known provider event")
        need(not live and current[:PERSISTENT] == c["final"], "Complete final frame and owned return")
        need(set(adapters) == {(side, r) for side in ("old_to_new", "new_to_old") for r in range(224)},
             "All 448 main adapter events")
        for (side, target), position in adapters.items():
            entrance = side == "old_to_new"
            f = c["start" if entrance else "final"][target]
            if self.old_frame(target, entrance) != self.frame(f):
                need(all(position < j if entrance else j < position for j in contacts[target]),
                     "Nonidentity adapters surround every use of their role")
        need(dict(paid) == {int(k): v for k, v in c["local_profile"].items()}, "Complete paid profile")
        return dict(events=dict(counts), paid=dict(sorted(paid.items())), pairs=pairs, warps=warps)

    def problem(self, direction):
        """Expand every physical event and keep all 633 input and return roles."""
        bank = {}

        def put(name, circuit):
            if not circuit:
                return None
            oriented = conjugate(circuit) if direction == "backward" else circuit
            need(name not in bank or bank[name] == oriented, "One circuit per symbol")
            bank[name] = oriented
            return name

        def frame(index):
            return put("frame_" + str(index), self.frame(index))

        def old(register, entrance):
            circuit = self.old_frame(register, entrance)
            index = self.c["start" if entrance else "final"][register]
            if circuit == self.frame(index):
                return frame(index)
            return put(("entrance_" if entrance else "exit_") + str(register), circuit)

        def apply(out, target, symbol, inverse=False):
            if symbol is not None:
                out.append(dict(op="apply", dst=target, symbol=symbol, inverse=inverse))

        program = []
        offsets = []
        for event in self.word["programs"][direction]:
            offsets.append(len(program))
            kind = event[0]
            if kind in ("climb", "center", "warp"):
                if kind == "climb":
                    target, a, b = event[2:5]
                elif kind == "center":
                    target, a, b = OWNED, event[2], event[3]
                else:
                    target, signed, a, b = role(event[1]), *event[2:]
                apply(program, target, frame(a), True)
                if kind == "warp":
                    apply(program, target, put("warp_" + str(abs(signed)), self.maps[abs(signed)]), signed < 0)
                apply(program, target, frame(b))
            elif kind == "adapter":
                _, side, target, f = event
                if side == "old_to_new":
                    apply(program, target, old(target, True), True)
                    apply(program, target, frame(f))
                else:
                    apply(program, target, frame(f), True)
                    apply(program, target, old(target, False))
            elif kind == "scalar":
                gate = event[1]
                target, op = role(gate[1]), gate[0]
                if op in ("clear", "copy"):
                    program.append(dict(op="scale", dst=target, coefficient="0"))
                if op in ("copy", "add"):
                    program.append(dict(op="add", dst=target, src=role(gate[2]),
                                        coefficient=str(Q(1) if op == "copy" else Q(gate[3], gate[4]))))
                elif op == "scale":
                    program.append(dict(op="scale", dst=target, coefficient=str(Q(gate[2], gate[3]))))
            else:
                need(kind == "phase", "Known physical program marker")
        offsets.append(len(program))
        reference = []
        for register in range(PERSISTENT):
            apply(reference, register, old(register, True), True)
        for j in range(112):
            source, target, sign = (112+j, j, -1) if direction == "backward" else (j, 112+j, 1)
            reference.append(dict(op="add", dst=target, src=source, coefficient=str(sign)))
        for register in range(PERSISTENT):
            apply(reference, register, old(register, False))
        reference.append(dict(op="scale", dst=OWNED, coefficient="0"))
        return dict(axes=N, roles=PERSISTENT+1, operators=bank, program=program, reference=reference), offsets


def role(register):
    need(type(register) is list and len(register) == 2, "Register syntax")
    tag, index = register
    need(type(index) is int and ((tag == "L" and 0 <= index < PERSISTENT) or (tag == "C" and index == 0)),
         "Register domain")
    return index if tag == "L" else OWNED


def add(target, source, coefficient=Q(1)):
    for key, value in tuple(source.items()):
        value = target.get(key, Q(0)) + coefficient*value
        if value:
            target[key] = value
        else:
            target.pop(key, None)


def append_letter(word, letter, right=False):
    if right:
        return word[:-1] if word and word[-1] == -letter else word + (letter,)
    return word[1:] if word and word[0] == -letter else (letter,) + word


def interval(program, first, second, register, transpose_row=False):
    """Compute one full row or column of the logical interval matrix."""
    rows = [{} for _ in range(PERSISTENT+1)]
    rows[register][()] = Q(1)
    events = program[first+1:second]
    for event in reversed(events) if transpose_row else events:
        kind = event[0]
        if kind == "warp":
            target, signed = role(event[1]), event[2]
            rows[target] = {append_letter(w, signed, transpose_row): q for w, q in rows[target].items()}
        elif kind == "scalar":
            gate = event[1]
            target, op = role(gate[1]), gate[0]
            if op == "clear":
                rows[target] = {}
            elif op == "copy":
                source = role(gate[2])
                if transpose_row:
                    add(rows[source], rows[target])
                    rows[target] = {}
                else:
                    rows[target] = rows[source].copy()
            elif op == "add":
                source, q = role(gate[2]), Q(gate[3], gate[4])
                add(rows[source], rows[target], q) if transpose_row else add(rows[target], rows[source], q)
            else:
                need(op == "scale", "Known interval scalar")
                q = Q(gate[2], gate[3])
                rows[target] = {w: q*v for w, v in rows[target].items()}
    return rows[:PERSISTENT]


def fusion_pairs(program):
    previous, out = {}, []
    for j, event in enumerate(program):
        if event[0] != "climb":
            continue
        target = event[2]
        for k, earlier in previous.get(target, []):
            out.append((k, j, target, earlier[3], earlier[4], event[3], event[4]))
        previous.setdefault(target, []).append((j, event))
    return out


def contact_witness(program, pair):
    first, second, target, a, b, c, d = pair
    for transposed in (False, True):
        rows = interval(program, first, second, target, transposed)
        for other, entry in enumerate(rows):
            if other != target and len(entry) == 1:
                word, coefficient = next(iter(entry.items()))
                return dict(first=first, second=second, role=target, frames=[a, b, c, d],
                            ranks=[program[first][5], program[second][5]],
                            output=target if transposed else other, input=other if transposed else target,
                            coefficient=str(coefficient), word=list(word))
    raise ValueError("No single-term contact certificate for " + str(pair))


def complete_endpoint(problem, instructions):
    """Expand all independent inputs together. Coefficients remain rational."""
    symbols = {name: j+1 for j, name in enumerate(problem["operators"])}
    rows = [{(j, ()): Q(1)} for j in range(problem["roles"])]
    total = peak_total = problem["roles"]
    peak_row = 1
    for instruction in instructions:
        target, op = instruction["dst"], instruction["op"]
        total -= len(rows[target])
        if op == "apply":
            signed = symbols[instruction["symbol"]] * (-1 if instruction.get("inverse", False) else 1)
            rows[target] = {(entry, append_letter(word, signed)): q for (entry, word), q in rows[target].items()}
        elif op == "add":
            add(rows[target], rows[instruction["src"]], Q(instruction["coefficient"]))
        else:
            need(op == "scale", "Known complete program instruction")
            q = Q(instruction["coefficient"])
            rows[target] = {key: q*value for key, value in rows[target].items()} if q else {}
        total += len(rows[target])
        peak_total, peak_row = max(peak_total, total), max(peak_row, len(rows[target]))
    return rows, dict(peak_total_terms=peak_total, peak_row_terms=peak_row, final_terms=total)
