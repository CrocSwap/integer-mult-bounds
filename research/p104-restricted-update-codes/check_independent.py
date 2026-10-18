"""Replay the independent census and compare complete fiber counts."""
from pathlib import Path
import json
import types

ROOT=Path(__file__).resolve().parent

def load(name):
    path=ROOT/(name+".py")
    module=types.ModuleType(name)
    module.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),"exec",optimize=0),module.__dict__)
    return module

independent=load("independent")
verify=load("verify")

def main():
    actual=independent.run(include_rank3=True)
    expected=json.loads((ROOT/"INDEPENDENT-RESULT.json").read_text())
    verify.need(verify.typed_equal(actual,expected),"independent receipt")
    primary=json.loads((ROOT/"RESULT.json").read_text())
    second=actual["raw_boxes"]+[actual["rank3_independent_character_quotient"]]
    for first, other in zip(primary["censuses"],second,strict=True):
        factor=other["inputs"]//first["cosets"]
        verify.need(other["inputs"]==factor*first["cosets"],"domain multiplicity")
        for coordinate in first["coordinates"]:
            j=coordinate["coordinate"]
            for step in coordinate["steps"]:
                s=str(step["step"])
                verify.need(step["states"]==other["counts_by_step_all_coordinates"][s][j],"independent state count")
                hist={str(int(k)*factor):v for k,v in step["fiber_histogram"].items()}
                verify.need(hist==other["fiber_histograms"][s][j],"independent complete fibers")
    print("PASS_P104_INDEPENDENT_RESTRICTED_CODES_ALL_RANKS_1_TO_3")

if __name__=="__main__":main()
