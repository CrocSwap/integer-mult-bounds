"""Price #7131 scalar edits across two stationary blockers."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import argparse
import json
from pathlib import Path

from importlib.util import module_from_spec, spec_from_file_location


ROOT = Path(__file__).resolve().parents[3]
PRIOR = ROOT / "kappa-typea-birth2-20261110T2258Z/evidence/scalar/port.py"
LEGACY = ROOT / "kappa-two-blockers-20261110T1036Z/evidence/two_blockers.py"
PLANNER = Path(__file__).resolve().parents[1] / "planner/two_blockers.py"
FREE_TERM = PLANNER.with_name("free_term.py")
ALL_TERMS = PLANNER.with_name("all_terms.py")
OVERLAP = PLANNER.parents[1] / "overlap/overlap.py"


def module(name, path):
    spec = spec_from_file_location(name, path)
    value = module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def key_for(belong, visits):
    return tuple(sorted({tuple(sorted((belong(a), belong(b))))
                         for a, b in visits if belong(a) != belong(b)}))


def equality_groups(keys):
    groups = []
    for a, b in keys:
        group = {a, b}
        keep = []
        for existing in groups:
            if existing & group:
                group.update(existing)
            else:
                keep.append(existing)
        groups = [*keep, group]
    return groups


def pricing_rows(word, raw, scalar, bridges, legacy, mode, statistics):
    if mode == "joint-cut":
        planner = module("joint_cut_planner", PLANNER)
        for add, blockers, cut, ops, pairs in planner.choices(word, raw, scalar, bridges, statistics):
            yield dict(add=add, blockers=blockers, cut=cut, ops=ops, visits=pairs,
                       direction="later" if blockers[0] > add else "earlier")
        return
    if mode in ("free-term", "all-terms", "overlap"):
        path, entry_point = {
            "free-term": (FREE_TERM, "choices_free"),
            "all-terms": (ALL_TERMS, "choices_all"),
            "overlap": (OVERLAP, "choices_overlap"),
        }[mode]
        planner = module("separate_cut_planner", path)
        choices = getattr(planner, entry_point)
        for add, blockers, cut, ops, pairs, cuts in choices(word, raw, scalar, bridges, statistics):
            yield dict(add=add, blockers=blockers, cut=cut, ops=ops, visits=pairs,
                       term_cuts=cuts, direction="later" if blockers[0] > add else "earlier")
        return
    if mode == "stationary":
        yield from legacy.placements(word, raw, scalar, bridges)
    elif mode == "reciprocal":
        yield from legacy.placements(word, raw, scalar, bridges, allow_recip=True)
    elif mode == "slide-correction":
        yield from legacy.slide_placements(word, raw, scalar, bridges)
    elif mode in ("slide-move", "slide-move-edge"):
        yield from legacy.slide_move_placements(word, raw, scalar, bridges,
                                                edge_only=mode == "slide-move-edge")


def screen(word, graph, engine, legacy, bracket, journal, mode, start, cap):
    raw, _, comp, raw_paid, raw_target, fixed, scalar, original, entry, end, child = legacy.inventory(word, graph)
    initial_state = {i: legacy.chart(s) for i, s in enumerate(original) if s is not None}
    paid0 = Counter((comp[a], comp[b]) for _, a, b in raw_paid)
    old_low, old_high, _ = legacy.bounds(original, paid0, {comp[j] for j in fixed})
    left, right = map(Fraction, bracket)
    weights = {r: (engine.raw_margin({r: 1}, right)[0], engine.raw_margin({r: 1}, left)[1])
               for r in range(1, 10)}
    tally, blockers, planner_stats = Counter(), Counter(), Counter()
    previous, pending, hits = None, None, []
    join = legacy.propagate.__globals__["join"]

    for index, plan in enumerate(pricing_rows(word, raw, scalar, child, legacy, mode, planner_stats)):
        if index < start:
            continue
        if cap is not None and tally["placements"] == cap:
            pending = index
            break
        tally["placements"] += 1
        blockers["+".join(word["program"][j][0] for j in plan["blockers"])] += 1
        add = plan["add"]
        if previous != add:
            old, new = comp[scalar[add][0]], len(original)
            branch = child[add]
            split = {j for j, c in enumerate(comp)
                     if c == old and entry[branch] <= entry[j] < end[branch]}

            def belong(j):
                return new if j in split else comp[j]

            assert {belong(j) for j in scalar[add]} == {old, new}
            space = [*original, original[old]]
            paid = Counter((belong(a), belong(b)) for _, a, b in raw_paid)
            target = Counter((belong(a), belong(b)) for a, b in raw_target)
            low, high, adjacency = legacy.bounds(space, paid, {belong(j) for j in fixed})
            changed = {old, new} | {j for j in range(len(original))
                                    if (low[j], high[j]) != (old_low[j], old_high[j])}
            state = initial_state | {new: initial_state[old]}
            cache = {}
            previous = add
            tally["ADD bridges"] += 1
        key = key_for(belong, plan["visits"])
        groups = equality_groups(key)
        if mode == "all-terms":
            key = tuple(sorted((min(g), j) for g in groups for j in g if j != min(g)))
        if any({old, new} <= group for group in groups):
            status = "reinstates original scalar equality"
        elif key in cache:
            status = cache[key]
            tally["duplicate price constraints"] += 1
        else:
            joined = []
            for group in groups:
                a = frozenset({0})
                for j in sorted(group):
                    a = join(a, low[j])
                joined.append((a, set.intersection(*(set(high[j]) for j in group))))
            if any(not lo <= hi for lo, hi in joined):
                status, blocks = "incompatible span bounds", []
            else:
                status, blocks = legacy.price_box(
                    space, paid, target, state, low, high, adjacency, changed, key, weights
                )
            cache[key] = status
            if blocks:
                receipt = dict(index=index, status=status, proposal=plan, equalities=key,
                               old_component=old, new_component=new,
                               split_visits=[raw[j] for j in sorted(split)], blocks=blocks)
                hits.append(receipt)
                print(json.dumps(receipt, sort_keys=True), file=journal, flush=True)
        tally[status] += 1
        if tally["placements"] % 250 == 0:
            print(json.dumps(dict(index=index, add=add, counts=tally), sort_keys=True),
                  file=journal, flush=True)
    return dict(mode=mode, counts=tally, blockers=blockers, planner_stats=planner_stats,
                start=start, cap=cap, pending=pending, unresolved=len(hits), hits=hits)


def main(word_path, result_path, caller_path, journal_path, mode, start, cap):
    assert __debug__
    prior = module("pinned_source", PRIOR)
    legacy = module("retained_price", LEGACY)
    graph = module("literal_graph", prior.GRAPH)
    engine = module("directed_price", prior.PRICE)
    word = prior.read(word_path, prior.WORD, True)
    source = prior.read(result_path, prior.RESULT)
    caller = prior.read(caller_path, prior.CALLER)
    paid, target, _ = prior.count_invoice(word, caller, graph)
    assert paid == {int(k): v for k, v in source["price"]["after"]["P"].items()}
    assert target == {int(k): v for k, v in source["price"]["after"]["T"].items()}
    bracket = source["price"]["gate"]["raw_bracket"]
    signed = target.copy()
    signed.subtract(paid)
    assert engine.raw_margin(signed, Fraction(bracket[0]))[0] > 0
    assert engine.raw_margin(signed, Fraction(bracket[1]))[1] < 0
    with journal_path.open("x") as journal:
        result = screen(word, graph, engine, legacy, bracket, journal, mode, start, cap)
    dependencies = [PRIOR, LEGACY, prior.GRAPH, prior.PRICE]
    if mode in ("joint-cut", "free-term", "all-terms"):
        dependencies.append(PLANNER)
    if mode in ("free-term", "all-terms"):
        dependencies.append(FREE_TERM)
    if mode == "all-terms":
        dependencies.append(ALL_TERMS)
    if mode == "overlap":
        dependencies.extend((PLANNER, OVERLAP))
    pins = {}
    for path in dependencies:
        key = path.relative_to(ROOT).as_posix()
        if key in pins:
            raise ValueError(f"Duplicate dependency key {key}")
        pins[key] = sha256(path.read_bytes()).hexdigest()
    print(json.dumps(dict(word=prior.WORD, result=prior.RESULT, caller=prior.CALLER,
                          source_bracket=bracket, baseline_P=paid, baseline_T=target,
                          dependencies=pins, **result), indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for path in ("word_path", "result_path", "caller_path", "journal_path"):
        parser.add_argument(path, type=Path)
    parser.add_argument("--mode", choices=("joint-cut", "free-term", "all-terms", "overlap",
                                           "stationary", "reciprocal",
                                           "slide-correction", "slide-move", "slide-move-edge"),
                        default="joint-cut")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--cap", type=int)
    main(**vars(parser.parse_args()))
