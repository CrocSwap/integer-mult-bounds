#!/usr/bin/env python3
"""Optimized read-only export; independent CLI and disk-corruption controls."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    with tempfile.TemporaryDirectory(prefix='fanout-cut-export-') as temp:
        root = Path(temp)
        package = root/'research'/HERE.name
        shutil.copytree(HERE,package,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        for name in json.loads((HERE/'VERIFY.json').read_bytes())['inputs']:
            to = root/name
            to.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/name,to)
        def run(script,*args):
            return subprocess.run([sys.executable,'-O','-B',str(package/script),*map(str,args)],
                                  cwd=root,capture_output=True,text=True,timeout=240)
        files = [p for p in root.rglob('*') if p.is_file()]
        dirs = sorted([p for p in root.rglob('*') if p.is_dir()],key=lambda p:len(p.parts),reverse=True)
        for p in files:
            p.chmod(0o444)
        for p in (*dirs,root):
            p.chmod(0o555)
        try:
            completed = run('verify.py')
        finally:
            for p in (root,*reversed(dirs)):
                p.chmod(0o755)
            for p in files:
                p.chmod(0o644)
        need(completed.returncode == 0 and 'PASS_DIRTY_FANOUT_CUT_SYNTHESIS' in completed.stdout,
             'optimized read-only Git-free replay: '+completed.stderr)
        # Generate a real CLI certificate, then remove the compiler completely.
        tariffs = package/'examples/chain.json'
        generated = run('synthesize.py',tariffs)
        need(generated.returncode == 0,'compiler CLI: '+generated.stderr)
        cert = package/'cli-certificate.json'
        cert.write_text(generated.stdout)
        compiler = package/'synthesize.py'
        compiler.rename(package/'compiler-unavailable.txt')
        checked = run('check.py',tariffs,cert)
        need(checked.returncode == 0 and 'PASS_DIRTY_FANOUT_CUT_CERTIFICATE' in checked.stdout,
             'independent CLI without compiler: '+checked.stderr)
        changed = json.loads(generated.stdout)
        changed['word'].pop()
        cert.write_text(json.dumps(changed))
        rejected = run('check.py',tariffs,cert)
        need(rejected.returncode != 0 and 'arbitrary-dirt endpoint' in rejected.stderr,
             'disk word corruption rejected')
        (package/'compiler-unavailable.txt').rename(compiler)
        receipt = package/'RESULT.json'
        raw = receipt.read_bytes()
        changed = json.loads(raw)
        changed['controls']['nonlaminar_certificate'] = 1
        receipt.write_text(json.dumps(changed))
        rejected = run('verify.py','--suite','controls')
        need(rejected.returncode != 0 and 'complete typed receipt' in rejected.stderr,
             'typed receipt corruption rejected')
        receipt.write_bytes(raw)
        source = root/'research/dirty-anchor-tradeoff/PROOF.md'
        raw = source.read_bytes()
        source.write_bytes(raw+b'\nchanged\n')
        rejected = run('verify.py','--suite','controls')
        need(rejected.returncode != 0 and 'live source SHA256' in rejected.stderr,
             'live source drift rejected')
        source.write_bytes(raw)
        certificates = package/'CERTIFICATES.json'
        raw = certificates.read_bytes()
        changed = json.loads(raw)
        changed['chain']['cost'] = '6'
        certificates.write_text(json.dumps(changed))
        # Only this single certificate is needed to detect its corruption.
        cert.write_text(json.dumps(changed['chain']))
        rejected = run('check.py',tariffs,cert)
        need(rejected.returncode != 0 and 'primal dual equality' in rejected.stderr,
             'certificate cost corruption rejected')
        certificates.write_bytes(raw)
        bad_input = package/'duplicate-tariffs.json'
        bad_input.write_text('{"mu":[1],"mu":[2],"add":[[null]]}')
        rejected = run('synthesize.py',bad_input)
        need(rejected.returncode != 0 and 'duplicate JSON key' in rejected.stderr,
             'duplicate input key rejected')
    print('PASS_DIRTY_FANOUT_CUT_EXPORT_CONTROLS')


if __name__ == '__main__':
    main()
