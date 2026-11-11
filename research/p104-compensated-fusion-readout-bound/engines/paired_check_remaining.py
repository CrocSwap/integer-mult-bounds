"""Independent direct forward and adjoint test for a virtual-zero helper split."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from tarfile import open as tar_open
from time import monotonic

HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
WORD = '4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a'
PARENT_WORD = 'c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9'
ARCHIVE = '0589953b3886d96eacf3bda3d38d8d574bb739fba1056af7f32f56047b6061e2'
MEMBER = 'research/p104-funded-863-return/WORD.json.gz'
BLOCK = (40222, 40840, 42609, 43022, 43023, 43024, 43025, 43026, 43028,
         43030, 43403, 43491, 43535, 43696, 43698, 43887, 45365, 45396)
PROTECTED = {319, 863, 1355, 1568}
ADMISSION = 'c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13'
PRICE = '4a7841699dd17688f6aada5c902a2a91e94558b2b1b4460c46b0e55aa95b3f9f'


def pinned(path, expected):
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == expected, ('changed input', path.name)
    return raw


def decode(raw):
    def unique(pairs):
        result = dict(pairs)
        assert len(result) == len(pairs), 'duplicate JSON key'
        return result

    return loads(raw, object_pairs_hook=unique)


@cache
def coefficient(text):
    value = Q(text)
    assert value
    return value


def add(values, role, value):
    total = values.get(role, 0) + value
    if total:
        values[role] = total
    else:
        values.pop(role, None)


def impulse(events, role, *, adjoint=False):
    """Apply M e_role, or e_role^T M with reversed literal scalar updates."""
    values = {role: Q(1)}
    for op, dest, *args in reversed(events) if adjoint else events:
        coeff = coefficient(args[-2])
        if op == 'SCALE':
            if dest in values:
                values[dest] *= coeff
        else:
            assert op == 'ADD' and dest != args[0]
            source = args[0]
            if adjoint:
                source, dest = dest, source
            value = values.get(source)
            if value:
                add(values, dest, coeff * value)
    return values


def cancellation(left, right, roles):
    """Return the scalar making left + scalar * right zero on all roles."""
    pivot = next((r for r in sorted(roles) if right.get(r)), None)
    value = -left.get(pivot, 0) / right[pivot] if pivot is not None else Q(0)
    residue = {r: left.get(r, 0) + value * right.get(r, 0) for r in sorted(roles)}
    return value, {r:c for r,c in residue.items() if c}


def legal(value):
    denominator = value.denominator
    for prime in (2,3,5):
        while denominator % prime == 0:
            denominator //= prime
    return denominator == 1 and abs(value.numerator) <= 64 and value.denominator <= 36000


def pair(forward, reverse, h, p, q, high):
    left, right = forward(h), forward(p)
    exterior = (left.keys() | right.keys()) - high
    lam, residue = cancellation(left, right, exterior)
    if residue:
        return {'status':'forward_identity_failed', 'lambda_trial':str(lam), 'residual':residue}
    direction = left.copy()
    for role, value in right.items():
        add(direction, role, lam * value)
    assert direction and direction.keys() <= high and h not in direction
    difference = reverse(h).copy()
    add(difference, h, Q(-1))
    readout = reverse(q) if q is not None else {}
    mu, residue = cancellation(difference, readout, difference.keys() | readout.keys())
    if residue:
        return {'status':'adjoint_identity_failed', 'lambda':str(lam), 'mu_trial':str(mu), 'residual':residue}
    assert q is not None or mu == 0
    emitted = [-lam, *direction.values(), -mu]
    preferred = all(v.denominator == 1 and abs(v) <= 16 for v in emitted)
    extra = sum(map(bool,emitted))
    fits = extra <= 6 and all(map(legal,emitted))
    free_lambda = not any(right.get(r) for r in exterior)
    status = ('exact_identity_supported' if fits else
              'coefficient_obligation_unresolved' if free_lambda else 'coefficient_or_count_failed')
    return dict(status=status,
                lambda_=str(lam), mu=str(mu), direction=direction,
                output_row={h:Q(1)}, preferred_small_integer=preferred,
                coefficient_screen_passed=fits, extra_adds=extra, free_lambda=free_lambda)


def check_pair(events, h, p, q, high):
    return pair(lambda role: impulse(events,role), lambda role: impulse(events,role,adjoint=True),
                h,p,q,high)


def controls(archive=None):
    # M maps e_h to e_p, and a signed peer recovers h's output row.
    body = [['ADD',1,0,'1',2], ['ADD',0,1,'-1',2]]
    result = check_pair(body,0,1,1,{1})
    assert result['status'] == 'exact_identity_supported'
    assert result['lambda_'] == '0' and result['mu'] == '1'
    assert result['direction'] == {1:Q(1)}
    assert check_pair(body,0,1,None,{1})['status'] == 'adjoint_identity_failed'
    assert check_pair(body,0,1,1,set())['status'] == 'forward_identity_failed'
    assert check_pair([['ADD',1,0,'1',2]],0,1,None,{1})['status'] == 'forward_identity_failed'
    if archive is None:
        return {'toy':['signed_pair', 'omitted_readout_rejected', 'exterior_output_rejected']}
    pinned(archive,ARCHIVE)
    with tar_open(archive,'r:gz') as stream:
        raw = stream.extractfile(MEMBER).read()
    assert sha256(raw).hexdigest() == PARENT_WORD
    word = decode(decompress(raw))
    events = [word['program'][t] for t in BLOCK]
    assert all(e[0] in ('ADD','SCALE') and e[-1] == 207 for e in events)
    good = check_pair(events,319,1081,1467,{1081,1467})
    assert good['status'] == 'exact_identity_supported'
    assert (good['lambda_'],good['mu'],good['direction']) == ('-1','1',{1081:Q(-1),1467:Q(1)})
    assert check_pair(events,319,1081,None,{1081,1467})['status'] == 'adjoint_identity_failed'
    assert check_pair(events,319,1081,1467,{1081})['status'] == 'forward_identity_failed'
    return {'toy':['signed_pair', 'omitted_readout_rejected', 'exterior_output_rejected'],
            'archived_319':good, 'archived_319_clocks':BLOCK, 'archive_sha256':ARCHIVE,
            'parent_word_sha256':PARENT_WORD}


def groups(geometry, word):
    public = word['public']
    tape = word['program']
    for index, key in enumerate(geometry['survivors']):
        h = key['h']
        a, b, c = key['chart_path']
        first, second = key['move_clocks']
        clocks = key['block']
        assert h < public and h not in PROTECTED
        assert tape[first] == ['MOVE',h,a,b,False] and tape[second] == ['MOVE',h,b,c,False]
        assert clocks == sorted(set(clocks)) and clocks
        events = [tape[t] for t in clocks]
        assert all(e[0] in ('ADD','SCALE') and e[-1] == b for e in events)
        actual = {r for e in events for r in (e[1:3] if e[0] == 'ADD' else e[1:2])}
        assert h in actual and actual <= set(key['roles'])
        lo,hi = key['clock_range']
        assert lo <= key['clock'] <= hi and key['aux'] >= public
        low = sorted(set(key['low']) - {h})
        high = set(key['high']) - {h}
        assert all(0 <= r < public for r in set(low) | high)
        yield index,key,events,low,high


def scan(word, geometry, deadline, cap):
    decisions, remaining = [], []
    for index,key,events,low,high in groups(geometry,word):
        h = key['h']
        readouts = [None, *sorted(high)]
        count = len(low) * len(readouts)

        @cache
        def forward(role):
            return impulse(events,role)

        @cache
        def reverse(role):
            return impulse(events,role,adjoint=True)

        visited = 0
        for p in low:
            for q in readouts:
                if len(decisions) >= cap or monotonic() >= deadline:
                    break
                result = pair(forward,reverse,h,p,q,high)
                decisions.append(dict(key=[h,*key['move_clocks'],key['clock'],p,q], geometry_index=index,**result))
                visited += 1
            if len(decisions) >= cap or monotonic() >= deadline:
                break
        if visited < count:
            remaining.append(dict(geometry_index=index,h=h,clock=key['clock'],low=low,
                                  readouts=readouts,first_unvisited_offset=visited,
                                  unvisited_count=count-visited))
    return dict(decisions=decisions,cases_visited=len(decisions),unvisited=remaining,
                unvisited_cases=sum(row['unvisited_count'] for row in remaining),
                support_only=[row for row in decisions if row['status']=='exact_identity_supported'],
                unresolved_coefficients=[row for row in decisions if row['status']=='coefficient_obligation_unresolved'])


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--controls-only',action='store_true')
    parser.add_argument('--control-archive',type=Path)
    parser.add_argument('--word',type=Path)
    parser.add_argument('--geometry',type=Path)
    parser.add_argument('--geometry-sha')
    parser.add_argument('--admission',type=Path)
    parser.add_argument('--admission-sha')
    parser.add_argument('--cap',type=int,default=1193,choices=range(1,1194),metavar='1..1193')
    args = parser.parse_args()
    if args.controls_only:
        print(dumps(controls(args.control_archive),sort_keys=True,indent=2,default=str))
        return
    if not all((args.word,args.geometry,args.geometry_sha,args.admission,args.admission_sha)):
        parser.error('admitted exact #7334 word and authenticated geometry are required')

    def stop(*_):
        raise TimeoutError('hard runner deadline')

    signal(SIGALRM,stop)
    alarm(35)
    deadline = monotonic()+32
    try:
        assert args.admission_sha == ADMISSION
        admission = decode(pinned(args.admission,args.admission_sha))
        assert admission['head'] == HEAD and admission['exit'] == 0
        assert admission['inputs']['WORD.json.gz'] == WORD
        assert set(admission['stages']) == {'early','native','caller','frontier'}
        assert all(marker.startswith('PASS_') for marker in admission['stages'].values())
        geometry = decode(pinned(args.geometry,args.geometry_sha))
        assert geometry['comparator_head'] == HEAD and geometry['word_sha256'] == WORD
        assert geometry['admission_sha256'] == ADMISSION and geometry['price_sha256'] == PRICE
        word = decode(decompress(pinned(args.word,WORD)))
        result = scan(word,geometry,deadline,args.cap)
    finally:
        alarm(0)
    print(dumps(dict(head=HEAD,word_sha256=WORD,geometry_sha256=args.geometry_sha,
                     admission_sha256=args.admission_sha,price_sha256=PRICE,case_cap=args.cap,seconds_cap=35,
                     controls=controls(),**result),sort_keys=True,indent=2,default=str))


if __name__ == '__main__':
    assert __debug__
    main()
