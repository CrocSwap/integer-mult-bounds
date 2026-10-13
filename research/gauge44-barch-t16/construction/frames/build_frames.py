#!/usr/bin/env python3
"""Apply the eight pinned B-gate frame raises of FRAME-RECIPE-sw4.json (chafreaky's PR741) to the SW4 word.

usage: build_frames.py INPUT_WORD.json.gz OUT_DIR RECIPE.json

Standard library only. The frames are applied by BlockInvert's `../promo/build_promotion.apply` (no entrances, eight
'B' gate_frames), which checks each old frame and recomputes the local profile and widths. This builder then checks:
input sha pin; the scalar program of A, cut, B, precondition and cleanup unchanged (every field but the frame); start
and end frames unchanged; local profile and width inventory equal to the recipe's; output sha pin. Three pin controls
(input pin, wrong old frame, output pin) must be rejected at their pinned reasons on every build.
Adapted from PR741's extras/build_frames.py (chafreaky). Apache-2.0.
"""
import copy, gzip, hashlib, importlib.util, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_s = importlib.util.spec_from_file_location('promotion', HERE.parent / 'promo/build_promotion.py')
B = importlib.util.module_from_spec(_s); _s.loader.exec_module(B)


def construct(raw, recipe):
    assert hashlib.sha256(raw).hexdigest() == recipe['input_content_sha256'], 'input word pin'
    w = json.loads(raw)
    assert len(recipe['gate_frames']) == 8 and all(c[0] == 'B' for c in recipe['gate_frames']), 'eight B frames'
    out = B.apply(w, dict(entrances={}, gate_frames=recipe['gate_frames']))
    for section in ('A', 'cut', 'B', 'precondition', 'cleanup'):
        assert [e[:-1] for e in w[section]] == [e[:-1] for e in out[section]], 'scalar program unchanged'
    assert out['start_extra'] == w['start_extra'] and out['helper_final'] == w['helper_final'], 'endpoint frames unchanged'
    assert out['report']['local_profile'] == recipe['expected']['local_profile'] and \
        out['report']['width_inventory'] == recipe['expected']['width_inventory'], 'profile and width pins'
    data = json.dumps(out, sort_keys=True, separators=(',', ':')).encode()
    assert hashlib.sha256(data).hexdigest() == recipe['expected']['output_content_sha256'], 'output word pin'
    return data


def main():
    assert __debug__, 'Assertions are required'
    inp, outd, rfile = map(Path, sys.argv[1:4])
    raw = gzip.decompress(inp.read_bytes()); recipe = json.loads(rfile.read_text())
    data = construct(raw, recipe)
    rejected = []
    for name, change, reason in [
            ('input-pin', lambda r: r.__setitem__('input_content_sha256', '0' * 64), 'input word pin'),
            ('old-frame', lambda r: r['gate_frames'][0].__setitem__(2, []), 'gate frame mismatch'),
            ('output-pin', lambda r: r['expected'].__setitem__('output_content_sha256', '0' * 64), 'output word pin')]:
        r = copy.deepcopy(recipe); change(r)
        try:
            construct(raw, r)
        except AssertionError as e:
            assert reason in str(e), (name, str(e)); rejected.append(dict(name=name, reason=reason))
        else:
            raise AssertionError('accepted ' + name)
    outd.mkdir(parents=True)
    (outd / 'FULL-WORD.json.gz').write_bytes(gzip.compress(data, mtime=0))
    (outd / 'BUILD.json').write_text(json.dumps(dict(
        status='PASS_EIGHT_FRAME_EXACT_CONSTRUCTION', input_sha256=hashlib.sha256(raw).hexdigest(),
        output_sha256=hashlib.sha256(data).hexdigest(), scalar_program_unchanged=True, frames=8,
        rejected_controls=rejected), indent=2) + '\n')
    print('PASS eight B frames and three pin controls')


if __name__ == '__main__':
    main()
