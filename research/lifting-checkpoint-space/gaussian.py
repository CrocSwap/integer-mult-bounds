"""Small Boolean realization of the exact scaled C tensor; no fast tariff.

The immutable direct program deliberately overwrites scratch/carry bits, so
checkpoint reversal must restore information. Tekalign/Codex, Apache-2.0.
"""


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rotate(a,b,phase):
    return ((a,b),(-b,a),(-a,-b),(b,-a))[phase%4]


def compile_linear(n,axes,width,inverse=False):
    need(type(n) is type(width) is int and 1 <= n <= 5 and width >= 3, 'finite compiler domain')
    need(1 <= len(axes) <= n and len(set(axes)) == len(axes)
         and all(type(j) is int and 0 <= j < n for j in axes), 'active axes')
    count = 1 << n
    payload = 2*count*width
    scratch = 2*payload
    carry,p,aandb,pandc,total,bbit = range(scratch,scratch+6)
    size = scratch+6
    code = []

    def gate(op,dst,x=0,y=0):
        code.append((op,dst,x,y))

    def accumulate(dst,src,coefficient):
        if coefficient == 0:
            return
        magnitude = abs(coefficient)
        need(magnitude & (magnitude-1) == 0, 'power-two coefficient')
        shift = magnitude.bit_length()-1
        gate('set',carry,int(coefficient<0))
        for bit in range(width):
            if bit < shift:
                gate('set',bbit,0)
            else:
                gate('copy',bbit,src+bit-shift)
            if coefficient < 0:
                gate('not',bbit,bbit)
            # Keep both old operands until the carry is computed.
            gate('xor',p,dst+bit,bbit)
            gate('and',aandb,dst+bit,bbit)
            gate('and',pandc,p,carry)
            gate('xor',total,p,carry)
            gate('xor',carry,aandb,pandc)
            gate('copy',dst+bit,total)

    rank = len(axes)
    factor = rotate(2,0,rank//2) if rank%2==0 else rotate(1,1,rank//2)
    for y in range(count):
        for subset in range(1 << rank):
            delta = sum(1<<axis for i,axis in enumerate(axes) if subset>>i&1)
            x = y ^ delta
            cr,ci = rotate(*factor,-subset.bit_count())
            if inverse:
                ci = -ci
            yr,yi = payload+2*y*width,payload+(2*y+1)*width
            xr,xi = 2*x*width,(2*x+1)*width
            accumulate(yr,xr,cr)
            accumulate(yr,xi,-ci)
            accumulate(yi,xr,ci)
            accumulate(yi,xi,cr)
    return code,size,range(payload,2*payload)


def encode_input(values,width,size):
    need(2*len(values)*width <= size, 'input capacity')
    result = [0]*size
    low,high = -(1 << (width-1)),1 << (width-1)
    for i,value in enumerate(t for z in values for t in z):
        need(type(value) is int and low <= value < high, 'signed input headroom')
        for bit in range(width):
            result[i*width+bit] = (value>>bit)&1
    return result


def decode_output(bits,width):
    need(len(bits)%(2*width) == 0, 'output word shape')
    result = []
    for start in range(0,len(bits),width):
        value = sum(bits[start+i]<<i for i in range(width))
        if value >> (width-1):
            value -= 1<<width
        result.append(value)
    return list(zip(result[::2],result[1::2]))


def encode_output(values,width):
    return encode_input(values,width,2*len(values)*width)
