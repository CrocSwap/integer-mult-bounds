"""Exact signed HALF/DOUBLE transducers, including wider-word boundaries."""
from hashlib import sha256
from pathlib import Path
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import scalar_sources
scalar_sources.activate()
from cardinal_counts import Count
from check_support import no_decode
from records import Tape
from scalar_test_support import body,encode,snapshot
from scalar_words import shifted
from scratch_pool import ScratchPool
from session import sealed_constructors
from signed_linear import CoefficientDomainError
from words import need


def run():
    source,output,pool = Tape(),Tape(),ScratchPool(32)
    counts,digest = dict(valid=0,inexact=0,headroom=0),sha256()
    for bits in (2,3,4,8,17,65):
        width = Count.literal(bits)
        saved = snapshot((width,))
        limit = 1<<(bits-1)
        values = range(-limit,limit) if bits <= 8 else (-limit,-limit+1,-limit//2-1,-limit//2,-1,0,1,limit//2-1,limit//2,limit-2,limit-1)
        with no_decode(),sealed_constructors(),pool.install():
            for value in values:
                raw = encode(value,bits)
                for bit in raw:
                    source.append(bit)
                source.rewind()
                for double in (False,True):
                    expected = 2*value if double else value//2
                    category = "inexact" if not double and value%2 else "headroom" if not -limit <= expected < limit else "valid"
                    try:
                        shifted(source,output,width,double)
                    except CoefficientDomainError as error:
                        need(category != "valid" and category in str(error), "exact signed shift rejection")
                    else:
                        need(category == "valid" and body(output) == encode(expected,bits), "exact signed shift value")
                    need(body(source) == raw and source.head == 1 and snapshot((width,)) == saved,
                         "signed shift preserves borrowed word and width")
                    counts[category] += 1
                    digest.update(json.dumps((bits,value,double,category,expected),separators=(",",":")).encode())
                    output.clear()
                    pool.empty()
                source.clear()
        width.close()
    return dict(counts=counts,peak=pool.peak,sha256=digest.hexdigest(),scope="Exhaust widths2/3/4/8 and17/65 signed boundaries; exact HALF and final DOUBLE fit")


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
    print("PASS_PHYSICAL_SCALAR_SHIFTS")
