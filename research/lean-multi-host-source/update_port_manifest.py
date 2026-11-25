#!/usr/bin/env python3
"""Regenerate the complete Lean 4.21 port inventory without changing audit scope."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
BASE = 'c4b1560a569f54064608bf88440f9e492c03fba3'
LEAN_COMMIT = '6741444a63eec253a7eae7a83f1beb3de015023d'
MATHLIB_COMMIT = '308445d7985027f538e281e18df29ca16ede2ba3'
SIBLINGS = ['lean-multi-host-source', 'lean-multi-host-framework',
            'lean-whole-residual-hosting', 'lean-source-invocation-audit',
            'lean-single-stream-obstruction']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2) + '\n')


def code(text):
    # Nested block comments are legal Lean syntax; preserve line boundaries.
    out, i, depth = [], 0, 0
    while i < len(text):
        if text.startswith('/-', i):
            depth += 1; i += 2
        elif depth and text.startswith('-/', i):
            depth -= 1; i += 2
        elif depth:
            out.append('\n' if text[i] == '\n' else ' '); i += 1
        elif text.startswith('--', i):
            end = text.find('\n', i)
            i = len(text) if end < 0 else end
        else:
            out.append(text[i]); i += 1
    assert depth == 0, 'Unclosed block comment'
    return ''.join(out)


def imports(path):
    return [name for row in re.findall(r'^import\s+(.+)$', code(path.read_text()), re.M)
            for name in row.split()]


def relative(path):
    return os.path.relpath(path, ROOT)


def main():
    def baseline_json(sibling):
        path = 'research/' + sibling + '/proof-manifest.json'
        return json.loads(subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=REPO))

    config = tomllib.loads((ROOT / 'lakefile.toml').read_text())
    paths = {}
    for lib in config['lean_lib']:
        directory = ROOT / lib.get('srcDir', '.')
        for name in lib['roots']:
            assert name not in paths, name
            paths[name] = directory / (name.replace('.', '/') + '.lean')
    records = {name: {'module': name, 'source': relative(path), 'sha256': digest(path),
                      'imports': imports(path)} for name, path in paths.items()}
    def closure(names):
        ordered, active = [], set()
        def visit(name):
            if name == 'Std' or name == 'Lean' or name.startswith(('Std.', 'Lean.', 'Mathlib.')):
                return
            assert name in records, 'Unmanifested dependency: ' + name
            assert name not in active, 'Import cycle: ' + name
            if name in ordered:
                return
            active.add(name)
            for dep in records[name]['imports']:
                visit(dep)
            active.remove(name)
            ordered.append(name)
        for name in names:
            visit(name)
        return ordered
    ordered = closure(sorted(paths))
    task_b = json.loads((ROOT / 'proof-manifest.json').read_text())
    baseline_b = baseline_json('lean-multi-host-source')
    original_b_names = [r['module'] for r in baseline_b['modules']]
    assert len(original_b_names) == len(set(original_b_names)) == 52
    b_names = closure(original_b_names)
    assert len(task_b['audit_declarations']) == 931
    assert task_b['audit_declarations'] == baseline_json('lean-multi-host-source')['audit_declarations']
    assert 'SourceInvocation.actualContract' in task_b['audit_declarations']
    task_b.update(lean_commit=LEAN_COMMIT, mathlib_commit=MATHLIB_COMMIT,
                  modules=[records[name] for name in b_names])
    write(ROOT / 'proof-manifest.json', task_b)
    audits = {}
    specifications = [
        ('task_a', 'lean-multi-host-framework', 'TaskAAxioms.lean', 21),
        ('hosting', 'lean-whole-residual-hosting', '../lean-whole-residual-hosting/Audit.lean', 47),
        ('source_invocation', 'lean-source-invocation-audit', '../lean-source-invocation-audit/Audit.lean', 422),
    ]
    for key, sibling, audit_source, count in specifications:
        directory = ROOT.parent / sibling
        manifest_path = directory / 'proof-manifest.json'
        old = json.loads(manifest_path.read_text())
        names = old['theorems']
        assert names == baseline_json(sibling)['theorems'], 'Changed original audit inventory: ' + key
        assert len(names) == count and len(set(names)) == count
        old['lean_commit'] = LEAN_COMMIT
        if key == 'task_a':
            modules = list(old['sha256'])
            old['sha256'] = {name: records[name]['sha256'] for name in modules}
            old['imports'] = {name: records[name]['imports'] for name in modules}
            (ROOT / audit_source).write_text('\n'.join('import ' + n for n in modules)
                + '\n\n' + '\n'.join('#print axioms ' + n for n in names) + '\n')
        elif key == 'hosting':
            old['sha256'] = {name: digest(directory / name) for name in old['sha256']}
            old['imports'] = {name: imports(directory / name) for name in old['imports']}
        else:
            for record in old['modules'].values():
                path = directory / record['path']
                record.update(sha256=digest(path), imports=imports(path))
        write(manifest_path, old)
        audits[key] = {'source': audit_source, 'declarations': names}
    b_audit = 'TaskBAxioms.lean'
    (ROOT / b_audit).write_text('\n'.join('import ' + n for n in b_names)
        + '\n\n' + '\n'.join('#print axioms ' + n for n in task_b['audit_declarations']) + '\n')
    audits['task_b'] = {'source': b_audit, 'declarations': task_b['audit_declarations']}
    single = ROOT.parent / 'lean-single-stream-obstruction'
    single_names = re.findall(r'^#print axioms (\S+)\s*$', (single / 'SingleStream.lean').read_text(), re.M)
    assert len(single_names) == len(set(single_names)) == 15
    (ROOT / 'SingleStreamAxioms.lean').write_text('import SingleStream\n\n'
        + '\n'.join('#print axioms ' + n for n in single_names) + '\n')
    write(single / 'proof-manifest.json', {'SingleStream.lean': digest(single / 'SingleStream.lean')})
    audits['single_stream'] = {'source': 'SingleStreamAxioms.lean', 'declarations': single_names}
    for item in audits.values():
        item['sha256'] = digest(ROOT / item['source'])
        assert re.findall(r'^#print axioms (\S+)\s*$', (ROOT / item['source']).read_text(), re.M) == item['declarations']
    versions_path = ROOT / 'source-versions.json'
    versions = json.loads(versions_path.read_text())
    versions['lean'] = {'version': '4.21.0', 'commit': LEAN_COMMIT,
        'linux_archive_sha256': '455c6df09d5bd54d2a51b137939c47e2dda816d512ac789c4b3642c9bf98bde8'}
    versions['mathlib'] = {'tag': 'v4.21.0', 'commit': MATHLIB_COMMIT}
    versions['project_toolchain_base'] = 'db0e57bc7f36b5ac0fc844ad7ce1396165ee6647'
    write(versions_path, versions)
    for sibling in SIBLINGS:
        toolchain = ROOT.parent / sibling / 'lean-toolchain'
        if toolchain.exists():
            toolchain.write_text('leanprover/lean4:v4.21.0\n')
    (ROOT / 'mathlib-lake-manifest.json').write_bytes((ROOT / 'lake-manifest.json').read_bytes())
    original = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE, '--',
        *['research/' + n for n in SIBLINGS]], cwd=REPO, text=True).splitlines()
    original = [name for name in original if name.endswith('.lean')]
    archives, contribution = [], []
    for name in original:
        original_bytes = subprocess.check_output(['git', 'show', BASE + ':' + name], cwd=REPO)
        path = REPO / name
        row = {'source': relative(path), 'baseline_sha256': hashlib.sha256(original_bytes).hexdigest(),
               'sha256': digest(path)}
        if '/review-receipts/' in name:
            assert row['sha256'] == row['baseline_sha256'], name
            archives.append(row)
        else:
            contribution.append(row)
    assert len(contribution) == 66 and len(archives) == 9
    original_sources = {row['source'] for row in contribution}
    module_sources = {record['source'] for record in records.values()}
    audit_sources = {audit['source'] for audit in audits.values()}
    assert len(original_sources) == 66 and len(module_sources) == len(paths)
    assert len(original_sources & module_sources) == 64
    original_audits = original_sources - module_sources
    assert len(original_audits) == 2 and original_audits <= audit_sources
    assert not module_sources & {row['source'] for row in archives}
    support_modules = [name for name in ordered if records[name]['source'] not in original_sources]
    inventory_counts = {'originalContributionFiles': 66, 'originalCompiledModules': 64,
        'originalAuditFiles': 2, 'supportModules': len(support_modules),
        'localModules': len(paths), 'taskBModules': len(b_names)}
    assert len(paths) == 64 + len(support_modules)
    selected = set(paths.values()) | {ROOT / a['source'] for a in audits.values()}
    selected.update(ROOT.glob('*.py'))
    selected.update(ROOT.glob('requirements*.txt'))
    selected.update(ROOT / name for name in ['lakefile.toml', 'lake-manifest.json',
        'lean-toolchain', 'mathlib-lake-manifest.json', 'source-versions.json', 'proof-manifest.json'])
    selected.update((ROOT / 'inputs').glob('*'))
    for sibling in SIBLINGS:
        for filename in ['lean-toolchain', 'proof-manifest.json']:
            path = ROOT.parent / sibling / filename
            if path.exists():
                selected.add(path)
    lake_manifest = json.loads((ROOT / 'lake-manifest.json').read_text())
    pins = {p['name']: p['rev'] for p in lake_manifest['packages']}
    assert len(pins) == 9 and pins['mathlib'] == MATHLIB_COMMIT
    manifest = {'schemaVersion': 1, 'scope': 'lean421-full-port', 'baselineCommit': BASE,
        'leanVersion': '4.21.0', 'leanCommit': LEAN_COMMIT, 'mathlibCommit': MATHLIB_COMMIT,
        'dependencyPins': pins, 'defaultTargets': config['defaultTargets'],
        'libraries': config['lean_lib'], 'modules': [records[n] for n in ordered],
        'supportModules': support_modules, 'inventoryCounts': inventory_counts,
        'audits': audits, 'originalContribution': contribution,
        'archivedExclusions': archives,
        'archivePolicy': 'Preserve byte-for-byte; exclude from build targets and axiom audits.',
        'files': {relative(p): digest(p) for p in sorted(selected)}}
    write(ROOT / 'port-manifest.json', manifest)
    print(f'Full port: {len(paths)} build modules (64 original + {len(support_modules)} support); '
          '66 original contribution files; 9 unchanged archival exclusions')
    print('Audits: ' + ', '.join(k + '=' + str(len(v['declarations'])) for k,v in audits.items()))


if __name__ == '__main__':
    main()
