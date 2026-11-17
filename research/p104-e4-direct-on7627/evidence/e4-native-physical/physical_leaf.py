# SPDX-License-Identifier: Apache-2.0
"""Guarded finite replay adapter for authenticated #7627 retained leaves.

No top-level execution. Call only inside the independently reviewed one-run
controller after GO, using paths yielded by the authenticated source loader.
"""
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

SOURCE = 'b80b6e74bff87c8d8160c5e121dac7c68df0827a7061847b896075417a346238'
CANDIDATE = '1ea66c263faa51da704d7aae944f3371400afaf5df8a56904ab96319f6554e0e'
ORIGINAL = 'cca66a7ec924bab47ccd1410968d16e071a01dc6110b5c08040bd207f753d066'
PINS = {'verify_host3_odd.py':'e75ad2096ba2587d1dc9c8982b2c2eb7c6fd2636a80adcd943314ef2cf6fd258',
        'physical.py':'4e995d1158033d83bf69b671f23dc7924d66edbbe07623ba063ba7421234ea20',
        'physical_child.py':'b61be680bb100bb514dd7320117e5de0d04e95d07f450d17633e374b5711bc2e'}
def need(condition, message):
    if not condition: raise ValueError(message)
def sha(data): return hashlib.sha256(data).hexdigest()
def canonical(word): return json.dumps(word,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
def checked(path, digest):
    path=Path(path)
    need(path.is_file() and not path.is_symlink(),'missing or symlinked input: '+str(path))
    data=path.read_bytes(); need(sha(data)==digest,'input digest mismatch: '+str(path)); return data

def run(vendor, rank9, word, odd_scale, run_dir, *, authorization, caller_sha256, expected_route_charge):
    """Run source OR candidate once in a fresh directory under reviewed controller.

    `vendor`, `rank9` originate from authenticated source.sources(); `word` is
    the authenticated literal object, `odd_scale` is freshly derived. Caller
    hash and expected charge must be freshly bound by the parent price engine.
    Logs and marker are exclusive; the controller owns resource/time/custody.
    """
    need(authorization=='INDEPENDENT_GO','independent GO required')
    need(__debug__,'assertions required')
    digest=sha(canonical(word)); need(digest in (SOURCE,CANDIDATE),'literal word identity')
    need(type(odd_scale) is int and odd_scale>0,'invalid derived odd scale')
    need(type(expected_route_charge) is int and expected_route_charge>0,'route charge required')
    vendor,rank9,run_dir=map(Path,(vendor,rank9,run_dir))
    paths={'host':vendor/'frozen/verify_host3_odd.py','physical':vendor/'frozen/physical.py',
           'rank9':rank9/'physical_child.py'}
    raw={k:checked(p,PINS[p.name]) for k,p in paths.items()}
    caller=rank9/'dyadic/CALLER.json'; caller_raw=checked(caller,caller_sha256)
    # Remaining files belong to the loader-authenticated archive closure.
    cliff=vendor/'frozen/clifford_exact.py'; incumbent=vendor/'data/caller.json'
    dependency={str(p.name):sha(p.read_bytes()) for p in (cliff,incumbent,rank9/'signed_child.py')}
    need(run_dir.is_dir() and not run_dir.is_symlink(),'fresh existing run directory required')
    marker=run_dir/'STARTED'; fd=os.open(marker,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    with os.fdopen(fd,'w') as f: f.write(digest+'\n')
    word_path=run_dir/'word.json.gz'
    with word_path.open('xb') as f: f.write(gzip.compress(canonical(word),mtime=0))
    edits=raw['rank9'].decode(); need(edits.count(ORIGINAL)==1,'rank9 identity anchor')
    adapted=edits.replace(ORIGINAL,digest)
    # Isolated interpreter prevents module cache contamination across invocations.
    wrapper='''import sys,types\nfrom pathlib import Path\nsys.path.insert(0,sys.argv[1])\np=Path(sys.argv[2]); s=p.read_text(); old=sys.argv[3]; new=sys.argv[4]\nassert s.count(old)==1\nm=types.ModuleType("e4_signed_physical"); m.__file__=str(p)\nexec(compile(s.replace(old,new),str(p),"exec"),m.__dict__)\nm.main(Path(sys.argv[5]),Path(sys.argv[6]),Path(sys.argv[7]))\n'''
    logs={}
    def invoke(name, args):
        path=run_dir/(name+'.log')
        with path.open('xb') as f:
            p=subprocess.run([sys.executable,'-I','-B',*map(str,args)],stdout=f,stderr=subprocess.STDOUT,check=False)
        data=path.read_bytes(); logs[name]={'sha256':sha(data),'bytes':len(data),'returncode':p.returncode}
        need(p.returncode==0,name+' failed; see retained log')
        return data.decode()
    host=invoke('verify_host3_odd',[paths['host'],word_path,odd_scale])
    need('PASS_HOST3 decoupled ports' in host,'host pass marker missing')
    physical=invoke('physical',[paths['physical'],word_path,cliff,1000000009,11])
    need('PASS_PHYSICAL ' in physical,'physical pass marker missing')
    mutant=invoke('physical_wrong_alpha2',[paths['physical'],word_path,cliff,1000000009,11,'mutate'])
    need('rows bad' in mutant,'physical wrong sign control missing output')
    routes=invoke('rank9_physical_child',['-c',wrapper,rank9,paths['rank9'],ORIGINAL,digest,word_path,incumbent,caller])
    result=json.loads(routes)
    need(result['status']=='PASS_PHYSICAL_RANK9_ALGEBRA' and result['word_sha']==digest and result['paid_calls']==32,'signed physical route identity')
    need(result['proposed_sha']==sha(caller_raw),'signed physical caller identity')
    charge=1000*sum(len(row['caller_fields'])*row['ordinary_elementary_units'] for row in result['bindings'])
    need(charge==expected_route_charge,'signed route charge mismatch')
    return {'schema':'e4-finite-physical-leaf/v1','status':'PASS_FINITE_PHYSICAL_ONLY',
            'word_canonical_sha256':digest,'word_gzip_sha256':sha(word_path.read_bytes()),'odd_scale':odd_scale,
            'prime':1000000009,'seed':11,'wrong_alpha2_rejected':True,'signed_routes':result,
            'route_charge':charge,'source_sha256':{k:sha(v) for k,v in raw.items()},
            'dependencies_sha256':dependency,'caller_sha256':sha(caller_raw),
            'rank9_adaptation':{'before':ORIGINAL,'after':digest,'occurrences':1,'adapted_sha256':sha(adapted.encode())},
            'logs':logs,'limitations':['Finite field replay is a sampled physical check; not a complete native, certificate, price, or 17-stage signed caller qualification.']}
