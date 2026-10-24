"""Unit-head binary arithmetic on the retained record Tape alphabet.
JoyboyBrian; substantial OpenAI Codex assistance; Apache-2.0.
Only symbols, carries, borrows and comparison signs enter runtime control.
"""
from records import Tape
from cardinality import Natural
from words import ZERO, ONE, LEFT, RIGHT, BLANK, need


def view(tape):
    result=object.__new__(Natural);result.tape=tape
    return result


def scan(tape, positive=False):
    """Validate before mutation; borrowed divisor must be canonical."""
    tape.rewind();seen=False;nonzero=False;last=ZERO;many=False
    try:
        while tape.read()!=RIGHT:
            bit=tape.read();need(bit in (ZERO,ONE),'binary input digit')
            many=seen;seen=True;nonzero=nonzero or bit==ONE;last=bit;tape.step(1)
    finally:tape.rewind()
    need(seen and (last==ONE or not many),'canonical binary input')
    need(not positive or nonzero,'positive binary divisor')


def shift(tape, bit):
    carry=bit
    while tape.read()!=RIGHT:
        following=tape.read();tape.write(carry);carry=following;tape.step(1)
    if carry:
        tape.write(carry);tape.step(1);tape.write(RIGHT)
    tape.rewind()


def add(target, source):
    """Canonical nonnegative addition; source and target are distinct."""
    carry=ZERO
    while source.read()!=RIGHT or target.read()!=RIGHT or carry:
        a=source.read();b=target.read()
        total=(ZERO if a==RIGHT else a)+(ZERO if b==RIGHT else b)+carry
        target.write(total&1);carry=total>>1;target.step(1)
        if b==RIGHT:target.write(RIGHT)
        if a!=RIGHT:source.step(1)
    source.rewind();target.rewind()


def multiply_into(left,right,output):
    need(left is not right and output is not left and output is not right,'distinct multiplication roles')
    need(output.read()==BLANK,'blank multiplication output')
    output.append(ZERO);output.append(RIGHT);output.rewind()
    view(right).msb()
    while right.read()!=LEFT:
        shift(output,ZERO)
        if right.read()==ONE:add(output,left)
        right.step(-1)
    right.step(1)
    view(output).normalize()


def power_into(radix, dimension, first, second):
    """dimension is a fixed compiled source parameter, not a decoded input."""
    need(radix is not first and radix is not second and first is not second,'distinct power roles')
    need(type(dimension) is int and dimension>0,'compiled positive dimension')
    scan(radix,True);need(first.read()==second.read()==BLANK,'blank power roles')
    first.append(ONE);first.append(RIGHT);first.rewind()
    for _ in range(dimension*dimension):
        multiply_into(first,radix,second)
        first.clear();first,second=second,first
    return first,second


def divide(numerator,divisor,remainder,denominator):
    """Write quotient in numerator and owned remainder; erase denominator.

    All four roles are distinct, numerator/divisor canonical, scratch blank.
    Successful execution restores every borrowed divisor byte/head. General
    allocation failure rollback is outside this valid-input refinement.
    """
    need(len({id(x) for x in (numerator,divisor,remainder,denominator)})==4,'distinct division roles')
    scan(numerator);scan(divisor,True)
    need(remainder.read()==denominator.read()==BLANK,'blank division scratch')
    while divisor.read()!=RIGHT:
        denominator.append(divisor.read());remainder.append(ZERO);divisor.step(1)
    divisor.rewind()
    denominator.append(ZERO);denominator.append(RIGHT);denominator.rewind()
    remainder.append(ZERO);remainder.append(RIGHT);remainder.rewind()
    view(numerator).msb()
    while numerator.read()!=LEFT:
        carry=numerator.read()
        while remainder.read()!=RIGHT:
            following=remainder.read();remainder.write(carry);carry=following;remainder.step(1)
        need(carry==ZERO,'padded remainder shift')
        remainder.rewind();comparison=0
        while remainder.read()!=RIGHT:
            a,b=remainder.read(),denominator.read()
            if a!=b:comparison=1 if a>b else -1
            remainder.step(1);denominator.step(1)
        remainder.rewind();denominator.rewind()
        if comparison>=0:
            borrow=ZERO
            while remainder.read()!=RIGHT:
                difference=remainder.read()-denominator.read()-borrow
                remainder.write(difference&1);borrow=ONE if difference<0 else ZERO
                remainder.step(1);denominator.step(1)
            need(borrow==ZERO,'nonnegative remainder subtraction')
            remainder.rewind();denominator.rewind();numerator.write(ONE)
        else:numerator.write(ZERO)
        numerator.step(-1)
    numerator.step(1)
    view(numerator).normalize();view(remainder).normalize();denominator.clear()


def zero(tape):
    result=True
    while tape.read()!=RIGHT:
        result=result and tape.read()==ZERO;tape.step(1)
    tape.rewind();return result
