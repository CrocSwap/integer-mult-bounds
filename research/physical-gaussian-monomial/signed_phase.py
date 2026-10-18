"""Fixed-width signed Gaussian phases on literal sequential tapes."""
import phase_sources
phase_sources.activate()
from cardinal_counts import Count
from compact_counts import copy_bits
from session import borrowed_tape
from stream import Counter
from words import BLANK,need


class SignedHeadroomError(ValueError):
    pass


MOVES = (((0,False),(1,False)),((1,True),(0,False)),
         ((0,True),(1,True)),((1,False),(0,True)))


def read_component(source,target,width):
    """Copy the exact width; report the most-negative signed bit pattern."""
    remaining = Counter(width)
    lower_zero,sign = True,0
    try:
        while not remaining.finished:
            bit = source.read()
            need(bit in (0,1), "complete signed binary component")
            target.append(bit)
            source.step(1)
            remaining.decrement()
            if remaining.finished:
                sign = bit
            else:
                lower_zero = lower_zero and bit == 0
        target.rewind()
        return bool(sign and lower_zero)
    finally:
        remaining.close()


def emit_component(source,target,width,negative):
    source.rewind()
    if not negative:
        copy_bits(source,target,width)
    else:
        remaining,carry = Counter(width),1
        try:
            while not remaining.finished:
                bit = source.read()
                need(bit in (0,1), "signed component digit")
                value = (1-bit)+carry
                target.append(value&1)
                carry = value>>1
                source.step(1)
                remaining.decrement()
        finally:
            remaining.close()
    need(source.read() == BLANK, "complete fixed-width component emission")


def pair(source,target,width,phase,real,imag):
    need(type(phase) is int and 0 <= phase < 4, "finite Gaussian unit phase")
    try:
        minima = (read_component(source,real,width),read_component(source,imag,width))
        if any(negative and minima[which] for which,negative in MOVES[phase]):
            raise SignedHeadroomError("signed Gaussian phase headroom")
        buffers = (real,imag)
        for which,negative in MOVES[phase]:
            emit_component(buffers[which],target,width,negative)
    finally:
        # Retain the two active leases across coefficient fields.
        borrowed_tape(real).clear()
        borrowed_tape(imag).clear()


def scan(source,plan,recipe,columns,spacing,residue,width,coefficients,outer_rows,factory,inverse=False):
    output,real,imag = factory(),factory(),factory()
    rows = Counter(outer_rows)
    source.rewind()
    try:
        while not rows.finished:
            records,index = Counter(plan.records),Count.literal(0)
            try:
                while not records.finished:
                    state = plan.decode(index)
                    try:
                        phase = recipe.phase(state,columns,spacing,residue,inverse)
                    finally:
                        plan.close_state(state)
                    fields = Counter(coefficients)
                    try:
                        while not fields.finished:
                            pair(source,output,width,phase,real,imag)
                            fields.decrement()
                    finally:
                        fields.close()
                    index.increment()
                    records.decrement()
            finally:
                records.close()
                index.close()
            rows.decrement()
        need(source.read() == BLANK, "complete Gaussian phase packet")
        source.clear()
        output.rewind()
        return output
    except BaseException:
        output.clear()
        raise
    finally:
        real.clear()
        imag.clear()
        rows.close()
