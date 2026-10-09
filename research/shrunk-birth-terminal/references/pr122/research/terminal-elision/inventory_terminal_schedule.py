"""Exact simultaneous output-chain check for terminal-role candidates."""
import argparse
from collections import defaultdict
import gzip
import json
from pathlib import Path
from frame_extension import basis, contains


def inspect(w, candidates):
    frames = {int(k): v for k, v in w['frames'].items()}
    sigma = {int(k): v for k, v in w['sigma'].items()}
    roots = {int(k): v for k, v in w['role_root'].items()}
    leaves = {int(k): v for k, v in w['leaf_of'].items()}
    initial = [[] for _ in range(w['v'])]
    for s in w['deferred']:
        for t in w['reach'][s]:
            assert contains(initial[t], sigma[s])
            initial[t] = sigma[s]
    bytarget = defaultdict(list)
    for s in sorted(set(candidates)):
        j = roots[s]
        t = w['target'][j]
        assert not w['kind'][j] and w['adjoint_centre'][s] is None
        assert {int(k):v for k,v in w['adjoint_ordinary'][s].items()} == {t:(21 if j<w['v'] else -21)}
        if s in leaves:
            bytarget[t].append((-1,s,frames[w['first_node'][s]]))
    phase1 = set(w['phase_one'])
    for i, o in enumerate(w['ops']):
        if o[0] == 'add': dst,src=o[1],o[2]
        elif o[0] == 'copy': src,dst=o[1],o[2]
        else:continue
        assert src not in candidates
        if dst in candidates:
            assert i not in phase1
            bytarget[w['target'][roots[dst]]].append((i,dst,frames[o[3]]))
    accepted, rejected, receipt = set(),set(),{}
    for t, seq in bytarget.items():
        seq.sort(key=lambda x:(x[0],x[1]))
        fs = [initial[t]]+[row[2] for row in seq]
        ok = all(contains(A,B) for A,B in zip(fs,fs[1:]))
        roles=set(s for _,s,_ in seq)
        (accepted if ok else rejected).update(roles)
        receipt[t]=dict(roles=sorted(roles),nested=ok,
                        frame_dimensions=[len(basis(f)) for f in fs],
                        event_indices=[i for i,_,_ in seq])
    assert accepted|rejected == set(candidates)
    return dict(accepted=sorted(accepted),rejected=sorted(rejected),
                target_count=len(bytarget),targets=receipt)


def main():
    p=argparse.ArgumentParser();p.add_argument('--word',type=Path,required=True)
    p.add_argument('--inventory',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();w=json.loads(gzip.decompress(a.word.read_bytes()))
    inv=json.loads(a.inventory.read_text());o=inspect(w,set(inv['terminal_roles']))
    a.out.write_text(json.dumps(o,indent=2)+'\n')
    print(json.dumps(dict(accepted=len(o['accepted']),rejected=len(o['rejected']),targets=o['target_count'])))


if __name__=='__main__':main()
