"""Probe the actual seven-stage configuration, its positive receiver and its signed caller."""

from fractions import Fraction as F
import json

from installations import EXTENDED

D = EXTENDED.positive_stop_denominator
HM = EXTENDED.complex_log


def exact_capped_test(power_le):
    for e in (2, 3, 9):
        for k in (1, 2, 5, 29, 100):
            for d in (-1, 0, 1):
                x = e**k+d
                assert power_le(e,k,x) == (e**k <= x)
    e = 2 << HM
    assert not power_le(e, D, e)
    assert power_le(e, 1, e)

    class Two:
        """Represent 2**exponent exactly. Only ceiling+1 can have plus=1."""
        counts = {"multiply": 0, "successor": 0}
        def __init__(self, exponent, plus=0):
            self.e, self.plus = exponent, plus

        def __mul__(self, other):
            assert self.plus == other.plus == 0
            Two.counts["multiply"] += 1
            return Two(self.e + other.e)

        def __rmul__(self, one):
            assert one == 1 and not self.plus
            Two.counts["multiply"] += 1
            return self

        def __add__(self, one):
            assert one == 1 and not self.plus
            Two.counts["successor"] += 1
            return Two(self.e,1)

        def __lt__(self, other):
            assert min(self.e, other.e) > 0
            return (self.e,self.plus) < (other.e,other.plus)

        def __gt__(self, other):
            return other < self

    trace = []
    for off in (-1,0,1):
        Two.counts = dict.fromkeys(Two.counts, 0)
        assert power_le(Two(HM+1), D, Two((HM+1)*D+off)) == (off>=0)
        assert Two.counts == {"multiply":D.bit_length()-1 + D.bit_count(),
                               "successor":D.bit_length()-1}
        trace.append((off, dict(Two.counts)))
    return trace


def install_test():
    import band_product as bp
    p = EXTENDED
    from compact_columns import Columns
    from positive import power_le
    from spool import Field

    recipes = bp.prepare_native(p)
    assert len(recipes) == 3 and D == 10**18 and HM == 20000000
    for recipe, height in zip(recipes, (*p.rank_logs, HM), strict=True):
        assert recipe.rank_log == height and recipe.width_log == 92*height
    supplier=bp.production_supplier(HM, D)
    assert supplier.carrier == 1 << HM and supplier.denominator == D
    recipe = supplier.recipe
    assert recipes[-1] is recipe
    assert (len(recipe.targets),len(recipe.paid),len(recipe.cells))==(105216,564144,54)
    assert recipe.trial == F(2092819,2**29)
    e = supplier.carrier * 2
    field = Field(1,8)
    payload = bytes(range(32))
    field.stream.write(payload)
    field.stream.seek(0)
    columns = Columns(1,0,1,0,0,0,0,None)
    try:
        supplier._run(field,0,e,columns,e)
    except ValueError as exc:
        assert str(exc) == "The positive field has no independent row reserve."
    else:
        raise AssertionError("The receiver accepted a short physical field")
    field.stream.seek(0)
    assert field.stream.read(len(payload))==payload
    field.retire()
    from ordinary_carrier import stage_for_width_log
    from staged_carriers import admitted_stage, entrance_logs
    small = (1,2,3,4,5,6,7)
    for i,cut in enumerate(entrance_logs(small),1):
        for digits in ((1<<cut)-1, 1<<cut, (1<<cut)+1):
            assert stage_for_width_log(digits.bit_length()-1,7,small) == admitted_stage(digits,7,small)
    return {"installed_rank_exponents":[q.rank_log for q in recipes],
            "atlas_ports":len(recipe.targets),"paid_ports":len(recipe.paid),
            "coupling_cells":len(recipe.cells),"positive_trial":str(recipe.trial),
            "production_receiver_negative_probe":"short physical field rejected; input preserved",
            "D_bits":D.bit_length(),"D_ones":D.bit_count(),
            "actual_gate_exponent_pair_traces":exact_capped_test(power_le)}


if __name__ == "__main__":
    print(json.dumps(install_test(),indent=2))
