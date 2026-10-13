"""PR1130's four semantic X54 failures, in each composed scalar context.

Frame refits do not alter scalar sequences. Mutants must fail at the original
endpoint/entrance predicate, rather than a profile or unrelated frame check.
"""
import argparse,contextlib,io,tempfile
from pathlib import Path
from common import P,ROOT,read,dump,load,sha

def check(out):
    ck=load(ROOT/'research/gauge44-slots/independent/audit_local.py','x54_independent_raw_checker')
    tri=load(P/'vendor/pr1207/build_tri.py','source_x54_recipe_controls')
    rc=read(P/'vendor/pr1207/MAPPED-RECIPE.json')
    expected={'drop_restore':'all-column endpoint failure (False, ', 'restore_full':'all-column endpoint failure (False, ',
      'drop_preread':'nonzero entrance response','donation_after':'nonzero entrance response'}
    rejected=[]
    with tempfile.TemporaryDirectory(prefix='mixed-x54-controls-')as tmp:
        d=Path(tmp)
        def audit(word):
            dump(d/'WORD.json.gz',word)
            with contextlib.redirect_stdout(io.StringIO()):ck.run(d/'WORD.json.gz',d/'AUDIT.json',ROOT)
        for pid,base,path in [('demote3',P/'vendor/pr1195/FULL-WORD.json.gz',P/'vendor/pr1207/BASE-X54-WORD.json.gz'),
          ('demote4',P/'data/PRE-X54-FOUR-WORD.json.gz',P/'data/FOUR-WORD.json.gz')]:
            before,after=read(base),read(path);audit(after);sem=tri.apply(before,rc)
            for sec in ('A','B','cleanup'):
                assert [g[:-1]for g in sem[sec]]==[g[:-1]for g in after[sec]]
            for control,prefix in expected.items():
                bad=tri.apply(before,rc,control)
                try:audit(bad)
                except RuntimeError as error:
                    assert str(error).startswith(prefix),(pid,control,str(error))
                    rejected.append(dict(provider=pid,control=control,reason=str(error)))
                else:raise AssertionError('Accepted X54 control '+pid+' '+control)
    assert len(rejected)==8
    result=dict(status='PASS_BOTH_PROVIDERS_X54_SEMANTIC_CONTROLS',rejected=rejected,recipe_sha256=sha(P/'vendor/pr1207/MAPPED-RECIPE.json'))
    dump(out,result);return result

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    assert not a.out.exists();print(check(a.out)['status'])
