"""Exact candidate parsing and native-word annotations; no solver is used.

Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
import json


def primal(U, model):
    data = U.primal_data()
    raw = data["assignment"]
    U.need(set(raw) == {json.dumps(n) for n in model.domain}, "complete primal node coverage")
    assignment = {}
    for node, domain in model.domain.items():
        f = tuple(raw[json.dumps(node)])
        U.need(f in domain, "primal frame outside complete domain")
        assignment[node] = f
    profile = model.profile(assignment)
    U.need(profile == {int(r): n for r, n in data["profile"].items()}, "primal profile")
    return assignment, profile


def native_word(word, model, assignment):
    result = deepcopy(word)
    for i in range(len(word["A"])):
        result["A"][i][-1] = list(model.frame_of(("G", i), assignment))
    for i in range(len(word["B"])):
        result["B"][i][-1] = list(model.frame_of(("G", model.nA+i), assignment))
    for i in range(len(word["early_cleanup"])):
        result["early_cleanup"][i][1] = list(model.frame_of(("G", model.nA+model.nB+i), assignment))
    for q in model.original_caps:
        result["helper_final"][str(q)] = list(model.frame_of(("E", q), assignment))
    profile = model.profile(assignment)
    widths = Counter(len(model.frame_of(("E", q), assignment))-len(model.fixed_frames[("S", q)])
                     for q in range(2*model.v, model.n))
    result["report"].update(local_profile={str(r): n for r, n in profile.items()},
                            local_rank_mass=sum(r*n for r, n in profile.items()),
                            width_inventory={str(r): n for r, n in sorted(widths.items())})
    return result
