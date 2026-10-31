"""Exact export-check conformance and recorded benchmark arithmetic."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import statistics
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = 'research/fixture'
RECEIPT = '.research-export.json'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def bindings():
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    rows = sources['retained_baseline']
    require({row['package_path'] for row in rows} ==
            {'baseline/export_research_package.py', 'baseline/research_package.py'},
            'baseline inventory changed')
    for row in rows:
        data = (HERE / row['package_path']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == row['sha256'], 'baseline source changed')
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(blob == row['git_blob'], 'baseline Git blob changed')


def bundle(path, count, order, mode, raw=None, extra=False, corrupt=False):
    names = [f'inputs/item-{index}.bin' for index in range(count)]
    files = {PACKAGE + '/README.md': b'scope',
             PACKAGE + '/VERIFY.json': json.dumps({'inputs': names}).encode() if raw is None else raw}
    files.update({name: bytes([index, 0, 255]) for index, name in enumerate(names)})
    if extra:
        files['undeclared.bin'] = b'extra'
    receipt = {'format': 'research-package-export-v1', 'commit': 'a' * 40,
               'package': PACKAGE, 'files': [
                   {'path': name, 'mode': mode, 'size': len(data),
                    'sha256': hashlib.sha256(data).hexdigest()} for name, data in files.items()]}
    rows = list(files.items())
    rows.insert(min(order, len(rows)), (RECEIPT, json.dumps(receipt).encode()))
    with tarfile.open(path, 'w') as archive:
        for name, data in rows:
            info = tarfile.TarInfo(name)
            info.size, info.mode = len(data), mode
            archive.addfile(info, io.BytesIO(data))
    if corrupt:
        with tarfile.open(path, 'r:') as archive:
            offset = archive.getmember(PACKAGE + '/README.md').offset_data
        with path.open('r+b') as stream:
            stream.seek(offset)
            require(stream.write(b'X') == 1, 'incomplete corruption fixture')


def outcome(module, path, check_inputs):
    try:
        return ['accept', canonical(module.check_bundle(path, check_inputs=check_inputs))]
    except (OSError, ValueError, TypeError, KeyError, RecursionError, tarfile.TarError) as exc:
        return ['reject', type(exc).__name__, str(exc)]


def conformance(before, after, directory):
    path = Path(directory) / 'fixture.tar'
    counts = {'accept': 0, 'reject': 0}
    witnesses = []
    valid = [(count, order, mode, None, False, False)
             for count in (0, 1, 7, 31) for order in (0, 1, 100) for mode in (0o644, 0o755)]
    malformed = [b'[]', b'{"inputs":1}', b'{"inputs":[],"inputs":[]}',
                 b'{"inputs":["x","x"]}', b'{"inputs":["../x"]}',
                 b'{"inputs":["C:/x"]}', b'{"inputs":["missing.bin"]}',
                 b'{"inputs":[".research-export.json"]}', b'{"inputs":[true]}']
    invalid = [(0, order, 0o644, raw, False, False)
               for order in (0, 100) for raw in malformed]
    invalid += [(0, 100, 0o644, None, True, False), (0, 0, 0o644, None, False, True)]
    for index, fixture in enumerate(valid + invalid):
        bundle(path, *fixture)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        for check_inputs in (False, True):
            old = outcome(before, path, check_inputs)
            new = outcome(after, path, check_inputs)
            require(old == new, f'conformance mismatch at {index}, {check_inputs}')
            if index < len(valid):
                require(new[0] == 'accept', 'positive fixture rejected')
            elif check_inputs:
                require(new[0] == 'reject', 'negative fixture accepted')
            counts[new[0]] += 1
            witnesses.append([index, check_inputs, new])
        require(hashlib.sha256(path.read_bytes()).hexdigest() == digest, 'check wrote input')
    return {**counts, 'fixtures': len(valid + invalid),
            'complete_outcomes_sha256': hashlib.sha256(canonical(witnesses).encode()).hexdigest()}


def measured_evidence():
    result = {}
    scripts = [HERE / 'baseline/export_research_package.py', ROOT / 'scripts/export_research_package.py']
    for label in ('toolkit', 'small'):
        value = json.loads((HERE / f'BENCHMARK-{label}.json').read_text())
        require(value['source_sha256'] == [hashlib.sha256(p.read_bytes()).hexdigest() for p in scripts],
                'timed source no longer matches')
        require(value['pairs'] == 9 and value['commands_per_side_per_pair'] == 5, 'sample shape')
        require(value['successful_commands'] == 90 and value['errors'] == 0, 'measurement failures')
        runs = value['elapsed_ns']
        require(len(runs) == 2 and all(len(side) == 9 for side in runs), 'pair count')
        require(all(len(row) == 5 for side in runs for row in side), 'batch count')
        require(all(type(n) is int and 0 < n < 60_000_000_000
                    for side in runs for row in side for n in row), 'invalid duration')
        medians = [statistics.median([n for row in side for n in row]) for side in runs]
        require(value['median_ns'] == medians, 'median arithmetic')
        require(value['wall_time_reduction'] == 1 - medians[1] / medians[0], 'reduction arithmetic')
        improvements = sum(statistics.median(b) < statistics.median(a) for a, b in zip(*runs))
        result[label] = {'median_ns': medians, 'improving_batches': improvements}
    require(result['toolkit']['improving_batches'] == 9, 'primary batches do not all improve')
    return result


def summary():
    bindings()
    original_path = list(sys.path)
    try:
        sys.path.insert(0, str(ROOT / 'scripts'))
        before = load(HERE / 'baseline/export_research_package.py', 'baseline_export')
        after = load(ROOT / 'scripts/export_research_package.py', 'candidate_export')
        with tempfile.TemporaryDirectory(prefix='export-conformance-') as directory:
            result = {'conformance': conformance(before, after, directory),
                      'recorded_measurements': measured_evidence()}
    finally:
        sys.path[:] = original_path
    files = sorted(p for p in HERE.rglob('*') if p.is_file()
                   and p.name != 'RESULT.json' and '__pycache__' not in p.parts)
    require(len(files) <= 24, 'package file limit')
    result['package_sha256'] = {p.relative_to(HERE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in files}
    result['input_sha256'] = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                              for name in json.loads((HERE / 'VERIFY.json').read_text())['inputs']}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit-to', type=Path)
    args = parser.parse_args()
    result = summary()
    if args.emit_to is None:
        expected = json.loads((HERE / 'RESULT.json').read_text())
        require(canonical(result) == canonical(expected), 'generated result differs')
    else:
        target = args.emit_to.resolve()
        require(not target.is_relative_to(ROOT), 'receipt output must be external')
        with target.open('x') as stream:
            json.dump(result, stream, sort_keys=True, indent=2)
            stream.write('\n')
    print('PASS_EXPORT_SINGLE_SCAN ' + canonical(result['conformance']))


if __name__ == '__main__':
    main()
