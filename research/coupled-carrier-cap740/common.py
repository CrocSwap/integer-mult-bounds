# SPDX-License-Identifier: Apache-2.0
"""Pinned inputs shared by the new allocation, materializer and finite checks.

Jeremy Diviney, with substantial OpenAI Codex assistance. Mathematical engines
are the exact credited predecessor bytes identified in VENDOR/SOURCE-PINS.
"""
import collections
import gzip
import hashlib
import json
from pathlib import Path
import types

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
MAIN = ROOT / 'research/rank7-joint-endframes'
HEAD = '51eb9c4ee9e4722010d308aa3309e039d3940cc2'
LOCAL = {1: 2433, 2: 724, 3: 228, 4: 102, 5: 20, 8: 8}
INVENTORY = {4: 26, 5: 2, 6: 18, 7: 50, 8: 99, 9: 213}
IDLE = {1: 173160, 3: 48951, 5: 13875, 48: 282569}
PROFILE = {1: 16376940, 2: 4821840, 3: 1567431, 4: 679320,
           5: 147075, 8: 53280, 48: 282569}
DELTA = {1: 20, 3: 21, 5: -25, 39: -10, 48: 9}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def load(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def authenticate():
    paths = list(P.rglob('*'))
    need(not any(path.is_symlink() for path in paths), 'regular package files')
    actual = {path.relative_to(P).as_posix(): sha(path)
              for path in paths if path.is_file() and path != P/'MANIFEST.json'}
    need(actual == read(P/'MANIFEST.json'), 'complete published package inventory')
    for path, expected in read(P/'SOURCE-PINS.json').items():
        need(sha(ROOT/path) == expected, 'external source ' + path)
    for record in read(P/'VENDOR.json'):
        need(sha(P/record['path']) == record['sha256'], 'vendor source ' + record['path'])


def context():
    c = types.SimpleNamespace()
    c.lift = load(P/'vendor/lift.py', 'retained_lift')
    c.owner = load(MAIN/'allocation/vendor/independent_owners.py', 'retained_owners')
    c.cap = load(P/'cap_check.py', 'adapted_cap')
    c.base = read(P/'vendor/PR3133-FILL.json.gz')['rows']
    c.order = read(MAIN/'allocation/ORDER.json')
    c.dispatch = {(s, r): key for s, r, key in read(MAIN/'allocation/DISPATCH.json')}
    c.providers = read(P/'vendor/PR3133-PROVIDERS.json')
    c.widths = [c.providers[c.dispatch[tuple(call)]]['widths'] for call in c.order]
    c.plan = read(MAIN/'allocation/vendor/PLAN.json.gz')
    c.template = read(MAIN/'allocation/vendor/TEMPLATE.json.gz')
    c.win = c.owner.windows(c.template, c.order, 74)
    c.families = {int(child): 2*pair+c.plan['sides'][child]
                  for child, pair in c.plan['pairs'].items()}
    c.bins = collections.defaultdict(list)
    for index, row in enumerate(c.base):
        c.bins[tuple(row[2:5])].append(index)
    c.pattern = lambda key: (c.win[key[:2]][0], tuple(sorted(
        c.widths[c.base[i][0]][c.base[i][1]] for i in c.bins[key])))
    return c


def witness(c):
    journal = read(P/'EXCHANGE.json')
    need(journal['base_head'] == HEAD, 'journal source head')
    need(journal['base_fill_sha256'] == sha(P/'vendor/PR3133-FILL.json.gz'), 'journal source fill')
    need(len(journal['edits']) == 145, 'complete new exchange')
    edits = c.lift.patch(c.base, journal)
    order, dispatch = c.lift.chronology(c.order, c.dispatch)
    return c.lift.Rows(c.base, edits), order, dispatch, edits
