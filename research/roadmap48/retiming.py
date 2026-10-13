"""Bounded full-cleanup-to-early-tail retiming with exact scalar commutation.

The pool consists of ordinary cleanup gates whose operands are untouched by
earlier ordinary cleanup gates. Each gate is tried at every tail insertion
position that commutes with the crossed tail suffix. Frame repair may only
raise tail frames and must stay inside every register's fixed final frame.
This is a specified search class, not global circuit or frame optimality.
Liamia: theoretical guidance and corrections. OpenAI Codex: implementation
and verification. Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q

import experiment as E


def coefficient(gate):
    if gate[0] == "add":
        return Q(gate[3], gate[4])
    E.require(gate[0] == "scale", "scalar primitive")
    return Q(gate[2], gate[3])


def commute(a, b):
    """Exact criterion for distinct-register ADDs and nonzero SCALEs."""
    for g in (a, b):
        E.require(g[0] in {"add", "scale"}, "scalar primitive")
        if g[0] == "add":
            E.require(g[1] != g[2], "self add")
        else:
            E.require(coefficient(g) != 0, "zero scale")
    if (a[0] == "add" and coefficient(a) == 0) or (a[0] == "scale" and coefficient(a) == 1):
        return True
    if (b[0] == "add" and coefficient(b) == 0) or (b[0] == "scale" and coefficient(b) == 1):
        return True
    if a[0] == b[0] == "scale":
        return True
    if a[0] == "scale":
        return a[1] not in E.AUDIT.registers(b)
    if b[0] == "scale":
        return b[1] not in E.AUDIT.registers(a)
    return a[1] != b[2] and b[1] != a[2]


def movable_pool(word):
    early = {i for i, _ in word["early_cleanup"]}
    touched, pool = set(), []
    for i, g in enumerate(word["cleanup"]):
        if i in early:
            continue
        registers = set(E.AUDIT.registers(g))
        if not (registers & touched):
            pool.append(i)
        touched.update(registers)
    return pool


def before_tail(word):
    cur, end = E.frame_state(word)
    for section in ("A", "B"):
        for g in word[section]:
            frame = E.basis(tuple(g[-1]))
            for r in E.AUDIT.registers(g):
                E.require(E.join(cur[r], frame) == frame, "baseline chain")
                cur[r] = frame
    return cur, end


def replay_tail(word, cur, end, entries, repair):
    cur, paid, fitted = cur.copy(), Counter(), []
    for position, (i, old_frame) in enumerate(entries):
        g = word["cleanup"][i]
        frame = E.basis(tuple(old_frame))
        if repair:
            for r in E.AUDIT.registers(g):
                frame = E.join(frame, cur[r])
        for r in E.AUDIT.registers(g):
            if E.join(frame, end[r]) != end[r]:
                return dict(status="FINAL_FRAME_CAP", position=position, cleanup_index=i, register=r)
            if E.join(cur[r], frame) != frame:
                return dict(status="NONMONOTONE", position=position, cleanup_index=i, register=r)
            rank = len(frame)-len(cur[r])
            if rank:
                paid[rank] += 1
            cur[r] = frame
        fitted.append([i, list(frame)])
    for r, final in enumerate(end):
        if E.join(cur[r], final) != final:
            return dict(status="END_CAP", register=r)
        rank = len(final)-len(cur[r])
        if rank:
            paid[rank] += 1
    return dict(status="PASS", profile=paid, fitted=fitted)


def scan(word):
    E.check_report(word)
    cur, end = before_tail(word)
    original = replay_tail(word, cur, end, word["early_cleanup"], False)
    E.require(original["status"] == "PASS", "honest tail")
    prefix = Counter(E.ints(word["report"]["local_profile"]))
    prefix.subtract(original["profile"])
    E.require(all(n >= 0 for n in prefix.values()), "nonnegative prefix profile")
    pool = movable_pool(word)
    rows, representatives, categories = [], {}, Counter()
    for cleanup_index in pool:
        g = word["cleanup"][cleanup_index]
        crossed = [word["cleanup"][i] for i, _ in word["early_cleanup"]]
        last_barrier = max((j for j, h in enumerate(crossed) if not commute(g, h)), default=-1)
        for position in range(last_barrier+1, len(crossed)+1):
            entries = word["early_cleanup"][:position]+[[cleanup_index, list(E.FULL)]]+word["early_cleanup"][position:]
            fitted = replay_tail(word, cur, end, entries, True)
            row = dict(cleanup_index=cleanup_index, tail_position=position, status=fitted["status"])
            categories[fitted["status"]] += 1
            if fitted["status"] == "PASS":
                profile = prefix+fitted["profile"]
                E.require(E.rank_mass(profile) == word["report"]["local_rank_mass"], "retiming changed telescoping mass")
                key = tuple(sorted(profile.items()))
                representatives.setdefault(key, dict(cleanup_index=cleanup_index, tail_position=position,
                                                     early_cleanup=fitted["fitted"]))
                row["profile"] = dict(key)
            else:
                row["register"] = fitted.get("register")
                row["blocking_cleanup_index"] = fitted.get("cleanup_index")
            rows.append(row)
    return dict(pool=pool, registers=sorted({r for i in pool for r in E.AUDIT.registers(word["cleanup"][i])}),
                rows=rows, categories=dict(sorted(categories.items())), representatives=representatives)


def candidate(word, representative):
    result = deepcopy(word)
    result["early_cleanup"] = representative["early_cleanup"]
    E.refresh_report(result)
    return result
