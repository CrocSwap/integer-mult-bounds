# SPDX-License-Identifier: Apache-2.0
"""Route one existing continuation through the donor return chart."""
from collections import Counter
from copy import deepcopy


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def delta(a, b):
    return {k: a.get(k, 0)-b.get(k, 0) for k in a.keys() | b.keys() if a.get(k, 0)!=b.get(k, 0)}


def profiles(w):
    ranks = list(map(len, w["frames"]))
    main = set(w["live"]) | {i+112 for i in w["live"]} | set(w["hosted"]["X2"] + w["hosted"]["Y2"])
    target = Counter(ranks[b]-ranks[a] for i,(a,b) in enumerate(zip(w["initial"], w["final"], strict=True)) if i not in main)
    paid = Counter(abs(ranks[e[3]]-ranks[e[2]]) for e in w["program"] if e[0]=="MOVE")
    return target, paid


FIRST, RETIMED, CORRECT, TAIL = 45667, 45668, 45677, 76416
LATE = [76433, 76434, 76441, 76442, 76443]


def construct(old, _witness=None):
    p = old["program"]
    need((old["public"], old["owned_fields"], len(p)) == (1501,67,76444), "Exact incumbent inventory")
    need([old["initial"][i] for i in (988,991,1499,1500)] == [3,3,1091,245] and
         [old["final"][i] for i in (988,991,1499,1500)] == [245,127,127,127], "Exact donor boundaries")
    need(p[FIRST:CORRECT] == [
        ["MOVE",1499,1091,127,False], ["ADD",1000,1499,"1",127],
        ["ADD",991,1565,"8",1091], ["MOVE",991,1091,245,False],
        ["ADD",996,991,"1",245], ["ADD",988,1565,"8",1091],
        ["MOVE",988,1091,245,False], ["ADD",996,988,"-1",245],
        ["ADD",779,991,"1",245], ["ADD",779,988,"-1/2",245],
    ], "Exact moves, retimed ADD and external consumer clocks")
    need(p[TAIL:TAIL+2] == [["MOVE",1500,245,127,False],["MOVE",991,245,127,False]],
         "Exact terminal exits")
    need([p[i] for i in LATE] == [
        ["ADD",1500,1499,"-8",127], ["ADD",991,1499,"-8",127],
        ["SCALE",1500,"2",127], ["ADD",991,1500,"1/2",127], ["ADD",1500,991,"-1",127],
    ], "Exact terminal basis and correction")
    need(p[58907:58920] == [
        ["ADD",1566,988,"1",245], ["ADD",1566,991,"-1",245], ["INIT",1567,245],
        ["ADD",1567,1500,"1",245], ["ADD",1567,1566,"-1",245],
        ["ADD",1500,988,"1",245], ["ADD",1500,1566,"-1",245], ["ADD",1500,1567,"-1",245],
        ["ADD",988,1566,"1",245], ["ADD",988,1500,"-1",245], ["CLEAR",1566,245],
        ["ADD",1500,1567,"1/2",245], ["ADD",991,1567,"-1/2",245],
    ], "Exact late antisymmetric cut")
    # No scalar consumer sees a shifted donor except the exact late cut above.
    for i,e in enumerate(p[CORRECT:TAIL],CORRECT):
        roles = e[1:3] if e[0] in ("ADD","COPY") else e[1:2]
        need(not set(roles)&{988,991,1500} or 58907<=i<58920, "No intervening donor or continuation contact")
    need(not any(e[1] == 1499 for e in p[FIRST+1:]), "Continuation retains its exact terminal value")
    early = [["MOVE",1499,1091,245,False],*p[RETIMED+1:CORRECT],
             ["ADD",988,1499,"-8",245],["ADD",991,1499,"-8",245],
             ["MOVE",1499,245,127,False],p[RETIMED]]
    tail = [[*p[i][:-1],245] for i in LATE[-3:]] + [p[TAIL]]
    out = deepcopy(old)
    out["final"][991] = 245
    omit = {TAIL+1,*LATE}
    out["program"] = [*p[:FIRST],*early,*p[CORRECT:TAIL],*tail,
                      *(e for i,e in enumerate(p[TAIL+2:],TAIL+2) if i not in omit)]
    before, after = profiles(old), profiles(out)
    need(delta(after[0],before[0]) == {8:1,9:-1} and delta(after[1],before[1]) == {4:1,5:-1},
         "Exact paid and target rank deltas")
    need(len(out["program"]) == len(p), "Instruction count preserved")
    return out
