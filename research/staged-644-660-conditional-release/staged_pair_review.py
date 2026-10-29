"""Source-stage audit for the two new staged pair words and actual defects.

The inherited free-operator auditor supplies the independent endpoint check.
Each defect has inverse cleanup regenerated, so failure is not stale cleanup.
"""
from pathlib import Path
import argparse,copy,gzip,hashlib,json,os,subprocess,sys
sys.dont_write_bytecode=True
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes()))
def need(x,s):
    if not x:raise AssertionError(s)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--borrow',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    b=a.borrow.resolve();o=a.out.resolve();need(not o.exists(),'fresh output');o.mkdir(parents=True)
    sys.path.insert(0,str(b));import staged_pair as producer
    audit=b/'audit_local.py';need(sha(audit)=='a38940094f7d19cd6376aafdd4734fa68eabc9aff4c98c3c4a3e9540328b1c90','inherited arbitrary-input audit pin')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');rows=[]
    def check(w,name):
        p=o/(name+'.json.gz');p.write_bytes(gzip.compress(json.dumps(w,separators=(',',':')).encode(),mtime=0))
        cmd=[sys.executable,'-B',str(audit),'--word',str(p),'--output',str(o/(name+'.audit.json'))]
        r=subprocess.run(cmd,capture_output=True,env=env);(o/(name+'.log')).write_bytes(r.stdout+r.stderr)
        return r.returncode==0
    for tag in ['base','extra']:
        old=b/f'inputs/PR3133-FINAL-{tag}.json.gz';new=b/f'words/BORROW-WORD-43{tag}.json.gz';rp=b/f'inputs/STAGED-PAIR-RECORD-{tag}.json.gz'
        parent,target,record=read(old),read(new),read(rp)
        need(producer.apply(parent,record)==target,'exact recorded stage')
        need(target['helper_final']==parent['helper_final'] and target['removed']==parent['removed'],'same restoration and physical helper set')
        need(target['compensation']==parent['compensation'] and target['initial_corrections']==parent['initial_corrections'],'same paid correction word')
        need(check(target,tag+'-positive'),'positive all-column audit')
        controls=[]
        for h in [644,660]:
            donor=640 if h==644 else 656
            i=next(i for i,g in enumerate(target['B']) if g[:3]==['add',donor,h])
            for kind in ['omit','flip']:
                w=copy.deepcopy(target)
                if kind=='omit':
                    w['B'].pop(i)
                    for warp in w['warps']:
                        if warp[0]>i:warp[0]-=1
                else:w['B'][i][3]*=-1
                w['cleanup']=producer.cleanup(w)
                need(not check(w,tag+'-'+str(h)+'-'+kind),'actual defect must be rejected')
                controls.append(str(h)+'-'+kind)
        rows.append(dict(provider=tag,parent_word_sha256=sha(old),word_sha256=sha(new),recipe_sha256=sha(rp),
                         positive_arbitrary_input_audit=True,regenerated_cleanup_controls_rejected=controls))
    (o/'RESULT.json').write_text(json.dumps(dict(status='PASS_STAGED_PAIR_SOURCE_BOUND_AUDIT',variants=rows,
       audit_sha256=sha(audit),producer_sha256=sha(b/'staged_pair.py'),scope='Deterministic source and finite arbitrary-input endpoint/control check; native physical context and all-size transfer remain separate.'),indent=2)+'\n')
    print('PASS_STAGED_PAIR_SOURCE_BOUND_AUDIT',flush=True)
if __name__=='__main__':main()
