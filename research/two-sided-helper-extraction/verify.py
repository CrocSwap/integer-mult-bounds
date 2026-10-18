#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay the local construction; optional full native replay. No global kappa claim."""
import argparse,copy,gzip,hashlib,json,os,subprocess,sys,types
from pathlib import Path
P=Path(__file__).resolve().parent

def need(ok,reason):
    if not ok:raise RuntimeError(reason)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if b[:2]==b'\x1f\x8b' else b)
def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def word(p,x):p.write_bytes(gzip.compress(json.dumps(x,separators=(',',':')).encode(),mtime=0))
def load(name,p):
    m=types.ModuleType(name);m.__file__=str(p);sys.modules[name]=m
    exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--native',action='store_true');a=ap.parse_args()
    need(not sys.flags.optimize,'assertions enabled')
    out=a.work.resolve();need(not out.exists() and not out.is_relative_to(P) and not P.is_relative_to(out),'fresh external output');out.mkdir(parents=True)
    pins=read(P/'PINS.json');actual={f.relative_to(P).as_posix():sha(f) for d in ('vendor','data') for f in (P/d).rglob('*') if f.is_file()}
    need(actual==pins,'exact complete vendor/data bytes')
    pm=load('preload_move',P/'vendor/preload_move.py');gen=load('channel_extract',P/'extract.py');aud=load('independent_channel_audit',P/'vendor/audit_local.py')
    structure=load('channel_structure',P/'structure.py')
    transform=read(P/'data/TRANSFORM.json');rows={}
    for tag in ('base','extra'):
        parent=read(P/f'data/PARENT-{tag}.json.gz');got=gen.apply(parent,transform);expected=read(P/f'data/WORD-{tag}.json.gz')
        need(got==expected,'complete literal reconstruction '+tag)
        aud.run(P/f'data/PARENT-{tag}.json.gz',out/f'PARENT-AUDIT-{tag}.json')
        aud.run(P/f'data/WORD-{tag}.json.gz',out/f'AUDIT-{tag}.json')
        receipt=read(out/f'AUDIT-{tag}.json')
        need(receipt['independent_inputs']==632 and receipt['restored_cold']==receipt['zero_buffers']==73,'charged 73 private buffers')
        need(receipt['local_profile']==gen.PROFILE and receipt['width_inventory']==gen.INVENTORY,'independently derived profile/inventory')
        rows[tag]={'parent_sha256':sha(P/f'data/PARENT-{tag}.json.gz'),'word_sha256':sha(P/f'data/WORD-{tag}.json.gz'),'audit':receipt,'structure':structure.check(parent,transform,aud)}
    def bad_scale(w):
        g=next(g for g in w['A'][w['prelude_events']:] if g[:2]==['scale',408]);g[2]=1
    def bad_output(w):w['restore'][-1][3]=-1
    def bad_comp(w):w['compensation']=copy.deepcopy(read(P/'data/PARENT-base.json.gz')['compensation'])
    def bad_buffer(w):w['cleanup']=[['add',g[1]-704 if g[1]==1112 else g[1],g[2]-704 if g[2]==1112 else g[2],*g[3:]] if g[0]=='add' else g for g in w['cleanup']]
    rejected={}
    for name,change,regen in [('wrong_input_scale',bad_scale,True),('wrong_output_cancellation',bad_output,True),('stale_compensation',bad_comp,False),('omit_new_private_buffer',bad_buffer,False)]:
        w=copy.deepcopy(read(P/'data/WORD-base.json.gz'));change(w)
        need(w!=read(P/'data/WORD-base.json.gz'),'nontrivial mutant')
        if regen:
            profile,inventory=pm.frame_report(w);w['report']['local_profile']=profile;w['report']['width_inventory']=inventory
            z=copy.deepcopy(w);z['A']=z['A'][z['prelude_events']:];w['cleanup']=pm.derive_cleanup(z,set(map(int,z['helper_final'])))
        f=out/(name+'.json.gz');word(f,w)
        try:aud.run(f,out/(name+'.json'))
        except (AssertionError,RuntimeError,ValueError) as e:rejected[name]=str(e)
        else:raise RuntimeError('semantic mutant accepted: '+name)
    native={}
    if a.native:
        for tag in ('base','extra'):
            dest=out/('native-'+tag);cmd=[sys.executable,'-X','pycache_prefix='+str(out/'bytecode'),'-B',str(P/'vendor/fastnative/run_native.py'),str(P/f'data/WORD-{tag}.json.gz'),str(dest),'--engine','sparse']
            env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1');env.pop('PYTHONOPTIMIZE',None)
            with (out/('NATIVE-'+tag+'.log')).open('w') as log:subprocess.run(cmd,check=True,env=env,stdout=log,stderr=subprocess.STDOUT)
            native[tag]=read(dest/'RESULT.json');need(native[tag]['status']=='PASS_COMPLETE_T74_NATIVE_REPLAY' and native[tag]['word_sha256']==rows[tag]['word_sha256'],'native result binding')
    need(actual=={f.relative_to(P).as_posix():sha(f) for d in ('vendor','data') for f in (P/d).rglob('*') if f.is_file()},'source bytes unchanged')
    result={'status':'PASS_TWO_SIDED_HELPER408_LOCAL_CONSTRUCTION','scope':'Exact local construction only; no owner allocation or higher kappa admitted. Extra private buffer is mandatory.','providers':rows,'semantic_controls':rejected,'native':native,'native_replayed':a.native}
    save(out/'RESULT.json',result);print(result['status'],json.dumps(rejected),flush=True)
if __name__=='__main__':main()
