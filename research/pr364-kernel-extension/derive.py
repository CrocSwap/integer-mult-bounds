"""Deterministic two-family extension of the exact PR364 final word.
Uses the inherited shared-donor kernel emitter and its exact complete checker.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent / 'w3-design-t-staged-p10b-reorder-mc'
INPUT = '790ebf533a8f7884414ff1061a2650bdfb14f72f70c25148ecbc86443649e2c5'
KERNEL = '7a48f2657280393db64bbabde1ebd64f62a3ca1cdfa869be72a17a5d79522cf1'
OUTPUT = '7b4bb2f0944d422699501ccb9a9d1cdde5b8fbe8a7877b16ee844a73f7b92139'


def derive(source, destination):
    if not __debug__:
        raise SystemExit('Assertions must be enabled')
    sys.path.insert(0, str(PARENT/'code'))
    import stages
    import stagelib as L
    selection = json.loads((ROOT/'selection.json').read_text())
    snap = L.load_snapshot(source)
    assert L.rec_sha(snap) == INPUT
    assert {e['pivot'] for e in selection} == {7107, 7848}
    assert all(len(e['basis']) == 2 and len(e['donors']) == 3 for e in selection)
    upstream=json.loads((ROOT/'pr366-selection.json').read_text())
    assert upstream['input_records_sha256']==INPUT
    assert len(upstream['entries'])==123
    published=stages.retime(snap,upstream['entries'])
    assert L.rec_sha(published)==upstream['output_records_sha256']=='b99fa242f1ca49c6df3d9e7f0e60b241b04d37332177cecd03b648fc71fde6a1'
    L.save_snapshot(published,Path(destination).parent/'pr366')
    before = snap['s']
    out = stages.kernel(snap, selection)
    checked = L.full_check(out, L.labels_chi(str(PARENT/'data/labels.json')))
    assert L.rec_sha(out) == KERNEL
    assert out['fr'] == snap['fr'], 'This extension requires no new frame'
    assert out['s']['final'] == before['final']
    changed = sorted(int(k) for k,v in out['s']['initial'].items() if v != before['initial'][k])
    assert changed == [7107, 7848]
    assert before['record_count'] == 405697 and out['s']['record_count'] == 405695
    kernel_path=Path(destination).parent/'kernel'
    L.save_snapshot(out, kernel_path)
    assert (Path(source)/'frames.json').read_bytes() == (kernel_path/'frames.json').read_bytes()
    retiming=json.loads((ROOT/'retiming.json').read_text())
    assert retiming['stage']=='retime' and retiming['input_records_sha256']==KERNEL
    assert len(retiming['entries'])==128
    union={e['record']:e for e in retiming['entries']}
    assert len(union)==128
    from collections import defaultdict
    indices=defaultdict(list)
    for i,row in enumerate(out['rec'].tolist()):
        if row[0]==1: indices[tuple(row)].append(i)
    mapped=set();upstream_registers=set()
    for e in upstream['entries']:
        row=tuple(snap['rec'][e['record']].tolist())
        assert len(indices[row])==1
        i=indices[row][0];mapped.add(i)
        assert union[i]['new_basis']==e['new_basis'] and union[i]['scalar']==e['scalar']
        upstream_registers.update(row[1:3])
    extra=sorted(set(union)-mapped)
    assert len(extra)==5
    extra_registers={x for i in extra for x in out['rec'][i,1:3].tolist()}
    assert not(extra_registers & upstream_registers)
    assert sorted(out['rec'][i,1:4].tolist() for i in extra)==sorted([
        [8681,7323,1],[8789,7838,1],[8789,8681,1],[8681,7838,1],[8681,8788,1]])
    retimed=stages.retime(out,retiming['entries'])
    retimed_check=L.full_check(retimed,L.labels_chi(str(PARENT/'data/labels.json')))
    assert L.rec_sha(retimed)==retiming['output_records_sha256']==OUTPUT
    assert retimed['s']['initial']==out['s']['initial'] and retimed['s']['final']==out['s']['final']
    assert retimed['s']['record_count']==405678
    def scalar_projection(snapshot):
        return [(o,a,b,c,z) if o==1 else (o,a,b,c,f,z)
                for o,a,b,c,f,z in snapshot['rec'].tolist() if o!=0]
    assert scalar_projection(out)==scalar_projection(retimed)
    added_frames=set(retimed['fr']['frames'])-set(out['fr']['frames'])
    assert len(added_frames)==55
    L.save_snapshot(retimed,destination)
    return dict(status='PASS_TWO_KERNELS_AND_COMPONENT_RETIMING_SOURCE_BOUND_DERIVATION',
                input_records_sha256=INPUT,kernel_records_sha256=KERNEL,output_records_sha256=OUTPUT,
                kernel_new_frames=0,retiming_new_frames=55,retimed_gates=128,upstream_retimed_gates=123,new_retimed_gates=5,
                upstream_frames_preserved=True,new_gates_register_disjoint_from_upstream=True,
                retiming_scalar_projection_unchanged=True,changed_entrances=changed,
                entrance_rank_gain=4,kernel_checks=checked,retiming_checks=retimed_check)
