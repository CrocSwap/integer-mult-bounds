"""Replay independent finite schedule evidence plus the repaired recurrence.

External scripts are retained byte-for-byte and Git-object pinned. Their
finite models check identities and failure modes, not an all-size machine.
"""
from pathlib import Path
import hashlib, json, os, subprocess, sys, tempfile

P=Path(__file__).resolve().parent


def need(ok,message):
    if not ok:raise RuntimeError(message)


def main():
    pins=json.loads((P/'external/SOURCE-PINS.json').read_text())
    for rec in pins['files']:
        blob=(P/'external'/rec['path']).read_bytes()
        need(hashlib.sha256(blob).hexdigest()==rec['sha256'],'external script changed')
        need(hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()==rec['git_blob_sha1'],
             'external script git object differs')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONHASHSEED='0')
    env.pop('PYTHONOPTIMIZE',None)
    need(__debug__,'assertions required')
    results={}
    paths={
        'recurrence':P/'check_recurrence.py',
        'product_diagonal':P/'external/outer-audit/pr1673-fusion/b_diag_tape.py',
        'ordered_embedding':P/'external/outer-audit/pr1673-fusion/a_qembed.py',
        'five_factor_group':P/'external/outer-audit/pr1673-fusion/c_fused_group.py',
    }
    with tempfile.TemporaryDirectory(prefix='phase-fusion-independent-controls-')as td:
        scratch=Path(td)
        for name,script in paths.items():
            output=scratch/(name+'.json')
            cp=subprocess.run([sys.executable,'-B',str(script),str(output)],
                              env=env,cwd=scratch,capture_output=True,text=True,timeout=180)
            need(cp.returncode==0,name+' failed\n'+cp.stdout[-1500:]+cp.stderr[-1500:])
            need(output.is_file(),name+' left no fresh output')
            result=json.loads(output.read_text())
            if name=='recurrence':
                need(result['status']=='PASS_EXACT_MIXED_RECURRENCE_AND_ORIGINAL_OUTER_COST_CONTROLS',name)
                need(result==json.loads((P/'RECURRENCE-CONTROLS.json').read_text()),
                     'retained recurrence receipt differs from fresh calculation')
                need(len(result['cost_exponents'])==12 and all(result['controls'].values()),name)
            elif name=='product_diagonal':
                need(len(result)>=20 and all(x['coef_moves_per_record']+x['suffix_moves_per_record']<7
                     and x['mults_per_record']<3 for x in result),'diagonal cost control failed')
            elif name=='ordered_embedding':
                need(result['exhaustive_axes_checked']>1000 and len(result['group_embedding'])==6,name)
                need(all(x['one_pass_moves']<x['per_axis_pass_moves']for x in result['group_embedding']),name)
            else:
                need(len(result)==6 and all(x['exact_match']and x['dense_global_calls']==3 for x in result),name)
            canonical=json.dumps(result,sort_keys=True,separators=(',',':')).encode()
            results[name]={'semantic_sha256':hashlib.sha256(canonical).hexdigest(),
                           'source_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),
                           'result':result}
    out={'status':'PASS_PR1673_INDEPENDENT_SCHEDULE_AND_MIXED_RECURRENCE_CONTROLS',
         'external_review_repository':pins['repository'],'external_review_commit':pins['commit'],
         'checks':results,'scope':'Original PR1673 cost regime and exact finite '
                 'supporting schedule models. External five-factor examples also '
                 'test a denser union; no other PR outer result is imported. '
                 'Written proof and retained all-size interfaces are separate.'}
    (P/'CONTROL-REPLAY.json').write_text(json.dumps(out,indent=2)+'\n')
    print(out['status'],len(results),'fresh independent controls')


if __name__=='__main__':main()
