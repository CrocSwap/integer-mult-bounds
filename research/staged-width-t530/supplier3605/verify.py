"""Portable replay of the exact staged-helper local construction.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
No optimizer, Git, network or retained run receipt is required. Native children
run without optimization and use a fresh private bytecode-cache namespace.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse, copy, gzip, hashlib, json, os, subprocess, sys, tempfile, time, types
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OLD=ROOT/'research/rank7-coupled-586-588-carrier-fold'
NATIVE=ROOT/'research/t74-native-fast/vendor/native/new/code/borrow'
def require(value,message):
    if not value:raise ValueError(message)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):
    data=path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix=='.gz' else data)
def module(path,name):
    # Execute authenticated source, never preexisting bytecode.
    result=types.ModuleType(name);result.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),result.__dict__)
    return result
def authenticate():
    for row in read(HERE/'SOURCES.json')['files']:
        if row['usage']=='input':require(sha(ROOT/row['path'])==row['sha256'],'input pin: '+row['path'])
    for name,digest in read(HERE/'ARTIFACTS.json').items():
        require(sha(HERE/name)==digest,'artifact pin: '+name)
def endpoint(word,audit,dual=False):
    """Complete dirty-input operator for actual semantic defect controls.

    The pinned inherited free-algebra primitive interpreter is used; this
    driver constructs the literal sequence and checks every private row.
    """
    live=sorted(set(range(704))-set(word['removed']));restored=set(map(int,word['helper_final']))
    rows={r:{(r,()):Q(1)} for r in live};rows.update({r+704:{} for r in restored})
    program=[['corr',c['target'],c['source'],tuple(c['operator_word']),Q(c['coefficient'])] for c in word['initial_corrections']]
    program+=word['precondition']+word['compensation']+word['A']+word['cut'];warps={}
    for op,rec in enumerate(word['warps'],1):warps.setdefault(rec[0],[]).append(['warp',rec[1],op])
    for i in range(len(word['B'])+1):
        program+=warps.get(i,[])
        if i<len(word['B']):program.append(word['B'][i])
    program+=word['restore']+word['cleanup']
    for gate in program:audit.walg_apply(gate,rows,dual,10**6)
    expected={r:{(r,()):Q(1)} for r in live}
    for t in range(112):expected[t if dual else 112+t][(112+t if dual else t,())]=Q(-1 if dual else 1)
    return [r for r in live if rows[r]!=expected[r]],[r for r in restored if rows[r+704]]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--provider',choices=('base','extra'),required=True);args=ap.parse_args()
    started=time.monotonic();authenticate()
    producer=module(HERE/'staged_pair.py','declared_staged_pair')
    audit=module(OLD/'vendor/audit_local.py','pinned_independent_auditor')
    tag=args.provider;parent=read(OLD/f'edits/FINAL-WORD-{tag}.json.gz')
    record=read(HERE/f'STAGED-PAIR-RECORD-{tag}.json.gz');word_path=HERE/f'STAGED644-660-{tag}.json.gz';word=read(word_path)
    require(producer.apply(parent,record)==word,'complete canonical reconstruction')
    require(sha(word_path)==record['target_compressed_sha256'],'immutable word byte pin')
    # Generated-container equality is semantic; compression streams may differ.
    controls=[]
    for label,change in (
        ('wrong release coefficient',lambda r:r['B_inserted'][0]['gates'][0].__setitem__(3,1)),
        ('wrong scalar preimage',lambda r:r['B_deleted'][0]['old'].__setitem__(3,19))):
        wrong=copy.deepcopy(record);change(wrong);rejected=False
        try:producer.apply(parent,wrong)
        except ValueError:rejected=True
        require(rejected,'accepted record defect: '+label);controls.append(label)
    with tempfile.TemporaryDirectory(prefix='staged-pair-replay-') as temporary:
        scratch=Path(temporary);env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None);stages=[]
        def run(name,path,*argv):
            began=time.monotonic()
            command=[sys.executable,'-B','-X','pycache_prefix='+str(scratch/('cache-'+name)),str(path),*map(str,argv)]
            result=subprocess.run(command,capture_output=True,env=env,timeout=300)
            if result.returncode:sys.stderr.buffer.write(result.stdout+result.stderr)
            require(result.returncode==0,'stage failed: '+name)
            stages.append({'stage':name,'seconds':time.monotonic()-began,'source_sha256':sha(path)})
            print('PASS_STAGE',tag,name,flush=True);return result.stdout
        scope=json.loads(run('independent-prefix-invoice',HERE/'check_scope.py',tag))
        require(scope['status']=='PASS_ROOT_SOURCE_PATCH_PREFIX_AND_FRAME_INVOICE','scope result')
        run('independent-whole-word',OLD/'vendor/audit_local.py','--word',word_path,'--output',scratch/'word-audit.json')
        audit_result=read(scratch/'word-audit.json')
        require(audit_result['independent_inputs']==632 and audit_result['zero_buffers']==91,'complete dirty/private domain')
        require(audit_result['orientations']=={'forward':'PASS','dual':'PASS'},'both orientations')
        require(endpoint(word,audit)==([],[]),'control interpreter positive fixture')
        for helper,donor in ((644,640),(660,656)):
            index=next(i for i,gate in enumerate(word['B']) if gate[:3]==['add',donor,helper])
            for kind in ('omit','flip'):
                wrong=copy.deepcopy(word)
                if kind=='omit':
                    wrong['B'].pop(index)
                    for warp in wrong['warps']:
                        if warp[0]>index:warp[0]-=1
                else:wrong['B'][index][3]*=-1
                wrong['cleanup']=producer.cleanup(wrong);bad,buffers=endpoint(wrong,audit)
                require(any(112<=r<224 for r in bad),'semantic target defect was not rejected')
                require(not buffers,'control must retain literal clean-buffer restoration')
                controls.append({'helper':helper,'defect':kind,'bad_targets':[r for r in bad if 112<=r<224]})
        out=scratch/'native'
        run('transport',NATIVE/'bw_transport.py',word_path,out)
        run('residual-adapters',NATIVE/'bw_adapters.py',out/'CANONICAL-WORD.json.gz',out/'RESIDUAL-ADAPTERS.json',out/'LEMMA-A.json')
        for name in ('bw_emit.py','bw_audit_local.py','bw_phases.py','bw_check_recipes.py'):run(name,NATIVE/name,out)
        residual=json.loads(run('changed-width-phase-controls',HERE/'check_residual.py',NATIVE))
        require(residual['status']=='PASS_EXACT_PAIRED_ENTRANCE_FULL_WIDTH7_RESIDUAL','residual controls');authenticate()
        print(json.dumps({'status':'PASS_STAGED_PAIR_LOCAL_CONSTRUCTION','provider':tag,'word_sha256':sha(word_path),
            'local_profile':word['report']['local_profile'],'inventory':word['report']['width_inventory'],
            'independent_inputs':632,'private_buffers':91,'orientations':['forward','dual'],
            'controls':controls+residual['controls'],'stages':stages,'elapsed_seconds':time.monotonic()-started,
            'scope':'Finite exact local word, frame invoice and full native chain; no owner allocation or kappa claim.'},sort_keys=True))
if __name__=='__main__':main()
