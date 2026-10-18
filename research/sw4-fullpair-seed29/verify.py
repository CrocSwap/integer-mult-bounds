#!/usr/bin/env python3
"""Independent verification for the simultaneous-full-exchange search (seed 29).

Replays the complete arity-2/3 enumeration with an independently written
evaluator (no code shared with search.py), checks every committed evidence
entry, reconstructs the known SW4 word byte for byte through an independent
rewrite path, and runs mathematical failure controls.

Usage (from the repository root):
  python3 -B -I research/sw4-fullpair-seed29/verify.py
Expected final line:
  PASS_SW4_FULLPAIR_SEED29 pairs=703 triples=8436 legal=9139 no_beats_sw4
Standard library only. Reads inputs/ and the committed EVIDENCE/CANDIDATES.
"""
import gzip
import hashlib
import itertools
import json
import math
import random
import sys
import time
from collections import Counter
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RECIPE_PATH = REPO / "research/complex-sw4-frame8/construction/sw4/SW4-RECIPE-P6k4.json"
WORD_PATH = HERE / "inputs/P6K4-WORD.json.gz"
CAND_PATH = HERE / "CANDIDATES.json"
EVD_PATH = HERE / "EVIDENCE.json.gz"
EXP_PATH = HERE / "EXPECTED.json"

DIM = 112
H = 9
SEED = 29
FLOAT_EXP = 0.0016634287545402057


def red_basis(vecs):
    """Reduced F2 row-echelon form, returned top-bit-first. Written
    independently from search.py (explicit elimination table)."""
    return _red_basis(tuple(vecs))


@lru_cache(maxsize=None)
def _red_basis(vecs):
    pivots = {}
    for v in vecs:
        x = v
        while x:
            b = x.bit_length() - 1
            if b in pivots:
                x ^= pivots[b]
            else:
                pivots[b] = x
                break
    for b in sorted(pivots):
        row = pivots[b]
        for c in sorted(pivots):
            if c > b and (pivots[c] >> b) & 1:
                pivots[c] ^= row
    return tuple(pivots[b] for b in sorted(pivots, reverse=True))


@lru_cache(maxsize=None)
def span_join(left, right):
    return _red_basis(tuple(left) + tuple(right))


@lru_cache(maxsize=None)
def inside_cap(frame, port):
    for x in frame:
        if bin(x & port).count("1") % 2:
            return False
    return True


def port_hyperplane(port):
    return red_basis(
        tuple(v for v in range(1, 1 << H) if bin(v & port).count("1") % 2 == 0)
    )


WHOLE = red_basis(tuple(1 << i for i in range(H)))


def gate_regs(gate):
    if gate[0] == "add":
        return (gate[1], gate[2])
    return (gate[1],)


def float_cost(profile):
    return sum(n * (int(r) ** (1.0 - FLOAT_EXP)) for r, n in profile.items())


class Checker:
    def __init__(self, word):
        self.word = word
        total = 2 * DIM + word["report"]["R"]
        begin = [tuple([p]) for p in word["ports"]] + [() for _ in range(total - DIM)]
        for key, frm in word["start_extra"].items():
            begin[int(key)] = red_basis(tuple(frm))
        finish = (
            [WHOLE] * DIM
            + [port_hyperplane(p) for p in word["ports"]]
            + [WHOLE] * (total - 2 * DIM)
        )
        for key, frm in word["helper_final"].items():
            finish[int(key)] = red_basis(tuple(frm))
        state = [list(s) for s in begin]
        ledger = Counter()
        for gate in word["A"]:
            frm = red_basis(tuple(gate[-1]))
            for reg in gate_regs(gate):
                if span_join(tuple(state[reg]), frm) != frm:
                    raise ValueError(("A-scope", reg))
                grown = len(frm) - len(state[reg])
                if grown:
                    ledger[grown] += 1
                state[reg] = list(frm)
        levels = {
            int(t): red_basis(tuple(frm))
            for t, frm in word.get("target_levels", {}).items()
        }
        for num, frm in zip(word["centers"], word["center_frames"]):
            frm = red_basis(tuple(frm))
            served = {
                levels.get(gate[1] - DIM, ()) for gate in word["cut"] if gate[2] == num
            }
            for got in sorted(served, key=lambda x: -len(x)):
                if got != frm:
                    ledger[len(frm) - len(got)] += 1
                frm = got
        self.a_state = [tuple(s) for s in state]
        self.a_paid = ledger
        self.finish = finish
        self.blines = [
            (
                list(gate_regs(g)),
                red_basis(tuple(g[-1])),
            )
            for g in word["B"]
        ]
        self.ttails = [
            (list(gate_regs(word["cleanup"][idx])), red_basis(tuple(frm)))
            for idx, frm in word.get("early_cleanup", [])
        ]

    def apply(self, moves, materialize=False):
        remap = {}
        drop = set()
        extra = {}
        for mv in moves:
            at = mv["read_index"]
            if at in remap:
                return None, ["conflicting_read", at]
            remap[at] = (
                mv["target"],
                mv["r"] if mv["kind"] == "h2r" else mv["h"],
            )
            if mv["kind"] == "h2r":
                gone = mv["delete_preread_index"]
                if gone in drop:
                    return None, ["conflicting_delete", gone]
                drop.add(gone)
            else:
                extra.setdefault(mv["insert_preread_before"], []).append(
                    (mv["target"], mv["h"])
                )
        if drop & set(remap):
            return None, ["edit_delete_overlap"]
        state = [list(s) for s in self.a_state]
        ledger = Counter(self.a_paid)
        frames_out = []

        def step(regs, floor, tag):
            frm = floor
            for reg in regs:
                frm = span_join(frm, tuple(state[reg]))
            for reg in regs:
                if DIM <= reg < 2 * DIM and not inside_cap(
                    frm, self.word["ports"][reg - DIM]
                ):
                    return ["cap", tag if isinstance(tag, int) else tag[0], reg]
            for reg in regs:
                grown = len(frm) - len(state[reg])
                if grown:
                    ledger[grown] += 1
                state[reg] = list(frm)
            if materialize:
                frames_out.append(list(frm))
            return None

        for num, (regs, floor) in enumerate(self.blines):
            for pair in extra.get(num, []):
                bad = step(list(pair), (), ["insert", num])
                if bad:
                    return None, bad
            if num in drop:
                continue
            if num in remap:
                bad = step(list(remap[num]), (), num)
            else:
                bad = step(regs, floor, num)
            if bad:
                return None, bad
        tails_out = []
        for num, (regs, floor) in enumerate(self.ttails):
            frm = floor
            for reg in regs:
                frm = span_join(frm, tuple(state[reg]))
            for reg in regs:
                if (
                    span_join(tuple(state[reg]), frm) != frm
                    or span_join(frm, self.finish[reg]) != self.finish[reg]
                ):
                    return None, ["tail", num, reg]
            for reg in regs:
                grown = len(frm) - len(state[reg])
                if grown:
                    ledger[grown] += 1
                state[reg] = list(frm)
            tails_out.append(list(frm))
        for reg, frm in enumerate(self.finish):
            if span_join(tuple(state[reg]), frm) != frm:
                return None, ["end", reg]
            grown = len(frm) - len(state[reg])
            if grown:
                ledger[grown] += 1
        prof = {"%d" % k: v for k, v in sorted(ledger.items()) if k}
        if materialize:
            return (prof, frames_out, tails_out), None
        return prof, None


def discover_pairs(word):
    """Pair discovery traversing copy gates first (different order from
    search.py, same acceptance rule)."""
    gates = word["B"]
    copies = []
    for num, gate in enumerate(gates):
        if gate[0] == "add" and gate[3:5] == [1, 1] and not DIM <= gate[2] < 2 * DIM:
            copies.append((num, gate[1], gate[2]))
    found = []
    starters = {int(k) for k in word["start_extra"]}
    for num, h, r in copies:
        if h not in starters:
            continue
        if num != next(
            i for i, g in enumerate(gates) if g[1] == h
        ):
            continue
        earlier = [i for i, g in enumerate(gates[:num]) if h in gate_regs(g)]
        if any(
            not (
                gates[i][0] == "add"
                and DIM <= gates[i][1] < 2 * DIM
                and gates[i][2] == h
            )
            for i in earlier
        ):
            continue
        halt = next(
            (
                i
                for i in range(num + 1, len(gates))
                if gates[i][1] in (h, r)
            ),
            len(gates),
        )
        slot = earlier[-1] + 1 if earlier else num
        bundle = []
        for i in range(num + 1, halt):
            g = gates[i]
            if g[0] != "add" or not DIM <= g[1] < 2 * DIM or g[2] not in (h, r):
                continue
            tgt, num_a, den_b = g[1], g[3], g[4]
            if g[2] == h:
                pre = [
                    j
                    for j in earlier
                    if gates[j][:5] == ["add", tgt, h, -num_a, den_b]
                ]
                if len(pre) != 1:
                    continue
                bundle.append(
                    {
                        "h": h,
                        "r": r,
                        "read_index": i,
                        "target": tgt,
                        "coef": [num_a, den_b],
                        "kind": "h2r",
                        "delete_preread_index": pre[0],
                    }
                )
            else:
                bundle.append(
                    {
                        "h": h,
                        "r": r,
                        "read_index": i,
                        "target": tgt,
                        "coef": [num_a, den_b],
                        "kind": "r2h",
                        "insert_preread_before": slot,
                        "preread": ["add", tgt, h, -num_a, den_b],
                    }
                )
        if bundle:
            found.append({"h": h, "r": r, "moves": bundle})
    return sorted(found, key=lambda p: p["h"])


def order_moves(moves):
    return sorted(moves, key=lambda m: (m["read_index"], m["kind"], m["h"]))


def rebuild_word(word, moves, outcome):
    """Materialize the rewritten B section + tails for byte comparison."""
    prof, frames, tails = outcome
    book = {}
    skip = set()
    addon = {}
    for mv in moves:
        g = list(word["B"][mv["read_index"]][:-1])
        g[2] = mv["r"] if mv["kind"] == "h2r" else mv["h"]
        book[mv["read_index"]] = g
        if mv["kind"] == "h2r":
            skip.add(mv["delete_preread_index"])
        else:
            addon.setdefault(mv["insert_preread_before"], []).append(list(mv["preread"]))
    # frames_out parallels the emitted gate stream (inserts first, then the
    # gate; deletions emit nothing), so bodies built in the same walk zip exactly.
    stream = []
    for i, gate in enumerate(word["B"]):
        for extra_gate in addon.get(i, []):
            stream.append(extra_gate)
        if i not in skip:
            stream.append(list(book.get(i, gate[:-1])))
    assert len(stream) == len(frames), (len(stream), len(frames))
    out = dict(word)
    out["B"] = [body + [frm] for body, frm in zip(stream, frames)]
    out["early_cleanup"] = [
        [old[0], fr] for old, fr in zip(word.get("early_cleanup", []), tails)
    ]
    assert len(out["early_cleanup"]) == len(word.get("early_cleanup", []))
    out["report"] = dict(
        word["report"],
        local_profile=prof,
        local_rank_mass=sum(int(k) * v for k, v in prof.items()),
    )
    return out


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def explicit_span(generators):
    """Truly independent frame math: explicit vector sets (no pivots)."""
    seen = {0}
    for g in generators:
        seen |= {x ^ g for x in seen}
    return frozenset(seen)


def explicit_profile(word, moves):
    """Full refit over explicit subspaces; returns paid profile or failure."""
    total = 2 * DIM + word["report"]["R"]
    begin = [explicit_span([p]) for p in word["ports"]] + [
        frozenset([0]) for _ in range(total - DIM)
    ]
    for key, frm in word["start_extra"].items():
        begin[int(key)] = explicit_span(frm)
    finish = (
        [explicit_span([1 << i for i in range(H)])] * DIM
        + [frozenset(v for v in range(512) if bin(v & p).count("1") % 2 == 0) for p in word["ports"]]
        + [explicit_span([1 << i for i in range(H)])] * (total - 2 * DIM)
    )
    for key, frm in word["helper_final"].items():
        finish[int(key)] = explicit_span(frm)
    state = list(begin)
    ledger = Counter()
    for gate in word["A"]:
        frm = explicit_span(gate[-1])
        for reg in gate_regs(gate):
            if not state[reg] <= frm:
                return None, ("A-scope", reg)
            if len(frm) > len(state[reg]):
                grown = int(math.log2(len(frm))) - int(math.log2(len(state[reg])))
                ledger[grown] += 1
            state[reg] = frm
    levels = {
        int(t): explicit_span(frm) for t, frm in word.get("target_levels", {}).items()
    }
    for num, frm in zip(word["centers"], word["center_frames"]):
        frm = explicit_span(frm)
        served = {
            levels.get(gate[1] - DIM, frozenset([0]))
            for gate in word["cut"]
            if gate[2] == num
        }
        for got in sorted(served, key=lambda x: -len(x)):
            if got != frm:
                ledger[int(math.log2(len(frm))) - int(math.log2(len(got)))] += 1
            frm = got
    remap = {}
    drop = set()
    extra = {}
    for mv in moves:
        if mv["read_index"] in remap:
            return None, ("conflicting_read",)
        remap[mv["read_index"]] = (
            mv["target"],
            mv["r"] if mv["kind"] == "h2r" else mv["h"],
        )
        if mv["kind"] == "h2r":
            drop.add(mv["delete_preread_index"])
        else:
            extra.setdefault(mv["insert_preread_before"], []).append(
                (mv["target"], mv["h"])
            )
    if drop & set(remap):
        return None, ("edit_delete_overlap",)

    def step(regs, floor):
        frm = floor
        for reg in regs:
            frm = explicit_span(list(frm) + list(state[reg]))
        for reg in regs:
            if DIM <= reg < 2 * DIM and any(
                bin(x & word["ports"][reg - DIM]).count("1") % 2 for x in frm
            ):
                return None, ("cap", reg)
        for reg in regs:
            if len(frm) > len(state[reg]):
                ledger[
                    int(math.log2(len(frm))) - int(math.log2(len(state[reg])))
                ] += 1
            state[reg] = frm
        return True, None

    for num, gate in enumerate(word["B"]):
        for pair in extra.get(num, []):
            ok, bad = step(list(pair), frozenset([0]))
            if bad:
                return None, bad
        if num in drop:
            continue
        if num in remap:
            ok, bad = step(list(remap[num]), frozenset([0]))
        else:
            ok, bad = step(list(gate_regs(gate)), explicit_span(gate[-1]))
        if bad:
            return None, bad
    for idx, frm in word.get("early_cleanup", []):
        regs = gate_regs(word["cleanup"][idx])
        scope = explicit_span(list(frm) + [x for reg in regs for x in state[reg]])
        for reg in regs:
            if not state[reg] <= scope or not scope <= finish[reg]:
                return None, ("tail", reg)
        for reg in regs:
            if len(scope) > len(state[reg]):
                ledger[int(math.log2(len(scope))) - int(math.log2(len(state[reg])))] += 1
            state[reg] = scope
    for reg, frm in enumerate(finish):
        if not state[reg] <= frm:
            return None, ("end", reg)
        if len(frm) > len(state[reg]):
            ledger[int(math.log2(len(frm))) - int(math.log2(len(state[reg])))] += 1
    return {"%d" % k: v for k, v in sorted(ledger.items()) if k}, None


PRIME = 2147483629


def bend_end_state(word):
    """Sparse register rows mod PRIME after A + cut + B (identity start)."""
    total = 2 * DIM + word["report"]["R"]
    rows = [{i: 1} for i in range(total)]
    for gate in word["A"] + word["cut"] + word["B"]:
        if gate[0] == "scale":
            coef = gate[2] % PRIME * pow(gate[3] % PRIME, PRIME - 2, PRIME) % PRIME
            rows[gate[1]] = {
                k: (x * coef) % PRIME for k, x in rows[gate[1]].items()
            }
        else:
            q = gate[3] % PRIME * pow(gate[4] % PRIME, PRIME - 2, PRIME) % PRIME
            dst = rows[gate[1]]
            for k, x in rows[gate[2]].items():
                y = (dst.get(k, 0) + q * x) % PRIME
                if y:
                    dst[k] = y
                else:
                    dst.pop(k, None)
    return rows


def main():
    t0 = time.monotonic()
    raw = gzip.decompress(WORD_PATH.read_bytes())
    word = json.loads(raw)
    assert hashlib.sha256(raw).hexdigest() == (
        "0390ec65dc4d47df1887aabdc2ec5b6ddea3cfc8e65582873fdfeba81d100073"
    ), "input pin"
    recipe = json.loads(RECIPE_PATH.read_text())
    assert recipe["input_sha256"] == hashlib.sha256(raw).hexdigest()
    expected = json.loads(EXP_PATH.read_text())

    mine = Checker(word)
    base, bad = mine.apply([])
    assert not bad and base == recipe["profile_in"], ("baseline", base, bad)
    sw, bad = mine.apply(order_moves(recipe["moves"]))
    assert not bad and sw == recipe["profile_out"], ("SW4 profile", sw, bad)

    # Independent byte reconstruction of the SW4 word.
    outcome, bad = mine.apply(order_moves(recipe["moves"]), materialize=True)
    assert not bad
    rebuilt = rebuild_word(word, order_moves(recipe["moves"]), outcome)
    assert (
        hashlib.sha256(encode(rebuilt)).hexdigest() == recipe["output_sha256"]
    ), "SW4 byte reconstruction"
    print("RECONSTRUCT_OK", recipe["output_sha256"], flush=True)

    mine_pairs = discover_pairs(word)
    filed = json.loads(CAND_PATH.read_text())
    assert filed["input_sha256"] == recipe["input_sha256"]
    assert [p["h"] for p in mine_pairs] == [p["h"] for p in filed["pairs"]], "pair set"
    assert sum((1 << len(p["moves"])) - 1 for p in mine_pairs) == 602, "single domain"
    for a, b in zip(mine_pairs, filed["pairs"]):
        assert a["r"] == b["r"] and len(a["moves"]) == len(b["moves"])
        for x, y in zip(
            sorted(
                (m["kind"], m["read_index"], m["target"]) for m in a["moves"]
            ),
            sorted(
                (m["kind"], m["read_index"], m["target"]) for m in b["moves"]
            ),
        ):
            assert x == y, ("pair moves", a["h"], x, y)
    print("PAIRS_OK n=54 subsets=602", flush=True)

    fulls = {p["h"]: p["moves"] for p in mine_pairs if len(p["moves"]) == 4}
    assert len(fulls) == 38, "legal-full census"
    # Singles revalidation through the independent checker.
    legal = 0
    single_counts = Counter()
    for p in mine_pairs:
        for mask in range(1, 1 << len(p["moves"])):
            moves = [m for j, m in enumerate(p["moves"]) if mask >> j & 1]
            prof, bad = mine.apply(order_moves(moves))
            single_counts["single_total"] += 1
            if prof is None:
                single_counts["single_" + bad[0]] += 1
            else:
                single_counts["single_legal"] += 1
                if mask == (1 << len(p["moves"])) - 1:
                    legal += 1
    assert legal == 38
    for key in ("single_total", "single_cap", "single_legal"):
        assert single_counts[key] == expected["counts"][key], dict(single_counts)
    print("SINGLES_OK", dict(single_counts), flush=True)

    evd_raw = EVD_PATH.read_bytes()
    assert hashlib.sha256(evd_raw).hexdigest() == expected["evidence_sha256"]
    evd = json.loads(gzip.decompress(evd_raw))
    assert (
        hashlib.sha256(CAND_PATH.read_bytes()).hexdigest()
        == expected["candidates_sha256"]
    )
    assert evd["input_sha256"] == recipe["input_sha256"]
    assert evd["seed"] == SEED
    assert evd["counts"] == expected["counts"], evd["counts"]
    rng = random.Random(SEED)
    total = 0
    beats = 0
    cost_sw = float_cost(sw)
    best_seen = {}
    for arity in (2, 3):
        groups = sorted(
            itertools.combinations(sorted(fulls), arity),
            key=lambda g: list(g),
        )
        shuffled = list(groups)
        rng.shuffle(shuffled)
        assert [e["group"] for e in evd["groups_%d" % arity]] == [
            list(g) for g in shuffled
        ], ("evidence order seed", arity)
        for entry, grp in zip(evd["groups_%d" % arity], shuffled):
            assert entry["group"] == list(grp)
            moves = order_moves([m for h in grp for m in fulls[h]])
            prof, bad = mine.apply(moves)
            total += 1
            if entry["ok"]:
                assert prof is not None and prof == entry["profile"], grp
                if float_cost(prof) < cost_sw - 1e-9:
                    beats += 1
                if arity not in best_seen or float_cost(prof) < float_cost(
                    best_seen[arity]["profile"]
                ):
                    best_seen[arity] = {"group": list(grp), "profile": prof}
            else:
                assert prof is None and list(bad) == entry["fail"], (grp, bad)
    assert total == 703 + 8436 == 9139, total
    assert beats == 0, beats
    assert beats == expected["beats_sw4"] == 0
    assert total == expected["n_groups_2"] + expected["n_groups_3"]
    for arity in (2, 3):
        exp = expected["best_%d" % arity]
        got = best_seen[arity]
        assert got["group"] == exp["group"], (arity, got["group"])
        assert got["profile"] == exp["profile"], arity
    print("REPLAY_OK total=%d beats_sw4=%d" % (total, beats), flush=True)

    # Explicit-subspace spot checks on the load-bearing cases.
    key_groups = [
        [461, 581],
        [581, 603],
        [581, 591, 603],
        [461, 581, 591, 603],
        [602, 614],
        [449, 461],
    ]
    spot = {h: fulls[h] for h in sorted({h for g in key_groups for h in g})}
    for h, moves in spot.items():
        prof, bad = explicit_profile(word, order_moves(moves))
        ref, _ = mine.apply(order_moves(moves))
        assert prof is not None and prof == ref, ("explicit single", h)
    for grp in key_groups:
        moves = order_moves([m for h in grp for m in fulls[h]])
        prof, bad = explicit_profile(word, moves)
        ref, _ = mine.apply(moves)
        assert prof is not None and prof == ref, ("explicit combo", grp)
    print("EXPLICIT_OK cases=%d" % (len(spot) + len(key_groups)), flush=True)

    # Exactness controls over F prime: the honest rebuild preserves every
    # B-end register row; a single flipped coefficient moves them.
    rows_in = bend_end_state(word)
    assert bend_end_state(rebuilt) == rows_in, "B-end state preserved"
    evil = json.loads(json.dumps(word))
    evil["B"][856][3] = -evil["B"][856][3]
    assert bend_end_state(evil) != rows_in, "coef flip must move B-end rows"
    # Tamper control: a flipped evidence verdict no longer verifies.
    probe = evd["groups_2"][0]
    grp = probe["group"]
    moves = order_moves([m for h in grp for m in fulls[h]])
    reprof, _ = mine.apply(moves)
    flipped_ok = not probe["ok"]
    match = (
        (reprof is not None and reprof == probe["profile"])
        if flipped_ok
        else (reprof is None)
    )
    assert not match, "tampered verdict must not verify"
    # A lone partial move must fail frames (cf. recipe control N2).
    half = [m for m in fulls[461] if m["kind"] == "h2r"][:1]
    prof, bad = mine.apply(order_moves(half))
    assert prof is None and bad[0] == "cap", ("partial must fail frames", bad)
    print(
        "CONTROLS_OK exactness=preserved flip=trips tamper=trips partial=%s"
        % (bad,),
        flush=True,
    )

    assert expected["counts"] == {
        "single_total": 602,
        "single_cap": 564,
        "single_legal": 38,
        "g2_legal": 703,
        "g3_legal": 8436,
    }, expected["counts"]
    assert expected["n_legal_full"] == 38
    assert expected["input_sha256"] == recipe["input_sha256"]
    assert expected["comparison_sha256"] == recipe["output_sha256"]
    assert expected["seed"] == SEED
    secs = round(time.monotonic() - t0, 1)
    print(
        "PASS_SW4_FULLPAIR_SEED29 pairs=703 triples=8436 legal=9139 "
        "no_beats_sw4 seconds=%.1f" % secs,
        flush=True,
    )


if __name__ == "__main__":
    sys.exit(main())
