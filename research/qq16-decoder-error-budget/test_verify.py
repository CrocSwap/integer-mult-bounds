#!/usr/bin/env python3
"""Entrypoint, source-integrity and underestimated-budget failure controls."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise ValueError(why)


def digest_tree(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def run(root, expected_error=None):
    result = subprocess.run([sys.executable, '-I', '-O', '-B', str(root/'verify.py')],
                            cwd=root.parent, capture_output=True, text=True, timeout=30)
    if expected_error:
        need(result.returncode != 0 and expected_error in result.stderr,
             'expected rejection: ' + expected_error)
    else:
        need(result.returncode == 0 and 'PASS_QQ16_DECODER_ERROR_BUDGET' in result.stdout,
             'copied-directory positive replay: ' + result.stderr)


def main():
    with tempfile.TemporaryDirectory(prefix='qq16-error-controls-') as temporary:
        root = Path(temporary)/'package'
        shutil.copytree(HERE, root)
        before = digest_tree(root)
        run(root)
        need(before == digest_tree(root), 'default replay is read-only')
        manifest = json.loads((root/'SNAPSHOTS.json').read_text())
        for entry in manifest['files']:
            path = root/entry['path']
            raw = path.read_bytes()
            path.write_bytes(raw+b'\n')
            run(root, 'source SHA256')
            path.write_bytes(raw)
        receipt = root/'RESULT.json'
        raw = receipt.read_bytes()
        data = json.loads(raw)
        data['word_events'] = True
        receipt.write_text(json.dumps(data))
        run(root, 'committed result mismatch')
        receipt.write_bytes(raw)
        receipt.rename(root/'saved-result.json')
        run(root, 'FileNotFoundError')
        (root/'saved-result.json').rename(receipt)
        need(before == digest_tree(root), 'controls preserve the copied positive fixture')
    # Change each advertised output coefficient. The full-word enclosure must
    # reject the reduced budget at an actual prefix, not only at a receipt diff.
    spec = importlib.util.spec_from_file_location('error_budget_under_test', HERE/'verify.py')
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    word = verifier.authenticated_word()
    original = dict(verifier.OWNED)
    for key in original:
        verifier.OWNED = dict(original)
        verifier.OWNED[key] -= 1
        try:
            verifier.forward(word)
        except ValueError as exc:
            need('error envelope at' in str(exc), 'underbound rejected at a real field')
        else:
            raise ValueError('underclaimed error channel accepted')
    verifier.OWNED = original
    # A declared stage rank must not accept JSON booleans as integers.
    bad = json.loads(json.dumps(word))
    next(e for e in bad if e['op'] == 'stage')['rank'] = True
    try:
        verifier.forward(bad)
    except ValueError as exc:
        need('rank-eight child' in str(exc), 'rank type rejected')
    else:
        raise ValueError('boolean child rank accepted')
    print('PASS_QQ16_ERROR_FAILURE_CONTROLS source_mutations=4 budget_underclaims=4 entrypoint_controls=3')


if __name__ == '__main__':
    main()
