"""Ten coupled frame changes on the pinned PR369 word, in three frozen stages.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent/'pr364-kernel-extension'
BASE = ROOT.parent/'w3-design-t-staged-p10b-reorder-mc'
INPUT = '7b4bb2f0944d422699501ccb9a9d1cdde5b8fbe8a7877b16ee844a73f7b92139'
CHAIN = [INPUT,
         'e1cb90cd9e8ea698223b47b79894eeb0c630cb880706049dd463c1cd030aba52',
         'ea64cf5dbab663058131182772025a2fd5514211fed89973420d4818d84c42c2',
         'b0fd6cfb9a976e07c3860a5fddd34962504db31163d5346f96fc5e7c6624fdb0']


def scalar_projection(word):
    return [(o, a, b, c, z) if o == 1 else (o, a, b, c, f, z)
            for o, a, b, c, f, z in word['rec'].tolist() if o != 0]


def derive(source, destination):
    if not __debug__:
        raise SystemExit('Assertions must be enabled')
    sys.path.insert(0, str(BASE/'code'))
    import stages
    import stagelib as L
    expected = json.loads((PARENT/'EXPECTED.json').read_text())
    for name, digest in expected['source_hashes'].items():
        assert hashlib.sha256((Path(source)/name).read_bytes()).hexdigest() == digest
    snap = L.load_snapshot(source)
    selections = json.loads((ROOT/'selection.json').read_text())
    assert len(selections) == 3
    records = [[340471, 342906], [340242, 342529],
               [325115, 325117, 325118, 325444, 339087, 340653]]
    scalars = [[[8353, 7736, 1, 12], [7736, 6997, 1, 12]],
               [[8337, 7716, 1, 12], [7716, 6994, 1, 12]],
               [[8744, 7780, 1, 12], [8744, 8548, 1, 12], [8548, 7780, 1, 12],
                [8548, 7231, 1, 12], [6846, 6587, 1, 12], [6587, 6386, 1, 12]]]
    old_dimensions = [[13, 15], [13, 15], [13, 13, 13, 15, 13, 15]]
    new_dimensions = [[12, 14], [12, 14], [12, 12, 12, 14, 12, 14]]
    # Each later gate alone must exhibit its exact failed MOVE inclusion.
    controls = [[(1, [[342904, 7736, 48684, 65005, 1]])],
                [(1, [[342527, 7716, 48753, 64834, 1]])],
                [(3, [[325442, 8548, 31338, 69148, 1]]),
                 (5, [[340651, 6587, 49098, 63971, 1]])]]
    new_frames = [{'69146'}, {'69147'}, {'69148', '69149', '69150'}]
    components = [scalars[0], scalars[1], scalars[2][:4], scalars[2][4:]]
    registers = [{r for scalar in group for r in scalar[:2]} for group in components]
    assert all(a.isdisjoint(b) for i,a in enumerate(registers) for b in registers[i+1:])
    receipts = []
    original_scalars = scalar_projection(snap)
    for index, selection in enumerate(selections):
        assert L.rec_sha(snap) == selection['input_records_sha256'] == CHAIN[index]
        entries = selection['entries']
        assert [e['record'] for e in entries] == records[index]
        assert [e['scalar'] for e in entries] == scalars[index]
        assert [e['old_dimension'] for e in entries] == old_dimensions[index]
        assert [e['new_dimension'] for e in entries] == new_dimensions[index]
        for entry in entries:
            row = snap['rec'][entry['record']].tolist()
            assert row[0] == 1
            assert [row[1], row[2], row[3], row[5]] == entry['scalar']
            assert len(snap['fr']['frames'][str(row[4])]['B']) == entry['old_dimension']
            assert len(entry['new_basis']) == entry['new_dimension']
        negative = []
        for entry_index, failed in controls[index]:
            alone = stages.retime(snap, [entries[entry_index]])
            frames = L.Frames(alone['fr'])
            violations = [[k, a, b, c, f] for k, (o, a, b, c, f, z) in enumerate(alone['rec'].tolist())
                          if o == 0 and not frames.sub(b, c)]
            assert violations == failed
            negative.append(dict(later_record=entries[entry_index]['record'],
                                 later_gate_alone_rejected=True, illegal_moves=violations))
        result = stages.retime(snap, entries)
        structural = L.full_check(result, L.labels_chi(str(BASE/'data/labels.json')))
        assert L.rec_sha(result) == selection['output_records_sha256'] == CHAIN[index+1]
        assert result['s']['initial'] == snap['s']['initial']
        assert result['s']['final'] == snap['s']['final']
        assert result['s']['record_count'] == 405677-index
        assert scalar_projection(result) == original_scalars
        assert set(result['fr']['frames']) - set(snap['fr']['frames']) == new_frames[index]
        receipts.append(dict(input_records_sha256=CHAIN[index], output_records_sha256=CHAIN[index+1],
                             structural=structural, negative_controls=negative))
        if index < 2:
            L.save_snapshot(result, Path(destination).parent/f'stage-{index+1}')
        snap = result
    L.save_snapshot(snap, destination)
    return dict(status='PASS_SOURCE_BOUND_TEN_GATE_PROPAGATION',
                input_records_sha256=INPUT, output_records_sha256=CHAIN[-1],
                changed_gates=10, new_frames=5, scalar_sequence_unchanged=True,
                endpoints_unchanged=True, component_registers_disjoint=True, stages=receipts)
