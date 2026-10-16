"""Columnwise lift of fixed binary affine maps and Gaussian unit phases."""
from streams import Tape,need,copy,digit_permutation,flip_digit
from compact import Compact,execute


def binary_word(recipe):
    rows=list(recipe["matrix_rows"]);m=len(rows);reduction=[]
    need(0<m<=73 and all(0<=row<1<<m for row in rows),"fixed binary matrix extent")
    for j in range(m):
        p=next((i for i in range(j,m) if rows[i]>>j&1),None)
        need(p is not None,"invertible monomial linear map")
        if p!=j:
            for target,source in ((j,p),(p,j),(j,p)):
                rows[target]^=rows[source];reduction.append(("add",target,source))
        for i in range(m):
            if i!=j and rows[i]>>j&1:
                rows[i]^=rows[j];reduction.append(("add",i,j))
    need(rows==[1<<i for i in range(m)],"complete binary elimination")
    return tuple(reversed(reduction))+tuple(("flip",i,-1) for i in range(m) if recipe["offset"]>>i&1)


def column_phase(recipe,x):
    m=len(recipe["matrix_rows"])
    # Raw retained recipes can store symmetric/diagonal entries. The source
    # qvalue convention uses only the strict upper part; alpha holds diagonals.
    value=sum(recipe["linear_Z4"][i] for i in range(m) if x>>i&1)
    value+=2*sum(((recipe["quadratic_rows"][i]>>(i+1))&(x>>(i+1))).bit_count()
                 for i in range(m) if x>>i&1)
    return value%4


def column_map(recipe,x):
    return recipe["offset"]^sum(((row&x).bit_count()%2)<<i
                                for i,row in enumerate(recipe["matrix_rows"]))


def columns(state,m,f,K,rho):
    return tuple(sum(((state["v"+str(i)]>>(rho+j*K))&1)<<i for i in range(m)) for j in range(f))


def tensor_phase(recipe,state,f,K,rho,omit_tensor_constant=False):
    constant=recipe["phase"]*(1 if omit_tensor_constant else f)
    return (constant+sum(column_phase(recipe,x)
                        for x in columns(state,len(recipe["matrix_rows"]),f,K,rho)))%4


def negate(bits):
    """Two's-complement negation in least-significant-bit stream order."""
    carry=1;out=bytearray()
    for bit in bits:
        value=(1-bit)+carry;out.append(value&1);carry=value>>1
    return out


def phase_pass(source,layout,recipe,f,K,rho,coefficient_bits,inverse=False,
               omit_tensor_constant=False):
    need(coefficient_bits>=2 and layout.record_bits%(2*coefficient_bits)==0,"Gaussian record extent")
    source.rewind();out=Tape(source.meter);real=Tape(source.meter);imag=Tape(source.meter)
    def emit(tape,negative):
        if negative:
            carry=1
            for _ in range(coefficient_bits):
                value=(1-tape.read(1)[0])+carry
                out.write(bytes((value&1,)));carry=value>>1
        else:copy(tape,out,coefficient_bits)
        tape.finish()
    for index in range(layout.records):
        phase=tensor_phase(recipe,layout.decode(index),f,K,rho,omit_tensor_constant)
        if inverse:phase=-phase%4
        source.meter.control_evaluations+=1
        for _ in range(layout.record_bits//(2*coefficient_bits)):
            copy(source,real,coefficient_bits);copy(source,imag,coefficient_bits)
            real.rewind();imag.rewind()
            if phase==0:emit(real,False);emit(imag,False)
            elif phase==1:emit(imag,True);emit(real,False)
            elif phase==2:emit(real,True);emit(imag,True)
            else:emit(imag,False);emit(real,True)
            real.erase();imag.erase()
    source.finish();source.erase();out.rewind();return out


def execute_monomial(source,layout,recipe,f,K,G,rho,coefficient_bits,inverse=False,
                     omit_tensor_constant=False):
    need(f>=1,"positive tensor width");word=binary_word(recipe)
    if not inverse:
        source=phase_pass(source,layout,recipe,f,K,rho,coefficient_bits,
                          omit_tensor_constant=omit_tensor_constant)
    for kind,i,k in reversed(word) if inverse else word:
        target="v"+str(i);control=None if kind=="flip" else "v"+str(k)
        if f>1:
            source=execute(source,layout,Compact(f-1,K,G,rho,control,target,
                           False if control is None else k>i))
        elif control is None:
            source=flip_digit(source,layout.bits,layout.position(target,rho),layout.record_bits)
        else:
            a,b=layout.position(control,rho),layout.position(target,rho)
            mapping=(0,1,3,2) if a<b else (0,3,2,1)
            source=digit_permutation(source,layout.bits,min(a,b),max(a,b),layout.record_bits,mapping)
    if inverse:
        source=phase_pass(source,layout,recipe,f,K,rho,coefficient_bits,True,
                          omit_tensor_constant)
    return source
