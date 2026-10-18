"""Source-bound bounded matvec memoization; ywz65 + OpenAI Codex, Apache-2.0."""
import argparse
from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT/'research/p104-native-channel'
CACHE_SIZE = 32768


def require(ok, why):
    if not ok:
        raise ValueError(why)


def checked_module():
    manifest = json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))
    for rec in manifest['files']:
        if rec.get('usage') == 'input':
            require(hashlib.sha256((ROOT/rec['path']).read_bytes()).hexdigest() == rec['sha256'],
                    'source drift before executable import: '+rec['path'])
    spec = importlib.util.spec_from_file_location('p104_original_checker', SOURCE/'check_native.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def replay(cached=True):
    module = checked_module()
    original = module.N.mul
    memo = lru_cache(maxsize=CACHE_SIZE)(original)
    if cached:
        module.N.mul = memo
    try:
        result = json.loads(json.dumps(module.replay(True)))
        expected = json.loads((SOURCE/'EXPECTED.json').read_text(encoding='utf-8'))
        require(result == expected, 'complete original receipt mismatch')
        stats = memo.cache_info()._asdict()
    finally:
        module.N.mul = original
        memo.cache_clear()
        module.N.action.cache_clear()
    return {'source_receipt': result, 'cache_statistics': stats,
            'cache_bound': CACHE_SIZE, 'cached': cached}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--reference', action='store_true')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = replay(not args.reference)
    if args.out:
        with args.out.open('x', encoding='utf-8', newline='\n') as out:
            json.dump(result, out, indent=2)
            out.write('\n')
    print('PASS_P104_NATIVE_MATVEC_CACHE '+json.dumps(result['cache_statistics'], sort_keys=True))
