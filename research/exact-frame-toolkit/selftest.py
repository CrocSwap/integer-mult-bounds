"""selftest: reproduce published facts with the toolkit, using only files already on main, and run its failure-mode controls.

 1. kappa.py reproduces #1094's selected kappa (T16) and #942's checkpoint kappa (T37) from their exact global profiles.
 2. The seven-slot k8 word: the surrogate optimum equals its published local profile (integer certificate), and the
    true-moment interval at b puts its published frames within a rigorous width (< 1e-6 units) of the minimum over the model.
 3. Controls: the interval of a deliberately worse assignment has the exact width of its true excess; the exact dual bound
    stays below the primal for multipliers beyond int64 and rejects non-finite ones; a port written in B and undone in an
    early tail passes the B+tail map screen, but the harness rejects it (compensation-changed) and audit_local fails it.
 4. Each of #1018's seven slots is worth -1788 surrogate units on the pre-slot word; together -12516 = the seven-slot profile;
    every slot is a certified true-moment gain at b (true -1784.83 units each, -12493.80 together).
 5. At the X=439 and X=444 slot sites, the source-holder fusion with full read-set exchange is worth -3957 each.
 6. Five slots plus the two fusions: -16854, audit_local PASS, unchanged interfaces, kappa 0.001672756914849856 on #1094's owners.
Words are read from the retained #1042/#1094 replay archives. usage: python -B selftest.py [--quick]   (--quick: steps 1-4)"""
import argparse, gzip, hashlib, json, random, sys, tarfile, tempfile, time
from fractions import Fraction as Q
from pathlib import Path
from paths import ROOT
import numpy as np
import harness as C, kappa as KA, slots as SL, frames as F, writeback as WB
from word import inline
from compat import child_env
SEVEN = ("research/community-frontier1094-audit/selected-replay.tar.gz", "candidate/strict/global/base/providers/gauge44/FULL-WORD.json.gz",
         "c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8")
PRE = ("research/community-frontier1042-audit/selected-replay.tar.gz", "chain/frames/FULL-WORD.json.gz",
       "db2c7cfb3f8eee2b76c2e0154fc530520fb4d90cd9511a002cab527b16033b83")
failures = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (" | " + detail if detail else ""), flush=True)
    if not ok: failures.append(name)
def extract(spec, d):
    archive, member, payload_sha = spec
    with tarfile.open(ROOT / archive) as t:
        m = t.getmember(member)
        if not m.isfile(): raise RuntimeError(f"archive member is not a regular file: {member}")
        raw = t.extractfile(m).read()
    if hashlib.sha256(gzip.decompress(raw)).hexdigest() != payload_sha: raise RuntimeError(f"payload pin mismatch: {member}")
    p = Path(d) / (payload_sha[:8] + ".json.gz"); p.write_bytes(raw); return str(p)
def prof(w): return {int(k): v for k, v in w['report']['local_profile'].items()}
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter); ap.add_argument("--quick", action="store_true"); a = ap.parse_args()
    t0 = time.time(); d = tempfile.mkdtemp(prefix="eft-selftest-"); seven, pre = extract(SEVEN, d), extract(PRE, d)
    rep = json.loads((ROOT / "research/community-frontier1094-audit/REPLAY.json").read_text(encoding="utf-8"))
    k, _ = KA.kappa(rep['complex_profile'], 16); check("kappa T16 = #1094 selected", k == Q(rep['kappa']), str(k))
    cp = json.loads((ROOT / "certificates/checkpoints/frontier942.json").read_text(encoding="utf-8")); asm = json.loads((ROOT / cp['certificate']).read_text(encoding="utf-8"))
    k, _ = KA.kappa(asm['complex_profile'], 37); check("kappa T37 = #942 checkpoint", k == Q(cp['kappa']), str(k))
    W7 = C.load(seven); P7 = C.Pricer(seven, interval=True); p7 = {r: n for r, n in prof(W7).items() if r != 8}; iv7 = P7.base_interval
    check("seven-slot frames: surrogate optimum = published profile", P7.base_certified and P7.base_profile == p7, str(P7.base_profile))
    check("seven-slot frames: true-moment interval at b", iv7['fine_profile'] == p7 and not iv7['surrogate_not_minimal'] and 0 <= iv7['width_units'] < 1e-6,
          f"published frames within {iv7['width_units']:.3g} units of the minimum (surrogate rounding bound {P7.costs.moment_upper(p7) * 2**40 - P7.base_cost:.1f})")
    # controls
    g = F.Graph(inline(P7.base, True), check_literal=True, tail_mutable=True, caps=P7.caps, cut_equality=True)
    r7 = F.optimal_frames(inline(P7.base, True), P7.costs, check_literal=True, graph=g); a7 = r7['assign']
    fr = lambda k, a: a[k] if k in g.varset else g.nodes[k][1]
    def worse(a):
        for k in g.var:
            for Fx in g.dom[k]:
                if len(Fx) != len(a[k]) and all(F.leq(fr(g.prev[k, q], a), Fx) and F.leq(Fx, fr(g.nxt[k, q], a)) for q in g.nodes[k][0]):
                    b = dict(a); b[k] = Fx; return b
    a2 = worse(a7); iv2 = F.moment_interval(g, P7.costs, a2); excess = (P7.costs.moment_upper(g.profile(a2)) - P7.costs.moment_upper(g.profile(a7))) * 2**40
    check("control: interval width of a worse assignment = its true excess", iv2['lower'] == iv7['lower'] and excess > 1 and abs(iv2['width_units'] - float(excess) - iv7['width_units']) < 1e-6,
          f"excess {float(excess):.2f} units, width {iv2['width_units']:.2f}")
    comp = max(g.components, key=len); dd = F.ChainDD(g, P7.costs, var_subset=comp); rd = dd.solve(); rnd = random.Random(7)
    for k in dd.mu: dd.mu[k] = np.array([float(rnd.choice((-1, 1)) * 2 ** rnd.randint(62, 90)) for _ in dd.mu[k]])
    huge = dd.dual_bound_exact(); k0 = next(iter(dd.mu)); dd.mu[k0] = dd.mu[k0].copy(); dd.mu[k0][0] = float('nan')
    try: dd.dual_bound_exact(); nan_rejected = False
    except ValueError: nan_rejected = True
    check("control: exact dual with multipliers beyond int64 stays a lower bound; NaN rejected", rd['certified'] and huge <= rd['primal'] and nan_rejected,
          f"bound {huge:.3e} <= primal {rd['primal']}")
    nB = len(W7['B']); ed = dict(delete=[], insert=[[nB, ["add", 132, 390, 1, 1, []]]], tail=[[0, ["add", 132, 390, -1, 1, []]]], prepend=[])
    w1 = C.compile_edits(P7.base, ed); rp = P7.price(ed); ok1, rep1, _ = WB.audit(w1)
    check("control: port write undone in an early tail", C.exact_same(P7.base, w1, 0) and rp['status'] == 'compensation-changed' and not ok1 and 'endpoint failure' in str(rep1),
          f"screen passes, harness {rp['status']}, audit_local: {str(rep1)[:60]}")
    P = C.Pricer(pre, interval=True); inst = SL.split(P.base, json.load(open(SL.REC, encoding="utf-8")))
    sr = [P.price(SL.union([x])) for x in inst]; singles = [x['delta'] for x in sr]; allr = P.price(SL.union(inst))
    check("each slot -1788", singles == [-1788] * 7 and all(x['status'] == 'ok' and x['audit'] for x in sr), str(singles))
    check("all seven slots -12516, profile = seven-slot word", allr['delta'] == -12516 and allr['profile'] == p7 and allr['audit'], str(allr['profile']))
    check("slots are certified true-moment gains at b", all(x['gain_certified'] for x in sr + [allr]),
          f"true {sr[0]['realized_delta_units'][1]:.2f} units each, {allr['realized_delta_units'][1]:.2f} together")
    if not a.quick:
        import repair as R, fusion as G, subprocess
        R.init(pre); cs = G.candidates(R.P.base)
        for (t, A, H, h) in ((190, 439, 10, 584), (214, 444, 34, 590)):
            best = min((R.repair(c)['best'] or {'delta': 0, 'steps': ()} for c in cs if (c['t'], c['A'], c['H']) == (t, A, H)), key=lambda b: b['delta'])
            check(f"fusion t={t} A={A} H={H} -3957 with exchange of {h}", best['delta'] == -3957 and best['steps'] == (("exchange", h),), str((best['delta'], best['steps'])))
        out = Path(d) / "compose"; idle = json.dumps(rep['idle_remainder_profile'])
        r = subprocess.run([sys.executable, "-B", str(Path(__file__).with_name("compose.py")), pre, str(out), "--reference", seven, "--host", f"144:16:{idle}"], capture_output=True, text=True, encoding="utf-8", errors="replace", env=child_env())
        print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-800:])
        cj = json.loads((out / "COMPOSE.json").read_text(encoding="utf-8")) if (out / "COMPOSE.json").exists() else {}
        check("composition -16854, audit PASS, interfaces unchanged", cj.get('delta') == -16854 and cj.get('audit') is True and cj.get('interfaces_same') is True, str(cj.get('profile')))
        check("composition kappa on #1094 owners", list(cj.get('kappa', {}).values()) == ["26136826794529/15625000000000000"], str(cj.get('kappa')))
    print(f"{'SELFTEST PASS' if not failures else 'SELFTEST FAIL ' + str(failures)} in {time.time()-t0:.0f}s"); sys.exit(1 if failures else 0)
