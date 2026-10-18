#!/usr/bin/env python3
"""Temporal Gaussian common rounding; Sagar Thakrar with OpenAI Codex.

Apache-2.0. Extends Hanson Sun's PR1490 static rounding argument. PR696's
real lowerer is the only imported implementation. Default replay is read-only.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "ef5f39403610d231a0c27e8a6b4f08c10209bcd6"
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
LOWER = "research/complex-dyadic-lowering/lower.py"
INPUTS = {ARCHIVE, LOWER}
ONE, ZERO = (Q(1), Q(0)), (Q(0), Q(0))
IDENTITY = (0, 0)
STATES = tuple([(a, 0) for a in range(-4, 5)] + [(a, 1) for a in range(-4, 4)])
REAL_STATES = tuple(s for s in STATES if s[1] == 0)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sources(reader=None):
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    rows = [x for x in manifest["files"] if x["usage"] == "input"]
    need(manifest["base_commit"] == BASE, "base pin")
    need(len(rows) == len(INPUTS) and {x["path"] for x in rows} == INPUTS,
         "input inventory")
    read = reader or (lambda name: (ROOT / name).read_bytes())
    for row in rows:
        data = read(row["path"])
        need(digest(data) == row["sha256"], "source SHA256 " + row["path"])
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        need(blob == row["git_blob"], "source Git blob " + row["path"])


@lru_cache(maxsize=1)
def lowerer():
    spec = importlib.util.spec_from_file_location("pr696", ROOT / LOWER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.lower


def pow2(a):
    return Q(2 ** a) if a >= 0 else Q(1, 2 ** -a)


def mul(z, w):
    return z[0] * w[0] - z[1] * w[1], z[0] * w[1] + z[1] * w[0]


def inv(z):
    norm = z[0] ** 2 + z[1] ** 2
    need(norm != 0, "nonzero factor")
    return z[0] / norm, -z[1] / norm


def factor(state, phase=0):
    a, b = state
    need(b in (0, 1) and phase in range(4), "unit parameters")
    return mul((pow2(a), b * pow2(a)), (ONE, (Q(0), Q(1)), (-Q(1), Q(0)), (Q(0), -Q(1)))[phase])


def c(q):
    q = Q(q)
    need(q and q.denominator & (q.denominator - 1) == 0, "nonzero dyadic")
    n = abs(q.numerator)
    twos = (n & -n).bit_length() - 1
    odd, exponent = n >> twos, twos - (q.denominator.bit_length() - 1)
    return 1 + odd.bit_length() + odd.bit_count() + abs(exponent) - int(abs(q) == 1)


def add_cost(z):
    need(z != ZERO and (not z[0] or not z[1] or abs(z[0]) == abs(z[1])), "axis/diagonal coefficient")
    return 2 * c(z[0] or z[1]) + 2 * bool(z[0] and z[1])


def transition_cost(old, new):
    da, db = new[0] - old[0], new[1] - old[1]
    return abs(2 * da + db) + 2 * abs(db)


def reverse(word):
    inverse = {"add": "subtract", "subtract": "add", "double": "halve",
               "halve": "double", "negate": "negate"}
    return [(inverse[g[0]], *g[1:]) for g in reversed(word)]


def entry(state, registers, phase=0):
    a, b = state
    x, y = registers
    if not b:
        shift, end = a, []
    elif a >= 0:
        shift, end = a, [("add", y, x), ("double", x), ("subtract", x, y)]
    else:
        shift, end = a + 1, [("subtract", x, y), ("halve", x), ("add", y, x)]
    word = [("double" if shift > 0 else "halve", r) for r in registers for _ in range(abs(shift))] + end
    quarter = [("subtract", x, y), ("add", y, x), ("subtract", x, y)]
    word += [[], quarter, [("negate", x), ("negate", y)], reverse(quarter)][phase]
    return word


def transition(old, new, registers):
    da, db = new[0] - old[0], new[1] - old[1]
    if db >= 0:
        result = entry((da, db), registers)
    else:
        result = reverse(entry((-da, -db), registers))
    need(len(result) == transition_cost(old, new), "transition attainment")
    return result


def gaussian_add(z, target, source):
    need(target != source, "distinct operands")
    add_cost(z)
    result = []
    for channel, coefficients in enumerate(((z[0], z[1]), (-z[1], z[0]))):
        src, work = source + (channel,), ("W", channel)
        uses = [(target + (i,), q) for i, q in enumerate(coefficients) if q]
        dst, q = uses[0]
        word = lowerer()(["add", dst, src, q.numerator, q.denominator], work=work)
        if len(uses) == 2:
            dst2, q2 = uses[1]
            word.insert(len(word) - 1, ("add" if q2 > 0 else "subtract", dst2,
                                       src if abs(q) == 1 else work))
        result += word
    need(len(result) == add_cost(z), "ADD invoice")
    return result


def matrix(word, registers):
    size = len(registers)
    rows = {r: [Q(int(i == j)) for j in range(size)] for i, r in enumerate(registers)}
    for g in word:
        tag, dst = g[:2]
        if tag in ("add", "subtract"):
            sign = 1 if tag == "add" else -1
            rows[dst] = [x + sign * y for x, y in zip(rows[dst], rows[g[2]])]
        elif tag == "copy":
            rows[dst] = list(rows[g[2]])
        elif tag == "clear":
            rows[dst] = [Q(0)] * size
        else:
            need(tag in ("double", "halve", "negate"), "primitive opcode")
            scale = {"double": Q(2), "halve": Q(1, 2), "negate": Q(-1)}[tag]
            rows[dst] = [x * scale for x in rows[dst]]
    return [rows[r] for r in registers]


def local_checks():
    registers = tuple((i,) for i in range(2))
    states = [(a, b, j) for a in range(-3, 4) for b in range(2) for j in range(4)]
    transition_cases = 0
    for old, new in itertools.product(states, repeat=2):
        word = reverse(entry(old[:2], registers, old[2])) + entry(new[:2], registers, new[2])
        z = mul(factor(new[:2], new[2]), inv(factor(old[:2], old[2])))
        need(matrix(word, registers) == [[z[0], -z[1]], [z[1], z[0]]], "phased transition map")
        floor = transition_cost(old[:2], new[:2])
        need(len(word) >= floor, "transition lower bound")
        rounded = [2 * abs(new[0] + t * new[1] - old[0] - t * old[1]) for t in (0, 1)]
        need(2 * floor == sum(rounded) + 4 * abs(new[1] - old[1]), "transition rounding identity")
        optimal = transition(old[:2], new[:2], registers)
        expected = mul(factor(new[:2]), inv(factor(old[:2])))
        need(matrix(optimal, registers) == [[expected[0], -expected[1]], [expected[1], expected[0]]], "attaining transition map")
        transition_cases += 1
    coefficients, inequalities = set(), 0
    for odd, exponent, sign, da, bs, bt, phase in itertools.product(
            range(1, 16, 2), range(-5, 6), (-1, 1), range(-6, 7), range(2), range(2), range(4)):
        q = sign * odd * pow2(exponent)
        z = mul((q, Q(0)), mul(factor((da, bt), phase), inv(factor((0, bs)))))
        rounded = [2 * c(q * pow2(da + t * (bt - bs))) for t in (0, 1)]
        need(2 * add_cost(z) >= sum(rounded), "ADD common rounding")
        coefficients.add(z)
        inequalities += 1
    regs = (("T", 0), ("T", 1), ("S", 0), ("S", 1), ("W", 0), ("W", 1))
    for z in sorted(coefficients):
        got = matrix(gaussian_add(z, ("T",), ("S",)), regs)
        expected = [[Q(int(i == j)) for j in range(6)] for i in range(6)]
        expected[0][2:4], expected[1][2:4] = [z[0], -z[1]], [z[1], z[0]]
        expected[4], expected[5] = [Q(0)] * 6, [Q(0)] * 6
        need(got == expected, "six-column dirty Gaussian ADD")
    return {"transition_cases_all_four_phases": transition_cases,
            "add_inequalities": inequalities, "distinct_literal_add_macros": len(coefficients)}


def load():
    prefix = "candidate/strict/global8/base/providers/gauge44/"
    with tarfile.open(ROOT / ARCHIVE) as archive:
        raw = {n: archive.extractfile(prefix + n).read() for n in (
            "CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz", "INDEPENDENT-LOCAL-REPLAY.json")}
    word, programs = [json.loads(gzip.decompress(raw[n])) for n in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz")]
    receipt = json.loads(raw["INDEPENDENT-LOCAL-REPLAY.json"])
    for name, field in [("CANONICAL-WORD.json.gz", "canonical_word_sha256"), ("LOCAL-PROGRAMS.json.gz", "local_programs_sha256")]:
        need(receipt[field] == digest(raw[name]), "retained receipt binding")
    need((word["v"], word["R"]) == (112, 480), "selected dimensions")
    excluded = set(word["centers"])
    for events in programs.values():
        for e in events:
            if e[0] == "residual_adapter":
                excluded.add(e[2])
            if e[0] == "scalar" and e[1][0] in ("copy", "clear"):
                excluded.update(r[1] for r in e[1][1:] if isinstance(r, list) and r[0] == "L")
    helpers = {h for h in range(224, 704) if h not in excluded and word["start"][h] == 0 and word["final"][h] == 1}
    edges = sorted({tuple(sorted((e[1][1][1], e[1][2][1]))) for events in programs.values() for e in events
                    if e[0] == "scalar" and e[1][0] == "add" and e[1][1][0] == e[1][2][0] == "L"
                    and e[1][1][1] in helpers and e[1][2][1] in helpers})
    need(len(helpers) == 237 and len(edges) == 2414 and edges[22] == (225, 340), "seed-selected interaction")
    return programs, edges[22], {n: digest(b) for n, b in raw.items()}


def segments(events, helper):
    answer, current = [], []
    for index, e in enumerate(events):
        if e[0] != "scalar":
            if current:
                answer.append(current)
                current = []
        elif e[1][0] == "add" and ["L", helper] in e[1][1:3]:
            g = e[1]
            current.append((index, Q(g[3], g[4]), 1 if g[1] == ["L", helper] else -1))
    if current:
        answer.append(current)
    return answer


def solve(events, helper, states):
    # Segment checkpoints are identity. The boolean records an actual odd use.
    total = {False: (0, {})}
    evaluations = 0
    for block in segments(events, helper):
        dp = {(IDENTITY, False): (0, ())}
        for index, q, direction in block:
            nxt = {}
            for state in states:
                f = factor(state)
                coefficient = mul((q, Q(0)), f if direction == 1 else inv(f))
                fee = add_cost(coefficient)
                for (old, seen), (price, path) in dp.items():
                    key = (state, seen or bool(state[1]))
                    candidate = (price + transition_cost(old, state) + fee, path + (state,))
                    if key not in nxt or candidate < nxt[key]:
                        nxt[key] = candidate
                    evaluations += 1
            dp = nxt
        best = {}
        for (state, seen), (price, path) in dp.items():
            candidate = (price + transition_cost(state, IDENTITY), path)
            if seen not in best or candidate < best[seen]:
                best[seen] = candidate
        nxt_total = {}
        for had, (cost, history) in total.items():
            for seen, (price, path) in best.items():
                key = had or seen
                schedule = dict(history)
                schedule.update((row[0], list(state)) for row, state in zip(block, path))
                candidate = (cost + price, schedule)
                if key not in nxt_total or candidate[0] < nxt_total[key][0]:
                    nxt_total[key] = candidate
        total = nxt_total
    return total, evaluations


def stream(events, schedules, theta=None):
    states = {h: IDENTITY for h in schedules}
    for index, e in enumerate(events):
        desired = dict(states)
        if e[0] != "scalar":
            desired = {h: IDENTITY for h in schedules}
        else:
            for h, schedule in schedules.items():
                if index in schedule:
                    a, b = schedule[index]
                    desired[h] = (a, b) if theta is None else (a + theta * b, 0)
        for h, state in desired.items():
            if state != states[h]:
                yield ("transition", h, states[h], state)
        states = desired
        if e[0] == "scalar" and e[1][0] == "add":
            g = e[1]
            fs = [factor(states.get(r[1], IDENTITY)) if r[0] == "L" else ONE for r in g[1:3]]
            z = mul((Q(g[3], g[4]), Q(0)), mul(fs[0], inv(fs[1])))
            yield ("add", tuple(g[1]), tuple(g[2]), z)
        else:
            yield ("original", e)
    for h, state in states.items():
        if state != IDENTITY:
            yield ("transition", h, state, IDENTITY)


def primitives(item):
    if item[0] == "transition":
        _, h, old, new = item
        return transition(old, new, (("L", h, 0), ("L", h, 1)))
    if item[0] == "add":
        return gaussian_add(item[3], item[1], item[2])
    e = item[1]
    if e[0] != "scalar":
        return []
    g, result = e[1], []
    for channel in (0, 1):
        dst = tuple(g[1]) + (channel,)
        op = [g[0], dst]
        if g[0] == "copy":
            op += [tuple(g[2]) + (channel,)]
        elif g[0] == "scale":
            op += g[2:4]
        else:
            need(g[0] == "clear", "retained scalar opcode")
        result += lowerer()(op, work=("W", channel))
    return result


def replay(events, schedules, orientation, theta=None):
    rows = {("L", i): {i: ONE} for i in range(704)}
    rows.update({("C", i): {704 + i: ONE} for i in range(8)})
    envelopes = {r + (c,): Q(1) for r in rows for c in (0, 1)}
    envelopes.update({("W", c): Q(1) for c in (0, 1)})
    peak, count, changes, odd_changes, shared = Q(1), 0, 0, 0, 0
    primitive_hash, macro_hash = hashlib.sha256(), hashlib.sha256()
    paid = Counter()
    def scale(dst, z):
        rows[dst] = {i: mul(v, z) for i, v in rows[dst].items()}
    for item in stream(events, schedules, theta):
        macro_hash.update(repr(item).encode() + b"\n")
        if item[0] == "transition":
            _, h, old, new = item
            scale(("L", h), mul(factor(new), inv(factor(old))))
            changes += 1
            odd_changes += abs(new[1] - old[1])
        elif item[0] == "add":
            _, dst, src, z = item
            if dst[0] == src[0] == "L" and dst[1] in schedules and src[1] in schedules:
                shared += 1
            for i, v in rows[src].items():
                term, before = mul(v, z), rows[dst].get(i, ZERO)
                after = before[0] + term[0], before[1] + term[1]
                if after == ZERO:
                    rows[dst].pop(i, None)
                else:
                    rows[dst][i] = after
        else:
            e = item[1]
            if e[0] == "scalar":
                g, dst = e[1], tuple(e[1][1])
                if g[0] == "scale":
                    scale(dst, (Q(g[2], g[3]), Q(0)))
                elif g[0] == "copy":
                    rows[dst] = dict(rows[tuple(g[2])])
                else:
                    need(g[0] == "clear", "replay scalar opcode")
                    rows[dst] = {}
            elif e[0] == "climb":
                paid[e[5]] += 1
            elif e[0] == "center":
                paid[e[4]] += 1
        for g in primitives(item):
            count += 1
            primitive_hash.update(canonical(g) + b"\n")
            tag, dst = g[:2]
            if tag in ("add", "subtract"):
                envelopes[dst] += envelopes[g[2]]
            elif tag == "copy":
                envelopes[dst] = envelopes[g[2]]
            elif tag == "clear":
                envelopes[dst] = Q(0)
            elif tag == "double":
                envelopes[dst] *= 2
            elif tag == "halve":
                envelopes[dst] /= 2
            else:
                need(tag == "negate", "envelope opcode")
            peak = max(peak, envelopes[dst])
    for i in range(704):
        expected = {i: ONE}
        if orientation == "forward" and 112 <= i < 224:
            expected[i - 112] = ONE
        if orientation == "backward" and i < 112:
            expected[i + 112] = (-Q(1), Q(0))
        need(rows["L", i] == expected, "complete dirty endpoint " + str(i))
    need(all(not rows["C", i] for i in range(8)), "private centers cleared")
    need(envelopes["W", 0] == envelopes["W", 1] == 0, "coefficient scratch cleared")
    need(peak < 2 ** 192, "retained 192-bit local envelope")
    return {"scalar_primitives": count, "transitions": changes, "odd_transitions": odd_changes,
            "shared_adds": shared, "primitive_sha256": primitive_hash.hexdigest(),
            "macro_sha256": macro_hash.hexdigest(), "positive_prefix_l1": str(peak),
            "paid_profile": {str(k): v for k, v in sorted(paid.items())},
            "complex_columns": 712, "real_columns": 1424}


def controls():
    names = []
    def reject(name, action):
        try:
            action()
        except ValueError:
            names.append(name)
        else:
            raise ValueError("control accepted: " + name)
    reject("unit discount cannot use Lipschitz one", lambda: need(c(Q(2)) - c(Q(1)) <= 1, "unit discount"))
    reject("independent helper rounding", lambda: need(2 * c(Q(1)) >= 2 * c(Q(2)), "shared equal-odd edge"))
    reject("independent time rounding", lambda: need(transition_cost((0, 1), (0, 1)) >= 2, "constant gauge becomes nonconstant"))
    reject("free odd transition", lambda: need(transition_cost(IDENTITY, (0, 1)) == 1, "two mixing additions"))
    regs = (("T", 0), ("T", 1), ("S", 0), ("S", 1), ("W", 0), ("W", 1))
    good = gaussian_add((Q(1), Q(1)), ("T",), ("S",))
    truth = matrix(good, regs)
    reject("uncleared dirty coefficient work", lambda: need(matrix(good[:-1], regs) == truth, "dirty work"))
    bad = list(good)
    pos = next(i for i, g in enumerate(bad) if g[0] == "subtract")
    bad[pos] = ("add", *bad[pos][1:])
    reject("wrong cross-channel sign", lambda: need(matrix(bad, regs) == truth, "complex product"))
    registers = ((0,), (1,))
    forward = entry((0, 1), registers)
    reject("omitted inverse transition", lambda: need(matrix(forward, registers) == [[1, 0], [0, 1]], "return dirt"))
    reject("nondyadic coefficient", lambda: c(Q(1, 3)))
    reject("nonunit-shaped coefficient", lambda: add_cost((Q(1), Q(2))))
    reject("aliased operands", lambda: gaussian_add(ONE, ("T",), ("T",)))
    reject("modified source", lambda: sources(lambda name: (ROOT / name).read_bytes() + b"\n"))
    return names


def brute_force_planner():
    """A literal word enumeration checks both dirty orientations and all cuts."""
    states = ((0, 0), (1, 0), (0, 1))
    registers = (("L", 225, 0), ("L", 225, 1))
    cases, paths = 0, 0
    for directions, cuts in itertools.product(itertools.product((-1, 1), repeat=3), range(4)):
        events = []
        for i, (q, direction) in enumerate(zip((Q(-1, 2), Q(3, 2), Q(-2)), directions)):
            target, source = (["L", 225], ["L", 0]) if direction == 1 else (["L", 0], ["L", 225])
            events.append(["scalar", ["add", target, source, q.numerator, q.denominator], 0])
            if i < 2 and cuts & (1 << i):
                events.append(["phase", "checkpoint"])
        expected = {}
        for assignment in itertools.product(states, repeat=3):
            word, old, index = [], IDENTITY, 0
            for event in events:
                if event[0] != "scalar":
                    word += transition(old, IDENTITY, registers)
                    old = IDENTITY
                    continue
                state = assignment[index]
                word += transition(old, state, registers)
                g = event[1]
                z = factor(state)
                if directions[index] == -1:
                    z = inv(z)
                word += gaussian_add(mul((Q(g[3], g[4]), Q(0)), z), tuple(g[1]), tuple(g[2]))
                old, index = state, index + 1
            word += transition(old, IDENTITY, registers)
            odd = any(s[1] for s in assignment)
            expected[odd] = min(expected.get(odd, len(word)), len(word))
            paths += 1
        computed, _ = solve(events, 225, states)
        need({k: v[0] for k, v in computed.items()} == expected, "exhaustive tiny planner")
        cases += 1
    return {"signed_checkpoint_cases": cases, "literal_paths": paths}


def result():
    sources()
    local = local_checks()
    programs, pair, pins = load()
    outputs, optimization = {}, []
    for orientation, events in sorted(programs.items()):
        schedules = {}
        for h in pair:
            gaussian, ge = solve(events, h, STATES)
            real, re = solve(events, h, REAL_STATES)
            need(gaussian[False][0] == real[False][0], "real subdomain optimum")
            need(gaussian[True][0] >= real[False][0] + 4, "forced odd episode floor")
            schedules[h] = gaussian[True][1]
            optimization.append({"orientation": orientation, "helper": h,
                                 "real_incident_cost": real[False][0], "forced_odd_incident_cost": gaussian[True][0],
                                 "candidate_transitions": ge + re,
                                 "schedule": {str(i): state for i, state in gaussian[True][1].items()}})
        base = replay(events, {}, orientation)
        variants = {"gaussian": replay(events, schedules, orientation),
                    "round0": replay(events, schedules, orientation, 0),
                    "round1": replay(events, schedules, orientation, 1)}
        g, r0, r1 = [variants[k] for k in ("gaussian", "round0", "round1")]
        need(g["odd_transitions"] >= 4 and g["odd_transitions"] % 2 == 0, "two closed odd schedules")
        need(2 * g["scalar_primitives"] >= r0["scalar_primitives"] + r1["scalar_primitives"] + 4 * g["odd_transitions"], "complete temporal inequality")
        need(all(v["paid_profile"] == base["paid_profile"] for v in variants.values()), "unchanged paid profile")
        need(base["scalar_primitives"] == (149002 if orientation == "forward" else 149018), "retained baseline invoice")
        shared_index = next(i for i, e in enumerate(events) if e[0] == "scalar" and e[1][0] == "add"
                            and all(e[1][j][0] == "L" and e[1][j][1] in pair for j in (1, 2)))
        mixed = {h: dict(schedule) for h, schedule in schedules.items()}
        a, b = mixed[pair[0]][shared_index]
        need(b == 0 and mixed[pair[1]][shared_index][1] == 0, "unmodified shared parity")
        mixed[pair[0]][shared_index] = [a, 1]
        mixed_variants = [replay(events, mixed, orientation, theta) for theta in (None, 0, 1)]
        mg, mr0, mr1 = mixed_variants
        need(2 * mg["scalar_primitives"] >= mr0["scalar_primitives"] + mr1["scalar_primitives"] + 4 * mg["odd_transitions"], "mixed shared-ADD rounding")
        need(all(v["paid_profile"] == base["paid_profile"] for v in mixed_variants), "mixed paid profile")
        outputs[orientation] = {"baseline": base, **variants,
                                "mixed_shared_add": {"event_index": shared_index, "changed_helper": pair[0],
                                                     "new_state": [a, 1], "gaussian": mg, "round0": mr0, "round1": mr1},
                                "twice_rounding_slack": 2 * g["scalar_primitives"] - r0["scalar_primitives"] - r1["scalar_primitives"] - 4 * g["odd_transitions"]}
    # One odd target helper, one incoming ADD of coefficient 1 attains equality.
    sharp = {"gaussian": 12, "round0": 4, "round1": 12, "odd_transitions": 2}
    need(transition_cost(IDENTITY, (0, 1)) * 2 + add_cost(factor((0, 1))) == 12, "sharp Gaussian invoice")
    need(2 * sharp["gaussian"] == sharp["round0"] + sharp["round1"] + 4 * sharp["odd_transitions"], "sharp penalty")
    return {"status": "PASS_TEMPORAL_GAUSSIAN_ROUNDING_NO_NEW_KAPPA", "base_commit": BASE,
            "seed": 22, "pair": pair, "domain": {"real_states": REAL_STATES, "gaussian_states": STATES,
            "checkpoints": "identity at every nonscalar event and call return", "stopping_rule": "all states at every incident ADD on the two selected helpers, both orientations"},
            "source_members": pins, "local_checks": local, "planner_check": brute_force_planner(), "optimization": optimization,
            "complete_fixtures": outputs, "sharp_penalty": sharp, "negative_controls": controls()}


if __name__ == "__main__":
    actual = result()
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(actual, sort_keys=True, indent=2))
    else:
        need(not sys.argv[1:], "usage: verify.py [--emit]")
        expected = json.loads((HERE / "RESULT.json").read_text())
        need(canonical(actual) == canonical(expected), "saved result mismatch")
        print(actual["status"], "pair=225,340 orientations=2 columns=712 controls=" + str(len(actual["negative_controls"])))
