"""Encoded fixed-width shifts, logical zeros and owned scalar word updates."""
import scalar_sources
scalar_sources.activate()
from compact_counts import copy_bits
from session import borrowed_tape
from signed_linear import CoefficientDomainError,linear_word
from stream import Counter
from words import BLANK,need


class ScalarContractError(CoefficientDomainError):
    pass


def zero_word(tape,width):
    tape.rewind()
    remaining = Counter(width)
    try:
        while not remaining.finished:
            tape.write(0)
            tape.step(1)
            remaining.decrement()
        need(tape.read() == BLANK, "complete scalar logical-zero extent")
    finally:
        remaining.close()
        tape.rewind()


def require_zero(tape,width):
    tape.rewind()
    remaining = Counter(width)
    try:
        while not remaining.finished:
            if tape.read() != 0:
                raise ScalarContractError("scalar logical scratch is not zero")
            tape.step(1)
            remaining.decrement()
        need(tape.read() == BLANK, "complete scalar zero word")
    finally:
        remaining.close()
        tape.rewind()


def shifted(source,target,width,double):
    source.rewind()
    remaining = Counter(width)
    first,previous,last = True,0,0
    try:
        if double:
            target.append(0)
        while not remaining.finished:
            bit = source.read()
            need(bit in (0,1), "complete scalar shift input")
            source.step(1)
            remaining.decrement()
            if double:
                if remaining.finished:
                    if bit != previous:
                        raise CoefficientDomainError("signed scalar DOUBLE headroom")
                else:
                    target.append(bit)
            elif first:
                if bit:
                    raise CoefficientDomainError("inexact scalar HALF")
            else:
                target.append(bit)
            first,previous,last = False,bit,bit
        need(source.read() == BLANK, "complete fixed scalar shift width")
        if not double:
            target.append(last)
    finally:
        remaining.close()
        source.rewind()


def instruction(registers,operation,width,work,zero):
    kind,port = operation[:2]
    target = registers[port]
    if kind == "clear":
        zero_word(target,width)
        return
    try:
        if kind == "add":
            linear_word((target,registers[operation[2]]),work,width,(1,operation[3]))
        elif kind == "copy":
            require_zero(target,width)
            source = registers[operation[2]]
            source.rewind()
            copy_bits(source,work,width)
            need(source.read() == BLANK, "complete scalar COPY source")
            source.rewind()
        elif kind == "neg":
            linear_word((zero,target),work,width,(1,-1))
        else:
            need(kind in ("double","half"), "compiled scalar shift kind")
            shifted(target,work,width,kind == "double")
        work.rewind()
        borrowed_tape(target).clear()
        copy_bits(work,target,width)
        need(work.read() == BLANK, "complete scalar unit result")
        target.rewind()
    finally:
        borrowed_tape(work).clear()


def restored_source(local,borrowed,width):
    """Compare only the current borrowed component, then resume its cursor."""
    back = Counter(width)
    try:
        while not back.finished:
            borrowed.step(-1)
            back.decrement()
    finally:
        back.close()
    local.rewind()
    forward = Counter(width)
    try:
        while not forward.finished:
            if local.read() != borrowed.read():
                raise ScalarContractError("scalar source component not restored")
            local.step(1)
            borrowed.step(1)
            forward.decrement()
        need(local.read() == BLANK, "complete restored scalar source")
    finally:
        forward.close()
        local.rewind()
