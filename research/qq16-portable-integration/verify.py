#!/usr/bin/env python3
"""PR4790 replay with one authenticated, in-memory path-rendering correction.

Mihir Srivastava, substantial OpenAI Codex assistance. Apache-2.0.
The retained verifier, protocol and authentication keep their original authors.
"""
import argparse
import builtins
from contextlib import contextmanager
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import subprocess
import sys
import tarfile
import tempfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIOR = ROOT / 'research/qq16-protected-return-caller'
ARCHIVE = ROOT / 'research/physical-gaussian-leaf/inputs/pr3087.tar'
ARCHIVE_SHA = 'd7e9c04a5e6d3f76158555d84080786c7cd8028ca31a61c9399de2b2c67bfd53'
NESTED = (
    ('inputs/pr3055.tar', 'c76e11cce0696db643715a362631b60fb14f26ba66c1e3bb5b5b0389eb52e95d'),
    ('inputs/pr2899.tar', 'fc4a2e07423835737c8fb3872664b16ff12aa4cf83b1e26e49878debef40c531'),
    ('inputs/pr2809.tar', 'ee1d4ec05e3c872d264be3b38f71a8c153acf37427f5d3ba87f8e15440c9ccf0'),
)
ORIGINAL_SHA = '65126e788eeea10e830fc583cf4afe0bfc4d67495cbf8ac21de3507dbe624d56'
ADAPTED_SHA = 'd3685f34f88b1e2f5f8aaf5fe55bdbaf7f4bb004af8bcf321a2e9e4cb4e74ec9'
OLD = b"str(path.relative_to(here/'predecessor'))"
NEW = b"path.relative_to(here/'predecessor').as_posix()"
COMPILE = builtins.compile


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def authenticate():
    rows = json.loads((HERE / 'SOURCES.json').read_bytes())['files']
    inputs = [r for r in rows if r['usage'] == 'input']
    need(len(inputs) == len({r['path'] for r in inputs}), 'unique live source inventory')
    for row in inputs:
        path = ROOT / row['path']
        need(path.is_file() and not path.is_symlink(), 'regular source: ' + row['path'])
        need(sha(path.read_bytes()) == row['sha256'], 'source integrity: ' + row['path'])
    return inputs


def load_source(raw, path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(COMPILE(raw, str(path), 'exec'), module.__dict__)
    return module


def retained():
    return load_source((PRIOR / 'verify.py').read_bytes(), PRIOR / 'verify.py', 'retained_pr4790')


def compare_result(prior, observed, expected):
    need(prior.canonical(observed) == prior.canonical(expected), 'complete typed PR4790 receipt')


def adapt(raw):
    need(sha(raw) == ORIGINAL_SHA, 'exact PR2753 verifier before adaptation')
    need(raw.count(OLD) == 1, 'one inventory path expression')
    result = raw.replace(OLD, NEW)
    need(sha(result) == ADAPTED_SHA, 'exact adapted PR2753 verifier')
    return result


@contextmanager
def inventory_adapter():
    """Only this exact source image changes; source files and pins stay intact."""
    calls = []

    def compile_source(source, filename, mode, *args, **kwargs):
        raw = source.encode('utf-8') if isinstance(source, str) else source
        if isinstance(raw, bytes) and sha(raw) == ORIGINAL_SHA:
            need(mode == 'exec', 'adapt complete executable module only')
            source = adapt(raw)
            calls.append(ORIGINAL_SHA)
        return COMPILE(source, filename, mode, *args, **kwargs)

    need(builtins.compile is COMPILE, 'unmodified compiler at adapter entry')
    builtins.compile = compile_source
    try:
        yield calls
    finally:
        builtins.compile = COMPILE


def run_case(name):
    authenticate()
    prior = retained()
    with inventory_adapter() as calls:
        result = prior.case(name)
    need(calls == [ORIGINAL_SHA], 'exactly one adapted PR2753 module per case')
    return result


def replay():
    """Use the complete original aggregator, redirecting only its six workers."""
    prior = retained()
    seen = []

    def run(command, **kwargs):
        expected = [sys.executable, '-I', '-B'] + (['-O'] if sys.flags.optimize else [])
        need(command[:len(expected)] == expected and len(command) == len(expected) + 5,
             'original isolated worker arguments')
        need(command[-3] == str(PRIOR / 'verify.py') and command[-2] == '--case'
             and command[-1] in prior.CASE_NAMES, 'original known worker destination')
        need(command[len(expected)] == '-X' and
             command[len(expected)+1].startswith('pycache_prefix='), 'fresh original worker cache')
        need(kwargs == dict(capture_output=True, text=True, timeout=90), 'original worker bounds')
        seen.append(command[-1])
        command = list(command)
        command[-3] = str(HERE / 'verify.py')
        return subprocess.run(command, **kwargs)

    # A module-local facade: no global subprocess monkeypatch or new aggregator.
    prior.subprocess = types.SimpleNamespace(run=run)
    result = prior.compute()
    need(seen == list(prior.CASE_NAMES), 'all six original workers in original order')
    expected = json.loads((PRIOR / 'RESULT.json').read_bytes())
    compare_result(prior, result, expected)
    return result


def predecessor_archive():
    raw = ARCHIVE.read_bytes()
    need(sha(raw) == ARCHIVE_SHA, 'outer immutable archive')
    for name, digest in NESTED:
        with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
            members = [m for m in archive.getmembers() if m.name == name]
            need(len(members) == 1 and members[0].isfile(), 'one regular nested archive: ' + name)
            raw = archive.extractfile(members[0]).read()
        need(sha(raw) == digest, 'nested immutable archive: ' + name)
    return raw


def controls():
    """Exercise the actual retained authenticator, including real file faults."""
    rejected = []

    def reject(label, action, message):
        try:
            action()
        except ValueError as error:
            need(str(error) == message, 'wrong rejection boundary: ' + label + ': ' + str(error))
            rejected.append(label)
        else:
            raise ValueError('negative control accepted: ' + label)

    prior = retained()
    with tempfile.TemporaryDirectory(prefix='qq16-portable-controls-') as td:
        root = Path(td).resolve()
        prior.projection(root, prior.authenticate())
        container = root / 'auth-fixture'
        container.mkdir()
        with tarfile.open(fileobj=io.BytesIO(predecessor_archive())) as archive:
            seen = set()
            for member in archive.getmembers():
                path = PurePosixPath(member.name)
                need(not path.is_absolute() and '..' not in path.parts and
                     member.name not in seen and (member.isfile() or member.isdir()),
                     'regular unique relative predecessor member')
                seen.add(member.name)
            archive.extractall(container, filter='data')
        here = container / 'inputs/pr2753'
        loader_path = container / 'loader.py'
        loader = load_source(loader_path.read_bytes(), loader_path, 'retained_pr2809_loader')
        loader.REPOSITORY = root
        sources = loader.selected_sources((root / 'certificates/selected-result.json').read_bytes())
        loader.compatibility_controls()
        raw = (here / 'verify.py').read_bytes()
        fixed = load_source(adapt(raw), here / 'verify.py', 'adapted_auth_control')
        original = load_source(raw, here / 'verify.py', 'original_auth_control')
        kwargs = dict(sources=sources, here=here, root=root)
        positive = fixed.authenticate(**kwargs)
        if sys.platform == 'win32':
            reject('original_windows_inventory', lambda: original.authenticate(**kwargs),
                   'no omitted or extra predecessor files')
        else:
            need(original.authenticate(**kwargs) == positive, 'unchanged POSIX authentication')
        for cls in (PurePosixPath, PureWindowsPath):
            need(sorted(cls(p).as_posix() for p in fixed.FROZEN_FILES) == sorted(fixed.FROZEN_FILES),
                 'same exact inventory on both path flavours')
        need(sorted(str(PureWindowsPath(p)) for p in fixed.FROZEN_FILES) != sorted(fixed.FROZEN_FILES),
             'original Windows inventory mismatch reproduced independently')
        victim = here / 'predecessor/vendor/controller.py'
        saved = victim.read_bytes()
        victim.unlink()
        try:
            reject('missing_file', lambda: fixed.authenticate(**kwargs), 'no omitted or extra predecessor files')
        finally:
            victim.write_bytes(saved)
        extra = here / 'predecessor/vendor/unexpected.py'
        extra.write_bytes(b'# extra source\n')
        try:
            reject('extra_file', lambda: fixed.authenticate(**kwargs), 'no omitted or extra predecessor files')
        finally:
            extra.unlink()
        victim.write_bytes(saved + b'\n# changed source\n')
        try:
            reject('changed_file', lambda: fixed.authenticate(**kwargs), 'pinned bytes changed: vendor/controller.py')
        finally:
            victim.write_bytes(saved)
        frozen = json.loads((here / 'PREDECESSOR.json').read_bytes())
        changed = deepcopy(frozen)
        changed['files']['vendor/controller.py']['git_blob'] = '0' * 40
        reject('changed_git_blob', lambda: fixed.authenticate(predecessor=changed, **kwargs),
               'pinned Git blob changed: vendor/controller.py')
        changed = deepcopy(frozen)
        del changed['files']['vendor/controller.py']
        reject('omitted_manifest_entry', lambda: fixed.authenticate(predecessor=changed, **kwargs),
               'exact predecessor source inventory')
        changed = deepcopy(sources)
        changed['files'] = [r for r in changed['files'] if r['path'] != fixed.LIVE_INPUTS[0]]
        reject('omitted_live_source', lambda: fixed.authenticate(**dict(kwargs, sources=changed)),
               'exact live source inventory')
        manifest = json.loads((here / 'VERIFY.json').read_bytes())
        manifest['inputs'].pop()
        reject('omitted_CI_input', lambda: fixed.authenticate(manifest=manifest, **kwargs),
               'exact replay invalidation inventory')
        reject('changed_adapter_source', lambda: adapt(raw + b'\n'), 'exact PR2753 verifier before adaptation')
        need(fixed.authenticate(**kwargs) == positive, 'authentication restored after all controls')
        need((here / 'verify.py').read_bytes() == raw, 'retained executable bytes unchanged')
        receipt = json.loads((PRIOR / 'RESULT.json').read_bytes())
        compare_result(prior, receipt, deepcopy(receipt))
        changed = deepcopy(receipt)
        changed['cases']['fixed']['final_inventory_exact'] = 1
        reject('receipt_bool_to_integer', lambda: compare_result(prior, changed, receipt),
               'complete typed PR4790 receipt')
        changed = deepcopy(receipt)
        changed['cases']['fixed']['fresh_record_tapes'] = float(changed['cases']['fixed']['fresh_record_tapes'])
        reject('receipt_integer_to_float', lambda: compare_result(prior, changed, receipt),
               'complete typed PR4790 receipt')
        changed = deepcopy(receipt)
        del changed['cases']['service-stop']
        reject('receipt_omitted_cleanup', lambda: compare_result(prior, changed, receipt),
               'complete typed PR4790 receipt')
        changed = deepcopy(receipt)
        changed['finite_matched_saving_RWM']['reads'] += 1
        reject('receipt_changed_saving', lambda: compare_result(prior, changed, receipt),
               'complete typed PR4790 receipt')
    return {'authentication': positive,
            'rejected': [r for r in rejected if r != 'original_windows_inventory'],
            'path_flavours': ['posix', 'windows'], 'single_expression_sha256': ADAPTED_SHA}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=('fixed', 'adopt', 'stale-engines', 'stale-external', 'output-alias', 'service-stop'))
    parser.add_argument('--controls-only', action='store_true')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    authenticate()
    if args.case:
        need(not args.controls_only, 'one worker mode')
        print(canonical(run_case(args.case)))
        return
    checked = controls()
    if args.controls_only:
        print(canonical(checked))
        return
    result = replay()
    report = {'status': 'PASS_QQ16_PORTABLE_INTEGRATION', 'controls': checked,
              'complete_prior_receipt_sha256': sha(canonical(result).encode()),
              'cases': list(result['cases']), 'finite_matched_saving_RWM': result['finite_matched_saving_RWM'],
              'source_census': 'inherited, not independently rerun', 'new_kappa': False}
    print(canonical(report) if args.json else report['status'])


if __name__ == '__main__':
    main()
