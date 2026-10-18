"""Portable paths and external output locations for the retained experiments."""
from pathlib import Path
import os
import tempfile

PACKAGE = Path(__file__).resolve().parents[2]
WORKBENCH = PACKAGE / 'workbench'
CHECKOUT = PACKAGE.parents[1]
_DEFAULT_WORKSPACE = None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def workspace_path(value=None):
    global _DEFAULT_WORKSPACE
    value = value or os.environ.get('NIEMEIER_WORKSPACE')
    if value is None:
        if _DEFAULT_WORKSPACE is None:
            _DEFAULT_WORKSPACE = Path(tempfile.mkdtemp(prefix='niemeier-controller-'))
        path = _DEFAULT_WORKSPACE
    else:
        path = Path(value).expanduser().resolve()
    require(not path.is_relative_to(CHECKOUT), 'Generated output must be outside the checkout')
    path.mkdir(parents=True, exist_ok=True)
    return path


def output_path(relative):
    path = workspace_path() / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def source_name(path):
    return str(Path(path).resolve().relative_to(PACKAGE))


def replay_scripts(directory, cases, workspace, optimized=True):
    """Run standalone programs and compare every field of their JSON receipts."""
    import json
    import subprocess
    import sys
    import time

    workspace = workspace_path(workspace)
    relative_directory = directory.relative_to(WORKBENCH)
    rows = []
    for script, receipt in cases:
        started = time.monotonic()
        command = [sys.executable, '-I'] + (['-O'] if optimized else [])
        command.append(str(directory / script))
        environment = dict(os.environ, NIEMEIER_WORKSPACE=str(workspace),
                           PYTHONDONTWRITEBYTECODE='1')
        result = subprocess.run(command, cwd=workspace, env=environment,
                                capture_output=True, text=True)
        log = workspace / relative_directory / (script.replace('/', '_') + '.log')
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(result.stdout + result.stderr)
        require(result.returncode == 0,
                f'{script} failed; log: {log}\n{(result.stdout + result.stderr)[-3000:]}')
        generated = workspace / relative_directory / receipt
        require(generated.is_file(), f'{script} did not generate {receipt}')
        expected = json.loads((directory / receipt).read_text())
        actual = json.loads(generated.read_text())
        require(actual == expected, f'{script}: canonical JSON differs for {receipt}')
        rows.append(dict(script=script, receipt=receipt, status='PASS',
                         seconds=round(time.monotonic() - started, 3)))
        print(f'PASS {relative_directory}/{script}: {rows[-1]["seconds"]}s', flush=True)
    return rows
