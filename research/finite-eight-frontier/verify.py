"""Fresh original ten-stage replay followed by the arithmetic-only refinement.
Apache-2.0; substantial OpenAI Codex assistance. See NOTICE.md and PROOF.md.
"""
import argparse,hashlib,json,os,subprocess,sys,traceback
from pathlib import Path

HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'five-stage-gen5-collective-kernels'
STAGES=sorted(('virtual','raw','bit','kernel','scalar','primes','banks','complex','math','finite'))

def need(ok,why):
    if not ok:raise ValueError(why)

def pin(p):
    b=p.read_bytes();return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}

def inventory(d):
    out={}
    for p in sorted(d.rglob('*')):
        need(not p.is_symlink(),'symlink in package')
        if p.is_file():out[p.relative_to(d).as_posix()]=pin(p)
    return out

def bind(config):
    need(inventory(BASE)==config['baseline_files'],'exact original136 input closure')
    for name,expected in config['implementation_files'].items():need(pin(HERE/'implementation'/name)==expected,'refinement source changed '+name)
    for name,expected in config['publication_files'].items():need(pin(HERE/name)==expected,'publication source changed '+name)
    for name,blob in config['baseline_git_blobs'].items():
        b=(BASE/name).read_bytes();need(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==blob,'original Git blob '+name)

def typed(a,b):
    if type(a) is not type(b):return False
    if type(a) is dict:return a.keys()==b.keys() and all(typed(a[k],b[k]) for k in a)
    if type(a) is list:return len(a)==len(b) and all(typed(x,y) for x,y in zip(a,b))
    return a==b

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    sys.set_int_max_str_digits(100000)
    config=json.loads((HERE/'SOURCE_BINDING.json').read_bytes());bind(config)
    output=a.output.resolve();need(not output.exists(),'fresh output required')
    need(not output.is_relative_to(HERE) and not output.is_relative_to(BASE),'output outside both packages')
    output.mkdir(parents=True)
    environment={k:v for k,v in os.environ.items() if not k.upper().startswith('PYTHON')}
    commands=[];completed=[]
    try:
        baseline=output/'baseline'
        cmd=[sys.executable,'-E','-X','utf8','-B',str(HERE/'original_shim.py'),'--output',str(baseline)]
        commands.append(cmd);subprocess.run(cmd,env=environment,check=True);completed.append('original-ten-stages')
        original=json.loads((baseline/'verification.json').read_bytes())
        need(original['status']=='PASS_IMMUTABLE_GEN5_KERNEL_ENTRIES_FIVE_STAGE_BANKED_CONSTRUCTION' and original['fresh_stages']==STAGES and original['inputs_unchanged'] is True,'actual complete original replay')
        need(original['manifest_sha256']==config['baseline_files']['MANIFEST.json']['sha256'] and original['files']==135,'original literal manifest binding')
        need(original['kappa']=='186178624839407/250000000000000000','original exact kappa')
        need(original['negative_controls']==['omitted '+s+' stage' for s in STAGES],'original ten omission controls')
        need(len(json.loads((baseline/'scalar.json').read_bytes())['controls'])==11 and len(json.loads((baseline/'primes.json').read_bytes())['controls'])==6,'original scalar/prime controls')
        kernel=json.loads((baseline/'kernel.json').read_bytes())
        need(len(kernel['scalar']['controls'])==2 and all(row['wrong_rows']>0 for row in kernel['scalar']['controls']),'original kernel setup/restore omission controls')
        input_pins=inventory(baseline)
        (output/'baseline-artifacts.json').write_text(json.dumps(input_pins,sort_keys=True,indent=2)+'\n',encoding='utf-8')
        results=[]
        for label,flags in (('normal',[]),('optimized',['-OO'])):
            target=output/(label+'-result.json')
            cmd=[sys.executable,'-E',*flags,'-X','utf8','-B',str(HERE/'refinement_shim.py'),'--baseline',str(baseline),'--pins',str(output/'baseline-artifacts.json'),'--out',str(target)]
            commands.append(cmd);subprocess.run(cmd,env=environment,check=True);completed.append(label)
            results.append(json.loads(target.read_bytes()))
        need(typed(*results),'normal/OO typed equality')
        need(len(results[0]['controls'])==config['refinement_control_count'],'complete refinement controls')
        need(inventory(baseline)==input_pins,'original artifacts changed during refinement');bind(config)
        certificate={'schema':'pr290-eight-level-arithmetic-refinement-public-v001','original_head':config['original_head'],'original_source_manifest':config['baseline_files']['MANIFEST.json'],'frozen_arithmetic_source':config['frozen_arithmetic_source'],'construction_changed':False,'normal_optimized_typed_equal':True,'mathematics':results[0],'inherited_allsize_assumptions':config['inherited_allsize_assumptions']}
        (output/'certificate.json').write_text(json.dumps(certificate,sort_keys=True,indent=2)+'\n',encoding='utf-8')
        report={'status':'PASS_ORIGINAL_TEN_STAGES_AND_EIGHT_LEVEL_ARITHMETIC','original_head':config['original_head'],'kappa':results[0]['kappa'],'baseline_artifacts':input_pins,'source_binding':pin(HERE/'SOURCE_BINDING.json'),'commands':commands,'completed':completed,'original_stages':STAGES,'normal_optimized_typed_equal':True,'allsize_proved':False}
        (output/'verification.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'status':report['status'],'kappa':report['kappa']}),flush=True)
    except BaseException as exc:
        (output/'failure.json').write_text(json.dumps({'error':str(exc),'completed':completed,'commands':commands,'traceback':traceback.format_exc()},indent=2)+'\n',encoding='utf-8')
        raise

if __name__=='__main__':main()
