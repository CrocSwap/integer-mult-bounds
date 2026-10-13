"""Adversarial mathematical and immutable-package checks. Apache-2.0."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('sink_independent', HERE / 'independent.py')
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)
source = check.source


def rejects(action, name):
    try:
        action()
    except ValueError:
        return
    raise RuntimeError('negative control accepted: ' + name)


def main():
    source.checked_sources()
    certificate = json.loads((HERE / 'CERTIFICATE.json').read_text(encoding='utf-8'))
    check.audit(certificate)
    changes = []
    c = copy.deepcopy(certificate); c['patterns'].pop(); changes.append(('missing pattern', c))
    c = copy.deepcopy(certificate); c['patterns'][0] = c['patterns'][1]; changes.append(('duplicate pattern', c))
    c = copy.deepcopy(certificate); c['minors'][0]['determinant'] = 0; changes.append(('zero minor', c))
    c = copy.deepcopy(certificate); c['minors'][0]['determinant'] = float(c['minors'][0]['determinant']); changes.append(('float minor', c))
    c = copy.deepcopy(certificate)
    record = next(r for r in c['patterns'] if r['repairs'])
    target = next(iter(record['repairs']))
    record['repairs'][target][0] = int(target)
    changes.append(('target used as its own source', c))
    c = copy.deepcopy(certificate)
    record = next(r for r in c['patterns'] if r['rank'] == 7)
    record['columns'][-1] = next(iter(set(range(8)) - set(record['columns'])))
    changes.append(('wrong coordinate upper bound', c))
    for name, c in changes:
        rejects(lambda c=c: check.audit(c), name)
    pins = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    with tempfile.TemporaryDirectory(prefix='sink97-controls-', dir=source.ROOT) as tmp:
        package = Path(tmp)
        (package / 'BASE-SELECTED.json').write_bytes((HERE / 'BASE-SELECTED.json').read_bytes())
        mutations = []
        p = copy.deepcopy(pins); p['files'].pop(next(iter(p['files']))); mutations.append(p)
        p = copy.deepcopy(pins); p['files']['extra'] = '0'*64; mutations.append(p)
        p = copy.deepcopy(pins); p['base'] = '0'*40; mutations.append(p)
        p = copy.deepcopy(pins); p['files'][next(iter(p['files']))] = '0'*64; mutations.append(p)
        p = copy.deepcopy(pins); p['selected_snapshot_sha256'] = '0'*64; mutations.append(p)
        for p in mutations:
            (package / 'SOURCES.json').write_text(json.dumps(p), encoding='utf-8')
            rejects(lambda: source.checked_sources(package=package), 'package pins')
    print('PASS_P112_FREE_SINK_CONTROLS mathematical=6 package=5')


if __name__ == '__main__':
    main()
