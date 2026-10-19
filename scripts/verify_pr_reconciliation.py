#!/usr/bin/env python3
"""Check immutable snapshot, subsequent family rounds and incorporation receipts.

Offline integrity check, not a mathematical verifier or a live GitHub-state check.
"""
from pathlib import Path
import hashlib
import tempfile
import json
import zipfile
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / 'research/pr-reconciliation-20261012'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_batch1047_file(item):
    """Preserve the Makefile prefix and exact reviewed P112 source successors.

    Batch1099 separately binds the entire current Makefile. Other historical
    source files still require their original complete byte hashes unless the
    exact successor is also bound by the historical-input ledger.
    """
    current = (ROOT / item['integrated_path']).read_bytes()
    name = item['integrated_path']
    digest = hashlib.sha256(current).hexdigest()
    if digest == item['integrated_sha256']:
        return
    # Exact live successors are also recorded in replay_historical_check.py.
    reviewed = {
        'research/p112-free-sink-audit97/README.md': (
            'c792fc8f5de0c784049904c6febf3eed9b20e2462b30dc643c72730470d72b79',
            '6924c590eaa9a954d986153fa417c3f1ee074bcb194a42c79e1e37cb69f2cd4a',
        ),
        'research/p112-free-sink-audit97/independent.py': (
            '46806efe1ee7744c810a69981d471b42dfceaa336fee226991c55ba1edfd129f',
            'c77cf3dd1234c26cfb7df2d356752721e8b1b37169f20543678fe2f4d07a53f8',
        ),
    }
    if name in reviewed:
        predecessor, successor = reviewed[name]
        require(item['integrated_sha256'] == predecessor, 'Changed historical P112 pin: ' + name)
        require(digest == successor, 'Changed integrated file: ' + name)
        return
    require(name == 'Makefile', 'Changed integrated file: ' + name)
    original = (ROOT / 'research/community-batch1099-audit/checkpoints/Makefile1047').read_bytes()
    require(hashlib.sha256(original).hexdigest() == item['integrated_sha256'], 'Changed historical Makefile')
    require(original.endswith(b'\n') and current.startswith(original), 'Historical Makefile content changed')


def check_frontier890_file(item):
    """Authenticate the exact spectrum pin refresh accepted in 02c46c7e.

    Preserve the frozen frontier890 receipt. Sagar Thakrar's refresh changed
    only the single_intersection.py source digest in SOURCE.json and RESULT.json;
    every other byte, including all 41 mathematical cases, must still match.
    Dennis with substantial OpenAI Codex assistance; Apache-2.0.
    """
    name = item['integrated_path']
    current = (ROOT / name).read_bytes()
    if hashlib.sha256(current).hexdigest() == item['integrated_sha256']:
        return
    if name == 'scripts/verify_complex741_parallel.py':
        check_reviewed_family_source(name, item['integrated_sha256'])
        return
    predecessors = {
        'research/single-intersection-spectrum-audit/RESULT.json':
            '9cb2210e148b2cce3fe59cf529fbf99f3b663dc7673db2e3969246595692f580',
        'research/single-intersection-spectrum-audit/SOURCE.json':
            '610fb9887add31b4f597a39dc58b3beff0e14c91a5fd7ee340c3b2e7d4b0fb4c',
    }
    require(name in predecessors and item['integrated_sha256'] == predecessors[name],
            'Changed integrated file: ' + name)
    old = b'08ddae46e5621a5b4c525b504e67ae655abe9b49461d894feaa7abc89a51847d'
    new = b'6874d41b75590369182ed61e0c6da5b547e035e0e43b50ea2b39e1f3861dca6d'
    source = 'scripts/experiments/single_intersection.py'
    require(hashlib.sha256((ROOT / source).read_bytes()).hexdigest().encode() == new,
            'Changed spectrum successor source')
    require(json.loads(current)['source_sha256'][source].encode() == new
            and current.count(new) == 1, 'Changed spectrum source pin')
    require(hashlib.sha256(current.replace(new, old)).hexdigest() == predecessors[name],
            'Changed spectrum evidence beyond the accepted source pin')


def check_batch932_file(item):
    """Bind exact assertion-safety and historical replay runner successors.

    Credit woklerx for keeping assertions enabled in child research processes.
    These exact successor blobs are an explicit maintenance adaptation,
    not permission to change any other bytes or the frozen batch932 receipt.
    Also authenticate the exact PR53 replay adapter and its test from c58c1778;
    this extension retains the earlier assertion guard and every module.
    Also bind the exact complete legacy-family routing and its failure test,
    plus the reviewed production data-corner evidence refresh.
    """
    name = item['integrated_path']
    digest = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    if digest == item['integrated_sha256']:
        return
    successors = {
        'scripts/run_isolated_tests.py': (
            '96ea543e6c707424afe247e77bd86c82152f90fc76a0773c4232145da5cdf8d1',
            ('b1c645e815a6abfbfdc2d77c4121c543ed0ca958095e97e1181d64e84cac0ed8',
             '05839996482058359b2ab8087d7d96e76934bd03d79981df9b99447e8ed09331',
             'fdc022f70e42a9b5a2be8c6c3645cfdc211c6dffdffac68904b2945b1cdc3e5a', 'f569b1c287252c698b4d59bc1bd0f013159e772cc3be64e26c4eab8eb99d0478', '6f353dae3f922d78f62bedddcb50cfe2b500b4195a888cec5ffac2367b1a4f88', '2bcc91541d4c328e9ca329aa02516836dc55fe326299ad6ecee6439f5806f6aa', '8f9298eb83184a447ee2dda64a42dfc5a56df08e4affae56f99974cad632713a',
             # Descendants inherit the module's private cache namespace.
             'ef5035e6216d39569da670f32b2717c870b23c418016fd134cc0a72649fb912a')),
        'tests/test_isolated_test_runner.py': (
            '628391b6abfbc8674ceec1751867a4392f2cc0b5b66886243e139af86cf355ac',
            ('8262f36202e426b849a925123ff789843115d5e564962710c31ab14f84c88067',
             '6f5ad20a5f174be0aab874cf524cba01c5401dafa46dd176999bad43ab566522',
             '5c2a715a66c0c87fd672ce46889cb878dd7017a8bfa0c44395b340306b1b5382', '3638fb4a6233475d1984568a5027b57af30f0dbcce9a22d3c459cef4f7716aa7', '8188e0ff7755bf72dfcd8728413cbda9793d3d7913507f7a9831f91e19ab93b8')),
        'research/data-corner-performance/README.md': (
            'eaa548973e42e1ca6695fb3d6a8ae3c738ff29a5c4ccd053c9bf44f6eacb545c',
            ('6e8b28070731ab42fca90519f16eb17f9a19b86362b2b8533fa2ddcb2bdd6e0c',)),
        'research/data-corner-performance/SOURCE.json': (
            'ceda6f692682d98f7a4bc258717764ea2b549304b5808ba380f7ee48783dcb53',
            ('513628ac6fc4941c7bf2f9b890099ed163d9f2521f4461d3f42f07773d04eef1',)),
        'research/data-corner-performance/replay.py': (
            'ce7cceeabb816d4a70aaa6352d5ba0432ac7dea4f66f903e3af4fa91aa44c822',
            ('eb96c629a8732216fc1bf6243ada832d0041b467ede3af7a70e07783900694ba',)),
        'research/data-corner-performance/test_replay.py': (
            '5f134d0cf4e3c4b79e0aa274117523582badbe8e6431554832f0277bb644724e',
            ('0c7ab29c0f5628ec1943501f79f6144d2d474efd837c44dbb9ee5dd97b569ad1',)),
    }
    require(name in successors and successors[name][0] == item['integrated_sha256']
            and digest in successors[name][1],
            'Changed integrated file: ' + name)


def check_reviewed_family_source(name, digest):
    """Keep historical pins while accepting exact, separately reviewed successors."""
    current = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    if current == digest:
        return
    successor = {
        'scripts/verify_hpe_lean_binding.py': (
            '52aa1d23641e4c716b43c98f6b883ad042087dd03a9d01369e8e6a735b07aa03',
            '2fe5aac5828b1fdb79ff5e9ba87faef4db77e0c9339f362a1775b498a6d59e13',
        ),
        'research/complex-k492-owner-repair/code/hpe_audit_and_transport.py': (
            'c9a05ff291016b870b4fc925b317abd9c3a604c73ffc8920dfdbbeb475e20aa3',
            'd777db4abe316594df5cd3dc1269b42f4af4a8c87d4d0df500d32655e3775b87',
        ),
        'research/complex-factory5-resynthesis/SOURCE-PINS.json': (
            '79e00db34b721dc38830a7816f3126a09615d49c12f1b6a630147f1f50378f63',
            '9581d53e525c4f7f7a6e9bd96c02814cb3ab7be7734c5de3c42cc74042df8718',
        ),
        'research/complex-factory5-resynthesis/verify.py': (
            'edbae43b68c0e4f65978a2f9b9a739867128f4ef19d8bbe81d06ed2e5bc165f1',
            '90c917080f577f24390b1ba8ab059e052314eb0cee2cccb2e4321bcc2c6cf74a',
        ),
        'research/supplier-circuit-consolidation/SOURCES.json': (
            'ef2568aac251c94d86736936b9d8c7507d224b129da2907d1bc6a1c2b5546742',
            'ad8665bf62453b4597f798aeeec1fa9d145413dbb725f11893a5345ba5a4ee4b',
        ),
        'docs/ci-verification.md': (
            'a854022e0e1d5d4db4d60e586be3ea56005013ef14a1fc06d02bc06e8529c4b0',
            'a3711fe12d560fac7726c530b9c8c622182f3d4f231a876c163616e49bd911bc',
        ),
        'scripts/verify_selected_result.py': (
            'd7fd929726b326aeeaf0a3996475adec88eee9aac09ae0bebeeaa0bc1fc8f199',
            'c0cc23a8534d91c8d272195315c725213f13279815750ffdef055ec3adfbe911',
        ),
        'scripts/verify_complex741_parallel.py': (
            '616cff67233958647dd1e6f33dcc5ffc6132df68e0e1230dc768e820d00155a1',
            'f368e6ed6461806107ab425cbe15f5c6dc9056a2bd29a90ed75d22791744c61b',
        ),
    }
    require(name in successor and successor[name] == (digest, current),
            'Changed reviewed family source: ' + name)


def check_family_decision(item, decision):
    """Bind projected ledger state to its authoritative, pinned family decision."""
    fields = ('number', 'reviewed_head', 'current_head', 'disposition',
              'github_state', 'integration_location', 'unresolved_question', 'closure')
    for field in fields + ('review_completion', 'verification_evidence'):
        if field == 'closure' and field not in decision:
            # Intake decisions without closure metadata predate the closure projection.
            continue
        if field in fields or field in decision:
            # JSON equality must distinguish true from 1, including nested flags.
            require(field in item and json.dumps(item[field], sort_keys=True) ==
                    json.dumps(decision[field], sort_keys=True),
                    f'#{decision["number"]}: ledger differs from family decision: {field}')


def check_starting_head(item, expected_head, in_starting_snapshot):
    """Distinguish a PR's frozen first head from later family metadata."""
    if item['starting_head'] == expected_head:
        return
    # Records added after the frozen snapshot may carry a later captured head.
    # Accept that only when the ledger still preserves its original head and
    # the captured family head is the ledger's current head.
    require(not in_starting_snapshot and item['current_head'] == expected_head and
            item['starting_head'] in item.get('previously_reviewed_heads', []),
            f'#{item["number"]}: starting head changed')


def check_batch1099_file(item):
    """Authenticate the Makefile prefix and exact reviewed R439 successors."""
    current = (ROOT / item['integrated_path']).read_bytes()
    name = item['integrated_path']
    digest = hashlib.sha256(current).hexdigest()
    if digest == item['integrated_sha256']:
        return
    # Exact live successors are also recorded in replay_historical_check.py.
    reviewed = {
        'research/r439-omission-atlas-seed81/README.md': (
            '6fc756df2aa0afe5b63985c1a5b4878659a3387250092e9ae5167f3316d5de9f',
            '812fabd455a7d1f77331e59d57150f28ff8ddc6ff47f9a54c5b24970f6dcc00a',
        ),
        'research/r439-omission-atlas-seed81/verify.py': (
            '127d7679fb26e264018548a1301b2f0f437d834eb1f0ffa215556243077ff866',
            '6c3c94b01e3db5fb6d9e45eda4f60628252de1fab218e6e8233cc7949afd8966',
        ),
    }
    if name in reviewed:
        predecessor, successor = reviewed[name]
        require(item['integrated_sha256'] == predecessor, 'Changed historical R439 pin: ' + name)
        require(digest == successor, 'Changed integrated file: ' + name)
        return
    require(name == 'Makefile', 'Changed integrated file: ' + name)
    original = (ROOT / 'research/community-reconciliation92-audit/checkpoints/Makefile-before154').read_bytes()
    require(hashlib.sha256(original).hexdigest() == item['integrated_sha256'], 'Changed historical Makefile')
    require(original.endswith(b'\n') and current.startswith(original), 'Historical Makefile content changed')


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


def check_companion_review(item, companion, decision=None):
    """Keep scoped evidence; only a later authoritative whole-head review clears its hold."""
    require(item['current_head'] == companion['head'] and
            item.get('companion_reviews') == [companion],
            'Companion review lost its parent-head binding')
    flags = (decision or {}).get('review_completion', {})
    if (decision and decision['reviewed_head'] == companion['head'] and
            all(flags.get(k, False) for k in ('changed_file_coverage',
                'scoped_mechanism_review', 'required_execution_complete'))):
        check_family_decision(item, decision)
        check_review_completion(item, decision)
        return
    require(item['unresolved_question'] == companion['remaining'],
            'Companion review lost its remaining scope')
    require(item['disposition'] == 'changed_since_review' and
            item['closure'] is None and item['github_state'] == 'OPEN',
            'Companion replay incorrectly promoted whole parent PR')


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


def decision_paths(root=ROOT):
    """Authoritative family order shared by the ledger checker and its tests."""
    return (root / 'research/community-family533-audit/DISPOSITIONS.json',
            root / 'research/community-family588-audit/DISPOSITIONS.json',
            root / 'research/community-hyperplane599-audit/DISPOSITIONS.json',
            root / 'research/community-cold617-audit/DISPOSITIONS.json',
            root / 'research/community-k492-audit/DISPOSITIONS.json',
            root / 'research/community-frontier741-audit/DISPOSITIONS.json',
            root / 'research/community-frontier799-audit/DISPOSITIONS.json',
            root / 'research/community-frontier890-audit/DISPOSITIONS.json',
            root / 'research/community-batch932-audit/DISPOSITIONS.json',
            root / 'research/community-batch952-audit/DISPOSITIONS.json',
            root / 'research/community-batch970-audit/DISPOSITIONS.json',
            root / 'research/community-batch1047-audit/DISPOSITIONS.json',
            root / 'research/community-batch1099-audit/DISPOSITIONS.json',
            root / 'research/pr-reconciliation100-20261013/DISPOSITIONS.json',
            root / 'research/community-historical-five-audit/DISPOSITIONS.json',
            root / 'research/community-reconciliation92-audit/DISPOSITIONS.json',
            root / 'research/community-reconciliation-next100-audit/DISPOSITIONS.json',
            root / 'research/community-reconciliation-third100-audit/DISPOSITIONS.json',
            root / 'research/community-reconciliation-fourth100-audit/DISPOSITIONS.json',
            root / 'research/community-pilot20-audit/DISPOSITIONS.json',
            root / 'research/community-efficient100-audit/DISPOSITIONS.json',
            root / 'research/community-efficient200-audit/DISPOSITIONS.json',
            root / 'research/community-efficient300-audit/DISPOSITIONS.json',
            root / 'research/community-efficient400-audit/DISPOSITIONS.json',
            root / 'research/community-efficient500-audit/DISPOSITIONS.json',
            root / 'research/community-efficient600-audit/DISPOSITIONS.json',
            root / 'research/community-efficient700-audit/DISPOSITIONS.json',
            root / 'research/community-efficient800-audit/DISPOSITIONS.json',
            root / 'research/community-efficient900-audit/DISPOSITIONS.json',
            root / 'research/community-efficient1000-audit/DISPOSITIONS.json',
            root / 'research/community-efficient1100-audit/DISPOSITIONS.json',
            root / 'research/community-efficient1200-audit/DISPOSITIONS.json',
            root / 'research/community-efficient1300-audit/DISPOSITIONS.json',
            root / 'research/community-efficient1400-audit/DISPOSITIONS.json',
            root / 'research/community-efficient1500-audit/DISPOSITIONS.json',
            root / 'research/community-efficient1600-audit/DISPOSITIONS.json',
            root / 'research/community-efficient1700-audit/DISPOSITIONS.json',
            root / 'research/community-efficient1800-audit/DISPOSITIONS.json',
        root / 'research/community-efficient1900-audit/DISPOSITIONS.json',
            root / 'research/community-efficient2000-audit/DISPOSITIONS.json',
            root / 'research/community-efficient2100-audit/DISPOSITIONS.json',
            root / 'research/community-efficient2200-audit/DISPOSITIONS.json',
            root / 'research/community-efficient2300-audit/DISPOSITIONS.json',
            root / 'research/community-efficient2400-audit/DISPOSITIONS.json',
            root / 'research/community-efficient2500-audit/DISPOSITIONS.json',
            root / 'research/community-efficient2600-audit/DISPOSITIONS.json',
            root / 'docs/research/pr-intake-decisions.json')


def main():
    ledger = json.loads((ROOT / 'docs/research/pr-ledger.json').read_text())
    snapshot = json.loads((AUDIT / 'starting-snapshot.json').read_text())
    expected = {p['number']: p for p in snapshot['pull_requests']}
    starting_numbers = set(expected)
    family_decisions = {}
    for family_path in decision_paths():
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
        check_starting_head(pr, expected[number]['headRefOid'], number in starting_numbers)
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
                data = (ROOT / f.get('integrated_path', f['path'])).read_bytes()
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
                check_reviewed_family_source(name, digest)
            check_archived_files(ROOT, json.loads((folder / 'COMPLETED-EVIDENCE.json').read_text()))
            coverage = json.loads((folder / 'CONTENT-COVERAGE.json').read_text())['pull_requests']
            decisions = json.loads((folder / 'DISPOSITIONS.json').read_text())['pull_requests']
            require({str(d['number']) for d in decisions} == set(receipt['reviewed_heads']) == set(coverage),
                    'Hyperplane review scope differs')
            for decision in decisions:
                n = decision['number']
                require(decision['reviewed_head'] == receipt['reviewed_heads'][str(n)], 'Hyperplane reviewed head')
                # A later exact-head reconciliation can supersede this immutable partial record.
                check_review_completion(actual[n] if family_decisions[n] == decision else decision, decision)
                c = coverage[str(n)]
                require(c['head'] == decision['reviewed_head'] and len(c['files']) == c['changed_files'],
                        'Incomplete hyperplane changed-file inventory')
                require(len({f['source_path'] for f in c['files']}) == c['changed_files'], 'Duplicate covered path')
                for f in c['files']:
                    if f['integrated_path'] is None:
                        require(not decision['review_completion']['changed_file_coverage'] and f['remaining'],
                                'Uncovered file in completed PR')
                    else:
                        check_reviewed_family_source(f['integrated_path'], f['sha256'])
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
                    check_reviewed_family_source(item['integrated_path'], item['integrated_sha256'])
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
    receipt_path = ROOT / 'docs/research/community-frontier890-integration.json'
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        for name, digest in receipt['receipts'].items():
            require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                    'Changed frontier890 evidence: ' + name)
        folder = ROOT / 'research/community-frontier890-audit'
        coverage = json.loads((folder / 'CONTENT-COVERAGE.json').read_text())['pull_requests']
        decisions = json.loads((folder / 'DISPOSITIONS.json').read_text())['pull_requests']
        require(set(coverage) == set(receipt['reviewed_heads']) == {str(d['number']) for d in decisions},
                'Frontier890 review scope differs')
        for decision in decisions:
            number = decision['number']; row = coverage[str(number)]
            require(row['head'] == decision['reviewed_head'] == receipt['reviewed_heads'][str(number)],
                    'Frontier890 coverage head differs')
            require(len(row['files']) == row['changed_files'] == len({f['source_path'] for f in row['files']}),
                    'Frontier890 changed-file inventory incomplete')
            check_review_completion(actual[number], decision)
            for item in row['files']:
                require(item['action'] in {'retained', 'adapted', 'excluded', 'pending'}, 'Unknown file action')
                if item['action'] == 'pending':
                    require(not decision['review_completion']['changed_file_coverage'], 'Incomplete review')
                if item.get('integrated_sha256'):
                    check_frontier890_file(item)
                if item['action'] != 'retained':
                    require(bool(item.get('reason')), 'Missing scope or adaptation reason')
        print('PASS frontier890 batch: reviewed sources, finite replays, scoped claims and closure bindings')
    receipt_path = ROOT / 'docs/research/community-batch932-integration.json'
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        for name, digest in receipt['receipts'].items():
            require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                    'Changed batch932 evidence: ' + name)
        folder = ROOT / 'research/community-batch932-audit'
        coverage = json.loads((folder / 'CONTENT-COVERAGE.json').read_text())['pull_requests']
        decisions = json.loads((folder / 'DISPOSITIONS.json').read_text())['pull_requests']
        require(set(coverage) == set(receipt['reviewed_heads']) == {str(d['number']) for d in decisions},
                'Batch932 review scope differs')
        for decision in decisions:
            number = decision['number']; row = coverage[str(number)]
            require(row['head'] == decision['reviewed_head'] == receipt['reviewed_heads'][str(number)],
                    'Batch932 coverage head differs')
            require(len(row['files']) == row['changed_files'] == len({f['source_path'] for f in row['files']}),
                    'Batch932 changed-file inventory incomplete')
            check_review_completion(actual[number], decision)
            for item in row['files']:
                require(item['action'] in {'retained', 'adapted', 'excluded', 'pending'}, 'Unknown file action')
                if item['action'] == 'pending':
                    require(not decision['review_completion']['changed_file_coverage'], 'Incomplete review')
                if item.get('integrated_sha256'):
                    check_batch932_file(item)
                if item['action'] != 'retained':
                    require(bool(item.get('reason')), 'Missing scope or adaptation reason')
        print('PASS batch932 batch: reviewed sources, finite replays, scoped claims and closure bindings')
    receipt_path = ROOT / 'docs/research/community-batch952-integration.json'
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        for name, digest in receipt['receipts'].items():
            require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                    'Changed batch952 evidence: ' + name)
        folder = ROOT / 'research/community-batch952-audit'
        coverage = json.loads((folder / 'CONTENT-COVERAGE.json').read_text())['pull_requests']
        decisions = json.loads((folder / 'DISPOSITIONS.json').read_text())['pull_requests']
        require(set(coverage) == set(receipt['reviewed_heads']) == {str(d['number']) for d in decisions},
                'Batch952 review scope differs')
        for decision in decisions:
            number = decision['number']; row = coverage[str(number)]
            require(row['head'] == decision['reviewed_head'] == receipt['reviewed_heads'][str(number)],
                    'Batch952 coverage head differs')
            require(len(row['files']) == row['changed_files'] == len({f['source_path'] for f in row['files']}),
                    'Batch952 changed-file inventory incomplete')
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
        print('PASS batch952 batch: reviewed sources, finite replays, scoped claims and closure bindings')
    receipt_path = ROOT / 'docs/research/community-batch970-integration.json'
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        for name, digest in receipt['receipts'].items():
            require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                    'Changed batch970 evidence: ' + name)
        folder = ROOT / 'research/community-batch970-audit'
        coverage = json.loads((folder / 'CONTENT-COVERAGE.json').read_text())['pull_requests']
        decisions = json.loads((folder / 'DISPOSITIONS.json').read_text())['pull_requests']
        require(set(coverage) == set(receipt['reviewed_heads']) == {str(d['number']) for d in decisions},
                'Batch970 review scope differs')
        for decision in decisions:
            number = decision['number']; row = coverage[str(number)]
            require(row['head'] == decision['reviewed_head'] == receipt['reviewed_heads'][str(number)],
                    'Batch970 coverage head differs')
            require(len(row['files']) == row['changed_files'] == len({f['source_path'] for f in row['files']}),
                    'Batch970 changed-file inventory incomplete')
            check_review_completion(actual[number], decision)
            for item in row['files']:
                require(item['action'] in {'retained', 'adapted', 'excluded', 'pending'}, 'Unknown file action')
                if item['action'] == 'pending':
                    require(not decision['review_completion']['changed_file_coverage'], 'Incomplete review')
                if item.get('integrated_sha256'):
                    check_reviewed_family_source(item['integrated_path'], item['integrated_sha256'])
                if item['action'] != 'retained':
                    require(bool(item.get('reason')), 'Missing scope or adaptation reason')
        companion_path = folder / 'COMPANION-REVIEWS.json'
        if companion_path.exists():
            for companion in json.loads(companion_path.read_text())['pull_requests']:
                item = actual[companion['number']]
                check_companion_review(item, companion, family_decisions.get(companion['number']))
        print('PASS batch970 batch: reviewed sources, finite replays, scoped claims and closure bindings')
    receipt_path = ROOT / 'docs/research/community-batch1047-integration.json'
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        for name, digest in receipt['receipts'].items():
            require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                    'Changed batch1047 evidence: ' + name)
        folder = ROOT / 'research/community-batch1047-audit'
        coverage = json.loads((folder / 'CONTENT-COVERAGE.json').read_text())['pull_requests']
        decisions = json.loads((folder / 'DISPOSITIONS.json').read_text())['pull_requests']
        require(set(coverage) == set(receipt['reviewed_heads']) == {str(d['number']) for d in decisions},
                'Batch1047 review scope differs')
        for decision in decisions:
            number = decision['number']; row = coverage[str(number)]
            require(row['head'] == decision['reviewed_head'] == receipt['reviewed_heads'][str(number)],
                    'Batch1047 coverage head differs')
            require(len(row['files']) == row['changed_files'] == len({f['source_path'] for f in row['files']}),
                    'Batch1047 changed-file inventory incomplete')
            check_review_completion(actual[number], decision)
            for item in row['files']:
                require(item['action'] in {'retained', 'adapted', 'excluded', 'pending'}, 'Unknown file action')
                if item['action'] == 'pending':
                    require(not decision['review_completion']['changed_file_coverage'], 'Incomplete review')
                if item.get('integrated_sha256'):
                    check_batch1047_file(item)
                if item['action'] != 'retained':
                    require(bool(item.get('reason')), 'Missing scope or adaptation reason')
        print('PASS batch1047: scoped source coverage and review completion')
    receipt_path = ROOT / 'docs/research/community-batch1099-integration.json'
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        for name, digest in receipt['receipts'].items():
            require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                    'Changed batch1099 evidence: ' + name)
        folder = ROOT / 'research/community-batch1099-audit'
        coverage = json.loads((folder / 'CONTENT-COVERAGE.json').read_text())['pull_requests']
        decisions = json.loads((folder / 'DISPOSITIONS.json').read_text())['pull_requests']
        require(set(coverage) == set(receipt['reviewed_heads']) == {str(d['number']) for d in decisions},
                'Batch1099 review scope differs')
        for decision in decisions:
            number = decision['number']; row = coverage[str(number)]
            require(row['head'] == decision['reviewed_head'] == receipt['reviewed_heads'][str(number)],
                    'Batch1099 coverage head differs')
            require(len(row['files']) == row['changed_files'] == len({f['source_path'] for f in row['files']}),
                    'Batch1099 changed-file inventory incomplete')
            # Later family rounds may update the live ledger projection; keep
            # this archived batch bound to its own immutable review decision.
            check_review_completion(
                actual[number] if family_decisions[number] == decision else decision,
                decision)
            for item in row['files']:
                require(item['action'] in {'retained', 'adapted', 'excluded', 'pending'}, 'Unknown file action')
                if item['action'] == 'pending':
                    require(not decision['review_completion']['changed_file_coverage'], 'Incomplete review')
                if item.get('integrated_sha256'):
                    check_batch1099_file(item)
                if item['action'] != 'retained':
                    require(bool(item.get('reason')), 'Missing scope or adaptation reason')
        print('PASS batch1099: scoped source coverage and review completion')
    import runpy
    reconciliation100 = ROOT / 'research/pr-reconciliation100-20261013/verify.py'
    if reconciliation100.exists():
        runpy.run_path(str(reconciliation100), run_name='__main__')
    historical_five = ROOT / 'research/community-historical-five-audit/replay.py'
    if historical_five.exists():
        runpy.run_path(str(historical_five), run_name='__main__')
    reconciliation92 = ROOT / 'research/community-reconciliation92-audit/verify.py'
    if reconciliation92.exists():
        # The original checker binds the pre-PR154 Makefile. Reuse the
        # authenticated isolated replay rather than weakening that pin.
        subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/replay_historical_check.py'),
                        'reconciliation92'], cwd=ROOT, check=True)
    third100 = ROOT / 'research/community-reconciliation-third100-audit/verify.py'
    if third100.exists():
        runpy.run_path(str(third100), run_name='__main__')
    fourth100 = ROOT / 'research/community-reconciliation-fourth100-audit/verify.py'
    if fourth100.exists():
        runpy.run_path(str(fourth100), run_name='__main__')
    next100 = ROOT / 'research/community-reconciliation-next100-audit/verify.py'
    if next100.exists():
        runpy.run_path(str(next100), run_name='__main__')
    print(f'PASS immutable snapshot plus explicit family rounds: {len(actual)} PRs, attributed heads, evidence pins and unresolved questions')


if __name__ == '__main__':
    main()
