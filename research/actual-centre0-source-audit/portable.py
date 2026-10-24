"""Private path/byte transport only; frozen scientific expressions stay unchanged.
Prepared by Chris R / Clear1nsight with substantial OpenAI Codex assistance.
Apache-2.0; predecessor credit and source notices are preserved in this package.
"""
from pathlib import Path
from hashlib import sha256
import ast
import contextlib
import io
import json
import runpy
import shutil
import sys
import tempfile
import types

HERE = Path(__file__).resolve().parent
OUTPUTS = HERE / 'evidence/outputs'


def need(ok, label):
    if not ok:
        raise ValueError(label)


def authenticate(root, manifest):
    for name, expected in manifest.items():
        p = root / name
        need(p.is_file() and not p.is_symlink(), 'Missing regular input: ' + name)
        need(sha256(p.read_bytes()).hexdigest() == expected, 'Input hash mismatch: ' + name)


def source_reader():
    requests = json.loads((HERE / 'SOURCE-REQUESTS.json').read_bytes())
    lookup = {Path(r['path']).name: r for r in requests}
    need(len(lookup) == len(requests), 'Unique source basenames')

    def read(name):
        need(name in lookup, 'Unknown frozen source request')
        r = lookup[name]
        need(r['head'] == '86e474038e05f99a76d41f71d81946ad2327e4a4', 'Original source head')
        data = (HERE / r['snapshot']).read_bytes()
        need(sha256(data).hexdigest() == r['sha256'], 'Frozen source byte mismatch')
        return data
    return read


def load_source_audit(path, read):
    # The sole AST adaptation replaces the Git byte reader, never an algebraic expression.
    tree = ast.parse(path.read_bytes(), filename=str(path))
    readers = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'read']
    need(len(readers) == 1, 'One original Git byte reader')
    reader = readers[0]
    need([x.arg for x in reader.args.args] == ['name'], 'Original read(name) ABI')
    reader.body = ast.parse('return _authenticated_blob(name)').body
    ast.fix_missing_locations(tree)
    module = types.ModuleType('check_producer_packet')
    module.__file__ = str(path)
    module.__dict__['_authenticated_blob'] = read
    exec(compile(tree, str(path), 'exec'), module.__dict__)
    return module


def same_result(stage, original):
    need(stage.read_bytes() == original.read_bytes(), 'Replay receipt differs: ' + original.name)


def run():
    # Fresh writable scratch preserves the original relative outputs hierarchy.
    # Input files can themselves be read-only; copyfile does not preserve their modes.
    with tempfile.TemporaryDirectory(prefix='actual-centre0-replay-') as d:
        root = Path(d)
        shutil.copytree(OUTPUTS, root / 'outputs', copy_function=shutil.copyfile,
                        ignore=shutil.ignore_patterns('__pycache__'))
        v = root / 'outputs/new-approach-verification-20261023'
        original = OUTPUTS / 'new-approach-verification-20261023'
        read = source_reader()
        try:
            read('../undeclared')
        except ValueError:
            pass
        else:
            raise ValueError('Unknown source request accepted')
        module = load_source_audit(v / 'check_producer_packet.py', read)
        old = sys.modules.get('check_producer_packet')
        sys.modules['check_producer_packet'] = module
        argv = sys.argv[:]
        capture = io.StringIO()
        try:
            with contextlib.redirect_stdout(capture):
                module.main()
                sys.argv = [str(v / 'check_declared_product.py')]
                runpy.run_path(sys.argv[0], run_name='__main__')
                sys.argv = [str(root / 'outputs/new-approach-ceilings-20261023/centre0-p2/check_burden.py')]
                runpy.run_path(sys.argv[0], run_name='__main__')
                sys.argv = [str(v / 'check_economic_reviews.py'), '--p2-only']
                runpy.run_path(sys.argv[0], run_name='__main__')
        finally:
            sys.argv = argv
            if old is None:
                sys.modules.pop('check_producer_packet', None)
            else:
                sys.modules['check_producer_packet'] = old
        suffix = '-OPTIMIZED' if sys.flags.optimize else ''
        for stem in ('PRODUCER-PACKET-RESULT', 'DECLARED-PRODUCT-RESULT', 'ECONOMIC-REVIEWS-P2-RESULT'):
            same_result(v / (stem + suffix + '.json'), original / (stem + suffix + '.json'))
        # The author burden checker is stdout-only. Extract its one result object
        # from the already captured transcript; do not run it again.
        transcript = capture.getvalue()
        decoder = json.JSONDecoder()
        found = []
        for i, ch in enumerate(transcript):
            if ch == '{':
                try:
                    value, end = decoder.raw_decode(transcript[i:])
                except json.JSONDecodeError:
                    continue
                if isinstance(value, dict) and 'source_derived_local_profile_matches' in value:
                    found.append(value)
        need(len(found) == 1, 'One author conditional p2 JSON receipt')
        expected = json.loads((OUTPUTS / 'new-approach-ceilings-20261023/centre0-p2/CHECK-RESULT.json').read_bytes())
        need(found[0] == expected, 'Author p2 arithmetic receipt differs')
        producer = json.loads((v / ('PRODUCER-PACKET-RESULT' + suffix + '.json')).read_bytes())
        product = json.loads((v / ('DECLARED-PRODUCT-RESULT' + suffix + '.json')).read_bytes())
        need(producer['status'] == 'PASS_SOURCE_PACKET_AUDIT_ONLY', 'Source-specification status')
        need(product['status'].startswith('REJECT'), 'Declared product placement must fail')
        return {'source_specification': producer['status'], 'declared_product': product['status'],
                'conditional_accounting': 'author and independent exact receipts match',
                'unknown_source_request_control': 'rejected', 'native_word_emitted': False,
                'complete_caller': False, 'new_kappa': None}
