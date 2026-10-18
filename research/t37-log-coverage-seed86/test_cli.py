# SPDX-License-Identifier: Apache-2.0
"""Exercise output safety and source/path admission through the public CLIs.

Prepared for Sagar Thakrar with substantial OpenAI Codex assistance.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

if not __debug__:
    raise RuntimeError('Run CLI tests with assertions enabled')

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
REL = PACKAGE.relative_to(ROOT)


def run(script, *args, optimized=False):
    command = [sys.executable, '-I', '-B'] + (['-O'] if optimized else [])
    return subprocess.run(command + [str(script), *map(str, args)], capture_output=True, text=True)


with tempfile.TemporaryDirectory(prefix='t37-cli-validation-') as temporary:
    root = Path(temporary).resolve()
    reports = []
    for optimized in (False, True):
        output = root / (str(optimized) + '.json')
        p = run(PACKAGE / 'verify.py', '--out', output, optimized=optimized)
        assert p.returncode == 0, p.stderr
        reports.append(output.read_bytes())
    assert reports[0] == reports[1]

    relocated = root / 'relocated with spaces'
    inputs = json.loads((PACKAGE / 'SOURCES.json').read_bytes())['consumed_sha256']
    for name in list(inputs) + [str(REL / n) for n in ('audit.py', 'verify.py', 'SOURCES.json', 'CERTIFICATE.json')]:
        target = relocated / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    p = run(relocated / REL / 'verify.py', '--out', root / 'relocated.json')
    assert p.returncode == 0, p.stderr
    assert (root / 'relocated.json').read_bytes() == reports[0]

    source = relocated / 'research/complex-t37-owners/verify.py'
    source.write_bytes(source.read_bytes() + b'\n# source corruption control\n')
    output = root / 'must-not-exist.json'
    p = run(relocated / REL / 'verify.py', '--out', output)
    assert p.returncode != 0 and 'Source pin differs' in p.stderr and not output.exists()
    sentinel = root / 'preserved.json'
    sentinel.write_bytes(b'preserve existing output\n')
    p = run(relocated / REL / 'verify.py', '--out', sentinel)
    assert p.returncode != 0 and 'Source pin differs' in p.stderr
    assert sentinel.read_bytes() == b'preserve existing output\n'
    p = run(PACKAGE / 'verify.py', '--out', sentinel)
    assert p.returncode != 0 and 'FileExistsError' in p.stderr
    assert sentinel.read_bytes() == b'preserve existing output\n'

    evidence = root / 'evidence'
    evidence.mkdir()
    with tarfile.open(ROOT / 'research/community-frontier942-audit/t37-replay.tar.gz') as bundle:
        for member in bundle.getmembers():
            if member.name in ('STAGES.json', 'native/STEPS.json', 'discovery/STAGES.json', 'strict/STAGES.json') or member.name.endswith('.log'):
                target = evidence / member.name
                assert member.isfile() and target.resolve().is_relative_to(evidence)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(bundle.extractfile(member).read())
    p = run(PACKAGE / 'audit.py', '--work', evidence, '--out', root / 'audit.json')
    assert p.returncode == 0, p.stderr
    missing = evidence / 'native/phases.log'
    original = missing.read_bytes()
    missing.unlink()
    p = run(PACKAGE / 'audit.py', '--work', evidence, '--out', output)
    assert p.returncode != 0 and 'Missing or escaping file: native/phases.log' in p.stderr
    assert not output.exists()
    outside = root / 'outside.log'
    outside.write_bytes(original)
    missing.symlink_to(outside)
    p = run(PACKAGE / 'audit.py', '--work', evidence)
    assert p.returncode != 0 and 'Missing or escaping file: native/phases.log' in p.stderr

print('PASS_T37_LOG_CLI_CONTROLS: optimized equivalence, relocation, source pin, '
      'output preservation, missing log, escaping symlink; receipt ' + hashlib.sha256(reports[0]).hexdigest())
