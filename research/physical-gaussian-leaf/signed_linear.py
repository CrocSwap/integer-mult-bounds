"""Finite-carry exact C components and signed sums on encoded-width words."""
import leaf_sources
leaf_sources.activate()
from compact_counts import copy_bits
from session import borrowed_tape
from stream import Counter
from words import BLANK,need

ROWS = ((1,-1,1,1),(1,1,-1,1),(1,1,1,-1),(-1,1,1,1))


class CoefficientDomainError(ValueError):
    pass


def transition(carry,bits,signs):
    value = carry+sum(sign*bit for sign,bit in zip(signs,bits))
    return value%2,value//2


def linear_word(sources,target,width,signs,halve=False):
    """Append an exact signed word; preserve the fixed input component tapes."""
    need(type(sources) is tuple and type(signs) is tuple and type(halve) is bool and
         ((halve and len(sources) == 4 and signs in ROWS) or
          (not halve and len(sources) == 2 and signs in ((1,1),(1,-1)))),
         "compiled finite Gaussian coefficient operation")
    remaining = Counter(width)
    carry,first,output_sign = 0,True,0
    sign_bits = (0,)*len(sources)
    for source in sources:
        source.rewind()
    try:
        need(not remaining.finished, "positive signed component width")
        while not remaining.finished:
            bits = tuple(source.read() for source in sources)
            need(all(bit in (0,1) for bit in bits), "complete signed coefficient inputs")
            for source in sources:
                source.step(1)
            digit,carry = transition(carry,bits,signs)
            need(-1 <= carry <= 2, "finite signed carry state")
            if halve and first:
                if digit:
                    raise CoefficientDomainError("inexact Gaussian halving")
            else:
                target.append(digit)
                output_sign = digit
            first = False
            sign_bits = bits
            remaining.decrement()
        need(all(source.read() == BLANK for source in sources), "exact fixed component widths")
        for extension in range(2 if halve else 1):
            digit,carry = transition(carry,sign_bits,signs)
            if halve and extension == 0:
                target.append(digit)
                output_sign = digit
            elif digit != output_sign:
                raise CoefficientDomainError("signed Gaussian result headroom")
    finally:
        remaining.close()
        for source in sources:
            source.rewind()


def c_pair(left,right,out_left,out_right,width,buffers,inverse=False):
    """Consume two complete Gaussian fields using four reusable component roles."""
    need(type(buffers) is tuple and len(buffers) == 4 and type(inverse) is bool,
         "fixed C component roles and direction")
    try:
        for source,pair in ((left,buffers[:2]),(right,buffers[2:])):
            for buffer in pair:
                copy_bits(source,buffer,width)
                buffer.rewind()
        rows = ROWS[2:]+ROWS[:2] if inverse else ROWS
        for signs,target in zip(rows,(out_left,out_left,out_right,out_right)):
            linear_word(buffers,target,width,signs,True)
    finally:
        for buffer in buffers:
            borrowed_tape(buffer).clear()


def add_component(left,right,target,width,buffers,subtract=False):
    need(type(buffers) is tuple and len(buffers) == 2 and type(subtract) is bool,
         "fixed signed-add component roles and direction")
    try:
        for source,buffer in zip((left,right),buffers):
            copy_bits(source,buffer,width)
            buffer.rewind()
        linear_word(buffers,target,width,(1,-1) if subtract else (1,1))
    finally:
        for buffer in buffers:
            borrowed_tape(buffer).clear()
