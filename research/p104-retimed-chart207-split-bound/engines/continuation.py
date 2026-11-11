"""Resume only the 18 untouched chart-207 split keys from Round 72."""
from argparse import ArgumentParser
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

HERE=Path(__file__).resolve().parent
PINS={
    'inputs/paired_support.py':'38c796cbe1a73f386177faf88cd53294d4b911f6cde7fd47cd9fcef3b558373f',
    'inputs/R72-SUPPORT.json':'d90ce338aab69c0c074f72e2e91e2eaa04fd347ea6cded83237d0996af327f98',
    'inputs/R72-OCCUPANCY.json':'4c349e06b22bfebb431fab1c9ae04f0e798f398acc6fdd99591b49b1c95ef6ca',
    'inputs/7334-WORD.json.gz':'4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
    'inputs/PRICE.json':'b3c36d5a1d199a1e74f979d660fac295c55659a9d4edb70eaef541095670323b',
    'inputs/ADMITTED.json':'c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13',
}
CAP=18


def need(condition,message):
    if not condition:
        raise ValueError(message)


def unique(items):
    row=dict(items)
    need(len(row)==len(items),'Duplicate input key')
    return row


def pinned(path,digest):
    raw=(HERE/path).read_bytes()
    need(sha256(raw).hexdigest()==digest,f'Changed dependency {path}')
    return raw


def parsed(name):
    return loads(pinned(name,PINS[name]),object_pairs_hook=unique)


def encoded(value):
    return (dumps(value,indent=2,sort_keys=True)+'\n').encode()


def select():
    geom=parsed('inputs/R72-OCCUPANCY.json')
    prior=parsed('inputs/R72-SUPPORT.json')
    price=parsed('inputs/PRICE.json')
    admission=parsed('inputs/ADMITTED.json')
    need(geom['head']==prior['head']==price['head']==admission['head'],'Source head mismatch')
    need(prior['geometry_sha256']==PINS['inputs/R72-OCCUPANCY.json'] and
         geom['price_sha256']==prior['price_sha256']==PINS['inputs/PRICE.json'],'Geometry or price mismatch')
    need(prior['word_sha256']==admission['inputs']['WORD.json.gz']==PINS['inputs/7334-WORD.json.gz'] and
         prior['admission_sha256']==PINS['inputs/ADMITTED.json'] and admission['exit']==0,'Admission mismatch')
    need(price['productive_delta']=={'1':17,'8':17,'9':-17} and not price['paid_delta'],'Wrong frozen price')
    earlier=[tuple(row['key']) for row in prior['decisions']]
    keys=[tuple(row) for row in geom['unvisited_keys']]
    need(earlier==[tuple(row) for row in geom['representative_keys']] and len(set(earlier))==128 and
         not prior['support_only'],'Prior scope did not exhaust the 128 authorized keys')
    need(keys==[tuple(row) for row in prior['unresolved']] and len(set(keys))==CAP and
         set(keys).isdisjoint(earlier),'Continuation is not the exact untouched suffix')
    by_cut={}
    for row in prior['decisions']:
        cut=row['key'][0]
        record={k:v for k,v in row.items() if k!='key'}
        need(cut not in by_cut or by_cut[cut]==record,'Different results at the same literal bank')
        by_cut[cut]=record
    reused=[]
    fresh=[]
    for key in keys:
        cut,chart,pivot=key
        need(chart==207 and pivot in geom['endpoint_cohort'],'Wrong target bank or pivot cohort')
        if cut in by_cut:
            row=by_cut[cut]
            need(pivot in row['public_bank'],'New pivot is absent at previously checked cut')
            reused.append(dict(key=key,**row))
        else:
            fresh.append(key)
    derived=geom|dict(representative_keys=keys,unvisited_keys=[],
                      r72_occupancy_sha256=PINS['inputs/R72-OCCUPANCY.json'],
                      r72_support_sha256=PINS['inputs/R72-SUPPORT.json'],
                      same_bank_keys=[row['key'] for row in reused],fresh_keys=fresh)
    return derived,reused,fresh,price


def main():
    p=ArgumentParser(description=__doc__)
    commands=p.add_mutually_exclusive_group(required=True)
    commands.add_argument('--derive-only',action='store_true')
    commands.add_argument('--support',action='store_true')
    p.add_argument('--selection-sha')
    a=p.parse_args()
    assert __debug__
    derived,reused,fresh,price=select()
    selection=encoded(derived)
    if a.derive_only:
        print(selection.decode(),end='');return
    need(a.selection_sha and sha256(selection).hexdigest()==a.selection_sha,'Frozen selection pin required')
    pinned('inputs/paired_support.py',PINS['inputs/paired_support.py'])
    engine=run_path(str(HERE/'inputs/paired_support.py'))
    controls=engine['controls']()
    def watchdog(*_):
        raise TimeoutError('R73 hard 35-second watchdog')
    signal(SIGALRM,watchdog)
    alarm(35)
    try:
        deadline=monotonic()+32
        raw=pinned('inputs/7334-WORD.json.gz',PINS['inputs/7334-WORD.json.gz'])
        word=loads(decompress(raw),object_pairs_hook=unique)
        exact=engine['audit'](word,derived|dict(representative_keys=fresh),deadline)
    finally:
        alarm(0)
    all_rows={tuple(row['key']):row for row in reused+exact['decisions']}
    all_keys=derived['representative_keys']
    result=dict(head=derived['head'],selected=CAP,case_cap=CAP,seconds_cap=35,
                status='EXHAUSTED' if not exact['unresolved'] else 'CAPPED',
                same_bank_reused=len(reused),fresh_replayed=len(exact['decisions']),
                decisions=[all_rows[key] for key in all_keys if key in all_rows],
                unresolved=exact['unresolved'],support_only=exact['support_only'],
                prefix_events=exact['prefix_events'],suffix_events=exact['suffix_events'],
                selection_sha256=a.selection_sha,input_sha256=PINS,controls=controls,
                unvisited_credit_upper=price['one_edit_optimistic_credit'][1])
    print(encoded(result).decode(),end='')


if __name__=='__main__':
    main()
