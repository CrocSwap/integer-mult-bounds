"""Mutation checks targeting the newly introduced44th alias, not an inherited one."""
from pathlib import Path
import argparse,copy,gzip,json,sys,tempfile,contextlib,io
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'borrow'))
import audit_local as A

def need(ok,label):
    if not ok:raise RuntimeError(label)

def main():
    p=argparse.ArgumentParser();p.add_argument('--word',type=Path,required=True);p.add_argument('--base',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    original=json.loads(gzip.decompress(a.word.read_bytes()));K=len(original['warps']);need(K==44,'requires new44-alias word')
    controls=[]
    with tempfile.TemporaryDirectory(prefix='borrow-extension-controls-') as td:
        def replay(w):
            q=Path(td)/'word.json.gz';q.write_bytes(gzip.compress(json.dumps(w).encode(),mtime=0))
            with contextlib.redirect_stdout(io.StringIO()):A.run(q,Path(td)/'receipt.json',None,a.base)
        replay(original)
        tests=[]
        w=copy.deepcopy(original);w['warps'][-1][2][0]=0;tests.append(('new alias singular basis map',w,'G not invertible'))
        w=copy.deepcopy(original);w['warps'][-1][4]=w['warps'][-1][4][:-1];tests.append(('new alias wrong handoff dimension',w,'dim(from)!=dim(to)'))
        w=copy.deepcopy(original);i=next(i for i,g in enumerate(w['cleanup']) if g[0]=='warp' and g[2]==-K);del w['cleanup'][i];tests.append(('new alias inverse omitted',w,'explicit cleanup differs'))
        w=copy.deepcopy(original);w['report']['local_profile']['4']+=1;tests.append(('new alias saving erased from claimed profile',w,'paid profile mismatch'))
        for label,w,expected in tests:
            try:replay(w)
            except RuntimeError as e:
                need(expected in str(e),label+': wrong rejection reason '+str(e));controls.append({'control':label,'rejected':True,'reason':str(e)})
            else:raise RuntimeError(label+': mutation accepted')
    out={'status':'PASS_NEW_ALIAS_NEGATIVE_CONTROLS','unmutated_passed':True,'new_operator':K,'controls':controls}
    a.out.write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');print(json.dumps(out))
if __name__=='__main__':main()
