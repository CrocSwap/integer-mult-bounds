"""Replay the archived finite refutation; never rerun the expensive SAT search."""
import gzip
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from importlib.metadata import version
from pathlib import Path

from checks import audit_counter_bridge, build_instance

ROOT = Path(__file__).resolve().parent


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def accepted(result, marker):
    return result.returncode == 0 and marker in result.stdout.splitlines()


def run(command, timeout=300):
    return subprocess.run(command, capture_output=True, text=True, timeout=timeout)


def require(result, marker):
    if not accepted(result, marker):
        raise ValueError('native replay did not verify: ' + result.stdout[-2000:] +
                         result.stderr[-2000:])


def main():
    if version('python-sat') != '1.9.dev15':
        raise ValueError('requires python-sat==1.9.dev15')
    manifest = json.loads((ROOT / 'SOURCES.json').read_text())
    for row in manifest['vendored_files']:
        if digest(ROOT / row['path']) != row['sha256']:
            raise ValueError('source pin mismatch: ' + row['path'])
    with tempfile.TemporaryDirectory(prefix='connector-c5-replay-') as directory:
        temp = Path(directory)
        for row in manifest['payloads']:
            destination = temp / row['name']
            with gzip.open(ROOT / row['archive'], 'rb') as src, destination.open('wb') as dst:
                shutil.copyfileobj(src, dst)
            if digest(destination) != row['sha256']:
                raise ValueError('certificate payload mismatch: ' + row['name'])
        cnf, pool = build_instance()
        audit_counter_bridge(cnf, pool)
        cnf.to_file(str(temp / 'regenerated.cnf'))
        if (temp / 'regenerated.cnf').read_bytes() != (temp / 'instance.cnf').read_bytes():
            raise ValueError('pinned generator does not reproduce certified formula')
        for name, flags in [('drat-trim', []), ('lrat-check', ['-DLONGTYPE'])]:
            source = (ROOT / 'vendor/lrat-check-pr43.c' if name == 'lrat-check' else
                      ROOT / 'vendor/drat-trim/drat-trim.c')
            compiled = run(['gcc', '-std=c99', *flags, '-O2',
                            str(source),
                            '-o', str(temp / name)], 60)
            if compiled.returncode:
                raise ValueError('checker compilation failed: ' + compiled.stderr)
        drat = run([str(temp / 'drat-trim'), str(temp / 'instance.cnf'),
                    str(temp / 'trimmed.drat'), '-L', str(temp / 'proof.lrat')])
        require(drat, 's VERIFIED')
        executable = temp / 'lrat-check'
        actual = run([str(executable), str(temp / 'instance.cnf'), str(temp / 'proof.lrat')])
        require(actual, 'c VERIFIED')

        # A genuine refutation is required, not merely an UNSAT verdict or file.
        (temp / 'empty.lrat').write_text('')
        empty = run([str(executable), str(temp / 'instance.cnf'), str(temp / 'empty.lrat')])
        if accepted(empty, 'c VERIFIED'):
            raise ValueError('empty certificate accepted')
        (temp / 'fake.lrat').write_text('52673 0 1 0\n')
        fake = run([str(executable), str(temp / 'instance.cnf'), str(temp / 'fake.lrat')])
        if accepted(fake, 'c VERIFIED'):
            raise ValueError('unsupported empty-clause derivation accepted')
        (temp / 'sat.cnf').write_text('p cnf 1 1\n1 0\n')
        (temp / 'sat-fake.lrat').write_text('2 0 1 0\n')
        sat = run([str(executable), str(temp / 'sat.cnf'), str(temp / 'sat-fake.lrat')])
        if accepted(sat, 'c VERIFIED'):
            raise ValueError('satisfiable formula falsely refuted')

        # Replay the predecessor's original word controls without modifying it.
        stage = temp / 'predecessor'
        package = stage / 'research/connector-six-source-small-char'
        interface = stage / 'research/connector-depth-blocks'
        package.mkdir(parents=True)
        interface.mkdir(parents=True)
        shutil.copyfile(ROOT / 'vendor/verify.py', package / 'verify.py')
        shutil.copyfile(ROOT / 'vendor/connector-depth-blocks-README.md', interface / 'README.md')
        for flags in [[], ['-O']]:
            result = run([sys.executable, *flags, '-B', str(package / 'verify.py')], 60)
            if result.returncode or not any(line.startswith('PASS_CONNECTOR_SIX_SOURCE_SMALL_CHAR ')
                                            for line in result.stdout.splitlines()):
                raise ValueError('predecessor control replay failed')
        print(json.dumps({'status': 'PASS_CONNECTOR_C5_CERTIFICATE',
                          'variables': cnf.nv, 'clauses': len(cnf.clauses),
                          'counter_blocks': 12, 'native_rejection_controls': 3,
                          'predecessor_modes': 2,
                          'drat_checker_stdout': drat.stdout,
                          'lrat_checker_stdout': actual.stdout}, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        raise SystemExit(2)
