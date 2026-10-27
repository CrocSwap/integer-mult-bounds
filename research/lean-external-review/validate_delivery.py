#!/usr/bin/env python3
"""Check an exported archive and apply its patch in an isolated public-base tree.

Requires a Git checkout containing the pinned public base and delivery commit.
Fresh proof reproduction is a separate command; this checks delivery integrity.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[2]


def run(command, cwd):
    return subprocess.check_output(command, cwd=cwd, stderr=subprocess.STDOUT)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def checksums(root):
    count = 0
    for line in (root / 'SHA256SUMS').read_text().splitlines():
        digest, name = line.split('  ', 1)
        path = (root / name).resolve(strict=True)
        require(path.is_relative_to(root.resolve()), 'Checksum path escapes delivery')
        require(sha(path) == digest, 'Delivery digest mismatch: ' + name)
        count += 1
    return count


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--delivery-dir', required=True, type=Path)
    p.add_argument('--receipt', required=True, type=Path)
    p.add_argument('--allow-pending-task-b', action='store_true',
                   help='check delivery integrity while reporting Task B verification as unfinished')
    a = p.parse_args()
    delivery = a.delivery_dir.resolve()
    verify_command = [sys.executable, 'research/lean-external-review/verify_package.py']
    if a.allow_pending_task_b:
        verify_command.append('--allow-pending-task-b')
    outer_count = checksums(delivery)
    metadata = json.loads((delivery / 'delivery.json').read_text())
    base, head = metadata['base_commit'], metadata['review_commit']
    require(sha(delivery / 'review.patch') == metadata['patch_sha256'], 'Patch metadata mismatch')
    with tempfile.TemporaryDirectory(prefix='lean-review-delivery-') as tmp:
        work = Path(tmp)
        with tarfile.open(delivery / 'integer-mult-lean-review.tar.gz') as archive:
            archive.extractall(work, filter='data')
        snapshot = work / 'integer-mult-lean-review'
        inner_count = checksums(snapshot)
        require((snapshot / 'delivery.json').read_bytes() == (delivery / 'delivery.json').read_bytes(),
                'Archive/external delivery metadata differ')
        require((snapshot / 'review.patch').read_bytes() == (delivery / 'review.patch').read_bytes(),
                'Archive/external patches differ')
        inventory = json.loads(run(verify_command, snapshot))
        source_binding = json.loads(run([sys.executable, 'research/lean-multi-host-source/check_sources.py'], snapshot))
        baseline = work / 'public-base'
        baseline.mkdir()
        archive_path = work / 'base.tar'
        run(['git', 'archive', '--format=tar', '--output=' + str(archive_path), base], ROOT)
        with tarfile.open(archive_path) as archive:
            archive.extractall(baseline, filter='data')
        run(['git', 'init', '--quiet'], baseline)
        run(['git', 'add', '--force', '.'], baseline)
        before = run(['git', 'write-tree'], baseline).decode().strip()
        require(before == run(['git', 'rev-parse', base + '^{tree}'], ROOT).decode().strip(),
                'Extracted baseline does not match exact public-base tree')
        run(['git', 'apply', '--check', '--index', str(delivery / 'review.patch')], baseline)
        run(['git', 'apply', '--index', str(delivery / 'review.patch')], baseline)
        after = run(['git', 'write-tree'], baseline).decode().strip()
        require(after == run(['git', 'rev-parse', head + '^{tree}'], ROOT).decode().strip(),
                'Applied patch does not reconstruct delivery commit tree')
        patched_inventory = json.loads(run(verify_command, baseline))
        require(inventory['status'] == patched_inventory['status'] == metadata['validation_status'],
                'Delivery/archive/patch validation status mismatch')
        require(inventory['task_b_verified'] == metadata['task_b_verified'],
                'Delivery Task B verification status mismatch')
        require(inventory['manifest_sha256'] == patched_inventory['manifest_sha256'],
                'Archive/patch inventory divergence')
    receipt = {
        'status': inventory['status'], 'delivery_integrity': 'PASS', 'completed_utc': datetime.now(timezone.utc).isoformat(),
        'base_commit': base, 'review_commit': head, 'base_tree': before, 'result_tree': after,
        'outer_checksums_verified': outer_count, 'archive_checksums_verified': inner_count,
        'archive_inventory': inventory, 'archive_source_binding': source_binding,
        'patch_inventory': patched_inventory,
        'artifacts_sha256': {name: sha(delivery / name) for name in
                            ['review.patch', 'integer-mult-lean-review.tar.gz', 'delivery.json']},
        'scope': 'Fresh isolated patch application, archive inventory and source regeneration; not a new Lean compilation. PENDING_TASK_B means Task B verification is unfinished.',
    }
    a.receipt.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'status': inventory['status'], 'delivery_integrity': 'PASS', 'commit': head, 'receipt': str(a.receipt)}))


if __name__ == '__main__':
    main()
