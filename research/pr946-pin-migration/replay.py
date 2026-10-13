#!/usr/bin/env python3
"""Offline PR946 source-pin conflict and source-preserving PR950 replay.

Python 3.11+; standard library only. Every audit/admission uses a fresh isolated
interpreter and a disposable source closure. No Git command or network access
is needed. The vendored proposal bytes are checked against batch952's original
content-coverage record; none are imported or executed in the working tree.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import platform
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = 'research/central-factor-packed'
MANIFEST = PACKAGE + '/SOURCES.json'
COVERAGE = 'research/community-batch952-audit/CONTENT-COVERAGE.json'
BASE = '407d52ff15b2217b6e22bce44728b4c3907b6515'
PROPOSAL = 'b6e22dbf548d72f18b722ccb6c2ea8e3d9df6ac1'
MANIFEST_SHA256 = 'cc1165946c6469f8873ad4fcf8be6698b210411c300314dde8a0319f9b1ad7df'
COVERAGE_SHA256 = '5a50ca8c71f1d02bf4bae64f1a5e23eae9168e4e5c592358f3d744ad2be7e76a'
CONFLICTS = (
    'certificates/dyadic-central-factor.json',
    'scripts/audit_complex_centers.py',
    'scripts/certify.py',
    'scripts/complex_compression.py',
    'scripts/paired_network.py',
    'scripts/prepare_layers.py',
    'scripts/search_network.py',
    'scripts/shared_point_network.py',
)
ADMIT = (
    'import json,runpy,sys; '
    'p=runpy.run_path(sys.argv[1])["admit_sources"](); '
    'print(json.dumps({"status":"PASS_SOURCE_ADMISSION",'
    '"source_files":len(p["files"])}))'
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pinned_bytes(path, expected):
    raw = path.read_bytes()
    require(sha(raw) == expected, 'Replay input pin mismatch: ' + str(path))
    return raw


def safe_path(root, name):
    relative = PurePosixPath(name)
    require(not relative.is_absolute() and '..' not in relative.parts and
            '\\' not in name and ':' not in name, 'Invalid relative path: ' + name)
    return root.joinpath(*relative.parts)


def write(root, name, raw):
    path = safe_path(root, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def closure_hashes(root):
    return {path.relative_to(root).as_posix(): sha(path.read_bytes())
            for path in sorted(root.rglob('*')) if path.is_file()}


def invoke(root, admission=False, rejected_path=None):
    verifier = str(root / PACKAGE / 'verify.py')
    arguments = ['-c', ADMIT, verifier] if admission else [verifier]
    started = time.perf_counter()
    process = subprocess.run(
        [sys.executable, '-I', '-B', *arguments], cwd=root,
        capture_output=True, text=True, encoding='utf-8', timeout=120)
    elapsed = time.perf_counter() - started
    if rejected_path is not None:
        expected = 'ValueError: Source pin mismatch: ' + rejected_path
        last_line = process.stderr.strip().splitlines()[-1:]
        require(process.returncode != 0 and last_line == [expected],
                'Expected exact source-admission rejection for ' + rejected_path +
                ', got exit ' + str(process.returncode) + ': ' + process.stderr)
        require(not process.stdout.strip(), 'Rejected replay emitted a result')
        return dict(status='EXPECTED_SOURCE_PIN_REJECTION',
                    invocation='admission' if admission else 'full_audit',
                    rejected_path=rejected_path, exception=expected,
                    process_exit_code=process.returncode, wall_seconds=elapsed)
    require(process.returncode == 0,
            'Original/restored replay failed: ' + process.stderr)
    result = json.loads(process.stdout)
    expected_status = 'PASS_SOURCE_ADMISSION' if admission else 'PASS_CENTRAL_FACTOR_PACKED'
    require(result['status'] == expected_status, 'Unexpected replay status')
    require(result['source_files'] == 43, 'Unexpected inherited source count')
    if not admission:
        require(result['scope'] == 'complete_historical_audit' and
                result['engine'] == 'packed' and
                result['coefficients_checked'] == 2600**2 and
                result['source_manifest_sha256'] == MANIFEST_SHA256,
                'Full historical replay result is incomplete')
    result['wall_seconds'] = elapsed
    if process.stderr.strip():
        result['interpreter_diagnostics'] = process.stderr.strip().splitlines()
    return result


def replay(scratch_parent=None):
    require(__debug__, 'Run this replay without Python -O')
    started = time.perf_counter()
    manifest_raw = pinned_bytes(ROOT / MANIFEST, MANIFEST_SHA256)
    coverage_raw = pinned_bytes(ROOT / COVERAGE, COVERAGE_SHA256)
    pins = json.loads(manifest_raw)
    coverage = json.loads(coverage_raw)['pull_requests']['946']
    require(coverage['head'] == PROPOSAL and coverage['changed_files'] == 165,
            'Unexpected PR946 coverage record')
    records = {item['source_path']: item for item in coverage['files']}
    require(len(records) == 165, 'Duplicate or missing PR946 coverage records')
    overlaps = tuple(sorted(set(pins['files']) & records.keys()))
    require(overlaps == CONFLICTS, 'PR946 / PR950 overlap set changed')
    original = {name: pinned_bytes(safe_path(ROOT, name), expected)
                for name, expected in pins['files'].items()}
    original[MANIFEST] = manifest_raw
    for name, expected in pins['adapter_files'].items():
        full_name = PACKAGE + '/' + name
        original[full_name] = pinned_bytes(safe_path(ROOT, full_name), expected)
    require(len(original) == 46, 'Unexpected complete closure size')
    proposed = {}
    input_records = []
    for name in overlaps:
        record = records[name]
        require(record['action'] == 'pending', 'Proposal already integrated: ' + name)
        raw = pinned_bytes(safe_path(HERE / 'inputs/pr946', name),
                           record['source_sha256'])
        require(raw != original[name], 'Expected actual byte conflict: ' + name)
        proposed[name] = raw
        input_records.append(dict(path=name, historical_sha256=sha(original[name]),
                                  proposed_sha256=sha(raw),
                                  original_bytes=len(original[name]), proposed_bytes=len(raw)))
    expected_receipt = pins['files']['certificates/dyadic-central-factor.json']
    scratch_parent = Path(scratch_parent or tempfile.gettempdir()).resolve()
    require(scratch_parent.is_dir(), 'Scratch parent must be an existing directory')
    with tempfile.TemporaryDirectory(prefix='pr946-pin-migration-',
                                     dir=scratch_parent) as temporary:
        root = Path(temporary).resolve()
        require(root.parent == scratch_parent, 'Unexpected temporary directory location')
        for name, raw in original.items():
            write(root, name, raw)
        original_hashes = closure_hashes(root)
        original_admission = invoke(root, admission=True)
        original_audit = invoke(root)
        require(original_audit['receipt_sha256'] == expected_receipt,
                'Original receipt SHA256 mismatch')
        require(closure_hashes(root) == original_hashes, 'Original audit mutated its inputs')

        # Isolate every conflict; failure on the first combined pin does not
        # demonstrate admission sensitivity to the remaining seven inputs.
        controls = []
        for name, raw in proposed.items():
            write(root, name, raw)
            try:
                controls.append(invoke(root, admission=True, rejected_path=name))
            finally:
                write(root, name, original[name])
            require(closure_hashes(root) == original_hashes,
                    'Single-file control did not restore the closure')

        for name, raw in proposed.items():
            write(root, name, raw)
        overlaid_hashes = closure_hashes(root)
        changed = sorted(name for name in original_hashes
                         if original_hashes[name] != overlaid_hashes.get(name))
        require(changed == list(CONFLICTS) and
                overlaid_hashes.keys() == original_hashes.keys(),
                'Overlay changed more than the eight proposed inputs')
        first_mismatch = next(name for name in pins['files'] if name in proposed)
        overlay_admission = invoke(root, admission=True, rejected_path=first_mismatch)
        overlay_audit = invoke(root, rejected_path=first_mismatch)
        require(closure_hashes(root) == overlaid_hashes, 'Rejected audit mutated inputs')

        # Restoring generators alone is insufficient: retain the proposed
        # receipt after restoring all seven scripts, and demand rejection.
        fixture = 'certificates/dyadic-central-factor.json'
        for name in proposed:
            if name != fixture:
                write(root, name, original[name])
        partial_hashes = closure_hashes(root)
        require([name for name in original_hashes
                 if original_hashes[name] != partial_hashes[name]] == [fixture],
                'Receipt-only control changed unexpected inputs')
        receipt_only_control = invoke(root, rejected_path=fixture)
        require(closure_hashes(root) == partial_hashes,
                'Receipt-only rejection mutated inputs')

        # Keep the original bytes and the original verifier/manifest/fixture.
        # Restoring this whole source namespace models an archival closure.
        for name in proposed:
            write(root, name, original[name])
        require(closure_hashes(root) == original_hashes, 'Historical closure not restored')
        restored_admission = invoke(root, admission=True)
        restored_audit = invoke(root)
        require(restored_audit['receipt_sha256'] == expected_receipt,
                'Restored receipt SHA256 mismatch')
        require(closure_hashes(root) == original_hashes, 'Restored audit mutated inputs')

    return dict(
        status='PASS_PR946_PIN_MIGRATION_REPLAY', repository_base=BASE,
        proposal_head=PROPOSAL, python=sys.version, platform=platform.platform(),
        source_manifest_sha256=MANIFEST_SHA256, content_coverage_sha256=COVERAGE_SHA256,
        historical_input_mode='hash-verified working-tree snapshot',
        inherited_source_files=43, copied_closure_files=46,
        preserved_package_files={name: original_hashes[name] for name in
                                 (MANIFEST, PACKAGE + '/packed.py', PACKAGE + '/verify.py')},
        proposed_inputs=input_records, original_admission=original_admission,
        original_audit=original_audit, single_file_controls=controls,
        overlay_changed_paths=changed, overlay_admission=overlay_admission,
        overlay_full_audit=overlay_audit, receipt_only_control=receipt_only_control,
        restored_admission=restored_admission,
        restored_audit=restored_audit, historical_closure_byte_identical=True,
        full_receipt_byte_identical=True, receipt_sha256=expected_receipt,
        source_and_adapter_checks_unchanged=True,
        limits=[
            'Only eight PR946 inputs in PR950 closure are overlaid; not the full 165-file patch.',
            'Proposal bytes fail source admission and are never executed by the historical audit.',
            'Restoration demonstrates retention of historical inputs, not a re-pinned migrated verifier.',
            'No semantic-equivalence, selected-frontier or whole-repository claim is made.',
        ], seconds=time.perf_counter() - started)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        help='Write a new JSON record; existing files are never replaced')
    parser.add_argument('--scratch-parent', type=Path,
                        help='Existing writable parent for disposable closure (default: system temp)')
    args = parser.parse_args()
    if args.output is not None and args.output.exists():
        parser.error('Output already exists')
    result = replay(args.scratch_parent)
    encoded = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output is not None:
        with args.output.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(encoded)
    print(encoded, end='')


if __name__ == '__main__':
    main()
