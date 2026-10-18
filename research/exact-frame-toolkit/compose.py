"""compose: pre-slot k8 word + every slot of the slot recipe except those at the chosen sites + a source-holder fusion with
FULL-cleanup restore and full read-set exchange of the copy pair at each site. Surrogate-optimal frames, write-back, independent audit,
interface comparison with a reference word, and kappa on any owner maps given with --host.

usage: python -B compose.py PRE.json.gz OUTDIR [--sites 190:439:10:932 214:444:34:940] [--reference SEVEN_SLOT.json.gz]
           [--host 144:16:'{"1":2276,"3":377,"7":7,"48":4866}' ...]
A site is t:A:H:p (target, donated register, holder, donation position on the pre-slot word). Writes FULL-WORD.json.gz and
COMPOSE.json (edits, profile, audit, kappas)."""
import argparse, gzip, json, os
import harness as C, fusion as G, slots as SL, kappa as KA
from joint import swap_edit, merge
from exchange import copy_pairs, movable_reads
from writeback import audit
def cb2_edit(w, t, A, H, p):
    c = [c for c in G.candidates(w) if (c['t'], c['A'], c['H'], c['p'], c['rest']) == (t, A, H, p, 'prepend')]
    assert len(c) == 1, ("fusion", t, A, H, p, len(c)); ed0 = c[0]['ed']
    pr = copy_pairs(w); hs = [h for h, (r, ic) in pr.items() if A in (h, r)]; assert len(hs) == 1, ("copy pair of", A, hs); h = hs[0]; r, ic = pr[h]
    rest = [m for m in movable_reads(w, h, r, ic) if m[0] not in ed0['delete']]; ss = [swap_edit(w, h, r, ic, m) for m in rest]
    assert rest and all(ss), ("exchange", h); return merge([ed0] + ss), h
def interfaces(w): return {k: w[k] for k in ('start_extra', 'helper_final')}
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pre"); ap.add_argument("outdir"); ap.add_argument("--sites", nargs="+", default=["190:439:10:932", "214:444:34:940"])
    ap.add_argument("--recipe", default=str(SL.REC)); ap.add_argument("--reference"); ap.add_argument("--host", action="append", default=[])
    a = ap.parse_args(); os.makedirs(a.outdir, exist_ok=True); sites = [tuple(map(int, s.split(':'))) for s in a.sites]
    P = C.Pricer(a.pre); inst = SL.split(P.base, json.load(open(a.recipe, encoding="utf-8"))); cbe = []; xs = set()
    for (t, A, H, p) in sites:
        e, h = cb2_edit(P.base, t, A, H, p); cbe.append(e); xs.add(A); print(f"site t={t} A={A} H={H} pair ({h},{A}): {len(e['delete'])} deletes {len(e['insert'])} inserts {len(e['prepend'])} prepends")
    keep = [x for x in inst if x['X'] not in xs]; print("kept slots:", [x['X'] for x in keep])
    ed = merge([SL.union(keep)] + cbe); assert ed is not None, "delete conflict"
    ed['delete'] = sorted(ed['delete']); ed['insert'] = sorted(ed['insert'], key=lambda q: q[0]); ed['tail'] = sorted(ed['tail'], key=lambda q: q[0])
    r = P.price(ed, want_word=True, timeout=600); print("composed:", r['status'], "delta", r.get('delta'), r.get('profile'), flush=True)
    w = r['word']; prof = dict(r['profile']); prof[8] = {int(k): v for k, v in P.base['report']['local_profile'].items()}.get(8, 0)
    w['report'] = dict(w['report']); w['report']['local_profile'] = {str(k): v for k, v in sorted(prof.items())}
    ok, rep, sha = audit(w); print("audit_local", ok, sha)
    same = None
    if a.reference: same = interfaces(w) == interfaces(C.load(a.reference)); print("start_extra/helper_final identical to reference:", same)
    open(os.path.join(a.outdir, "FULL-WORD.json.gz"), "wb").write(gzip.compress(json.dumps(w, separators=(',', ':')).encode(), mtime=0))
    kap = {}
    for hspec in a.host:
        calls, T, idle = hspec.split(':', 2); k, _ = KA.price(prof, int(calls), int(T), {int(q): n for q, n in json.loads(idle).items()})
        kap[hspec] = str(k); print(f"kappa on host {calls} calls / T{T}: {k} = {float(k):.18f}")
    json.dump(dict(edits=ed, profile=prof, delta=r['delta'], audit=ok, sha=sha, interfaces_same=same, kappa=kap, sites=sites, kept_slots=[x['X'] for x in keep]), open(os.path.join(a.outdir, "COMPOSE.json"), "w", encoding="utf-8", newline="\n"), indent=1)
