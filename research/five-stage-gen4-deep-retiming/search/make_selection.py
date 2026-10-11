"""Convert a searched gate->basis assignment into a frozen descent selection (descent_transform format)."""
import json, hashlib, pickle, sys
from pathlib import Path
from collections import Counter
from search import setup
from bcd import BCD, restore
from frames import cost, saving_from_local

def sha_basis(B): return hashlib.sha256(json.dumps(B, separators=(',', ':')).encode()).hexdigest()

def main(path, out):
    d, L, ev, frame, ops, fixed, need = setup(); rec = d['rec']
    st = BCD(d, L, ev, frame, ops, fixed, need)
    obj = pickle.load(open(path, 'rb'))
    if obj and isinstance(next(iter(obj.values())), int): st.frame.update(obj)
    else: restore(st, path)
    old = json.load(open(Path(__file__).resolve().parents[2]/'five-stage-gen4-banks/descent-selection.json'))
    asg = {}
    for i, g in st.frame.items():
        if rec[6*i] == 1 and g != rec[6*i+4] and not (L.sub(g, rec[6*i+4]) and L.sub(rec[6*i+4], g)): asg[i] = g
    base = cost(d, L, {}); h = cost(d, L, asg)
    delta = Counter(h); delta.subtract(base); delta = {r: c for r, c in sorted(delta.items()) if c}
    entries = []
    for i in sorted(asg):
        op, a, b, c, f, z = rec[6*i:6*i+6]; g = asg[i]
        assert op == 1 and b != d['n'] and i not in fixed
        entries.append(dict(record=i, scalar=[a, b, c, z], old_dimension=L.dimf[f], old_basis_sha256=sha_basis(L.B[f]),
                            new_dimension=L.dimf[g], new_basis=[list(r) for r in L.B[g]]))
    sel = dict(status='FROZEN_CONCAVE_DESCENT_FRAME_SELECTION', input_raw_sha256=old['input_raw_sha256'],
               input_scalar_sha256=old['input_scalar_sha256'], source_record_count=old['source_record_count'],
               selected_gate_count=len(entries), expected_local_histogram_delta={str(r): c for r, c in delta.items()},
               expected_rank_mass=sum(r*c for r, c in h.items()), expected_removed_calls=sum(base.values())-sum(h.values()),
               expected_scalar_additions=old['expected_scalar_additions'], entries=entries)
    json.dump(sel, open(out, 'w'), indent=1); open(out, 'a').write('\n')
    desc = Counter({1: -1760, 2: 880, 20: -880, 21: 1760, 22: -880}); cur = Counter(base); cur.update(desc)
    print('gates', len(entries), 'calls', sum(h.values()), 'removed', sel['expected_removed_calls'], 'delta', delta, 'saving', saving_from_local(h, cur))

if __name__ == '__main__': main(sys.argv[1], sys.argv[2])
