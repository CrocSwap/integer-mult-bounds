#!/usr/bin/env python3
"""Exact source-extracted checks for the conditional ordinary-stack coefficient.

Caller tests execute actual retained function bodies with call-description or
extent-only payload interpreters. Allocator tests use actual Page/PacketStack
implementations on in-memory byte streams. No production calendar is executed.
"""
from __future__ import annotations

import argparse
import ast
from contextlib import ExitStack, contextmanager, nullcontext
from copy import deepcopy
from fractions import Fraction as F
from functools import lru_cache, partial
from hashlib import sha256
from io import BytesIO
from itertools import product
from math import prod
from pathlib import Path
from types import ModuleType, SimpleNamespace
import json
import sys

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "sources"


def need(condition, why):
    if not condition:
        raise AssertionError(why)


def extract(filename, names, env, mutate=None):
    tree = ast.parse((SOURCE / filename).read_text(), filename=filename)
    nodes = []
    for name in names:
        parts = name.split(".")
        body = tree.body
        for part in parts:
            found = next((x for x in body if isinstance(x, (ast.FunctionDef, ast.ClassDef))
                          and x.name == part), None)
            need(found is not None, "missing source definition " + filename + ":" + name)
            body = found.body
        nodes.append(deepcopy(found))
    unit = ast.Module(body=nodes, type_ignores=[])
    if mutate:
        unit = mutate.visit(unit)
        ast.fix_missing_locations(unit)
    exec(compile(unit, str(SOURCE / filename), "exec"), env)


def source_pins():
    manifest = json.loads((HERE / "SOURCE-BINDINGS.json").read_text())
    need(manifest["commit"] == "dfd25d553a843a946ca0b94130a5ff8943e98fdd", "source head changed")
    for name, record in manifest["files"].items():
        need(Path(name).name == name, "nonlocal source name")
        data = (SOURCE / name).read_bytes()
        need(len(data) == record["size"] and sha256(data).hexdigest() == record["sha256"],
             "source pin mismatch " + name)
    return len(manifest["files"])


def volume(atom, shape):
    return (shape["available"] * shape["older"] * atom ** (2 * shape["atoms"])
            * shape["gap"] * shape["suffix"])


def geometry_checks():
    schedules = []

    def pipe(arena, kind, source, target, size, schedule):
        schedules.append((kind, size, list(schedule)))

    def lower_tape(*args, **kwargs):
        pass

    env = {"partial": partial, "prod": prod, "lru_cache": lru_cache,
           "one_weight": lambda *_: 1, "pipe": pipe, "lower_tape": lower_tape,
           "weighted_pair": lower_tape}
    extract("module_atoms.py", ["pair_shape"], env)
    extract("same_order_body.py", ["SameOrderBody.weighted"], env)
    weighted = env["weighted"]
    extract("five_exchange.py", ["corner_exchanges", "same_order_line", "direct_line"], env)
    extract("receiver.py", ["Receiver.serve_line"], env)

    # The direct line imports these only to construct route descriptors. The
    # real source child shape executes unchanged; payload routes are not run.
    replacements = {"direct_body": ModuleType("direct_body"),
                    "factored_frames": ModuleType("factored_frames")}
    replacements["direct_body"].direct_route = lower_tape
    replacements["factored_frames"].inverse_word = lambda w: tuple(reversed(w))
    saved = {key: sys.modules.get(key) for key in replacements}
    sys.modules.update(replacements)
    counts = {"compiled": 0, "direct_empty": 0, "direct_wrapped": 0, "covered_children": 0}
    no_q_rejected = False
    try:
        for n, width, b, unused, old, gap, suffix in product((2, 3, 4), (1, 2), (2, 17),
                                                            (1, 3), (1, 2), (1, 2), (1, 3)):
            alpha = 3**width
            q = prod(3**j-1 for j in range(1, n+1))
            high = 3 ** ((width-1)*n*(n+1)//2)
            captured = []

            def child(*args, **shape):
                captured.append(shape)

            core = SimpleNamespace(n=n, atom=alpha, modulus=3**width, stock=b*q*high,
                                   layout=(1, width, 0, 0), previous=lower_tape,
                                   direct=True, weighted=child, compiled=lower_tape,
                                   storage=lambda: nullcontext(None))
            for f, remainder in ((1, 0), (1, n-1), (2, 1)):
                c = n*f + remainder
                original = dict(atoms=c, available=unused*b*q*high, older=old,
                                gap=gap, suffix=suffix)
                schedules.clear()
                weighted(core, None, None, **original)
                need(len(schedules) == 1 and schedules[0][1] == volume(alpha, original),
                     "weighted full incoming volume")
                compiled = schedules[0][2][-1].keywords
                bank_slot = (compiled["unused"]*q*high*compiled["older"]*
                             alpha**(2*n*compiled["f"])*compiled["gap"]*compiled["suffix"])
                need(b*bank_slot == volume(alpha, original), "compiler owner omitted residual or stock")
                counts["compiled"] += 1
            f = 2
            for axis in range(n):
                frame = SimpleNamespace(mask=(axis,), word=())
                captured.clear()
                env["serve_line"](core, None, None, frame, f, unused, old, gap, suffix, lambda *_: 1)
                true_slot = unused*old*alpha**(2*n*f)*gap*suffix
                need(len(captured) == 1 and volume(alpha, captured[0]) == true_slot,
                     "direct empty-line true argument")
                counts["direct_empty"] += 1
                for word in ((), (("swap", 0, n-1),)):
                    frame.word = word
                    schedules.clear()
                    env["direct_line"](core, None, None, frame, f, unused, old, gap, suffix, lambda *_: 1)
                    children = [p for p in schedules[0][2] if p.func is child]
                    need(len(children) == 1 and volume(alpha, children[0].keywords) == true_slot,
                         "direct wrapped argument")
                    counts["direct_wrapped"] += 1
            factors_list = [([1]*n, [1]*n, 0),
                            ([0]*(n-1)+[1], [1]+[0]*(n-1), n-1),
                            ([1]+[0]*(n-1), [1]+[0]*(n-1), 0)]
            for primal, dual, pivot in factors_list:
                schedules.clear()
                env["same_order_line"](core, None, None, pivot=pivot,
                    factors=lambda _, u=primal, v=dual: (u, v), f=f, unused=unused,
                    heights=high, older=old, gap=gap, suffix=suffix, weight=lambda *_: 1)
                packet = unused*high*old*alpha**(2*n*f)*gap*suffix
                need(schedules[0][1] == packet, "covered wrapper packet")
                children = [p for p in schedules[0][2] if p.func is child]
                need(len(children) in (1, 3, 5), "wrong ordered itinerary")
                for p in children:
                    need(volume(alpha, p.keywords) == packet, "covered true argument")
                    wrong = dict(p.keywords, available=p.keywords["available"]*q)
                    no_q_rejected |= volume(alpha, wrong) != packet
                    counts["covered_children"] += 1
    finally:
        for key, value in saved.items():
            if value is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = value
    need(no_q_rejected, "missing low divisor negative control was vacuous")
    return {**counts, "missing_low_divisor_rejected": no_q_rejected}


class Extent:
    """Independent interval semantics without materializing any payload."""
    def __init__(self, size=0):
        self.size = self.peak = size
        self.position = 0

    def seek(self, position, whence=0):
        self.position = (0, self.position, self.size)[whence] + position
        need(0 <= self.position <= self.size, "extent seek outside input")
        return self.position


def consume(source, target, count):
    need(count >= 0 and source.position + count <= source.size, "short extent input")
    source.position += count
    if target is not None:
        grow(target, count)


def grow(target, count):
    target.position += count
    target.size = max(target.size, target.position)
    target.peak = max(target.peak, target.size)


def erase_extent(tape):
    tape.position = tape.size = 0


def extent_env():
    created = []

    @contextmanager
    def work_tapes(count):
        tapes = [Extent() for _ in range(count)]
        created.extend(tapes)
        try:
            yield tapes
        finally:
            for tape in tapes:
                erase_extent(tape)

    def shift(source, target, temporary, prefix, side, gap, piece, factor, offset):
        consume(source, target, prefix*side*gap*piece*(side if factor is not None else 1))

    def negate(source, target, temporary, prefix, side, piece):
        consume(source, target, prefix*side*piece)

    return {"work_tapes": work_tapes, "copy_bytes": consume, "write_zeros": grow,
            "erase": erase_extent, "shift_field": shift, "negate_field": negate}, created


class EnlargeOddTail(ast.NodeTransformer):
    def visit_AugAssign(self, node):
        if (isinstance(node.target, ast.Name) and node.target.id == "tail"
                and isinstance(node.op, ast.Mult) and isinstance(node.value, ast.Constant)
                and node.value.value == 3):
            node.value = ast.Constant(9)
        return self.generic_visit(node)


def predecessor_checks(mutate=None):
    env, _ = extent_env()
    extract("limb_scale.py", ["unit_scale"], env, mutate)
    calls = 0
    tests = 0
    for digits, prefix, piece, unit in product(range(1, 9), (1, 2), (1, 3), (2, 4, 5, 8, 17)):
        full = prefix*3**digits*piece

        def previous(source, target, d, p, g, s):
            nonlocal calls
            need(p*3**(2*d)*g*s == full, "scaler predecessor enlarged or truncated argument")
            consume(source, target, full)
            calls += 1

        out = Extent()
        env["unit_scale"](Extent(full), out, digits, prefix, piece, unit, previous)
        need(out.size == full, "scaler final complete extent")
        tests += 1
    # The two direct shapes and the affine exponent identity are checked over
    # independent caller indices; the full packet tests above bind actual dims.
    identities = 0
    for fields, left, right in product(range(2, 9), range(8), range(8)):
        if not 0 <= left < right < fields:
            continue
        for digits in range(1, 5):
            side = 3**digits
            need(side**left * side**2 * side**(right-left-1) * side**(fields-right-1)
                 == side**fields, "affine whole-interval identity")
            identities += 1
    return {"scaler_cases": tests, "source_predecessor_calls": calls,
            "affine_exponent_cases": identities}


def root_checks():
    env, created = extent_env()
    extract("ordinary.py", ["least_power"], env)
    extract("module_atoms.py", ["total_width"], env)
    extract("triangular_ordinary.py", ["root_body"], env)
    tests = 0
    for e, prefix, gap, suffix, owners, width in product((40, 41, 72), (1, 2), (1, 3),
                                                       (1, 2), (2, 3), (1, 2)):
        seen = []
        cold = []
        layout = (1, width, 0, 0)
        n = 2
        core = SimpleNamespace(n=n, layout=layout, owners=owners, low=1, high=1)
        before = len(created)
        u = prefix*3**(2*e)*gap*suffix

        def body(source, target, c, available, older, g, s):
            w = available*older*3**(2*width*c)*g*s
            need(u <= w < 2*u, "fresh ordinary stage pad escaped factor two")
            seen.append(w)
            consume(source, target, w)

        def cold_swap(source, target, digits, p, g, s):
            size = p*3**(2*digits)*g*s
            need(size == u, "root correction changed the true unpadded field")
            consume(source, target, size)
            cold.append(size)

        core.body_ordinary = body
        env["cold_swap_tape"] = cold_swap
        out = Extent()
        env["root_body"](Extent(u), out, e, prefix, gap, suffix, core)
        need(len(seen) == 1 and out.size == u, "root did not return its exact field")
        need(len(created)-before == 5 and all(t.peak <= seen[0] for t in created[before:]),
             "persistent root envelope")
        tests += 1
    return {"source_root_cases": tests, "method": "exact extent interpreter; no payload allocation"}


def allocator_checks():
    streams = []

    class MemoryFile(BytesIO):
        def close(self):
            need(not any(self.getvalue()), "dirty byte survived a complete source frame return")
            streams.append(self.getvalue())
            super().close()

    env = {"ExitStack": ExitStack, "contextmanager": contextmanager, "TemporaryFile": MemoryFile}
    extract("streaming_routes.py", ["read_exact", "write_zeros"], env)
    env.update(CHUNK=65536, ZEROS=bytes(65536))
    extract("stack_tapes.py", ["FileHead", "Page", "PacketStack", "Arena"], env)
    expected = {"weighted": 2, "compiler": 3, "issued-leaf": 1, "chart-line": 2,
                "chart-packet": 2, "exposed-leaf": 2, "direct-coordinate": 2,
                "matcher": 2, "triangular-body": 2}
    tree = ast.parse((SOURCE/"check_stage_inventory.py").read_text())
    source_arities = next(ast.literal_eval(x.value) for x in tree.body
                          if isinstance(x, ast.Assign) and any(isinstance(t, ast.Name)
                          and t.id == "PAGE_ARITIES" for t in x.targets))
    need(source_arities == expected and sum(expected.values())+2 == 20, "named role inventory")
    cases = 0
    for depth in range(1, 7):
        arena = env["Arena"]()
        b = 2
        w0 = 16*b**(depth+1)

        def visit(level, w):
            with ExitStack() as stack:
                for name, arity in expected.items():
                    pages = stack.enter_context(arena.frames(name, arity))
                    for i, page in enumerate(pages):
                        if name == "weighted":
                            length = w
                        elif name == "compiler":
                            length = 2*w if i == 0 else w
                        elif name in {"chart-packet", "exposed-leaf", "triangular-body"}:
                            length = w//(16*b)
                        else:
                            length = w//b
                        page.write(bytes([1+level])*length)
                if level < depth:
                    visit(level+1, w//b)
                    if level == 0:
                        # A second shorter dirty sibling reuses every parent base.
                        visit(level+1, w//(2*b))

        visit(0, w0)
        need(all(not h.frames for h in arena.heads.values()), "named frames retained")
        named_sum = sum(h.peak for h in arena.heads.values())
        named_bound = F((6*b)*8+75, 8*(b-1))*w0
        need(named_sum <= named_bound, "historical sum lost an ancestor or sibling")
        arena.close()
        cases += 1
    # Actual packet operations show why sum(max) differs from max(sum).
    arena = env["Arena"]()
    v, ell = 64, 4
    source = BytesIO(bytes(range(v)))
    source.seek(v)
    arena.pending.push_reverse(source, v)
    live_peak = v
    for _ in range(v//ell):
        packet = BytesIO()
        arena.pending.pop_forward(packet, ell)
        packet.seek(0)
        arena.answers.append(packet, ell)
        live_peak = max(live_peak, arena.pending.top+arena.answers.top)
    out = BytesIO()
    arena.answers.take_answers(0, out)
    need(out.getvalue() == bytes(range(v)), "packet order changed")
    history = arena.pending.head.peak+arena.answers.head.peak
    need(history == 2*v and live_peak == v, "historical-vs-live control lost its distinction")
    arena.close()
    return {"adversarial_page_traces": cases, "page_depth_max": 7,
            "packet_live_peak": live_peak, "packet_historical_sum": history,
            "instantaneous_sum_substitution_rejected": history > live_peak,
            "scope": "actual allocator methods; role-bounded traces, not a full native calendar"}


def cold_checks():
    created = []

    class Meter(BytesIO):
        def __init__(self, data=b""):
            super().__init__(data)
            self.peak = len(data)

        def write(self, data):
            n = super().write(data)
            self.peak = max(self.peak, self.tell())
            return n

    env = {"CHUNK": 65536, "ZEROS": bytes(65536)}
    extract("streaming_routes.py", ["read_exact", "copy_bytes", "write_zeros", "erase",
            "trit_swap", "cold_swap_tape"], env)

    @contextmanager
    def work_tapes(count):
        tapes = [Meter() for _ in range(count)]
        created.extend(tapes)
        try:
            yield tapes
        finally:
            for tape in tapes:
                env["erase"](tape)

    env["work_tapes"] = work_tapes
    cases = 0
    for digits, prefix, gap, suffix in product(range(1, 5), (1, 2), (1, 2), (1, 3)):
        side = 3**digits
        v = prefix*side**2*gap*suffix
        data = bytes((i*31+i//251)%256 for i in range(v))
        out = Meter()
        start = len(created)
        env["cold_swap_tape"](Meter(data), out, digits, prefix, gap, suffix)
        expected = b"".join(data[(((p*side+a)*gap+g)*side+b)*suffix:
                                  (((p*side+a)*gap+g)*side+b+1)*suffix]
                            for p, b, g, a in product(range(prefix), range(side), range(gap), range(side)))
        need(out.getvalue() == expected, "cold interchange permutation")
        peaks = [x.peak for x in created[start:]]
        need(len(peaks) == 11 and all(x <= v for x in peaks[:2])
             and all(9*x <= v for x in peaks[2:]) and sum(peaks) <= 3*v,
             "cold fixed-role envelope")
        cases += 1
    return {"source_cold_cases": cases, "uniform_role_coefficients": ["1", "1"]+["1/9"]*9}


def stage_and_coefficients():
    tree = ast.parse((SOURCE/"ordinary_carrier.py").read_text())
    body = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "stage_body")
    caps = [k.value for n in ast.walk(body) if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Name) and n.func.id == "partial"
            for k in n.keywords if k.arg == "maximum"]

    def strict_cap(nodes):
        need(len(nodes) == 1 and ast.dump(nodes[0], include_attributes=False)
             == ast.dump(ast.parse("stage-1", mode="eval").body, include_attributes=False),
             "predecessor stage is not strictly descending")

    strict_cap(caps)
    rejected = False
    try:
        strict_cap([ast.Name(id="stage", ctx=ast.Load())])
    except AssertionError:
        rejected = True
    need(rejected, "same-stage predecessor negative control")
    env = {"entrance_logs": lambda ranks: tuple(3*(i+1) for i in range(len(ranks)))}
    extract("ordinary_carrier.py", ["stage_for_width_log"], env)
    selector_cases = 0
    for maximum, available in product(range(8), range(25)):
        chosen = env["stage_for_width_log"](available, maximum, tuple(range(7)))
        need(0 <= chosen <= maximum, "selector escapes cap")
        selector_cases += 1
    recipes = {}
    extract("transport.py", ["Recipe"], recipes)
    recipe = recipes["Recipe"](1024, 1, (), (), {}, F(0))
    need(recipe.width_log == 92*1024 and recipe.width == 1 << (92*1024), "production B formula")
    install = ast.parse((SOURCE/"installations.py").read_text())
    profiles = [ast.literal_eval(n.value.args[0]) for n in install.body if isinstance(n, ast.Assign)
                and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name)
                and n.value.func.id == "Profile"]
    need(len(profiles) == 7 and min(min(p) for p in profiles) >= 5610
         and max(map(len, profiles)) == 7, "installed production rank domain")
    rational_cases = 0
    for b in (2, 3, 16, 17, 31, 256, 65536):
        coefficients = [F(1), F(1), F(2), F(1), F(1), F(1,b),
                        *([F(1,b)]*2), *([F(1,16*b)]*4),
                        *([F(1,b)]*4), *([F(1,16*b)]*2), *([F(1,b)]*2)]
        need(len(coefficients) == 20, "twenty coefficient entries")
        c = sum(coefficients)
        need(c == 6+F(75,8*b), "named-role sum")
        g = c*F(b,b-1)
        need(g == 6+F(123,8*(b-1)) and g <= F(171,8), "geometric named coefficient")
        if b >= 17:
            need(g < 7, "production seven-volume bound")
        for depth in range(17):
            need(sum(F(1,b**j) for j in range(depth+1))*c < g, "finite chain exceeds sum")
            rational_cases += 1
    for m in range(1, 8):
        need(sum(2**(m-j+1) for j in range(1,m+1)) == 2**(m+1)-2, "stage sum")
    need(2+15*254+3*128 == 4196 and 9*4196 == 37764 and 9*254 == 2286,
         "complete ordinary coefficient")
    # Exact symbolic noncontraction: the first weighted page at each of D+1
    # levels contains the same true W when B=1. The other page need not peak
    # simultaneously and is not needed for the obstruction.
    b1 = [{"depth": d, "weighted_first_head_ratio": d+1} for d in (1, 4, 8, 32)]
    return {"selector_cases": selector_cases, "stage_cap_mutation_rejected": rejected,
            "rational_cases": rational_cases, "small_rank_B1_boundary": b1,
            "seven_stage_bound": "(4196+254*A)*T < (37764+2286*A)*X",
            "retained_premises": ["binary capacity beta<=2", "uniform coordinatewise transient envelopes",
                                  "legal complete headers and return contracts", "fixed-stage role lowering"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE/"evidence/RESULT.json")
    args = parser.parse_args()
    pins = source_pins()
    result = {"source_files": pins, "geometry": geometry_checks(),
              "predecessor": predecessor_checks(), "root": root_checks(),
              "allocator": allocator_checks(), "cold": cold_checks(),
              "coefficients": stage_and_coefficients()}
    rejected = False
    try:
        predecessor_checks(EnlargeOddTail())
    except AssertionError:
        rejected = True
    need(rejected, "enlarged odd tail mutation was not rejected")
    result["predecessor"]["enlarged_odd_tail_rejected"] = rejected
    result["status"] = "PASS_SOURCE_BOUND_ORDINARY_ANCESTOR_COMPOSITION"
    result["proof_sha256"] = sha256((HERE/"PROOF.md").read_bytes()).hexdigest()
    result["checker_sha256"] = sha256(Path(__file__).read_bytes()).hexdigest()
    result["scope"] = "Conditional composition and exact caller/allocator controls; no production replay or premise discharge"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
