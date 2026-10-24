"""Replay the exact upstream verifier with scratch files inside this package."""
from pathlib import Path
from hashlib import sha256, sha1
import json, os, platform, subprocess, sys, time
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent

def need(ok, why):
    if not ok:
        raise ValueError(why)

def source_check():
    pins = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    for p in pins['files']:
        b = (HERE / p['local']).read_bytes()
        need(len(b) == p['bytes'] and sha256(b).hexdigest() == p['sha256'], 'Source SHA drift: ' + p['local'])
        need(sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest() == p['git_blob'], 'Source Git blob drift: ' + p['local'])
    actual = {p.relative_to(HERE).as_posix() for p in (HERE / 'upstream').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    need(actual == {p['local'] for p in pins['files']}, 'Upstream file set drift')
    return pins

def main():
    pins = source_check()
    scratch = HERE / '.scratch'
    scratch.mkdir(exist_ok=True)
    env = dict(os.environ, TMP=str(scratch), TEMP=str(scratch), TMPDIR=str(scratch), PYTHONUTF8='1')
    argv = [sys.executable, '-I', '-O', '-B', str(HERE / 'upstream' / 'verify.py')]
    start = time.perf_counter()
    run = subprocess.run(argv, cwd=HERE / 'upstream', env=env, capture_output=True, timeout=2100)
    (HERE / 'REPLAY.stdout.log').write_bytes(run.stdout)
    (HERE / 'REPLAY.stderr.log').write_bytes(run.stderr)
    result = dict(status='PASS' if run.returncode == 0 else 'FAIL', command=argv, returncode=run.returncode, elapsed_seconds=time.perf_counter()-start, python=sys.version, platform=platform.platform(), head=pins['head'], sources_sha256=sha256((HERE/'SOURCES.json').read_bytes()).hexdigest(), runner_sha256=sha256(Path(__file__).read_bytes()).hexdigest(), stdout_sha256=sha256(run.stdout).hexdigest(), stderr_sha256=sha256(run.stderr).hexdigest())
    if run.returncode == 0:
        result['upstream'] = json.loads(run.stdout)
        need(result['upstream']['status'] == 'PASS_COMPLETE_NATIVE_DUAL_SUPPLIERS_NO_NEW_KAPPA', 'Unexpected verifier status')
    source_check()
    (HERE / 'REPLAY.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    need(run.returncode == 0, run.stderr.decode('utf-8', errors='replace')[-6000:])
    print('PASS_INDEPENDENT_EXACT_HEAD_REPLAY', pins['head'])

if __name__ == '__main__':
    main()
