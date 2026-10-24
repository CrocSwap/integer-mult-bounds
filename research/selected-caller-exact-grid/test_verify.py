"""Rejecting controls for verify.py.  Each mutation must raise SystemExit('FAIL...')."""
import copy
import gzip
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify as V  # noqa: E402

spec = importlib.util.spec_from_file_location('selected_caller_test_ce', V.CLIFFORD)
CE = importlib.util.module_from_spec(spec); spec.loader.exec_module(CE)
BODY = json.loads(V.BODY.read_text(encoding='utf-8'))
CALLER = json.loads(V.CALLER.read_text(encoding='utf-8'))
PROV = json.loads((V.PROV / 'PROVIDER.json').read_text(encoding='utf-8'))
WORD = json.loads(gzip.decompress((V.PROV / 'WORD.json.gz').read_bytes()))
CAN = json.loads(gzip.decompress(V.EIGHT.read_bytes()))['canonical']
OPS = V.Ops(CE, CAN, json.loads(V.NORM.read_text(encoding='utf-8')))
V.Body.ops_ref = OPS


def rejects(name, fn):
    try:
        fn()
    except SystemExit as exc:
        if not str(exc).startswith('FAIL'):
            raise
        print('rejected:', name)
        return
    raise AssertionError('control accepted: ' + name)


def drift():
    rows = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    row = next(r for r in rows['files'] if r['usage'] == 'input')
    data = (V.ROOT / row['path']).read_bytes()
    V.require(V.hashlib.sha256(data).hexdigest() == '0' * 64, 'input drift: ' + row['path'])


def odd_division():
    body = copy.deepcopy(BODY)
    next(o for o in body['operations'] if o['op'] == 'ADD')['coefficient'] = '1/3'
    B = V.Body(body, PROV, WORD, CAN); B.run()
    V.require(B.odd == 0, 'every coefficient of the complete body is dyadic')


def broken_block_inverse():
    body = copy.deepcopy(BODY)
    idx = [i for i, o in enumerate(body['operations']) if o['op'] == 'MONOMIAL' and 'purpose' not in o and 'whole_job_boundary' not in o]
    body['operations'][idx[200]]['word'] = [['X', 1]]
    V.monomial_block_is_identity(body, OPS)


def missing_q_power():
    caller = copy.deepcopy(CALLER)
    ev = caller['controller']['physical_events']
    ev.pop(next(i for i, e in enumerate(ev) if e[0] == 'Q_POWER'))
    V.laurent(caller['controller'])


def missing_owned_clear():
    body = copy.deepcopy(BODY)
    ops = body['operations']
    ops.pop(max(k for k, o in enumerate(ops) if o['op'] == 'CLEAR'))
    B = V.Body(body, PROV, WORD, CAN); B.run()


def tampered_result():
    stored = json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8'))
    stored['controller']['guard'] = 72
    V.require(stored['controller']['guard'] == 73, 'stored RESULT.json equals the rebuild')


for name, fn in [('drifted input hash', drift), ('an odd division in a body ADD', odd_division),
                 ('a block map that is not inverted', broken_block_inverse),
                 ('a missing controller Q_POWER', missing_q_power), ('a missing owned CLEAR', missing_owned_clear),
                 ('tampered RESULT.json', tampered_result)]:
    rejects(name, fn)
print('PASS_SELECTED_CALLER_EXACT_GRID_CONTROLS')
