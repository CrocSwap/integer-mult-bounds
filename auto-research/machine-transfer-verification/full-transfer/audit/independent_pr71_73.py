"""Independent selected PR71/73 binary-word and rational-witness audit.

Run from the session workspace:
python3 outputs/full-transfer/audit/independent_pr71_73.py --repo CHECKOUT --output RECEIPT
The checkout must be pinned to PR73 253ecc88faeed55a950c76026d1fe67a7f690123.
No contributor semantic or arithmetic routine is imported. The shared independent
auditors are retained outputs from this research session and their hashes bind them.
"""
import argparse
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
OUTPUTS = HERE.parents[1]
sys.path.insert(0, str(OUTPUTS))
import independent_moment as im
import independent_assembly as ia

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    repo = args.repo.resolve()
    pin = subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
    assert pin == '253ecc88faeed55a950c76026d1fe67a7f690123'
    helper = OUTPUTS/'audit/scatter_binding_audit.py'
    spec = importlib.util.spec_from_file_location('strict_scatter',helper)
    strict = importlib.util.module_from_spec(spec); spec.loader.exec_module(strict)
    record = json.loads((repo/'certificates/split-pair-compiler.json').read_text())
    result = dict(source_pin=pin, payload='F2', axes=[], arithmetic=[],
                  independent_sources={str(p.relative_to(OUTPUTS)):sha256(p.read_bytes()).hexdigest()
                    for p in (Path(__file__), helper, Path(im.__file__), Path(ia.__file__))},
                  scope='Exact scalar words and supplied finite profiles; full physical transfer remains separate.')
    for h in (23,25):
        path = repo/f'certificates/split-pair-word-{h}.json.gz'
        raw = gzip.decompress(path.read_bytes()); w = json.loads(raw)
        assert sha256(raw).hexdigest() == record['axes'][str(h)]['word_sha256']
        scatter = strict.verify_scatter(w)
        v,R = w['v'],w['R']
        initial = [1 << i for i in range(2*v+R)]
        M = [(2*v+a,2*v+b) for a,b,_ in w['ops']]
        J = [tuple(x) for x in w['scatter']]
        V = [(2*v+s,int(i)) for i,s in w['sources'].items()]
        word = M+J+M[::-1]+V+M+J+M[::-1]+V
        for dual in (False,True):
            state = initial.copy()
            for t,s in reversed(word) if dual else word:
                if dual: t,s = s,t
                assert t != s and 0 <= t < len(state) and 0 <= s < len(state)
                state[t] ^= state[s]
            expected = initial.copy()
            for i in range(v): expected[i if dual else v+i] ^= initial[v+i if dual else i]
            assert state == expected
        files = [path, repo/f'certificates/split-pair-profiles-{h}.json',
                 repo/f'certificates/split-pair-transitions-{h}.json']
        result['axes'].append(dict(h=h,R=R,basis_size=len(initial),complete_both_orientations=True,
            raw_word_sha256=sha256(raw).hexdigest(),literal_scatter=scatter,
            inputs={str(p.relative_to(repo)):sha256(p.read_bytes()).hexdigest() for p in files}))
        print(f'PASS h={h}: independent literal F2 basis, arbitrary dirty columns and scatter binding',flush=True)
    names = ['certificates/split-pair-kappa.json','research/round6-pr71/parameter-certificate.json']
    certs = [json.loads((repo/name).read_text()) for name in names]
    # PR71 embeds two arithmetic enclosures inside `bit`; PR73 moves these
    # to top-level fields. Compare every remaining physical/profile field.
    physical71 = {k:v for k,v in certs[0]['bit'].items() if k not in ('moment','excluded_moment')}
    assert physical71 == certs[1]['bit']
    assert certs[0]['finite_bridge'] == certs[1]['finite_bridge']
    for name,c in zip(names,certs):
        mr = im.run(repo/name,search=False);mr['source']=name
        h = Q(1,10**12) if name == names[0] else Q(1,10**18)
        ar = ia.assemble(c,Q(c['bit_saving']),Q(c['kappa']),h)
        original = c['assembly'] if name == names[0] else c['preferred']['assembly']
        assert ar['constraints'] == {n:Q(v) for n,v in original['constraints'].items()}
        assert ar['margins'] == {n:Q(v) for n,v in original['margins'].items()}
        nextlo,nexthi = im.moment(c['bit']['m'],c['bit']['W'],
            {int(t):n for t,n in c['bit']['child_multiplicities'].items()},Q(c['bit_saving'])+Q(1,10**18))
        assert nextlo > 1
        result['arithmetic'].append(dict(moment=mr,assembly=ar,next_saving_moment=[nextlo,nexthi]))
        print(f'PASS {name}: independent characteristic and 47 inequalities/seven margins',flush=True)
    result['same_profile_and_finite_bridge']=True
    result['parameter_only_kappa_gain']=Q(certs[1]['kappa'])-Q(certs[0]['kappa'])
    args.output.write_text(json.dumps(im.encode(result),indent=2)+'\n')

if __name__ == '__main__': main()
