"""Rejecting controls for verify.py.  Each mutation must raise SystemExit('FAIL...')."""
import copy
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify as V  # noqa: E402

CE = V.load_clifford()
BODY = json.loads(V.BODY.read_text(encoding='utf-8'))
CALLER = json.loads(V.CALLER.read_text(encoding='utf-8'))
PLAN = json.loads(V.PLAN.read_text(encoding='utf-8'))
PROV = json.loads((V.PROV / 'PROVIDER.json').read_text(encoding='utf-8'))
WORD = json.loads(gzip.decompress((V.PROV / 'WORD.json.gz').read_bytes()))
CAN = json.loads(gzip.decompress(V.EIGHT.read_bytes()))['canonical']
NORM = json.loads(V.NORM.read_text(encoding='utf-8'))


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


def wrapper_phase():
    nz = copy.deepcopy(NORM)
    word = nz['ports'][7]['compiled_wrappers']['backward_input_X']['word']
    ph = next(e for e in word if e[0] == 'phase'); ph[1] = (ph[1] + 1) % 4
    V.port_bindings(V.Ops(CE, CAN, nz))


def mixed_convention():
    ops = V.Ops(CE, CAN, NORM)
    ops.conj = lambda op: op          # read the backward wrappers against unconjugated charts
    V.port_bindings(ops)


def leftover_warp():
    word = copy.deepcopy(WORD)
    ev = next(e for e in word['word'] if e[0] == 'warp' and e[1][0] == 'L' and e[1][1] < 112)
    word['word'].remove(ev)           # its inverse partner no longer cancels
    B = V.Body(BODY, PROV, word, CAN); B.run()
    V.body_endpoint(B, V.Ops(CE, CAN, NORM))


def owned_not_cleared():
    body = copy.deepcopy(BODY)
    body['operations'] = [o for o in body['operations'] if o['op'] != 'CLEAR']
    B = V.Body(body, PROV, WORD, CAN); B.run()


def overlapping_planes():
    plan = copy.deepcopy(PLAN)
    plan['stage_embeddings'][1]['local_axes'] = plan['stage_embeddings'][0]['local_axes']
    V.controller_realization(V.Ops(CE, CAN, NORM), CALLER, plan)


def missing_q_power():
    caller = copy.deepcopy(CALLER)
    ev = caller['controller']['physical_events']
    ev.pop(next(i for i, e in enumerate(ev) if e[0] == 'Q_POWER'))
    V.laurent(caller['controller'])


def tampered_result():
    stored = json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8'))
    bad = copy.deepcopy(stored); bad['port_bindings']['group_identities'] = 895
    V.require(bad == stored, 'stored RESULT.json equals the rebuild')


def main():
    rejects('input drift', drift)
    rejects('wrapper phase mutation (port 7)', wrapper_phase)
    rejects('mixed orientation convention', mixed_convention)
    rejects('leftover native warp at the endpoint', leftover_warp)
    rejects('owned field not cleared', owned_not_cleared)
    rejects('overlapping private planes', overlapping_planes)
    rejects('missing controller Q_POWER', missing_q_power)
    rejects('tampered RESULT.json', tampered_result)
    print('PASS_ALLWIDTH_CALLER_CERTIFICATE_CONTROLS')


if __name__ == '__main__':
    main()
