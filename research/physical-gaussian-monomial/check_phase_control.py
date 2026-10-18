"""Encoded repeated phases against direct strict-upper integer polynomials."""
from hashlib import sha256
from pathlib import Path
from random import Random
import json
import sys
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import phase_sources
_native,_compact,reference = phase_sources.activate()
from cardinal_counts import Count
from check_support import no_decode
from gaussian_test_support import GENERIC,oracle_phase,selected_recipe,snapshot
from phase_recipe import Recipe
from scratch_pool import ScratchPool
from session import sealed_constructors
from words import need


def run():
    rng,digest = Random(30552422),sha256()
    cases,peak,nonzero = 0,0,0
    for literal in (selected_recipe(),GENERIC):
        vectors = tuple("v"+str(i) for i in range(len(literal["matrix_rows"])))
        recipe = Recipe(literal,vectors)
        scenarios = []
        if len(vectors) == 9:
            scenarios.extend((1,1,0,{name:(address>>i)&1 for i,name in enumerate(vectors)}) for address in range(512))
        for f,K,rho in ((2,1,0),(3,3,2),(4,2,1),(5,2,0),(65,3,2)):
            for _ in range(8 if f < 65 else 2):
                scenarios.append((f,K,rho,{name:rng.getrandbits(f*K) for name in vectors}))
        pool = ScratchPool(256)
        for f,K,rho,raw in scenarios:
            parameters = [Count.literal(value) for value in (f,K,rho)]
            state = {name:Count.literal(value) for name,value in raw.items()}
            saved = snapshot((*parameters,*state.values()))
            expected = oracle_phase(literal,raw,vectors,f,K,rho)
            def forbidden(*_args,**_kwargs):
                raise ValueError("indexed phase oracle used by encoded arithmetic")
            with no_decode(),sealed_constructors(),pool.install(), \
                    patch.multiple(reference,tensor_phase=forbidden,column_phase=forbidden,columns=forbidden):
                actual = recipe.phase(state,*parameters)
                inverse = recipe.phase(state,*parameters,True)
                need((actual,inverse) == (expected,(-expected)%4), "encoded phase and recovered-address inverse")
                pool.empty()
            need(snapshot((*parameters,*state.values())) == saved, "phase controls preserve encoded borrows")
            digest.update(json.dumps((f,K,rho,raw,actual),sort_keys=True,separators=(",",":")).encode())
            nonzero += int(actual != 0)
            cases += 1
            for value in (*parameters,*state.values()):
                value.close()
        peak = max(peak,pool.peak)
    need(nonzero > 0, "nontrivial encoded phases")
    return dict(cases=cases,selected_single_columns=512,maximum_columns=65,nonzero=nonzero,peak=peak,
                sha256=digest.hexdigest(),scope="Exact encoded phase arithmetic; source-algebra and selected recipe remain credited predecessors")


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
    print("PASS_ENCODED_GAUSSIAN_PHASE_CONTROL")
