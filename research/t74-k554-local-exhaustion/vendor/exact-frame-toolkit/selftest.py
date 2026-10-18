"""selftest: reproduce published facts with the toolkit, using only files already on main.

 1. kappa.py reproduces #1094's selected kappa (T16) and #942's checkpoint kappa (T37) from their exact global profiles.
 2. The exact frame solver reproduces the seven-slot k8 word's published local profile (its frames are optimal).
 3. Each of #1018's seven slots is worth -1788 cost units on the pre-slot word; together -12516 = the seven-slot profile.
 4. At the X=439 and X=444 slot sites, the source-holder fusion with full read-set exchange is worth -3957 each.
 5. Five slots plus the two fusions: -16854, audit_local PASS, unchanged interfaces, kappa 0.001672756914849856 on #1094's owners.
Words are read from the retained #1042/#1094 replay archives. usage: python -B selftest.py [--quick]   (--quick: steps 1-3)"""
import argparse, gzip, hashlib, json, sys, tarfile, tempfile, time
from fractions import Fraction as Q
from pathlib import Path
from paths import ROOT
import harness as C, kappa as KA, slots as SL
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
        m = t.getmember(member); assert m.isfile(); raw = t.extractfile(m).read()
    assert hashlib.sha256(gzip.decompress(raw)).hexdigest() == payload_sha, ("payload pin", member)
    p = Path(d) / (payload_sha[:8] + ".json.gz"); p.write_bytes(raw); return str(p)
def prof(w): return {int(k): v for k, v in w['report']['local_profile'].items()}
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter); ap.add_argument("--quick", action="store_true"); a = ap.parse_args()
    t0 = time.time(); d = tempfile.mkdtemp(prefix="eft-selftest-"); seven, pre = extract(SEVEN, d), extract(PRE, d)
    rep = json.loads((ROOT / "research/community-frontier1094-audit/REPLAY.json").read_text())
    k, _ = KA.kappa(rep['complex_profile'], 16); check("kappa T16 = #1094 selected", k == Q(rep['kappa']), str(k))
    cp = json.loads((ROOT / "certificates/checkpoints/frontier942.json").read_text()); asm = json.loads((ROOT / cp['certificate']).read_text())
    k, _ = KA.kappa(asm['complex_profile'], 37); check("kappa T37 = #942 checkpoint", k == Q(cp['kappa']), str(k))
    W7 = C.load(seven); P7 = C.Pricer(seven); p7 = {r: n for r, n in prof(W7).items() if r != 8}
    check("seven-slot frames optimal", P7.base_profile == p7, str(P7.base_profile))
    P = C.Pricer(pre); inst = SL.split(P.base, json.load(open(SL.REC)))
    singles = [P.price(SL.union([x]))['delta'] for x in inst]; allr = P.price(SL.union(inst))
    check("each slot -1788", singles == [-1788] * 7, str(singles))
    check("all seven slots -12516, profile = seven-slot word", allr['delta'] == -12516 and allr['profile'] == p7, str(allr['profile']))
    if not a.quick:
        import repair as R, fusion as G, subprocess
        R.init(pre); cs = G.candidates(R.P.base)
        for (t, A, H, h) in ((190, 439, 10, 584), (214, 444, 34, 590)):
            best = min((R.repair(c)['best'] or {'delta': 0, 'steps': ()} for c in cs if (c['t'], c['A'], c['H']) == (t, A, H)), key=lambda b: b['delta'])
            check(f"fusion t={t} A={A} H={H} -3957 with exchange of {h}", best['delta'] == -3957 and best['steps'] == (("exchange", h),), str((best['delta'], best['steps'])))
        out = Path(d) / "compose"; idle = json.dumps(rep['idle_remainder_profile'])
        r = subprocess.run([sys.executable, "-B", str(Path(__file__).with_name("compose.py")), pre, str(out), "--reference", seven, "--host", f"144:16:{idle}"], capture_output=True, text=True)
        print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-800:])
        cj = json.loads((out / "COMPOSE.json").read_text()) if (out / "COMPOSE.json").exists() else {}
        check("composition -16854, audit PASS, interfaces unchanged", cj.get('delta') == -16854 and cj.get('audit') is True and cj.get('interfaces_same') is True, str(cj.get('profile')))
        check("composition kappa on #1094 owners", list(cj.get('kappa', {}).values()) == ["26136826794529/15625000000000000"], str(cj.get('kappa')))
    print(f"{'SELFTEST PASS' if not failures else 'SELFTEST FAIL ' + str(failures)} in {time.time()-t0:.0f}s"); sys.exit(1 if failures else 0)
