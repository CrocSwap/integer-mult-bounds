"""Run an all-column C word on independent complete rows with a common binary grid."""
from fine_ring import Tape, map_tape
from finite_c_word import compile_within, turn, pm
from selected_h import SelectedH, single_c_numerator


def xor_literal(field, pairs, address_bits, precision):
    """Execute disjoint, aligned binary shears on each complete global row."""
    del address_bits, precision
    count=len(field.cells)
    for a,b in pairs:
        buckets=[Tape(field.width, field.trace) for _ in range(4)]
        field.home()
        for i in range(count):
            buckets[2*(i>>a&1)+(i>>b&1)].append(field.read())
        field.release()
        for bucket in buckets:
            bucket.home()
        out=Tape(field.width,field.trace)
        for i in range(count):
            c=i>>a&1
            out.append(buckets[2*c+(c^(i>>b&1))].read())
        for bucket in buckets:
            bucket.release()
        field=out
    return field


def matchings(bits, ambient):
    """Factor the complete extension of selected[i] -> i as two involutions."""
    image=dict(zip(bits,range(len(bits))))
    source=set(bits)
    target=set(range(len(bits)))
    image.update(zip(sorted(target-source),sorted(source-target)))
    first,second=[],[]
    seen=set()
    for i in sorted(image):
        if i in seen:
            continue
        cycle=[]
        j=i
        while j not in seen:
            seen.add(j)
            cycle.append(j)
            j=image[j]
        for k,a in enumerate(cycle):
            for off,pairs in ((0,first),(1,second)):
                b=cycle[(off-k)%len(cycle)]
                if a<b:
                    pairs.append((a,b))
    return tuple(tuple(pairs) for pairs in (first,second) if pairs)


def route(field, schedule, address_bits, p, xor_bank):
    for pairs in schedule:
        for swap_direction in (False,True,False):
            edges=tuple((b,a) if swap_direction else (a,b) for a,b in pairs)
            field=xor_bank(field,edges,address_bits,p)
    return field


def reverse_blocks(field, size):
    out=Tape(field.width,field.trace)
    for start in range(0,len(field.cells),size):
        field.seek(start+size)
        for _ in range(size):
            out.append(field.read_back())
    field.release()
    return out


def exact_drop(z, bits):
    scale=1<<bits
    if (z[0]|z[1])&(scale-1):
        raise ArithmeticError("common dyadic grid does not contain this exact value")
    return z[0]>>bits,z[1]>>bits


def one_c(field, axis):
    count=len(field.cells)
    return map_tape(single_c_numerator(field,axis),count,lambda _,z:exact_drop(z,1))


def run_word(field, request, word, xor_bank):
    """The only accelerated address operation is xor_bank on disjoint real bit pairs."""
    h=request.rank
    n=request.address_bits
    p=request.input_fraction
    N,W=word.dimension,word.productive
    depth=0
    e=h
    while e>=N:
        e//=N
        depth+=1
    stock=W**depth
    row_bits=(stock-1).bit_length()
    if row_bits+h>n:
        # The growing geometry admits this case only below a fixed size.
        return unlimited_elementary(field,request)
    schedule=matchings(request.selected,n)
    field=route(field,schedule,n,p,xor_bank)
    # Each completed rank-s child adds at most s to dyadic height and to log norm.
    # Direct instructions add at most one per scalar gate and one per rank-one tail.
    guard=8*(len(word.ops)+N+1)*(h+1)
    out_width=field.width
    count=len(field.cells)
    # Use separate space for the exact fractional lift and temporary magnitudes.
    field=map_tape(field,count,lambda _,z:(z[0]<<guard,z[1]<<guard),out_width+2*guard+4)
    ambient=n-row_bits
    stride=1<<ambient
    rows=1<<row_bits
    padded=(rows+stock-1)//stock*stock
    for _ in range((padded-rows)*stride):
        field.append((0,0))
    stack=Tape(field.width,field.trace)

    def visit(input_field, num_rows, start, span):
        columns,tail=divmod(span,N)
        for axis in range(start+span-tail,start+span):
            input_field=one_c(input_field,axis)
        if not columns:
            return input_field
        remaining=num_rows//W
        if not remaining or remaining*W!=num_rows:
            raise ValueError("native C word lacks independent complete rows")
        size=remaining*stride
        width,tr=input_field.width,input_field.trace
        regs=[Tape(width,tr) for _ in range(W+word.owned)]
        input_field.home()
        for i in range(num_rows):
            dest=regs[i%W]
            for _ in range(stride):
                dest.append(input_field.read())
        input_field.release()
        for private in regs[W:]:
            for _ in range(size):
                private.append((0,0))
        for op,reg,*args in word.ops:
            current=regs[reg]
            if op in ("add","sub"):
                s=1 if op=="add" else -1
                if reg==args[0]:
                    regs[reg]=map_tape(current,size,lambda _,z:pm(z,z,s))
                else:
                    other=regs[args[0]]
                    other.home()
                    regs[reg]=map_tape(current,size,lambda _,z:pm(z,other.read(),s))
                    other.home()
            elif op in ("half","clear","neg","i","unit"):
                def scalar(_,z):
                    if op=="half":
                        return exact_drop(z,1)
                    if op=="clear":
                        return 0,0
                    return turn(z,2 if op=="neg" else 1 if op=="i" else columns)
                regs[reg]=map_tape(current,size,scalar)
            elif op=="paid":
                # Suspend every nonchild owner on one shared physical stack.
                for j,old in enumerate(regs):
                    if j!=reg:
                        old.seek(size)
                        for _ in range(size):
                            stack.append(old.read_back())
                        old.release()
                        regs[j]=None
                regs[reg]=yield current,remaining,start+args[0]*columns,columns
                for j in reversed(range(len(regs))):
                    if j!=reg:
                        restored=Tape(width,tr)
                        for _ in range(size):
                            restored.append(stack.pop())
                        regs[j]=restored
            else:
                a=start+args[0]*columns
                last=start+args[-1]*columns
                mask=(1<<columns)-1
                if op=="cx":
                    edges=tuple((a+j,last+j) for j in range(columns))
                    regs[reg]=xor_bank(current,edges,ambient,p+guard)
                elif op=="x":
                    regs[reg]=reverse_blocks(reverse_blocks(current,1<<(a+columns)),1<<a)
                else:
                    def diagonal(i,z):
                        first=(i>>a)&mask
                        exp=first.bit_count() if op=="s" else 2*(first & (i>>last)).bit_count()
                        return turn(z,exp)
                    regs[reg]=map_tape(current,size,diagonal)
        out=Tape(width,tr)
        for reg in regs[:W]:
            reg.home()
        for i in range(num_rows):
            source=regs[i%W]
            for _ in range(stride):
                out.append(source.read())
        for reg in regs:
            reg.release()
        return out

    frames=[]
    cursor=visit(field,padded,0,h)
    response=None
    while True:
        try:
            child=cursor.send(response)
        except StopIteration as complete:
            if not frames:
                out=complete.value
                break
            response=complete.value
            cursor=frames.pop()
        else:
            frames.append(cursor)
            cursor=visit(*child)
            response=None
    if stack.cells:
        raise ValueError("unrestored native continuation")
    stack.release()
    out.home()
    final=Tape(out_width,out.trace)
    for _ in range(count):
        final.append(exact_drop(out.read(),guard-h))
    for _ in range((padded-rows)*stride):
        if out.read()!=(0,0):
            raise ArithmeticError("native productive endpoint changed a zero padded row")
    out.release()
    return route(final,reversed(schedule),n,p,xor_bank)


def unlimited_elementary(field,request):
    for axis in request.selected:
        field=single_c_numerator(field,axis)
    return field


class SourceC:
    def __init__(self,xor_bank=xor_literal):
        self.xor_bank=xor_bank

    def __call__(self,field,request):
        word=compile_within(request.input_fraction)
        if word is None:
            return unlimited_elementary(field,request)
        return run_word(field,request,word,self.xor_bank)


uniform_h=SelectedH(SourceC())
