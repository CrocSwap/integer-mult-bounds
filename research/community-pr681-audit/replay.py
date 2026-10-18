"""Independent replay of PR #681's raw complex-factory resynthesis.

Rohan Guliani (@Rohansguliani), with substantial AI assistance. Apache-2.0.
Audits PR #681 by Alluri (@alluri-ritual) at
e536f6fc8aad65adef8ac4682d13625598a5c3f9. No PR #681 code is imported; the
two scalar templates below are transcribed from its CIRCUIT.json
(sha256 f64a9e88491af13fe564f0512e8455eb268d1732a978b1b4fe3b93e601b59f71).

Python 3.11+, standard library, offline. Temporary files only. Run:

    python3 -B research/community-pr681-audit/replay.py
"""
from collections import Counter
from fractions import Fraction as Q
import gzip
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / "research/complex-k492-owner-repair/code"
SELECTED = ROOT / "certificates/selected-result.json"
W = ("W",)

# Frame-free 8-register scalar templates: [add, target, source, num, den] or
# [scale, target, num, den]. ORIGINAL must be found in the fresh constructor.
ORIGINAL = json.loads('[["add",1,0,1,1],["add",0,1,-1,1],["add",1,0,1,1],["scale",0,-1,1],["add",3,0,-1,1],["add",7,0,1,2],["add",2,1,1,1],["add",1,2,-1,1],["add",2,1,1,1],["scale",1,-1,1],["add",5,1,1,2],["add",6,1,1,2],["add",4,3,1,1],["add",3,4,-1,1],["add",4,3,1,1],["scale",3,-1,1],["scale",3,-2,1],["add",6,4,1,1],["add",4,6,-1,1],["add",6,4,1,1],["scale",4,-1,1],["scale",4,2,1],["add",6,5,1,1],["add",5,6,-1,1],["add",6,5,1,1],["scale",5,-1,1],["scale",5,-1,1],["add",0,5,-1,1],["add",3,5,1,1],["add",7,5,-1,1],["add",7,6,1,1],["add",6,7,-1,1],["add",7,6,1,1],["scale",6,-1,1],["add",0,6,-1,1],["add",3,6,1,1],["add",5,6,1,1],["add",1,7,-1,1],["add",2,7,-1,1],["add",4,7,-1,1],["add",6,7,1,1],["add",5,7,1,1],["add",4,7,-1,1],["add",7,6,-1,1],["add",4,6,1,1],["add",3,6,1,1],["add",1,6,-1,1],["add",7,5,-1,1],["add",4,5,1,1],["add",3,5,1,1],["add",2,5,-1,1],["add",6,5,1,1],["add",5,6,-1,1],["add",6,5,1,1],["scale",5,-1,1],["add",7,4,1,1],["add",6,4,-1,1],["add",5,4,-1,1],["add",3,4,-1,1],["add",2,4,1,1],["add",1,4,1,1],["scale",4,-2,1],["add",6,3,-1,1],["add",5,3,-1,1],["add",2,3,1,1],["add",1,3,1,1],["add",0,3,-1,1],["add",4,3,1,1],["add",3,4,-1,1],["add",4,3,1,1],["scale",3,-1,1],["add",6,2,1,1],["add",4,2,-1,1],["add",0,2,1,1],["scale",2,-2,1],["add",5,1,1,1],["add",4,1,-1,1],["add",0,1,1,1],["scale",1,-2,1],["add",3,1,1,1],["add",1,3,-1,1],["add",3,1,1,1],["scale",1,-1,1],["add",4,0,1,1],["add",3,0,1,1],["add",2,0,1,1],["add",1,0,1,1]]')
REPLACEMENT = json.loads('[["add",3,0,1,1],["add",3,5,-2,1],["add",5,0,-1,2],["add",2,0,-1,1],["add",5,7,1,1],["add",4,7,-1,1],["scale",7,-2,1],["add",2,7,-1,1],["add",1,7,1,1],["scale",6,2,1],["add",6,7,-1,1],["add",7,6,1,1],["add",6,7,-1,1],["add",6,2,-1,1],["add",5,2,-1,2],["add",0,2,1,1],["scale",0,2,1],["add",6,5,-2,1],["scale",5,1,-1],["add",2,4,2,1],["add",1,4,-2,1],["add",4,1,1,2],["scale",1,2,1],["add",2,7,1,1],["scale",2,2,1],["add",0,1,1,1],["add",1,6,2,1],["add",6,5,-1,1],["add",3,7,1,1],["add",7,5,1,1],["add",3,0,-1,2],["add",0,3,1,1],["add",1,0,-1,1],["add",2,1,1,1]]')

# Numbers claimed by PR #681 (complex-factory5-resynthesis/README.md) and by the
# PR #681 consolidation for the raw word under PR #696's lowering.
CLAIM = {
    "scalar_saved_with_cleanup": 1484,
    "old_lowering": {"forward": (170488, 160296), "backward": (170536, 160344)},
    "pr696_lowering": {"forward": (128696, 123768), "backward": (128712, 123784)},
}


def load(path):
    data = Path(path).read_bytes()
    return json.loads(gzip.decompress(data) if str(path).endswith(".gz") else data)


def regs(e):
    return [e[1], e[2]] if e[0] == "add" else [e[1]]


def match(window, template):
    """Injective register relabeling template->window, or None."""
    m = {}
    for g, t in zip(window, template):
        if g[0] != t[0] or g[3 if g[0] == "add" else 2:-1] != t[3 if t[0] == "add" else 2:]:
            return None
        for a, b in zip(regs(t), regs(g)):
            if m.setdefault(a, b) != b:
                return None
    return m if len(set(m.values())) == len(m) == 8 else None


def inverse(events):
    out = []
    for e in reversed(events):
        e = list(e)
        if e[0] == "add":
            e[3] = -e[3]
        else:
            e[2], e[3] = e[3], e[2]
        out.append(e)
    return out


def coeff(e):
    return Q(e[3], e[4]) if e[0] == "add" else Q(e[2], e[3])


def symbolic(events, state=None):
    """Exact sparse linear forms of every register after the event list."""
    state = {} if state is None else state
    get = lambda r: state.setdefault(r, {r: Q(1)})
    for e in events:
        t = get(e[1])
        q = coeff(e)
        if e[0] == "add":
            for k, v in get(e[2]).items():
                x = t.get(k, 0) + q * v
                if x:
                    t[k] = x
                else:
                    t.pop(k, None)
        else:
            for k in t:
                t[k] *= q
    return state


def old_word(op):
    """Cleared-work binary Horner (the emitter's real_component_primitive_bound)."""
    tag, t = op[0], tuple(op[1])
    if tag == "clear":
        return [("clear", t)]
    if tag == "copy":
        return [("copy", t, tuple(op[2]))]
    if tag == "scale":
        q = Q(op[2], op[3])
        k = abs(q.numerator).bit_length() - q.denominator.bit_length()
        return [("mul", t, Q(2) if k > 0 else Q(1, 2))] * abs(k) + ([("mul", t, Q(-1))] if q < 0 else [])
    s, q = tuple(op[2]), Q(op[3], op[4])
    word = [("clear", W)]
    for i, bit in enumerate(bin(abs(q.numerator))[2:]):
        if i:
            word.append(("mul", W, Q(2)))
        if bit == "1":
            word.append(("acc", W, s, 1))
    word += [("mul", W, Q(1, 2))] * (q.denominator.bit_length() - 1)
    return word + [("acc", t, W, 1 if q > 0 else -1), ("clear", W)]


def pr696_word(op):
    """PR #696 lowering, as re-implemented in the PR #696 audit: copy-init; unit = acc + clear."""
    if op[0] != "add":
        return old_word(op)
    t, s, q = tuple(op[1]), tuple(op[2]), Q(op[3], op[4])
    if abs(q) == 1:
        return [("acc", t, s, 1 if q > 0 else -1), ("clear", W)]
    return [("copy", W, s)] + old_word(op)[2:]


def run(regs_, word):
    for p in word:
        if p[0] == "clear":
            regs_[p[1]] = 0
        elif p[0] == "copy":
            regs_[p[1]] = regs_[p[2]]
        elif p[0] == "mul":
            regs_[p[1]] = regs_[p[1]] * p[2]
        else:
            regs_[p[1]] = regs_.get(p[1], 0) + p[3] * regs_[p[2]]


def native(raw, out, logs):
    """Unchanged inherited raw-word audit, emitter and local auditor from main."""
    route = ROOT / "research/direct-delivery504-global/inputs/phase-baseline/CANONICAL-WORD.json.gz"
    for script, args in (("hpe_audit_and_transport.py", ["--raw", raw, "--routing", route, "--out", out]),
                         ("hpe_emit_local.py", [out]), ("hpe_audit_local.py", [out])):
        p = subprocess.run([sys.executable, "-I", "-B", str(CODE / script), *map(str, args)],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        (logs / f"{out.name}-{script}.log").write_text(p.stdout)
        assert p.returncode == 0, (script, p.stdout[-1500:])
    return (load(out / "SCALAR-FRAME-AUDIT.json"), load(out / "LOCAL-PROGRAMS.json.gz"),
            load(out / "LOCAL-CHECKS.json"), load(out / "INDEPENDENT-LOCAL-REPLAY.json"))


def main():
    with tempfile.TemporaryDirectory(prefix="pr681-audit-") as tmp:
        replay(Path(tmp))


def replay(tmp):
    # 1. Fresh, unpatched constructor run from main.
    p = subprocess.run([sys.executable, "-I", "-B", str(CODE / "construct_k_triangle.py"),
                        str(ROOT / "research/direct-delivery504-global/inputs/hamming"), str(tmp / "old"),
                        str(ROOT / "research/complex-k492-owner-repair/data/TRI-SCHEDULE.json")],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    assert p.returncode == 0, p.stdout[-1500:]
    old = load(tmp / "old/FULL-WORD.json.gz")
    A = old["A"]

    # 2. Find every occurrence of the 87-gate template (constant frame, 8 distinct registers).
    hits, used, i = [], set(), 0
    while i + len(ORIGINAL) <= len(A):
        win = A[i:i + len(ORIGINAL)]
        m = match(win, ORIGINAL)
        if m is not None and len({json.dumps(g[-1]) for g in win}) == 1:
            assert not used & set(m.values()), "factory windows share registers"
            used |= set(m.values())
            hits.append((i, m, win[0][-1]))
            i += len(ORIGINAL)
        else:
            i += 1
    assert len(hits) == 14, len(hits)

    # 3. Local exact identity of the templates, all four orientations.
    for name, f in (("main", lambda x: x), ("cleanup", inverse)):
        a, b = symbolic(f(ORIGINAL)), symbolic(f(REPLACEMENT))
        assert all(a.get(r, {r: 1}) == b.get(r, {r: 1}) for r in range(8)), name
    assert set(r for e in REPLACEMENT for r in regs(e)) == set(range(8)), "replacement skips a register"
    assert all(abs(coeff(e).denominator) & (abs(coeff(e).denominator) - 1) == 0 for e in REPLACEMENT)

    # 4. Splice, descending so earlier indices stay valid; rebuild cleanup by the
    #    inherited rule after confirming that rule reproduces the old cleanup.
    def cleanup(word):
        full = [256, 128, 64, 32, 16, 8, 4, 2, 1]
        return [e[:-1] + [full] for e in inverse([e for e in word["A"] + word["B"] if not 112 <= e[1] < 224])]
    assert old["cleanup"] == cleanup(old), "old cleanup is not the literal inverse rule"
    new = json.loads(json.dumps(old))
    for start, m, frame in reversed(hits):
        new["A"][start:start + len(ORIGINAL)] = [
            [e[0], m[e[1]], m[e[2]], e[3], e[4], frame] if e[0] == "add" else [e[0], m[e[1]], e[2], e[3], frame]
            for e in REPLACEMENT]
    new["cleanup"] = cleanup(new)
    gz = tmp / "new/FULL-WORD.json.gz"
    gz.parent.mkdir()
    gz.write_bytes(gzip.compress(json.dumps(new).encode(), mtime=0))

    # 5. Whole-word exact identity: every register's linear form after A, A+B
    #    and A+B+cleanup, over all registers (arbitrary dirty inputs included).
    for upto in (("A",), ("A", "B"), ("A", "B", "cleanup")):
        so = symbolic([e for k in upto for e in old[k]])
        sn = symbolic([e for k in upto for e in new[k]])
        keys = set(so) | set(sn)
        assert all(so.get(r, {r: 1}) == sn.get(r, {r: 1}) for r in keys), ("map differs", upto)
    forms_checked = len(keys)
    for k in old:
        if k not in ("A", "cleanup", "report"):
            assert old[k] == new[k], k
    scalar_events = lambda w: sum(len(w[k]) for k in ("precondition", "cut", "A", "B", "cleanup"))
    saved_events = scalar_events(old) - scalar_events(new)
    assert saved_events == CLAIM["scalar_saved_with_cleanup"] == 2 * 14 * (87 - 34)

    # 6. Inherited native audit (all 716 columns, compensation, frames, edges),
    #    emitter and local auditor on both words; compare and recount.
    ao, po, co, lo = native(tmp / "old/FULL-WORD.json.gz", tmp / "before", tmp)
    an, pn, cn, ln = native(gz, tmp / "after", tmp)
    assert ao["scalar_operations"] - an["scalar_operations"] == saved_events
    rng, lowering = random.Random(681), {}
    for ori in ("forward", "backward"):
        assert co[ori]["paid_profile"] == cn[ori]["paid_profile"]
        # Frame climbs fire at a register's first touch, so the new window
        # reorders them; the multiset and every register's climb path must hold.
        no, nn = ([e for e in p_[ori] if e[0] != "scalar"] for p_ in (po, pn))
        assert Counter(map(json.dumps, no)) == Counter(map(json.dumps, nn)), "non-scalar events changed"
        assert [e for e in no if e[0] != "climb"] == [e for e in nn if e[0] != "climb"]
        path = lambda es: sorted((json.dumps(e[1:3]), i, e[3:]) for i, e in enumerate(x for x in es if x[0] == "climb"))
        assert [(r, c) for r, _, c in path(no)] == [(r, c) for r, _, c in path(nn)], "climb path changed"
        reordered = sum(x != y for x, y in zip(no, nn))
        so_ = [e[1] for e in po[ori] if e[0] == "scalar"]
        sn_ = [e[1] for e in pn[ori] if e[0] == "scalar"]
        assert len(so_) - len(sn_) == saved_events
        row = {"reordered_climb_events": reordered}
        for name, low in (("old_lowering", old_word), ("pr696_lowering", pr696_word)):
            b, a = (2 * sum(len(low(op)) for op in ws) for ws in (so_, sn_))
            assert (b, a) == CLAIM[name][ori], (name, ori, b, a)
            row[name] = {"before": b, "after": a, "saved": b - a, "percent": f"{100 * (b - a) / b:.2f}"}
        assert row["old_lowering"]["before"] == co[ori]["real_component_primitive_bound"]
        assert row["old_lowering"]["after"] == cn[ori]["real_component_primitive_bound"]
        # Randomised scalar replay of the emitted programs, dirty inputs incl. W.
        for trial in range(2):
            init = {}
            for op in so_ + sn_:
                for r in [op[1]] + ([op[2]] if op[0] in ("add", "copy") else []):
                    init.setdefault(tuple(r), Q(rng.randint(-10**6, 10**6), rng.randint(1, 999)))
            init[W] = Q(rng.randint(-10**6, 10**6), 7)
            x, y = dict(init), dict(init)
            for op in so_:
                run(x, pr696_word(op))
            for op in sn_:
                run(y, pr696_word(op))
            assert x == y, "emitted programs differ"
        row["prefix_l1_upper"] = {"before": lo["local"][ori]["prefix_l1_upper"],
                                  "after": ln["local"][ori]["prefix_l1_upper"]}
        assert Q(row["prefix_l1_upper"]["after"]) <= Q(row["prefix_l1_upper"]["before"])
        lowering[ori] = row

    selected = load(SELECTED)
    result = {
        "status": "PASS_PR681_INDEPENDENT_REPLAY",
        "windows": [{"A_start": s, "registers": [m[k] for k in range(8)], "frame": f} for s, m, f in hits],
        "linear_forms_checked": forms_checked,
        "scalar_events": {"before": scalar_events(old), "after": scalar_events(new), "saved": saved_events},
        "native_scalar_operations": {"before": ao["scalar_operations"], "after": an["scalar_operations"]},
        "real_component_primitives": lowering,
        "selected_kappa": selected["kappa"],
        "scope": "Raw PR622 constructor word only; selected CK/JP8 providers and the selected certificate are untouched.",
    }
    print(json.dumps(result, indent=1))
    f = lowering["forward"]
    print(f"PASS_PR681_INDEPENDENT_REPLAY windows=14 scalar_saved={saved_events} "
          f"fwd_primitives_old={f['old_lowering']['before']}->{f['old_lowering']['after']} "
          f"fwd_primitives_pr696={f['pr696_lowering']['before']}->{f['pr696_lowering']['after']} "
          f"kappa={selected['kappa']}")


if __name__ == "__main__":
    main()
