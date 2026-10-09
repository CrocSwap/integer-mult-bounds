#!/usr/bin/env python3
"""Independent literal binding and full F2 basis semantics of the chosen words.

This imports no contributor semantic/replay routine. The strict scatter
binding helper is the earlier independent audit code. Paid frame profiles
and scalar-to-tape transfer require their separately stated checks.
"""
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUTPUTS = HERE.parents[1]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', type=Path, required=True)
    ap.add_argument('--package', default='research/cost-live-both')
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    helper = OUTPUTS/'audit/scatter_binding_audit.py'
    spec = importlib.util.spec_from_file_location('strict_scatter', helper)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    package = args.repo/args.package
    records = json.loads((package/'frame-compiler.json').read_text())
    result = dict(package=args.package, payload='F2', axes=[],
                  helper_sha256=hashlib.sha256(helper.read_bytes()).hexdigest(),
                  checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope='Literal binary linear word only; full profiles and physical transfer checked separately')
    for h in (23,25):
        path = package/f'frame-word-{h}.json.gz'
        raw = gzip.decompress(path.read_bytes())
        w = json.loads(raw)
        assert hashlib.sha256(raw).hexdigest() == records['axes'][str(h)]['word_sha256']
        scatter = mod.verify_scatter(w)
        v, R = w['v'], w['R']
        initial = [1 << i for i in range(2*v+R)]
        M = [(2*v+a,2*v+b) for a,b,_ in w['ops']]
        J = [tuple(x) for x in w['scatter']]
        V = [(2*v+s,int(i)) for i,s in w['sources'].items()]
        word = M+J+M[::-1]+V+M+J+M[::-1]+V
        for dual in (False,True):
            state = initial.copy()
            for t,s in reversed(word) if dual else word:
                if dual:
                    t,s = s,t
                assert t != s and 0 <= t < len(state) and 0 <= s < len(state)
                state[t] ^= state[s]
            expected = initial.copy()
            for i in range(v):
                expected[i if dual else v+i] ^= initial[v+i if dual else i]
            assert state == expected
        result['axes'].append(dict(h=h, R=R, basis_size=len(initial),
                                   complete_both_orientations=True, literal_scatter=scatter,
                                   raw_word_sha256=hashlib.sha256(raw).hexdigest()))
        print(f'PASS h={h} independent complete F2 basis and exact scatter binding', flush=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')

if __name__ == '__main__':
    main()
