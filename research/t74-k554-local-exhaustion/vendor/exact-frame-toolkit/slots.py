"""slots: split a triangle-hybrid slot recipe (build_tri format, default RECIPE-SLOTS-k8.json of #1018) into its instances
and price every instance alone and all together on the pre-slot word with the exact frame solver.
usage: python -B slots.py PRE_WORD.json.gz OUT.json [--recipe RECIPE.json]
Recipe instances are partitioned by register sets {X, E, holders}; the partition must cover every recipe edit exactly once."""
import argparse, json
import harness as C
from paths import SLOT_RECIPE as REC
def split(w, rc):
    B = w['B']; inst = []
    for v in rc['variants']:
        S = {v['X'], v['E'], *v['hold']}; sel = lambda g: bool({g[1], g[2]} & S)
        inst.append(dict(X=v['X'], delete=[i for i in rc['B_delete'] if sel(B[i])], insert=[(p, g) for p, g in rc['B_insert'] if sel(g)],
                         tail=[(j, g) for j, g in rc['tail_insert'] if sel(g)], prepend=[g for g in rc['cleanup_prepend'] if sel(g)]))
    for key, rk in (('delete', 'B_delete'), ('insert', 'B_insert'), ('tail', 'tail_insert'), ('prepend', 'cleanup_prepend')):
        assert sum(len(x[key]) for x in inst) == len(rc[rk]), ("recipe partition", key)
    return inst
def union(parts):
    ed = dict(delete=[], insert=[], tail=[], prepend=[])
    for x in parts:
        for k in ed: ed[k] += list(x[k])
    ed['delete'] = sorted(ed['delete']); ed['insert'] = sorted(ed['insert'], key=lambda t: t[0]); ed['tail'] = sorted(ed['tail'], key=lambda t: t[0])
    return ed
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__); ap.add_argument("pre"); ap.add_argument("out"); ap.add_argument("--recipe", default=str(REC)); a = ap.parse_args()
    P = C.Pricer(a.pre); rc = json.load(open(a.recipe)); inst = split(P.base, rc); out = {}
    r = P.price(union(inst)); out['all'] = r; print("all slots:", r['status'], r.get('delta'), r.get('profile'), flush=True)
    for x in inst:
        r = P.price(union([x])); out['single_%d' % x['X']] = r; print(f"slot X={x['X']}: {r['status']} delta {r.get('delta')} {r.get('profile')}", flush=True)
    json.dump(dict(out=out, inst=inst), open(a.out, "w"))
