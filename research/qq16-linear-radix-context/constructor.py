"""Construct the source Context with one fixed-radix quotient scan per digit.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Fixed-radix long division follows the retained Natural.divide_small method.
The loop interchange follows ToikY and Chris R's shared-radix work.
"""


def need(ok,message):
    if not ok:raise ValueError(message)


def divide_fixed(word,q):
    """q is a compiled constant. Only a remainder below q enters control."""
    word.msb()
    remainder=0
    while (symbol:=word.read())!=2:  # LEFT in the retained word alphabet.
        need(symbol in (0,1),'binary quotient input')
        remainder=2*remainder+symbol
        if remainder>=q:
            word.write(1);remainder-=q
        else:word.write(0)
        word.step(-1)
    word.step(1)
    return remainder


def build(ring,codes,Context,Count):
    """Return a genuine Context. The class factories are fixed source bindings."""
    q,d=codes.q,codes.dimension
    need(type(q) is int and q>=2 and type(d) is int and d>=1,'compiled context vocabulary')
    a=ring.arena;raw=ring.raw;protected=set(a.live)
    value=None;success=False
    try:
        power=a.copy(ring.modulus)
        value=Count()
        first=True;cap=None
        while raw.compare(power,ring.one)>0:
            need(divide_fixed(power,q)==0,'exact radix power')
            if first:
                cap=a.copy(power);first=False
            else:
                for _ in range(d*d):value.multiply_small(q)
        need(not first and raw.compare(power,ring.one)==0,'positive radix exponent')
        a.free(power)
        context=object.__new__(Context)
        context.ring,context.arena,context.raw=ring,a,raw
        context.codes=codes;context.q=q;context.dimension=d
        context.cap,context.highs=cap,value
        success=True
        return context
    finally:
        if not success:
            if value is not None:value.close()
            a.rollback(protected)
