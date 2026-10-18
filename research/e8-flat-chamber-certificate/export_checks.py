"""Portable fail-closed and Git-free replay controls; writes only a temp tree."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def need(ok,message):
    if not ok:
        raise ValueError(message)


def call(script,*args,ok=True,contains=None):
    run = subprocess.run([sys.executable,'-I','-O','-B',str(script),*map(str,args)],
                         capture_output=True,text=True,encoding='utf-8',timeout=90)
    need((run.returncode == 0) == ok,'exit status: '+run.stdout+run.stderr)
    if contains:
        need(contains in run.stdout+run.stderr,'expected failure boundary: '+run.stdout+run.stderr)


def hashes(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def main():
    with tempfile.TemporaryDirectory(prefix='e8-flat-export-') as temporary:
        target = Path(temporary)
        package = target/'research'/P.name
        shutil.copytree(P,package)
        for row in json.loads((P/'SOURCES.json').read_text(encoding='utf-8'))['files']:
            dst = target/row['path']
            dst.parent.mkdir(parents=True,exist_ok=True)
            dst.write_bytes((ROOT/row['path']).read_bytes())
        checker = package/'check_certificate.py'
        before = hashes(target)
        call(checker)
        need(before == hashes(target),'Git-free default replay changed files')
        regenerated = target/'new-certificate.json'
        call(package/'build_certificate.py','--out',regenerated)
        need(json.loads(regenerated.read_text()) == json.loads((package/'certificate.json').read_text()),
             'producer regeneration differs')
        call(checker,'--certificate',regenerated)
        saved = regenerated.read_bytes()
        call(package/'build_certificate.py','--out',regenerated,ok=False,contains='FileExistsError')
        need(regenerated.read_bytes() == saved,'producer overwrote existing file')
        saved_receipt = (package/'RESULT.json').read_bytes()
        call(checker,'--out',package/'RESULT.json',ok=False,contains='FileExistsError')
        need((package/'RESULT.json').read_bytes() == saved_receipt,'checker overwrote existing receipt')
        receipt = json.loads(saved_receipt)
        receipt['zero_normal_control']['reflections'] = False
        (package/'RESULT.json').write_text(json.dumps(receipt),encoding='utf-8')
        call(checker,ok=False,contains='committed receipt replay')
        (package/'RESULT.json').write_bytes(saved_receipt)
        source = target/'research/complex-frame-pair-decoders/verify.py'
        original = source.read_bytes()
        # A changed function would execute a visible failing body if AST
        # evaluation ran before authentication. The pin error must win.
        source.write_bytes(original+b'\ndef e8_roots():\n    raise RuntimeError("UNAUTHENTICATED_AST_EXECUTED")\n')
        call(checker,ok=False,contains='source SHA-256:')
        source.write_bytes(original)
        need(not (target/'.git').exists(),'export unexpectedly has Git state')
    print('PASS_E8_FLAT_EXPORT_CONTROLS: Git-free read-only, regeneration, two output refusals, typed receipt, source-before-AST')


if __name__ == '__main__':
    main()
