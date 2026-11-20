"""Check physical sparse repair, rectangular B1 calls and unchanged spectators."""

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from random import Random


from fine_ring import Tape, Trace
from scattered_cnot import ScatteredCNOT, SparseWord, WORD, exchange_number, literal


def ensure(test, message):
    if not test:
        raise ArithmeticError(message)


class CheckedOrdinary:
    def __init__(self):
        self.calls = []

    def __call__(self,field,h,prefix,gap,suffix):
        ensure(prefix*(1<<(2*h))*gap*suffix == len(field.cells), "incorrect complete B1 volume")
        a = suffix.bit_length()-1
        b = a+h+gap.bit_length()-1
        self.calls.append((h,prefix,gap,suffix))
        for bit in range(h):
            edges = ((a+bit,b+bit),)
            field = literal(field,edges)
            field = literal(field,((b+bit,a+bit),))
            field = literal(field,edges)
        return field


def source_index(i,pairs):
    original = i
    for a,b in pairs:
        original ^= ((i>>a)&1)<<b
    return original


def full(n,rows,pairs,short_policy=False,ordinary=CheckedOrdinary):
    tr = Trace()
    field = Tape(25,tr)
    N = (1<<n)*rows
    data = [(i,17-(i*13)%135113) for i in range(N)]
    for z in data:
        field.append(z)
    bank = ScatteredCNOT(ordinary())
    result = bank.run_parameters(field,pairs,n,1,1,5) if short_policy else bank(field,pairs,n,27)
    result.home()
    for i in range(N):
        ensure(result.read()==data[source_index(i,pairs)], "returned record is out of place")
    result.release()
    ensure(tr.live==0, "lost payload or repair tape")
    print(n,rows,pairs,"compact fixture" if short_policy else "standard",bank.receipt)
    return bank.receipt


def raw_forward(raw,address):
    for op in WORD:
        if op[0] == "swap":
            address = exchange_number(address,raw.shifts[op[1]],raw.shifts[op[2]],raw.h)
        else:
            s = raw.shifts[op[1]]
            mask = (1<<raw.widths[op[1]])-1
            old = (address>>s)&mask
            address ^= (old ^ ((old+raw.offset(address,op))&mask))<<s
    return address


def probe(addresses,raw):
    good = bad = 0
    for i in addresses:
        target = raw_forward(raw,i)
        ensure(raw.inverse(target)==i, "raw inverse failed on dirty controls")
        ensure(raw.bad(target)==raw.bad(i), "raw word did not preserve bad set")
        if raw.bad(i):
            bad += 1
        else:
            good += 1
            ensure(target==raw.ideal(i), "raw word changed a good spectator")
    ensure(good and bad, "the probe did not exercise both regimes")
    print("raw geometry",raw.n,raw.h,raw.g,raw.k,"good",good,"repaired",bad)


def integrated():
    from c_dispatch import run_word
    from compact_ordinary import transpose
    from fine_ring import grouped_h, tz
    from finite_c_word import Word
    from selected_h import SelectedH

    receipt = full(11,3,((6,2),),True,lambda:transpose)
    ensure(receipt.ordinary==16, "the actual ordinary adapter missed a call")
    n,selected = 8,(7,0,3,1)
    ops = tuple(op for r in range(3) for op in
                (("cx",r,0,1),("cx",r,0,1),("paid",r,0),("paid",r,1)))
    word = Word(2,3,0,ops)
    ensure(word.valid_syntax() and word.all_columns(), "invalid three-row integration word")
    real = ScatteredCNOT(transpose)
    rows = set()
    def bank(field,pairs,ambient,p):
        rows.add(len(field.cells)//(1<<ambient))
        return real(field,pairs,ambient,p)
    def native(field,request):
        return run_word(field,request,word,bank)
    trace = Trace()
    field = Tape(20,trace)
    data = [(7-((i*i+3)%113),((i*53+1)%127)-66) for i in range(1<<n)]
    for z in data:
        field.append(z)
    field = grouped_h(field,1<<n,selected,backend=SelectedH(native),fractional_bits=12,elementary_cap=0)
    mask = sum(1<<a for a in selected)
    field.home()
    for i in range(1<<n):
        a = b = 0
        for j in range(1<<n):
            if j & ~mask:
                continue
            x,y = data[(i&~mask)|j]
            sign = 1-2*((i&j).bit_count()&1)
            a += sign*x
            b += sign*y
        ensure(field.read() == (tz(a,1<<len(selected)),tz(b,1<<len(selected))),
               "the native recursive owner returned a wrong Walsh value")
    field.release()
    ensure(trace.live==0 and any(c>1 and c&(c-1) for c in rows),
           "the nested check missed non-power-of-two complete outer rows")
    print("integrated sparse and compact ordinary, nested native outer row counts",sorted(rows))


if __name__=="__main__":
    full(7,3,((6,0),(1,5)))
    repaired = full(11,3,((6,2),),True)
    ensure(repaired.batches>0 and repaired.repaired_records>0, "the fixture missed sparse repair")
    moved = full(12,1,((0,5),),True)
    third = full(12,1,((8,11),),True)
    tail = full(12,1,((7,0),),True)
    ensure(moved.batches and third.ordinary>moved.ordinary and tail.literal==1,
           "the low-suffix, third-reservoir or literal-tail case did not execute")
    probe(range(1<<11), SparseWord(11,1,1,5,((2,0),)))
    rng = Random(98133)
    probe((rng.randrange(1<<28) for _ in range(5000)),
          SparseWord(28,4,2,7,((3,0),(11,8))))
    integrated()
