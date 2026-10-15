"""Sequential stream lowering with a charged completed-interchange oracle.

The split/merge operations instantiate the retained ordered-affine stream lemma.
Jose Manuel, with substantial OpenAI Codex assistance. Apache-2.0.
"""

from collections import Counter
from dataclasses import dataclass, field
from fractions import Fraction as F
from math import gcd


def need(ok, message):
    if not ok:
        raise ValueError(message)


@dataclass
class Meter:
    reads: int = 0
    writes: int = 0
    moves: int = 0
    primitives: Counter = field(default_factory=Counter)
    ordinary: list = field(default_factory=list)


class Tape:
    """Append-only output or sequential input; no seek operation."""
    def __init__(self, meter, bits=()):
        self.meter, self.bits, self.head = meter, list(bits), 0

    def read(self):
        need(self.head < len(self.bits), "read beyond stream")
        value = self.bits[self.head]
        self.head += 1
        self.meter.reads += 1
        self.meter.moves += 1
        return value

    def write(self, value):
        need(self.head == len(self.bits), "output must append")
        need(value in (0,1), "bit alphabet")
        self.bits.append(value)
        self.head += 1
        self.meter.writes += 1
        self.meter.moves += 1

    def rewind(self):
        self.meter.moves += self.head
        self.head = 0

    def finished(self):
        need(self.head == len(self.bits), "unconsumed stream suffix")


def copy_bits(source, target, count):
    for _ in range(count):
        target.write(source.read())


def rotate_fibers(source, qpower, block, fibers, offset):
    """Move data from coordinate y to y+offset(prefix), modulo qpower."""
    need(qpower>=1 and block>=1 and fibers>=1, "complete fiber dimensions")
    need(len(source.bits)==qpower*block*fibers, "fiber volume")
    meter=source.meter;meter.primitives["ordered_shift"]+=1
    left,right,out=(Tape(meter) for _ in range(3))
    source.rewind()
    for prefix in range(fibers):
        a=offset(prefix)%qpower
        copy_bits(source,left,(qpower-a)*block)
        copy_bits(source,right,a*block)
    source.finished();left.rewind();right.rewind()
    for prefix in range(fibers):
        a=offset(prefix)%qpower
        copy_bits(right,out,a*block)
        copy_bits(left,out,(qpower-a)*block)
    left.finished();right.finished()
    return out


def multiply_fibers(source, qpower, block, fibers, c, inverse=False):
    """Fixed positive integer unit, implemented by monotone pieces."""
    need(c>=1 and gcd(c,qpower)==1, "fixed unit multiplier")
    need(len(source.bits)==qpower*block*fibers, "scaling volume")
    meter=source.meter;meter.primitives["inverse_integer_scale" if inverse else "integer_scale"]+=1
    if c==1 or qpower==1:
        return source
    source.rewind()
    pieces=[Tape(meter) for _ in range(c)];out=Tape(meter)
    lengths=[((j+1)*qpower+c-1)//c-(j*qpower+c-1)//c for j in range(c)]
    inv=pow(qpower,-1,c)
    if not inverse:
        for _ in range(fibers):
            for j,length in enumerate(lengths):copy_bits(source,pieces[j],length*block)
        for tape in pieces:tape.rewind()
        for _ in range(fibers):
            for y in range(qpower):copy_bits(pieces[(-y*inv)%c],out,block)
    else:
        for _ in range(fibers):
            for y in range(qpower):copy_bits(source,pieces[(-y*inv)%c],block)
        for tape in pieces:tape.rewind()
        for _ in range(fibers):
            for j,length in enumerate(lengths):copy_bits(pieces[j],out,length*block)
    source.finished()
    for tape in pieces:tape.finished()
    return out


def negate_fibers(source,qpower,block,fibers):
    """Reverse blocks1..Q-1, restoring the bit order inside each block."""
    need(len(source.bits)==qpower*block*fibers,"negation volume")
    meter=source.meter;meter.primitives["negation"]+=1
    source.rewind();out=Tape(meter)
    for _ in range(fibers):
        copy_bits(source,out,block)
        stack=[]
        for _ in range((qpower-1)*block):
            stack.append(source.read());meter.writes+=1;meter.moves+=1
        for _ in range(qpower-1):
            temporary=[]
            for _ in range(block):
                temporary.append(stack.pop());meter.reads+=1;meter.writes+=1;meter.moves+=2
            for _ in range(block):
                out.write(temporary.pop());meter.reads+=1;meter.moves+=1
        need(not stack,"local stack restored")
    source.finished()
    return out


def unit_scale(source,qpower,block,fibers,c):
    c=F(c);need(c and gcd(c.numerator*c.denominator,qpower)==1,"rational unit")
    if c<0:source=negate_fibers(source,qpower,block,fibers)
    if abs(c.numerator)!=1:source=multiply_fibers(source,qpower,block,fibers,abs(c.numerator))
    if c.denominator!=1:source=multiply_fibers(source,qpower,block,fibers,c.denominator,True)
    return source


def completed_swap_oracle(source,qpower,before,middle,suffix):
    """Pad, invoke the assumed complete binary swap, and unpad.

    Random access occurs only inside the declared ordinary-callee oracle.
    Its time is charged as T_old, never as a linear stream primitive.
    """
    need(len(source.bits)==before*qpower*middle*qpower*suffix,"swap volume")
    if qpower==1:return source
    u=(qpower-1).bit_length();power=1<<u
    meter=source.meter;source.rewind();padded=Tape(meter)
    for _ in range(before):
        for x in range(power):
            for _ in range(middle):
                for y in range(power):
                    if x<qpower and y<qpower:copy_bits(source,padded,suffix)
                    else:
                        for _ in range(suffix):padded.write(0)
    source.finished()
    meter.ordinary.append({"binary_width":u,"real_volume":len(source.bits),
                           "padded_volume":len(padded.bits),"before":before,"middle":middle,"suffix":suffix})
    need(len(padded.bits)<4*len(source.bits),"two-field padding factor")
    # This exact dense oracle stands for the completed previous-stage call.
    result=[]
    for a in range(before):
        for x in range(power):
            for z in range(middle):
                for y in range(power):
                    start=(((a*power+y)*middle+z)*power+x)*suffix
                    result.extend(padded.bits[start:start+suffix])
    exchanged=Tape(meter,result);out=Tape(meter)
    for _ in range(before):
        for x in range(power):
            for _ in range(middle):
                for y in range(power):
                    for _ in range(suffix):
                        bit=exchanged.read()
                        if x<qpower and y<qpower:out.write(bit)
                        else:need(bit==0,"completed swap preserves genuine rectangle")
    exchanged.finished()
    return out


def low_update(x,y,c,q,scale=False):
    c=F(c);a,d=c.numerator,c.denominator
    need(gcd(d,q)==1 and (not scale or gcd(a,q)==1),"radix unit")
    numerator=a*y if scale else d*y+a*x
    new=numerator*pow(d,-1,q)%q
    carry,remainder=divmod(numerator-d*new,q)
    need(remainder==0,"integer carry")
    return new,carry


def permute_finite_classes(source,before,classes,block,permutation):
    """Move whole high packets between a fixed finite set of low GL types."""
    need(sorted(permutation)==list(range(classes)),"finite class bijection")
    need(len(source.bits)==before*classes*block,"finite class layout")
    source.meter.primitives["finite_class_permutation"]+=1
    source.rewind();pieces=[Tape(source.meter) for _ in range(classes)]
    for _ in range(before):
        for old in range(classes):copy_bits(source,pieces[permutation[old]],block)
    source.finished()
    for piece in pieces:piece.rewind()
    out=Tape(source.meter)
    for _ in range(before):
        for piece in pieces:copy_bits(piece,out,block)
    for piece in pieces:piece.finished()
    return out


def add_high(source,high,c,carry,before,middle,suffix,reversed_fields=False):
    """carry(a) uses the prefix before both selected high fields."""
    c=F(c)
    need(len(source.bits)==before*high*middle*high*suffix,"high packet layout")
    if high==1:return source
    if reversed_fields:source=completed_swap_oracle(source,high,before,middle,suffix)
    fibers=before*high*middle
    source=unit_scale(source,high,suffix,fibers,F(c.denominator))
    source=rotate_fibers(source,high,suffix,fibers,
                         lambda prefix:c.numerator*((prefix//middle)%high)+carry(prefix//(high*middle)))
    source=unit_scale(source,high,suffix,fibers,F(1,c.denominator))
    if reversed_fields:source=completed_swap_oracle(source,high,before,middle,suffix)
    return source


def scale_high(source,high,c,carry,before,suffix):
    c=F(c)
    need(len(source.bits)==before*high*suffix,"single high-field layout")
    if high==1:return source
    source=unit_scale(source,high,suffix,before,F(c.numerator))
    source=rotate_fibers(source,high,suffix,before,carry)
    return unit_scale(source,high,suffix,before,F(1,c.denominator))


def physical_add(source,q,width,low_x,low_y,c,before=1,middle=1,suffix=1,reversed_fields=False,omit_carry=False):
    need(q>=3 and q%2 and width>=1,"odd radix and positive width")
    high=q**(width-1);c=F(c);new,carry=low_update(low_x,low_y,c,q)
    if omit_carry:carry=0
    return add_high(source,high,c,lambda _:carry,before,middle,suffix,reversed_fields),new


def physical_scale(source,q,width,low,c,before=1,suffix=1):
    high=q**(width-1);c=F(c);new,carry=low_update(0,low,c,q,True)
    return scale_high(source,high,c,lambda _:carry,before,suffix),new
