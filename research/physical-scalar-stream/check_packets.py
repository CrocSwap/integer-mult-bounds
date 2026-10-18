"""Complete packets through every compiled literal and policy."""
from hashlib import sha256
from pathlib import Path
import json
import sys
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import scalar_sources
lower = scalar_sources.activate()
from cardinal_counts import Count
from check_support import no_decode
from compact_counts import append_bits
from records import Tape
from scalar_engine import ScalarEngine
from scalar_test_support import (POLICIES,TEMPLATES,body,closed_work,fill,packet,
                                 prefix_oracle,snapshot)
from session import erase_marker
from words import need


def forbidden(*_args,**_kwargs):
    raise ValueError("indexed recipe interpreter reached physical scalar execution")


def run():
    literals = tuple((*template,policy) for template in TEMPLATES for policy in POLICIES)
    engine = ScalarEngine(literals)
    width,count = Count.literal(84),Count.literal(7)
    left,right,middle = Tape(),Tape(),Tape()
    left_values = [(((index*31)%17)-8)*(1<<37) for index in range(14)]
    right_values = [(((index*7)%19)-9)*(1<<35) for index in range(14)]
    left_raw,right_raw = packet(left_values,84),packet(right_values,84)
    saved = snapshot((width,count))
    digest,cases = sha256(),0
    for literal in literals:
        engine.select(literal)
        recipe = engine.recipe
        expected = []
        for x,y in zip(left_values,right_values):
            value,error = prefix_oracle(recipe,x,y if recipe.kind == "add" else 0,84)
            need(error is None, "admitted complete scalar fixture")
            expected.append(value)
        fill(left,left_raw)
        fill(right,right_raw)
        with no_decode(),patch.multiple(lower,execute=forbidden,certify=forbidden,lower=forbidden):
            returned = engine.run(left,right if recipe.kind == "add" else None,width,count)
        need(body(returned) == packet(expected,84), "complete physical scalar packet endpoint")
        need(body(left) == left_raw and body(right) == right_raw and left.head == right.head == returned.head == 1 and
             snapshot((width,count)) == saved, "scalar packet borrowed inputs and descriptors")
        closed_work(engine)
        digest.update(json.dumps(literal,separators=(",",":")).encode()+body(returned))
        returned.clear()
        erase_marker(returned)
        cases += 1

    pipeline = []
    for policy in POLICIES:
        fill(left,left_raw)
        fill(right,right_raw)
        engine.select(("scale",-1,2,policy))
        with no_decode():
            returned = engine.run(left,None,width,count)
        append_bits(returned,middle)
        middle.rewind()
        returned.clear()
        erase_marker(returned)
        engine.select(("add",1,2,policy))
        with no_decode():
            returned = engine.run(middle,right,width,count)
        expected = packet([(y-x)//2 for x,y in zip(left_values,right_values)],84)
        need(body(returned) == expected and body(left) == left_raw and body(right) == right_raw,
             "literal forward109/110 two-macro packet composition")
        closed_work(engine)
        pipeline.append(sha256(expected).hexdigest())
        returned.clear()
        erase_marker(returned)
        middle.clear()
    for tape in (left,right,middle):
        tape.clear()
    width.close()
    count.close()
    return dict(literal_templates=31,policy_cases=cases,component_bits=84,gaussians=7,peak=engine.pool.peak,
                sha256=digest.hexdigest(),event109_110_sha256=pipeline,
                scope="Complete aligned packets for31literal templates and3policies; literal109/110 composition, not reconstructed632-input prelude values")


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
    print("PASS_PHYSICAL_SCALAR_PACKETS")
