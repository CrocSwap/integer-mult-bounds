"""Replay the independent phase certificate and the actual source consumer.

Prepared with substantial OpenAI Codex assistance. Apache-2.0.
"""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import runpy
from types import SimpleNamespace
from audit import audit, core, need

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PHASES = 'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/sources/DATA-PHASES.json'

def digest(records):
    return hashlib.sha256(json.dumps(records, separators=(',', ':')).encode()).hexdigest()

def authenticate(data, expected):
    need(hashlib.sha256(data).hexdigest() == expected, 'source byte mismatch')

def reject(fn, why):
    try:
        fn()
    except (ValueError, AssertionError):
        return
    raise ValueError('control accepted: ' + why)

def main():
    sources = json.loads((HERE/'SOURCES.json').read_bytes())
    for row in sources['files']:
        if row['usage'] == 'input':
            authenticate((ROOT/row['path']).read_bytes(), row['sha256'])
    caller = json.loads((ROOT/'research/balanced-query-tree/CONTROLLER.json').read_bytes())
    phases = json.loads((ROOT/PHASES).read_bytes())
    word = json.loads(gzip.decompress((ROOT/'research/p104-native-input-lifting/WORD.json.gz').read_bytes()))
    records = audit(caller, phases, word['ports'])
    expected = json.loads((HERE/'RESULT.json').read_bytes())
    need(len(records) == 1976 and digest(records) == expected['contact_sha256'], 'independent records')
    # Run the original consumer unchanged, using its original phase backend.
    # It is a comparison oracle, never the implementation of audit.py.
    L = SimpleNamespace(ROOT=ROOT, need=need,
        read=lambda p: json.loads(p.read_bytes()),
        load=lambda p, name: SimpleNamespace(**runpy.run_path(str(p))))
    consumer = runpy.run_path(str(ROOT/'research/balanced-query-tree/physical.py'))['physical']
    result = consumer(caller, word, L)
    need(result['route_payload_sha256'] == digest(records), 'actual consumer contact digest')
    need(result['physical_contacts'] == 7904 and result['full_calls'] == 19, 'actual consumer counts')
    receipt = json.loads((ROOT/'research/balanced-query-tree/RESULT.json').read_bytes())
    need(json.loads(json.dumps(result)) == receipt['physical'], 'fresh consumer differs from source receipt')

    # A tilted source basis must fail the physical contact requirements.
    probe = next(r for r in phases['recipes'] if r['q'] == 11)
    basis = probe['idle_children'][0]['orthogonal_axes'][:8]
    wrong = basis[:]
    wrong[0] ^= 1
    reject(lambda: core(11, wrong), 'tilted basis')
    for index in (0, 9, 18):
        c = copy.deepcopy(caller)
        local = [e for e in c['events'] if e[0] == 'LOCAL']
        local[index][1] = 1 if index else 2
        reject(lambda: audit(c, phases, word['ports']), 'wrong stage')
    damaged = copy.deepcopy(phases)
    next(r for r in damaged['recipes'] if r['q'] == 11)['idle_children'][0]['orthogonal_axes'][0] ^= 1
    reject(lambda: audit(caller, damaged, word['ports']), 'actual input basis')
    row = next(r for r in sources['files'] if r['usage'] == 'input')
    reject(lambda: authenticate((ROOT/row['path']).read_bytes()+b' ', row['sha256']), 'changed source byte')
    damaged_records = copy.deepcopy(records)
    damaged_records[-1][2][0]['translation'] ^= 1
    reject(lambda: need(digest(damaged_records) == result['route_payload_sha256'], 'translation ledger'),
           'one changed translation')
    # The source consumer itself must not match when its port order is changed.
    reordered = dict(word, ports=list(reversed(word['ports'])))
    different = consumer(caller, reordered, L)
    reject(lambda: need(different['route_payload_sha256'] == digest(records), 'consumer port order'),
           'consumer binding')
    print(json.dumps({'status':'PASS_P104_ALL_STAGE_CONTACTS', 'stages':19, 'ports':104,
                      'contacts':7904, 'contact_sha256':digest(records),
                      'actual_consumer':'fresh source physical.py with original backend',
                      'scope':'LOCAL contact phases only; no supplier/all-column/outer admission'}, sort_keys=True))

if __name__ == '__main__':
    main()
