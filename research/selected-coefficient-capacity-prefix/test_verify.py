"""Explicit source, resource-contract and receipt defects; active under -O."""
import json
from pathlib import Path
import shutil
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from runtime import ROOT, authenticate, load, require
from verify import compare, run


def rejects(function, message):
    try:
        function()
    except RuntimeError as error:
        require(message in str(error), 'intended defect detected: '+str(error))
    else:
        raise RuntimeError('defect was accepted: '+message)


def main():
    m = load()
    control = run(m, {'branch':'child-unit'})
    require(control['extension_peak'] == 11, 'literal half witness')
    rejects(lambda:run(m, {'branch':'child-unit'}, extension_bound=10), 'half extension needs eleven')
    # A success-only meter would not inspect a zero request rejected by its own quota.
    # Our probe observes the would-be slot before calling the source guard.
    fail = run(m, {'branch':'child-good'}, (0,-1))
    require(fail['rejected']['demand'] == 22, 'first rejected index allocation observed')
    rejects(lambda:run(m, {'branch':'child-unit'}, budgets=(20494,20)), 'pending request exceeds')
    original_extend = m.children.extend
    raw = (ROOT/'vendor/children.py').read_text()
    require(raw.count('    index.free(f)\n') == 1, 'unique source defect site')
    mutated = raw.replace('    index.free(f)\n', '    pass  # deliberate retained-index defect\n')
    try:
        exec(compile(mutated, str(ROOT/'vendor/children.py'), 'exec', dont_inherit=True), m.children.__dict__)
        rejects(lambda:run(m, {'branch':'child-good'}), 'pending request exceeds')
    finally:
        m.children.extend = original_extend
    with tempfile.TemporaryDirectory(prefix='coefficient-prefix-control-') as temporary:
        root = Path(temporary)/'package'
        shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('__pycache__'))
        # Only the disposable control copy becomes writable; preserve the source export.
        for copy in root.rglob('*'):
            copy.chmod(0o755 if copy.is_dir() else 0o644)
        root.chmod(0o755)
        target = root/'vendor/words.py'
        target.write_bytes(target.read_bytes()+b'\n# changed scientific source\n')
        rejects(lambda:authenticate(root), 'input SHA256')
        target.write_bytes((ROOT/'vendor/words.py').read_bytes())
        manifest = json.loads((root/'INPUTS.json').read_text())
        manifest['files'].pop()
        (root/'INPUTS.json').write_text(json.dumps(manifest))
        rejects(lambda:authenticate(root), 'complete source inventory')
    rejects(lambda:compare({'peak':11}, {'peak':10}), 'complete typed receipt')
    rejects(lambda:compare({'peak':1}, {'peak':True}), 'complete typed receipt')
    print('PASS_CAPACITY_PREFIX_CONTROLS groups=8 half_understatement retained_f source_pin inventory receipt no_new_kappa')


if __name__ == '__main__':
    main()
