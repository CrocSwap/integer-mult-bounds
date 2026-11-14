# SPDX-License-Identifier: Apache-2.0
"""Cold source authentication and required stateless #7544 review stages."""
import argparse, hashlib, io, json, os, signal, subprocess, sys, tarfile, tempfile, time
from pathlib import Path

HERE=Path(__file__).resolve().parent
CAPS={'native':480,'signed':495,'audit':225}


def require(ok,message):
    if not ok:raise ValueError(message)


def read(path):
    def unique(pairs):
        result=dict(pairs);require(len(result)==len(pairs),'Duplicate JSON key');return result
    return json.loads(path.read_bytes(),object_pairs_hook=unique)


def digest(b):return hashlib.sha256(b).hexdigest()


def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()


def authenticate():
    for name,h in read(HERE/'INTEGRITY.json').items():
        path=HERE/name
        require(path.resolve().is_relative_to(HERE) and not path.is_symlink(),'Contained regular file')
        require(digest(path.read_bytes())==h,'Changed package file '+name)
    commands=read(HERE/'VERIFY.json')['commands']
    require([c['argv'][-1] for c in commands]==list(CAPS),'All three stages required in order')
    require([c['timeout_seconds'] for c in commands]==list(CAPS.values()),'Whole-command caps')
    for row in read(HERE/'ORACLES.json'):
        b=(HERE/row['vendored_path']).read_bytes()
        require(digest(b)==row['sha256'],'Exact oracle source')
        require(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['git_blob'],'Oracle blob identity')


def unpack(destination):
    m=read(HERE/'SOURCE-MAP.json');blob=(HERE/m['archive']).read_bytes()
    require(m['head']=='d6be7d620c9c8337104daeb09fe01196eced5fe3','Reviewed head')
    require(digest(blob)==m['archive_sha256'],'Pinned source archive')
    entries={r['path']:r for r in m['files']}
    require(len(entries)==len(m['files'])==74,'Complete source inventory')
    with tarfile.open(fileobj=io.BytesIO(blob),mode='r:gz') as tar:
        members=tar.getmembers()
        require(len(members)==len(entries) and {x.name for x in members}==entries.keys(),'Exact source member set')
        for member in members:
            require(member.isfile() and member.name in entries,'Regular declared source member')
            row=entries[member.name];path=destination/member.name
            require(path.resolve().is_relative_to(destination),'Source containment')
            require(member.size==row['size']<=40*1024**2,'Source size pin')
            b=tar.extractfile(member).read();require(digest(b)==row['sha256'],'Source byte pin')
            require(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['git_blob'],'Git blob identity')
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b)
    return destination


def binding(src):
    native=read(src/'expected/NATIVE.json');native.pop('timings')
    names=['expected/NATIVE.json','expected/SIGNED.json','expected/FINAL.json','PINS.json',
           'engines/native.py','engines/signed.py','engines/adapt_native.py','engines/adapt_signed.py','engines/check_final.py']
    return dict(source_head=read(HERE/'SOURCE-MAP.json')['head'],
                archive_sha256=read(HERE/'SOURCE-MAP.json')['archive_sha256'],
                candidate_canonical_sha256=read(src/'expected/FINAL.json')['candidate_canonical_sha256'],
                caller_sha256=digest((src/'bench/inputs/7113-CALLER.json').read_bytes()),
                native_mathematical_sha256=digest(canonical(native)),
                frozen_files={name:digest((src/name).read_bytes()) for name in names})


def contained(argv,env,remaining):
    """Own and clean the complete child group on success, failure or TERM."""
    child=None
    def terminate(signum,frame):
        if child is not None:
            try:os.killpg(child.pid,signal.SIGKILL)
            except ProcessLookupError:pass
        raise SystemExit(128+signum)
    previous={s:signal.signal(s,terminate) for s in (signal.SIGTERM,signal.SIGINT)}
    try:
        child=subprocess.Popen(argv,env=env,start_new_session=True)
        code=child.wait(timeout=remaining)
        require(code==0,'Required stage failed with exit '+str(code))
    finally:
        if child is not None:
            try:os.killpg(child.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            child.wait()
        for s,h in previous.items():signal.signal(s,h)


def main():
    started=time.monotonic()
    require(__debug__ and sys.version_info[:2]==(3,12),'Unoptimized Python3.12 required')
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=tuple(CAPS),required=True);a=p.parse_args()
    authenticate();env=dict(os.environ);env.pop('PYTHONOPTIMIZE',None)
    with tempfile.TemporaryDirectory(prefix='independent7544-review-') as temp:
        root=Path(temp).resolve();src=unpack(root/'source');out=root/'review'
        common=binding(src);cache=root/'bytecode';env['PYTHONPYCACHEPREFIX']=str(cache)
        if a.stage=='audit':
            argv=[sys.executable,'-I','-B','-X','pycache_prefix='+str(cache),str(HERE/'review.py'),str(src),'--out',str(out)]
        else:
            argv=[sys.executable,'-I','-B','-X','pycache_prefix='+str(cache),str(HERE/'staged_source.py'),str(src),str(root/'work'),'--stage',a.stage]
        remaining=CAPS[a.stage]-(time.monotonic()-started)-1
        require(remaining>0,'Preparation exhausted whole-command cap')
        contained(argv,env,remaining)
        if a.stage=='audit':
            require(read(out/'REVIEW.json')==read(HERE/'expected/REVIEW.json'),'Fresh independent review receipt')
            report=dict(stage='audit',fresh_review_sha256=digest((out/'REVIEW.json').read_bytes()))
        else:
            report=read(root/'work/REPLAY-STAGE.json')
            field='fresh_native_math_sha256' if a.stage=='native' else 'consumed_native_math_sha256'
            require(report[field]==common['native_mathematical_sha256'],'Required native mathematical dependency join')
            if a.stage=='signed':
                require(report['consumed_native_sha256']==common['frozen_files']['expected/NATIVE.json'],
                        'Signed consumes exact authenticated frozen receipt')
        report.update(binding=common,binding_sha256=digest(canonical(common)))
        print('REVIEW7544_STAGE_RECEIPT',json.dumps(report,sort_keys=True),flush=True)
    authenticate()
    print('PASS_COLD_REVIEW7544_'+a.stage.upper(),'whole_command_seconds',time.monotonic()-started,flush=True)


if __name__=='__main__':main()
