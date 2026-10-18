"""Build both provider words from PR1148's joint-entrance word by frozen literal patches, without optimization.

data/RECIPE-THREE.json: PR1195's two source-holder fusions (X=439, X=444) and the PR1130/PR1178 X54/E589 slot.
data/RECIPE-FOUR.json: the same edits plus PR1193's four-helper entrance group 627 (data/FOUR-RECIPE.json).
Each recipe lists, for every changed list section, sequence-diff operations [tag, start, end, removed, added]
whose removed base elements are checked before use; whole replaced dictionary sections; and the report.
Base and output payloads are pinned. discovery/compose.py records how the recipes were composed.
"""
import argparse,copy,gzip,hashlib,json
from pathlib import Path
from common import P,read,sha

def apply(base,recipe):
    w=copy.deepcopy(base)
    for sec,ops in recipe['sections'].items():
        old=base[sec];out=[];pos=0
        for tag,i1,i2,removed,added in ops:
            assert tag in ('replace','delete','insert') and i1>=pos and old[i1:i2]==removed,(sec,tag,i1,i2)
            out+=old[pos:i1]+added;pos=i2
        w[sec]=out+old[pos:]
    for key,value in recipe['replaced'].items():
        assert key in base and not isinstance(base[key],list);w[key]=value
    w['report']=recipe['report']
    return w

def build(out3,out4):
    raw=gzip.decompress((P/'vendor/pr1148/JOINT-WORD.json.gz').read_bytes());base=json.loads(raw)
    result={}
    for name,out in (('THREE',out3),('FOUR',out4)):
        assert not out.exists()
        recipe=read(P/('data/RECIPE-%s.json'%name))
        assert hashlib.sha256(raw).hexdigest()==recipe['base_content_sha256'],'joint word pin'
        data=json.dumps(apply(base,recipe),separators=(',',':')).encode()
        assert hashlib.sha256(data).hexdigest()==recipe['output_content_sha256'],'output pin '+name
        assert json.loads(data)==read(P/('data/%s-WORD.json.gz'%name))
        out.write_bytes(gzip.compress(data,mtime=0))
        result[name.lower()]=dict(content_sha256=recipe['output_content_sha256'],recipe_sha256=sha(P/('data/RECIPE-%s.json'%name)))
    four=read(P/'data/FOUR-RECIPE.json');word4=read(out4)
    for helper,old,new in four['start_extra']:assert word4['start_extra'][helper]==new
    return dict(status='PASS_FROZEN_FUSIONS_X54_RECIPES',source_sha256=sha(P/'vendor/pr1148/JOINT-WORD.json.gz'),**result)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out3',type=Path,required=True);ap.add_argument('--out4',type=Path,required=True);a=ap.parse_args()
    print(build(a.out3,a.out4)['status'])
