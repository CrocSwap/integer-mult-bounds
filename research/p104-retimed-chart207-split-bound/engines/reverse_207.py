"""Reverse exact old/new chart-207 occupancy for the #7334 retimed block."""
from argparse import ArgumentParser
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
ADMISSION = 'c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13'
PRICE = 'b3c36d5a1d199a1e74f979d660fac295c55659a9d4edb70eaef541095670323b'
PINS = {
    '7314-WORD.json.gz':'c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9',
    '7334-WORD.json.gz':'4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
    'IDENTITIES.json':'f4d3f6ca2d87f8cd68c01ac9f77b69bd5a796f92bd567cea8afe3ac7c72e8e4b',
}
CHART, AUX, OLD_HELPER = 207, 1567, 319
PROTECTED = {319,863,1355,1568}
CAP = 128


def decode(raw):
    def unique(items):
        obj = dict(items)
        assert len(obj) == len(items), 'duplicate JSON key'
        return obj
    return loads(raw,object_pairs_hook=unique)


def pinned(path, expected):
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == expected, ('changed input',path.name)
    return raw


def roles(event):
    return event[1:3] if event[0] in ('ADD','COPY') else event[1:2]


def event_charts(event):
    return event[2:4] if event[0] == 'MOVE' else [event[-1]]


def snapshots(word, marks, affected, eligible, frame, deadline):
    """Read exact cut states backward, including the post-final cut."""
    public = word['public']
    frames = word['frames']
    tape = word['program']
    state = dict(enumerate(word['final']))
    selected = {}
    target = min(marks)

    @cache
    def span(chart):
        vectors = {0}
        for v in frames[chart]:
            assert v not in vectors
            vectors.update(x ^ v for x in tuple(vectors))
        return frozenset(vectors)

    visited = 0
    for cut in range(len(tape), target-1, -1):
        if monotonic() >= deadline:
            break
        if cut in marks:
            public_bank = sorted(r for r,f in state.items() if f == frame and r < public)
            selected[cut] = dict(public_bank=public_bank,
                                 owned_bank=sorted(r for r,f in state.items() if f == frame and r >= public),
                                 pivots=sorted(eligible.intersection(public_bank)),
                                 affected_charts={r:state.get(r) for r in sorted(affected)})
        if cut == target:
            break
        op, dest, *args = tape[cut-1]
        visited += 1
        if op == 'MOVE':
            old,new,owned = args
            assert state[dest] == new and owned == (dest >= public)
            assert span(old) < span(new) or owned and span(new) < span(old)
            state[dest] = old
        elif op == 'INIT':
            assert dest >= public and state.pop(dest) == args[0]
        elif op == 'CLEAR':
            assert dest >= public and dest not in state
            state[dest] = args[0]
        else:
            assert op in ('ADD','COPY','SCALE') and Fraction(args[-2])
            assert state[dest] == args[-1]
            if op in ('ADD','COPY'):
                assert args[0] != dest and state[args[0]] == args[-1]
                assert op != 'COPY' or dest >= public
    return selected, sorted(marks - selected.keys()), visited


def controls():
    word = dict(public=2, frames=[[],[1],[1,2]], initial=[0,1], final=[2,1],
                program=[
                    ['MOVE',0,0,1,False],['INIT',2,1],['COPY',2,0,'-1',1],
                    ['ADD',1,2,'2',1],['CLEAR',2,1],['MOVE',0,1,2,False]])
    found,missing,_=snapshots(word,{0,1,2,4,5,6},{0,1,2},{0},1,float('inf'))
    assert not missing
    assert found[0]['public_bank'] == [1] and not found[0]['pivots']
    assert found[1]['pivots'] == [0] and not found[1]['owned_bank']
    assert found[2]['owned_bank'] == found[4]['owned_bank'] == [2]
    assert not found[5]['owned_bank'] and found[6]['public_bank'] == [1]
    return ['literal_pre_post_move_cut','guarded_owned_lifetime','protected_public_pivot_filter']


def audit(old, new, identity, deadline):
    assert identity['status'] == 'PASS_INDEPENDENT_319_BLOCK'
    lo,hi = identity['literal_candidate_clocks']
    assert (lo,hi) == (44588,44627)
    affected = set(identity['roles'])
    assert len(affected) == 14 and OLD_HELPER in affected
    assert old['initial'] == new['initial'] and old['final'] == new['final']
    assert old['frames'] == new['frames'] and old['public'] == new['public']
    frames = new['frames']
    def span(chart):
        vectors = {0}
        for v in frames[chart]:
            assert v not in vectors
            vectors.update(x ^ v for x in tuple(vectors))
        return vectors
    assert (len(frames[3]),len(frames[CHART]),len(frames[127])) == (0,8,9)
    assert span(3) < span(CHART) < span(127)

    forbidden = PROTECTED | set(new['live']) | {r+112 for r in new['live']}
    forbidden.update(new['hosted']['X2']+new['hosted']['Y2'])
    cohort = {r for r in affected if r < new['public'] and
              (new['initial'][r],new['final'][r]) == (3,127)}
    eligible = cohort - forbidden
    old_tape, new_tape = old['program'],new['program']
    old_body = identity['body_clocks']
    new_body = [t for t in range(lo,hi+1)
                if new_tape[t][0] in ('ADD','SCALE') and new_tape[t][-1] == CHART]
    assert len(old_body) == len(new_body) == 18
    assert set(r for t in old_body for r in roles(old_tape[t])) == affected
    for before, after in zip(old_body,new_body,strict=True):
        event = old_tape[before].copy()
        assert event[0] in ('ADD','SCALE') and event[-1] == CHART
        for k in (1,2) if event[0]=='ADD' else (1,):
            if event[k] == OLD_HELPER:
                event[k] = AUX
        assert new_tape[after] == event
    assert [new_tape[t] for t in range(lo,hi+1) if new_tape[t][0] in ('INIT','CLEAR')]==[
        ['INIT',AUX,CHART],['CLEAR',AUX,CHART]]

    old_move_clocks = [t for t in range(old_body[0],46309)
                       if old_tape[t][0]=='MOVE' and old_tape[t][1] in affected and
                       CHART in event_charts(old_tape[t])]
    assert {43029,46308} <= set(old_move_clocks)
    old_marks = {t+d for t in old_body+old_move_clocks+identity['window'] for d in (0,1)}
    new_marks = set(range(lo,hi+2))
    reps = {lo,hi+1}
    reps.update(t+1 for t in range(lo,hi+1) if CHART in event_charts(new_tape[t]))
    old_views,old_missing,old_events = snapshots(old,old_marks,affected,eligible,CHART,deadline)
    new_views,new_missing,new_events = snapshots(new,new_marks,affected|{AUX},eligible,CHART,deadline)

    alignment = []
    for old_clock,new_clock in zip(old_body,new_body,strict=True):
        for offset in (0,1):
            a,b = old_clock+offset,new_clock+offset
            if a not in old_views or b not in new_views:
                continue
            old_pivots,new_pivots = old_views[a]['pivots'],new_views[b]['pivots']
            alignment.append(dict(old_clock=old_clock,new_clock=new_clock,side='before' if offset==0 else 'after',
                                  old_pivots=old_pivots,new_pivots=new_pivots,
                                  gained_pivots=sorted(set(new_pivots)-set(old_pivots)),
                                  lost_pivots=sorted(set(old_pivots)-set(new_pivots))))
    raw_keys = [[cut,CHART,r] for cut in sorted(new_views) for r in new_views[cut]['pivots']]
    rep_keys = [[cut,CHART,r] for cut in sorted(reps & new_views.keys()) for r in new_views[cut]['pivots']]
    return dict(
        old_literal_events=len(old_tape),new_literal_events=len(new_tape),
        old_reverse_events=old_events,new_reverse_events=new_events,
        cohort=sorted(cohort),eligible_affected=sorted(eligible),protected_roles=sorted(PROTECTED),
        affected=sorted(affected),old_body=old_body,new_body=new_body,old_move_clocks=old_move_clocks,
        old_snapshots=old_views,new_snapshots=new_views,alignment=alignment,
        representative_cuts=sorted(reps),raw_key_count=len(raw_keys),representative_key_count=len(rep_keys),
        representative_keys=rep_keys[:CAP],unvisited_keys=rep_keys[CAP:],
        old_unvisited_cuts=old_missing,new_unvisited_cuts=new_missing,
        new_pivot_roles=sorted({r for _,_,r in raw_keys}),
        old_relevant_pivot_roles=sorted({r for v in old_views.values() for r in v['pivots']}),
        aligned_gains=[r for r in alignment if r['gained_pivots']],
        complete=not (old_missing or new_missing or len(rep_keys)>CAP))


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument('--inputs',type=Path)
    p.add_argument('--price',type=Path)
    p.add_argument('--price-sha')
    p.add_argument('--controls-only',action='store_true')
    args = p.parse_args()
    checks=controls()
    if args.controls_only:
        print(dumps(checks))
        return
    if not all((args.inputs,args.price,args.price_sha)):
        p.error('exact old/new inputs and saved price required')

    def stop(*_):
        raise TimeoutError('hard runner deadline')

    signal(SIGALRM,stop)
    alarm(20)
    deadline=monotonic()+17
    try:
        assert args.price_sha == PRICE
        quote = decode(pinned(args.price,PRICE))
        assert quote['head'] == HEAD and quote['inputs']['ADMITTED.json'] == ADMISSION
        assert quote['productive_delta'] == {'1':17,'8':17,'9':-17} and not quote['paid_delta']
        assert sum(quote['paid'].values()) == 110519 and sum(quote['new_targets'].values()) == 22478
        assert 0 < Fraction(quote['new_margin'][0]) and Fraction(quote['margin_with_one_added_raw_rank_one_upper']) < 0
        data={name:pinned(args.inputs/name,digest) for name,digest in PINS.items()}
        result=audit(decode(decompress(data['7314-WORD.json.gz'])),
                     decode(decompress(data['7334-WORD.json.gz'])),decode(data['IDENTITIES.json']),deadline)
    finally:
        alarm(0)
    print(dumps(dict(comparator_head=HEAD,price_sha256=PRICE,input_sha256=PINS,controls=checks,
                     cut_convention='cut k immediately before event k; include post-block cut',
                     geometry_only=True,runner_cap=20,case_cap=CAP,**result),sort_keys=True,indent=2))


if __name__ == '__main__':
    assert __debug__
    main()
