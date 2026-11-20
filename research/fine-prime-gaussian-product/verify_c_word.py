from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from itertools import permutations
from c_dispatch import run_word, xor_literal, matchings
from finite_c_word import Word, NAMES, parse, compile_within
from fine_ring import Tape, Trace, grouped_h, tz
from selected_h import SelectedH


def raw(W):
    ops=[]
    for role in range(W):
        ops.extend([('add',W,role),('sub',W,role),('half',role),('add',role,role),
                    ('i',role),('i',role),('neg',role),('unit',role),('unit',role),
                    ('unit',role),('unit',role),('x',role,1),('x',role,1),
                    ('cx',role,1,0),('cx',role,1,0),('cz',role,1,0),('cz',role,1,0),
                    ('s',role,1),('s',role,1),('s',role,1),('s',role,1),
                    ('paid',role,0),('paid',role,1)])
    return Word(2,W,1,tuple(ops))


def numeric(word,bits,ambient):
    tr=Trace()
    tape=Tape(21,tr)
    values=[(i*53%113-64,i*i*11%191-100) for i in range(1<<ambient)]
    for z in values:
        tape.append(z)
    def native(field,req):
        return run_word(field,req,word,xor_literal)
    tape=grouped_h(tape,1<<ambient,bits,backend=SelectedH(native),fractional_bits=15,elementary_cap=0)
    mask=sum(1<<k for k in bits)
    labels=[i for i in range(1<<ambient) if not i&~mask]
    tape.home()
    for i in range(1<<ambient):
        a=b=0
        for j in labels:
            u,v=values[(i&~mask)|j]
            sign=-1 if (i&j).bit_count()%2 else 1
            a+=sign*u
            b+=sign*v
        if not (tape.read()==(tz(a,len(labels)),tz(b,len(labels)))):
            raise ArithmeticError('independent check failed at verify_c_word.py:39')
    tape.release()
    if not (tr.live==0):
        raise ArithmeticError('independent check failed at verify_c_word.py:41')
    print('complete finite native C word over all rows',word.productive,bits,ambient,'routed and restored')


def main():
    for w in (2,3):
        program=raw(w)
        if not (program.valid_syntax() and program.all_columns() and not program.funded()):
            raise ArithmeticError('independent check failed at verify_c_word.py:48')
        tokens=[program.dimension,program.productive,program.owned]
        for op,*args in program.ops:
            tokens.extend((NAMES.index(op),*args))
        if not (parse(''.join('1'*i+'0' for i in tokens))==program):
            raise ArithmeticError('independent check failed at verify_c_word.py:52')
        numeric(program,(6,0,3,2),8)
        numeric(program,(0,3,6,2,4),9)
    # Two columnwise global i phases and a fixed minus cancel for one column only.
    good=raw(2)
    bad=Word(2,2,1,good.ops+(('unit',0),('unit',0),('neg',0)))
    if not (not bad.all_columns()):
        raise ArithmeticError('independent check failed at verify_c_word.py:58')
    if not (not Word(2,2,0,(('paid',0,0),('paid',1,0))).all_columns()):
        raise ArithmeticError('independent check failed at verify_c_word.py:59')
    if not (compile_within(1<<10) is None):
        raise ArithmeticError('independent check failed at verify_c_word.py:60')
    ambient=13
    n=1<<ambient
    values=[((47*i)%1009-501,(i*i*3)%977-469) for i in range(n)]
    tr=Trace()
    unsubsidized=Tape(15,tr)
    for z in values:
        unsubsidized.append(z)
    unsubsidized=grouped_h(unsubsidized,n,tuple(range(ambient)),fractional_bits=12)
    for b in range(ambient):
        block=1<<b
        for start in range(0,n,2*block):
            for off in range(block):
                i=start+off
                a,b0=values[i]
                c,d=values[i+block]
                values[i],values[i+block]=(a+c,b0+d),(a-c,b0-d)
    unsubsidized.home()
    if not (all(unsubsidized.read()==(tz(a,n),tz(b,n)) for a,b in values)):
        raise ArithmeticError('independent check failed at verify_c_word.py:78')
    unsubsidized.release()
    if not (tr.live==0):
        raise ArithmeticError('independent check failed at verify_c_word.py:80')
    print('default undiscovered-word path, rank 13, 8192 complete rows, peak tracked bits',tr.high_water)
    count=0
    for ambient in range(1,5):
        for rank in range(1,ambient+1):
            for bits in permutations(range(ambient),rank):
                schedule=matchings(bits,ambient)
                mapped=list(range(1<<ambient))
                for pairs in schedule:
                    mapped=[v^sum((((v>>a)^(v>>b))&1)*((1<<a)|(1<<b)) for a,b in pairs) for v in mapped]
                for i,m in enumerate(mapped):
                    if not (all((m>>j&1)==(i>>b&1) for j,b in enumerate(bits))):
                        raise ArithmeticError('independent check failed at verify_c_word.py:91')
                count+=1
    print('all-column f=1 cancellation and missing input controls rejected;',count,'complete selector extensions')


if __name__=='__main__':
    main()
