#!/usr/bin/env python3
"""KB5j job 1: classify the escape mechanism of PR 2963's escaping witnesses.

PR 2963 (box_search.bpp_strictness, part (b)) found 21 escaping witnesses
(out-of-box valid L8 witnesses) on v = 3..5 fixture sub-decoders with no strict
projection drop. This script regenerates exactly that witness pool and
classifies each escape:

  E1 cosmetic       escaping bits affect neither K_tt nor any forward-zero-arc
                    parity of the kept set (sub-anchor projection preserves the
                    witness verbatim in value AND constraints);
  E2 certification  some kept line is certified through non-tied shared bits
                    (Lemma BPP condition (i) fails on the raw witness);
  E3 arc parity     some forward zero arc carries odd off-anchor shared parity
                    (condition (ii) fails on the raw witness);
  E4 both.

For every escaping witness it also recomputes: the ab_value of the witness, the
ab_value of its sub-anchor projection, whether an in-box witness of the SAME
value exists (exact box run at v <= 5), and per escape line the exact bits used
outside a0/b0. Stdlib only, deterministic. Writes data/escape-receipt.json.

Run: python3 -B escape_classify.py
"""
import importlib.util
import json
import os
import random
import sys
import time

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "predecessor", "pr2963"))
import named_exact as ne  # noqa: E402

fg = ne.fg
DATA = os.path.join(HERE, "predecessor", "pr2963", "predecessor", "pr2914",
                    "data")
spec = importlib.util.spec_from_file_location(
    "box_attack",
    os.path.join(HERE, "predecessor", "pr2963", "predecessor", "pr2936",
                 "box_attack.py"))
ba = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ba)


def log(msg):
    print("[%7.1fs] %s" % (time.time() - T0, msg), flush=True)


def bpp_projection(ad, wit):
    a = [x & ad["a0"][t] for t, x in enumerate(wit["a"])]
    b = [x & ad["b0"][t] for t, x in enumerate(wit["b"])]
    return dict(a=a, b=b, order=list(wit["order"]), kept=list(wit["kept"]))


def bpp_conditions(mod, ad, wit):
    ok1 = True
    for t in wit["kept"]:
        tied = wit["a"][t] & wit["b"][t] & ad["a0"][t] & ad["b0"][t]
        if bin(tied).count("1") % 2 != 1:
            ok1 = False
    ok2 = True
    kept = set(wit["kept"])
    pos = {t: i for i, t in enumerate(wit["order"])}
    for t in kept:
        for s in kept:
            if t != s and mod["M"][t][s] == 0 and pos.get(t, 10 ** 9) < pos.get(s, -1):
                off = (wit["a"][t] & wit["b"][s]) \
                    & ~(ad["a0"][t] & ad["b0"][s])
                if bin(off).count("1") % 2 != 0:
                    ok2 = False
    return ok1, ok2


def escape_bits(ad, wit, t):
    """The exact out-of-box bits used on line t (a-side and b-side)."""
    return dict(a_out=wit["a"][t] & ~ad["a0"][t],
                b_out=wit["b"][t] & ~ad["b0"][t],
                a0=ad["a0"][t], b0=ad["b0"][t],
                tied=ad["a0"][t] & ad["b0"][t], tau=ad["tau"][t])


def classify_one(mod, ad, wit):
    kept = wit["kept"]
    val = fg.ab_value(mod, wit["a"], wit["b"])
    proj = bpp_projection(ad, wit)
    pval = fg.ab_value(mod, proj["a"], proj["b"])
    ok1, ok2 = bpp_conditions(mod, ad, wit)
    inb, esc = fg.in_box(mod, ad, wit)
    verbatim = all(wit["a"][t] == proj["a"][t] and wit["b"][t] == proj["b"][t]
                   for t in kept)
    if ok1 and ok2:
        kind = "E1"
    elif not ok1 and not ok2:
        kind = "E4"
    elif not ok1:
        kind = "E2"
    else:
        kind = "E3"
    return dict(value=val, projected_value=pval, cond_i=ok1, cond_ii=ok2,
                projection_verbatim=verbatim, escape_kind=kind,
                escape_lines=[dict(line=t, **escape_bits(ad, wit, t))
                              for t in esc])


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    pool = []
    for fixture in ("tied_min.json", "cex_min_1.json"):
        mod0 = fg.model(*fg.load_decoder(os.path.join(DATA, fixture)))
        for size in (3, 4, 5):
            subs, _n, _t = fg.subsets_smallest_first(mod0["v"], size, 40, 1)
            for S in subs:
                pool.append((fixture, list(S), size))
    pool.sort(key=lambda c: (c[2], sum(c[1])))
    records = []
    esc_total = 0
    for fixture, S, size in pool:
        mod0 = fg.model(*fg.load_decoder(os.path.join(DATA, fixture)))
        sub = fg.restrict(mod0, S)
        ad = fg.anchor_data(sub)
        v = sub["v"]
        wits = []
        for seed in (1234, 2025, 77, 4242):
            _val, wit = fg.cert_hillclimb(sub, iters=200, seed=seed)
            if wit is not None and fg.replay_witness(sub, wit):
                wits.append(dict(wit, source="hillclimb:%d" % seed))
        rr = random.Random(4242 + 100 * size + sum(S))
        for _ in range(600):
            a = [rr.randrange(8) & sub["pi"][t] for t in range(v)]
            b = [rr.randrange(8) & sub["sg"][t] for t in range(v)]
            wit = dict(a=a, b=b, order=list(range(v)), kept=list(range(v)))
            if fg.replay_witness(sub, wit):
                wits.append(dict(wit, source="random"))
        seen = set()
        exacts = {}

        def exacts_cached():
            if not exacts:
                ce, _ = fg.cert_exact(sub, max_v=v)
                bx, _ = ba.box_exact_tolerant(sub, ad)
                exacts["ce"] = ce
                exacts["bx"] = bx
            return exacts["ce"], exacts["bx"]

        for wit in wits:
            if fg.in_box(sub, ad, wit)[0]:
                continue
            key = (tuple(wit["a"]), tuple(wit["b"]))
            if key in seen:
                continue
            seen.add(key)
            esc_total += 1
            rec = classify_one(sub, ad, wit)
            ce, bx = exacts_cached()
            rec.update(fixture=fixture, S=S, v=v, tau=list(ad["tau"]),
                       source=wit["source"], cert=ce, box=bx,
                       kept=list(wit["kept"]), a=list(wit["a"]),
                       b=list(wit["b"]), order=list(wit["order"]))
            records.append(rec)
    counts = {}
    for r in records:
        counts[r["escape_kind"]] = counts.get(r["escape_kind"], 0) + 1
    drops = [r for r in records if r["projected_value"] < r["value"]]
    boxgaps = [r for r in records if r["box"] < r["cert"]]
    log("escapes=%d distinct=%d kinds=%s drops=%d box-gaps=%d"
        % (esc_total, len(records), counts, len(drops), len(boxgaps)))
    with open(os.path.join(HERE, "data", "escape-receipt.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump(dict(generator="escape_classify.py (PR 2963 box_search "
                                 "pool, deduplicated by label pair)",
                       pool_sizes=len(pool), escapes_seen=esc_total,
                       records=records), fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("PASS_ESCAPE_CLASSIFY escapes=%d distinct=%d kinds=%s "
          "projection-drops=%d box-gaps=%d"
          % (esc_total, len(records), counts, len(drops), len(boxgaps)))


if __name__ == "__main__":
    main()
