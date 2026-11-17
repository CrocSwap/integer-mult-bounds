#!/usr/bin/env python3
"""Portable path/custody adapter for the original strict-74 reviewer."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
REVIEW_SHA = '8590fbfa198eec5499a55606943110c612dd372f64f92436cefe1cea609dd5dd'
EXACT_SHA = '966f98673b8b3e41f16ec54819ce7c230b16bede9446d686fed474ef00399fb2'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if len(sys.argv) != 3 or sys.argv[1] != '--output':
        raise SystemExit('usage: replay.py --output NEW_FILE')
    output = Path(sys.argv[2])
    if output.exists():
        raise ValueError('output already exists')
    if digest(HERE / 'review.py') != REVIEW_SHA or digest(HERE / 'exact.py') != EXACT_SHA:
        raise ValueError('original independent reviewer pin')
    spec = importlib.util.spec_from_file_location('package_verify', PACKAGE / 'verify.py')
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    with tempfile.TemporaryDirectory(prefix='p104-independent-review-') as temporary:
        root = Path(temporary)
        port = root / 'port74'
        port.mkdir()
        verifier.extract_source(port)
        for name in ('build_candidate.py', 'combined.py'):
            shutil.copyfile(PACKAGE / 'src' / name, port / name)
            subprocess.run([sys.executable, '-I', '-B', str(port / name)], check=True)
        review = root / 'review'
        review.mkdir()
        for name in ('review.py', 'exact.py'):
            shutil.copyfile(HERE / name, review / name)
        source = port / 'source7644'
        inputs = [review / 'review.py', review / 'exact.py', source / 'data' / 'word.json.gz',
                  source / 'data' / 'peer7611.json', source / 'data' / 'invoice.json',
                  source / 'independent.py', port / 'candidate.json.gz', port / 'candidate-invoice.json']
        freeze = {'files': [{'path': str(path), 'sha256': digest(path)} for path in inputs]}
        freeze_path = review / 'FREEZE.json'
        freeze_path.write_text(json.dumps(freeze, sort_keys=True) + '\n')
        loader = ('import runpy,sys; d=sys.argv[1]; f=sys.argv[2]; '
                  'sys.path.insert(0,d); sys.argv=[d+"/review.py","--execute","--freeze-sha256",f]; '
                  'runpy.run_path(sys.argv[0],run_name="__main__")')
        subprocess.run([sys.executable, '-I', '-B', '-c', loader, str(review), digest(freeze_path)],
                       check=True, timeout=610)
        result = (review / 'RESULT.json').read_bytes()
        parsed = json.loads(result)
        if parsed.get('status') != 'PASS_INDEPENDENT_STRICT74' or parsed.get('candidate_word') != verifier.CANDIDATE_SHA:
            raise ValueError('independent review did not pass on this candidate')
        with output.open('xb') as stream:
            stream.write(result)
    print('PASS_PORTABLE_INDEPENDENT_REVIEW', verifier.CANDIDATE_SHA)


if __name__ == '__main__':
    main()
