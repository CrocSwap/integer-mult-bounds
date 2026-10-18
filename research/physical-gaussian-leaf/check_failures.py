"""Source, finite-carry, coefficient traversal and protected-return controls."""
from pathlib import Path
from types import ModuleType
import importlib.util
import json
import sys
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))


def rejected(label,call,message):
    try:
        call()
    except ValueError as error:
        if message not in str(error):
            raise ValueError("unexpected control failure for "+label+": "+str(error)) from error
    else:
        raise ValueError("accepted injected fault: "+label)
    return label


def fresh_sources():
    spec = importlib.util.spec_from_file_location("failure_leaf_sources",HERE/"leaf_sources.py")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def run():
    controls = []
    source = fresh_sources()
    with patch.dict(sys.modules,{"words":ModuleType("words")}):
        controls.append(rejected("warm source namespace",source.activate,"cold physical Gaussian coefficient namespace"))
    source = fresh_sources()
    with patch.object(source,"ARCHIVE_SHA256","0"*64):
        controls.append(rejected("changed predecessor archive",source.activate,"immutable Gaussian monomial source archive"))

    import check_words
    import check_leaf
    import signed_linear
    import axis_stream
    from coefficient_engine import CoefficientEngine
    from compact_counts import copy_bits
    from leaf_test_support import body
    from session import erase_marker,initialize_marker
    from words import need

    def truncate_carry(carry,bits,signs):
        value = carry+sum(sign*bit for sign,bit in zip(signs,bits))
        return value%2,(abs(value)//2)*(-1 if value < 0 else 1)
    with patch.object(signed_linear,"transition",truncate_carry):
        controls.append(rejected("truncate negative carry toward zero",check_words.run,"exact C component"))

    actual_word = signed_linear.linear_word
    def suppress(kind):
        def faulty(*args,**kwargs):
            try:
                return actual_word(*args,**kwargs)
            except signed_linear.CoefficientDomainError as error:
                if kind not in str(error):
                    raise
        return faulty
    for kind in ("inexact","headroom"):
        with patch.object(check_words,"linear_word",suppress(kind)):
            controls.append(rejected("suppress "+kind+" rejection",check_words.run,"exact C component value"))

    actual_pair = axis_stream.c_pair
    def wrong_inverse(left,right,out_left,out_right,width,buffers,inverse=False):
        return actual_pair(left,right,out_left,out_right,width,buffers,False)
    with patch.object(axis_stream,"c_pair",wrong_inverse):
        controls.append(rejected("forward C in inverse leaf",check_leaf.run,"complete encoded C leaf inverse"))

    calls = 0
    def first_field_only(left,right,out_left,out_right,width,buffers,inverse=False):
        nonlocal calls
        if calls%3 == 0:
            actual_pair(left,right,out_left,out_right,width,buffers,inverse)
        else:
            for _ in range(2):
                copy_bits(left,out_left,width)
                copy_bits(right,out_right,width)
        calls += 1
    with patch.object(axis_stream,"c_pair",first_field_only):
        controls.append(rejected("skip later coefficient fields",check_leaf.run,"complete encoded C leaf forward"))

    engine = CoefficientEngine(("v0",),"v0")
    initialize_marker(engine.output)
    engine.output.append(1)
    engine.output.rewind()
    saved = body(engine.output)
    controls.append(rejected("overwrite unconsumed output",engine.rearm,"consume previous coefficient output"))
    need(body(engine.output) == saved and engine.output.head == 1 and engine.closed,
         "rejected reuse preserves protected output")
    engine.output.clear()
    erase_marker(engine.output)
    return dict(controls=controls,rejected=len(controls),scope="Eight source, carry/guard, inverse, all-field and returned-port failures; admitted named rejection recovery remains separately checked")


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
    print("PASS_GAUSSIAN_LEAF_FAILURE_CONTROLS")
