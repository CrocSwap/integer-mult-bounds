"""Rebuild PR1207's X54 base from PR1195 with a frozen literal patch.

The scalar gate sequences and cleanup order must also equal the original
PR1130/1196 mapped recipe. Only frame choices may differ after the refit.
"""
import argparse
from pathlib import Path
from common import P,read,dump,load,identity

def build(base,out):
    assert not out.exists();old=read(base)
    assert old==read(P/'vendor/pr1195/FULL-WORD.json.gz')
    patch=load(P/'vendor/pr1195/build_word.py','retained_literal_patch_builder')
    new=patch.build(old,read(P/'data/X54-LITERAL-PATCH.json'))
    assert new==read(P/'vendor/pr1207/BASE-X54-WORD.json.gz')
    tri=load(P/'vendor/pr1207/build_tri.py','retained_x54_recipe')
    semantic=tri.apply(old,read(P/'vendor/pr1207/MAPPED-RECIPE.json'))
    for section in ('A','B','cleanup'):
        assert [g[:-1]for g in new[section]]==[g[:-1]for g in semantic[section]],section
    assert [x[0]for x in new['early_cleanup']]==[x[0]for x in semantic['early_cleanup']]
    for key in ('start_extra','helper_final','ports','centers','center_frames'):
        assert new[key]==old[key]==semantic[key],key
    dump(out,new);return dict(status='PASS_LITERAL_X54_PATCH_AND_SOURCE_SCALAR_RECIPE',content_sha256=identity(new))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    for n in ('base','out'):ap.add_argument('--'+n,type=Path,required=True)
    a=ap.parse_args();print(build(a.base,a.out)['status'])
