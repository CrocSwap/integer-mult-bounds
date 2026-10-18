"""Exhaust small signed packets against every literal instruction prefix."""
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
from scalar_engine import ScalarEngine
from scalar_test_support import (POLICIES,TEMPLATES,body,closed_work,fill,packet,
                                 prefix_oracle,snapshot)
from session import erase_marker
from signed_linear import CoefficientDomainError
from words import need


def run():
    literals = tuple((*template,policy) for template in TEMPLATES for policy in POLICIES)
    engine = ScalarEngine(literals)
    width,count = Count.literal(3),Count.literal(1)
    left,right = Tape(),Tape()
    saved = snapshot((width,count))
    digest,counts = sha256(),dict(valid=0,inexact=0,headroom=0)
    for literal in literals:
        engine.select(literal)
        recipe = engine.recipe
        for x in range(-4,4):
            for y in range(-4,4) if recipe.kind == "add" else (0,):
                xs = (x,-x if x != -4 else x)
                ys = (y,-y if y != -4 else y)
                left_raw,right_raw = packet(xs,3),packet(ys,3)
                expected,error = [],None
                for a,b in zip(xs,ys):
                    value,error = prefix_oracle(recipe,a,b,3)
                    if error is not None:
                        break
                    expected.append(value)
                fill(left,left_raw)
                fill(right,right_raw)
                with no_decode():
                    try:
                        returned = engine.run(left,right if recipe.kind == "add" else None,width,count)
                    except CoefficientDomainError as failure:
                        need(error is not None and error in str(failure), "exact literal scalar prefix rejection")
                        closed_work(engine,True)
                    else:
                        need(error is None and body(returned) == packet(expected,3), "exact literal scalar prefix endpoint")
                        closed_work(engine)
                        returned.clear()
                        erase_marker(returned)
                need(body(left) == left_raw and body(right) == right_raw and left.head == right.head == 1 and
                     snapshot((width,count)) == saved, "prefix guard preserves complete borrowed data")
                counts[error or "valid"] += 1
                digest.update(json.dumps((literal,x,y,expected,error),separators=(",",":")).encode())
    left.clear()
    right.clear()
    width.close()
    count.close()
    return dict(counts=counts,cases=sum(counts.values()),peak=engine.pool.peak,sha256=digest.hexdigest(),
                scope="All signed3-bit component pairs for ADD and all3-bit SCALE targets across31literals/3policies; compare every recipe prefix")


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
    print("PASS_PHYSICAL_SCALAR_PREFIXES")
