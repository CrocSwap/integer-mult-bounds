"""Restore exact frozen scientific bytes from the lossless publication transport."""
from pathlib import Path
from hashlib import sha256
import gzip
import json
import os

P = Path(__file__).resolve().parent
RAW = 'sources/experiments/architecture/whole-owner-pooling-v4/bit60/HOSTED-SIGMA.json'
RAW_SHA = 'c2303b1ecb3428ff586fc3db6b52f814b406a88f30ddc38a7d945227bfe3ee3f'
RAW_SIZE = 140028853
GZIP_SHA = '71d4d5c3a2e98557b0ea9c9a90182762fd197087bff64fb4b5db0cc89a6acd76'
SCIENCE_MANIFEST_SHA = '958a08ac4663e85a2bce573acbf3c60b0f3a83250d7d4fdee7c7d72eae29eef8'
def sha(path):
    h = sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1048576), b''):
            h.update(chunk)
    return h.hexdigest()

assert __debug__, 'Assertions must be enabled.'
assert sha(P/'SOURCE-MANIFEST.json') == SCIENCE_MANIFEST_SHA
science = json.loads((P/'SOURCE-MANIFEST.json').read_text())
assert len(science['files']) == 1130 and science['files'][RAW] == RAW_SHA
transport = json.loads((P/'TRANSPORT-MANIFEST.json').read_text())
assert transport['status'] == 'LOSSLESS_TRANSPORT_OF_FROZEN_POOLED60_V2'
assert transport['science_manifest_sha256'] == SCIENCE_MANIFEST_SHA
assert transport['raw_path'] == RAW and transport['raw_sha256'] == RAW_SHA
assert transport['compressed_sha256'] == GZIP_SHA and transport['raw_bytes'] == RAW_SIZE
expected = (set(science['files']) - {RAW}) | {
    'SOURCE-MANIFEST.json', RAW+'.gz', 'materialize.py', 'TRANSPORT.md'}
assert set(transport['files']) == expected
for name, item in transport['files'].items():
    relative = Path(name)
    assert not relative.is_absolute() and '..' not in relative.parts
    assert sha(P/name) == item['sha256'], name
    mode = '100755' if (P/name).stat().st_mode & 0o111 else '100644'
    assert mode == item['mode'], name
assert sha(P/(RAW+'.gz')) == GZIP_SHA
target = P/RAW
if not target.exists():
    temporary = target.with_name(target.name+'.materializing')
    assert not temporary.exists(), 'Inspect leftover materialization before retry.'
    try:
        h = sha256()
        size = 0
        with gzip.open(P/(RAW+'.gz'), 'rb') as src, temporary.open('xb') as dst:
            for chunk in iter(lambda: src.read(1048576), b''):
                size += len(chunk)
                assert size <= RAW_SIZE
                h.update(chunk)
                dst.write(chunk)
        assert size == RAW_SIZE and h.hexdigest() == RAW_SHA
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()
assert target.stat().st_size == RAW_SIZE and sha(target) == RAW_SHA
for name, checksum in science['files'].items():
    assert sha(P/name) == checksum, name
print(json.dumps({'status':'PASS_EXACT1130_FROZEN_SCIENCE_FILES_MATERIALIZED',
    'source_manifest_sha256':SCIENCE_MANIFEST_SHA,'raw_sigma_sha256':RAW_SHA,
    'raw_sigma_bytes':RAW_SIZE,'bound_files':1130}))
