"""Semantic rejection controls for the composed fusion and X54 edits.

For both provider words, every scalar gate that RECIPE-THREE/RECIPE-FOUR inserts into B or cleanup
(PR1195 fusion donations/restores and PR1130 X54 donations/restores) is removed in turn, and each
mutant must be rejected by the independent exact local audit.
"""
import argparse,contextlib,copy,gzip,importlib.util,io,json,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def main():
    assert __debug__
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();assert not a.out.exists()
    spec=importlib.util.spec_from_file_location('audit',ROOT/'research/gauge44-slots/independent/audit_local.py')
    A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
    rejected=[]
    with tempfile.TemporaryDirectory(prefix='fusion-x54-controls-') as d:
        d=Path(d)
        for name in ('THREE','FOUR'):
            word=json.loads(gzip.decompress((P/('data/%s-WORD.json.gz'%name)).read_bytes()))
            recipe=json.loads((P/('data/RECIPE-%s.json'%name)).read_text())
            gates=[(sec,g) for sec in ('B','cleanup') for t,i1,i2,rem,add in recipe['sections'][sec]
                   for g in add if t=='insert' and g not in rem]
            for sec,g in gates:
                w=copy.deepcopy(word);i=w[sec].index(g);del w[sec][i]
                if sec=='cleanup':
                    w['early_cleanup']=[[j-(j>i),U] for j,U in w['early_cleanup'] if j!=i]
                f=d/'mutant.json.gz';f.write_bytes(gzip.compress(json.dumps(w).encode(),mtime=0))
                label='%s-drop-%s-%s'%(name,sec,g[:3])
                try:
                    with contextlib.redirect_stdout(io.StringIO()):A.run(f,d/'audit.json',ROOT)
                except RuntimeError as e:rejected.append(dict(control=label,reason=str(e)[:200]));continue
                raise AssertionError('control admitted: '+label)
    assert len(rejected)==28
    a.out.write_text(json.dumps(dict(status='PASS_FUSION_X54_SEMANTIC_CONTROLS',rejected=rejected),indent=2)+'\n')
    print('PASS',len(rejected),'composition controls')
if __name__=='__main__':main()
