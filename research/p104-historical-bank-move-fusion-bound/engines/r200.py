"""Bounded exact reverse-row test for the frozen chart-127 historical coframe."""
from collections import defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM,alarm,signal
from time import monotonic

ROOT=Path(__file__).resolve().parent
HEAD='aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER='07a76c5e2738882c0cb322278e56f6cae3c9885d'
PINS={
 'inputs/7334-WORD.json.gz':'4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
 'inputs/BANK.json':'4843481ba524572696ac5977182dfe55768c2746c8d5dbf59ee7ba7ee6feeffb',
 'inputs/reverse_span.py':'f8b48f2ed99d003e20f5b3fb2270603c4edbc3ce9a01484102816aa2710ce9ff',
}
PAYLOAD='9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
OWNER,PEER,LEFT,ADD,RIGHT,BANK=1034,1561,48765,48766,48767,48768
EVENTS,DONORS,COLS,SECONDS=76466,760,1501,20


def unique(pairs):
    result=dict(pairs)
    assert len(result)==len(pairs),'duplicate JSON key'
    return result


def read(name):
    raw=(ROOT/name).read_bytes()
    assert sha256(raw).hexdigest()==PINS[name],name
    return raw


def timeout(*_):
    raise TimeoutError('20-second historical-bank gate')


def pin_bank(word, expected):
    tape=word['program']
    charts=word['initial']+[None]*word['owned_fields']
    starts={}
    completed={}
    observed_bank,observed_start,peer_start=None,None,None
    for t,event in enumerate(tape):
        if t==ADD:
            assert charts[PEER]==charts[OWNER]==306
            peer_start=starts[PEER]
        if t==BANK:
            assert charts[OWNER]==127
            observed_bank=[i for i,c in enumerate(charts) if c==127 and i!=OWNER]
            observed_start={r:starts[r] for r in observed_bank if r>=word['public']}
        op,d,*args=event
        if op=='MOVE':
            a,b,owned=args
            assert charts[d]==a and owned==(d>=word['public'])
            charts[d]=b
        elif op=='INIT':
            f,=args
            assert charts[d] is None and d>=word['public']
            charts[d]=f
            starts[d]=t
        elif op=='CLEAR':
            f,=args
            assert charts[d]==f and d>=word['public']
            charts[d]=None
            completed[d,starts.pop(d)]=t
        elif op=='SCALE':
            value,f=args
            assert charts[d]==f and Q(value)
        else:
            assert op in ('ADD','COPY')
            s,value,f=args
            assert d!=s and charts[d]==charts[s]==f and Q(value)
    assert charts==word['final']+[None]*word['owned_fields'] and not starts
    assert observed_bank==expected and len(observed_bank)==DONORS
    owned_lifetimes={r:[t,completed[r,t]] for r,t in observed_start.items()}
    return observed_bank,owned_lifetimes,[peer_start,completed[PEER,peer_start]]


def dot(row, v):
    values,d=row
    return sum((Q(values.get(j,0),d)*x for j,x in v.items()),Q(0))


def check_decision(bank,target,decision):
    if decision['status']=='exact_rank_exclusion':
        dual={int(j):Q(x) for j,x in decision['separating_covector'].items()}
        assert all(not dot(row,dual) for _,row in bank)
        assert dot(target,dual)==Q(decision['separated_target'])!=0
    elif decision['status']=='absent_exterior_coordinate':
        j=decision['coordinate']
        assert all(j not in row[0] for _,row in bank)
        assert dot(target,{j:Q(1)})==Q(decision['target_coefficient'])!=0
    else:
        assert decision['status']=='exact_span'
        rows=dict(bank)
        total=defaultdict(Q)
        for r,value in decision['coefficients'].items():
            values,d=rows[int(r)]
            for j,v in values.items():
                total[j]+=Q(v,d)*Q(value)
        values,d=target
        assert {j:v for j,v in total.items() if v}=={j:Q(v,d) for j,v in values.items()}


def main():
    assert __debug__
    signal(SIGALRM,timeout)
    alarm(SECONDS)
    until=monotonic()+SECONDS-1
    report={'head':HEAD,'caller':CALLER,'pins':PINS,'payload':PAYLOAD,'key':[LEFT,ADD,RIGHT,OWNER,PEER],
            'clock_convention':'pre-event', 'bank_cut':BANK, 'bank_chart':127,
            'case_cap':1,'bank_cap':DONORS,'source_coordinates':COLS,'runner_cap_seconds':SECONDS,
            'state':'unresolved','capped':False}
    try:
        spec=loads(read('inputs/BANK.json'),object_pairs_hook=unique)
        raw=decompress(read('inputs/7334-WORD.json.gz'))
        assert sha256(raw).hexdigest()==PAYLOAD
        word=loads(raw,object_pairs_hook=unique)
        assert (word['public'],word['owned_fields'],len(word['program']))==(COLS,68,EVENTS)
        assert (spec['head'],spec['caller'])==(HEAD,CALLER)
        assert not spec['before_first_move_bank']
        assert word['program'][LEFT:BANK]==[['MOVE',OWNER,9,306,False],['ADD',OWNER,PEER,'1',306],['MOVE',OWNER,306,127,False]]
        bank,owned,peer_life=pin_bank(word,spec['after_second_move_bank'])
        report.update(bank_roles=bank,bank_owned_lifetimes=owned,peer_lifetime=peer_life,
                      optimistic_paid_gain=spec['price_interval_17_calls'])
        read('inputs/reverse_span.py')
        engine=run_path(str(ROOT/'inputs/reverse_span.py'))
        requests={ADD:[(PEER,0)],BANK:[(r,j+1) for j,r in enumerate(bank)]}
        rows=engine['transpose_prefix'](word,requests,DONORS+1,until)
        assert len(rows)==DONORS+1 and all(0<=j<COLS for row,_ in rows for j in row)
        target=rows[0]
        exact_bank=list(zip(bank,rows[1:],strict=True))
        report.update(target_row=target,bank_support_sizes=[len(row[0]) for row in rows[1:]],
                      bank_rows_sha256=sha256(dumps(exact_bank,sort_keys=True).encode()).hexdigest())
        external=next((j for j in sorted(target[0]) if all(j not in row[0] for row in rows[1:])),None)
        if external is not None:
            result={'status':'absent_exterior_coordinate','coordinate':external,
                    'target_coefficient':str(Q(target[0][external],target[1]))}
        else:
            result=engine['exact_span'](exact_bank,target)
        check_decision(exact_bank,target,result)
        report.update(state=result['status'],decision=result)
        if result['status']=='exact_span':
            coeffs={int(r):Q(c) for r,c in result['coefficients'].items()}
            report.update(ordinary_additions=len(coeffs),
                          active_donor_lifetimes={r:owned.get(r,'public') for r in coeffs},
                          exact_dyadic=all(c.denominator.bit_count()==1 for c in coeffs.values()),
                          next_gate='prove exact physical direct MOVE and transported combination, then charge all added ADDs, precision, ownership, fixed tapes and compiler before build')
    except TimeoutError as err:
        report.update(capped=True,cap_reason=str(err))
    finally:
        alarm(0)
    print(dumps(report,sort_keys=True,indent=2,default=str))
    if report['capped']:
        raise SystemExit(2)


if __name__=='__main__':
    main()
