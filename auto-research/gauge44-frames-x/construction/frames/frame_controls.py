#!/usr/bin/env python3
"""Focused native controls for the eight B-frame raises (PR741's extras/frame_controls.py, ported).

usage: frame_controls.py WORD.json.gz ROUTING.json.gz OUT.json RECIPE.json   (env PR635_CODE = PR635's code/ directory)

The positive word must pass PR635's unchanged native audit `hpe_audit_and_transport.run`. Ten mutants must be rejected
at their pinned reasons: each of the eight raised gates with its frame emptied ('nonmonotone'), a doubled read
coefficient on the first raised gate ('arbitrary-dirt endpoint') and a tampered paid profile ('paid local profile
differs'). Apache-2.0; adapted from chafreaky's PR741.
"""
import copy, gzip, importlib.util, json, os, sys, tempfile, time
from pathlib import Path

_s = importlib.util.spec_from_file_location('audit', Path(os.environ['PR635_CODE']) / 'hpe_audit_and_transport.py')
A = importlib.util.module_from_spec(_s); _s.loader.exec_module(A)


def main():
    assert __debug__, 'Assertions are required'
    word, routing, out, rfile = map(Path, sys.argv[1:5])
    w = json.loads(gzip.decompress(word.read_bytes())); recipe = json.loads(rfile.read_text())

    def trial(z):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td); f = d / 'word.json.gz'; f.write_bytes(gzip.compress(json.dumps(z).encode(), mtime=0))
            try:
                A.run(f, routing, d / 'native'); return None
            except AssertionError as e:
                return str(e)

    start = time.monotonic(); assert trial(w) is None, 'positive word rejected'; records = []
    for section, i, old, new in recipe['gate_frames']:
        z = copy.deepcopy(w); z[section][i][-1] = []; error = trial(z)
        assert error and 'nonmonotone' in error, (i, error); records.append(dict(name='frame-%d-emptied' % i, rejected=error))
    z = copy.deepcopy(w); i = recipe['gate_frames'][0][1]; z['B'][i][3] *= 2; error = trial(z)
    assert error and 'arbitrary-dirt endpoint' in error, error; records.append(dict(name='changed-read-coefficient', rejected=error))
    z = copy.deepcopy(w); z['report']['local_profile']['1'] += 1; error = trial(z)
    assert error and 'paid local profile differs' in error, error; records.append(dict(name='paid-profile-tampering', rejected=error))
    out.write_text(json.dumps(dict(status='PASS_FOCUSED_EIGHT_FRAME_NATIVE_CONTROLS', positive=1, rejected=records,
                                   seconds=time.monotonic() - start), indent=2) + '\n')
    print('PASS', len(records), 'mutations', flush=True)


if __name__ == '__main__':
    main()
