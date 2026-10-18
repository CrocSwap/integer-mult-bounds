"""sites: run the repair step (repair.py) on chosen (t, A, H) fusions of a word, printing every fusion position/restore.
usage: python -B sites.py WORD.json.gz OUT.json t:A:H [t:A:H ...]      e.g. 190:439:10 214:444:34 on the pre-slot k8 word"""
import json, sys
import repair as R, fusion as G
if __name__ == "__main__":
    path, out = sys.argv[1], sys.argv[2]; want = [tuple(map(int, s.split(':'))) for s in sys.argv[3:]]
    R.init(path); cs = G.candidates(R.P.base); res = []
    for (t, A, H) in want:
        sub = [c for c in cs if (c['t'], c['A'], c['H']) == (t, A, H)]
        print(f"t={t} A={A} H={H}: {len(sub)} fusion candidates", flush=True)
        for c in sub:
            r = R.repair(c); res.append(r); b = r['best']
            print(f"   p={c['p']} rest={c['rest']} repairs={r['nrepairs']} tried={r['tried']} best={None if not b else (b['delta'], b['steps'], b['profile'])}", flush=True)
    json.dump(res, open(out, "w"))
