"""Source, repair, sorting and protected-output failure controls."""
from pathlib import Path
import json
import sys
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import native_sources


def rejected(action,message):
    try:
        action()
    except ValueError as error:
        if message not in str(error):
            raise ValueError("wrong rejection boundary: "+str(error)) from error
    else:
        raise ValueError("invalid source or semantics accepted: "+message)


def run():
    with patch.dict(sys.modules,{"streams":object()}):
        rejected(native_sources.activate,"cold compact/ordinary namespace")
    for name in ("pr2899","pr2250"):
        with patch.dict(native_sources.ARCHIVES,{name:"0"*64}):
            rejected(native_sources.activate,"immutable source archive")
    native_sources.activate()
    from check_payload import one_case,body
    from cardinal_counts import Count
    from compact_control import Control
    import compact_engine
    import compact_streams
    from records import Tape
    from session import erase_marker,sealed_constructors
    from words import need
    def fixture():
        return one_case(constant=True,omit_source=True,n=1,K=2,G=1,rho=0,outer=1,record_bits=1)
    with patch.object(compact_engine,"repair",lambda source,*_args:source):
        rejected(fixture,"complete compact endpoint")
    original = Control.execute_state
    def omit_inverse(control,state,plan,inverse=False):
        if not inverse:
            return original(control,state,plan,inverse)
    with patch.object(Control,"execute_state",omit_inverse):
        rejected(fixture,"complete compact endpoint")
    original_bit = compact_streams.bit_at
    with patch.object(compact_streams,"bit_at",lambda key,position:1-original_bit(key,position)):
        rejected(fixture,"sorted exceptional destination")
    engine,_result = one_case(constant=True,omit_source=True,K=2,outer=1,record_bits=1,consume=False)
    preserved = body(engine.output)
    source,one,zero = Tape(),Count.literal(1),Count.literal(0)
    rejected(lambda:engine.run(source,(),one,one,one,zero,one,one),"consume previous compact output")
    need(body(engine.output) == preserved, "rejected reuse preserves unconsumed output")
    engine.output.clear()
    erase_marker(engine.output)
    source.clear()
    one.close()
    zero.close()
    with sealed_constructors():
        rejected(Tape,"physical allocation")
    return dict(rejections=8,semantic_controls=["omitted_repair","omitted_inverse","reversed_radix_order"],
                protected_output_preserved=True)


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
    print("PASS_PHYSICAL_COMPACT_FAILURE_CONTROLS")
