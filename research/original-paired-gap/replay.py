"""Replay the fixed paired-gap package into an explicit output directory.

Python 3.10+, the standard library, and Git are required. New code is
Apache-2.0. OpenAI Codex assisted the research and implementation.
"""

from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import importlib.util
import json


HERE = Path(__file__).resolve().parent
CORE_PIN = 'f271842a741584389e166e700e262f161b0dd570ce8c7a540f2717e90ead5205'
PAIR_PIN = '42aeb0902d8b2330f9050718c6d949993111a9fd898acad599ec867bb63a2b20'


def need(value, message):
    if not value:
        raise ValueError(message)


def module(name):
    path = HERE / (name + '.py')
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def payload(name, expected):
    raw = gzip.decompress((HERE / 'data' / name).read_bytes())
    need(sha256(raw).hexdigest() == expected, 'Decompressed payload pin: ' + name)
    return json.loads(raw)


def write_json(path, value):
    raw = (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()
    path.write_bytes(raw)
    return sha256(raw).hexdigest()


def main(args):
    output = args.out.resolve()
    need(output != HERE and HERE not in output.parents, 'Use an output directory outside the package')
    sources = json.loads((HERE / 'SOURCES.json').read_bytes())
    inputs = {}
    for item in sources['copied_files']:
        name = item['file']
        raw = (HERE / name).read_bytes()
        need(sha256(raw).hexdigest() == item['sha256'], 'Pinned source differs: ' + name)
        inputs[name] = item['sha256']
    source = module('source_data')
    local = source.load_local(args.repo)
    cores = payload('FULL-MODE-PROGRAMS.json.gz', CORE_PIN)
    pair = payload('PAIRED-PROGRAMS.json.gz', PAIR_PIN)
    need(pair['schema'] == 'paired-original-complex-endpoint-graphs-v1', 'Fixed packet schema')
    need(pair['core_payload_sha256'] == CORE_PIN, 'Paired core binding')
    scalar, r, k = module('verify_pair').verify(local, cores, pair, source)
    print(scalar['status'], flush=True)
    lines = json.loads((HERE / 'data' / 'INPUT-LINES.json').read_bytes())
    native = module('verify_native').verify(local, lines, pair, r)
    print(native['status'], flush=True)
    algebra = module('verify_algebra').verify(r, k)
    print(algebra['status'], flush=True)
    output.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for name, value in [('PAIR-CHECKS.json', scalar), ('NATIVE-CHECKS.json', native), ('ALGEBRA-CHECKS.json', algebra)]:
        outputs[name] = write_json(output / name, value)
    result = {
        'status': 'PASS_PORTABLE_ORIGINAL_PAIRED_GAP',
        'source': source.source_manifest(), 'copied_input_sha256': inputs,
        'program_payload_sha256': PAIR_PIN, 'core_payload_sha256': CORE_PIN,
        'code_sha256': {name: sha256((HERE / name).read_bytes()).hexdigest()
                        for name in ('source_data.py', 'verify_pair.py', 'verify_native.py', 'verify_algebra.py', 'replay.py')},
        'source_manifest_sha256': sha256((HERE / 'SOURCES.json').read_bytes()).hexdigest(),
        'output_sha256': outputs,
        'fresh_checks': ['All 704 raw core input columns and 1408 paired input columns',
                         'Arbitrary modes, ordinary helper restoration, private non-use, both algebraic inverse orders',
                         'Exact 57344 line columns and 1008 source-derived affine routes',
                         'Ordered physical groups, literal local costs, general monomial-square identities and controls'],
        'inherited_or_not_run': ['Retained core native kernels and full helper interface are inherited',
                                 'Owner binding and one-shot mode histories are separately reviewed and not replayed here',
                                 'No complete global native word, final H/G access, coupled decoder, finite invoice, or supplier admission',
                                 'No repository-wide test suite or kappa calculation'],
    }
    write_json(output / 'REPLAY.json', result)
    print(result['status'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    main(parser.parse_args())
