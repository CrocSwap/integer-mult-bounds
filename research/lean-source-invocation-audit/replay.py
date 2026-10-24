#!/usr/bin/env python3
"""Fresh offline Lean 4.33.0 replay of the source trajectory and scope diagnostic."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parent
MODULES = ['CoordinateSwap', 'Hosting', 'PhysicalHosting',
           'SourceWord', 'ContractScope', 'SourceWitness', 'Audit']
CONTROLS = {
    'omit_actual_event_218': '''example :
      ActualWord.run (ActualWord.chunk1.set 18 ⟨1,126,243,false⟩)
        ActualWord.state1 = ActualWord.state2 := by decide''',
    'erase_actual_helper_output': '''example :
      ActualWord.runForward (1 <<< 243) = 0 := by
      rw [ActualWord.basis243_output]
      decide''',
    'ignore_second_retained_residual': '''example :
      SourceInvocation.declaredHostedObservation
        (SourceInvocation.witnessStream (0 : Fin 3))
        (SourceInvocation.witnessAddress (0 : Fin 3) 1) = true := by
      rw [SourceInvocation.declared_hosted_witness (0 : Fin 3) 1 (by decide)]
      decide''',
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def code_only(source):
    return re.sub(r'--[^\n]*', '', re.sub(r'/\-[\s\S]*?\-/', '', source))


def theorem_names(source):
    code = code_only(source)
    namespaces = re.findall(r'^namespace (\S+)\s*$', code, re.M)
    require(len(namespaces) == 1, 'Expected one explicit namespace')
    return [namespaces[0] + '.' + name for name in
            re.findall(r'^theorem ([\w.]+)(?=\s|:)', code, re.M)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lean', required=True, type=Path)
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    lean = args.lean.resolve(strict=True)
    env = dict(os.environ)
    for key in ('LEAN_PATH', 'LEAN_SRC_PATH'):
        env.pop(key, None)
    version = subprocess.check_output([str(lean), '--version'], env=env,
                                      text=True, timeout=30).strip()
    require(version.startswith('Lean (version 4.33.0,'), 'Lean 4.33.0 required')
    manifest = json.loads((ROOT / 'proof-manifest.json').read_text())
    sources, names = {}, []
    for module in MODULES:
        record = manifest['modules'][module]
        source = (ROOT / record['path']).read_bytes()
        require(hashlib.sha256(source).hexdigest() == record['sha256'],
                'Source hash mismatch: ' + module)
        code = code_only(source.decode())
        require(not re.search(r'\b(sorry|admit|unsafe|native_decide)\b', code),
                'Disallowed proof escape: ' + module)
        require(not re.search(r'^\s*(axiom|opaque)\s', code, re.M),
                'Project axioms/opaque declarations forbidden: ' + module)
        imports = re.findall(r'^import (.+)$', code, re.M)
        require(imports == record['imports'] and
                all(x == 'Std' or x in MODULES[:MODULES.index(module)] for x in imports),
                'Unexpected import: ' + module)
        if module != 'Audit':
            names.extend(theorem_names(source.decode()))
        sources[module] = source
    require(names == manifest['theorems'], 'Theorem inventory changed')
    require(re.findall(r'^#print axioms (\S+)$', sources['Audit'].decode(), re.M) == names,
            'Audit must cover every named theorem exactly once')
    with tempfile.TemporaryDirectory(prefix='actual-invocation-lean-') as temporary:
        build = Path(temporary)
        env['LEAN_PATH'] = str(build)
        for module, source in sources.items():
            (build / (module + '.lean')).write_bytes(source)

        def compile_file(name, output=False):
            command = [str(lean), '-t', '0']
            if output:
                command += ['-o', name + '.olean']
            command += [name + '.lean']
            return subprocess.run(command, cwd=build, env=env, text=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  timeout=240)

        timing = {}
        for module in MODULES:
            start = time.monotonic()
            result = compile_file(module, output=True)
            require(result.returncode == 0 and 'warning:' not in result.stdout,
                    module + '\n' + result.stdout)
            timing[module] = round(time.monotonic() - start, 3)
            print(json.dumps({'compiled': module, 'seconds': timing[module]}), flush=True)
        reports = {}
        for line in result.stdout.splitlines():
            match = re.fullmatch(r"'([^']+)' does not depend on any axioms", line)
            if match:
                reports[match[1]] = []
                continue
            match = re.fullmatch(r"'([^']+)' depends on axioms: \[([^]]*)\]", line)
            require(match is not None, 'Unexpected audit output: ' + line)
            axioms = match[2].split(', ') if match[2] else []
            require(set(axioms) <= {'propext', 'Quot.sound'},
                    'Unexpected transitive axiom: ' + line)
            reports[match[1]] = axioms
        require(list(reports) == names and len(result.stdout.splitlines()) == len(names),
                'Missing, extra or duplicate axiom report')
        rejected = {}
        for name, statement in CONTROLS.items():
            (build / 'Control.lean').write_text(
                'import SourceWitness\nset_option maxRecDepth 100000\n'
                'set_option maxHeartbeats 0\n' + statement + '\n')
            result = compile_file('Control')
            require(result.returncode != 0 and
                    'Tactic `decide` proved that the proposition' in result.stdout and
                    'is false' in result.stdout,
                    'Control not mathematically rejected: ' + name + '\n' + result.stdout)
            rejected[name] = result.stdout.strip()
        receipt = {
            'status': 'PASS', 'lean': version, 'trust_level': 0,
            'fresh_modules_compiled': len(MODULES), 'compile_seconds': timing,
            'sources': manifest['modules'], 'axioms': reports,
            'negative_controls_rejected': rejected,
            'scope': 'Two actual normalized trajectories; conditional declared-geometry contract diagnostic.',
        }
    if args.receipt:
        args.receipt.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'modules': len(MODULES),
                      'axiom_reports': len(reports), 'rejected_controls': len(rejected)}))


if __name__ == '__main__':
    main()
