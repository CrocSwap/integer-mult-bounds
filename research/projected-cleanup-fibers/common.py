"""Strict input binding and deterministic receipts; standard library only."""
import gzip
import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WORD = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
CHECKER = 'research/e8-bit-p111-tuned/code/xcheck_p.py'
EXPORTER = 'research/e8-bit-carrier-skeleton/code/bit/export_records.py'
GUARDS = 'research/r439-bsection-stars-seed01/verify.py'
INPUTS = {WORD, CHECKER, EXPORTER, GUARDS}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def decode(raw):
    def pairs(items):
        out = {}
        for k, v in items:
            need(k not in out, 'duplicate JSON key: '+k)
            out[k] = v
        return out
    def bad(x):
        raise ValueError('nonfinite JSON: '+x)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad)


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return decode(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def canonical(value):
    # Dict keys are normalized before sorting, so JSON round trips are stable.
    def normalize(x):
        if isinstance(x, dict):
            out = {}
            for k, v in x.items():
                need(type(k) in (int, str), 'unsupported JSON key')
                need(str(k) not in out, 'colliding JSON keys')
                out[str(k)] = normalize(v)
            return out
        if isinstance(x, (tuple, list)):
            return [normalize(v) for v in x]
        return x
    return json.dumps(normalize(value), sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')


def sources():
    rows = [r for r in read(PACKAGE/'SOURCES.json')['files'] if r['usage'] == 'input']
    need(len(rows) == len(INPUTS) and {r['path'] for r in rows} == INPUTS, 'live source inventory')
    for r in rows:
        need(sha(ROOT/r['path']) == r['sha256'], 'source drift: '+r['path'])
    return {r['path']: r['sha256'] for r in rows}
