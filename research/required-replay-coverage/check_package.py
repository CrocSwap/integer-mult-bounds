"""Minimal offline relocation and source/contract corruption controls."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify import extract, require, ROOT


def main():
    with tempfile.TemporaryDirectory(prefix='coverage relocation ') as temporary:
        root = Path(temporary) / 'root with spaces'
        files = [
            'scripts/verify_frontier741_bindings.py', 'scripts/verify_frontier799_bindings.py',
            'scripts/verify_frontier741.py', 'scripts/verify_frontier799.py',
            'scripts/verify_replay_coverage.py', 'scripts/verify_frontier_complete.py',
            'scripts/verify_frontier741_bridge_coverage.py',
            'certificates/replay-coverage/pr741-sw4-v1.json',
            'research/complex-sw4-frame8/verify.py', 'research/complex-sw4-frame8/MANIFEST.json',
            'research/complex-sw4-frame8/data/SPEC.json', 'research/complex-sw4-frame8/inputs/PR589-EXPECTED.json',
            'research/e8-bit-p111-tuned/tune/EXPECTED.json',
        ]
        for name in files:
            destination = root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)
        shutil.copytree(ROOT / 'research/gauge44-frames-x', root / 'research/gauge44-frames-x',
                        ignore=shutil.ignore_patterns('__pycache__'))
        replay = Path(temporary) / 'replay with spaces'
        extract(ROOT / 'research/community-frontier741-audit/composed-replay-evidence.tar.gz', replay / 'ancestor')
        extract(ROOT / 'research/community-frontier799-audit/integrated799-replay.tar.gz', replay)
        command = [sys.executable, '-I', '-O', '-B', str(root / 'scripts/verify_replay_coverage.py'),
                   '--frontier', '799', '--work', str(replay), '--ancestor', str(replay / 'ancestor')]
        result = subprocess.run(command, cwd=temporary, capture_output=True, text=True)
        require(result.returncode == 0 and 'PASS_COMPLETE_PR799_REPLAY_COVERAGE' in result.stdout,
                'Relocated isolated replay failed: ' + result.stderr[-2000:])
        # Exercise publication using real evidence, without claiming another
        # expensive supplier execution. The cold run uses this same postflight.
        sys.path.insert(0, str(ROOT / 'scripts'))
        import verify_frontier_complete as entrypoint
        output = Path(temporary) / 'public output'
        output.mkdir()
        entrypoint.publish(output, replay, '799', replay / 'ancestor')
        require((output / 'RESULT.json').is_file(), 'Complete result not published')
        (output / 'RESULT.json').unlink()
        phase_log = replay / 'native/phases.log'
        phase_log.unlink()
        try:
            entrypoint.publish(output, replay, '799', replay / 'ancestor')
        except ValueError:
            pass
        else:
            raise ValueError('Incomplete evidence published')
        require(not (output / 'RESULT.json').exists(), 'Failure left a public success record')
        # Restore the native log from the complete archived output.
        extract(ROOT / 'research/community-frontier799-audit/integrated799-replay.tar.gz', replay)
        producer = root / 'research/complex-sw4-frame8/verify.py'
        before = producer.read_bytes()
        producer.write_bytes(before + b'\n# unexpected source drift\n')
        result = subprocess.run(command, cwd=temporary, capture_output=True, text=True)
        require(result.returncode != 0 and 'Coverage producer version differs' in result.stderr,
                'Changed producer accepted')
        producer.write_bytes(before)
        contract = root / 'certificates/replay-coverage/pr741-sw4-v1.json'
        contract.write_text(contract.read_text().replace('integer-mult-replay-coverage-v1', 'unknown-version'), encoding='utf-8')
        result = subprocess.run(command, cwd=temporary, capture_output=True, text=True)
        require(result.returncode != 0 and 'Unsupported replay coverage version' in result.stderr,
                'Unknown relocated contract accepted')
    print('PASS_REQUIRED_COVERAGE_PACKAGE: isolated relocation; producer drift and unknown version rejected')


if __name__ == '__main__':
    main()
