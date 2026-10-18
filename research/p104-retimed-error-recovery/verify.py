"""Source-bound conditional precision/recovery certificate; standard library only."""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import types

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
M = types.ModuleType('retimed_response')
exec(compile((P / 'model.py').read_bytes(), str(P / 'model.py'), 'exec'), M.__dict__)


def load():
    pins = json.loads((P / 'SOURCES.json').read_text())
    for pin in pins['files']:
        if pin['usage'] != 'input':
            continue
        raw = (ROOT / pin['path']).read_bytes()
        M.need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source SHA256: ' + pin['path'])
        blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
        M.need(hashlib.sha1(blob).hexdigest() == pin['git_blob'], 'source blob: ' + pin['path'])
    return json.loads((ROOT / 'research/p104-dual-add-retiming/WORD.json').read_text())


def sign(value):
    return Q(1) if value > 0 else Q(-1)


def prove_rows(word, response):
    """Check every final response coefficient and each peak/private response."""
    program, public = word['program'], word['initial_frames']
    total = 0
    for role, expected in response['final'].items():
        actual = M.adjoint(program, len(program), role, public)
        M.need(actual == expected, 'endpoint forward/adjoint: ' + role)
        total += len(actual[0]) + len(actual[1])
    for key, expected in response['snapshots'].items():
        if key[0] == 'peak':
            peak = response['peaks'][key[1]]
            cut, role = peak['cut'], peak['role']
        else:
            cut, role = key
        M.need(M.adjoint(program, cut, role, public) == expected, 'cut forward/adjoint')
    return total


def witnesses(word, response):
    result = {}
    for key, peak in response['peaks'].items():
        inputs, errors = response['snapshots'][('peak', key)]
        initial, defects = {}, {}
        if key == 'P':
            initial = {i: sign(v) for i, v in inputs.items()}
        else:
            weights = {'A': None, 'K': response['weights'], 'J': response['operand'],
                       'N': response['native']}[key]
            defects = {i: sign(v) * (weights[i] if weights else 1)
                       for i, v in errors.items()}
        state, _ = M.literal(word['program'], peak['cut'], word['initial_frames'], initial, defects)
        M.need(state[peak['role']] == peak['value'], 'attaining independent fixture: ' + key)
        result[key] = {'cut': peak['cut'], 'role': peak['role'], 'value': str(peak['value']),
                       'response_terms': len(inputs) if key == 'P' else len(errors)}
    return result


def recovery_controls(word, response):
    spacing = Q(1, 128)
    for erasure in response['erasures']:
        cut, role = erasure['cut'], erasure['role']
        _, errors = response['snapshots'][(cut, role)]
        # Each private residual can be nonzero despite ideal exact cleanup.
        size = M.norm(errors)
        defects = {i: sign(v) * spacing / (4 * size) for i, v in errors.items()}
        state, _ = M.literal(word['program'], cut, word['initial_frames'], {}, defects)
        M.need(state[role] == spacing / 4, 'private nonzero residual fixture')
        M.need(M.nearest(state[role], spacing) == 0, 'strict private recovery')
    for value in (spacing / 2, -spacing / 2):
        try:
            M.nearest(value, spacing)
        except ValueError:
            pass
        else:
            raise ValueError('half-grid ambiguity accepted')
    M.need(M.nearest(51 * spacing / 100, spacing) == spacing, 'outside-radius control')
    # An escaped private defect is retained in public output response rows.
    private_sites = [i for i, e in enumerate(word['program'])
                     if e[1] == 'C' and e[0] in ('add', 'transport')]
    escaped = [(role, i, row[i]) for role, (_, row) in response['final'].items()
               for i in private_sites if row.get(i)]
    M.need(escaped, 'discard incorrectly removes exported private errors')
    role, site, coefficient = escaped[0]
    state, _ = M.literal(word['program'], len(word['program']), word['initial_frames'], {}, {site: Q(1)})
    M.need(state[role] == coefficient != 0, 'escaped private literal fixture')
    return {'private_residuals': 8, 'half_grid_rejections': 2,
            'outside_radius': True, 'escaped_private': [role, site, str(coefficient)]}


def certificate(word):
    response = M.replay(word)
    source = json.loads((ROOT / 'research/p104-dual-add-retiming/RESULT.json').read_text())['candidate']
    M.need(response['counts'] == source['counts'], 'source event census')
    M.need({str(k): v for k, v in response['profile'].items()} == source['profile'], 'source rank census')
    endpoint = {r: {s: str(v) for s, v in row.items()}
                for r, (row, _) in response['final'].items()}
    encoded = json.dumps(endpoint, sort_keys=True, separators=(',', ':')).encode()
    M.need(hashlib.sha256(encoded).hexdigest() == source['endpoint_sha256'], 'source complete ideal map')
    checked = prove_rows(word, response)
    attained = witnesses(word, response)
    controls = recovery_controls(word, response)
    J, K = (response['peaks'][k]['value'] for k in ('J', 'K'))
    JC = max(Q(e['J']) for e in response['erasures'])
    KC = max(Q(e['K']) for e in response['erasures'])
    g = 0
    while 2 ** g <= J + K:
        g += 1
    M.need(J > 2 ** (g - 1), 'minimal sufficient-formula uniform margin')
    # F>=7, h>=0 => private u<=2^(-F-h-9)<=2^-16.
    u0 = Q(1, 2 ** 16)
    private_bound = JC + KC * u0 * J / (1 - u0 * K)
    M.need(u0 * K < 1 and private_bound < 256 and JC > 128, 'private recovery bound')
    return {'status': 'PASS_P104_RETIMED_ERROR_RECOVERY', 'events': len(word['program']),
            'public_inputs': len(word['initial_frames']), 'defect_sites': len(response['weights']),
            'profile': {str(k): v for k, v in sorted(response['profile'].items())},
            'peaks': attained, 'endpoint_sha256': source['endpoint_sha256'],
            'endpoint_response_coefficients_checked': checked, 'erasures': response['erasures'],
            'all_cut_score_sha256': response['all_cut_score_sha256'],
            'J_plus_K': str(J + K), 'uniform_sufficient_guard': g,
            'private_J': str(JC), 'private_K': str(KC),
            'private_amplification_at_u_2neg16': str(private_bound),
            'private_recovery_u': '2^(-F-h-9)', 'all_output_recovery_u': '2^(-F-h-14)',
            'controls': controls,
            'scope': 'Conditional completed-update Hilbert defects and exact nearest-grid recovery; no rounded-child, cost, supplier or kappa admission.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', type=Path)
    args = parser.parse_args()
    result = certificate(load())
    if args.write_result:
        with args.write_result.open('x') as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write('\n')
    else:
        M.need(result == json.loads((P / 'RESULT.json').read_text()), 'complete receipt mismatch')
    print(result['status'], 'J=' + result['peaks']['J']['value'],
          'K=' + result['peaks']['K']['value'], 'zero_recoveries=8 no_new_kappa')


if __name__ == '__main__':
    main()
