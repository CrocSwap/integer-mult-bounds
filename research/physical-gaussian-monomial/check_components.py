"""Exhaust signed component phases against integer rotation matrices."""
from hashlib import sha256
from pathlib import Path
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import phase_sources
phase_sources.activate()
from cardinal_counts import Count
from check_support import no_decode
from records import Tape
from scratch_pool import ScratchPool
from session import sealed_constructors
from signed_phase import SignedHeadroomError,pair
from words import BLANK,need


ROTATIONS = ((1,0,0,1),(0,-1,1,0),(-1,0,0,-1),(0,1,-1,0))


def encode(value,bits):
    return bytes((value>>position)&1 for position in range(bits))


def body(tape):
    tape = getattr(tape,"physical",tape)
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def run():
    source,output,pool = Tape(),Tape(),ScratchPool(64)
    digest,valid,rejected = sha256(),0,0
    for bits in (2,3,4):
        width = Count.literal(bits)
        original_width = bytes(width.tape.cells)
        limit = 1<<(bits-1)
        with no_decode(),sealed_constructors(),pool.install():
            real,imag = pool.acquire(),pool.acquire()
            try:
                for phase,(a,b,c,d) in enumerate(ROTATIONS):
                    for x in range(-limit,limit):
                        for y in range(-limit,limit):
                            initial = encode(x,bits)+encode(y,bits)
                            for bit in initial:
                                source.append(bit)
                            source.rewind()
                            expected = (a*x+b*y,c*x+d*y)
                            fits = all(-limit <= value < limit for value in expected)
                            try:
                                pair(source,output,width,phase,real,imag)
                            except SignedHeadroomError:
                                need(not fits and not body(output), "reject signed overflow before pair emission")
                                rejected += 1
                            else:
                                need(fits and body(output) == b"".join(encode(value,bits) for value in expected),
                                     "exact fixed-width signed Gaussian phase")
                                valid += 1
                            need(body(source) == initial and not body(real) and not body(imag) and
                                 real.head == imag.head == 1, "source and two reusable component roles")
                            need(bytes(width.tape.cells) == original_width and width.tape.head == 1,
                                 "borrowed signed width preserved")
                            digest.update(json.dumps((bits,phase,x,y,expected,fits),separators=(",",":")).encode())
                            source.clear()
                            output.clear()
            finally:
                real.clear()
                imag.clear()
            pool.empty()
        width.close()
    need((valid,rejected) == (1235,109), "complete small signed-domain census")
    return dict(cases=valid+rejected,valid=valid,rejected=rejected,peak=pool.peak,
                sha256=digest.hexdigest(),scope="All signed pairs at widths2,3,4 and four phases; integer semantics, not byte roundtrip")


if __name__ == "__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
    print("PASS_PHYSICAL_SIGNED_COMPONENTS")
