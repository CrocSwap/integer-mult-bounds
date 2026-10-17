"""Apply a frozen four-helper entrance/frame recipe, without optimization."""
import argparse
from pathlib import Path
from common import P,read,dump,identity,sha

def build(out):
    assert not out.exists()
    word=read(P/'vendor/pr1148/JOINT-WORD.json.gz')
    recipe=read(P/'data/FOUR-RECIPE.json')
    assert set(recipe)=={'B','report','start_extra'}
    for helper,old,new in recipe['start_extra']:
        assert word['start_extra'][helper]==old
        word['start_extra'][helper]=new
    for index,old,new in recipe['B']:
        assert word['B'][index]==old
        # Scalar operation, registers and coefficient are unchanged.
        assert old[:-1]==new[:-1]
        word['B'][index]=new
    word['report']=recipe['report']
    assert word==read(P/'data/FOUR-WORD.json.gz')
    dump(out,word)
    return dict(status='PASS_FROZEN_FOUR_ENTRANCE_RECIPE',content_sha256=identity(word),
      source_sha256=sha(P/'vendor/pr1148/JOINT-WORD.json.gz'),recipe_sha256=sha(P/'data/FOUR-RECIPE.json'))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    print(build(a.out)['status'])
