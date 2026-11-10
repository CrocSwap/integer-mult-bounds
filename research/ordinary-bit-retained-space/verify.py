#!/usr/bin/env python3
"""Source pins, literal elementary scans, retained histories and negative controls."""
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from tapes import Buckets, Tape, reference, require

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def source_check():
    manifest = json.loads((HERE/'SOURCES.json').read_text())
    count = 0
    for entry in manifest['files']:
        if entry['usage'] == 'input':
            payload = (ROOT/entry['path']).read_bytes()
            require(hashlib.sha256(payload).hexdigest() == entry['sha256'],
                    'source hash mismatch: '+entry['path'])
            count += 1
    return count


def scanner_checks():
    total_cases = total_moves = 0
    shapes = [(2,1,1,1,1), (2,2,1,1,1), (2,2,2,3,2),
              (2,3,1,1,1), (3,1,2,2,2), (3,2,1,1,1)]
    for q,e,p,g,s in shapes:
        volume = p*g*s*q**(2*e)
        work = Buckets(q)
        fixtures = [[0]*volume, [1]*volume]
        fixtures += [[int(i == k) for i in range(volume)] for k in range(volume)]
        for bits in fixtures:
            work.load(bits)
            for digit in range(e):
                before = work.values()
                lengths = work.exchange(e,digit,p,g,s)
                require(work.values() == reference(before,q,e,p,g,s,digit),
                        'digit endpoint')
                require(sum(lengths) == volume, 'complete bucket volume')
            require(work.values() == reference(bits,q,e,p,g,s), 'whole chunk endpoint')
            require(work.live() == volume, 'scratch erasure')
            require(work.backing() <= (q*q+2)*(volume+1), 'per-tape extent bound')
            total_cases += 1
        total_moves += sum(t.moves for t in work.tapes)
    return {'payload_cases':total_cases,'unit_moves':total_moves,'shapes':len(shapes)}


def history_checks():
    work = Buckets(3)
    maxima = []
    for e in [1,2,3,4,1,3,1]:
        volume = 3**(2*e)
        work.load([0]*volume)
        work.exchange(e,0)
        maxima.append(volume)
        require(work.backing() <= 11*(max(maxima)+1), 'history envelope')
    backing = work.backing()
    bucket_backing = len(work.tapes[2].visited)
    for _ in range(100):
        work.load([0]*9)
        work.exchange(1,0)
    require(work.backing() == backing, 'reused origin retains max, not sum')
    require(bucket_backing >= 3**6, 'erased long bucket remains charged')
    require(work.live() == 9 and work.backing() > 9*11,
            'live-only/current-call accounting must fail')
    require(all(not t.cells for t in work.tapes[2:]), 'warm tail is blank')
    return {'retained_cells':backing,'final_live_cells':work.live(),
            'retained_bucket_cells':bucket_backing,'repetitions':100}


def interval_checks():
    cases = 0
    # Independent flat coordinate union; no Bucket implementation reused.
    for contraction in [2,3,5]:
        for depth in range(5):
            volume = contraction**depth
            tapes = [Tape() for _ in range(3)]
            def walk(v,d,origins):
                lengths = [(i+1)*v for i in range(3)]
                for t,start,length in zip(tapes,origins,lengths):
                    t.seek(start+length)
                    t.seek(start)
                if d:
                    next_origins = [x+y for x,y in zip(origins,lengths)]
                    for _ in range(3):
                        walk(v//contraction,d-1,next_origins)
                for t,start in zip(tapes,origins):
                    t.seek(start)
            walk(volume,depth,[0,0,0])
            exact = sum((i+1)*sum(volume//contraction**j for j in range(depth+1))+1
                        for i in range(3))
            require(sum(len(t.visited) for t in tapes) == exact, 'interval union')
            require(exact <= 6*volume*Fraction(contraction,contraction-1)+3,
                    'active-chain bound')
            cases += 1
    return cases


def controls():
    names = []
    bad = Buckets(3)
    bits = [int(i==1) for i in range(9)]
    bad.load(bits)
    bad.exchange(1,0,wrong_order=True)
    require(bad.values() != reference(bits,3,1,1,1,1), 'wrong merge control')
    names.append('wrong inverse bucket order')
    append = Buckets(3)
    for invocation in range(24):
        append.load([0]*9, origin=invocation*10)
        append.exchange(1,0)
    require(append.backing() > 11*(9+1), 'append-only origin control')
    names.append('append-only history exceeds volume envelope')
    warm = Tape()
    warm.seek(1000)
    warm.seek(0)
    warm.erase(0,2)
    require(len(warm.visited)>100 and not warm.cells, 'erasure does not deallocate')
    names.append('erased cells remain backing')
    require(len(warm.visited)>10, 'entry backing is nonzero')
    names.append('omitted entry backing')
    a,b = Tape(),Tape()
    a.seek(80); a.seek(0)
    b.seek(80); b.seek(0)
    require(len(a.visited)+len(b.visited)>max(len(a.visited),len(b.visited)),
            'sum per-tape history, not maximum current use')
    names.append('inactive tape history')
    original_backing = Buckets.backing
    try:
        Buckets.backing = Buckets.live
        rejected = False
        try:
            history_checks()
        except ValueError:
            rejected = True
        require(rejected, 'live-only meter mutation must be rejected')
    finally:
        Buckets.backing = original_backing
    names.append('mutated live-only meter rejected')
    original_erase = Tape.erase
    try:
        Tape.erase = lambda self, origin, extent: self.seek(origin)
        rejected = False
        try:
            no_erase = Buckets(3)
            no_erase.load([0]*9)
            no_erase.exchange(1,0)
        except ValueError as error:
            rejected = str(error) == 'erased buckets'
        require(rejected, 'missing erase mutation must be rejected at cleanup')
    finally:
        Tape.erase = original_erase
    names.append('mutated missing erasure rejected')
    return names


def padding_checks():
    cases=0
    for divisor in range(1,30):
        for rows in range(divisor,5*divisor+1):
            padded=((rows+divisor-1)//divisor)*divisor
            require(rows<=padded<2*rows and padded%divisor==0, 'one root padding')
            cases+=1
    for q in [3,5,7]:
        for binary_width in range(1,65):
            extent=2**binary_width
            padded=1
            while padded<extent:
                padded*=q
            require(padded<q*extent, 'radix range factor')
            require(2*padded*padded<2*q*q*extent*extent, 'combined volume factor')
            cases+=1
    return cases


def main():
    result={'source_inputs':source_check(),'scanner':scanner_checks(),
            'history':history_checks(),'nested_cases':interval_checks(),
            'negative_controls':controls(),'padding_cases':padding_checks(),
            'scope':'finite source-algorithm corroboration; written universal space proof separate'}
    print(json.dumps(result,sort_keys=True,indent=2))
    print('PASS_ORDINARY_BIT_RETAINED_SPACE')


if __name__=='__main__':
    main()
