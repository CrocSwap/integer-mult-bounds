"""Apply the fixed E8 frame witness; no search is needed.

Dylan Crow's E8 word; frame witness and replay prepared with OpenAI Codex.
Apache-2.0. Usage: python3 -B replay.py SOURCE.json.gz SELECTION.json OUT.json
"""
from pathlib import Path
from hashlib import sha256
import copy
import gzip
import json
import sys

assert __debug__, 'Assertions are required; do not use -O'


def reconstruct(source_bytes, selection):
    assert sha256(source_bytes).hexdigest() == selection['input_sha256']
    source = json.loads(gzip.decompress(source_bytes))
    word = copy.deepcopy(source)
    positions = []
    for phase in ('D', 'A', 'B', 'C'):
        word[phase] = [[f, d, [s]] for f, d, sources in word[phase] for s in sources]
        positions.extend((phase, i) for i in range(len(word[phase])))
    entries = selection['entries']
    assert len(entries) == selection['changed_gates'] == 128
    assert len({e['scalar_index'] for e in entries}) == len(entries)
    for entry in entries:
        phase, i = positions[entry['scalar_index']]
        assert phase == entry['phase'] and phase != 'D'
        assert word[phase][i] == [entry['old_frame'], entry['dst'], [entry['src']]]
        assert 0 <= entry['new_frame'] < len(word['frames'])
        assert entry['new_frame'] != entry['old_frame']
        word[phase][i][0] = entry['new_frame']
    # Frames and every non-gate field are inherited unchanged. Flattening changes
    # MOVE placement within source bundles, but preserves every primitive ADD.
    for key in source:
        if key not in ('D', 'A', 'B', 'C'):
            assert word[key] == source[key]
    for phase in ('D', 'A', 'B', 'C'):
        before = [(d, s) for _, d, sources in source[phase] for s in sources]
        after = [(d, s) for _, d, sources in word[phase] for s in sources]
        assert before == after
    data = json.dumps(word, sort_keys=True, separators=(',', ':')).encode()
    assert sha256(data).hexdigest() == selection['output_sha256']
    return data


def negative_controls(source_bytes, selection):
    controls = []
    changed = bytearray(source_bytes)
    changed[-1] ^= 1
    cases = [('changed source bytes', bytes(changed), selection)]
    bad = copy.deepcopy(selection)
    bad['entries'][0]['old_frame'] = -1
    cases.append(('wrong original frame', source_bytes, bad))
    bad = copy.deepcopy(selection)
    bad['entries'][1]['scalar_index'] = bad['entries'][0]['scalar_index']
    cases.append(('duplicate scalar entry', source_bytes, bad))
    for name, source, witness in cases:
        try:
            reconstruct(source, witness)
        except AssertionError:
            controls.append(name)
        else:
            raise AssertionError(('accepted invalid witness', name))
    return controls


if __name__ == '__main__':
    assert len(sys.argv) == 4, __doc__
    source, witness, target = map(Path, sys.argv[1:])
    selection = json.loads(witness.read_text())
    data = reconstruct(source.read_bytes(), selection)
    target.write_bytes(data)
    print('PASS_SOURCE_BOUND_E8_RETIMING', selection['changed_gates'], sha256(data).hexdigest())
