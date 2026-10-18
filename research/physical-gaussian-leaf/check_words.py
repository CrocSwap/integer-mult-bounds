"""Exact integer oracles for the signed finite-carry component transducer."""
from hashlib import sha256
from itertools import product
from pathlib import Path
from random import Random
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import leaf_sources
leaf_sources.activate()
from cardinal_counts import Count
from check_support import no_decode
from records import Tape
from scratch_pool import ScratchPool
from session import sealed_constructors
from signed_linear import CoefficientDomainError,ROWS,linear_word
from words import BLANK,need


def encode(value,width):
    return bytes((value>>index)&1 for index in range(width))


def body(tape):
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def c_numerators(values):
    ar,ai,br,bi = values
    p_real,p_imag = ar+br,ai+bi
    q_real,q_imag = bi-ai,ar-br
    return p_real+q_real,p_imag+q_imag,p_real-q_real,p_imag-q_imag


def run():
    sources,output,pool = tuple(Tape() for _ in range(4)),Tape(),ScratchPool(32)
    digest,rng = sha256(),Random(30872327)
    counts = dict(valid=0,inexact=0,overflow=0,negative_numerators=0)
    for bits in (2,3,17,65):
        width = Count.literal(bits)
        saved = (bytes(width.tape.cells),width.tape.head)
        limit = 1<<(bits-1)
        if bits <= 3:
            tuples = product(range(-limit,limit),repeat=4)
        else:
            edge = (-limit,-limit+1,-1,0,1,limit-2,limit-1)
            tuples = list(product(edge,repeat=4))
            tuples.extend(tuple(rng.randrange(-limit,limit) for _ in range(4)) for _ in range(128))
        with no_decode(),sealed_constructors(),pool.install():
            for values in tuples:
                raw = tuple(encode(value,bits) for value in values)
                for source,word in zip(sources,raw):
                    for bit in word:
                        source.append(bit)
                    source.rewind()
                numerators = c_numerators(values)
                need(len(ROWS) == 4, "four C output components")
                for signs,numerator in zip(ROWS,numerators):
                    expected = numerator//2
                    category = "inexact" if numerator%2 else "overflow" if not -limit <= expected < limit else "valid"
                    try:
                        linear_word(sources,output,width,signs,True)
                    except CoefficientDomainError as error:
                        need(category != "valid" and
                             (("inexact" in str(error)) == (category == "inexact")), "exact C component rejection")
                    else:
                        need(category == "valid" and body(output) == encode(expected,bits), "exact C component value")
                    need(tuple(body(source) for source in sources) == raw and
                         all(source.head == 1 for source in sources), "C word preserves component inputs")
                    counts[category] += 1
                    counts["negative_numerators"] += int(numerator < 0)
                    digest.update(json.dumps((bits,values,signs,category,expected),separators=(",",":")).encode())
                    output.clear()
                    pool.empty()
                for source in sources:
                    source.clear()
            need((bytes(width.tape.cells),width.tape.head) == saved, "word width borrow preserved")
        width.close()
    return dict(counts=counts,widths=[2,3,17,65],peak=pool.peak,sha256=digest.hexdigest(),
                scope="Exhaust all four-input signed words at widths2/3; boundary products and deterministic samples at17/65; exact parity and final-fit guards")


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
    print("PASS_FUSED_GAUSSIAN_WORDS")
