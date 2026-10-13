#!/usr/bin/env python3
"""Replay the joint-basis experiments against their pinned source words.

No baseline, native or phase admission is silently substituted by this search
replay. Prepared with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
SOURCE_MANIFEST='dd602912d0e60c9bb2befba446629ae531ea42a9d4fecda922f98aac40762c41'
PINS={
 'research/larger-gain/providers/width7/eight/FULL-WORD.json.gz':'6f99cffd73076a768d39c21bf97ced42b6a5d3228b1dcef79d6f072dd35c0ee5',
 'research/larger-gain/providers/coupled_frames_base.py':'b6033cd2959297a624b557f3d04665c8fbb680a4c0987daf0704ef93711700bd',
 'research/larger-gain/providers/search_suffix_kernels.py':'0523c90f036ff01cac9299fe4e47dc40dd04f264f09415985d2c98b4da43371c',
 'research/larger-gain/providers/promote_cold_frames.py':'631a85e47a02f48773f6c6ffde7903fa6a91f9bc30c5a500b3c66c36470a2a66',
 'research/structural-gain/frontier-composition/combined-eight-word/FULL-WORD.json.gz':'ee0fecf86bddcc5f4e675c60fbd5c572bd48269368a37a38c070346eefa3dd4a',
 'research/structural-gain/frontier-composition/combined-prefix-word/FULL-WORD.json.gz':'a6cd88224427bad6d00b6fbe1d201a2c09e496c90e2cecdc04d7f2ff11a4ba42'}


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def content_sha(p):return hashlib.sha256(gzip.decompress(p.read_bytes())).hexdigest()
def read(p):return json.loads(p.read_text())
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def require(ok,message):
    if not ok:raise ValueError(message)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-package',type=Path,required=True,help='Frozen PR564 complex-allcold package')
    ap.add_argument('--promoted-word',type=Path,required=True,help='Replayed PR558 promoted raw word')
    ap.add_argument('--optimizer-python',type=Path,default=Path(sys.executable),help='Python with numpy/scipy')
    ap.add_argument('--work',type=Path,required=True)
    a=ap.parse_args();require(__debug__,'Assertions required')
    source=a.source_package.resolve();work=a.work.resolve()
    require(not work.exists()and not work.is_relative_to(HERE),'Use a fresh external output directory')
    require(sha(source/'MANIFEST.json')==SOURCE_MANIFEST,'Wrong PR564 package')
    inventory={p.relative_to(source).as_posix():sha(p)for p in source.rglob('*')if p.is_file()
               and p!=source/'MANIFEST.json'and '__pycache__'not in p.parts}
    require(inventory==read(source/'MANIFEST.json'),'Source package inventory mismatch')
    for name,digest in PINS.items():require(sha(REPO/name)==digest,'Pinned input mismatch: '+name)
    recipe=read(source/'data/EIGHT-COLD.json')
    require(content_sha(a.promoted_word)==recipe['input_content_sha256'],'Wrong promoted scalar word')
    work.mkdir(parents=True);(work/'logs').mkdir()
    static=source/'vendor/pr558/vendor/pr552/complex-local/static44'
    selection=work/'SELECTION.json';dump(selection,read(static/'RECIPE.json')['selection'])
    search=REPO/'research/larger-gain/providers';gk=static/'gk'
    old=REPO/'research/larger-gain/providers/width7/eight/FULL-WORD.json.gz'
    combined=REPO/'research/structural-gain/frontier-composition/combined-eight-word/FULL-WORD.json.gz'
    prefix=REPO/'research/structural-gain/frontier-composition/combined-prefix-word/FULL-WORD.json.gz'
    steps=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None)
    def run(name,script,*args,optimizer=False):
        script=HERE/script;python=a.optimizer_python if optimizer else sys.executable
        cmd=[str(python),'-B',str(script),*map(str,args)];log=work/'logs'/(name+'.log')
        print('RUN',name,flush=True);start=time.monotonic()
        with log.open('w')as stream:proc=subprocess.run(cmd,stdout=stream,stderr=subprocess.STDOUT,env=env)
        require(proc.returncode==0,name+' failed\n'+log.read_text()[-4000:])
        steps.append(dict(name=name,command=cmd,script_sha256=sha(script),exit_code=proc.returncode,
                          seconds=time.monotonic()-start,log_sha256=sha(log)))
        dump(work/'STAGES.json',steps);print('PASS',name,flush=True)
    common=['--gk-dir',gk,'--search-code',search]
    for raised in (False,True):
        name='prefix-raised-screen'if raised else'prefix-screen'
        extra=['--raise-frames']if raised else[]
        run(name,'search_prefix_bases.py','--word',old,'--selection',selection,*common,*extra,'--out',work/name)
        target='prefix-raised-optimal-disjoint'if raised else'prefix-optimal-disjoint'
        run(target,'optimize_prefix_components.py','--screen',work/name,'--gk-dir',gk,'--out',work/target,optimizer=True)
    run('multicut-rank2-raised','search_multicut.py','--word',combined,*common,'--rank',2,
        '--raise-frames','--out',work/'multicut-rank2-raised')
    run('suffix-unlocked','unlock_suffix_kernels.py','--word',combined,'--original',a.promoted_word,
        '--gk-dir',gk,'--out',work/'suffix-unlocked')
    unlocked=work/'suffix-unlocked/FULL-WORD.json.gz'
    run('multicut-unlocked-rank2','search_multicut.py','--word',unlocked,*common,'--rank',2,
        '--raise-frames','--out',work/'multicut-unlocked-rank2')
    run('multicut-shared-compositions','compose_multicut_choices.py','--base',unlocked,'--rank1-word',combined,
        '--rank2-screen',work/'multicut-unlocked-rank2/SEARCH.json',*common,'--out',work/'multicut-shared-compositions')
    run('shared-gauges','search_shared_gauges.py','--word',prefix,*common,'--out',work/'shared-gauges')
    run('joint-gauge-bases','search_joint_gauge_bases.py','--word',combined,'--selection',selection,
        *common,'--out',work/'joint-gauge-bases')
    checks={}
    for stage in steps:
        name=stage['name'];folder=work/name;reference=HERE/name
        paths=sorted(folder.rglob('FULL-WORD.json.gz'))
        for path in paths:
            relative=path.relative_to(folder)
            require(content_sha(path)==content_sha(reference/relative),'Retained word differs: '+name+'/'+str(relative))
        if(folder/'SEARCH.json').exists():
            result,retained=read(folder/'SEARCH.json'),read(reference/'SEARCH.json')
            require(result['counts']==retained['counts'],'Search counts differ: '+name)
            for key in ('components','candidates'):
                # Old fixed-prefix receipts predate the explicit empty change list.
                def normalize(rows):return[{k:v for k,v in row.items()if k!='frame_changes'or v}for row in rows]
                require(normalize(result.get(key,[]))==normalize(retained.get(key,[])),
                        'Exact search results differ: '+name+'/'+key)
        checks[name]=dict(literal_words_reproduced=len(paths),exact_search_results_equal=True)
    result=dict(status='PASS_JOINT_BASIS_RESEARCH_REPLAY',stages=len(steps),checks=checks,
                source_head='f1db606a1416359229f944946667338305208064',source_manifest_sha256=SOURCE_MANIFEST,
                scope='Exact finite research replay and retained literal-word equality. '
                      'No new native/phase/global claim; frontier-composition owns admission.')
    dump(work/'RESULT.json',result)
    artifacts={p.relative_to(work).as_posix():sha(p)for p in work.rglob('*')if p.is_file()}
    dump(work/'RECEIPT.json',dict(status=result['status'],steps=steps,artifacts=artifacts,
         input_pins=PINS,code_sha256={p.name:sha(p)for p in HERE.glob('*.py')},
         source_manifest_sha256=SOURCE_MANIFEST,promoted_word_sha256=sha(a.promoted_word)))
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
