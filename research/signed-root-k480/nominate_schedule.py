"""Derive eight K-triangle schedules from PR635's four negative schedules.

Signed-root reflection nominates the positive read orders; it does not prove
their frame legality. The unchanged constructor and native replay do that.
Prepared by Jeremy Diviney with substantial OpenAI Codex assistance.
Apache-2.0; retain the constructor's upstream attribution in code/ and NOTICE.md.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import tempfile

P = Path(__file__).resolve().parent

def nominate(hamming, base):
    original = json.loads(base.read_text())
    assert len(original['triangles']) == 4
    assert all(t['e'] == -1 for t in original['triangles'])
    # Evaluate the unchanged constructor only through its factory and requests.
    # No packet-copy omission or K-triangle read has happened at this marker.
    source = (P/'code/construct_k_triangle.py').read_text()
    marker = 'tri_join_counts=Counter()'
    assert source.count(marker) == 1
    old_argv = sys.argv[:]
    with tempfile.TemporaryDirectory() as tmp:
        sys.argv = ['construct', str(hamming), str(Path(tmp)/'prefix'), str(base)]
        context = {}
        try:
            exec(compile(source.split(marker)[0], 'pinned-constructor-prefix', 'exec'), context)
        finally:
            sys.argv = old_argv
    roots = context['R']
    index = {tuple(row): i for i,row in enumerate(roots)}
    result = []
    for negative in original['triangles']:
        pair = tuple(negative['p']); axis = pair[1]
        reflection = {}
        for i,row in enumerate(roots):
            row = row[:]; row[axis] *= -1; sign = 1
            if next(x for x in row if x) < 0:
                row = [-x for x in row]; sign = -1
            reflection[i] = (index[tuple(row)], sign)
        # Enumerate the required positive reads independently of their order.
        expected = []
        for t,(key,_) in context['reqcoef'].items():
            block,p,e = key
            if p != pair or e != 1: continue
            own = context['own_rows'][t][0]
            loc = next(k for k,v in context['maps'][block].items() if v == own)
            expected.append((t-8,block,loc))
            for other in sorted(context['blocks']):
                if other == block or not set(pair) <= set(other): continue
                j,_ = context['face_info'](other,pair,1)
                event = context['blocks'][other]['events'][j]
                expected.extend((t-8,other,loc) for loc in event[:2])
        allowed = {}
        for _,block,loc in expected: allowed.setdefault(block,set()).add(loc)
        reads = []
        for t,block,loc in negative['reads']:
            block = tuple(block)
            row = context['rows'][context['maps'][block][loc]]
            reflected = {reflection[j][0]:q*reflection[j][1] for j,q in row.items()}
            choices = []
            for candidate in sorted(allowed[block]):
                other = context['rows'][context['maps'][block][candidate]]
                if other.keys() != reflected.keys(): continue
                j = next(iter(other)); scale = reflected[j]/other[j]
                if all(reflected[k] == scale*other[k] for k in other): choices.append(candidate)
            assert len(choices) == 1, ('ambiguous reflected leaver',block,loc,choices)
            reads.append([reflection[t+8][0]-8,list(block),choices[0]])
        assert Counter((t,tuple(c),l) for t,c,l in reads) == Counter(expected)
        assert len(reads) == 30
        result.extend([negative,dict(p=list(pair),e=1,reads=reads)])
    return dict(full_pairs=original['full_pairs'],triangles=result)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--hamming',type=Path,required=True)
    ap.add_argument('--base',type=Path,default=P/'data/BASE-K492-SCHEDULE.json')
    ap.add_argument('--out',type=Path,required=True)
    a = ap.parse_args(); assert not a.out.exists()
    a.out.write_text(json.dumps(nominate(a.hamming,a.base),indent=2)+'\n')
    print('Nominated eight triangles; unchanged constructor and native audits required.')
