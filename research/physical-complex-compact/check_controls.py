"""Compare encoded control states with the pinned, independently indexed oracle."""
from hashlib import sha256
from pathlib import Path
from random import Random
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import native_sources
_source, reference = native_sources.activate()
from cardinal_counts import Count
from check_support import no_decode
from compact_control import Control
from compact_layout import Layout
from scratch_pool import ScratchPool
from session import sealed_constructors
from words import RIGHT, need


def inspect_count(value):
    """Checker observation only; no result enters the encoded implementation."""
    tape = getattr(value.tape,"physical",value.tape)
    result = 0
    for position,bit in enumerate(tape.cells[1:]):
        if bit == RIGHT:
            return result
        need(bit in (0,1), "checker Count alphabet")
        result |= bit << position
    raise ValueError("checker Count has no delimiter")


def observe(state):
    return {name:inspect_count(value) for name,value in state.items()}


def run():
    rng, digest = Random(22502899), sha256()
    totals = dict(states=0, offsets=0, good=0, bad=0, crossing_witness=False, peak=0)
    for n,K,G,rho in ((1,1,1,0),(1,5,1,0),(2,2,1,1),(2,7,2,6),(3,9,3,8)):
        for late,constant in ((False,False),(True,False),(False,True)):
            vectors = (("y",(n+1)*K),("x",(n+1)*K)) if late else (("x",(n+1)*K),("y",(n+1)*K))
            fields = (("u",n*G),("gap",0),("t",n*G))+vectors+(("b",n*G),("tail",0))
            names = tuple(name for name,_width in fields)
            ref_layout = reference.Layout(fields,3)
            ref_word = reference.Compact(n,K,G,rho,None if constant else "x","y",late)
            raw_states = [{name:rng.randrange(1<<width) for name,width in fields} for _ in range(8)]
            raw_states += [{name:0 for name,_ in fields}, {name:(1<<width)-1 for name,width in fields}]
            if (n,K,G,rho,late,constant) == (2,2,1,1,False,False):
                raw_states += [dict(u=0,gap=0,t=1,x=2,y=2,b=0,tail=0)]
            inputs = [Count.literal(value) for value in (n,K,G,rho,3)]
            widths = tuple(Count.literal(width) for _name,width in fields)
            pool = ScratchPool(256)
            with no_decode(), sealed_constructors(), pool.install():
                plan = Layout(names,widths,inputs[-1])
                word = Control(*inputs[:4],None if constant else "x","y",late)
                word.validate(plan)
                need(word.operations == ref_word.operations(), "unchanged finite chronology")
                for raw in raw_states:
                    state = {name:Count.literal(value) for name,value in raw.items()}
                    try:
                        address = plan.encode(state)
                        recovered = plan.decode(address)
                        need(inspect_count(address) == ref_layout.encode(raw) and observe(recovered) == raw,
                             "encoded complete field order")
                        plan.close_state(recovered)
                        address.close()
                        bad = word.bad(state)
                        need(bad == ref_word.bad(raw), "encoded original sufficient guard")
                        totals["bad" if bad else "good"] += 1
                        for operation in word.operations:
                            if operation[0] != "rotate":
                                continue
                            value = word.offset(state,operation,plan)
                            expected = ref_word.offset(raw,operation) % (1<<ref_layout.width(operation[1]))
                            need(inspect_count(value) == expected, "encoded signed modular offset")
                            value.close()
                            totals["offsets"] += 1
                        word.execute_state(state,plan)
                        raw_result = ref_word.execute(raw,ref_layout)
                        need(observe(state) == raw_result, "encoded chronological raw word")
                        need(word.bad(state) == bad, "raw word preserves exceptional domain")
                        if raw.get("t") == 1 and (n,K,G,rho,late,constant) == (2,2,1,1,False,False) and raw.get("x") == raw.get("y") == 2:
                            need(inspect_count(state["t"]) == 3, "repair crosses a fixed dirty-t slice")
                            totals["crossing_witness"] = True
                        word.execute_state(state,plan,True)
                        need(observe(state) == raw, "encoded inverse uses current controls")
                        word.ideal_state(state,True)
                        ideal = ref_word.ideal(raw,True)
                        need(observe(state) == ideal, "complete selected-bit ideal")
                        digest.update(json.dumps((raw,raw_result,ideal,bad),sort_keys=True,separators=(",",":")).encode())
                        totals["states"] += 1
                    finally:
                        plan.close_state(state)
                plan.close()
                pool.empty()
            totals["peak"] = max(totals["peak"],pool.peak)
            need(all(value.tape.head == 1 for value in (*inputs,*widths)), "borrowed descriptors return at origin")
            for value in (*inputs,*widths):
                value.close()
    need(totals["good"] > 0 and totals["bad"] > 0 and totals["crossing_witness"], "both guard regimes and crossing control")
    totals["state_sha256"] = digest.hexdigest()
    return totals


if __name__ == "__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
    print("PASS_ENCODED_COMPACT_CONTROLS")
