"""Compare complete raw chart-207 cut snapshots and both key cap conventions."""
from argparse import ArgumentParser
from hashlib import sha256
from gzip import decompress
from json import dumps, loads
from pathlib import Path

LEAD = '4c349e06b22bfebb431fab1c9ae04f0e798f398acc6fdd99591b49b1c95ef6ca'
REVERSE = '587739d21541e7ffe01af9cb7e51abaa757ee69b580befe8bb768a81b614aa08'
WORD = '4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a'
CHART = 207
FIELDS = ('public_bank', 'owned_bank', 'pivots')


def read(path, digest):
    data = path.read_bytes()
    assert sha256(data).hexdigest() == digest, path.name
    return data


def bank(row):
    return tuple(tuple(row[key]) for key in FIELDS)


def event_charts(event):
    return event[2:4] if event[0] == 'MOVE' else [event[-1]]


def compare(forward, reverse, word):
    f, b = loads(read(forward,LEAD)), loads(read(reverse,REVERSE))
    tape = loads(decompress(read(word,WORD)))['program']
    assert f['head'] == b['comparator_head'] and f['price_sha256'] == b['price_sha256']
    assert f['new_interval'] == [44588,44628] and f['new']['complete'] and f['old']['complete']
    assert not (b['new_unvisited_cuts'] or b['old_unvisited_cuts'])
    assert len(b['new_snapshots']) == len(f['new']['rows']) == 41
    old = {r['cut']:r for r in f['old']['rows']}
    common = sorted(cut for cut in map(int,b['old_snapshots']) if cut in old)
    assert all(bank(old[cut]) == bank(b['old_snapshots'][str(cut)]) for cut in common)
    assert len(common) == 47
    extra_old = sorted(set(map(int,b['old_snapshots']))-set(common))
    assert extra_old == [45719,45737,45738,45968,45969,46011,46012,46308,46309]

    lead_reps, raw_keys, coverage = [], [], []
    latest = None
    for cut, row in enumerate(f['new']['rows'],44588):
        assert row['cut'] == cut and bank(row) == bank(b['new_snapshots'][str(cut)])
        raw_keys.extend([cut,CHART,p] for p in row['pivots'])
        expected_rep = cut == 44588 or CHART in event_charts(tape[cut-1])
        assert row['representative'] == expected_rep
        if row['representative']:
            latest = cut
            lead_reps.extend([cut,CHART,p] for p in row['pivots'])
        else:
            assert bank(row) == bank(b['new_snapshots'][str(latest)])
            assert all(CHART not in event_charts(tape[t]) for t in range(latest,cut))
        coverage.append([cut,latest])
    assert len(raw_keys) == b['raw_key_count'] == 166
    assert len(lead_reps) == 146 and lead_reps[:128] == f['representative_keys']
    assert lead_reps[128:] == f['unvisited_keys'] and len(f['unvisited_keys']) == 18
    independent_reps = b['representative_keys'] + b['unvisited_keys']
    added = [[44628,CHART,p] for p in b['new_snapshots']['44628']['pivots']]
    assert independent_reps == lead_reps + added
    assert len(added) == 5 and len(independent_reps) == 151 and len(b['unvisited_keys']) == 23
    assert b['representative_keys'] == f['representative_keys']
    assert b['unvisited_keys'] == f['unvisited_keys'] + added
    assert coverage[-3:] == [[44626,44626],[44627,44626],[44628,44626]]
    omitted = [[44626,tape[44626]],[44627,tape[44627]]]
    assert omitted == [[44626,['ADD',1467,319,'1',127]],[44627,['ADD',319,1467,'-1',127]]]
    active = set(b['new_snapshots']['44626']['public_bank']+b['new_snapshots']['44626']['owned_bank'])
    assert all(not active.intersection(e[1:3]) for _,e in omitted)
    return dict(head=f['head'],price_sha256=f['price_sha256'],forward_sha256=LEAD,reverse_sha256=REVERSE,
                matched_raw_new_cuts=41,matched_old_overlap_cuts=len(common),
                reverse_only_old_lift_cuts=extra_old,
                raw_pivot_pairs=166,lead_representative_pairs=146,reverse_representative_pairs=151,
                identical_first_keys=128,lead_unvisited=18,reverse_unvisited=23,
                equivalent_extra_pairs=added,equivalent_extra_cut=44626,
                disjoint_chart_127_events=omitted,cut_coverage=coverage,
                no_distinct_chart_207_event_omitted=True)


if __name__ == '__main__':
    assert __debug__
    p=ArgumentParser(description=__doc__)
    p.add_argument('forward',type=Path)
    p.add_argument('reverse',type=Path)
    p.add_argument('word',type=Path)
    a=p.parse_args()
    print(dumps(compare(a.forward,a.reverse,a.word),sort_keys=True,indent=2))
