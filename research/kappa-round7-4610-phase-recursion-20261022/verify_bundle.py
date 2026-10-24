"""Fast, read-only coherence check after the fresh scoped replays.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
Use --write-manifest once after changing/replaying the bundle. No Lean compile
or finite-control replay is performed by this checker.
"""
from datetime import datetime, timezone
from hashlib import sha256
import argparse
import gzip
import importlib.util
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT / 'research/kappa-lean-verification-20261022'
AUDITOR = '6c953b31c385179f852eb4b56246e62a4084cb8906843f15fbf2724508539895'
LEAN = 'fb7a62288f197279fb84e55bb1972348fd2cce1d550845793975f1cebb0c24ab'
MATHLIB = '308445d7985027f538e281e18df29ca16ede2ba3'
MODULES = {'RankGate': 5, 'ParallelControls': 2, 'GroupedPhase': 4, 'ActivePalette': 4}
EXCLUDED = {'BUNDLE-MANIFEST.json', 'BUNDLE-CHECK.json'}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def read(name):
    return json.loads((HERE / name).read_text(encoding='utf-8'))


def bound(path, expected):
    need(digest(path) == expected, 'Hash mismatch: ' + str(path))


def validate_lean(receipt, auditor, runtime):
    need(receipt['status'] == 'PASS_SCOPED_PHASE_RECURSION_ALGEBRA', 'Lean status')
    need(receipt['new_kappa'] is False, 'Lean scope')
    need(receipt['runtime_auditor_sha256'] == AUDITOR, 'Auditor receipt pin')
    need(receipt['runtime'] == runtime, 'Runtime/dependency receipt differs')
    need(receipt['allowed_axioms'] == sorted(auditor.ALLOW), 'Allowed axiom set')
    bound(HERE / 'replay_lean.py', receipt['script_sha256'])
    rows = receipt['modules']
    need([r['module'] for r in rows] == list(MODULES), 'Module set/order')
    report_count = 0
    objects = {}
    for row in rows:
        name = row['module']
        source, log, obj = [HERE / (name + suffix) for suffix in ('.lean', '.log', '.olean')]
        need(row['exit_code'] == 0, 'Compile exit: ' + name)
        bound(source, row['source_sha256'])
        bound(log, row['log_sha256'])
        bound(obj, row['olean_sha256'])
        expected = auditor.audit_source(source)
        need(len(expected) == MODULES[name], 'Actual source report count: ' + name)
        actual = auditor.parse_axioms(log, expected)
        need(actual == row['axioms'], 'Actual log reports differ: ' + name)
        report_count += len(actual)
        objects[obj.name] = row['olean_sha256']
    need(report_count == receipt['exported_reports'] == 15, 'Actual exported report count')
    for path, expected in receipt['inputs_sha256'].items():
        bound(ROOT / path, expected)
    return report_count, objects


def validate_controls():
    route = read('GROUPED-ROUTE.json')
    need(route['status'] == 'PASS_SCOPED_GROUPED_ROUTE_AND_RANK_CONTROLS', 'Route status')
    need(route['new_kappa'] is False, 'Route scope')
    bound(HERE / 'grouped_route.py', route['script_sha256'])
    match = route['matching']
    need(match['cases'] == 93312 and match['endpoint_and_dirty_restoration'] is True, 'Route count/restoration')
    need((match['swaps'], match['rotations']) == (12, 10), 'Route macro invoice')
    need(match['overlapping_guard_window_control']['rejected'] is True, 'Same-rho rejection control')
    need(route['permutation']['permutations'] == 46233, 'Permutation count')
    need(route['permutation']['parallel_control_layers'] == 6, 'Permutation invoice')
    need(route['rank']['nonzero_pauli_transvections'] == 5454, 'Transvection count')
    need(route['rank']['global_vs_tensor'] == [dict(columns=f, global_phase_defect_rank=1,
         tensor_transvection_defect_rank=f) for f in range(1, 33)], 'Global/tensor rank controls')
    palette = read('ACTIVE-PALETTE.json')
    need(palette['status'] == 'PASS_SCOPED_ACTIVE_PAULI_PALETTE', 'Palette status')
    need(palette['new_kappa'] is False, 'Palette scope')
    bound(HERE / 'active_palette.py', palette['script_sha256'])
    need((palette['rank_and_kernel_cases'], palette['actual_registered_frames'],
          palette['actual_unit_cancellations']) == (1023, 18, 32), 'Palette control counts')
    for path, expected in palette['input_sha256'].items():
        bound(ROOT / Path(path.replace('\\', '/')), expected)
    word = ROOT / 'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
    raw = gzip.decompress(word.read_bytes())
    need(sha256(raw).hexdigest() == palette['actual_word_canonical_sha256'], 'Actual word payload')
    frames = json.loads(raw)['canonical']['frames']
    need(len(palette['frames']) == 18, 'Palette frame list')
    unit_count = 0
    for row in palette['frames']:
        basis, rank = frames[row['frame']], row['rank']
        need(basis == row['registered_basis'] and len(basis) == rank, 'Actual registered frame binding')
        masks = list(dict.fromkeys([0] + ([1, 1 << (rank - 1), (1 << rank) - 1] if rank else [])))
        need([r['mask'] for r in row['recipes']] == masks, 'Palette recipe masks')
        for recipe in row['recipes']:
            weight = recipe['mask'].bit_count()
            need(recipe['active_weight'] == weight and recipe['fourier_rank'] == rank - weight % 2,
                 'Palette rank/weight receipt')
            need(bool(recipe['literal_circuit']), 'Missing actual operator recipe')
            unit_count += weight == 1
    need(unit_count == 32, 'Actual unit recipe count')
    return {'dirty_route_cases': 93312, 'permutations': 46233, 'transvections': 5454,
            'palette_kernel_cases': 1023, 'registered_frames': 18, 'unit_cancellations': 32}


def bundle_files():
    return sorted(p for p in HERE.iterdir() if p.is_file() and p.name not in EXCLUDED
                  and p.suffix != '.olean')


def negative_controls(receipt, auditor, runtime):
    # Exercise the same reader against in-memory false receipts, without
    # modifying the pinned sources, logs, objects, or successful receipt.
    cases = [('source', lambda r: r['modules'][0].update(source_sha256='0' * 64)),
             ('log', lambda r: r['modules'][1].update(log_sha256='0' * 64)),
             ('object', lambda r: r['modules'][2].update(olean_sha256='0' * 64)),
             ('report-count', lambda r: r.update(exported_reports=11)),
             ('custom-axiom', lambda r: r['modules'][3]['axioms'][0]['axioms'].append('untrusted'))]
    rejected = []
    for name, corrupt in cases:
        trial = json.loads(json.dumps(receipt))
        corrupt(trial)
        try:
            validate_lean(trial, auditor, runtime)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('False receipt accepted: ' + name)
    return rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-manifest', action='store_true')
    args = parser.parse_args()
    need(sys.version_info[:2] == (3, 14), 'Global Python 3.14 required')
    began = time.monotonic()
    helper = OLD / 'verify_lean.py'
    bound(helper, AUDITOR)
    spec = importlib.util.spec_from_file_location('phase_bundle_pinned_auditor', helper)
    auditor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(auditor)
    lean, _, runtime = auditor.environment(str(OLD / '.toolchain/lean-4.21.0-windows/bin/lake.exe'))
    bound(lean, LEAN)
    need(runtime['mathlib_revision'] == MATHLIB, 'Mathlib runtime pin')
    receipt = read('LEAN-PHASE-RECURSION.json')
    reports, objects = validate_lean(receipt, auditor, runtime)
    controls = validate_controls()
    rejected = negative_controls(receipt, auditor, runtime)
    files = {p.name: digest(p) for p in bundle_files()}
    manifest = dict(author='Cao Yifan', format_version=1, new_kappa=False,
                    files_sha256=files, local_ignored_objects_sha256=objects,
                    frozen_inputs_sha256=receipt['inputs_sha256'],
                    actual_lean_reports=reports, finite_control_counts=controls,
                    scope='Artifact coherence and existing scoped reports; no fresh compilation, finite replay, machine theorem, or new kappa.')
    if args.write_manifest:
        (HERE / 'BUNDLE-MANIFEST.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n',
                                                   encoding='utf-8', newline='\n')
    need(read('BUNDLE-MANIFEST.json') == manifest, 'Bundle manifest differs; replay then explicitly refresh it')
    result = dict(status='PASS_SCOPED_PHASE_BUNDLE_COHERENCE', author='Cao Yifan', new_kappa=False,
                  actual_lean_reports=reports, modules=len(MODULES), finite_control_counts=controls,
                  negative_receipts_rejected=rejected, runtime=runtime,
                  manifest_sha256=digest(HERE / 'BUNDLE-MANIFEST.json'),
                  checker_sha256=digest(__file__),
                  scope=manifest['scope'])
    if args.write_manifest:
        result['completed_utc'] = datetime.now(timezone.utc).isoformat()
        (HERE / 'BUNDLE-CHECK.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n',
                                               encoding='utf-8', newline='\n')
    else:
        previous = read('BUNDLE-CHECK.json')
        previous.pop('completed_utc', None)
        need(previous == result, 'Bundle check receipt differs')
    print(result['status'], len(files), len(objects), reports, len(rejected), round(time.monotonic() - began, 3), flush=True)


if __name__ == '__main__':
    main()
