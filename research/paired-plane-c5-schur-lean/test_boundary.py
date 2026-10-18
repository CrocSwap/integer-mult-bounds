#!/usr/bin/env python3
"""Git-free source/evidence binding probes; these do not rerun Lean."""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REL = HERE.relative_to(ROOT)
INPUTS = ['research/community-frontier1094-audit/selected-replay.tar.gz',
          'research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json']


def need(ok, message):
    if not ok:
        raise ValueError(message)


def hashes(root):
    return {str(p.relative_to(root)): sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def run(root, success, reason='', extra=()):
    p = subprocess.run([sys.executable, '-I', '-O', '-B', str(root/REL/'verify.py'), *map(str, extra)],
                       cwd=root, text=True, capture_output=True, timeout=45)
    need((p.returncode == 0) == success and reason in p.stdout+p.stderr, 'unexpected result: '+p.stdout+p.stderr)


def main():
    with tempfile.TemporaryDirectory(prefix='paired-c5-export-') as tmp:
        root = Path(tmp)
        shutil.copytree(HERE, root/REL, ignore=shutil.ignore_patterns('__pycache__'))
        for name in INPUTS:
            (root/name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/name, root/name)
        before = hashes(root)
        run(root, True)
        need(hashes(root) == before, 'default replay changed export')
        for name, reason in [(str(REL/'Schur.lean'), 'Lean receipt source binding'),
                             (INPUTS[1], 'source hash mismatch')]:
            path = root/name
            saved = path.read_bytes()
            path.write_bytes(saved+b' ')
            run(root, False, reason)
            path.write_bytes(saved)
        receipt = root/REL/'RESULT.json'
        saved = receipt.read_bytes()
        data = json.loads(saved)
        data['identity_block_scalar_dimension'] = 46
        receipt.write_text(json.dumps(data))
        run(root, False, 'complete receipt mismatch')
        receipt.write_bytes(saved)
        formal = root/REL/'LEAN-CHECK.json'
        saved_formal = formal.read_bytes()
        data = json.loads(saved_formal)
        data['theorem_axioms']['no_four_pivot'].append('sorryAx')
        formal.write_text(json.dumps(data))
        run(root, False, 'recorded formal inventory')
        formal.unlink()
        run(root, False, 'LEAN-CHECK.json')
        formal.write_bytes(saved_formal)
        out = root/'new.json'
        run(root, True, extra=('--out', out))
        need(json.loads(out.read_text()) == json.loads(saved), 'regeneration drift')
        run(root, False, 'FileExistsError', extra=('--out', out))
        out.unlink()
        need(hashes(root) == before, 'boundary probes failed to restore export')
    print('PASS_PAIRED_C5_BOUNDARY git_free_unchanged=1 changed_source_and_receipts=5 exclusive_output=1')


if __name__ == '__main__':
    main()
