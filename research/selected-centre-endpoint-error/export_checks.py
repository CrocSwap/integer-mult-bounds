"""Git-free replay and source/output/typed-receipt failure boundaries."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def need(ok,why):
    if not ok: raise ValueError(why)


def invoke(script,*args,ok=True,contains=''):
    result = subprocess.run([sys.executable,'-I','-O','-B',str(script),*map(str,args)],
                            capture_output=True,text=True,encoding='utf-8',timeout=500)
    need((result.returncode == 0) == ok,'unexpected exit: '+result.stdout+result.stderr)
    need(contains in result.stdout+result.stderr,'wrong failure boundary: '+result.stdout+result.stderr)


def hashes(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}


def main():
    with tempfile.TemporaryDirectory(prefix='centre-endpoint-') as folder:
        root = Path(folder); package = root/'research'/P.name
        shutil.copytree(P,package)
        for item in json.loads((P/'SOURCES.json').read_text(encoding='utf-8'))['files']:
            dest = root/item['path'];dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes((ROOT/item['path']).read_bytes())
        program = package/'endpoint.py'
        before = hashes(root)
        invoke(program)
        need(hashes(root) == before,'default Git-free replay changed files')
        receipt = package/'RESULT.json'; original = receipt.read_bytes()
        invoke(program,'--out',receipt,ok=False,contains='FileExistsError')
        need(receipt.read_bytes() == original,'existing receipt overwritten')
        wrong = json.loads(original)
        wrong['calls'][0][0] = False  # bool compares equal to the original int 0
        receipt.write_text(json.dumps(wrong),encoding='utf-8')
        invoke(program,ok=False,contains='typed receipt mismatch')
        receipt.write_bytes(original)
        vendor = package/'vendor/pr2199_verify.py'
        vendor.write_bytes(b'raise RuntimeError("UNAUTHENTICATED_VENDOR_EXECUTED")\n'+vendor.read_bytes())
        invoke(program,ok=False,contains='source SHA-256:')
        need(not (root/'.git').exists(),'unexpected Git checkout')
    print('PASS_CENTRE_ENDPOINT_EXPORT: Git-free unchanged replay, typed receipt, source-before-import, output refusal')


if __name__ == '__main__': main()
