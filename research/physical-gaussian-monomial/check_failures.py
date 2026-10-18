"""Reject mathematical, ownership and source-binding perturbations."""
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
            raise ValueError("unexpected rejection for "+label+": "+str(error)) from error
    else:
        raise ValueError("accepted perturbation: "+label)
    return label


def fresh_sources():
    spec = importlib.util.spec_from_file_location("failure_sources",HERE/"phase_sources.py")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def run():
    controls = []
    source = fresh_sources()
    with patch.dict(sys.modules,{"words":ModuleType("words")}):
        controls.append(rejected("warm source namespace",source.activate,"cold shared physical monomial namespace"))
    source = fresh_sources()
    with patch.object(source,"ARCHIVE_SHA256","0"*64):
        controls.append(rejected("corrupt archive digest",source.activate,"immutable physical Compact source archive"))

    import check_components
    import check_phase_control
    from cardinal_counts import Count
    from check_monomial import one_case
    from gaussian_test_support import GENERIC,body,native_fixture,oracle_address,oracle_phase
    from monomial_engine import MonomialEngine
    from phase_recipe import Recipe
    from session import erase_marker,initialize_marker
    import signed_phase

    actual_phase = Recipe.phase
    def missing_constant(self,state,columns,spacing,residue,inverse=False):
        value = actual_phase(self,state,columns,spacing,residue,inverse)
        repetition = Count(columns)
        try:
            missing = (repetition.divide_small(4)-1)*self.constant
        finally:
            repetition.close()
        return (value+(missing if inverse else -missing))%4
    with patch.object(Recipe,"phase",missing_constant):
        controls.append(rejected("omit repeated tensor constant",check_phase_control.run,"encoded phase and recovered-address inverse"))

    def integer(count):
        # Only the failure injector decodes the physical digits.
        return sum(bit<<index for index,bit in enumerate(body(count.tape)))
    def inverse_wrong_address(self,state,columns,spacing,residue,inverse=False):
        if not inverse:
            return actual_phase(self,state,columns,spacing,residue,inverse)
        f,K,rho = map(integer,(columns,spacing,residue))
        raw = {name:integer(value) for name,value in state.items()}
        mapped = oracle_address(GENERIC,raw,self.vectors,f,K,rho)
        return -oracle_phase(GENERIC,mapped,self.vectors,f,K,rho)%4
    with patch.object(Recipe,"phase",inverse_wrong_address):
        controls.append(rejected("inverse phase at destination address",
                                 lambda:one_case(GENERIC,f=1,rows=1),"complete guarded physical monomial inverse"))

    actual_pair,count = signed_phase.pair,0
    def first_field_only(source,target,width,phase,real,imag):
        nonlocal count
        actual_pair(source,target,width,phase if count%3 == 0 else 0,real,imag)
        count += 1
    with patch.object(signed_phase,"pair",first_field_only):
        controls.append(rejected("phase only first coefficient field",
                                 lambda:one_case(GENERIC,f=1,rows=1),"complete physical Gaussian monomial forward endpoint"))

    actual_read = signed_phase.read_component
    def unguarded(*args):
        actual_read(*args)
        return False
    with patch.object(signed_phase,"read_component",unguarded):
        controls.append(rejected("omit signed headroom",check_components.run,"exact fixed-width signed Gaussian phase"))

    names = ("u","t","v0","v1","dirty","b")
    engine = MonomialEngine(names,("v0","v1"),GENERIC,native_fixture())
    controls.append(rejected("uncompiled Compact action",
                             lambda:engine.compact.select(("u","v0",False)),"action belongs to the compiled monomial word"))
    output = engine.compact.output
    initialize_marker(output)
    output.append(1)
    output.rewind()
    controls.append(rejected("unconsumed Compact return",
                             lambda:engine.compact.select(engine.action(engine.recipe.word[0])),"closed consumed Compact action boundary"))
    output.clear()
    erase_marker(output)
    engine.compact.select(engine.action(engine.recipe.word[0]))
    return dict(controls=controls,rejected=len(controls),scope="Injected failures in actual physical execution and source entry; no arbitrary-malformed-input rollback claim")


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
    print("PASS_GAUSSIAN_FAILURE_CONTROLS")
