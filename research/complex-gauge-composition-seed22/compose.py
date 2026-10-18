# SPDX-License-Identifier: Apache-2.0
"""Re-optimize one time-varying helper on top of a pinned many-gauge word."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PR1263 = HERE / "vendor/pr1263"
PR1259 = HERE / "vendor/pr1259"
SEED = 22
HELPER = 248  # sorted eligible-helper index 22 in PR1263's 237-entry inventory
PR1259_HELPER = 276


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def blob_sha1(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def verify_file_record(data, record, label):
    need(digest(data) == record["sha256"], "SHA256 source pin " + label)
    need(blob_sha1(data) == record["git_blob_sha1"], "Git blob source pin " + label)


def verify_sources():
    manifest = json.loads((HERE / "SOURCES.json").read_bytes())
    need(manifest["base_commit"] == "bce54fb3f895cbe5cd4c0eb477c3afeed100190f", "exact base commit")
    need(manifest["predecessor_heads"] == {
        "1259": "61367611154266a982fe25e1a6243a8aad77227d",
        "1263": "5fbaca13028846bddbb001e8e07addc2ab8e5816",
    }, "exact predecessor heads")
    for name, entry in manifest["files"].items():
        root = HERE if entry["location"] == "package" else ROOT
        verify_file_record((root / name).read_bytes(), entry, name)
    return manifest


def power2(k):
    return F(2) ** k


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_pr1263():
    module = load_module("pr1263_independent", PR1263 / "independent.py")
    module.HERE = PR1263
    module.ROOT = ROOT
    return module


def load_lowerer():
    module = load_module("retained_pr696_lowerer", ROOT / "research/complex-dyadic-lowering/lower.py")
    return module


def verify_pr1259_pins():
    pins = json.loads((PR1259 / "SOURCES.json").read_bytes())
    for name, expected in pins["files"].items():
        raw = (ROOT / name).read_bytes()
        normalized = raw if name.endswith(".gz") else raw.replace(b"\r\n", b"\n")
        need(digest(normalized) == expected, "PR1259 input hash " + name)
    if pins.get("archive_members"):
        with tarfile.open(ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz") as archive:
            for name, expected in pins["archive_members"].items():
                member = "candidate/strict/global8/base/providers/gauge44/" + name.rsplit("/", 1)[-1]
                raw = archive.extractfile(member).read()
                need(digest(raw) == expected, "PR1259 archive member " + name)
    return pins


def fraction_from_gate(gate):
    return F(gate[3], gate[4])


def odd_power(q):
    q = abs(F(q))
    n, d = q.numerator, q.denominator
    exponent = 0
    while n % 2 == 0:
        n //= 2
        exponent += 1
    while d > 1:
        need(d % 2 == 0, "non-dyadic denominator")
        d //= 2
        exponent -= 1
    need(n % 2 == 1, "odd numerator")
    return n, exponent


def add_price(lower, q):
    q = F(q)
    return len(lower.lower(["add", ["L", 0], ["L", 1], q.numerator, q.denominator]))


def add_price_formula(q):
    """PR696 copy-init count derived independently from the lowered stream."""
    odd, exponent = odd_power(q)
    return 1 + odd.bit_length() + odd.bit_count() + abs(exponent) - int(odd == 1 and exponent == 0)


def terms_for_helper(events, gauges, helper, lower):
    """Return (index, q with other gauges applied, sign) for each incident ADD."""
    terms = []
    for i, event in enumerate(events):
        if event[0] != "scalar" or event[1][0] != "add":
            continue
        gate = event[1]
        target, source = gate[1], gate[2]
        sign = int(target == ["L", helper]) - int(source == ["L", helper])
        if not sign:
            continue
        other_shift = 0
        for s, register in ((1, target), (-1, source)):
            if register[0] == "L" and register[1] != helper:
                other_shift += s * gauges.get(register[1], 0)
        q = fraction_from_gate(gate) * power2(other_shift)
        terms.append((i, q, sign))
    need(terms, "helper incident ADDs")
    return terms


def optimize_path(terms, lower):
    """Exact DP on a proved finite interval for every integer exponent path."""
    breaks = {0}
    for _, q, sign in terms:
        need(add_price(lower, q) == add_price_formula(q), "baseline literal/add-price formula")
        _, exponent = odd_power(q)
        breaks.add(-sign * exponent)
    lo, hi = min(breaks), max(breaks)
    domain = range(lo, hi + 1)
    # Value tuple: real primitive cost, SCALE macro count, exponent L1, path.
    dp = {0: (0, 0, 0, ())}
    for _, q, sign in terms:
        following = {}
        for k in domain:
            adjusted = q * power2(sign * k)
            local = add_price(lower, adjusted)
            need(local == add_price_formula(adjusted), "candidate literal/add-price formula")
            following[k] = min(
                (value[0] + abs(k - previous) + local,
                 value[1] + int(k != previous),
                 value[2] + abs(k),
                 value[3] + (k,))
                for previous, value in dp.items()
            )
        dp = following
    best = min((value[0] + abs(k), value[1] + int(k != 0), value[2], value[3])
               for k, value in dp.items())
    path = tuple(best[3])
    schedule = [[term[0], k] for term, k in zip(terms, path)]
    static_k = None
    need(len(schedule) == len(terms), "complete exponent path")
    return {
        "domain": [lo, hi],
        "incident_adds": len(terms),
        "score_real": best[0],
        "scale_macros": best[1],
        "exponent_l1": best[2],
        "schedule": schedule,
        "breakpoints": sorted(breaks),
    }


def static_helper_score(terms, k, lower):
    return 2 * abs(k) + sum(add_price(lower, q * power2(sign * k)) for _, q, sign in terms)


def mixed_word(events, word, gauges, schedule, helper=HELPER, omit_transition=None):
    """Compose static gauges except one helper with its absolute changing gauge."""
    by_index = {i: k for i, k in schedule}
    need(len(by_index) == len(schedule), "duplicate dynamic event")
    need(word["start"][helper] == 0 and word["final"][helper] == 1, "cold/FULL helper")
    static = {h: k for h, k in gauges.items() if h != helper and k}
    out = [deepcopy(events[0])]
    for h, k in sorted(static.items()):
        q = power2(k)
        out.append(["scalar", ["scale", ["L", h], q.numerator, q.denominator], word["start"][h]])
    current = 0
    for i, original in enumerate(events[1:-1], start=1):
        event = deepcopy(original)
        if i in by_index:
            new = by_index[i]
            if new != current and i != omit_transition:
                q = power2(new - current)
                out.append(["scalar", ["scale", ["L", helper], q.numerator, q.denominator], event[2]])
            current = new
        if event[0] == "scalar" and event[1][0] == "add":
            gate = event[1]
            target, source = gate[1], gate[2]
            shift = 0
            if target[0] == "L":
                shift += current if target[1] == helper else static.get(target[1], 0)
            if source[0] == "L":
                shift -= current if source[1] == helper else static.get(source[1], 0)
            q = fraction_from_gate(gate) * power2(shift)
            gate[3:5] = [q.numerator, q.denominator]
        out.append(event)
    if current:
        q = power2(-current)
        out.append(["scalar", ["scale", ["L", helper], q.numerator, q.denominator], word["final"][helper]])
    for h, k in sorted(static.items()):
        q = power2(-k)
        out.append(["scalar", ["scale", ["L", h], q.numerator, q.denominator], word["final"][h]])
    out.append(deepcopy(events[-1]))
    need(out[0] == events[0] and out[-1] == events[-1], "phase boundaries")
    need([e for e in out if e[0] != "scalar"] == [e for e in events if e[0] != "scalar"],
         "non-scalar schedule unchanged")
    return out


def exact_columns(events, orientation):
    """Evaluate the macro stream on all 712 independent initial coordinates."""
    rows = {("L", i): {i: F(1)} for i in range(704)}
    rows.update({("C", i): {704 + i: F(1)} for i in range(8)})
    for event in events:
        if event[0] != "scalar":
            continue
        gate = event[1]
        tag, target = gate[0], tuple(gate[1])
        if tag == "clear":
            rows[target] = {}
        elif tag == "copy":
            rows[target] = dict(rows[tuple(gate[2])])
        elif tag == "scale":
            q = F(gate[2], gate[3])
            rows[target] = {i: q * a for i, a in rows[target].items() if q * a}
        elif tag == "add":
            source, q = tuple(gate[2]), F(gate[3], gate[4])
            need(target != source, "distinct ADD operands")
            result = dict(rows[target])
            for i, a in rows[source].items():
                result[i] = result.get(i, F(0)) + q * a
                if result[i] == 0:
                    del result[i]
            rows[target] = result
        else:
            raise ValueError("unknown scalar macro " + tag)
    for i in range(112):
        expected_x = {i: F(1)}
        expected_y = {112 + i: F(1)}
        if orientation == "forward":
            expected_y[i] = F(1)
        else:
            expected_x[112 + i] = F(-1)
        need(rows["L", i] == expected_x, "data endpoint X " + str(i))
        need(rows["L", 112 + i] == expected_y, "data endpoint Y " + str(i))
    for i in range(224, 704):
        need(rows["L", i] == {i: F(1)}, "dirty helper restoration " + str(i))
    need(all(not rows["C", i] for i in range(8)), "private-center clearing")
    return {"formal_columns": 712, "data_coordinates": 224,
            "dirty_helpers": 480, "dirty_centers": 8}


def compile_word(events, lower):
    operations = []
    for event in events:
        if event[0] == "scalar":
            operations.extend(lower.lower(event[1]))
    return operations


def execute(operations, initial, positive=False):
    state = initial.copy()
    peak = max(state.values()) if positive else F(0)
    for op in operations:
        tag, target = op[:2]
        if tag == "clear":
            state[target] = F(0)
        elif tag == "copy":
            state[target] = state[op[2]]
        elif tag == "double":
            state[target] *= 2
        elif tag == "halve":
            state[target] /= 2
        elif tag == "negate":
            if not positive:
                state[target] = -state[target]
        elif tag in ("add", "subtract"):
            state[target] += state[op[2]] * (1 if positive or tag == "add" else -1)
        else:
            raise ValueError("unknown primitive " + tag)
        if positive:
            peak = max(peak, state[target])
    return state, peak


def denominator_depth(operations, registers):
    depths = {r: 0 for r in registers}
    peak = 0
    for op in operations:
        tag, target = op[:2]
        if tag == "clear":
            depths[target] = 0
        elif tag == "copy":
            depths[target] = depths[op[2]]
        elif tag == "double":
            depths[target] = max(0, depths[target] - 1)
        elif tag == "halve":
            depths[target] += 1
        elif tag in ("add", "subtract"):
            depths[target] = max(depths[target], depths[op[2]])
        elif tag != "negate":
            raise ValueError("unknown primitive " + tag)
        peak = max(peak, depths[target])
    return peak


def local_invoice(events, lower, orientation):
    operations = compile_word(events, lower)
    registers = ([('L', i) for i in range(704)] + [('C', i) for i in range(8)] + [('W', 0)])
    _, peak = execute(operations, {r: F(1) for r in registers}, positive=True)
    need(peak < 2 ** 192, "retained local 192-bit payload cap")
    paid = Counter()
    for event in events:
        if event[0] == "climb":
            paid[event[5]] += 1
        elif event[0] == "center":
            paid[event[4]] += 1
    return {
        "real_primitives": len(operations),
        "complex_primitives": 2 * len(operations),
        "positive_prefix_l1": str(peak),
        "positive_prefix_bits": peak.numerator.bit_length() - peak.denominator.bit_length() + 1,
        "denominator_depth": denominator_depth(operations, registers),
        "paid_profile": {str(k): v for k, v in sorted(paid.items())},
        "orientation": orientation,
    }


def check_dirty_primitives(operations, orientation):
    registers = ([('L', i) for i in range(704)] + [('C', i) for i in range(8)] + [('W', 0)])
    rng = random.Random(29)
    for case in range(3):
        initial = {r: F(rng.randrange(-20000, 20001), 2 ** rng.randrange(5)) for r in registers}
        if case == 1:
            initial.update({('L', i): F((-1) ** i * (i + 1) ** 3, 8) for i in range(224, 704)})
        if case == 2:
            initial.update({('L', i): F(0) for i in range(224)})
        expected = initial.copy()
        for i in range(112):
            if orientation == "forward":
                expected['L', 112 + i] += initial['L', i]
            else:
                expected['L', i] -= initial['L', 112 + i]
        expected.update({('C', i): F(0) for i in range(8)})
        expected['W', 0] = F(0)
        actual, _ = execute(operations, initial)
        need(actual == expected, "primitive dirty-state endpoint case " + str(case))
    return 3


def verify_pr1259_candidate(certificate, word, programs, lower):
    search = load_module("pr1259_search", PR1259 / "search.py")
    results = {}
    for orientation in ("forward", "backward"):
        saved = certificate["orientations"][orientation]
        helper = saved["winner"]["helper"]
        schedule = saved["winner"]["schedule"]
        need(helper == PR1259_HELPER, "PR1259 L276 predecessor identity")
        candidate = search.transform(programs[orientation], word, helper, schedule)
        need(digest(canonical(candidate)) == saved["candidate_sha256"],
             "PR1259 predecessor candidate hash " + orientation)
        before = local_invoice(programs[orientation], lower, orientation)
        after = local_invoice(candidate, lower, orientation)
        need(after["complex_primitives"] == saved["after"]["complex_primitives"],
             "PR1259 predecessor full price " + orientation)
        need(before["complex_primitives"] - after["complex_primitives"] == 344,
             "PR1259 predecessor saving " + orientation)
        results[orientation] = {"candidate_sha256": digest(canonical(candidate)),
                                "saved_complex": 344}
    return results


def compute():
    verify_sources()
    pr1263 = load_pr1263()
    # This exact replay checks the predecessor's selected-source pins, all-712
    # baseline/candidate maps, literal PR696 invoices and its 13,000 saving.
    baseline_independent = pr1263.run()
    pr1263_cert = json.loads((PR1263 / "CERTIFICATE.json").read_bytes())
    gauges_raw = json.loads((PR1263 / "GAUGES.json").read_bytes())
    eligible = pr1263_cert["eligible_helpers"]
    need(len(eligible) == 237 and eligible == sorted(set(eligible)), "PR1263 sorted eligible inventory")
    need(eligible[SEED] == HELPER and not 37 <= SEED < 53, "OS seed selects helper outside PR1259 slice")
    pr1259_pins = verify_pr1259_pins()
    pr1259_cert = json.loads((PR1259 / "CERTIFICATE.json").read_bytes())
    word, programs = pr1263.source()
    lower = load_lowerer()
    pr1259_validation = verify_pr1259_candidate(pr1259_cert, word, programs, lower)
    result = {
        "status": "PASS_SEED22_HELPER248_DYNAMIC_ON_217_STATIC_GAUGES",
        "assignment_seed_os_random": SEED,
        "helper_selection": {"eligible_count": 237, "zero_based_sorted_index": SEED,
                             "helper": HELPER, "pr1259_seed37_slice": [37, 53]},
        "base": "bce54fb3f895cbe5cd4c0eb477c3afeed100190f",
        "predecessors": {
            "pr1259_head": "61367611154266a982fe25e1a6243a8aad77227d",
            "pr1263_head": "5fbaca13028846bddbb001e8e07addc2ab8e5816",
            "pr1259_source_base": pr1259_pins["base"],
            "pr1263_source_base": pr1263_cert["base"],
        },
        "pr1259_candidate_replay": pr1259_validation,
        "pr1263_independent_replay": baseline_independent,
        "orientations": {},
    }
    for orientation in ("forward", "backward"):
        events = programs[orientation]
        gauges = {int(h): int(k) for h, k in gauges_raw[orientation].items()}
        need(HELPER in gauges, "seed-selected L248 is in PR1263's static support")
        terms = terms_for_helper(events, gauges, HELPER, lower)
        optimum = optimize_path(terms, lower)
        static_score = static_helper_score(terms, gauges[HELPER], lower)
        need(optimum["score_real"] <= static_score, "dynamic class contains static gauge")
        candidate = mixed_word(events, word, gauges, optimum["schedule"])
        exact = exact_columns(candidate, orientation)
        invoice = local_invoice(candidate, lower, orientation)
        static_invoice = pr1263_cert["orientations"][orientation]["candidate"]
        need(invoice["real_primitives"] - static_invoice["real_primitives"] ==
             optimum["score_real"] - static_score,
             "full-word bill equals local dynamic objective difference")
        paid_events = [event for event in candidate if event[0] != "scalar"]
        static_paid_events = [event for event in pr1263.reconstruct(word, events, gauges)
                              if event[0] != "scalar"]
        need(paid_events == static_paid_events, "paid recursive and frame events unchanged")
        need(invoice["paid_profile"] == static_invoice["paid_profile"], "recursive paid profile unchanged")
        primitive_controls = check_dirty_primitives(compile_word(candidate, lower), orientation)
        need(digest(canonical(candidate)) != pr1263_cert["orientations"][orientation]["candidate_sha256"] or
             optimum["score_real"] == static_score,
             "different emitted word only for a priced improvement")
        result["orientations"][orientation] = {
            "helper": HELPER,
            "static_gauge_on_helper": gauges[HELPER],
            "incident_adds": optimum["incident_adds"],
            "finite_domain": optimum["domain"],
            "breakpoints": optimum["breakpoints"],
            "dynamic_score_real": optimum["score_real"],
            "static_helper_score_real": static_score,
            "saving_vs_pr1263_real": static_score - optimum["score_real"],
            "saving_vs_pr1263_complex": 2 * (static_score - optimum["score_real"]),
            "scale_macros_for_helper": optimum["scale_macros"],
            "schedule": optimum["schedule"],
            "candidate_sha256": digest(canonical(candidate)),
            "candidate_invoice": invoice,
            "dirty_primitive_cases": primitive_controls,
            "paid_event_sha256": digest(canonical(paid_events)),
            "predecessor_paid_profile": static_invoice["paid_profile"],
            "exact_endpoint": exact,
            "original_complex_primitives": pr1263_cert["orientations"][orientation]["baseline"]["complex_primitives"],
            "pr1263_complex_primitives": static_invoice["complex_primitives"],
            "total_saving_vs_pr1094_complex": pr1263_cert["orientations"][orientation]["baseline"]["complex_primitives"] - invoice["complex_primitives"],
            "non_scalar_events_unchanged": True,
        }
    forward = result["orientations"]["forward"]["schedule"]
    backward = result["orientations"]["backward"]["schedule"]
    need(backward == [[index, -exponent] for index, exponent in forward],
         "independently optimized reverse schedule is exact inverse")
    return result


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2, sort_keys=True))
