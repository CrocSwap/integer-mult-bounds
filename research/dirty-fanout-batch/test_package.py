"""Check standalone replay and deliberate source/result/program/cost faults."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

P = Path(__file__).resolve().parent


def run(root, expected_success):
    result = subprocess.run([sys.executable, '-I', '-O', '-B', str(root/'verify.py')],
                            cwd=root.parent, text=True, capture_output=True)
    if (result.returncode == 0) != expected_success:
        raise RuntimeError(result.stdout+result.stderr)
    if expected_success and 'PASS_DIRTY_FANOUT_BATCH' not in result.stdout:
        raise RuntimeError('missing successful outcome')


with tempfile.TemporaryDirectory(prefix='dirty fanout relocation ') as temp:
    root = Path(temp)/'package with spaces'
    shutil.copytree(P,root,ignore=shutil.ignore_patterns('__pycache__'))
    run(root,True)
    mutations = [
        ('source pin', 'sources/DIRTY-PROOF.md', lambda s:s+'\nchanged\n'),
        ('certificate count', 'CERTIFICATE.json', lambda s:s.replace('"leaf_calls": 246','"leaf_calls": 245',1)),
        ('missing restoration', 'batch.py', lambda s:s.replace('return right + left + inverse(right) + inverse(left), dirt', 'return right + left + inverse(left), dirt')),
        ('wrong inverse order', 'batch.py', lambda s:s.replace('in reversed(word)', 'in word')),
        ('unpaid head return', 'batch.py', lambda s:s.replace('moves += head', 'moves += 0')),
        ('unpaid child', 'batch.py', lambda s:s.replace('leaf_calls=len(word),', 'leaf_calls=len(word)-1,')),
    ]
    for name,path,change in mutations:
        file=root/path
        original=file.read_text()
        altered=change(original)
        if altered == original:
            raise RuntimeError('control did not change '+name)
        file.write_text(altered)
        run(root,False)
        file.write_text(original)
        print('REJECT',name)
print('PASS_PACKAGE: relocated optimized replay and six corruption controls')
