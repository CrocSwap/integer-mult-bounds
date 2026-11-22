"""Real bounded controls for an optional seven-stage #8042 configuration.

The finite product cannot exercise production-size rank logarithms. The tests
separately inspect live recipe construction, selected stage routing, stop
parameter propagation, and a complete reduced-rank physical product.
"""
from collections import Counter
from dataclasses import replace
from fractions import Fraction as Q
from unittest.mock import patch
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from upstream import install
install()

from installations import SEVEN_STAGE, BINARY_C, GAUSSIAN_C
from staged_carriers import admitted_stage, entrance_logs
from positive import power_le
from band_product import Product, prepare_native, production_supplier
from binary_receiver import Receiver
from module_atoms import balanced_widths
from ordinary import rectangle
from streaming_routes import work_tapes
from triangular_ordinary import root_body
from check_product import one, stock_and_public
from transport import Plan
import retimed_supplier

profile = SEVEN_STAGE


class FakeDigits:
    def __init__(self, available):
        self.available=available
    def __lt__(self, other):
        return False
    def bit_length(self):
        return self.available+1


def runtime_checks():
    cuts = entrance_logs(profile.rank_logs)
    for i, cut in enumerate(cuts):
        assert admitted_stage(FakeDigits(cut), len(cuts), profile.rank_logs) == i+1
        if cut:
            assert admitted_stage(FakeDigits(cut-1), len(cuts), profile.rank_logs) == i
    assert power_le(4,3,128) and not power_le(4,4,128)
    assert power_le(1,profile.positive_stop_denominator,1<<1000)
    assert not power_le(2,profile.positive_stop_denominator,1<<1000)

    with patch.object(Plan,"__init__",side_effect=AssertionError("calendar opened during fixed setup")):
        recipes=prepare_native(profile)
    assert len(recipes)==8
    assert tuple(x.rank_log for x in recipes[:-1]) == profile.rank_logs
    assert all(x.trial == BINARY_C and len(x.cells)==24 for x in recipes[:-1])
    assert recipes[-1].rank_log == 36000 and recipes[-1].trial == GAUSSIAN_C
    assert len(recipes[-1].cells)==31
    supplier=production_supplier(profile.complex_log,profile.positive_stop_denominator)
    assert supplier.denominator==10**20 and supplier.carrier==1<<36000
    assert supplier.recipe is recipes[-1]
    other=production_supplier(profile.complex_log,10**17)
    assert other is not supplier and other.denominator==10**17
    # Reach the real _run policy with a tiny stand-in field and record the
    # actual denominator supplied to the stop predicate. The real power_le
    # implementation is independently exercised above.
    old_carrier=supplier.carrier
    supplier.carrier=2
    try:
        observed=[]; leaves=[]
        class Columns:
            window=1
            offset=0
        with patch.object(retimed_supplier,"power_le",
                          side_effect=lambda base,den,root: observed.append((base,den,root)) or True), \
             patch.object(retimed_supplier,"one_axis",
                          side_effect=lambda field,axis: leaves.append(axis)):
            supplier._run(object(),0,4,Columns(),4096)
        assert observed==[(4,10**20,4096)] and leaves==[0,1,2,3]
    finally:
        supplier.carrier=old_carrier
    print("PASS_SEVEN_RUNTIME: 7 stage thresholds; original 24/31 raw couplings; exact policy 10^20",flush=True)


def signed_control():
    stock_and_public(profile)
    core=Receiver(2,balanced_widths(1),direct=True,profile=profile)
    calls=Counter()
    def exchange(src,dst,bits,prefix,gap,suffix):
        assert bits==1
        calls["shuttles"]+=1
        calls["padded_bytes"]+=prefix*81*gap*suffix
        with work_tapes(2) as (opened,restored):
            rectangle(src,opened,2,9,prefix,gap,suffix)
            opened.seek(0)
            root_body(opened,restored,2,prefix,gap,suffix,core)
            restored.seek(0)
            rectangle(restored,dst,2,9,prefix,gap,suffix,restrict=True)
    machine=Product((3,5),8,136,exchange,profile=profile)
    assert machine.profile is profile
    row=one(machine,-741503,466013)
    assert calls["shuttles"]==138 and row["H_calls"]==157248
    assert row["product"]=="-345550037539" and row["coefficients_prefix"]==[11811,10996,4152,868,77]
    print("PASS_SEVEN_SIGNED_CONTROL",row,dict(calls),flush=True)


if __name__=="__main__":
    if "--signed-only" in sys.argv[1:]:
        signed_control()
    else:
        runtime_checks()
        if "--signed" in sys.argv[1:]:
            signed_control()
