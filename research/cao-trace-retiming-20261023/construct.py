"""Source-bound scalar compression on Cao Yifan's final PR4610 word.

The triangle rewrite below is adapted verbatim except its helper628 exclusion
from Cinna Davis's PR4692 (scalar-trace-compression/verify.py), Apache-2.0.
That exclusion preserves the parent's entire chronological transport invoice.
Prepared for ahrazzle with substantial OpenAI Codex assistance.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import importlib.util,gzip,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('credited_scalar_compressor',ROOT/'research/scalar-trace-compression/verify.py')
T=importlib.util.module_from_spec(spec);spec.loader.exec_module(T)
roles,is_add,add=T.roles,T.is_add,T.add
SOURCE=ROOT/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'

def span(basis):
    s={0}
    for v in basis:s|={x^v for x in tuple(s)}
    return frozenset(s)

def triangles(program, spaces):
    """A B A^-1 shortcuts, requiring all moved-across roles to be disjoint."""
    deleted, replacements, counts = set(), {}, Counter()
    for i, first in enumerate(program):
        if i in deleted or i in replacements or not is_add(first):
            continue
        a, b = map(tuple, first[1][1:3])
        alpha = Q(*first[1][3:5])
        j = None
        for pos in range(i+1, min(i+180, len(program))):
            event = program[pos]
            if pos in deleted or pos in replacements or event[0] == 'phase':
                break
            if roles(event) & {a, b}:
                j = pos
                break
        if j is None or not is_add(program[j]):
            continue
        middle = program[j]
        x, y = map(tuple, middle[1][1:3])
        union = {a, b, x, y}
        if len(union) != 3 or ('L', 628) in union:
            continue
        k = None
        for pos in range(j+1, min(j+180, len(program))):
            event = program[pos]
            if pos in deleted or pos in replacements or event[0] == 'phase':
                break
            if roles(event) & union:
                k = pos
                break
        if k is None or not is_add(program[k]):
            continue
        last = program[k]
        if last[1][1:3] != first[1][1:3] or Q(*last[1][3:5]) != -alpha:
            continue
        if any(roles(event) & union for event in program[i+1:j]):
            continue
        frame = middle[2]
        if not spaces[first[2]] <= spaces[frame] <= spaces[last[2]]:
            continue
        beta = Q(*middle[1][3:5])
        if x == b and y not in {a, b}:
            replacement = [middle, add(a, y, -alpha*beta, frame)]
            kind = 'source_update'
        elif y == a and x not in {a, b}:
            replacement = [add(x, a, beta, frame), add(x, b, alpha*beta, frame)]
            kind = 'target_update'
        else:
            continue
        deleted.update((i, j, k))
        replacements[j] = replacement
        counts[kind] += 1
    result = []
    for index, event in enumerate(program):
        if index in replacements:
            result.extend(replacements[index])
        elif index not in deleted:
            result.append(event)
    return result, dict(sorted(counts.items()))


def construct():
    original=json.loads(gzip.decompress(SOURCE.read_bytes()));c=deepcopy(original['canonical'])
    spaces=[span(b) for b in c['frames']];programs={};history={}
    for direction,source in original['programs'].items():
        p=source;history[direction]=[]
        for iteration in range(6):
            combined,merge=T.combine(p)
            reduced,counts=triangles(combined,spaces)
            candidate=T.synthesize(c,reduced,spaces)
            T.need(T.paid(candidate)==T.paid(source),'Complete original paid profile at every rewrite stage')
            history[direction].append({'iteration':iteration,'merge':merge,'triangles':counts,'scalar_count':sum(e[0]=='scalar' for e in candidate)})
            if candidate==p:break
            p=candidate
        else:raise ValueError('Declared six-round compression budget exceeded')
        programs[direction]=p
    return original,{'canonical':c,'programs':programs},history

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--output');args=ap.parse_args()
    old,new,history=construct()
    if args.output:Path(args.output).write_bytes(gzip.compress(json.dumps(new,sort_keys=True,separators=(',',':')).encode(),mtime=0))
    print(json.dumps(history,sort_keys=True))
