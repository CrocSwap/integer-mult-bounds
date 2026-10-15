"""Independent rational comparisons for completed coefficient primitives."""
from fractions import Fraction as F
from hashlib import sha256

from streams import Tape,Meter,need,bit_key,key_value
from arithmetic import Grid,c_axis,scalar_add,scalar_scale,clear_packet,normalize_b


def integer(bits):
    value=key_value(bits)
    return value-(1<<len(bits)) if bits[-1] else value


def encode(values,grid):
    out=bytearray()
    for pair in values:
        for value in pair:
            number=value*(1<<grid.fraction_bits)
            need(number.denominator==1,"test input on common grid")
            need(-(1<<(grid.bits-1))<number<(1<<(grid.bits-1)),"test signed headroom")
            out.extend(bit_key(int(number)%(1<<grid.bits),grid.bits))
    return out


def decode(raw,grid):
    size=2*grid.bits;out=[]
    for start in range(0,len(raw),size):
        out.append(tuple(F(integer(raw[start+j*grid.bits:start+(j+1)*grid.bits]),
                           1<<grid.fraction_bits) for j in range(2)))
    return out


def c_oracle(values,address_bits,position,coefficients,inverse=False):
    out=values[:];mask=1<<(address_bits-position-1);sign=-1 if inverse else 1
    need(len(values)%((1<<address_bits)*coefficients)==0,"oracle complete outer rows")
    for row in range(len(values)//coefficients):
        if row&mask:continue
        for k in range(coefficients):
            i,j=row*coefficients+k,(row^mask)*coefficients+k
            ar,ai=values[i];br,bi=values[j]
            out[i]=((ar+br-sign*(ai-bi))/2,(ai+bi+sign*(ar-br))/2)
            out[j]=((ar+br+sign*(ai-bi))/2,(ai+bi-sign*(ar-br))/2)
    return out


def multiply(a,b):return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]


def run():
    grid=Grid(96,40);meter=Meter();address_bits=6;coefficients=2;outer_rows=3
    initial=[(F((i%11)-5,16),F((i%7)-3,16)) for i in range(outer_rows*(1<<address_bits)*coefficients)]
    raw=encode(initial,grid);stream=Tape(meter,raw);expected=initial
    selected=(0,2,5)
    for axis in selected:
        stream=c_axis(stream,address_bits,axis,coefficients,grid,outer_rows=outer_rows)
        expected=c_oracle(expected,address_bits,axis,coefficients)
        need(decode(stream.data,grid)==expected and not grid.workspace,"exact C axis and work closure")
    digest=sha256(stream.data).hexdigest()
    for axis in reversed(selected):stream=c_axis(stream,address_bits,axis,coefficients,grid,True,outer_rows)
    need(stream.data==raw,"completed C/inverse returns exact guarded words")
    source=Tape(meter,raw);target=Tape(meter,raw)
    target=scalar_add(target,source,F(-3,4),grid)
    need(decode(target.data,grid)==[(r/4,i/4) for r,i in initial],"exact Horner and halving")
    need(source.data==raw and source.head==0,"scalar source restoration")
    target=scalar_add(target,source,F(3,4),grid)
    need(target.data==raw and not grid.workspace,"scalar inverse with common grid")
    scaled=scalar_scale(Tape(meter,raw),F(-5,8),grid)
    need(decode(scaled.data,grid)==[tuple(F(-5,8)*x for x in z) for z in initial],"exact scale stream")
    cleared=clear_packet(scaled)
    need(len(cleared.data)==len(raw) and not any(cleared.data) and cleared.head==0,
         "clear preserves logical packet extent")
    normalization=[]
    for axes in (0,1,2,3,8,17):
        output=normalize_b(Tape(meter,raw),axes,grid)
        power=(F(1),F(0))
        for _ in range(axes):power=multiply(power,(F(1,2),F(-1,2)))
        need(decode(output.data,grid)==[multiply(z,power) for z in initial],"closed b-power normalization")
        normalization.append(axes)
    # Rounding at a child return destroys a cancellation that the grid keeps.
    small=Grid(24,12);start=[(F(1,4),F(0)),(F(0),F(0))]
    first=c_axis(Tape(Meter(),encode(start,small)),1,0,1,small)
    rounded=[tuple(F(int(4*x),4) for x in z) for z in decode(first.data,small)]
    wrong=c_axis(Tape(Meter(),encode(rounded,small)),1,0,1,small,True)
    need(decode(wrong.data,small)!=start,"child requantization control")
    bad=bit_key(1,small.bits)
    try:small.divide(bad,1)
    except ValueError as error:need(str(error)=="division discards only reserved zero bits","exact division guard")
    else:raise ValueError("unreserved division accepted")
    return {"status":"PASS_EXACT_GAUSSIAN_STREAM_PRIMITIVES","address_bits":address_bits,
            "outer_rows":outer_rows,"records":outer_rows*(1<<address_bits),"coefficients_per_record":coefficients,
            "selected_axes":list(selected),"word_bits":grid.bits,"fraction_bits":grid.fraction_bits,
            "C_output_sha256":digest,"normalization_axes":normalization,
            "completed_inverse":True,"scalar_source_restored":True,
            "child_requantization_control":"REJECT","unreserved_halving_control":"REJECT",
            "exact_divisions":grid.exact_divisions,"peak_arithmetic_words":grid.peak_words,
            "arithmetic_bit_work":grid.arithmetic_steps}
