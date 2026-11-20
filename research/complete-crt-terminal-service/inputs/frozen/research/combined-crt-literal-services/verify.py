"""Exact union replay: ownership, physical histories, tariffs, and pinned caller.

Oracles decode values only in observation code. No oracle, receipt, set, or
stack decoder chooses an execution owner or supplies an arithmetic result.
"""
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import resource
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import join

need = join.need


def frame(slot):
    return ("L", *(str((slot >> j) & 1) for j in range(6)), "R")


def stack(order):
    value = ("L", *(bit for slot in order for bit in frame(slot)[1:7]), "R")
    return value + ("_",) * (338 - len(value))


def code_value(cells):
    need(cells[0] == "L" and cells[7] == "R", "observer selector frame")
    return sum(int(cells[j + 1]) << j for j in range(6))


def value(cells, p):
    need(cells[0] == 2 and cells[p + 1] == 3
         and all(x in (0, 1) for x in cells[1:p + 1]), "observer complete Word")
    return sum(x << i for i, x in enumerate(cells[1:p + 1]))


class Audit:
    def __init__(self, p):
        self.p = p
        self.free = list(range(63, 7, -1))
        self.initialized = False
        self.packets = 0
        self.divisions = []
        self.arithmetic = Counter()
        self.complete_prices = []
        self.maximum_owned_live = 0

    def before(self, ports, name):
        return {"cells": [tuple(t.cells) for t in ports], "heads": [t.head for t in ports],
                "identities": [id(t.cells) for t in ports], "free": list(self.free)}

    def after(self, ports, name, before, receipt):
        p, m = self.p, len(before["free"])
        expected = list(before["cells"])
        expected_status = receipt["status"]
        expected_steps = None
        kind = name[2:]
        if ":SET_" in name:
            suffix = kind[4:].split("_")
            if name.startswith("A:"):
                role, slot = map(int, suffix)
                expected[64 + role] = frame(slot)
            else:
                expected[64] = frame(int(suffix[0]))
            expected_status, expected_steps = "BOUND", 31
        elif name == "A:ACQUIRE":
            for s in range(64, 68):
                expected[s] = ("_",) * 8
            expected_status, expected_steps = "READY", 89
        elif name == "L:INIT":
            self.free = list(range(63, 7, -1))
            expected[69] = stack(self.free)
            expected[64] = expected[65] = ("_",) * 8
            self.initialized = True
            expected_status, expected_steps = "READY", 2744
        elif name == "L:CLOSE":
            need(len(self.free) == 56, "no live owner discarded at CLOSE")
            expected[69] = ("_",) * 338
            expected_status, expected_steps = "RETIRED", 1395
            self.initialized = False
        elif name.startswith("L:"):
            source = code_value(before["cells"][64]) if kind in ("COPY", "FREE", "IS_LIVE") else None
            if kind in ("TAKE", "ZERO", "COPY"):
                out = self.free.pop()
                need(set(expected[out][1:]) <= {4}, "full inactive historical suffix")
                if kind == "ZERO":
                    expected[out] = (2, *([0] * p), 3, *expected[out][p + 2:])
                elif kind == "COPY":
                    need(source not in before["free"] and source != out, "live disjoint COPY source")
                    value(expected[source], p)
                    expected[out] = expected[source][:p + 2] + expected[out][p + 2:]
                expected_status = "ALLOC_" + str(out)
                expected_steps = {"TAKE": 36*m+155, "ZERO": 165*p+36*m+417,
                                  "COPY": 287*p+97*m+676}[kind]
            elif kind == "FREE":
                need(8 <= source < 64 and source not in self.free, "owned completed FREE")
                value(expected[source], p)
                expected[source] = (2,) + (4,) * (len(expected[source]) - 1)
                self.free.append(source)
                expected_status, expected_steps = "FREED", 160*p+61*m+409
            elif kind == "IS_LIVE":
                present = source not in self.free
                expected_status = "LIVE" if present else "FREE"
                expected_steps = 61*m+90 if present else 61*(self.free.index(source)+1)+89
            else:
                raise ValueError("unreviewed lifecycle entry")
            expected[69] = stack(self.free)
            expected[64] = expected[65] = ("_",) * 8
        else:
            slots = [code_value(before["cells"][s]) for s in range(64, 68)]
            a, b, q, r = slots
            x, y = value(expected[a], p), value(expected[b], p)
            self.arithmetic[kind] += 1
            if kind == "COMPARE":
                sign = (x > y) - (x < y)
                expected_status = {-1: "CMP_NEG", 0: "CMP_EQ", 1: "CMP_POS"}[sign]
                expected_steps = 125*p+388 if a == b else 247*p+602
                wanted = {"R": 2*p+3, "W": 0, "M": 2*p+4} if a == b else {
                    "R": 4*p+6, "W": 0, "M": 4*p+8}
            elif kind in ("ADD", "SUBTRACT"):
                need(q not in self.free and q not in (a, b) and set(expected[q][1:]) <= {4},
                     "fresh arithmetic output reservation")
                total = x+y if kind == "ADD" else x-y
                result = total % (1 << p)
                flag = int(total >= 1 << p) if kind == "ADD" else int(total < 0)
                expected[q] = (2, *((result >> i) & 1 for i in range(p)), 3, *expected[q][p+2:])
                expected_status = ("ADD_C" if kind == "ADD" else "SUB_B") + str(flag)
                expected_steps = 279*p+735 if a == b else 401*p+949
                wanted = {"R": 4*p+6, "W": p+1, "M": 4*p+8} if a == b else {
                    "R": 6*p+9, "W": p+1, "M": 6*p+12}
            elif kind == "DIVIDE":
                need(len(set(slots)) == 4 and 0 < y < 1 << (p-1), "admitted distinct division")
                quotient, remainder = divmod(x, y)
                c = quotient.bit_count()
                for owner, z in ((q, quotient), (r, remainder)):
                    need(owner not in self.free and set(expected[owner][1:]) <= {4},
                         "two fresh blank outputs")
                    expected[owner] = (2, *((z >> i) & 1 for i in range(p)), 3,
                                       *expected[owner][p+2:])
                expected_status = "DONE"
                expected_steps = 402*p*p+923*p+1346+(278*p+245)*c
                expected_logical = 18*p*p+36*p+458+(12*p+9)*c
                need(receipt["arithmetic_logical_instructions"] == expected_logical,
                     "exact divider logical cost")
                wanted = {"R": 6*p*p+13*p+12+(4*p+4)*c,
                          "W": p*p+3*p+2+p*c,
                          "M": 6*p*p+14*p+16+(4*p+4)*c}
                self.divisions.append({"p": p, "n": x, "d": y, "ones": c,
                                       "body_instructions": expected_steps})
            else:
                raise ValueError("unreviewed arithmetic entry")
            need(receipt["numeric_actions"] == wanted, "exact arithmetic numeric-action profile")
            need(receipt["instructions"] == receipt["arithmetic_logical_instructions"]
                 + 29*wanted["R"] + 30*(wanted["W"]+wanted["M"]), "literal expansion cost")
            outputs = 0 if kind == "COMPARE" else 2 if kind == "DIVIDE" else 1
            initial_free = m + outputs
            reservation = (122*initial_free+242, 158*initial_free+397,
                           194*initial_free+516)[outputs]
            self.complete_prices.append({"kind": kind, "slots": slots,
                                         "instructions": reservation+124+expected_steps})
            for s in range(64, 68):
                expected[s] = ("_",) * 8
        need(receipt["status"] == expected_status, "independent returned value/owner/flag")
        need(receipt["instructions"] == expected_steps, "exact primitive path tariff")
        need([tuple(t.cells) for t in ports] == expected, "complete same-owner contents and histories")
        need([t.head for t in ports] == before["heads"], "all active and suspended heads restored")
        need([id(t.cells) for t in ports] == before["identities"], "physical owner identity")
        if self.initialized:
            need(tuple(ports[69].cells) == stack(self.free), "actual ordered free stack")
            self.maximum_owned_live = max(self.maximum_owned_live, 56-len(self.free))
        self.packets += 1


def modules():
    w = join.load("words", "old-words.py")
    r = join.load("records", "old-records.py")
    e = join.load("entry", "old-entry.py")
    producer = join.load("current_producer", "old-producer.py")
    return w, r, e, producer


def eager(w, r, e, p):
    guide = e.Port(w)
    for _ in range(p):
        guide.append(w.ONE)
    guide.rewind()
    guards = tuple(e.Port(w) for _ in range(8))
    for i, guard in enumerate(guards):
        guard.cells.extend((r.RETURN, i % 2, w.BLANK, w.ONE))
    entry = e.Entry(w, r, guide, guards)
    for i, word in enumerate(entry.arena.words[8:]):
        word.cells.extend([w.BLANK] * (5 * i + i % 3))
    entry.arena.template.cells.extend([w.BLANK] * 41)
    return entry, guide, guards


def summary(machine, audit, bound):
    need(len(audit.complete_prices) == len(bound.arithmetic_calls), "complete arithmetic call census")
    for expected, actual in zip(audit.complete_prices, bound.arithmetic_calls):
        need(expected["kind"] == actual["kind"] and expected["slots"] == actual["slots"]
             and expected["instructions"] == actual["complete_instructions"],
             "complete reservation/setters/body invoice")
    return {"literal_calls": machine.calls, "literal_instructions": machine.instructions,
            "entry_counts": dict(sorted(machine.entries.items())),
            "entry_instruction_totals": dict(sorted(machine.entry_instructions.items())),
            "arithmetic_calls": dict(audit.arithmetic), "checked_packets": audit.packets,
            "arithmetic_alias_calls": dict(Counter(row["kind"] for row in bound.arithmetic_calls
                                                   if row["slots"][0] == row["slots"][1])),
            "maximum_observed_owned_live": audit.maximum_owned_live,
            "numeric_role_capacities": [len(t.cells) for t in bound.ports[:64]],
            "union_role_capacities": [len(t.cells) for t in bound.ports],
            "union_history_cells": sum(len(t.cells) for t in bound.ports),
            "per_role_touched_intervals": machine.history,
            "division_profiles": audit.divisions,
            "complete_arithmetic_instructions": sum(x["complete_instructions"] for x in bound.arithmetic_calls)}


def primitive_checks(code, metadata, smoke=False):
    w, r, e, _ = modules()
    reports = []
    for p in ((4,) if smoke else (4, 7, 19)):
        entry, guide, guards = eager(w, r, e, p)
        audit = Audit(p)
        machine = join.Program(code, metadata, audit)
        bound = join.BoundEntry(entry.arena, machine)
        raw = w.Unsigned(entry.arena)
        a = entry.arena
        if p == 4:
            pairs = [(5, 3)] if smoke else [(x, y) for x in range(16) for y in range(16)]
            divisions = [(15, 7)] if smoke else [(x, y) for x in range(16) for y in range(1, 8)]
            aliases = [9] if smoke else list(range(16))
        else:
            top = (1 << p)-1
            pairs = [(0, 1), (top, 1), (top, top), (top//3, top//5+1)]
            divisions = [(0, 1), (top, 1), (top, (1 << (p-1))-1), (top//2, 3)]
            aliases = [0, top]
        with join.forbid_old(w) as blocked:
            with bound.install(w):
                for x, y in pairs:
                    left, right = a.literal(x), a.literal(y)
                    raw.compare(left, right)
                    for function in (raw.add, raw.subtract):
                        output, _ = function(left, right)
                        copied = a.copy(output)
                        a.free(output)
                        a.free(copied)
                    a.free(left)
                    a.free(right)
                for x in aliases:
                    operand = a.literal(x)
                    raw.compare(operand, operand)
                    for function in (raw.add, raw.subtract):
                        output, _ = function(operand, operand)
                        a.free(output)
                    a.free(operand)
                for x, y in divisions:
                    left, right = a.literal(x), a.literal(y)
                    quotient, remainder = raw.divmod(left, right)
                    a.free(quotient)
                    a.free(left)
                    a.free(remainder)
                    a.free(right)
                need(blocked["calls"] == 0, "no primitive fallback")
                bound.close()
        need(all(set(t.cells[1:]) <= {w.BLANK} for t in a.words[8:]), "all primitive Word histories retired")
        report = summary(machine, audit, bound)
        report.update(p=p, distinct_pairs=pairs, aliases=aliases, divisions=divisions,
                      old_fallback_calls=blocked["calls"])
        reports.append(report)
    return reports


def canonical(r, w, pairs):
    tape = r.Tape()
    for pair in pairs:
        tape.append(r.ROOT)
        for z in pair:
            for i in range(max(1, z.bit_length())):
                tape.append((z >> i) & 1)
            tape.append(r.WORD_END)
        tape.append(r.RECORD_END)
    tape.append(w.RIGHT)
    tape.rewind()
    return tape


def meter_actions(meter):
    return meter.reads + meter.writes + meter.moves


def decode_records(tape, r, w, p):
    cells = tape.cells
    pos, out = 1, []
    while cells[pos] != w.RIGHT:
        need(cells[pos] == r.ROOT, "output record tag")
        pos += 1
        pair = []
        for _ in range(2):
            digits = cells[pos:pos+p]
            need(len(digits) == p and all(v in (0, 1) for v in digits), "output record digits")
            pair.append(sum(v << i for i, v in enumerate(digits)))
            pos += p
            need(cells[pos] == r.WORD_END, "output word end")
            pos += 1
        need(cells[pos] == r.RECORD_END, "output record end")
        pos += 1
        out.append(pair)
    need(tape.head == 1, "output head")
    return out


def source_check(code, metadata):
    w, r, e, producer = modules()
    p, left_pairs, right_pairs = 7, [(5, 1)], [(7, 2)]
    entry, guide, guards = eager(w, r, e, p)
    left, right = canonical(r, w, left_pairs), canonical(r, w, right_pairs)
    borrowed = [(tuple(t.cells), t.head) for t in (guide, *guards, left, right)]
    audit = Audit(p)
    machine = join.Program(code, metadata, audit)
    bound = join.BoundEntry(entry.arena, machine)
    all_ports = (*bound.ports, guide, left, right, entry.left, entry.right, entry.output)
    need(len({id(t.cells) for t in all_ports}) == 76, "complete 76-owner eager source context")
    identities = [id(t.cells) for t in all_ports]
    meters = {id(t.meter): t.meter for t in (guide, *guards, left, right, *entry.owned)}
    meters[id(entry.arena.meter)] = entry.arena.meter
    initial_actions = sum(meter_actions(m) for m in meters.values())
    with join.forbid_old(w) as blocked:
        with bound.install(w):
            result = entry.invoke(producer, left, right)
            lower, product = value(tuple(result["lower"].cells), p), value(tuple(result["product"].cells), p)
            records = decode_records(result["stream"], r, w, p)
            # Independent current-coordinate characterization.
            previous, congruences = 1, []
            for modulus, digit in left_pairs:
                congruences.append((modulus, (previous*digit) % modulus))
                previous *= modulus
            expected_lower = next(x for x in range(previous)
                                  if all(x % m == residue for m, residue in congruences))
            expected_records = []
            complete_prefix = previous
            for modulus, digit in right_pairs:
                offset = expected_lower * pow(complete_prefix, -1, modulus) % modulus
                expected_records.append([offset, (digit+offset) % modulus if digit < modulus else digit])
                complete_prefix *= modulus
            need((lower, product, records, result["left_valid"])
                 == (expected_lower, previous, expected_records, True), "independent complete CRT oracle")
            entry.consume(result)
            need(blocked["calls"] == 0, "no arithmetic or lifecycle fallback in full source")
    need([id(t.cells) for t in all_ports] == identities, "source retains every physical owner")
    need(borrowed == [(tuple(t.cells), t.head) for t in (guide, *guards, left, right)],
         "all borrowed source, guide and dirty guards restored")
    need(all(t.head == 1 and set(t.cells[1:]) <= {w.BLANK} for t in entry.arena.words[8:]),
         "source numerical histories blank")
    # Entry.close still asks arena.live. Retire the stack only after its final
    # physical membership queries, and charge the original close separately.
    close_before = sum(meter_actions(m) for m in meters.values())
    entry.close()
    retained_close_actions = sum(meter_actions(m) for m in meters.values()) - close_before
    bound.close()
    need([id(t.cells) for t in all_ports] == identities, "closure retains every physical owner")
    measured_actions = sum(meter_actions(m) for m in meters.values()) - initial_actions
    residual = measured_actions - machine.arena_actions
    need(residual >= 0, "disjoint literal/native source invoice")
    report = summary(machine, audit, bound)
    report.update(p=p, left=left_pairs, right=right_pairs, lower=lower, product=product,
                  records=records, old_fallback_calls=blocked["calls"],
                  physical_context_roles=76, residual_native_symbol_actions=residual,
                  measured_native_symbol_actions=measured_actions,
                  literal_arena_symbol_actions=machine.arena_actions,
                  physical_context_capacities=[len(t.cells) for t in all_ports],
                  retained_entry_close_actions=retained_close_actions,
                  sealed_provider_scope="producer invocation and result consumer; original Entry.close separately retained")
    need(all(t.head == 1 and set(t.cells) <= {w.BLANK} for t in entry.owned),
         "retained Entry closes its original owners")
    return report


def controls(code, metadata):
    w, r, e, _ = modules()
    reports = []
    entry, _, _ = eager(w, r, e, 4)
    audit = Audit(4)
    machine = join.Program(code, metadata, audit)
    bound = join.BoundEntry(entry.arena, machine)
    original = bound.ports
    aliases = list(original)
    aliases[69] = aliases[68]
    try:
        machine.run(tuple(aliases), "L:INIT")
    except ValueError as exc:
        need("70 distinct" in str(exc), "physical alias rejection")
        reports.append("aliased physical metadata owner")
    else:
        raise ValueError("physical alias escaped")
    with join.forbid_old(w) as counter:
        try:
            w.Arena.zero(entry.arena)
        except ValueError as exc:
            need(str(exc) == "OLD_ARITHMETIC_OR_LIFECYCLE_UNAVAILABLE", "old lifecycle sealed")
        else:
            raise ValueError("old lifecycle remained callable")
    need(counter["calls"] == 1, "fallback control actually exercised")
    reports.append("sealed old lifecycle positive control")
    bound.close()
    try:
        entry.close()
    except ValueError as exc:
        need(str(exc) == "independent returned value/owner/flag", "premature metadata retirement control")
        reports.append("metadata CLOSE before retained Entry.close is rejected")
    else:
        raise ValueError("post-retirement live query escaped")
    # A returning semantic corruption keeps output bits and every head correct.
    mutant = tuple(("H", "ADD_C1") if row == ("H", "ADD_C0") else row for row in code)
    entry, _, _ = eager(w, r, e, 4)
    audit = Audit(4)
    machine = join.Program(mutant, metadata, audit)
    bound = join.BoundEntry(entry.arena, machine)
    with join.forbid_old(w):
        with bound.install(w):
            a, b = entry.arena.literal(1), entry.arena.literal(2)
            try:
                w.Unsigned(entry.arena).add(a, b)
            except ValueError as exc:
                need(str(exc) == "independent returned value/owner/flag", "returning flag mutation")
                reports.append("returned carry corruption with correct arithmetic body")
            else:
                raise ValueError("wrong carry escaped semantic oracle")
    return reports


def main():
    started = time.monotonic()
    code, metadata = join.compile_union()
    built_seconds = time.monotonic()-started
    smoke = "--smoke" in sys.argv
    out = {"status": "PASS_COMBINED_CRT_LITERAL_SERVICES",
           "locations": len(code), "graph_sha256": join.digest(code), "roles": 70,
           "source_files": join.authenticate(), "lifecycle_role_map": list(join.ROLE_MAP),
           "primitive": primitive_checks(code, metadata, smoke),
           "source": source_check(code, metadata), "controls": controls(code, metadata),
           "scope": "One eager Entry. Four arithmetic providers and Word lifecycle literal; higher controller, grants, record/Word predicates and Entry closure retained."}
    if "--record" not in sys.argv and not smoke:
        # The receipt is a JSON artifact: normalize source-coordinate tuples
        # to JSON arrays before equality, without weakening any field check.
        need(json.loads(json.dumps(out)) == json.loads((HERE/"RESULT.json").read_text()),
             "receipt changed")
    print(json.dumps(out, indent=2, sort_keys=True))
    print(json.dumps({"compile_seconds": round(built_seconds, 3),
                      "total_seconds": round(time.monotonic()-started, 3),
                      "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}),
          file=sys.stderr)


if __name__ == "__main__":
    main()

