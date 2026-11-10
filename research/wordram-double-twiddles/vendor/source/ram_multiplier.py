"""Assemble and execute one fixed-size tcslib-ISA multiplication program.
Program generation depends only on public lengths and fixed field constants.
Every runtime instruction, including table synthesis and clearing, is interpreted.
"""
from dataclasses import dataclass
from ram.wordram_kernel import Builder, run, SCRATCH, ZERO, TEMP
from ntt.exact_ntt import validate_root, evaluate

P, BASE, GENERATOR = 65537, 16, 3

@dataclass
class Plan:
    program: list
    left: list
    right: list
    output: list
    temporaries: set
    butterflies: int
    modular_products: int
    n: int
    fused: bool


def build_multiplier(s, t, fused=True):
    if not (1 <= s <= 256 and 1 <= t <= 256):
        raise ValueError('each operand must have 1..256 hexadecimal digits')
    n = 1 << (s+t-2).bit_length()
    omega = pow(GENERATOR, (P-1)//n, P)
    validate_root(P, n, omega)
    b = Builder(); b.setup()
    left, right = list(range(1000,1000+s)), list(range(2000,2000+t))
    outputs = list(range(3000,3000+n+1))
    fresh_id, temporaries, constants = 10000, set(), {}
    butterflies = modular_products = 0
    def fresh():
        nonlocal fresh_id
        x = fresh_id; fresh_id += 1; temporaries.add(x)
        return x
    def const(value):
        if value not in constants:
            addr=fresh(); b.literal(addr,value); constants[value]=addr
        return constants[value]
    def transform(cells, inverse=False):
        nonlocal butterflies,modular_products
        widthbits = n.bit_length()-1
        perm = [int(format(i,'0'+str(widthbits)+'b')[::-1],2) if widthbits else 0 for i in range(n)]
        a=[]
        for i in perm:
            dst=fresh(); b.copy(dst,cells[i] if i<len(cells) else const(0));a.append(dst)
        root=pow(omega,P-2,P) if inverse else omega
        width=2
        while width<=n:
            rootstep=pow(root,n//width,P)
            for lo in range(0,n,width):
                w=1
                for j in range(lo,lo+width//2):
                    plus,minus=fresh(),fresh()
                    b.butterfly(a[j],a[j+width//2],const(w),plus,minus,fused=fused)
                    a[j],a[j+width//2]=plus,minus
                    w=w*rootstep%P
                    butterflies+=1;modular_products+=1 if fused else 2
            width*=2
        if inverse:
            invn=const(pow(n,P-2,P));scaled=[]
            for src in a:
                dst=fresh();b.mul(src,invn,dst);scaled.append(dst);modular_products+=1
            a=scaled
        return a
    aa,bb=transform(left),transform(right)
    products=[]
    for x,y in zip(aa,bb):
        dst=fresh();b.mul(x,y,dst);products.append(dst);modular_products+=1
    coeff=transform(products,True)
    # Restore quotient/remainder division by 16 using only allowed instructions.
    # Bounds: coefficient <= 57600, incoming carry <=3840, total <=61440.
    carry=const(0)
    for i,c in enumerate(coeff):
        total,quotient=fresh(),fresh()
        b.emit('add',total,c,carry);b.copy(quotient,const(0))
        for bit in reversed(range(12)):
            threshold,weight=const(BASE*(1<<bit)),const(1<<bit)
            b.emit('sub',TEMP,total,threshold)
            b.emit('bltz',TEMP,len(b.code)+3)
            b.emit('add',total,TEMP,ZERO)
            b.emit('add',quotient,quotient,weight)
        b.copy(outputs[i],total);carry=quotient
    b.copy(outputs[n],carry)
    # Clear every owned intermediate, table cell and constant; leave operands.
    for addr in sorted(temporaries):b.emit('sub',addr,addr,addr)
    b.cleanup();b.accept()
    return Plan(b.program(),left,right,outputs,temporaries,butterflies,modular_products,n,fused)


def execute(plan,a,b,dirty=False):
    if len(a)!=len(plan.left) or len(b)!=len(plan.right) or any(type(x)is not int or not 0<=x<BASE for x in a+b):
        raise ValueError('operand digits violate fixed program ABI')
    memory={**dict(zip(plan.left,a)),**dict(zip(plan.right,b)),-7:123456,777777:987654}
    if dirty:
        memory.update({x:0xDEADBEEF for x in plan.temporaries|SCRATCH|set(plan.output)})
    initial=memory.copy();result=run(plan.program,memory)
    assert result is not None and result.accepted
    digits=[result.memory[x] for x in plan.output]
    assert all(0<=x<BASE for x in digits)
    assert evaluate(digits,BASE)==evaluate(a,BASE)*evaluate(b,BASE)
    assert all(result.memory.get(x,0)==0 for x in plan.temporaries|SCRATCH)
    allowed=plan.temporaries|SCRATCH|set(plan.output)
    assert result.writes<=allowed
    assert all(result.memory.get(x,0)==v for x,v in initial.items() if x not in allowed)
    return result,digits
