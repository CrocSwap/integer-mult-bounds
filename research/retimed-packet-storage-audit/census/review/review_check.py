#!/usr/bin/env python3
"""Independent syntax, interval, custody and free-first checks for the owner census."""
from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
import hashlib
import importlib
import json
import sys
import tempfile

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
AUTHOR = BASE / "work-storage/wave2-stock"
RUNTIME = BASE / "work-storage/runtime-exact"
PROOF_PIN = "c3a4466317732d44c7c3c7e57e1180106a71d2fb3083152cb54b8b7971b35bf0"


def need(ok, message):
    if not ok:
        raise AssertionError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def bind_sources():
    need(sha(AUTHOR / "OWNER-CENSUS.md") == PROOF_PIN, "reviewed proof changed")
    (HERE / "tmp").mkdir(exist_ok=True)
    tempfile.tempdir = str(HERE / "tmp")
    sys.path.insert(0, str(RUNTIME))
    import upstream
    handles = upstream.install()
    manifest = json.loads((AUTHOR / "SOURCE-BINDINGS.json").read_text())
    records = {}
    for name, item in manifest["resolved_modules"].items():
        mod = importlib.import_module(name)
        path = Path(mod.__file__)
        need(sha(path) == item["sha256"], f"runtime binding differs: {name}")
        need(path.read_bytes() == (AUTHOR / "sources" / item["file"]).read_bytes(),
             f"author copy differs: {name}")
        records[name] = {"sha256": sha(path), "runtime_origin": str(path)}
    import installations
    need(installations.GAUSSIAN_C == Fraction(2092819, 2**29), "installed mass exponent")
    need(1 - installations.GAUSSIAN_C > Fraction(3, 4), "mass exponent range")
    records["installations"] = {"sha256": sha(Path(installations.__file__)),
                                "runtime_origin": str(Path(installations.__file__))}
    return handles, records


def syntax_inventory():
    from strong_complex import load_changed
    from closed_caller import templates, placement
    from mixed_caller import layout_bindings, instructions
    import tagged_sources

    graph, layout = load_changed(RUNTIME / "inputs")
    need(canonical(graph) == "38d2b3a2311a9ba5fee091cc7aa204c7ed95651aec95d75184b2391df090cbfb", "graph hash")
    need(canonical(layout) == "0ce3f9e383fc4bfdd22612b9e34fc9759d97204215937b82d23aec2cedd9b8ee", "layout hash")
    caller = tagged_sources.packed(tagged_sources.pinned(
        "data/CALLER.json.gz", tagged_sources.PINS["data/CALLER.json.gz"]))
    words, roots = templates(caller), placement(caller)
    binds, offsets, _ = layout_bindings(words, roots, layout, 48)
    root_registers = [offsets[kind, root] + i for kind, root in roots
                      for i in range(len(words[kind][1]))]
    need(len(root_registers) == len(set(root_registers)) == 9840, "root copies/aliases")
    hosted = layout["hosted"]
    pairs = dict(zip(hosted["Dports"], zip(hosted["X2"], hosted["Y2"], strict=True), strict=True))
    initial_roles = [i for p, x in enumerate(layout["live"])
                     for i in (x, x + 112) + pairs.get(p, ())]
    need(len(initial_roles) == len(set(initial_roles)) == 400, "repeated main copy")
    need(set(initial_roles) <= set(range(len(graph["initial"]))), "main role range")
    main = set(initial_roles)
    initial_roles += [i for i in range(len(graph["initial"])) if i not in main]
    need(sorted(initial_roles) == list(range(1291)), "public copy inventory")
    schedule = graph["schedule"]
    need(len(schedule) == len(set(schedule)) == 6965, "overwritten held node")
    forms = dict(graph["forms"])
    need(set(forms) == set(schedule), "form coverage")
    held = {~i for i in initial_roles}
    for node in schedule:
        need(node not in held, "held key overwritten")
        need(all(donor in held for donor, _ in forms[node]), "donor not retained")
        held.add(node)
    need(len(held) == 8256, "persistent graph envelope")
    outputs = {graph["first_output"] + i for i in initial_roles}
    need(len(outputs) == 1291 and outputs <= held, "output consumption coverage")
    need(len(held - outputs) == 6965, "remaining graph retirement inventory")
    moves = {n: (a, b) for n, a, b in graph["moves"]}
    need(len(moves) == 5674 and set(moves) <= set(schedule), "paid graph nodes")
    dimensions = list(map(len, graph["frames"]))
    helper_ranks = [dimensions[b] - dimensions[a]
                    for i, (a, b) in enumerate(zip(graph["initial"], graph["final"], strict=True))
                    if i not in main]
    need(len(helper_ranks) == 891 and min(helper_ranks) > 0, "helper copies")
    opcounts = Counter()
    paid_ranks = []
    native_calls = 0
    for row in instructions(words, roots, binds, offsets):
        opcounts[row[0]] += 1
        if row[0] == "NATIVE":
            native_calls += 1
            flat = [r for regs in row[3] for r in regs]
            need(len(flat) == len(set(flat)) == 400, "native root alias")
            for node in schedule:
                if node in moves:
                    a, b = moves[node]
                    paid_ranks.append(abs(dimensions[b] - dimensions[a]))
        elif row[0] == "QUERY" or row[0].startswith("IDLE_"):
            paid_ranks.append(1 if row[0] == "QUERY" else
                              8 * len(row[2]) + int(row[0] == "IDLE_ODD"))
    need(native_calls == 48 and len(paid_ranks) == 281568, "source paid inventory")
    need(paid_ranks.count(1) >= 1008, "split supply")
    targets = len(root_registers) + native_calls * len(helper_ranks)
    adapted = 2 * len(paid_ranks) + 1008
    zeros = 2 * targets
    graph_aux = len(held) + 1
    raw_aux = max(graph_aux, 2, len(root_registers) + 1)
    need((zeros, raw_aux, adapted) == (105216, 9841, 564144), "claimed constants")
    need(raw_aux > graph_aux, "output-list omission control")
    need(len(held - outputs) + len(held) > raw_aux, "graph-retirement omission control")
    return {"graph_sha256": canonical(graph), "layout_sha256": canonical(layout),
            "root_fields": len(root_registers), "main_fields": len(main),
            "helper_fields_per_graph": len(helper_ranks), "scheduled_nodes": len(schedule),
            "retained_graph_peak_envelope": len(held), "graph_with_replacement": graph_aux,
            "raw_auxiliary_envelope": raw_aux, "productive_zero_envelope": zeros,
            "per_context_envelope": zeros + raw_aux + 1, "adapted_paid_count": adapted,
            "original_rank_one_cuts": paid_ranks.count(1), "instruction_counts": dict(opcounts)}


def half_columns():
    from periodic import Job
    checked = 0
    for columns in (2, 4, 6, 32, 128):
        # Distinct, deliberately noncanonical axes expose an accidental reindexing.
        job = Job("one live field", tuple(3 + 7 * j for j in range(columns)))
        first = job.select(range(columns // 2))
        second = job.select(range(columns // 2, columns))
        need(first.owner == second.owner == job.owner, "half job created an owner")
        need(first.axes + second.axes == job.axes, "half concatenation lost an axis")
        need(not set(first.axes) & set(second.axes), "half columns overlap")
        checked += 1
    huge = 2**1024
    need(huge // 2 + huge // 2 == huge, "unbounded half interval identity")
    return {"actual_Job_select_cases": checked, "same_owner": True,
            "adapted_extra_cuts": 1008, "omitted_second_half_delay_error": "1008*D[e]"}


def frame(plan, band, birth, rep):
    return ((birth * len(plan.bands) + list(plan.bands).index(band))
            * max(plan.count.values()) + rep)


def grid(plan):
    """Construct events from complete context lifetimes, independently of tick scanning."""
    events = []
    q = len(plan.paid)
    for band in plan.bands:
        for birth in range(plan.ticks):
            for rep in range(plan.count[band]):
                ident = frame(plan, band, birth, rep)
                for j in range(q):
                    tick = birth + j * plan.delay[band]
                    if j == 0:
                        events.append(((tick, 1, -band, j, rep, 0), 0, ident, band, birth, j))
                    events.append(((tick, 1, -band, j, rep, 1), 1, ident, band, birth, j))
                tick = birth + q * plan.delay[band]
                events.append(((tick, 0, band, 0, rep, 0), 2, ident, band, birth, q))
    return sorted(events)


def empty_plan(q, births, counts):
    from transport import Plan
    plan = Plan.__new__(Plan)
    plan.bands = range(10, 16, 2)
    plan.ticks, plan.rounds = births, 10
    plan.count = dict(zip(plan.bands, counts, strict=True))
    plan.delay = dict(zip(plan.bands, (1, q + 1, (q + 1)**2), strict=True))
    plan.targets, plan.paid = (1, 1), (1,) * q
    plan.send, plan.receive, plan.sources = {}, {}, {}
    return plan


def calendar_intervals():
    cases = events_checked = outside_open = outside_close = 0
    peak_contexts = 0
    for q in (1, 2, 3, 5):
        for births in (1, 2, 7, 23):
            for counts in ((1, 2, 1), (2, 1, 3)):
                plan = empty_plan(q, births, counts)
                expected, actual = grid(plan), list(plan.events())
                need(len(expected) == len(actual), "event cardinality")
                live, resident, weights = set(), set(), {}
                cap = sum(plan.count[e] * (q * plan.delay[e] + 1) for e in plan.bands)
                serial = 0
                for entry, record in zip(expected, actual, strict=True):
                    key, op, ident, band, birth, j = entry
                    tick = key[0]
                    need(record[:2] == (op, ident), "calendar differs from sorted lifetimes")
                    local = sum(plan.count[e] * max(0, min(births - 1, tick)
                                - max(0, tick - q * plan.delay[e]) + 1) for e in plan.bands)
                    need(local <= cap, "inclusive cover")
                    if op == 0:
                        need(record == (0, ident, band - 8, 0, band - 8, 0, band - 8), "open bindings")
                        resident.add(ident)
                        weights[ident] = 105216
                        need(ident not in live, "opening allocation was already inserted")
                        outside_open += 1
                        live.add(ident)
                    elif op == 1:
                        need(record == (1, ident, serial, band - 8, 0), "paid ordinal")
                        serial += 1
                        weights[ident] = 105216 + 9841
                        need(sum(weights.values()) + 1 <= 115058 * cap, "paid replacement cover")
                    else:
                        live.remove(ident)
                        need(ident in resident and weights[ident] > 0, "close owner omitted")
                        outside_close += 1
                    need(len(resident) <= local <= cap, "residence left closed interval")
                    need(sum(weights.values()) <= 115058 * cap, "owner envelope")
                    peak_contexts = max(peak_contexts, len(resident))
                    if op == 2:
                        resident.remove(ident)
                        del weights[ident]
                need(not live and not resident and not weights, "epoch owner remainder")
                cases += 1
                events_checked += len(actual)
    # Three integer births in [t-QD,t] falsify deletion of +1 from THIS cover.
    need(sum(b <= 2 <= b + 2 for b in range(3)) == 3 > 2, "endpoint control")
    return {"calendar_cases": cases, "records_compared": events_checked,
            "opening_outside_dictionary_phases": outside_open,
            "closing_outside_dictionary_phases": outside_close,
            "peak_resident_contexts": peak_contexts,
            "endpoint_control": "Q=2,D=1,K=3,t=2: closed-interval count 3 > QD=2"}


def custody(parent_delay, births):
    from transport import Link, Plan
    plan = Plan.__new__(Plan)
    plan.bands = range(10, 32, 2)
    plan.ticks, plan.rounds = births, 1
    plan.count = {e: int(e in (14, 30)) for e in plan.bands}
    plan.delay = {e: (parent_delay if e == 30 else 1) for e in plan.bands}
    plan.targets, plan.paid = (1, 1), (Fraction(1, 2), Fraction(1, 2), 1)
    plan.send = {(30, j): [Link(0, 1, 14, j, 0)] for j in (0, 1)}
    plan.receive = {(14, j): [Link(0, 1, 30, j, 0)] for j in (0, 1)}
    plan.sources = {}
    records = list(plan.events())
    events = grid(plan)
    need(len(records) == len(events), "custody calendar length")
    live, owner, pending, returns = {}, {}, {}, {}
    cursor = transfers = 0
    for entry, record in zip(events, records, strict=True):
        key, op, ident, band, birth, j = entry
        need(record[:2] == (op, ident), "custody event order")
        if op == 0:
            ports = []
            bindings = iter(record[3:])
            for kind in bindings:
                if kind == 1:
                    token, parent = pending.pop(next(bindings))
                    need(owner[token][0] == "pending", "duplicate pending delivery")
                    returns[ident, token] = parent
                else:
                    need(kind == 0, "unexpected external source")
                    next(bindings)
                    token = cursor
                    cursor += 1
                owner[token] = ident
                ports.append(token)
            need(len(ports) == len(set(ports)), "two input tags alias one physical owner")
            live[ident] = ports
        elif op == 1:
            need(all(owner[token] == ident for token in live[ident]),
                 f"parent resumed while field borrowed at tick {key[0]}, paid {j}")
            serial, size, selected = record[2:]
            if selected:
                # Worst case: both successive half-column cuts use the SAME whole owner.
                token = live[ident][0]
                owner[token] = ("pending", serial)
                pending[serial] = token, ident
                transfers += 1
        else:
            need(all(owner[token] == ident for token in live[ident]), "close before return")
            for token in live.pop(ident):
                parent = returns.pop((ident, token), None)
                if parent is None:
                    del owner[token]
                else:
                    need(parent in live, "loan origin already closed")
                    owner[token] = parent
    need(not live and not pending and not owner and not returns, "custody remainder")
    return transfers


def external_sources():
    from transport import Plan, Source
    plan = Plan.__new__(Plan)
    plan.targets, plan.rounds = (1, 1), 10
    plan.sources = {(10, 0): [Source(0, 2, 0, 4)], (10, 1): [Source(0, 1, 12, 8)]}
    width, source_width, births = 31, 15, 3
    valid = zero = partial_cycle = last_group = 0
    for group in range(3):
        for round_no in range(plan.rounds):
            rows = []
            for port, count, period, start in ((0, 2, 4, 0), (1, 1, 8, 12)):
                cycles = plan.rounds // period
                for birth in range(births):
                    for replica in range(count):
                        kind, base, size, got_period = plan._external(10, port, replica, birth)
                        need((kind, size, got_period) == (2, 2, period), "external source descriptor")
                        need(base == start + (birth * count + replica) * cycles, "external block offset")
                        cycle = round_no // period
                        index = group * source_width + base + cycle
                        if cycle < cycles and index < width:
                            rows.append(index)
                            valid += 1
                        else:
                            zero += 1
                            partial_cycle += int(cycle >= cycles)
                            last_group += int(index >= width)
            need(len(rows) == len(set(rows)), "two live external occurrences share a row")
    need(partial_cycle > 0 and last_group > 0, "padding boundaries unexercised")
    return {"valid_external_visits": valid, "private_zero_occurrences": zero,
            "incomplete_cycle_occurrences": partial_cycle, "last_group_overflow_occurrences": last_group}


def free_first():
    seen = set()
    def visit(depth, high, free, live, peak):
        state = depth, high, free, live, peak
        if state in seen:
            return
        seen.add(state)
        need(high == len(free) + len(live) == peak, "historical capacity invariant")
        need(len(set(free + live)) == high, "free/live overlap or lost slot")
        if depth == 8:
            return
        if len(live) < 4:
            slot = free[-1] if free else high
            visit(depth + 1, high if free else high + 1, free[:-1] if free else (),
                  tuple(sorted(live + (slot,))), max(peak, len(live) + 1))
        for slot in live:
            visit(depth + 1, high, free + (slot,), tuple(s for s in live if s != slot), peak)
    visit(0, 0, (), (), 0)
    def one_trace(reuse):
        high, free, live, peak = 0, [], [], 0
        for op in ("allocate", "retire", "allocate"):
            if op == "retire":
                free.append(live.pop())
            else:
                if reuse and free:
                    slot = free.pop()
                else:
                    slot = high
                    high += 1
                live.append(slot)
                peak = max(peak, len(live))
        return high, peak
    need(one_trace(True) == (1, 1), "free-first control baseline")
    mutant_high, mutant_peak = one_trace(False)
    need(mutant_high > mutant_peak, "append-only mutation escaped")
    return {"allocator_states_checked": len(seen), "depth": 8, "maximum_live": 4,
            "append_only_control": {"high": mutant_high, "peak_live": mutant_peak}}


def main():
    boundary_paths = [AUTHOR / "OWNER-CENSUS.md", AUTHOR / "README.md", AUTHOR / "SOURCE-BINDINGS.json"]
    boundary_paths += sorted((AUTHOR / "sources").glob("*"))
    before = {str(path.relative_to(AUTHOR)): sha(path) for path in boundary_paths if path.is_file()}
    handles, modules = bind_sources()
    inventory = syntax_inventory()
    intervals = calendar_intervals()
    custody_cases = [custody(delay, births) for delay in (3, 4, 7) for births in (1, 2, 8, 13)]
    try:
        custody(1, 8)
    except AssertionError as exc:
        mutation = str(exc)
        need("parent resumed" in mutation, "unexpected custody mutation failure")
    else:
        raise AssertionError("flattened delay did not expose premature parent resume")
    for q, base in ((3, 3), (3, 4), (564144, 1048576)):
        for d in (1, 2, 17):
            need(q * d <= base * d, "child cannot close by next adapted cut")
            if base > q:
                need(q * d < base * d, "strict production return gap")
    need(6**77 > 2**20 * 5**77, "delay exponent")
    need(105216 + 9841 + 1 == 115058 < 2**17, "field coefficient")
    need(2**(9 * 1024) > 2**18, "native arena margin")
    after = {str(path.relative_to(AUTHOR)): sha(path) for path in boundary_paths if path.is_file()}
    need(before == after, "author boundary changed while reviewed")
    result = {"status": "PASS_INDEPENDENT_OWNER_CENSUS_REVIEW_CHECKS",
              "reviewed_proof_sha256": PROOF_PIN, "source_commit": "dfd25d553a843a946ca0b94130a5ff8943e98fdd",
              "modules": modules, "syntax": inventory, "intervals": intervals,
              "half_columns": half_columns(),
              "custody_cases": len(custody_cases), "custody_transfers": sum(custody_cases),
              "premature_resume_control": mutation, "external": external_sources(),
              "allocator": free_first(), "mass_enclosure": "retained explicit premise; not re-audited",
              "author_mock_executed": False, "checker_sha256": sha(Path(__file__))}
    (HERE / "READ-BOUNDARY.json").write_text(json.dumps(before, indent=2) + "\n")
    (HERE / "FINAL-BOUNDARY.json").write_text(json.dumps(after, indent=2) + "\n")
    (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    del handles


if __name__ == "__main__":
    main()
