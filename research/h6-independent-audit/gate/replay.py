#!/usr/bin/env python3
"""Fresh file export and corruption gates; Git blob checks use explicit source DB."""
from pathlib import Path
import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
ROOT = PACKAGE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    started = time.monotonic()
    previous = json.loads((HERE / 'RESULT.json').read_text()) if '--reuse-pass' in sys.argv else None
    if previous is not None:
        require(previous['status'] == 'PASS_FRESH_EXPORT_AND_DEFECT_SENSITIVE_GATES', 'Prior fresh replay passed')
    pins = json.loads((PACKAGE / 'provenance/PINS.json').read_text())
    workspace = Path(tempfile.mkdtemp(prefix='h6-clean-export-', dir='/private/tmp'))
    exported = workspace / 'minimal-source-tree'
    unrelated = workspace / 'unrelated-cwd'
    unrelated.mkdir()
    target = exported / 'research/h6-independent-audit'
    shutil.copytree(PACKAGE, target, ignore=shutil.ignore_patterns('__pycache__'))
    for name in pins:
        destination = exported / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)
    reused = []
    if previous is not None:
        previous_export = Path(previous['export'])
        for relative in ['walsh/audit.py', 'review/walsh/replay.py']:
            require((target / relative).read_bytes() == (previous_export / 'research/h6-independent-audit' / relative).read_bytes(),
                    'Reused exhaustive checker unchanged: ' + relative)
        for name in pins:
            require((exported / name).read_bytes() == (previous_export / name).read_bytes(), 'Reused frozen source unchanged: ' + name)
        for relative in ['walsh/results.json', 'review/walsh/RESULT.json']:
            origin = previous_export / 'research/h6-independent-audit' / relative
            shutil.copyfile(origin, target / relative)
            reused.append(dict(relative=relative, sha256=hashlib.sha256(origin.read_bytes()).hexdigest(), previous_export=str(previous_export)))
    gitdir = subprocess.check_output(['git', 'rev-parse', '--absolute-git-dir'], cwd=ROOT, text=True).strip()
    env = dict(os.environ, GIT_DIR=gitdir, GIT_WORK_TREE=str(exported))
    checks = []

    def execute(name, relative, *, must_fail=None, inline=None):
        command = [sys.executable, '-I', '-O', '-B']
        command += ['-c', inline] if inline is not None else [str(target / relative)]
        completed = subprocess.run(command, cwd=unrelated, env=env, capture_output=True, text=True)
        log = completed.stdout + completed.stderr
        (HERE / (name + '.txt')).write_text(log)
        if must_fail:
            require(completed.returncode != 0 and must_fail in log, name + ' must reject: ' + log[-1500:])
        else:
            require(completed.returncode == 0, name + ' replay failed: ' + log[-3000:])
        checks.append(dict(name=name, returncode=completed.returncode,
                          outcome='DETECTED' if must_fail else 'PASS',
                          expected_failure=must_fail, log_sha256=hashlib.sha256(log.encode()).hexdigest()))
        print(name + ': ' + checks[-1]['outcome'], flush=True)

    scripts = sorted(target.rglob('*.py'))
    script_hashes = {str(path.relative_to(exported)): hashlib.sha256(path.read_bytes()).hexdigest() for path in scripts}
    asserts = {str(path.relative_to(exported)): sum(isinstance(node, ast.Assert) for node in ast.walk(ast.parse(path.read_text()))) for path in scripts}
    require(not any(asserts.values()), 'New audit checks must remain active under Python -O')
    if previous is None:
        execute('clean-unified', 'verify.py')
    else:
        for relative in ['provenance/check.py', 'invoice/verify.py', 'helper/frame_support.py',
                         'helper/charged_screen.py', 'review/charged/replay.py', 'spectral/audit.py', 'lifecycle/probe.py']:
            execute('final-' + relative[:-3].replace('/', '-'), relative)
        execute('final-summary', 'verify.py', inline="import runpy; m=runpy.run_path(%r); m['summaries']()" % str(target / 'verify.py'))
    runner_ast = ast.parse((target / 'verify.py').read_text())
    covered = {node.args[0].value for node in ast.walk(runner_ast)
               if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
               and node.func.id == 'step' and node.args and isinstance(node.args[0], ast.Constant)}
    # Older runner snapshots receive the same additional gates separately.
    if 'lifecycle/probe.py' not in covered:
        execute('clean-lifecycle', 'lifecycle/probe.py')
    if 'review/walsh/replay.py' not in covered:
        execute('clean-independent-walsh', 'review/walsh/replay.py')

    def mutant(name, relative, old, new, failure):
        path = target / relative
        original = path.read_text()
        require(old in original, name + ' mutation anchor exists')
        path.write_text(original.replace(old, new, 1))
        try:
            execute(name, relative, must_fail=failure)
        finally:
            path.write_text(original)

    source = exported / 'research/leech-lattice/code/screen.py'
    original = source.read_bytes()
    source.write_bytes(original + b'\n# independent gate corruption\n')
    try:
        execute('source-corruption', 'verify.py', must_fail='frozen source pin: research/leech-lattice/code/screen.py')
    finally:
        source.write_bytes(original)
    # Invoke summary enforcement directly so regeneration cannot overwrite a corrupt receipt.
    summary_code = "import runpy; m=runpy.run_path(%r); m['summaries']()" % str(target / 'verify.py')
    walsh_receipt = json.loads((target / 'walsh/results.json').read_text())
    for name, relative, key, value, reason in [
        ('wrong-block-tally', 'spectral/results.json', 'corrected_ordered_off_diagonal_blocks', 28560, 'canonical block count'),
        ('wrong-block-sign', 'spectral/results.json', 'off_diagonal_compensation_sign_fixture.correct_I_minus_K', '5/16', 'compensation block sign'),
        ('histogram-corruption', 'walsh/results.json', 'pairing_histogram.3', walsh_receipt['pairing_histogram']['3'] + 1, 'complete ordered-pair coverage'),
        ('exception-summary', 'walsh/results.json', 'exceptional_abs_t_3_pairs', 3363841, 'exception summary')]:
        path = target / relative
        original = path.read_bytes()
        receipt = json.loads(original)
        destination = receipt
        pieces = key.split('.')
        for piece in pieces[:-1]:
            destination = destination[piece]
        destination[pieces[-1]] = value
        path.write_text(json.dumps(receipt))
        try:
            execute(name, relative, must_fail=reason, inline=summary_code)
        finally:
            path.write_bytes(original)
    mutant('wrong-exception-sign', 'walsh/audit.py',
           'right = 3 * t * B - 24 * np.sign(t)',
           'right = 3 * t * B + 24 * np.sign(t)', 'scaled compensation identity rows 0:')
    mutant('omitted-pad', 'invoice/verify.py',
           'for rank in partition(pad, cap))', 'for rank in [])',
           'independent helper rank-mass equality')
    mutant('omitted-cleanup', 'lifecycle/probe.py',
           'events = compensation + joins + gather + walsh + scatter + terminal + cleanup + target_finish',
           'events = compensation + joins + gather + walsh + scatter + terminal + target_finish',
           'forward arbitrary-dirt shear')
    require(all(hashlib.sha256(path.read_bytes()).hexdigest() == script_hashes[str(path.relative_to(exported))]
                for path in scripts), 'Every exported audit script restored after mutation controls')
    require(all(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest
                for name, digest in script_hashes.items()), 'Current audit scripts match tested fresh export')
    receipt = dict(status='PASS_FRESH_EXPORT_AND_DEFECT_SENSITIVE_GATES',
                   cwd=str(unrelated), export=str(exported), pinned_files=len(pins),
                   isolated_python=True, optimized_python=True, no_bytecode=True,
                   assert_nodes_by_new_script=asserts, checks=checks,
                   relocated_audit_script_sha256=script_hashes,
                   unified_steps=sorted(covered),
                   replay_mode='UNCHANGED_EXHAUSTIVE_RECEIPTS_REUSED_WITH_SOURCE_AND_CHECKER_HASH_EQUALITY' if previous else 'FULL_FRESH_REPLAY',
                   reused_exhaustive_receipts=reused,
                   python=sys.version, executable=sys.executable,
                   git_provenance=dict(mode='EXPLICIT_READ_ONLY_SOURCE_OBJECT_DATABASE', git_dir=gitdir,
                                       git_work_tree=str(exported), checks_disabled=False),
                   elapsed_seconds=round(time.monotonic()-started, 3),
                   limits=['Fresh export relocates source/audit files but Git blob provenance intentionally reads the exact original object database.',
                           'No standalone bundled Git object database, cold selected-supplier replay, hosted CI, or construction theorem claimed.'])
    (HERE / 'RESULT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(receipt['status'], flush=True)


if __name__ == '__main__':
    main()
