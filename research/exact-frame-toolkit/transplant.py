"""transplant: put a target word's local interfaces (start_extra = entrance frames, helper_final = end frames) onto
a donor word's scalar program, re-solve every A/B/tail frame (surrogate optimum), audit, and price on the target's owner map.
Preconditions checked: the target's scalar program equals REF's (the word the donor's scalar edits were made against).
usage: python -B transplant.py DONOR.json.gz TARGET.json.gz REF.json.gz OUTDIR --calls 144 --T 16
       --idle '{"1":360,"24":1,"48":4918}' --target-kappa 0.001675560947524449"""
import argparse, copy, gzip, json, os, sys
from fractions import Fraction as Q
import harness as C, kappa as KA
from writeback import audit
def gates(w, sec): return [g[:-1] for g in w[sec]]
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("donor"); ap.add_argument("target"); ap.add_argument("ref"); ap.add_argument("outdir")
    ap.add_argument("--calls", type=int, required=True); ap.add_argument("--T", type=int, required=True); ap.add_argument("--idle", required=True)
    ap.add_argument("--target-kappa", required=True); a = ap.parse_args(); os.makedirs(a.outdir, exist_ok=True)
    donor, tgt, ref = C.load(a.donor), C.load(a.target), C.load(a.ref); idle = {int(k): v for k, v in json.loads(a.idle).items()}
    same = all(tgt[s] == ref[s] for s in ('cut', 'precondition', 'scatter', 'centers', 'ports')) and all(gates(tgt, s) == gates(ref, s) for s in ('A', 'B', 'cleanup'))
    same = same and [i for i, U in tgt['early_cleanup']] == [i for i, U in ref['early_cleanup']]
    print("target scalar program == reference scalar program:", same); assert same, "target changed the scalar program; transplant does not apply"
    tl = {int(k): v for k, v in tgt['report']['local_profile'].items()}
    k0, b0 = KA.kappa(KA.global_profile([(a.calls, tl)], idle), a.T); print("target kappa reproduced:", k0 == Q(a.target_kappa), float(k0))
    Pt = C.Pricer(tgt, b=str(b0)); print("target surrogate frame optimum:", Pt.base_profile, "| published", dict(sorted(tl.items())))
    w = copy.deepcopy(donor); w['start_extra'] = copy.deepcopy(tgt['start_extra']); w['helper_final'] = copy.deepcopy(tgt['helper_final'])
    w['report'] = dict(w['report']); w['report']['width_inventory'] = tgt['report']['width_inventory']
    P = C.Pricer(w, b=str(b0), check_literal=False); r = P.price(dict(delete=[], insert=[], tail=[], prepend=[]), want_word=True, timeout=900)
    print("composed:", r['status'], r.get('profile'), flush=True)
    W = r['word']; prof = dict(r['profile']); prof[8] = tl.get(8, 0)
    W['report'] = dict(W['report']); W['report']['local_profile'] = {str(k): v for k, v in sorted(prof.items())}
    ok, rep, sha = audit(W); print("audit_local", ok, sha)
    sameif = W['start_extra'] == tgt['start_extra'] and W['helper_final'] == tgt['helper_final']; print("interfaces identical to target:", sameif)
    print("local delta vs target:", {k: prof.get(k, 0) - tl.get(k, 0) for k in sorted(set(prof) | set(tl)) if prof.get(k, 0) != tl.get(k, 0)})
    k1, _ = KA.kappa(KA.global_profile([(a.calls, prof)], idle), a.T)
    print(f"kappa on target owners: {k1} = {float(k1):.18f}  vs target {a.target_kappa}  delta {float(k1 - Q(a.target_kappa)):+.3e}")
    open(os.path.join(a.outdir, "FULL-WORD.json.gz"), "wb").write(gzip.compress(json.dumps(W, separators=(',', ':')).encode(), mtime=0))
    json.dump(dict(profile=prof, audit=ok, sha=sha, interfaces_identical=sameif, kappa=str(k1), target_kappa=a.target_kappa), open(os.path.join(a.outdir, "RESULT.json"), "w", encoding="utf-8", newline="\n"), indent=1)
