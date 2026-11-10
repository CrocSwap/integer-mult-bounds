"""Deterministic full preparation workload within PR1523's width limit."""
import random


def specification(d=8, rounds=4):
    if not 1 <= d <= 8 or not 1 <= rounds <= 16:
        raise ValueError("workload limit exceeded")
    rng = random.Random(1523)
    rows = [(1 << j) | ((1 << (j + 1)) if j < d - 1 else 0) for j in range(d)]
    steps = []
    for _ in range(rounds):
        order = list(range(d))
        rng.shuffle(order)
        steps.extend(order + order)
    return {"width": d, "B": rows,
            "readers": [rng.randrange(1, 1 << d) for _ in steps], "steps": steps}


def prepare(model, solve, spec, mixed):
    demands = model.demands(spec)
    conditions = [(item["reader"], item["demand"]) for item in demands]
    weights = [1 + 2 * j for j in range(spec["width"])]
    prices = [3 + i % 5 for i in range(len(conditions))] if mixed else None
    plan = solve(spec["width"], conditions, weights, prices)
    word = model.emit(spec, "planned", plan)
    checked = model.check_word(spec, word)
    # Both complete orientations are part of preparation, not an unconsumed plan.
    rows = list(checked["final_rows"])
    for target, origin, _ in reversed(word["gates"]):
        rows[target] ^= rows[origin]
    if rows != [1 << j for j in range(word["registers"])]:
        raise ValueError("complete inverse failed")
    return {"spec": spec, "plan": plan, "word": word,
            "semantics": checked, "invoice": model.invoice(word)}
