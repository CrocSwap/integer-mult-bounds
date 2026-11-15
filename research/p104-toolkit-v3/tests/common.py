# SPDX-License-Identifier: Apache-2.0
"""Shared helpers for the toolkit tests: pinned data, #7601 word from its edit list, PASS/FAIL reporting."""
import collections
import copy
import gzip
import hashlib
import json
import sys
import time
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
DATA = PKG / 'data'
sys.path.insert(0, str(PKG))

SHA = {
    'base-7546-word.json.gz': '6e03624b173b90356e96f845d05fc93153846b863734dc8163ab6c44c602cd32',  # ToikY #7546 bytes
    'caller-7113.json.gz': None,   # gzip container; the JSON inside is pinned below
    'edits-7601.json': '05535155f82eb3e906b390fd2734ac42bd06720de2c9a4c62defc9ec9e977ed5',        # our #7601 edit list
}
CALLER_JSON_SHA = '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc'           # Rohan Arun #7113 caller

KAPPA_7546 = '0.00364841129479084532481164'
KAPPA_7601 = '0.0036490213053944204892137903671'
T0 = time.time()


def ok(cond, label):
    if not cond:
        print('FAIL ' + label, flush=True)
        sys.exit(1)
    print('ok   %s  [%.1fs]' % (label, time.time() - T0), flush=True)


def check_data():
    for name, h in SHA.items():
        if h:
            ok(hashlib.sha256((DATA / name).read_bytes()).hexdigest() == h, 'sha256 pinned: data/' + name)
    raw = gzip.decompress((DATA / 'caller-7113.json.gz').read_bytes())
    ok(hashlib.sha256(raw).hexdigest() == CALLER_JSON_SHA, 'sha256 pinned: data/caller-7113.json.gz content (#7113 caller)')


def load_gz(path):
    return json.loads(gzip.decompress(Path(path).read_bytes()))


def base_word():
    return load_gz(DATA / 'base-7546-word.json.gz')


def caller_path():
    return DATA / 'caller-7113.json.gz'


def apply_edits(W, E):
    """our #7601 edit-list format: delete [(index, event)], insert_before [(index, [events])], append [events]."""
    prog = W['program']
    assert len(prog) == E['base_events']
    dele = {}
    for i, ev in E['delete']:
        assert prog[i] == ev, ('deleted event mismatch', i)
        dele[i] = ev
    ins = collections.defaultdict(list)
    for i, evs in E['insert_before']:
        ins[i].extend(evs)
    out = []
    for i, ev in enumerate(prog):
        out.extend(ins.get(i, []))
        if i not in dele:
            out.append(ev)
    out.extend(ins.get(len(prog), []))
    W2 = copy.deepcopy(W)
    W2['program'] = out + E['append']
    return W2


def word_7601(base=None):
    return apply_edits(base or base_word(), json.loads((DATA / 'edits-7601.json').read_text()))
