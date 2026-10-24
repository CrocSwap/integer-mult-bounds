"""Unchanged pinned quotient body with a zero-test-only encoded Count method.
JoyboyBrian; substantial OpenAI Codex assistance; Apache-2.0.
"""
import ast
from pathlib import Path
import binary
from records import Tape
from cardinal_counts import Count,positive
from cardinality import radix_power
from words import need


def compile_body(source,q,dimension,families,code_size,radix,family_divisor,low_divisor):
    """Finite source parameters select fixed divisor roles; no input decoding.

    The supplied radix/family/low tapes encode those compiled constants. Their
    construction is external; the high q^(dimension^2) divisor is built here.
    Caller owns disposal of the returned workspace after all invocations.
    """
    high,spare=binary.power_into(radix,dimension,Tape(),Tape())
    remainder,denominator=Tape(),Tape();high_tag=object()
    class LoweredCount(Count):
        def divide_small(self,constant):
            if constant is high_tag:divisor=high
            elif constant==families:divisor=family_divisor
            else:
                need(constant==code_size,'compiled divisor role');divisor=low_divisor
            binary.divide(self.tape,divisor,remainder,denominator)
            answer=0 if binary.zero(remainder) else 1
            remainder.clear()
            return answer
    tree=ast.parse(Path(source).read_text())
    outer=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='compile_quotient')
    original=next(n for n in outer.body if isinstance(n,ast.FunctionDef)and n.name=='quotient')
    # The adapter narrows divide_small to the exact zero predicates it consumes.
    divide_calls=[n for n in ast.walk(original)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='divide_small']
    guarded=[n.left for n in ast.walk(original)if isinstance(n,ast.Compare)and len(n.ops)==1 and isinstance(n.ops[0],ast.Eq)and len(n.comparators)==1 and isinstance(n.comparators[0],ast.Constant)and type(n.comparators[0].value)is int and n.comparators[0].value==0]
    need(len(divide_calls)==3 and all(any(n is g for g in guarded)for n in divide_calls),'exact three quotient zero predicates')
    module=ast.Module(body=[original],type_ignores=[]);ast.fix_missing_locations(module)
    namespace=dict(Count=LoweredCount,positive=positive,radix_power=radix_power,need=need,
                   q=q,dimension=dimension,high_factor=high_tag)
    exec(compile(module,str(source),'exec'),namespace)
    return namespace['quotient'],(high,spare,remainder,denominator),ast.dump(original,include_attributes=False)
