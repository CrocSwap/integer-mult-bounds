#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay the PR2853 vacancy relay, independent owner/moment audits and exact caps.

This finite check is separate from reproduce.py's complete conditional admission.
Marius-Paul Dumitrean, with substantial OpenAI Codex assistance.
"""
import argparse,gzip,hashlib,json,os,subprocess,sys,tempfile,types
from pathlib import Path
from fractions import Fraction as Q
from decimal import Decimal,localcontext
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'gmx-t74-borrow43-handoff'
PREDECESSOR=HERE.parent/'t248-dirtentry-residue'

def need(ok,message):
    if not ok:raise ValueError(message)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    data=path.read_bytes()
    return json.loads(gzip.decompress(data)if path.suffix=='.gz'else data)

def dec(value):
    with localcontext()as context:
        context.prec=45
        return str(Decimal(value.numerator)/Decimal(value.denominator))

def authenticate():
    before={}
    for row in read(HERE/'SOURCES.json')['files']:
        if row['usage']=='input':
            path=HERE.parents[1]/row['path']
            need(sha(path)==row['sha256'],'source drift: '+row['path'])
            before[path]=row['sha256']
    candidate=read(HERE/'data/CANDIDATE.json')
    need(candidate['source_head']==candidate['comparison_head']=='d01045dfb67428679618027dff552f1d032fa999','exact P53 heads')
    need(candidate['comparison_claim_sha256']==sha(SOURCE/'outer/OUTER-CLAIM.json')=='eb3260be191774b931cff6e562978a2af27bbc6ff666ca8c1d387a2b18dc86fa','full exact comparator')
    need(set(candidate['candidate_sha256'])=={'ORDER.json','FILL.json.gz','DISPATCH.json','PROFILE.json'},'four frozen payloads')
    for name,pin in candidate['candidate_sha256'].items():
        path=HERE/'data'/name;need(sha(path)==pin,'candidate drift: '+name);before[path]=pin
    before[HERE/'data/CANDIDATE.json']=sha(HERE/'data/CANDIDATE.json')
    return candidate,before

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path);a=ap.parse_args()
    if a.out:need(not a.out.exists()and not a.out.resolve().is_relative_to(HERE),'fresh external receipt required')
    need(not sys.flags.optimize,'retained word algebra requires assertions')
    candidate,before=authenticate();T=candidate['replicas'];need(T==74,'frozen relay has74 replicas')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1');env.pop('PYTHONOPTIMIZE',None)
    with tempfile.TemporaryDirectory(prefix='aphase-relay-')as temporary:
        work=Path(temporary)
        def run(script,*args):
            result=subprocess.run([sys.executable,'-I','-B',str(HERE/script),*map(str,args)],cwd=work,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=300)
            if result.returncode:raise RuntimeError(script+' failed\n'+result.stdout+'\n'+result.stderr)
            return result.stdout
        derivation=json.loads(run('check_derivation.py'))
        need(len(derivation['controls'])==5,'source adapter rejection controls')
        run('generate.py','--source',SOURCE,'--out',work/'generated')
        for name in candidate['candidate_sha256']:
            need(read(work/'generated'/name)==read(HERE/'data'/name),'deterministic mathematical payload '+name)
        run('build_adapter.py','--predecessor',PREDECESSOR,'--source',SOURCE,'--out',work/'adapter')
        for name in ['admit_aphase_residue.py','prepare_aphase_native.py']:
            need((work/'adapter'/name).read_bytes()==(HERE/name).read_bytes(),'exact admission executable '+name)
        run('build_wrapper.py','--basis',HERE/'derivation/H23-reproduce.py','--out',work/'reproduce.py')
        need((work/'reproduce.py').read_bytes()==(HERE/'reproduce.py').read_bytes(),'exact hardened wrapper derivation')
        owner=work/'OWNERS.json';moment=work/'MOMENT.json'
        run('independent/owners.py','--replicas',T,'--order',HERE/'data/ORDER.json','--fill',HERE/'data/FILL.json.gz','--dispatch',HERE/'data/DISPATCH.json','--profile',HERE/'data/PROFILE.json','--out',owner)
        run('independent/moment.py','--owner-receipt',owner,'--out',moment)
        o,m=read(owner),read(moment)
        need(len(o['controls'])==7 and len(m['controls'])==5,'complete independent control sets')
        profile={int(k):v for k,v in read(HERE/'data/PROFILE.json').items()};baseline={int(k):v for k,v in read(SOURCE/'new/PROFILE.json').items()}
        delta={k:profile.get(k,0)-baseline.get(k,0)for k in set(profile)|set(baseline)}
        need({k:v for k,v in delta.items()if v}=={7:-2,14:1},'complete paid relay delta')
        need(o['rank_mass']==4816512 and o['physical']==66794,'unchanged mass and fully charged stock')
        target=Q(m['proposed_outer_target']);previous=Q(read(SOURCE/'outer/OUTER-CLAIM.json')['kappa_rational'])
        need(target==Q(candidate['target'])and Q(m['complex_lower'])==Q(candidate['complex_lower']),'independently regenerated target')
        run('packing/verify_cap.py','--out',work/'CAP.json');cap=read(work/'CAP.json');cl,cu=map(Q,cap['root_bracket'])
        need(previous<target<cl<cu,'strict comparison below exact continuous cap')
        path=HERE/'packing/inputs/ceiling.py'
        need(sha(path)=='86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc','local-word engine source pin')
        engine=types.ModuleType('credited_local_word_ceiling');exec(compile(path.read_bytes(),str(path),'exec'),engine.__dict__)
        local={1:2402,2:638,3:266,4:128,5:26,8:8};ll,lu=engine.ceiling(local,73,896,9,64)
        need(ll==Q('0.001758353980844')and lu==Q('0.001758353980845')and target<ll,'actual local-word cap')
        report={'status':'PASS_P53_RELAY_FINITE_REPLAY_AND_EXACT_CAP','replicas':T,'roles':o['roles'],'physical':o['physical'],'rank_mass':o['rank_mass'],'profile':profile,'profile_delta':{7:-2,14:1},'complex_lower':m['complex_lower'],'complex_upper':m['complex_upper'],'target':str(target),'target_decimal':dec(target),'gain_over_full_PR2853':str(target-previous),'gain_decimal':dec(target-previous),'relative_gain_percent':dec(100*(target-previous)/previous),'fixed_bin_cap':[str(cl),str(cu)],'fraction_of_remaining_cap_gain':[str((target-previous)/(cu-previous)),str((target-previous)/(cl-previous))],'fraction_of_fixed_bin_cap':[str(target/cu),str(target/cl)],'remaining_fixed_bin_cap_gap':[str(cl-target),str(cu-target)],'local_word_ceiling':[str(ll),str(lu)],'fraction_of_local_word_ceiling':str(target/lu),'controls':{'owners':7,'moment':5,'source_adapter':5},'scope':'Finite literal owner/profile/arithmetic checks and continuous upper bounds. Complete native/global/outer admission is a separate command. All-size obligations remain inherited.'}
        need(before=={path:sha(path)for path in before},'input drift')
        if a.out:
            a.out.parent.mkdir(parents=True,exist_ok=True)
            with a.out.open('x',encoding='utf8')as stream:stream.write(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print(json.dumps({key:report[key]for key in ['status','replicas','roles','target_decimal','gain_decimal','relative_gain_percent','controls']},sort_keys=True))

if __name__=='__main__':main()
