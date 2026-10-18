"""Authenticate unchanged predecessor bytes before importing implementations."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load():
    for manifest, base in [('SOURCES.json', ROOT), ('VENDOR.json', HERE)]:
        for row in json.loads((HERE / manifest).read_text())['files']:
            if row.get('usage', 'input') != 'input':
                continue
            raw = (base / row['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source hash ' + row['path'])
            need(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'], 'source blob')
    prefix = 'candidate/strict/global/'
    suffixes = {'recipes':'base/providers/gauge44/CLIFFORD-RECIPES.json',
                'word':'base/providers/gauge44/CANONICAL-WORD.json.gz',
                'programs':'base/providers/gauge44/LOCAL-PROGRAMS.json.gz',
                'template':'hosted/GLOBAL-TEMPLATE.json.gz',
                'invoice':'audit/PREFIX-AND-INVOICE.json'}
    data, pins = {}, {}
    with tarfile.open(ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz') as archive:
        for key, suffix in suffixes.items():
            raw = archive.extractfile(prefix + suffix).read()
            pins[suffix] = hashlib.sha256(raw).hexdigest()
            data[key] = json.loads(gzip.decompress(raw) if suffix.endswith('.gz') else raw)
    invoice = data['invoice']['providers']['gauge44']['artifacts']
    for suffix, digest in pins.items():
        if '/providers/gauge44/' in suffix:
            need(invoice[suffix.rsplit('/', 1)[-1]] == digest, 'selected invoice member')
    need(data['template']['local_providers']['gauge44']['local_programs'] == data['programs'], 'selected literal word')
    recipe = data['recipes']['children'][1522]
    need((recipe['old'], recipe['new'], recipe['rank']) == (415, 0, 8), 'actual child1522')
    need(data['programs']['forward'][12553] == ['center', 0, 415, 0, 8], 'actual center event12553')
    frame = data['word']['frames'][415]
    need(len(frame) == 8 and data['word']['frames'][0] == [], 'actual inverse frame')
    sys.path.insert(0, str(HERE / 'vendor'))
    return recipe, frame, pins
