# SPDX-License-Identifier: Apache-2.0
"""Replay independent literal-owner and directed-rational moment certificates.
This is finite admission only. Run portable_frontier_cold.py for complete release checks,
and replay.py for the independent Lean kernel/axiom audit.
"""
from pathlib import Path
from fractions import Fraction
import argparse,hashlib,json,os,subprocess,sys,tempfile
sys.dont_write_bytecode=True
import verify as V
P=Path(__file__).resolve().parent

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,help='Fresh external output; default is a fresh system-temporary child.')
    a=ap.parse_args()
    V.need(__debug__,'enabled assertions required')
    pins=V.inventory(P);mh=V.digest(P/'MANIFEST.json')
    claim=json.loads((P/'CLAIM.json').read_text(encoding='utf8'))
    V.need(claim['status']=='COMPLETE_FINITE_RELEASE_PASSED_CONDITIONAL_KAPPA','complete conditional claim required')
    out=(a.out if a.out else Path(tempfile.mkdtemp(prefix='replica-independent-'))/'checked').resolve();V.need(not out.exists() and not out.is_relative_to(P),'fresh external output required')
    out.mkdir(parents=True)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1')
    env.pop('PYTHONOPTIMIZE',None)
    def run(name,script,*opts):
        r=subprocess.run([sys.executable,'-B',str(P/script),*map(str,opts)],env=env,cwd=out,text=True,encoding='utf8',stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=240)
        (out/(name+'.log')).write_text(r.stdout,encoding='utf8',newline='\n')
        V.need(r.returncode==0,'failed '+name+': '+r.stdout[-3000:])
        print('PASS_'+name.upper(),flush=True)
    run('owners','independent_candidate_owners_retired7.py','--replicas',claim['replicas'],
        '--order',P/'data/ORDER.json','--fill',P/'data/FILL.json.gz',
        '--dispatch',P/'data/DISPATCH.json','--profile',P/'data/PROFILE.json',
        '--out',out/'owners.json')
    run('moment','independent_candidate_moment_retired7.py','--owner-receipt',out/'owners.json',
        '--best-claim',P/'references/PR2802-CLAIM.json','--out',out/'moment.json')
    own=json.loads((out/'owners.json').read_text());m=json.loads((out/'moment.json').read_text())
    V.need(Fraction(m['proposed_outer_target'])==Fraction(claim['kappa']),'published headline rational binding')
    V.need(own['profile']==claim['profile'] and own['live']==claim['live'] and own['physical']==claim['physical'],'published complete profile/stock binding')
    V.need(V.inventory(P)==pins and V.digest(P/'MANIFEST.json')==mh,'source drift during independent checks')
    result=dict(status='PASS_INDEPENDENT_LITERAL_OWNERS_AND_EXACT_MOMENT',replicas=own['replicas'],
        roles=own['roles'],kappa=claim['kappa'],profile=own['profile'],
        rejected_owner_corruptions=len(own['controls']),rejected_moment_corruptions=len(m['controls']),
        owner_receipt_sha256=V.digest(out/'owners.json'),moment_receipt_sha256=V.digest(out/'moment.json'),
        manifest_sha256=mh,scope='Independent finite owner geometry and exact moment only; full native/global/outer release and formal audit are separate.')
    (out/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    print(result['status'],flush=True)
if __name__=='__main__':main()
