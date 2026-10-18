"""Fresh Lean compilation; Python receipt validation is never called a kernel run."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
VERSION = 'Lean (version 4.34.1, x86_64-w64-windows-gnu, commit 5045d0056413266e57c625dcd7c365b10e377c52, Release)'
AXIOMS = {
    'CompactRepair.fill_correct': ['propext'],
    'CompactRepair.radix_perm': ['propext', 'Quot.sound'],
    'CompactRepair.guarded_repair': ['propext', 'Quot.sound'],
    'CompactRepair.guarded_compact_repair': ['propext', 'Quot.sound'],
}
FOILS = {
    'wrong_inverse_payload': 'CompactRepair.fill (fun _ => true) [0, 1] [(0, 1), (1, 0)] [] = some ([0, 1] : List Nat)',
    'wrong_destination': 'CompactRepair.fill (fun _ => true) [0] [(1, 7)] [] = some ([7] : List Nat)',
    'unconsumed_records': 'CompactRepair.fill (fun _ => true) [] [(0, 7)] [] = some ([] : List Nat)',
    'missing_good_agreement': 'CompactRepair.fill (fun _ => false) [0, 1] [] [1, 0] = some ([0, 1] : List Nat)',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def audit_output(output):
    matches = re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", output)
    found = {name: [x.strip() for x in values.split(',') if x.strip()] for name, values in matches}
    need(len(matches) == len(AXIOMS) and found == AXIOMS, 'axiom/root mismatch')
    need('sorryAx' not in output and 'warning:' not in output and 'error:' not in output, 'untrusted kernel output')
    return found


def receipt_check():
    receipt = json.loads((HERE / 'KERNEL.json').read_text(encoding='utf-8'))
    need(receipt['repair_sha256'] == hashlib.sha256((HERE / 'Repair.lean').read_bytes()).hexdigest(), 'formal source receipt mismatch')
    need(receipt['version'] == VERSION and receipt['axioms'] == AXIOMS, 'formal receipt toolchain/axioms')
    need(receipt['fresh_kernel_compile'] is True, 'formal receipt status')
    need(receipt['rejected_false_probes'] == list(FOILS) and receipt['axiom_guard_negative_control'] is True, 'formal receipt controls')
    return receipt


def run(lean):
    lean = Path(lean).resolve(strict=True)
    version = subprocess.run([str(lean), '--version'], text=True, capture_output=True, check=True).stdout.strip()
    need(version == VERSION, 'pinned Lean version required; receipt is platform-specific')
    source = (HERE / 'Repair.lean').read_bytes()
    need(not re.search(rb'\b(sorry|axiom|admit|native_decide)\b', source), 'forbidden proof escape')
    with tempfile.TemporaryDirectory(prefix='compact-repair-lean-') as tmp:
        folder = Path(tmp)
        def compile_file(name, data):
            (folder / name).write_bytes(data)
            return subprocess.run([str(lean), name], cwd=folder, text=True, capture_output=True, timeout=120)
        result = compile_file('Repair.lean', source)
        need(result.returncode == 0, result.stdout + result.stderr)
        axioms = audit_output(result.stdout)
        rejected = []
        for label, proposition in FOILS.items():
            foil = source + ('\nexample : ' + proposition + ' := by decide\n').encode()
            answer = compile_file(label + '.lean', foil)
            need(answer.returncode != 0 and 'Tactic `decide` proved that the proposition' in answer.stdout and 'is false' in answer.stdout, 'false proposition not rejected: ' + label + '\n' + answer.stdout)
            rejected.append(label)
        try:
            audit_output(result.stdout.replace('[propext]', '[propext, sorryAx]', 1))
        except ValueError:
            pass
        else:
            raise ValueError('axiom control accepted')
    return {'repair_sha256': hashlib.sha256(source).hexdigest(), 'version': version,
            'axioms': axioms, 'fresh_kernel_compile': True, 'rejected_false_probes': rejected,
            'axiom_guard_negative_control': True,
            'limits': 'Std toolchain trusted; no Python-to-Lean verified translation, total-completion theorem, physical cost theorem or Mathlib bridge.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lean', required=True)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.out:
        need(not args.out.exists(), 'refuse receipt overwrite')
    result = run(args.lean)
    if args.out:
        with args.out.open('x', encoding='utf-8', newline='\n') as dest:
            json.dump(result, dest, indent=2, sort_keys=True)
            dest.write('\n')
    else:
        need(result == receipt_check(), 'fresh kernel receipt mismatch')
    print('PASS_COMPACT_REPAIR_KERNEL roots=4 false_probes=4 axiom_control=1')


if __name__ == '__main__':
    main()
