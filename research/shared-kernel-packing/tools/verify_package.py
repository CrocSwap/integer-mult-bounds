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
    cmds=[('construct',[root/'reproduce_t185.py','--baseline',base,'--relay-plan',root/'RELAY-PLAN.json','--out',work/'constructed']),('owners',[root/'tools/audit_owners2857.py','--source-package',base,'--candidate',root/'data','--out',work/'OWNERS.json']),('moment',[root/'tools/audit_moment2857.py','--source',base,'--candidate',root/'data','--out',work/'MOMENT.json']),('separate-review',[root/'review/review_current.py','--package',base,'--candidate',root/'data','--claim',root/'CLAIM.json','--field','kappa','--out',work/'REVIEW.json']),('exact-optimality',[root/'review/profile_lp_certificate.py','--package',base,'--candidate-profile',root/'data/PROFILE.json','--out',work/'lp'])]
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0');stages=[]
    for name,args in cmds:
        log=work/(name+'.txt')
        with log.open('w',encoding='utf-8',newline='\n')as out:proc=subprocess.run([sys.executable,'-B',*map(str,args)],env=env,cwd=work,stdout=out,stderr=subprocess.STDOUT)
        need(proc.returncode==0,'failed '+name+'; inspect '+str(log));stages.append(dict(stage=name,exit_code=0,output_sha256=sha(log)));print('PASS',name,flush=True)
    for name in ['FILL.json.gz','ORDER.json','DISPATCH.json','PROVIDERS.json','PROFILE.json']:need(sha(work/'constructed'/name)==sha(root/'data'/name),'byte-exact constructed '+name)
    claim=rd(root/'CLAIM.json');admission=rd(root/'evidence/ADMISSION-RESULT.json');release=rd(root/'evidence/RELEASE-RECEIPT.json');native=rd(root/'evidence/NATIVE-RESULT.json');moment=rd(work/'MOMENT.json');lp=rd(work/'lp/RESULT.json')
    need(admission['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'and release['status']=='PASS_RELEASE','stored complete release statuses')
    need(Q(claim['kappa'])==Q(admission['kappa'])==Q(release['kappa_decimal'])==Q(moment['target']),'exact verified headline binding')
    need(sha(root/'evidence/RELEASE-RECEIPT.json')==admission['release_receipt_sha256']==claim['release_receipt_sha256'],'complete release receipt binding')
    need(sha(root/'evidence/NATIVE-RECEIPT.json')==native['native_receipt_sha256'],'fresh shared-native binding')
    need(claim['native_receipt_sha256']==admission['native_receipt_sha256']==native['native_receipt_sha256'],'headline native provenance binding')
    need(lp['status']=='PASS_EXACT_CURRENT_INVENTORY_PRIMAL_DUAL_AND_ACTUAL_ATTAINMENT'and lp['pattern_count']==1163,'complete fixed-model optimality')
    need(authenticate(root)==pins,'read-only package drift')
    result=dict(status='PASS_T185_PACKAGE_CONSTRUCTION_OWNER_MOMENT_AND_OPTIMALITY',package_manifest_sha256=sha(root/'MANIFEST.json'),stages=stages,scope='Fresh exact construction and independent finite/LP checks; complete source/native/outer receipts authenticated. Fresh full replay is reproduce.py; inherited all-size hypotheses remain. Optimality applies only to fixed native words/inventory/capacities.')
    (work/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n');print(result['status'])
if __name__=='__main__':main()
