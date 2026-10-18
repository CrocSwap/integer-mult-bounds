"""PR2384's complete logical replay, adapted only to a certified owner evaluation.

Original commdata2338 / OpenAI Codex; adaptation Gareth Davidson / OpenAI Codex.
The unchanged maps and exact function algebra are imported from the pinned
predecessor. This is credited reuse, not an independent local-word verifier.
Apache-2.0.
"""
from copy import deepcopy

def replay(prior, model, template, h, reads, evaluation_vector, initial_sign=-1):
    combination, zero_bank = prior.combination, prior.zero_bank
    A, T, U = prior.A, prior.T, prior.U
    require, bind_schedule = prior.require, prior.bind_schedule
    def evaluate(function):
        return sum(c * ((evaluation_vector & v).bit_count() % 2) for v, c in function.items())
    H = model.query(h, 0)
    require(any(evaluate(f) for f in H), "old-chart defect is not witnessed at the certified owner")
    for stage in range(1, 9):
        require(not any(model.query(h, stage)), "later query does not vanish identically")
    selected = model.inject(H, 0, A)
    x, y = deepcopy(h), zero_bank()
    for p in A:
        x[p] = combination([(initial_sign, selected[p])])
        y[p] = combination([(-initial_sign, selected[p])])
    initial_A = [x[p] for p in A]
    require(any(evaluate(f) for f in initial_A), "nonzero original selected input")
    banks = [[x, y]] + [[zero_bank(), zero_bank()] for _ in range(3)]
    trace, histories = [], []
    bind_schedule(template["recipe"], template["calls"])
    for index, event in enumerate(template["recipe"]):
        kind = event["kind"]
        if kind == "local":
            pair, stage = event["pair"], event["stage"]
            x, y = banks[pair]
            if event["reverse"]:
                banks[pair] = list(model.backward(x, y, stage, stage + 1))
            else:
                xx, yy, f = model.forward(x, y, stage)
                require(not any(f), "forward history is nonzero")
                histories.append(stage)
                banks[pair] = [xx, yy]
        elif kind == "bridge":
            source, target, c = event["src"], event["dst"], event["coefficient"]
            for p in U:
                banks[target][0][p] = combination([(1, banks[target][0][p]),
                                                   (c, banks[source][0][p])])
                banks[source][1][p] = combination([(1, banks[source][1][p]),
                                                   (-c, banks[target][1][p])])
        else:
            require(kind == "terminal" and index == len(template["recipe"]) - 1,
                    "unique final terminal")
            banks = [[y, [combination([(-1, f)]) for f in x]] for x, y in banks]
        require(not any(fields[p] for pair in banks for fields in pair for p in A + T),
                "selected output survives")
        require(not any(fields[p] for pair in banks for fields in pair for p in reads),
                "ordinary read transcript is nonzero")
        if index >= 1:
            completed_side = 1 if kind == "terminal" else 0
            require(not any(pair[completed_side][p] for pair in banks for p in U),
                    "completed-X descendant is nonzero")
        multipliers = []
        for pair in banks:
            for fields in pair:
                candidates = [c for c in (-1, 0, 1)
                              if all(fields[p] == combination([(c, h[p])]) for p in U)]
                require(len(candidates) == 1, "ordinary trajectory not a unique h multiple")
                multipliers.append(candidates[0])
        trace.append({"event": event, "ordinary": multipliers})
    require(histories == [0, 2, 4, 6, 8], "all five forward histories")
    require(trace[-1]["ordinary"] == [1, 0, 0, 0, 0, 0, 0, 0], "former-Y endpoint")
    return initial_A, H, trace
