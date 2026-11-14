"""Reconstruct signed-554 scalar edits and reject broken restoration recipes.

The predecessor's exact sparse-rational map engine is retained unchanged.
Frames are validated separately by the independent raw and native replays.
"""
import argparse, copy, importlib.util, json
from fractions import Fraction as Q
from pathlib import Path

assert __debug__, 'assertions required'
P = Path(__file__).resolve().parent
s = importlib.util.spec_from_file_location('original566', P/'vendor/pr1625/rebuild.py')
C = importlib.util.module_from_spec(s); s.loader.exec_module(C)

def check(base, new, edit):
    B, cleanup, early = C.compile_edits(base, edit)
    seq = B + [cleanup[i] for i in early]
    original = [C.ops(g) for g in base['B']] + [C.ops(base['cleanup'][i]) for i, _ in base['early_cleanup']]
    before, after = C.rows(original), C.rows(seq)
    equal = all(before.get(k, {k: Q(1)}) == after.get(k, {k: Q(1)}) for k in set(before)|set(after))
    rest = [g for i,g in enumerate(cleanup) if i not in set(early)]
    old_rest = [C.ops(g) for i,g in enumerate(base['cleanup']) if i not in {j for j,_ in base['early_cleanup']}]
    writes = [i for i,g in enumerate(seq) if g[1] == 554]
    signed = len(writes) == 3 and [seq[i][0] for i in writes] == ['add','scale','add'] and C.rows(seq[:writes[-1]+1]).get(554) == {554: Q(-1)}
    return dict(exact_map=equal, remaining_cleanup=rest == old_rest, signed_restoration=signed,
                scalar_program=(B == [C.ops(g) for g in new['B']] and cleanup == [C.ops(g) for g in new['cleanup']] and early == [i for i,_ in new['early_cleanup']]),
                interface=all(base.get(k) == new.get(k) for k in C.INTERFACE))

ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
edit=json.loads((P/'inputs/EDIT.json').read_text()); result={}
for name in ['gauge44','extra']:
    base=C.load(P/f'vendor/pr1625/inputs/{name}-word-566.json.gz'); new=C.load(P/f'inputs/{name}-word.json.gz')
    row=check(base,new,edit); assert all(row.values()), (name,row)
    controls={}
    for i in range(len(edit['insert'])):
        bad=copy.deepcopy(edit); bad['insert'].pop(i)
        controls[f'omit_insert_{i}']=not check(base,new,bad)['exact_map']
    bad=copy.deepcopy(edit); bad['tail']=[]; controls['omit_tail']=not check(base,new,bad)['exact_map']
    bad=copy.deepcopy(edit); bad['tail'][0][1][3]*=-1; controls['wrong_tail_sign']=not check(base,new,bad)['exact_map']
    bad=copy.deepcopy(edit); bad['delete']=[]; controls['retain_deleted_read']=not check(base,new,bad)['exact_map']
    assert all(controls.values()), (name,controls)
    result[name]=dict(checks=row,rejected=controls)
a.out.write_text(json.dumps(dict(status='PASS_SIGNED554_LITERAL_MAP_AND_CONTROLS',words=result),sort_keys=True,indent=2)+'\n')
print('PASS signed554 literal maps and 16 negative controls')
