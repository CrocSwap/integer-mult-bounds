#!/usr/bin/env python3
"""Relocate the complete pinned H6 successor and run optimized semantic gates."""
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
EXTRA = ['research/niemeier-lattices/code/e8_sections.py',
         'research/split-centres-global/vendor/clifford_exact.py',
         'notes/general-clifford-frames.tex']


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_bindings(root, pins):
    for name, pin in pins.items():
        need(sha(root/name) == pin['sha256'], 'Frozen source binding: '+name)


def main():
    started = time.monotonic()
    task = json.loads((PACKAGE/'TASK.json').read_text())
    base = task['base']
    declared = json.loads((PACKAGE/'SOURCES.json').read_text())['sha256']
    prior = subprocess.check_output(['git', 'ls-files', 'research/h6-independent-audit'], cwd=ROOT, text=True).splitlines()
    names = sorted(set(declared) | set(prior) | set(EXTRA))
    pins = {}
    for name in names:
        need(not name.startswith('research/h6-compensation-network/'), 'Inherited source inventory contains mutable successor file: '+name)
        content = (ROOT/name).read_bytes()
        frozen = subprocess.check_output(['git', 'show', base+':'+name], cwd=ROOT)
        need(content == frozen, 'Inherited source/prior audit differs from pinned base: '+name)
        digest = hashlib.sha256(content).hexdigest()
        if name in declared:
            need(digest == declared[name], 'Declared source hash mismatch: '+name)
        pins[name] = dict(commit=base, sha256=digest)
    (HERE/'PINS.json').write_text(json.dumps(dict(base=base, files=pins,
        scope='Complete declared predecessor inventory, all tracked immutable prior audit artifacts, new runtime e8_sections/Clifford exact source and frame notes.'), indent=2, sort_keys=True)+'\n')
    workspace = Path(tempfile.mkdtemp(prefix='h6-successor-clean-'))
    exported = workspace/'minimal-source-tree'
    unrelated = workspace/'unrelated-cwd'
    unrelated.mkdir()
    target = exported/'research/h6-compensation-network'
    shutil.copytree(PACKAGE, target, ignore=shutil.ignore_patterns('__pycache__'))
    for name in names:
        destination = exported/name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/name, destination)
    check_bindings(exported, pins)
    scripts = sorted(target.rglob('*.py'))
    script_hashes = {str(path.relative_to(exported)): sha(path) for path in scripts}
    specifications = ['TASK.json', 'SOURCES.json', 'PACKAGING.json', 'routes/BUCKETED-SCHEMA.json',
                      'contract/THEOREM.md', 'physical_compiler/UNIVERSAL-THEOREM.md']
    specification_hashes = {str((target/name).relative_to(exported)): sha(target/name)
                            for name in specifications if (target/name).exists()}
    assertions = {str(path.relative_to(exported)): sum(isinstance(node, ast.Assert) for node in ast.walk(ast.parse(path.read_text())))
                  for path in scripts}
    need(not any(assertions.values()), 'Every new core check must survive Python -O')
    gitdir = subprocess.check_output(['git', 'rev-parse', '--absolute-git-dir'], cwd=ROOT, text=True).strip()
    environment = dict(os.environ, GIT_DIR=gitdir, GIT_WORK_TREE=str(exported))
    checks = []

    def execute(name, relative=None, inline=None, reason=None):
        command = [sys.executable, '-I', '-O', '-B']
        command += ['-c', inline] if inline is not None else [str(target/relative)]
        completed = subprocess.run(command, cwd=unrelated, env=environment, text=True, capture_output=True)
        output = completed.stdout + completed.stderr
        (HERE/(name+'.txt')).write_text(output)
        need(completed.returncode != 0 and reason in output if reason else completed.returncode == 0,
             name+' did not produce its required result:\n'+output[-4000:])
        checks.append(dict(name=name, status='DETECTED' if reason else 'PASS',
                          expected_error=reason, returncode=completed.returncode,
                          log_sha256=hashlib.sha256(output.encode()).hexdigest()))
        print(name+': '+checks[-1]['status'], flush=True)

    if '--preflight' not in sys.argv:
        need((target/'verify.py').is_file(), 'Final unified verifier must exist before full gate')
        execute('clean-unified', relative='verify.py')
    execute('independent-corruption-controls', relative='gate/controls.py')
    path = target/'k_encoder/network.py'
    original = path.read_text()
    need('weights.append(16)' in original, 'Exact K polynomial mutation anchor')
    path.write_text(original.replace('weights.append(16)', 'weights.append(17)', 1))
    try:
        execute('K-polynomial-coefficient', inline="import runpy; m=runpy.run_path(%r); m['polynomial_certificate']()" % str(path),
                reason='K exact check at original line 44')
    finally:
        path.write_text(original)
    path = exported/'research/niemeier-lattices/code/e8_sections.py'
    original = path.read_bytes()
    path.write_bytes(original+b'\n# independent gate source corruption\n')
    try:
        if '--preflight' not in sys.argv:
            execute('transitive-source-mutation', relative='verify.py', reason='e8_sections.py')
        else:
            try:
                check_bindings(exported, pins)
            except ValueError as exc:
                need('e8_sections.py' in str(exc), 'New transitive source mutation reason')
                checks.append(dict(name='transitive-source-mutation', status='DETECTED', expected_error=str(exc)))
            else:
                raise ValueError('Transitive source mutation was not detected')
    finally:
        path.write_bytes(original)
    # No successor replay may silently edit an imported old audit or frozen source.
    check_bindings(exported, pins)
    check_bindings(ROOT, pins)
    need({str(path.relative_to(ROOT)) for path in PACKAGE.rglob('*.py')} == set(script_hashes),
         'Current script inventory must equal the tested fresh export inventory')
    need(all(sha(exported/name) == digest and sha(ROOT/name) == digest for name, digest in script_hashes.items()),
         'Final current script snapshot and exported scripts must match, with all mutations restored')
    need(all(sha(exported/name) == digest and sha(ROOT/name) == digest
             for name, digest in specification_hashes.items()), 'Final source/task/schema/proof specification snapshot must match tested export')
    controls = json.loads((target/'gate/CONTROLS.json').read_text())
    (HERE/'CONTROLS.json').write_text(json.dumps(controls, indent=2, sort_keys=True)+'\n')
    receipt = dict(status='PASS_SUCCESSOR_PREFLIGHT' if '--preflight' in sys.argv else 'PASS_SUCCESSOR_FRESH_EXPORT_AND_MUTATION_GATES',
        base=base, export=str(exported), cwd=str(unrelated), inherited_pinned_files=len(pins),
        pins_sha256=sha(HERE/'PINS.json'), audit_script_sha256=script_hashes,
        specification_sha256=specification_hashes,
        assert_nodes_by_new_script=assertions, checks=checks, semantic_negative_controls=controls['checks'],
        inherited_exact_lowerer_assert_nodes=sum(isinstance(node, ast.Assert) for node in ast.walk(ast.parse(
            (exported/'research/split-centres-global/vendor/clifford_exact.py').read_text()))),
        optimized_guard_scope='New explicit rank, signed-tableau and complete exact state/phase guards remain active. Frozen lowerer legacy asserts are inactive under -O; its source is retained unchanged.',
        environment=dict(python=sys.version, executable=sys.executable, numpy=__import__('numpy').__version__,
                         isolated=True, optimized=True, no_bytecode=True),
        git_provenance=dict(mode='EXACT_BASE_BLOBS_AND_EXPLICIT_READ_ONLY_SOURCE_OBJECT_DATABASE',
                            git_dir=gitdir, checks_disabled=False),
        elapsed_seconds=round(time.monotonic()-started, 3),
        limits=['The file export has complete pinned runtime/evidence source closure, while Git provenance reads the exact original object database.',
                'The prior 958521600-entry exhaustive audit is immutable retained evidence, not replayed here.',
                'No billion-event full word, hosted CI, selected supplier cold replay, admission or new kappa claim.'])
    destination = HERE/('PREFLIGHT.json' if '--preflight' in sys.argv else 'RESULT.json')
    destination.write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(receipt['status'], flush=True)


if __name__ == '__main__':
    main()
