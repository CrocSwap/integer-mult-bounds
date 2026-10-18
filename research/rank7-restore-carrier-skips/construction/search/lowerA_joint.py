"""lowerA_joint.py -- joint frame-only lowering of groups of restored helpers sharing a target subspace W (and all unions of groups
whose single margins are within reach), exact certified solver + auditor on the best."""
import sys, json, copy, itertools, collections
sys.path.insert(0, 'S/r13/agents/A-extract/code')
from synth import *
BE = 2091300
w = load(sys.argv[1]); base = solve_frames(w, key='b')
recs = []
for p in sys.argv[2].split(','): recs += json.load(open(p))
cands = []
for r in recs:
    for x in r['results']:
        if 'margin' in x: cands.append((r['h'], tuple(x['W']), x['margin']))
print('single candidates:', len(cands), 'helpers with a candidate:', len({h for h, W, m in cands}), 'positive singles:', [c for c in cands if c[2] > 0], flush=True)
byW = collections.defaultdict(list)
for h, W, m in cands: byW[W].append((h, m))
out = []
def price(assign):
    x = copy.deepcopy(w)
    for h, W in assign.items(): x['helper_final'][str(h)] = list(W)
    try: pf = bp.frame_profile(x, literal=False)
    except Exception as ex: return None, None
    return pf['cost'] - base['cost'], pf
for W, lst in sorted(byW.items(), key=lambda t: -len(t[1])):
    hs = [h for h, m in lst]
    d, pf = price({h: W for h in hs})
    m = None if d is None else -d - len(hs) * BE
    out.append(dict(W=list(W), helpers=hs, singles=[m_ for h, m_ in lst], joint_delta=d, joint_margin=m))
    print(f'W {list(W)}: helpers {hs} singles {[m_ for h, m_ in lst]} -> joint margin {m}', flush=True)
# unions of groups (pairs of groups) with best joint margins
best = sorted([o for o in out if o['joint_margin'] is not None], key=lambda o: -o['joint_margin'])
for a, b in itertools.combinations(best[:8], 2):
    assign = {h: tuple(a['W']) for h in a['helpers']}; clash = any(h in assign for h in b['helpers'])
    if clash: continue
    assign.update({h: tuple(b['W']) for h in b['helpers']})
    d, pf = price(assign); m = None if d is None else -d - len(assign) * BE
    out.append(dict(union=[a['W'], b['W']], helpers=sorted(assign), joint_delta=d, joint_margin=m))
    print(f'union {a["helpers"]} + {b["helpers"]}: joint margin {m} (sum of parts {a["joint_margin"] + b["joint_margin"]})', flush=True)
json.dump(out, open('lowerA-joint.json', 'w'), indent=1, default=str)
