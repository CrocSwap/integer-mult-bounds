"""Independent all-cut covectors and operand weights; no forward replay used."""
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import types

P = Path(__file__).resolve().parent
def run(word, model):
    program, public = word['program'], word['initial_frames']
    magnitudes = {r: Q(1) for r in public}
    weights = {'K': {}, 'J': {}, 'N': {}}
    maxima = {k: Q(1) if k == 'P' else Q(0) for k in ('P', 'A', 'K', 'J', 'N')}
    locations, digest = {}, hashlib.sha256()
    checked = 0
    for index, event in enumerate(program):
        op, role, *args = event
        if op == 'zero':
            magnitudes[role] = Q(0)
            continue
        if op == 'erase':
            del magnitudes[role]
            continue
        if op == 'add':
            source, scalar, _ = args
            weights['K'][index] = 1 + abs(Q(scalar))
            weights['J'][index] = magnitudes[role] + abs(Q(scalar)) * magnitudes[source]
            weights['N'][index] = Q(0)
        elif op == 'transport':
            weights['K'][index] = weights['N'][index] = Q(1)
            weights['J'][index] = magnitudes[role]
        initial, errors = model.adjoint(program, index + 1, role, public)
        scores = {'P': sum(map(abs, initial.values()), Q(0)),
                  'A': sum(map(abs, errors.values()), Q(0))}
        for key in weights:
            scores[key] = sum((abs(c) * weights[key][j] for j, c in errors.items()), Q(0))
        magnitudes[role] = scores['P']
        for key, value in scores.items():
            if value > maxima[key]:
                maxima[key], locations[key] = value, (index + 1, role)
        payload = [index + 1, role, {key: str(v) for key, v in scores.items()}]
        digest.update((json.dumps(payload, sort_keys=True) + '\n').encode())
        checked += 1
    return maxima, locations, digest.hexdigest(), checked


def main():
    # The common authentication entry point is loaded from source bytes.
    verifier = types.ModuleType('recovery_verify')
    verifier.__file__ = str(P / 'verify.py')
    exec(compile((P / 'verify.py').read_bytes(), verifier.__file__, 'exec'), verifier.__dict__)
    result = json.loads((P / 'RESULT.json').read_text())
    maxima, locations, digest, checked = run(verifier.load(), verifier.M)
    expected = {k: Q(v['value']) for k, v in result['peaks'].items()}
    verifier.M.need(maxima == expected, 'independent all-cut maxima')
    for key, location in locations.items():
        peak = result['peaks'][key]
        verifier.M.need(location == (peak['cut'], peak['role']), 'first attaining all-cut location')
    verifier.M.need(digest == result['all_cut_score_sha256'], 'complete all-cut score digest')
    verifier.M.need(checked == 5252, 'all non-lifetime events')
    print('PASS_P104_RETIMED_REVERSE_ALL_CUTS', 'cuts=' + str(checked), digest)


if __name__ == '__main__':
    main()
