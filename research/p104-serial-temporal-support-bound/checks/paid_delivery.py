"""Necessary source span for one already-paid delivery to exact #7161 read 40529."""
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
from time import monotonic

HEAD = '16ea35caeeca1a166113ad21c76127f04889f6f5'
PINS = {
    'checks/charged_charts.py': '6745163b953006ae1ee2627a8a375cb0711748a6c2b89eead7abb71f887ed280',
    'checks/owned.py': '53da0a7b551b34f3baf633083a4362570ebe694a694e2d0b6226d01c08a6ab3b',
    'checks/side_rows.py': '4ee7c51298e53d54e33b9ab4abc68d489078f0cf5032f52248f773df3f4294e9',
    'checks/donor_intervals.py': '307af640b97bcc31a13a4b139b418038bbce137686fd6ffed93e8865e44c65ce',
}
ROLE, OLD_MOVE, READ, TARGET_CHART = 738, 40528, 40529, 619


def load(root, name):
    path = root/name
    assert sha256(path.read_bytes()).hexdigest() == PINS[name], name
    spec = importlib.util.spec_from_file_location('delivery_' + path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(package, cap, seconds):
    started = monotonic()

    def deadline():
        if monotonic() - started >= seconds:
            raise TimeoutError('paid delivery prepass')

    chart, owned, rank, donor = [load(package, name) for name in PINS]
    chart.controls(rank)
    donor.controls()
    root = package/'inputs'
    word, result, caller, gate = chart.read_sources(
        root/'peer', root/'caller/CALLER.json', root/'caller/interval_gate.py', owned, 1)
    assert word['program'][OLD_MOVE] == ['MOVE', ROLE, 252, TARGET_CHART, False]
    assert word['program'][READ] == ['ADD', 112, ROLE, '-1/2', TARGET_CHART]
    try:
        spaces, moves, _, _ = owned.scan_word(word, deadline, 80000)
        signed, invoice = owned.full_invoice(word, caller, result, moves)
        candidates = [m for m in moves if m['event'] < READ
                      and spaces[m['target']] == spaces[TARGET_CHART]]
        assert OLD_MOVE in [m['event'] for m in candidates]
        assert any(m['role'] == 1354 and m['event'] == 38236 for m in candidates)
        queries = {m['event']: spaces[m['source']] for m in candidates}
        queries[READ] = spaces[TARGET_CHART]
        live, snapshots = {}, {}

        def visit(cut, role, label, row):
            if label is None or not row:
                live.pop(role, None)
            else:
                live[role] = (label, row.copy())
            if cut in queries and cut != 0:
                snapshots[cut] = {r: item for r,item in live.items() if spaces[item[0]] == queries[cut]}

        donor.replay(word, READ+1, visit, deadline)
        assert snapshots.keys() == queries.keys()
    except TimeoutError:
        return dict(status='PREPASS_PENDING', first_pending='exact tape scan', head=owned.HEAD,
                    cap=cap, seconds=seconds, pins=owned.PINS | PINS)
    target = snapshots[READ][ROLE][1]
    assert target
    cases, pending = [], None
    for move in candidates:
        event = move['event']
        if len(cases) >= cap or monotonic()-started >= seconds:
            pending = dict(event=event, role=move['role'])
            break
        rows = [r for _,r in snapshots[event].values()]
        basis = {}
        for row in rows:
            rank.insert(basis,rank.integral(row))
        before = len(basis)
        needed = rank.insert(basis,rank.integral(target))
        missing = sorted(target.keys() - set().union(*(r.keys() for r in rows)))
        assert not missing or needed
        cases.append(dict(event=event, owner=move['role'], source=move['source'], target=move['target'],
                          pre_existing_paid_rank=move['rank'], rank_before=before, rank_after=len(basis),
                          missing_coordinates=missing, source_pool_size=len(rows), support=not needed,
                          predecessor_control=event == OLD_MOVE))
    old = next((c for c in cases if c['predecessor_control']), None)
    if old is not None:
        assert old['support'], old
    possible = [c['event'] for c in cases if c['support'] and not c['predecessor_control']]
    return dict(status='CAP_PENDING' if pending else 'EXHAUSTED', first_pending=pending,
                head=owned.HEAD, dependency_head=HEAD, pins=owned.PINS | PINS,
                cap=cap, seconds=seconds, seed=None, literal_read=READ, original_owner=ROLE,
                target=str(owned.TARGET), exact_target_row={i:str(v) for i,v in target.items()},
                baseline_moment=gate.show(gate.moment(signed,owned.TARGET)), invoice=invoice,
                cases=cases, alternatives_supported=possible, total_cases=len(candidates),
                cases_unresolved=len(candidates)-len(cases),
                favorable_model='One pre-existing paid MOVE ending in the exact read span. All baseline coframed source rows, arbitrary scalar mixing, caching, routing and restore free.')


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('package',type=Path)
    p.add_argument('--cap',type=int,default=1024)
    p.add_argument('--seconds',type=int,default=720)
    args=p.parse_args()
    assert __debug__ and 0 < args.cap <= 1024 and 0 < args.seconds <= 720
    print(json.dumps(run(**vars(args)),indent=2,sort_keys=True))
