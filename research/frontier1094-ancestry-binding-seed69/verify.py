#!/usr/bin/env python3
"""Certify the PR799/PR741 ancestry binding behind the selected #1094 reuse replay.

The committed PR799 and PR741 replay archives are rebuilt into the
check_selected layout. The unchanged check must return the exact bytes bound by
the published #1042 receipt and its archived replay. The pinned reuse-branch
statements of verify_frontier1094.py, and the whole pinned verifier in a scratch
root, then run on variant ancestors. The timing, bit_result and bit_supplier
variants pass check_selected but differ from the bound binding; the pinned code
accepts them and the one-line comparison suggested in README.md rejects them.
Identity is accepted by both, and a kappa control is rejected by check_selected.

Seed-69 adversarial audit. Sagar Thakrar with substantial Anthropic Claude
assistance. Apache-2.0.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]

A1094 = ROOT/'research/community-frontier1094-audit'
A1042 = ROOT/'research/community-frontier1042-audit'
ARCHIVE799 = ROOT/'research/community-frontier799-audit/integrated799-replay.tar.gz'
ARCHIVE741 = ROOT/'research/community-frontier741-audit/composed-replay-evidence.tar.gz'
# Audited verifier bytes: (path, Git blob, SHA256). Read from Git if the live file changes.
VERIFIER1094 = ('scripts/verify_frontier1094.py', '96e6c1386bd052b9bcaf136d934406f3f0c3f777',
                'c7e20f59968ed5736fb859735de4de207de3418083e37012310ebcded946b949')
VERIFIER1042 = ('scripts/verify_frontier1042.py', 'e4f129b0570865330e39ae11eafafe7167f7e374',
                '700fdcaeb6e8f57f6e63c71c2dd1652fc5b183e8d706cd092779bdc0d271e854')
RECEIPT1042_SHA256 = 'bf12c6ed3b412539638b76addb40591a631609b2ab9e5ee0db1f6bbe067d0ec0'
BINDING_SHA256 = '22575ff21833fdfcfc7d67d7d9b3b433cf13a3165628ebcb9aaae239b8145472'
EXPECTED = json.loads((PACKAGE/'EXPECTED.json').read_bytes())


def require(condition, message):
    if not condition:
        raise SystemExit('FAIL: ' + message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2)+'\n')


def canonical(binding):
    """The serialization verify_frontier1042.py writes to BASELINE-BINDING.json."""
    return (json.dumps(binding, indent=2)+'\n').encode()


def differing(a, b, path=''):
    if isinstance(a, dict) and isinstance(b, dict):
        return [p for k in sorted(set(a) | set(b)) for p in differing(a.get(k), b.get(k), path+'/'+k)]
    return [] if a == b else [path]


def pinned_source(entry):
    name, blob, digest = entry
    data = (ROOT/name).read_bytes() if (ROOT/name).is_file() else b''
    if sha(data) != digest:
        data = subprocess.run(['git', 'cat-file', 'blob', blob], cwd=ROOT,
                              capture_output=True, check=True).stdout
    require(sha(data) == digest, 'Pinned audited source: ' + name)
    return data


def extract(archive, target):
    with tarfile.open(archive) as tf:
        members = tf.getmembers()
        require(all(m.isfile() or m.isdir() for m in members), 'Archive contains links or devices')
        tf.extractall(target, filter='data')


def reuse_branch():
    """Return the three pinned reuse-branch statements and the suggested binding."""
    tree = ast.parse(pinned_source(VERIFIER1094))
    main = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main']
    require(len(main) == 1, 'One main function')
    body = main[0].body
    calls = [n for n in ast.walk(main[0]) if isinstance(n, ast.Call) and
             isinstance(n.func, ast.Name) and n.func.id == 'check_selected']
    require(len(calls) == 1, 'One check_selected call in verify_frontier1094.py')
    index = [i for i, n in enumerate(body) if isinstance(n, ast.Expr) and n.value is calls[0]]
    require(len(index) == 1, 'The check_selected call is a bare expression statement')
    i = index[0]
    statements = body[i-1:i+2]
    text = [ast.unparse(n) for n in statements]
    require(text == EXPECTED['pinned_reuse_branch'], 'Pinned reuse-branch statements')
    require(sum(isinstance(n, ast.Constant) and n.value == 'BASELINE-BINDING.json'
                for n in ast.walk(tree)) == 1, 'BASELINE-BINDING.json is read once, by hash only')
    fixed = ast.parse(EXPECTED['suggested_binding']).body
    pinned = ast.Module(body=statements, type_ignores=[])
    patched = ast.Module(body=[statements[0], *fixed, statements[2]], type_ignores=[])
    return (compile(ast.fix_missing_locations(pinned), VERIFIER1094[0], 'exec'),
            compile(ast.fix_missing_locations(patched), 'suggested-binding', 'exec'))


def writer_pattern():
    """verify_frontier1042.py records exactly check_selected's return value."""
    tree = ast.parse(pinned_source(VERIFIER1042))
    text = [ast.unparse(n) for n in ast.walk(tree) if isinstance(n, (ast.Assign, ast.Expr))]
    require(EXPECTED['writer_statements'][0] in text and EXPECTED['writer_statements'][1] in text,
            'PR1042 writer serializes the check_selected return value')


def run_branch(code, ancestor, receipt):
    """Execute pinned or suggested statements as the reuse branch would."""
    scope = dict(Path=Path, check_selected=check_selected, read=read,
                 require=source_require,
                 sha=lambda p: sha(Path(p).read_bytes()), baseline=A1042,
                 receipt=dict(receipt, baseline=str(ancestor)))
    try:
        exec(code, scope)
    except (ValueError, KeyError, FileNotFoundError) as error:
        return 'REJECT: ' + str(error)
    return 'ACCEPT'


COPIED = ['scripts/verify_replay_coverage.py', 'scripts/verify_frontier741_bridge_coverage.py',
          'scripts/verify_frontier741_bindings.py', 'scripts/verify_frontier799_bindings.py',
          'scripts/verify_frontier799.py', 'certificates/replay-coverage/pr741-sw4-v1.json',
          'research/complex-sw4-frame8/verify.py', 'research/complex-sw4-frame8/MANIFEST.json',
          'research/complex-sw4-frame8/data/SPEC.json', 'research/complex-sw4-frame8/inputs/PR589-EXPECTED.json',
          'research/e8-bit-p111-tuned/tune/EXPECTED.json', 'research/gauge44-frames-x']
STUB_CANDIDATE = '''import shutil, sys
from pathlib import Path
strict = Path(sys.argv[sys.argv.index('--work')+1])/'strict'
strict.mkdir(parents=True)
for name in ('REPLAY.json', 'ASSEMBLY.json'):
    shutil.copyfile(Path(%r)/name, strict/name)
'''


def end_to_end(tmp, variants, r1042):
    """Run the whole pinned PR1094 reuse mode in a scratch root, stubbing two stages.

    Stubbed: the historical-source stage and the rare-pattern candidate stage,
    which copies the published PR1094 REPLAY/ASSEMBLY. The receipt's baseline
    path is redirected to each variant, as if it were placed at the recorded path.
    """
    source = pinned_source(VERIFIER1094).decode()
    old = "    check_selected(ancestor, ancestor/'ancestor')\n"
    require(source.count(old) == 1, 'One bare reuse recheck line')
    fixed = source.replace(old, '    ' + EXPECTED['suggested_binding'].replace(' / ', '/') + '\n')
    archive = tmp/'b1042'
    extract(A1042/'selected-replay.tar.gz', archive)
    require((archive/'RESULT.json').read_bytes() == (A1042/'RESULT.json').read_bytes(), 'Archived PR1042 receipt')
    dropped = ('PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONSAFEPATH', 'FORCE_COLOR', 'PYTHON_COLORS')
    env = {k: v for k, v in os.environ.items() if k not in dropped} | {'NO_COLOR': '1', 'PYTHON_COLORS': '0'}
    rows = {}
    for label, text in [('pinned_reuse_mode', source), ('suggested_reuse_mode', fixed)]:
        root = tmp/('root-' + label)
        for name in COPIED + [s['script'] for s in r1042['stages']]:
            target = root/name
            target.parent.mkdir(parents=True, exist_ok=True)
            if (ROOT/name).is_dir():
                shutil.copytree(ROOT/name, target, ignore=shutil.ignore_patterns('__pycache__'))
            else:
                shutil.copyfile(ROOT/name, target)
        (root/'scripts/verify_frontier1094.py').write_text(text)
        (root/'scripts/verify_selected_result.py').write_text("print('stubbed historical-source stage')\n")
        stub = root/'research/complex-t16-rare-pattern-exchanges/verify.py'
        stub.parent.mkdir(parents=True)
        stub.write_text(STUB_CANDIDATE % str(A1094))
        (root/'research/community-frontier1042-audit').mkdir(parents=True)
        for name, work in variants:
            receipt = dict(r1042, baseline=str(work))
            for path in (archive/'RESULT.json', root/'research/community-frontier1042-audit/RESULT.json'):
                write(path, receipt)
            p = subprocess.run([sys.executable, '-B', str(root/'scripts/verify_frontier1094.py'),
                                '--work', str(tmp/('run-' + label + '-' + name)), '--baseline1042', str(archive)],
                               capture_output=True, text=True, env=env, timeout=300)
            last = (p.stdout if p.returncode == 0 else p.stderr).strip().splitlines()
            rows.setdefault(name, {})[label] = 'exit %d: %s' % (p.returncode, last[-1] if last else '')
    return rows


def rebind(work):
    """A consistent rerun records the ancestry check in ANCESTRY.json and RESULT.json."""
    binding = check_ancestry(work/'ancestor/bit', work/'ancestor/complex')
    for name, field in [('ANCESTRY.json', 'binding'), ('RESULT.json', 'ancestry')]:
        value = read(work/name)
        value[field] = binding
        write(work/name, value)


def timing(work):
    receipt = read(work/'ancestor/complex/RECEIPT.json')
    receipt['stages'][0]['seconds'] += 1.0
    write(work/'ancestor/complex/STAGES.json', receipt['stages'])
    require('STAGES.json' in receipt['artifacts'], 'Stage record is an inventoried artifact')
    receipt['artifacts']['STAGES.json'] = sha((work/'ancestor/complex/STAGES.json').read_bytes())
    write(work/'ancestor/complex/RECEIPT.json', receipt)
    rebind(work)


def bit_result(work):
    value = read(work/'ancestor/bit/RESULT9.json')
    value['next_grid_point_rejected'] = 'not-recorded'
    write(work/'ancestor/bit/RESULT9.json', value)
    rebind(work)


def bit_supplier(work):
    value = read(work/'global/ASSEMBLY.json')
    value['bit_supplier']['commit'] = '0'*40
    value['bit_supplier']['git_blob_sha1'] = '0'*40
    write(work/'global/ASSEMBLY.json', value)


def kappa(work):
    value = read(work/'RESULT.json')
    value['kappa'] = '1661634653669568/1000000000000000000'
    write(work/'RESULT.json', value)


VARIANTS = [('identity', None), ('timing', timing), ('bit_result', bit_result),
            ('bit_supplier', bit_supplier), ('kappa', kappa)]


def load_checkers():
    """Require every declared live input at its pin before importing the checkers."""
    rows = [r for r in read(PACKAGE/'SOURCES.json')['files'] if r['usage'] == 'input']
    for row in rows:
        require(sha((ROOT/row['path']).read_bytes()) == row['sha256'], 'Pinned input: ' + row['path'])
    pinned = {r['path']: r['sha256'] for r in rows}
    require(pinned['research/community-frontier1042-audit/RESULT.json'] == RECEIPT1042_SHA256 and
            pinned['research/community-frontier1042-audit/BASELINE-BINDING.json'] == BINDING_SHA256,
            'Receipt and binding pins')
    global check_selected, check_ancestry, source_require
    sys.path.insert(0, str(ROOT/'scripts'))
    from verify_replay_coverage import check_selected, require as source_require
    from verify_frontier741_bridge_coverage import check as check_ancestry


def main():
    require(sys.version_info >= (3, 12), 'Python 3.12 or later')
    require(not sys.flags.optimize, 'Inherited checks require assertions')
    load_checkers()
    r1094, r1042 = read(A1094/'RESULT.json'), read(A1042/'RESULT.json')
    bound = (A1042/'BASELINE-BINDING.json').read_bytes()
    require(r1094['status'] == 'PASS_COMPLETE_PR1094_COMPOSITION' and r1094['reused_completed_baseline'] is True and
            r1094['baseline_receipt_sha256'] == RECEIPT1042_SHA256, 'PR1094 receipt names the PR1042 receipt')
    require(r1042['status'] == 'PASS_COMPLETE_PR1042_COMPOSITION' and r1042['reused_completed_baseline'] is True and
            r1042['baseline_binding_sha256'] == sha(bound) == BINDING_SHA256, 'PR1042 receipt names the binding')
    with tarfile.open(A1042/'selected-replay.tar.gz') as tf:
        for name in ('RESULT.json', 'BASELINE-BINDING.json'):
            require(tf.extractfile(name).read() == (A1042/name).read_bytes(), 'Archived PR1042 replay: ' + name)
    baselines = dict(pr1094=r1094['baseline'], pr1042=r1042['baseline'])
    require(baselines == EXPECTED['recorded_baselines'], 'Recorded machine-local baselines')
    writer_pattern()
    pinned, patched = reuse_branch()
    with tempfile.TemporaryDirectory(prefix='ancestry1094-') as tmp:
        base = Path(tmp)/'base'
        require(not base.resolve().is_relative_to(ROOT), 'Use external scratch space')
        extract(ARCHIVE799, base)
        extract(ARCHIVE741, base/'ancestor')
        rows = {}
        for name, mutate in VARIANTS:
            work = Path(tmp)/name
            shutil.copytree(base, work)
            if mutate:
                mutate(work)
            try:
                binding = check_selected(work, work/'ancestor')
                row = dict(check_selected='PASS', binding_sha256=sha(canonical(binding)),
                           differs_from_bound=differing(binding, json.loads(bound)))
            except (ValueError, KeyError, AssertionError) as error:
                row = dict(check_selected='REJECT: ' + str(error))
            row['pinned_reuse_branch'] = run_branch(pinned, work, r1042)
            row['suggested_binding'] = run_branch(patched, work, r1042)
            rows[name] = row
            print(name, json.dumps(row, sort_keys=True), flush=True)
        identity = rows['identity']
        require(identity['check_selected'] == 'PASS' and identity['binding_sha256'] == sha(bound) and
                identity['differs_from_bound'] == [], 'Committed archives rebuild the exact bound binding')
        require(rows == EXPECTED['variants'], 'Variant outcomes')
        full = end_to_end(Path(tmp), [(name, Path(tmp)/name) for name, _ in VARIANTS], r1042)
        for name, row in full.items():
            print(name, json.dumps(row, sort_keys=True), flush=True)
        require(full == EXPECTED['end_to_end'], 'End-to-end reuse-mode outcomes')
    print('PASS_FRONTIER1094_ANCESTRY_BINDING_AUDIT', sha(bound))


if __name__ == '__main__':
    main()
