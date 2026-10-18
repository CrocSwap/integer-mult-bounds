#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Export pinned sources, construct T740, and run the complete composition.

Fresh retained bootstrap is the default. --retained reuses a source-authenticated
predecessor cache; both current providers are still rebuilt and checked fresh.
New integration: Jeremy Diviney with OpenAI Codex assistance. Exact predecessor
recipes and Petalas's allocation materializer remain unchanged.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path,PurePosixPath
import subprocess
import sys
import tarfile
import types

P=Path(__file__).resolve().parent
WORD_HEAD='84cc406ad91ec53fff329a11a445d7effe564a77'
WORD_PREFIX='research/rank7-restore-carrier-skips'
PACK_HEAD='78e77d820393c6b8648b47af219e991edfcc54e6'
PACK_PREFIX='research/rank7-t740-release'
BASE='d8e0f83f00191df62174b641e9fff055c357f641'

def need(ok,why):
    if not ok:raise ValueError(why)
def load(path,name):
    m=types.ModuleType(name);m.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def export(repo,head,prefix,out):
    raw=subprocess.run(['git','-C',str(repo),'archive',head,prefix],capture_output=True,check=True,timeout=90).stdout
    need(len(raw)<20_000_000,'bounded source archive');out.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
        members=tar.getmembers();need(len(members)<500,'bounded source inventory')
        for entry in members:
            name=PurePosixPath(entry.name)
            need(not name.is_absolute() and '..' not in name.parts,'safe source path')
            need(entry.isdir() or entry.isfile(),'regular source entry')
            if entry.isdir():continue
            need(name.is_relative_to(PurePosixPath(prefix)),'source prefix')
            target=out/name.relative_to(PurePosixPath(prefix));target.parent.mkdir(parents=True,exist_ok=True)
            stream=tar.extractfile(entry);need(stream is not None,'source stream')
            with stream:target.write_bytes(stream.read())
    return {p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file()}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ['repo','work']:ap.add_argument('--'+key,type=Path,required=True)
    ap.add_argument('--retained',type=Path);ap.add_argument('--jobs',type=int,choices=(1,2),default=1);ap.add_argument('--dry-run',action='store_true')
    a=ap.parse_args();repo=a.repo.resolve();work=a.work.resolve()
    need(__debug__,'inherited validators require assertions')
    need(not work.exists() and not work.is_relative_to(P) and not P.is_relative_to(work),'fresh external replay directory')
    work.mkdir(parents=True);source=work/'pr3042';packroot=work/'packing-source';pack=packroot/PACK_PREFIX
    inventories={'pr3042':export(repo,WORD_HEAD,WORD_PREFIX,source),'pr3030':export(repo,PACK_HEAD,PACK_PREFIX,pack)}
    pins=json.loads((pack/'PINS.json').read_bytes());need(len(pins)<=100,'source pin bound')
    for relative,expected in pins.items():
        path=PurePosixPath(relative);need(not path.is_absolute() and '..' not in path.parts,'safe dependency path')
        target=packroot/path
        if not target.exists():
            need(path.is_relative_to(PurePosixPath('research/rank7-joint-endframes')),'pinned main dependency')
            raw=subprocess.run(['git','-C',str(repo),'show',BASE+':'+relative],capture_output=True,check=True,timeout=30).stdout
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        need(sha(target)==expected,'exact predecessor input '+relative)
    (work/'EXPORTS.json').write_text(json.dumps(inventories,indent=2,sort_keys=True)+'\n')
    engine=load(P/'run_release.py','composition_engine');engine.authenticate(source)
    materialize=load(pack/'materialize.py','pinned_materialize3030')
    allocation=work/'allocation';allocation.mkdir();built=materialize.build(allocation)
    (allocation/'MATERIALIZED.json').write_text(json.dumps(built,indent=2,sort_keys=True)+'\n')
    run=work/'run';cmd=[sys.executable,'-B',str(source/'reproduce.py'),'--repo',str(repo),'--work',str(run),'--jobs',str(a.jobs),'--dry-run']
    if a.retained:cmd+=['--retained',str(a.retained.resolve())]
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    env.pop('PYTHONOPTIMIZE',None);env.pop('PYTHONPATH',None)
    subprocess.run(cmd,check=True,env=env,timeout=120)
    recipe=json.loads((run/'PREFLIGHT.json').read_bytes())['commands']
    engine.adapt(recipe,source,allocation)
    if a.dry_run:
        print('PASS_EXACT_EXPORTS_MATERIALIZATION_RECIPE_ONLY_NOT_A_RELEASE');return
    engine.execute(run,source,allocation,work/'evidence')

if __name__=='__main__':main()
