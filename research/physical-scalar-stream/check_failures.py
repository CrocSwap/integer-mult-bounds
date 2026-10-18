"""Reject source, shift, local-lifetime and protected-return perturbations."""
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
            raise ValueError("unexpected scalar control failure for "+label+": "+str(error)) from error
    else:
        raise ValueError("accepted scalar fault: "+label)
    return label


def fresh_sources():
    spec = importlib.util.spec_from_file_location("failure_scalar_sources",HERE/"scalar_sources.py")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def run():
    controls = []
    source = fresh_sources()
    with patch.dict(sys.modules,{"words":ModuleType("words")}):
        controls.append(rejected("warm physical namespace",source.activate,"cold physical scalar namespace"))
    source = fresh_sources()
    with patch.dict(source.ARCHIVES,{"pr3090":"0"*64}):
        controls.append(rejected("changed recipe source archive",source.exports,"immutable scalar source archive"))

    import check_shifts
    import check_packets
    import scalar_engine
    import scalar_words
    from scalar_test_support import body
    from session import erase_marker,initialize_marker
    from signed_linear import CoefficientDomainError
    from words import need

    actual_shift = scalar_words.shifted
    def suppress(category):
        def faulty(*args,**kwargs):
            try:
                return actual_shift(*args,**kwargs)
            except CoefficientDomainError as error:
                if category not in str(error):
                    raise
        return faulty
    for category in ("inexact","headroom"):
        with patch.object(check_shifts,"shifted",suppress(category)):
            controls.append(rejected("suppress shift "+category,check_shifts.run,"exact signed shift value"))

    actual_instruction = scalar_engine.instruction
    def omit_clear(registers,operation,*args):
        if operation == ("clear",2):
            return
        return actual_instruction(registers,operation,*args)
    with patch.object(scalar_engine,"instruction",omit_clear):
        controls.append(rejected("omit local scratch CLEAR",check_packets.run,"scalar logical scratch is not zero"))

    def omit_restore(registers,operation,*args):
        if operation == ("double",1):
            return
        return actual_instruction(registers,operation,*args)
    with patch.object(scalar_engine,"instruction",omit_restore):
        controls.append(rejected("omit source-walk inverse shifts",check_packets.run,"scalar source component not restored"))

    actual_zero,calls = scalar_engine.zero_word,0
    def dirty_initial_zero(tape,width):
        nonlocal calls
        actual_zero(tape,width)
        if calls == 0:
            tape.write(1)
        calls += 1
    with patch.object(scalar_engine,"zero_word",dirty_initial_zero):
        controls.append(rejected("COPY into nonzero local scratch",check_packets.run,"scalar logical scratch is not zero"))

    key = ("scale",1,1,"scratch")
    engine = scalar_engine.ScalarEngine((key,))
    initialize_marker(engine.output)
    engine.output.append(1)
    engine.output.rewind()
    saved = body(engine.output)
    controls.append(rejected("select with unconsumed return",lambda:engine.select(key),"closed consumed scalar selection boundary"))
    need(body(engine.output) == saved and engine.output.head == 1 and engine.closed,
         "scalar selection rejection preserves protected output")
    engine.output.clear()
    erase_marker(engine.output)
    return dict(controls=controls,rejected=len(controls),scope="Eight archive, shift, source/scratch return and protected-output failures; no arbitrary-interruption rollback claim")


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
    print("PASS_PHYSICAL_SCALAR_FAILURES")
