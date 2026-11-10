"""Authenticate all selected source and byte-identical published A1 evidence."""
import gzip
import hashlib
import json
from pathlib import Path

from common import require

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = '7c49fe32c55de02c2c873655c804b16e4c3fef0a'
PUBLISHED = 'e56a5bcf239fa0cd4ee57459af04c0ba7acb2c03'
PINS = {'research/p104-caller-independent-audit/capsule/outputs/p104-caller-route-audit-v2-20261025/sources/DATA-PHASES.json': 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
 'research/p104-helper470-twin-rung-removal/RESULT.json': '84fcbe2a0b64307b5703c363408042bdd91555b0419509aa50daa43b3b1924ad',
 'research/p104-helper470-twin-rung-removal/WORD.json.gz': '7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f',
 'research/p104-native-channel/vendor/clifford_exact.py': '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962',
 'research/p104-productive-controller/CONTROLLER.json': 'a84f6bbd547379597464e56c420cc665f96bc43a9a1351eed4b7cd0fce3cc4b9',
 'research/p104-productive-controller/caller.py': '300d40043953e4f6aecfde8f2d1004b8ad6dc5a79ec3c7666c9908c2466c91c8',
 'research/p104-productive-controller/local.py': '878734dfd64c4b9d362d0ae476cc5c2a19fe93e48b7378763b23f3e0dd0a5a71'}
VENDOR = {'vendor/a1/NATIVE.json.gz': 'ce62443d9a4d8d73d82df3819ed25c5c3a03e7cea486b0ec83563cea53bda4b4',
 'vendor/a1/PROOF.md': 'c5581d275d90f204c1e559f0e7dcb2172c68592b6ff96411c9ad7f4003893a5b',
 'vendor/a1/RESULT.json': 'b3efd599cd80c6f0a062e9fd1557d72701a9b4be8b0d79b6d012b4cfed395457',
 'vendor/a1/SOURCES.json': '813dd728542601b021c8504c5821704617418d1f2272f2335c117a7de04449c1'}


def authenticate(path, raw, pins):
    require(path in pins and len(raw) <= 2_000_000, 'bounded declared source: '+path)
    require(hashlib.sha256(raw).hexdigest() == pins[path], 'authenticated source bytes: '+path)
    return raw


def decode(raw, compressed=False):
    if compressed:
        raw = gzip.decompress(raw)
    require(len(raw) <= 16_000_000, 'bounded decompressed source')
    return json.loads(raw)


def load():
    raw = {p: authenticate(p, (ROOT/p).read_bytes(), PINS) for p in PINS}
    vendor = {p: authenticate(p, (HERE/p).read_bytes(), VENDOR) for p in VENDOR}
    old_sources = decode(vendor['vendor/a1/SOURCES.json'])
    require({r['path']: r['sha256'] for r in old_sources['files'] if r['usage'] == 'input'} == PINS,
            'A1 theorem uses exactly these selected sources')
    provenance = json.loads((HERE/'DEPENDENCY.json').read_text())
    require(provenance['published_commit'] == PUBLISHED
            and {r['path']: r['sha256'] for r in provenance['files']} == VENDOR, 'published A1 dependency inventory')
    prior = decode(vendor['vendor/a1/RESULT.json'])
    require(prior['source_sha256'] == PINS and prior['base_commit'] == BASE, 'A1 result source closure')
    native = decode(vendor['vendor/a1/NATIVE.json.gz'], True)
    return {
        'word': decode(raw['research/p104-helper470-twin-rung-removal/WORD.json.gz'], True),
        'result': decode(raw['research/p104-helper470-twin-rung-removal/RESULT.json']),
        'controller': decode(raw['research/p104-productive-controller/CONTROLLER.json']),
        'phase': decode(raw['research/p104-caller-independent-audit/capsule/outputs/p104-caller-route-audit-v2-20261025/sources/DATA-PHASES.json']),
        'native': native, 'dependency': prior,
    }
