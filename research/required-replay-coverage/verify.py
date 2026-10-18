"""Replay PR838's omissions against the complete PR799 binding and enforced gate.

Lucas (@ljste) supplied the original PR741 audit. New PR799 reachability and
production enforcement by nightangelflowerwin-ops with substantial Codex help.
Apache-2.0. Archive replays are not fresh multiplication theorem proofs.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'scripts'))
import verify_replay_coverage as covered
import verify_frontier799_bindings as original


def require(ok, message):
    if not ok:
        raise ValueError(message)


def extract(path, destination):
    with tarfile.open(path) as archive:
        for member in archive:
            if member.isfile():
                target = covered.artifact_path(destination, member.name)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.extractfile(member).read())
            else:
                require(member.isdir(), 'Unexpected archive member type')


def outcome(action):
    try:
        action()
        return 'accepted'
    except (ValueError, OSError, KeyError, TypeError):
        return 'rejected'


def run():
    sources = json.loads((HERE / 'SOURCES.json').read_bytes())
    for name, pin in sources['inputs'].items():
        require(covered.digest(ROOT / name) == pin, 'Pinned input drift: ' + name)
    contract = covered.contract()
    results = []
    with tempfile.TemporaryDirectory(prefix='required-coverage-') as temporary:
        root = Path(temporary)
        baseline = root / 'baseline'
        extract(ROOT / 'research/community-frontier741-audit/composed-replay-evidence.tar.gz', baseline / 'ancestor')
        extract(ROOT / 'research/community-frontier799-audit/integrated799-replay.tar.gz', baseline)
        def old(directory):
            return original.check(directory / 'ancestor', directory / 'native', directory / 'global',
                                  directory / 'INDEPENDENT-LOCAL.json', directory / 'INDEPENDENT-PRICE.json')
        def new(directory):
            return covered.check_selected(directory, directory / 'ancestor')
        require(outcome(lambda: old(baseline)) == outcome(lambda: new(baseline)) == 'accepted', 'Pristine current replay rejected')
        # Historical ordinary archive includes the same supported producer,
        # without the selected X4 evidence. It remains a valid PR741 input.
        covered.check_ancestor(baseline / 'ancestor/bit', baseline / 'ancestor/complex')
        directory = root / 'case'
        shutil.copytree(baseline, directory)
        mutable = ['ancestor/complex/RECEIPT.json', 'ancestor/complex/STAGES.json',
                   'native/phases.log', 'independent-price.log']
        mutable += ['ancestor/complex/' + name for name in contract['artifacts']]
        mutable += ['ancestor/complex/' + name + '.log' for name in contract['stages']]
        snapshots = {name: (baseline / name).read_bytes() for name in set(mutable)}

        def case(label, mutation):
            mutation(directory)
            old_result = outcome(lambda: old(directory))
            new_result = outcome(lambda: new(directory))
            require(new_result == 'rejected', 'Coverage mutation accepted: ' + label)
            results.append(dict(case=label, original_pr799=old_result, enforced_pr799=new_result))
            for name, payload in snapshots.items():
                path = directory / name
                if not path.exists() or path.read_bytes() != payload:
                    path.write_bytes(payload)
            (directory / 'ancestor/complex/unrelated-successful-command.log').unlink(missing_ok=True)
            if len(results) % 20 == 0:
                print('PASS', len(results), 'mutation cases', flush=True)

        def mutate_receipt(directory, action):
            path = directory / 'ancestor/complex/RECEIPT.json'
            receipt = covered.read(path)
            action(receipt, directory / 'ancestor/complex')
            path.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')

        for name in contract['stages']:
            def stage_mutation(directory, name=name):
                def change(receipt, complex_dir):
                    row = next(s for s in receipt['stages'] if s['name'] == name)
                    (complex_dir / (name + '.log')).unlink()
                    row['name'] = 'unrelated-successful-command'
                    log = complex_dir / (row['name'] + '.log')
                    log.write_text('Unrelated successful command.\n', encoding='utf-8')
                    row['log_sha256'] = covered.digest(log)
                    stages = complex_dir / 'STAGES.json'
                    stages.write_text(json.dumps(receipt['stages']), encoding='utf-8')
                    receipt['artifacts']['STAGES.json'] = covered.digest(stages)
                mutate_receipt(directory, change)
            case('replace-stage:' + name, stage_mutation)
        for name in contract['artifacts']:
            def omission(directory, name=name):
                mutate_receipt(directory, lambda receipt, folder: receipt['artifacts'].pop(name))
            case('omit-inventory:' + name, omission)
            if name not in ('RESULT.json', 'global-replay/ASSEMBLY.json'):
                def deletion(directory, name=name):
                    omission(directory, name)
                    (directory / 'ancestor/complex' / name).unlink()
                case('delete-artifact:' + name, deletion)
        case('empty-inventory', lambda d: mutate_receipt(d, lambda r,p: r.update(artifacts={})))
        def wrong_order(d):
            path = d / 'ancestor/complex/STAGES.json'
            rows = covered.read(path);rows.reverse();path.write_text(json.dumps(rows), encoding='utf-8')
            mutate_receipt(d, lambda r,p: r['artifacts'].update({'STAGES.json':covered.digest(path)}))
        case('execution-record-order', wrong_order)
        for label, action in [
            ('failed-stage', lambda r,p: r['stages'][0].update(exit_code=1)),
            ('boolean-exit-code', lambda r,p: r['stages'][0].update(exit_code=False)),
            ('wrong-source-pin', lambda r,p: r.update(manifest_sha256='0'*64)),
            ('wrong-listed-hash', lambda r,p: r['artifacts'].update({'RESULT.json':'0'*64})),
            ('missing-listed-file', lambda r,p: (p/'INDEPENDENT-LOCAL.json').unlink()),
            ('traversal-inventory', lambda r,p: r['artifacts'].update({'../outside':'0'*64})),
        ]:
            case(label, lambda d, action=action: mutate_receipt(d, action))
        case('missing-selected-native-log', lambda d: (d / 'native/phases.log').unlink())
        case('missing-selected-independent-price-log', lambda d: (d / 'independent-price.log').unlink())
        # Public CLI on actual archived files: complete selected binding passes;
        # after removing the ancestor phase evidence, original CLI still passes.
        directory = root / 'public'
        shutil.copytree(baseline, directory)
        phase = 'local/CLIFFORD-REVIEW.json'
        mutate_receipt(directory, lambda r,p: (r['artifacts'].pop(phase), (p/phase).unlink()))
        cli = [sys.executable, '-B', str(ROOT / 'scripts/verify_frontier799_bindings.py'),
               '--ancestor', str(directory / 'ancestor'), '--native', str(directory / 'native'),
               '--global', str(directory / 'global'), '--independent', str(directory / 'INDEPENDENT-LOCAL.json'),
               '--price', str(directory / 'INDEPENDENT-PRICE.json'), '--out', str(root / 'old-result.json')]
        p = subprocess.run(cli, capture_output=True, text=True)
        require(p.returncode == 0 and 'PASS_REBUILT_PR589_PR799_COMPOSITION' in p.stdout, 'Public current CLI did not reproduce witness')
        fixed_cli = [sys.executable, '-I', '-B', str(ROOT / 'scripts/verify_replay_coverage.py'),
                     '--frontier', '799', '--work', str(directory), '--ancestor', str(directory / 'ancestor')]
        p = subprocess.run(fixed_cli, capture_output=True, text=True)
        require(p.returncode != 0 and 'Required ancestry artifact inventory differs' in p.stderr, 'Enforced public CLI did not reject witness')
        # Reject invalid reuse before starting the expensive producer.
        destination = root / 'must-not-be-created'
        p = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/verify_frontier_complete.py'),
                            '--frontier', '799', '--work', str(destination), '--ancestor', str(directory / 'ancestor')],
                           capture_output=True, text=True)
        require(p.returncode != 0 and not destination.exists(), 'Incomplete reuse was launched')
        p = subprocess.run([sys.executable, '-I', '-O', '-B', str(ROOT / 'scripts/verify_replay_coverage.py'),
                            '--frontier', '799', '--work', str(baseline), '--ancestor', str(baseline / 'ancestor')],
                           capture_output=True, text=True)
        require(p.returncode == 0, 'Optimized complete coverage rejected pristine evidence')
    return dict(base=sources['base'], parent_audit_pr=838, selected_frontier=799,
                pristine='accepted', historical_pr741='accepted', mutation_results=results,
                original_pr799_accepted=sum(row['original_pr799'] == 'accepted' for row in results),
                enforced_rejections=len(results), public_cli_witness='reproduced_and_rejected',
                incomplete_reuse='rejected_before_launch', isolated_optimized='passed')


if __name__ == '__main__':
    result = run()
    if '--write' in sys.argv:
        (HERE / 'EXPECTED.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    else:
        require(result == json.loads((HERE / 'EXPECTED.json').read_bytes()), 'Evidence receipt differs')
    print('PASS_REQUIRED_REPLAY_COVERAGE', result['original_pr799_accepted'], 'original PR799 accepts;',
          result['enforced_rejections'], 'enforced rejections; valid historical and selected replays accepted')
