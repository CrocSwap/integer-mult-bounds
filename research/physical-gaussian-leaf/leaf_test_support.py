"""Checker-only exact integers, complete packet labels and ownership snapshots."""
import leaf_sources
leaf_sources.activate()
from words import BLANK,need


def body(tape):
    tape = getattr(tape,"physical",tape)
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def encode(value,width):
    return bytes((value>>position)&1 for position in range(width))


def decode(raw,width):
    values = []
    for start in range(0,len(raw),width):
        digits = raw[start:start+width]
        need(len(digits) == width, "checker complete signed component")
        value = sum(bit<<position for position,bit in enumerate(digits))
        values.append(value-(1<<width) if digits[-1] else value)
    return values


def packet(values,width):
    return b"".join(encode(value,width) for value in values)


def c_values(a,b,inverse=False):
    ar,ai = a
    br,bi = b
    p = (ar+br,ai+bi)
    q = (ai-bi,br-ar) if inverse else (bi-ai,ar-br)
    numerators = (p[0]+q[0],p[1]+q[1],p[0]-q[0],p[1]-q[1])
    need(all(value%2 == 0 for value in numerators), "checker exact C grid")
    return tuple(value//2 for value in numerators)


def oracle(raw,fields,field,f,K,rho,width,coefficients,rows,inverse=False):
    values = decode(raw,width)
    records = 1<<sum(length for _name,length in fields)
    after = sum(length for name,length in fields[1+next(i for i,row in enumerate(fields) if row[0] == field):])
    for column in reversed(range(f)) if inverse else range(f):
        mask = 1<<(after+rho+column*K)
        for row in range(rows):
            for address in range(records):
                if address&mask:
                    continue
                for index in range(coefficients):
                    first = 2*((row*records+address)*coefficients+index)
                    second = 2*((row*records+(address|mask))*coefficients+index)
                    transformed = c_values(values[first:first+2],values[second:second+2],inverse)
                    need(all(-(1<<(width-1)) <= value < 1<<(width-1) for value in transformed), "checker C headroom")
                    values[first:first+2],values[second:second+2] = transformed[:2],transformed[2:]
    return packet(values,width)


def snapshot(values):
    return [(bytes(getattr(value.tape,"physical",value.tape).cells),value.tape.head) for value in values]


def closed_work(engine,include_output=False):
    tapes = (*engine.pool.tapes,engine.output) if include_output else engine.pool.tapes
    need(engine.closed and not engine.pool.live, "closed coefficient inventory")
    need(all(tape.head == 1 and all(bit == BLANK for bit in tape.cells) for tape in tapes),
         "erased coefficient scratch and local heads")
