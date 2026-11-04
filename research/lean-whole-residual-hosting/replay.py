#!/usr/bin/env python3
"""Offline fresh Lean 4.33.0 kernel replay, using only Python's standard library."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
MODULES = [
    'CoordinateSwap', 'Hosting', 'PhysicalHosting', 'PinnedWindow',
    'PinnedHosting', 'BoundaryExamples', 'PhysicalExample', 'Audit',
]
# Each deliberately false equality is evaluated at explicit finite inputs.
CONTROLS = {
    'host_preservation_suffices':
        'readHost (flipHost (1, 0)) = flipHost (readHost (1, 0))',
    'overlap_is_union': '''
        bitAction fullMask (bitAction fullMask witnessStream) witnessAddress =
        bitAction (unionMask fullMask fullMask) witnessStream witnessAddress''',
    'outside_pending_is_allowed': '''
        bitAction (remainderMask (fun _ => false) fullMask)
            (bitAction fullMask witnessStream) witnessAddress =
        bitAction (fun _ => false) witnessStream witnessAddress''',
    'independent_charts_commute':
        'swapAB (otherChartCD .a) = otherChartCD (swapAB .a)',
    'omit_selected_slot': '''
        bitFactors [interval 0 8, interval 8 16, interval 16 24]
            selectedStream selectedAddress =
        bitAction pending selectedStream selectedAddress''',
    'keep_entire_pending_child': '''
        bitAction pending (bitFactors residualMasks selectedStream) selectedAddress =
        bitAction pending selectedStream selectedAddress''',
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def uncomment(source):
    """Strip this package's comments for supplementary declaration hygiene."""
    return re.sub(r'--[^\n]*', '', re.sub(r'/\-[\s\S]*?\-/', '', source))


def theorem_names(source):
    code = uncomment(source)
    namespace = re.findall(r'^namespace (\S+)\s*$', code, re.M)
    require(len(namespace) == 1, 'Expected one explicit module namespace')
    return [namespace[0] + '.' + name for name in
            re.findall(r'^theorem ([\w.]+)(?=\s|:)', code, re.M)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lean', required=True, type=Path,
                        help='installed Lean binary; no toolchain download is performed')
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    lean = args.lean.resolve(strict=True)
    env = dict(os.environ)
    for name in ('LEAN_PATH', 'LEAN_SRC_PATH'):
        env.pop(name, None)
    version = subprocess.check_output([str(lean), '--version'], env=env,
                                      text=True, timeout=30).strip()
    require(version.startswith('Lean (version 4.33.0,'), 'Lean 4.33.0 required')
    manifest = json.loads((ROOT / 'proof-manifest.json').read_text())
    sources, names = {}, []
    for module in MODULES:
        filename = module + '.lean'
        source = (ROOT / filename).read_bytes()
        require(hashlib.sha256(source).hexdigest() == manifest['sha256'][filename],
                'Source hash changed: ' + filename)
        code = uncomment(source.decode())
        require(not re.search(r'\b(sorry|admit|native_decide|unsafe)\b', code),
                'Disallowed proof escape: ' + filename)
        require(not re.search(r'^\s*(axiom|opaque)\s', code, re.M),
                'Project axioms/opaque declarations forbidden: ' + filename)
        imports = re.findall(r'^import (.+)$', code, re.M)
        require(imports == manifest['imports'][filename], 'Imports changed: ' + filename)
        require(all(x == 'Std' or x in MODULES[:MODULES.index(module)] for x in imports),
                'Unexpected external or forward import: ' + filename)
        if module != 'Audit':
            names.extend(theorem_names(source.decode()))
        sources[filename] = source
    require(names == manifest['theorems'], 'Theorem inventory changed')
    require(re.findall(r'^#print axioms (\S+)$', sources['Audit.lean'].decode(), re.M)
            == names, 'Audit must cover every named theorem exactly once')

    with tempfile.TemporaryDirectory(prefix='whole-hosting-lean-') as tmp:
        build = Path(tmp)
        env['LEAN_PATH'] = str(build)
        for filename, source in sources.items():
            (build / filename).write_bytes(source)

        def compile_file(filename, output=None):
            command = [str(lean), '-t', '0']
            if output:
                command += ['-o', output]
            command += [filename]
            return subprocess.run(command, cwd=build, env=env, text=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  timeout=60)

        compilation = {}
        for module in MODULES:
            result = compile_file(module + '.lean', module + '.olean')
            require(result.returncode == 0, module + '\n' + result.stdout)
            require('warning:' not in result.stdout, module + '\n' + result.stdout)
            compilation[module] = result.stdout
        reports = {}
        for line in compilation['Audit'].splitlines():
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
        require(list(reports) == names, 'Missing, duplicate, or extra axiom reports')
        require(len(compilation['Audit'].splitlines()) == len(names),
                'Duplicate axiom report')

        rejected = {}
        for name, statement in CONTROLS.items():
            control_source = '''import BoundaryExamples
import PinnedWindow
open WholeHosting WholeHosting.Boundary WholeHosting.PinnedBitWindow
def selectedAddress : Address (Fin 64) Bool := fun _ => (false, true)
def selectedStream : Stream (Fin 64) Bool Bool := fun a => (a ⟨24, by decide⟩).1
''' + f'theorem {name} : {statement} := by decide\n'
            (build / 'Control.lean').write_text(control_source)
            result = compile_file('Control.lean')
            require(result.returncode != 0 and
                    'Tactic `decide` proved that the proposition' in result.stdout and
                    'is false' in result.stdout,
                    'Control not mathematically rejected: ' + name + '\n' + result.stdout)
            rejected[name] = result.stdout.strip()
        receipt = {
            'status': 'PASS', 'lean': version, 'trust_level': 0,
            'source_sha256': manifest['sha256'],
            'fresh_modules_compiled': len(MODULES),
            'axioms': reports, 'negative_controls_rejected': rejected,
        }
    if args.receipt:
        args.receipt.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'compiled_modules': len(MODULES),
                      'axiom_reports': len(reports),
                      'negative_controls_rejected': len(rejected)}))


if __name__ == '__main__':
    main()
