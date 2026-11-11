#!/usr/bin/env python3
"""Independent source-relative coefficient-consumer review.

The mathematical oracle is the closed rank-two pair of projectors I-J/3
and diag(0,1,1); no author matrix oracle or author replay is imported.
Read-only by default. Copy this directory into the package for portability.
Prepared for @CubeJerry by an independent OpenAI Codex review agent.
"""
import argparse
from fractions import Fraction
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys
from types import ModuleType


def require(ok, why):
    if not ok:
        raise ValueError(why)


def load(path):
    name = "independent_coefficient_consumer"
    old = sys.modules.get(name)
    module = ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    try:
        exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    finally:
        if old is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = old
    return module


def rejected(call, substring):
    try:
        call()
    except ValueError as exc:
        require(substring in str(exc), "unexpected rejection: " + str(exc))
        return str(exc)
    raise ValueError("negative control accepted: " + substring)


def authenticate(package):
    root = package.parents[1]
    manifest = json.loads((package / "SOURCES.json").read_text())
    require(manifest["base_commit"] == "e54523517d0f03e58352e647c403a5af3e525a57", "review base")
    count = 0
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        data = (root / row["path"]).read_bytes()
        require(sha256(data).hexdigest() == row["sha256"], "input SHA256: " + row["path"])
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        require(sha1(blob).hexdigest() == row["git_blob"], "input Git blob: " + row["path"])
        count += 1
    return count


def dimensions(C):
    dimensions = (2, 3, 64, 65, 129, 130, 257, 32767, 32768, 65536)
    rows = []
    for n in dimensions:
        m = C.build(n)
        require(m.edit_count == 17, "exact specialization sites")
        expected = max(16, (2*n).bit_length())
        require(m.finite_bits == m.records.FINITE_BITS == expected, "fixed label width")
        arena = m.words.Arena((2*n).bit_length()+3, 16)
        raw = m.words.Unsigned(arena)
        one = arena.input(1)
        product = raw.times_small(one, 2*n)
        require(product.inspect() == 2*n and one.head == product.head == 1, "upper finite multiplier")
        arena.free(product)
        row = arena.input(2*n-1)
        require(m.controller.finite_word(row, 2*n) == 2*n-1 and row.head == 1,
                "upper finite selector")
        tape = m.records.Tape()
        m.records.append_finite(tape, 2*n)
        tape.rewind()
        require(m.records.read_finite(tape) == 2*n, "finite width encoding crosses 16 bits")
        rejected(lambda: raw.times_small(one, 2*n+1), "finite index multiplier")
        arena.free_many(one, row)
        require(not arena.live, "dimension probe retired")
        rows.append({"N": n, "finite_bits": expected, "multiplier": 2*n})
    return rows


def rank_two_catalogue(C, modulus):
    q, n = 5, 3
    # Columns span sum(x)=0, followed by (1,1,1). Thus P=I-J/3.
    good_h = ((1, 0, 1), (-1, 1, 1), (0, -1, 1))
    # First two columns are e_1,e_2; P=diag(0,1,1).
    bad_h = ((0, 0, 1), (1, 0, 0), (0, 1, 0))
    preparation = tuple(tuple(Fraction(i == j) for j in range(n)) for i in range(n))
    template = C.Template(q, 2, preparation)
    specs, highs = {}, {}
    for code, header, good in ((65537, good_h, True), (131069, bad_h, False)):
        low = tuple(tuple(x % q for x in row) for row in header)
        high = tuple(tuple(((x % modulus) - (x % q)) // q for x in row) for row in header)
        specs[code] = C.Specification(code, template, low, good)
        highs[code] = high
    return specs, highs


def independent_expected(kind, coordinate, target=None, inverse=False, operand=None):
    # Over Z/25, the Good pivots are 2/3=9 and (1/3)/(2/3)=1/2=13.
    # Root unit 2 gives weights 18 on [0,9), 1 on [9,18).
    # Pair field 4 has delta=1, pi(4)=1, reversal c=5-j.
    # It selects Good coordinate 6+(5-j)=11-j; denominator is one.
    weights = (1, 1, 1, 18, 18, 18)
    if kind == "unit":
        return 1
    if kind == "weight":
        return weights[coordinate]
    value = (13 * weights[2*target+coordinate] * pow(weights[coordinate], -1, 25)) % 25
    if inverse:
        value = -value % 25
    if operand is not None:
        value = value * operand % 25
    return value


def algebra_and_reentry(C):
    n, modulus, root, Q = 3, 25, 27, 17
    m = C.build(n)
    R, I = modulus.bit_length()+1, root.bit_length()+1
    bounds = C.footprint(n, 3, R, I, Q)
    r = m.words.Arena(R, bounds["residue_pending"]+64)
    i = m.words.Arena(I, bounds["index_pending"]+64)
    # Entry historical backing deliberately exceeds all future live demand.
    for arena, number in ((r, bounds["residue_pending"]+11),
                          (i, bounds["index_pending"]+9)):
        past = [arena.zero() for _ in range(number)]
        arena.free_many(*past)
    mod = r.input(modulus)
    ring = m.words.Ring(mod)
    specs, highs = rank_two_catalogue(C, modulus)
    workspace = C.Workspace(m, ring, i)
    tapes = tuple(t for s in workspace.roles for t in (s.tape, s.reverse))
    tape_ids = tuple(map(id, tapes))
    history = [len(t.cells)+1 for t in tapes]
    allocated_entry = (len(r.words), len(i.words))
    good, bad = 65537, 131069
    pair_events = [(0, good, 2, 0, False, False), (1, bad, 2, 4, True, False)]
    unit_events = pair_events + [(2, bad, 2, 0, False, False)]
    plans = [("unit", j, None, False, None) for j in range(2)]
    plans += [("weight", j, None, False, None) for j in range(6)]
    plans += [("coefficient", c, t, False, None) for t in (1, 2) for c in (0, 1)]
    plans += [("coefficient", 1, 2, True, None), ("coefficient", 1, 2, True, 7)]
    outputs, largest_pending = [], [0, 0]
    inspect = m.words.Word.inspect
    arena_zero, tape_init = m.words.Arena.zero, m.records.Tape.__init__
    for kind, coordinate, target, inverse, operand in plans:
        events = unit_events if kind == "unit" else pair_events
        internal = kind == "coefficient"
        codes = [e[1] for e in events] + ([good] if internal else [])
        program = m.records.Program.fixture(i, r, root, 2, events, Q)
        fields = m.records.Fields.fixture(i, r, [(code, highs[code]) for code in codes], Q)
        position = i.input(coordinate)
        source = r.input(operand) if operand is not None else None
        entry_live = (len(r.live), len(i.live))
        borrowed = tuple(tuple((slot, bytes(arena.words[slot].cells), arena.words[slot].head)
                               for slot in sorted(arena.live)) for arena in (r, i))
        frozen = (bytes(program.tape.cells), bytes(fields.tape.cells),
                  program.tape.head, fields.tape.head, bytes(position.cells), position.head)
        source_before = (bytes(source.cells), source.head) if source is not None else None
        pending = {id(r): len(r.live), id(i): len(i.live)}
        def observed_zero(arena):
            pending[id(arena)] = max(pending[id(arena)], len(arena.live)+1)
            return arena_zero(arena)
        def no_inspection(_):
            raise ValueError("review forbids decoding runtime numeric words")
        def no_tape(_):
            raise ValueError("review forbids fresh continuation tapes")
        m.words.Arena.zero = observed_zero
        m.words.Word.inspect = no_inspection
        m.records.Tape.__init__ = no_tape
        cb = None
        try:
            cb = workspace.open(program, fields, specs, good, leaf=not internal)
            if internal:
                out = (cb.offset(target, position, source, inverse) if source is not None
                       else cb.coefficient(target, position, inverse))
            else:
                out = cb.weight(position)
            cb.close()
        except Exception:
            if cb is not None and workspace.active:
                cb.abort()
            raise
        finally:
            m.words.Arena.zero = arena_zero
            m.words.Word.inspect = inspect
            m.records.Tape.__init__ = tape_init
        expected = independent_expected(kind, coordinate, target, inverse, operand)
        value = inspect(out)
        require(value == expected, "closed rank-two oracle")
        r.free(out)
        require(frozen == (bytes(program.tape.cells), bytes(fields.tape.cells),
                           program.tape.head, fields.tape.head, bytes(position.cells), position.head),
                "whole borrowed chronological prefix and coordinate restored")
        if source is not None:
            require(source_before == (bytes(source.cells), source.head), "borrowed operand restored")
        require((len(r.live), len(i.live)) == entry_live and not workspace.active, "normal close")
        require(tuple(id(t) for s in workspace.roles for t in (s.tape, s.reverse)) == tape_ids,
                "fixed continuation identities")
        require(borrowed == tuple(tuple((slot, bytes(arena.words[slot].cells), arena.words[slot].head)
                                        for slot in sorted(arena.live)) for arena in (r, i)),
                "all borrowed numerical bytes and heads restored")
        for arena in (r, i):
            require(arena.template.head == 1, "permanent arena-template head restored")
            for word in arena.words:
                if word.slot not in arena.live:
                    require(word.head == 1 and all(c == m.words.BLANK for c in word.cells[1:]),
                            "entire historical free numerical backing erased")
        b = C.footprint(n, len(events), R, I, Q)
        require(len(program.tape.cells)+1 <= b["program_extent"], "complete Program extent")
        require(len(fields.tape.cells)+1 <= b["fields_extent"], "complete N-squared Fields extent")
        for k, arena in enumerate((r, i)):
            delta = pending[id(arena)]-entry_live[k]
            largest_pending[k] = max(largest_pending[k], delta)
            require(delta <= (b["residue_pending"] if k == 0 else b["index_pending"]), "pre-guard demand")
        for k, tape in enumerate(tapes):
            history[k] = max(history[k], len(tape.cells)+1)
            require(tape.head == 1, "closed stack origin")
            require(all(cell == m.records.BLANK for cell in tape.cells[1:]), "erased historical stack suffix")
        require(sum(history) <= bounds["four_stack_extents"], "sum of four historical maxima")
        require((len(r.words), len(i.words)) == allocated_entry, "preexisting larger numerical backing reused")
        outputs.append({"operation": kind, "coordinate": coordinate, "target": target,
                        "inverse": inverse, "operand": operand, "value": value})
        i.free(position)
        if source is not None:
            r.free(source)
    ring.close()
    r.free(mod)
    require(not r.live and not i.live, "all numerical owners retired")
    return {"outputs": outputs, "pending_above_entry": largest_pending,
            "four_historical_maxima": history, "entry_allocated_slots": list(allocated_entry)}


def syntax_case(C, n, kind, rank, field, *, old_multiplier=False, wrong_label=False):
    m = C.build(n)
    if old_multiplier:
        # The N=64 specialization reinstalls exactly the historical <=128 guard.
        m.words.Unsigned.times_small = C.build(64).words.Unsigned.times_small
    root, code, Q, q = 2*n, 131069, 17, 3
    r = m.words.Arena(q.bit_length()+1, 64)
    i = m.words.Arena(root.bit_length()+1, 64)
    modulus = r.input(q)
    ring = m.words.Ring(modulus)
    identity = tuple(tuple(Fraction(a == b) for b in range(n)) for a in range(n))
    # Only construction/label validation is tested here; no dense matrix
    # preparation or selected numerical catalogue is claimed by this case.
    low = tuple(tuple(int(a == (b if kind == 0 else (b+1) % n))
                      for b in range(n)) for a in range(n))
    spec = C.Specification(code, C.Template(q, rank, identity), low, kind == 0)
    events = [(kind, code, rank, field, field >= n if kind == 1 else False, False)]
    program = m.records.Program.fixture(i, r, root, 2, events, Q)
    fields = m.records.Fields.fixture(i, r, [(code if not wrong_label else code-1,
                                             tuple((0,)*n for _ in range(n)))], Q)
    frozen = (bytes(program.tape.cells), bytes(fields.tape.cells))
    workspace = C.Workspace(m, ring, i)
    entry_live = (len(r.live), len(i.live))
    if old_multiplier or wrong_label:
        substring = "finite index multiplier" if old_multiplier else "original global raw-field code"
        error = rejected(lambda: workspace.open(program, fields, {code: spec}, code,
                                                allow_fallback=True, leaf=True), substring)
        require(not workspace.active, "reject releases lease")
        require((len(r.live), len(i.live)) == entry_live, "constructed rejection retired")
        result = {"N": n, "control": error}
    else:
        cb = workspace.open(program, fields, {code: spec}, code, allow_fallback=True, leaf=True)
        require(not cb.prepared_codes, "large boundary case avoids numerical matrix execution")
        cb.close()
        require(frozen == (bytes(program.tape.cells), bytes(fields.tape.cells)), "large full-prefix preservation")
        require(program.tape.head == fields.tape.head == 1, "large record head restoration")
        require((len(r.live), len(i.live)) == entry_live, "large constructor closes")
        result = {"N": n, "kind": kind, "rank": rank, "field": field,
                  "raw_digit_words": n*n, "fields_cells": len(fields.tape.cells)+1}
    ring.close()
    r.free(modulus)
    require(not r.live and not i.live, "boundary test retired")
    return result


def effect_checks(C):
    # Independently derived phase bounds. Loops restore their scalar baseline;
    # shape allocations are included in full even before the final request.
    samples = 0
    for n in tuple(range(2, 65)) + (129, 130, 257, 32768, 65536):
        phase = max(4*n*n+12, 2*n*n+n+12, 5*n*n+12) + 64
        require(phase <= 16*n*n+128, "source-site residue effect inequality")
        for h in (0, 1, 2, 3, 17, 100):
            for r, i in ((3, n.bit_length()+1), (67, n.bit_length()+3)):
                q = 17
                b = C.footprint(n, h, r, i, q)
                t = max(2*i+4, r+3)
                independent_stacks = (3*h+4)*t+8
                require(independent_stacks <= b["four_stack_extents"], "four separate stack maxima")
                program = 2*i+r+7+h*(q+5*max(16,(2*n).bit_length())+2*i+10)
                fields = (h+1)*(q+n*n*(r+1)+2)+2
                require(program <= b["program_extent"] and fields <= b["fields_extent"], "exact grammar extents")
                samples += 1
    return samples


def lease_domain(C):
    """Demonstrate the exact normal-use guard and its deliberate scope limit.

    The stale-handle probe is outside the theorem's linear-use contract. It
    verifies that the documentation must not promise generation-safe handles.
    """
    m = C.build(3)
    r, i = m.words.Arena(3, 64), m.words.Arena(3, 64)
    modulus = r.input(3)
    ring = m.words.Ring(modulus)
    identity = tuple(tuple(Fraction(a == b) for b in range(3)) for a in range(3))
    spec = C.Specification(0, C.Template(3, 1, identity),
                           tuple(tuple(int(a == b) for b in range(3)) for a in range(3)), True)
    program = m.records.Program.fixture(i, r, 3, 1, [], 1)
    fields = m.records.Fields.fixture(i, r, [], 1)
    workspace = C.Workspace(m, ring, i)
    old = workspace.open(program, fields, {0: spec}, 0, leaf=True)
    old.close()
    current = workspace.open(program, fields, {0: spec}, 0, leaf=True)
    rejected(lambda: workspace.open(program, fields, {0: spec}, 0, leaf=True),
             "exclusive continuation workspace")
    require(workspace.active and len(i.live) == 6, "successor holds the live lease")
    old.abort()  # Deliberately invalid client use, isolated from all valid cases.
    require(not workspace.active and not i.live and len(r.live) == 2,
            "stale abort is not generation-guarded")
    del current
    ring.close()
    r.free(modulus)
    return {"concurrent_open_rejected": True, "stale_abort_generation_guarded": False,
            "required_contract": "Only the current live callback may act; closed/aborted handles are retired."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--write-result", type=Path)
    args = parser.parse_args()
    package = args.package_root.resolve()
    inputs = authenticate(package)
    C = load(package/"consumer.py")
    result = {"status": "pass", "base_commit": "e54523517d0f03e58352e647c403a5af3e525a57",
              "input_pins": inputs, "consumer_sha256": sha256((package/"consumer.py").read_bytes()).hexdigest(),
              "dimension_probes": dimensions(C), "rank_two": algebra_and_reentry(C),
              "syntax_cases": [syntax_case(C, 65, 1, 64, 128),
                               syntax_case(C, 130, 0, 129, 0),
                               syntax_case(C, 257, 2, 256, 0)],
              "negative_controls": [syntax_case(C, 130, 0, 129, 0, old_multiplier=True),
                                    syntax_case(C, 3, 2, 2, 0, wrong_label=True)],
              "effect_samples": effect_checks(C), "lease_domain": lease_domain(C)}
    result["negative_control_count"] = len(result["dimension_probes"]) + len(result["negative_controls"])
    if args.write_result:
        args.write_result.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print("PASS_INDEPENDENT_COEFFICIENT_REVIEW", len(result["dimension_probes"]),
          len(result["rank_two"]["outputs"]), len(result["syntax_cases"]),
          result["effect_samples"], result["negative_control_count"])


if __name__ == "__main__":
    main()
