"""Run the H6 export gate without rewriting the checked-out CI evidence."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SELECTED_RECORD = 'certificates/selected-result.json'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export_sources(root, pins, contents):
    """Keep the historical price benchmark separate from today's selected record.

    All ordinary inherited files must still match their pins in the checkout.
    Only the moving selected record is read from its recorded Git object; its
    exact bytes must match the original SHA256 before entering the export.
    The workflow checks the current selected record independently afterwards.
    """
    need(SELECTED_RECORD in pins and SELECTED_RECORD in contents,
         'CI requires the historical selected-record pin and current record')
    exported = dict(contents)
    for name, pin in pins.items():
        data = (subprocess.check_output(['git', 'show', pin['commit']+':'+name], cwd=root)
                if name == SELECTED_RECORD else contents[name])
        need(hashlib.sha256(data).hexdigest() == pin['sha256'],
             'CI inherited input binding: '+name)
        exported[name] = data
    return exported


def main():
    pins = json.loads((HERE/'gate/PINS.json').read_text())['files']
    names = set(pins)
    names.update(str(path.relative_to(ROOT)) for path in HERE.rglob('*') if path.is_file()
                 and '__pycache__' not in path.parts)
    contents = {name: (ROOT/name).read_bytes() for name in names}
    before = {name: hashlib.sha256(data).hexdigest() for name, data in contents.items()}
    exported = export_sources(ROOT, pins, contents)
    gitdir = subprocess.check_output(['git', 'rev-parse', '--absolute-git-dir'],
                                     cwd=ROOT, text=True).strip()
    with tempfile.TemporaryDirectory(prefix='h6-ci-') as directory:
        export = Path(directory)/'source-tree'
        unrelated = Path(directory)/'unrelated-cwd'
        unrelated.mkdir()
        for name in sorted(names):
            destination = export/name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(exported[name])
        environment = dict(os.environ, GIT_DIR=gitdir, GIT_WORK_TREE=str(export))
        gate = export/'research/h6-compensation-network/gate/replay.py'
        subprocess.run([sys.executable, '-I', '-O', '-B', str(gate)], cwd=unrelated,
                       env=environment, check=True)
        receipt = json.loads(gate.with_name('RESULT.json').read_text())
        need(receipt['status'] == 'PASS_SUCCESSOR_FRESH_EXPORT_AND_MUTATION_GATES',
             'CI must execute the complete fresh-export gate')
        need(all(digest(ROOT/name) == value for name, value in before.items()),
             'CI replay rewrote checked-out source/evidence')
        print(json.dumps(dict(status='PASS_H6_CI_REPLAY_CHECKOUT_UNCHANGED',
            inherited_files=receipt['inherited_pinned_files'],
            scripts=len(receipt['audit_script_sha256']),
            specifications=len(receipt['specification_sha256']),
            gate_checks=receipt['checks'],
            semantic_corruption_controls=len(receipt['semantic_negative_controls']),
            historical_benchmark=dict(path=SELECTED_RECORD, **pins[SELECTED_RECORD]),
            checkout_selected_sha256=before[SELECTED_RECORD],
            scope='Scoped successor replay with retained exhaustive predecessor evidence; no all-size or hosted-admission claim.'),
            sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
