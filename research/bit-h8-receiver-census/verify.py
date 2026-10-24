"""Replay of the h = 8 receiver census: data tables, controls on PR589, the receiver variants, their collision with the
compact436 lineage and the stacking estimate under #4760's invoice.  usage: python3.12 -B verify.py [tables|words|all] [--json OUT]"""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import copy, gzip, hashlib, itertools, json, subprocess, sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h8lib as H  # noqa: E402
from h8lib import need  # noqa: E402

ORDER = [10, 15, 51, 53, 56, 66, 72, 89, 111]
R437 = H.ROOT / "research/bit-p111-r437-gl464-470-20261018"
EXPECTED = {}


def table(name):
    lines = gzip.decompress((HERE / "data" / name).read_bytes()).decode().splitlines()
    head = lines[0].split(",")
    return [dict(zip(head, l.split(","))) for l in lines[1:]]


def prof(s):
    return {int(a): int(b) for a, b in (x.split(":") for x in s.split(";"))}


def fkappa(local, helpers=None):
    """Float raw crossing of the invoice (same root as the census' float screen); exact brackets are separate."""
    T, P = H.invoice(local, helpers or {8: 439})
    a, b = 0.003, 0.004
    for _ in range(60):
        m = (a + b) / 2
        g = sum(n * r ** (1 - m) for r, n in T.items()) - sum(n * r ** (1 - m) for r, n in P.items())
        a, b = (m, b) if g > 0 else (a, m)
    return (a + b) / 2


def check_tables(out):
    A, B, C = table("STAGE-A.csv.gz"), table("STAGE-B.csv.gz"), table("STAGE-C.csv.gz")
    P589 = " ".join(map(str, ORDER))
    # Stage A covers exactly the admissible sets of research/e8-bit-p111's choose rule (enumerated in sets.py)
    import sets
    S = sets.admissible(552)
    need([" ".join(map(str, s)) for s in S] == [r["punctured"] for r in A], "stage A set list")
    need(len(A) == 17478 and all(r["status"] == "ok" for r in A), "stage A complete")
    Rs = Counter(int(r["R"]) for r in A)
    best = max(A, key=lambda r: float(r["kappa_float"]))
    need(best["punctured"] == P589 and int(best["R"]) == 442, "PR589's set is the stage A optimum")
    second = sorted(Rs)[1]
    need(second == 446 and min(int(r["R"]) for r in A if r["punctured"] != P589) == 446, "next R 446")
    # every stored float kappa is the root of its stored profile (float screen agrees to 1e-12)
    bad = 0
    for rows, rkey in ((A, "R"), (B, "R"), (C, "R")):
        for r in rows:
            if abs(fkappa(prof(r["local_profile"]), {8: int(r[rkey])}) - float(r["kappa_float"])) > 1e-12:
                bad += 1
            # mass identity 8R + 63 + 14v of the generator (v = 111)
            p = prof(r["local_profile"])
            need(sum(k * n for k, n in p.items()) == 8 * int(r[rkey]) + 63 + 14 * 111, "mass identity")
    need(bad == 0, "stored kappa equals the root of its stored profile")
    # Stage B: the 200 best stage-A sets, 31 draws each; only PR589's set reaches R <= 444
    need(len(B) == 6200 and len({r["punctured"] for r in B}) == 200, "stage B shape")
    other = [r for r in B if r["punctured"] != P589]
    need(min(int(r["R"]) for r in other) == 445 and max(float(r["kappa_float"]) for r in other) < 0.0034493,
         "stage B: other sets R >= 445, kappa < 0.0034493")
    # Stage C: all 3^9 receiver choices of PR589's set
    need(sorted(r["receivers_10_15_51_53_56_66_72_89_111"] for r in C) ==
         ["".join(map(str, t)) for t in itertools.product((1, 2, 3), repeat=9)], "stage C is all 3^9 choices")
    base = EXPECTED["pr589_raw"]
    beat = [r for r in C if float(r["kappa_float"]) > float(F(base[0]))]
    cb = max(C, key=lambda r: float(r["kappa_float"]))
    out["tables"] = {"stage_A_sets": len(A), "stage_A_R_histogram_low": {k: Rs[k] for k in sorted(Rs)[:6]},
                     "stage_B_rows": len(B), "stage_C_rows": len(C), "stage_C_untuned_above_PR589": len(beat),
                     "stage_C_best_untuned": [cb["receivers_10_15_51_53_56_66_72_89_111"], cb["R"], cb["kappa_float"]]}
    need(len(beat) == EXPECTED["stage_C_above"], "count above PR589")
    return A, C


def spot_replays(A, C, out):
    """Rebuild a few stored rows from scratch with the generator settings of their stage."""
    picks = []
    As = sorted(A, key=lambda r: float(r["kappa_float"]))
    for r in (As[0], As[len(As) // 2], As[-2]):
        picks.append(("A", [int(x) for x in r["punctured"].split()], None, 50, r))
    Cs = sorted(C, key=lambda r: float(r["kappa_float"]))
    for r in (Cs[0], Cs[len(Cs) // 2], Cs[-1]):
        sel = dict(zip(ORDER, map(int, r["receivers_10_15_51_53_56_66_72_89_111"])))
        picks.append(("C", ORDER, sel, 2000, r))
    done = []
    for stage, P, sel, nodeopt, r in picks:
        w = H.build(P, 552, sel, nodeopt)
        need(w is not None, "spot rebuild")
        p = H.profile(w)
        need(w["R"] == int(r["R"]) and p == prof(r["local_profile"]), "spot replay " + stage + " " + str(P))
        done.append(stage)
    out["spot_replays"] = done


def word_hash(w):
    return hashlib.sha256(json.dumps(w, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def gl464_470(w):
    """research/bit-p111-r437-gl464-470-20261018/code/generate.py (helper464 joint GL node + credited public #1043
    helper470 deletion), applied to an arbitrary R439 word; every structural guard and the full D0 restoration of the
    original are kept, only the input-hash pins are dropped."""
    v = w["v"]
    node = json.loads((R437 / "data/NEW-NODE.json").read_bytes())

    def run(gs, a):
        for f, d, ss in gs:
            for s in ss:
                a[d] ^= a[s]

    def d0(t, width):
        a = [1 << i for i in range(width)]
        run(t["A"], a)
        cap = [a[r] for r in t["ret"]]
        for target, idx in enumerate(t["scatter"]):
            for j in idx:
                a[v + target] ^= cap[j]
        run(t["B"], a)
        out = []
        for target in range(v):
            need(a[v + target] & ((1 << (2 * v)) - 1) == (1 << target) ^ (1 << (v + target)), "target restored")
            ss = [j for j in range(2 * v, width) if a[v + target] >> j & 1]
            if ss:
                out.append([0, v + target, ss])
        return out

    removed = 464
    need(w["R"] == 439 and w["A"][224] == [56, 464, [54]], "GL464 entrance gate")
    need(w["A"][1986:1989] == [[506, 349, [6, 56, 233, 319, 322, 340, 462, 463]], [506, 340, [233, 241, 319, 349, 464]],
                               [506, 241, [6, 56, 233, 319, 322, 463, 464]]], "GL464 replaced node")

    def role(r):
        need(r != removed, "removed role used")
        return r - int(r > removed)

    def gates(gs):
        return [[f, role(d), [role(s) for s in ss]] for f, d, ss in gs]

    t = copy.deepcopy(w)
    t["R"] = 438
    t["A"] = gates([z for j, z in enumerate(w["A"][:1986]) if j != 224]) + node + gates(w["A"][1989:])
    t["B"] = gates(w["B"])
    t["ret"] = [role(r) for r in w["ret"]]
    for key in ("start", "final"):
        t[key] = [f for r, f in enumerate(w[key]) if r != removed]
    t["C"] = [[1, d, ss[:]] for f, d, ss in reversed(t["A"] + t["B"]) if not v <= d < 2 * v]
    t["D"] = d0(t, 2 * v + t["R"])
    t["stats"]["extra_carriers"] -= 1
    old, removed, birth, late = t, 469, 229, 1999
    need(old["A"][birth] == [79, removed, [77]] and old["A"][late] == [79, 444, [removed]], "470 carrier gates")
    need([(s, j) for s in ("A", "B") for j, (f, d, ss) in enumerate(old[s]) if removed in [d] + ss] ==
         [("A", birth), ("A", late)], "470 carrier has no other use")
    a = [1 << i for i in range(2 * v + old["R"])]
    cur = old["start"][:]
    for f, d, ss in old["A"][:late]:
        for r in [d] + ss:
            cur[r] = f
        for s in ss:
            a[d] ^= a[s]
    need(a[77] == 1 << 77 and a[removed] == (1 << 77) ^ (1 << removed) and cur[77] == 186 and cur[444] == 0,
         "470 carrier value and frames at the late gate")
    t = copy.deepcopy(old)
    t["A"] = gates([[186, 444, [77]] if j == late else g for j, g in enumerate(old["A"]) if j != birth])
    t["B"] = gates(t["B"])
    for key in ("start", "final"):
        t[key] = [f for r, f in enumerate(old[key]) if r != removed]
    t["ret"] = [role(r) for r in old["ret"]]
    t["R"] = 437
    t["stats"]["extra_carriers"] -= 1
    t["C"] = [[1, d, ss[:]] for f, d, ss in reversed(t["A"] + t["B"]) if not v <= d < 2 * v]
    t["D"] = d0(t, 2 * v + t["R"])
    return t


def touched(a, b, sec):
    import difflib
    x = [json.dumps(g) for g in a[sec]]
    y = [json.dumps(g) for g in b[sec]]
    regs = set()
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, x, y, autojunk=False).get_opcodes():
        if op != "equal":
            for f, d, ss in a[sec][i1:i2] + b[sec][j1:j2]:
                regs.update([d] + ss)
    return regs


def variants(out):
    moves = json.loads((H.TUNED / "moves.json").read_text())["moves"]
    sel589 = H.canon_gz(R437 / "data/SELECTED589.json.gz")
    # control: PR555's frozen parameters rebuild the shipped base and PR589's two moves give the selected word
    P, s, sel, no = H.shipped()
    base = H.build(P, s, sel, no)
    need(base == H.canon_gz(H.P111 / "data/bitE8mut-p111.json.gz"), "shipped base word rebuilt")
    w589 = H.apply_moves(base, moves)
    need(w589 == sel589 and w589 == H.canon_gz(H.TUNED / "bitE8mut-p111-tuned.json.gz"), "PR589 word rebuilt")
    need(word_hash(gl464_470(w589)) == json.loads((R437 / "EXPECTED.json").read_text())["word_content_sha256"],
         "GL464 + 470 control reproduces the published R437 word")
    lo, hi = H.raw_root(H.profile(w589))
    need([str(lo), str(hi)] == EXPECTED["pr589_raw"], "PR589 raw root")
    res = {"PR589": {"profile": H.PR589_LOCAL, "raw_root": [str(lo), str(hi)]}}
    words, bases = {}, {}
    for name, change in (("rcv51_89", {51: 3, 89: 3}), ("rcv51", {51: 3}), ("rcv89", {89: 3})):
        P, s, sel, no = H.shipped(change)
        b = bases[name] = H.build(P, s, sel, no)
        tw, m = H.tune(b)
        p = H.profile(tw)
        lo, hi = H.raw_root(p)
        e = EXPECTED["variants"][name]
        need(tw["R"] == 439 and m == e["moves"] and p == {int(k): v for k, v in e["profile"].items()}
             and [str(lo), str(hi)] == e["raw_root"], "variant " + name)
        words[name] = tw
        res[name] = {"receivers_changed": change, "tuner_moves": m, "profile": p, "raw_root": [str(lo), str(hi)]}
    # the best variant passes PR555's independent checker (exact replay, interface lemma H1-H5)
    with __import__("tempfile").TemporaryDirectory() as d:
        wp = Path(d) / "w.json.gz"
        H.save(words["rcv51_89"], str(wp))
        r = subprocess.run([sys.executable, "-I", "-B", str(H.P111 / "code/xcheck_p.py"), str(wp)],
                           capture_output=True, text=True)
        need(r.returncode == 0 and "PASS interleaved interface lemma" in r.stdout, "xcheck_p on rcv51_89")
    res["rcv51_89"]["xcheck_p"] = "PASS"
    # collision with the compact436 lineage: the 89 receiver rewrites helpers 413/469 (public #4183's retirement)
    # in section A; the 51 receiver alone does not touch 413, 464, 469 or 470 and survives GL464 + 470
    t89 = touched(base, bases["rcv89"], "A")
    t51 = touched(base, bases["rcv51"], "A")
    need({413, 469} <= t89 and not ({413, 464, 469, 470} & t51), "A-section collision pattern")
    r437 = gl464_470(H.apply_moves(bases["rcv51"], moves))
    res["rcv51"]["gl464_470_port"] = {"R": r437["R"], "word_content_sha256": word_hash(r437)}
    try:  # PR589's two moves, then GL464 + 470, on the 89 variant
        gl464_470(H.apply_moves(bases["rcv89"], moves))
    except (ValueError, AssertionError) as e:
        res["rcv89"]["gl464_470_port"] = "REJECT: " + type(e).__name__ + " " + str(e)
    else:
        res["rcv89"]["gl464_470_port"] = "applies"
    out["variants"] = res
    return res


def stacking(res, out):
    """Additive profile transfer onto compact436 (#4760 invoice): an estimate, not a constructed word."""
    head = H.raw_root(H.COMPACT_LOCAL, H.COMPACT_HELPERS)
    need([str(head[0]), str(head[1])] == EXPECTED["compact436_raw"], "#4760 raw root control")
    est = {}
    for name in ("rcv51_89", "rcv51"):
        p = Counter(H.COMPACT_LOCAL)
        p.update(res[name]["profile"])
        p.subtract(H.PR589_LOCAL)
        lo, hi = H.raw_root(dict(p), H.COMPACT_HELPERS)
        gain = lo / head[1] - 1
        need(F(0) < gain < F(1, 1000), "estimate below #4760's 0.1% improvement gate")
        est[name] = {"profile": dict(sorted(p.items())), "raw_root": [str(lo), str(hi)], "relative_gain_lower": str(gain),
                     "relative_gain_display": float(gain)}
        need([str(lo), str(hi)] == EXPECTED["stacking"][name], "stacking " + name)
    out["stacking_estimate"] = {"compact436_raw_root": [str(head[0]), str(head[1])], "variants": est,
                                "status": "estimate only; rcv51_89 collides, rcv51 not carried through #4183/compact"}


def main():
    EXPECTED.update(json.loads((HERE / "RESULT.json").read_text())["expected"])
    out = {}
    part = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "all"
    if part in ("tables", "all"):
        A, C = check_tables(out)
        spot_replays(A, C, out)
    if part in ("words", "all"):
        res = variants(out)
        stacking(res, out)
    out["status"] = "PASS_H8_RECEIVER_CENSUS_" + part.upper()
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
