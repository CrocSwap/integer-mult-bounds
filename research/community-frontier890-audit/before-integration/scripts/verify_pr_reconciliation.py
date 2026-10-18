#!/usr/bin/env python3
"""Check immutable snapshot, subsequent family rounds and incorporation receipts.

Offline integrity check, not a mathematical verifier or a live GitHub-state check.
"""
from pathlib import Path
import hashlib
import tempfile
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / 'research/pr-reconciliation-20261012'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_family_decision(item, decision):
    """Bind projected ledger state to its authoritative, pinned family decision."""
    fields = ('number', 'reviewed_head', 'current_head', 'disposition',
              'github_state', 'integration_location', 'unresolved_question', 'closure')
    for field in fields + ('review_completion', 'verification_evidence'):
        if field in fields or field in decision:
            # JSON equality must distinguish true from 1, including nested flags.
            require(field in item and json.dumps(item[field], sort_keys=True) ==
                    json.dumps(decision[field], sort_keys=True),
                    f'#{decision["number"]}: ledger differs from family decision: {field}')


def check_review_completion(item, decision):
    """An incorporated disposition must not outrun its source/execution/publication record."""
    flags = decision['review_completion']
    required = {'changed_file_coverage', 'scoped_mechanism_review',
                'required_execution_complete', 'published'}
    require(set(flags) == required and all(type(v) is bool for v in flags.values()),
            'Invalid review-completion flags')
    require(item.get('review_completion') == flags and
            item.get('verification_evidence') == decision['verification_evidence'],
            'Ledger lost detailed review or evidence state')
    require(decision['verification_evidence'], 'Missing contribution evidence')
    if item['disposition'] == 'incorporated':
        require(all(flags.values()), 'Incorporated before review, execution or publication completed')
        require(item['reviewed_head'] == item['current_head'],
                'Incorporated current head differs from reviewed head')
        require(item['integration_location'], 'Incorporated without integration location')


def check_archived_files(root, records):
    """Verify the archived artifacts named by a separately pinned evidence inventory."""
    for record in records:
        require(record.get('files'), 'Empty replay evidence inventory')
        for name, digest in record['files'].items():
            path = (root / name).resolve()
            require(path.is_relative_to(root.resolve()) and path.is_file(),
                    'Invalid replay evidence path: ' + name)
            require(hashlib.sha256(path.read_bytes()).hexdigest() == digest,
                    'Changed archived replay artifact: ' + name)


def archive_inventory(package, manifest):
    """Check immutable ZIP pins and hash every Git blob without buffering the ZIP.

    A temporary file supplies the seekability required by ZipFile. Reading each
    member through EOF preserves ZIP CRC checks; both actual lengths and the
    complete compressed archive SHA256 remain checked. No extraction occurs.
    """
    chunk_size = 1024 * 1024
    archive = {}
    with tempfile.TemporaryFile() as spool:
        archive_hash = hashlib.sha256()
        for item in manifest['parts']:
            part_hash = hashlib.sha256()
            size = 0
            with (package / item['file']).open('rb') as part:
                while chunk := part.read(chunk_size):
                    size += len(chunk)
                    part_hash.update(chunk)
                    archive_hash.update(chunk)
                    spool.write(chunk)
            require(size == item['bytes'], 'Archive part size')
            require(part_hash.hexdigest() == item['sha256'], 'Archive part digest')
        require(archive_hash.hexdigest() == manifest['archive_sha256'], 'Archive digest')
        spool.seek(0)
        with zipfile.ZipFile(spool) as z:
            for name in z.namelist():
                # Name lookup deliberately retains the original duplicate-name
                # semantics (last entry wins); the immutable ZIP pin is unchanged.
                info = z.getinfo(name)
                blob = hashlib.sha1(b'blob ' + str(info.file_size).encode() + b'\0')
                size = 0
                with z.open(name) as member:
                    while chunk := member.read(chunk_size):
                        size += len(chunk)
                        blob.update(chunk)
                require(size == info.file_size, 'Archive member size')
                archive[name] = blob.hexdigest()
    require(len(archive) == manifest['files'], 'Archive file count')
    return archive


def main():
    ledger = json.loads((ROOT / 'docs/research/pr-ledger.json').read_text())
    snapshot = json.loads((AUDIT / 'starting-snapshot.json').read_text())
    expected = {p['number']: p for p in snapshot['pull_requests']}
    family_decisions = {}
    for family_path in (ROOT / 'research/community-family533-audit/DISPOSITIONS.json',
                        ROOT / 'research/community-family588-audit/DISPOSITIONS.json',
                        ROOT / 'research/community-hyperplane599-audit/DISPOSITIONS.json',
                        ROOT / 'research/community-cold617-audit/DISPOSITIONS.json',
                        ROOT / 'research/community-k492-audit/DISPOSITIONS.json',
                        ROOT / 'research/community-frontier741-audit/DISPOSITIONS.json',
                        ROOT / 'research/community-frontier799-audit/DISPOSITIONS.json'):
        if not family_path.exists():
            continue
        family = json.loads(family_path.read_text())
        numbers = [p['number'] for p in family['pull_requests']]
        require(len(numbers) == len(set(numbers)), 'Duplicate family PR')
        for row in family['pull_requests']:
            # The generator applies later rounds in this order; retain the final
            # authoritative projection without rewriting historical metadata.
            family_decisions[row['number']] = row
            if row['number'] not in expected:
                expected[row['number']] = row['metadata']
    actual = {p['number']: p for p in ledger['pull_requests']}
    require(len(actual) == len(ledger['pull_requests']) == len(expected), 'Duplicate or missing PR')
    require(actual.keys() == expected.keys(), 'Starting PR set changed')
    for number, decision in family_decisions.items():
        check_family_decision(actual[number], decision)
    for number, pr in actual.items():
        require(pr['starting_head'] == expected[number]['headRefOid'], f'#{number}: starting head changed')
        require(pr['contributor'] == expected[number]['author'], f'#{number}: attribution changed')
        require(pr['disposition'] in {'unreviewed', 'partially_reviewed', 'changed_since_review',
                                     'incorporated', 'superseded'}, f'#{number}: unknown disposition')
        if pr['disposition'] not in ('incorporated', 'superseded'):
            require(bool(pr['unresolved_question']), f'#{number}: missing remaining question')
    for path, digest in ledger['source_sha256'].items():
        require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, f'Stale source: {path}')
    package = ROOT / 'research/coordinated-frames-and-entrance-banks'
    manifest = json.loads((package / 'BASELINE.json').read_text())
    archive = archive_inventory(package, manifest)
    checks = json.loads((AUDIT / 'incorporation-checks.json').read_text())['checks']
    comparison = json.loads((AUDIT / 'content-comparison.json').read_text())
    for number, check in checks.items():
        files = json.loads((AUDIT / f'pr{number}-files.json').read_text())
        head = json.loads((AUDIT / f'pr{number}-head.json').read_text())
        require(check['head'] == head['headRefOid'] == actual[int(number)]['starting_head'], 'Head mismatch')
        require(len(files) == len({f['filename'] for f in files}) == check['changed_files'] == head['changedFiles'], 'Incomplete changed-file list')
        require(not comparison[number]['unresolved'], 'Unresolved paths in closure candidate')
        for f in files:
            require(f['status'] in ('added', 'modified'), 'Deletion/rename requires separate semantic review')
            require(archive.get(f['filename']) == f['sha'], f'#{number}: absent/different archive file {f["filename"]}')
        print(f'PASS #{number}: all {len(files)} changed files match the published historical archive')
    receipt_path = ROOT / 'docs/research/community-formal-20261012-integration.json'
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        for path, digest in receipt['receipts'].items():
            require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, f'Changed batch receipt: {path}')
        source = json.loads((ROOT / 'research/community-formal-20261012-audit/SOURCE.json').read_text())
        for path, digest in source['source_files'].items():
            require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, f'Changed reviewed source: {path}')
        for number, head in receipt['reviewed_heads'].items():
            require(actual[int(number)]['starting_head'] == head, f'#{number}: batch head mismatch')
        print('PASS formal/tooling batch: reviewed heads, source inventory and execution receipt bindings')
    receipt_path = ROOT / 'docs/research/community-family533-integration.json'
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        for path, digest in receipt['receipts'].items():
            require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest,
                    f'Changed construction-family receipt: {path}')
        source = json.loads((ROOT / 'research/community-family533-audit/SOURCE.json').read_text())
        for path, digest in source['source_files'].items():
            require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest,
                    f'Changed construction-family source: {path}')
        for number, head in receipt['reviewed_heads'].items():
            require(actual[int(number)]['current_head'] == head, f'#{number}: family head mismatch')
        closures = ROOT / 'research/community-family533-audit/CLOSURES.json'
        if closures.exists():
            for row in json.loads(closures.read_text())['closures']:
                item = actual[row['number']]
                require(item['disposition'] == 'incorporated' and item['github_state'] == row['github_state'],
                        'Closure does not match disposition')
                require(row['reviewed_head'] == item['current_head'] and row['comment_url'],
                        'Closure lacks head or explanation')
        print('PASS construction/formal family: complete source inventory, replay evidence and supported closures')
    receipt_path = ROOT / 'docs/research/community-family588-integration.json'
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        for name, digest in receipt['receipts'].items():
            require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                    f'Changed family588 receipt: {name}')
        decisions = {p['number']: p for p in json.loads(
            (ROOT / 'research/community-family588-audit/DISPOSITIONS.json').read_text())['pull_requests']}
        for name in ('BATCH1-EVIDENCE.json', 'BATCH2-EVIDENCE.json', 'SCOPED-EVIDENCE.json',
                     'PR587-STRICT-EVIDENCE.json', 'PR587-SUITE-EVIDENCE.json',
                     'PUBLIC-COLD-EVIDENCE.json'):
            evidence = json.loads((ROOT / 'research/community-family588-audit' / name).read_text())
            check_archived_files(ROOT, evidence if isinstance(evidence, list) else [evidence])
        source = json.loads((ROOT / 'research/community-family588-audit/SOURCE.json').read_text())
        for name, digest in source['source_files'].items():
            require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                    f'Changed family588 source: {name}')
        coverage = json.loads((ROOT / 'research/community-family588-audit/CONTENT-COVERAGE.json').read_text())
        require(set(coverage['pull_requests']) == set(receipt['reviewed_heads']),
                'Family588 changed-file coverage differs from reviewed PR set')
        for number, head in receipt['reviewed_heads'].items():
            item = actual[int(number)]
            require(item['reviewed_head'] == head, f'#{number}: family588 reviewed head mismatch')
            check_review_completion(item, decisions[int(number)])
            covered = coverage['pull_requests'][number]
            require(covered['head'] == head and len(covered['files']) == covered['changed_files'],
                    f'#{number}: incomplete family588 coverage')
            require(len({f['path'] for f in covered['files']}) == covered['changed_files'],
                    f'#{number}: repeated changed file')
            for f in covered['files']:
                data = (ROOT / f['path']).read_bytes()
                blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
                require(blob == f['integrated_blob'], f'#{number}: covered bytes changed: {f["path"]}')
        closures = ROOT / 'research/community-family588-audit/CLOSURES.json'
        if closures.exists():
            for row in json.loads(closures.read_text())['closures']:
                item = actual[row['number']]
                require(item['disposition'] == 'incorporated' and item['github_state'] == row['github_state'],
                        'Family588 closure does not match disposition')
                require(row['reviewed_head'] == item['current_head'] and row['comment_url'],
                        'Family588 closure lacks current-head check or explanation')
        print('PASS family588: complete changed-file coverage, source bytes, receipts and supported closures')
    for family in ('hyperplane599', 'cold617', 'k492'):
        receipt_path = ROOT / f'docs/research/community-{family}-integration.json'
        if receipt_path.exists():
            receipt = json.loads(receipt_path.read_text())
            for name, digest in receipt['receipts'].items():
                require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                        'Changed hyperplane review receipt: ' + name)
            folder = ROOT / f'research/community-{family}-audit'
            source = json.loads((folder / 'SOURCE.json').read_text())
            for name, digest in source['source_files'].items():
                require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                        'Changed hyperplane reviewed source: ' + name)
            check_archived_files(ROOT, json.loads((folder / 'COMPLETED-EVIDENCE.json').read_text()))
            coverage = json.loads((folder / 'CONTENT-COVERAGE.json').read_text())['pull_requests']
            decisions = json.loads((folder / 'DISPOSITIONS.json').read_text())['pull_requests']
            require({str(d['number']) for d in decisions} == set(receipt['reviewed_heads']) == set(coverage),
                    'Hyperplane review scope differs')
            for decision in decisions:
                n = decision['number']
                require(decision['reviewed_head'] == receipt['reviewed_heads'][str(n)], 'Hyperplane reviewed head')
                check_review_completion(actual[n], decision)
                c = coverage[str(n)]
                require(c['head'] == decision['reviewed_head'] and len(c['files']) == c['changed_files'],
                        'Incomplete hyperplane changed-file inventory')
                require(len({f['source_path'] for f in c['files']}) == c['changed_files'], 'Duplicate covered path')
                for f in c['files']:
                    if f['integrated_path'] is None:
                        require(not decision['review_completion']['changed_file_coverage'] and f['remaining'],
                                'Uncovered file in completed PR')
                    else:
                        require(hashlib.sha256((ROOT / f['integrated_path']).read_bytes()).hexdigest() == f['sha256'],
                                'Changed hyperplane integrated file: ' + f['integrated_path'])
                if decision.get('closure'):
                    closure = decision['closure']
                    require(closure['reviewed_head'] == decision['current_head'] and closure['explanation_url'],
                            'Hyperplane closure lacks exact-head explanation')
                    require(decision['disposition'] == 'incorporated' and
                            decision['github_state'] == closure['github_state'], 'Unsupported hyperplane closure')
            print('PASS hyperplane family: source coverage, scoped evidence, partial-history distinction and resolutions')
    receipt_path = ROOT / 'docs/research/community-frontier741-integration.json'
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        for name, digest in receipt['receipts'].items():
            require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                    'Changed frontier741 review evidence: ' + name)
        folder = ROOT / 'research/community-frontier741-audit'
        coverage = json.loads((folder / 'CONTENT-COVERAGE.json').read_text())['pull_requests']
        decisions = json.loads((folder / 'DISPOSITIONS.json').read_text())['pull_requests']
        require(set(coverage) == set(receipt['reviewed_heads']) == {str(d['number']) for d in decisions},
                'Frontier741 review scope differs')
        for decision in decisions:
            number = decision['number']
            row = coverage[str(number)]
            require(row['head'] == decision['reviewed_head'] == receipt['reviewed_heads'][str(number)],
                    'Frontier741 coverage head differs')
            require(len(row['files']) == row['changed_files'] == len({f['source_path'] for f in row['files']}),
                    'Frontier741 changed-file inventory incomplete')
            # Historical partial decisions remain immutable after a later review.
            check_review_completion(actual[number] if family_decisions[number] == decision else decision, decision)
            for item in row['files']:
                require(item['action'] in {'retained', 'adapted', 'excluded', 'pending'}, 'Unknown file action')
                if item['action'] == 'pending':
                    require(not decision['review_completion']['changed_file_coverage'], 'Incomplete PR marked reviewed')
                if item.get('integrated_sha256'):
                    require(hashlib.sha256((ROOT / item['integrated_path']).read_bytes()).hexdigest()
                            == item['integrated_sha256'], 'Changed integrated file: ' + item['integrated_path'])
                if item['action'] != 'retained':
                    require(bool(item.get('reason')), 'Missing adaptation or remaining scope')
        print('PASS frontier741 batch: scoped source coverage, replay evidence and projection bindings')
    receipt_path = ROOT / 'docs/research/community-frontier799-integration.json'
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        for name, digest in receipt['receipts'].items():
            require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                    'Changed frontier799 evidence: ' + name)
        folder = ROOT / 'research/community-frontier799-audit'
        coverage = json.loads((folder / 'CONTENT-COVERAGE.json').read_text())['pull_requests']
        decisions = json.loads((folder / 'DISPOSITIONS.json').read_text())['pull_requests']
        require(set(coverage) == set(receipt['reviewed_heads']) == {str(d['number']) for d in decisions},
                'Frontier799 review scope differs')
        for decision in decisions:
            number = decision['number']; row = coverage[str(number)]
            require(row['head'] == decision['reviewed_head'] == receipt['reviewed_heads'][str(number)],
                    'Frontier799 coverage head differs')
            require(len(row['files']) == row['changed_files'] == len({f['source_path'] for f in row['files']}),
                    'Frontier799 changed-file inventory incomplete')
            check_review_completion(actual[number], decision)
            for item in row['files']:
                require(item['action'] in {'retained', 'adapted', 'excluded', 'pending'}, 'Unknown file action')
                if item['action'] == 'pending':
                    require(not decision['review_completion']['changed_file_coverage'], 'Incomplete review')
                if item.get('integrated_sha256'):
                    require(hashlib.sha256((ROOT / item['integrated_path']).read_bytes()).hexdigest()
                            == item['integrated_sha256'], 'Changed integrated file: ' + item['integrated_path'])
                if item['action'] != 'retained':
                    require(bool(item.get('reason')), 'Missing scope or adaptation reason')
        print('PASS frontier799 batch: reviewed sources, finite replays, scoped claims and closure bindings')
    print(f'PASS immutable snapshot plus explicit family rounds: {len(actual)} PRs, attributed heads, evidence pins and unresolved questions')


if __name__ == '__main__':
    main()
