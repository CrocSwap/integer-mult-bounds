"""Physical 3-bit adapter from generated grants to the retained continuation.

No descriptor arithmetic is evaluated here. The literal producer table is
executed through the unchanged PR6719 stateless codec, then actual binary
backing is erased and outputs are placed at the retained grant-copy origins.
This is a one-edge adapter, not a production depth/weight evaluator.
thu-nmrc with substantial OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path
import importlib.util
import sys
import producer as P

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('retained_composition',HERE/'inputs/PR6719-composition/composition.py')
C=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=C
spec.loader.exec_module(C)


class GrantBridge:
    """L is compiled before the physical inputs; four scratch roles are fixed."""
    def __init__(self, low_types):
        self.program=P.build(low_types)

    def run(self, parent_a, high_header, parent_r, child_a, child_r, scratch):
        C.s.need(len(scratch)==4,'four fixed grant-producer scratch tapes')
        ports=(parent_a,high_header,parent_r,child_a,child_r)+tuple(scratch)
        C.execute(self.program,tuple(C.CodedTape(t)for t in ports))
        # Logical blank000 is genuine retained binary backing, so it must
        # also be erased physically before the scratch is called empty.
        for tape in scratch:
            C.clear_base(tape)
        # The existing return/copy protocol consumes a full encoded packet
        # from just after BASE, including its logical LEFT codeword.
        C.origin(child_a,C.s.BASE)
        C.origin(child_r,C.s.BASE)
