# SPDX-License-Identifier: Apache-2.0
"""Replay actual construction, complete owners/moments and fixed-model optimality."""
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
def need(c,m):
    if not c:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):return json.loads(p.read_bytes())
def authenticate(root):
    pins=rd(root/'MANIFEST.json');actual={}
    for f in root.rglob('*'):
        need(not f.is_symlink(),'package symlink')
        if f.is_file()and f!=root/'MANIFEST.json':actual[f.relative_to(root).as_posix()]=sha(f)
    need(actual==pins,'complete package inventory/hashes');return pins

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--hash-only',action='store_true');ap.add_argument('--work',type=Path);a=ap.parse_args();need(not sys.flags.optimize,'assertions required');root=Path(__file__).resolve().parents[1];pins=authenticate(root)
    if a.hash_only:print(json.dumps(dict(status='PASS_COMPLETE_PACKAGE_HASHES',files=len(pins)+1)));return
    need(a.work is not None,'fresh external --work required');work=a.work.resolve();need(not work.exists()and not work.is_relative_to(root)and not root.is_relative_to(work),'fresh disjoint work');work.mkdir(parents=True);base=root/'vendor/pr2857'
    sys.path.insert(0,str(root/'vendor/pm'));import preload_move as PM
    for tag in ('base','extra'):
        shared=json.loads(__import__('gzip').decompress((base/'words'/('WORD-'+tag+'.json.gz')).read_bytes()));patch=rd(root/'vendor/pm'/('patch-'+tag+'.json'));word=json.loads(__import__('gzip').decompress((root/'vendor/pm/words'/('WORD-PM-'+tag+'.json.gz')).read_bytes()))
        derived,ledger=PM.apply(shared,patch);need(derived==word,'declared preload-move stage reproduces the shipped '+tag+' word exactly');need(ledger['A_inserted']==14 and len(ledger['A_replaced'])==2 and ledger['B_edits']==2 and ledger['start_extra_added']==['457','458'],'declared stage census '+tag)
    print('PASS declared-stage-apply',flush=True)
    cmds=[('owners',[root/'tools/audit_owners2857.py','--source-package',base,'--candidate',root/'data','--words',root/'vendor/pm/words','--out',work/'OWNERS.json']),('moment',[root/'tools/audit_moment2857.py','--source',base,'--candidate',root/'data','--out',work/'MOMENT.json']),('separate-review',[root/'review/review_current.py','--package',base,'--candidate',root/'data','--claim',root/'CLAIM.json','--field','kappa','--out',work/'REVIEW.json'])]
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0');stages=[]
    for name,args in cmds:
        log=work/(name+'.txt')
        with log.open('w',encoding='utf-8',newline='\n')as out:proc=subprocess.run([sys.executable,'-B',*map(str,args)],env=env,cwd=work,stdout=out,stderr=subprocess.STDOUT)
        need(proc.returncode==0,'failed '+name+'; inspect '+str(log));stages.append(dict(stage=name,exit_code=0,output_sha256=sha(log)));print('PASS',name,flush=True)
    claim=rd(root/'CLAIM.json');admission=rd(root/'evidence/ADMISSION-RESULT.json');release=rd(root/'evidence/RELEASE-RECEIPT.json');native=rd(root/'evidence/NATIVE-RESULT.json');moment=rd(work/'MOMENT.json')
    need(admission['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'and release['status']=='PASS_RELEASE','stored complete release statuses')
    need(Q(claim['kappa'])==Q(admission['kappa'])==Q(release['kappa_decimal'])==Q(moment['target']),'exact verified headline binding')
    need(sha(root/'evidence/RELEASE-RECEIPT.json')==admission['release_receipt_sha256']==claim['release_receipt_sha256'],'complete release receipt binding')
    need(sha(root/'evidence/NATIVE-RECEIPT.json')==native['native_receipt_sha256'],'fresh shared-native binding')
    need(claim['native_receipt_sha256']==admission['native_receipt_sha256']==native['native_receipt_sha256'],'headline native provenance binding')
    need(authenticate(root)==pins,'read-only package drift')
    result=dict(status='PASS_T74_PRELOAD_MOVE_PACKAGE_STAGE_OWNER_AND_MOMENT',package_manifest_sha256=sha(root/'MANIFEST.json'),stages=stages,scope='Declared preload-move stage re-applied to the PR2857 words; fresh independent owner (literal fill against widths derived from the shipped words), moment and separate-review checks; complete source/native/outer receipts authenticated. No optimality certificate is claimed for the new inventory. Fresh full replay is reproduce.py; inherited all-size hypotheses remain.')
    (work/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n');print(result['status'])
if __name__=='__main__':main()
