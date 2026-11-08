"""Executed small physical controls for the new join, independent of source LU.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from types import ModuleType


def run(engine, decode, need):
    from cardinal_counts import Count
    from check_support import no_decode
    from periodic_consumer import convert
    from periodic_tapes import emit
    from records import Tape
    from ring_words import difference, scaled, truncate
    from router_metadata import owned
    from session import erase_marker, initialize_marker, sealed_constructors

    def tape_for(words, width):
        tape = Tape(); emit(words, tape, width); tape.rewind(); return tape

    def enter():
        for tape in engine.pool.tapes:
            initialize_marker(tape)

    def leave():
        engine.pool.empty()
        for tape in engine.pool.tapes:
            erase_marker(tape)

    def conversion(operation):
        with owned(Count.literal(4), Count.literal(8), Count.literal(2), Count.literal(1)) as (n,w,f,g):
            source=tape_for((-1,-3,1,3),w); target=Tape()
            enter()
            try:
                with no_decode(), sealed_constructors(), engine.scope.installed():
                    operation(source,target,n,w,w,f,g)
                    engine.pool.empty()
                target.rewind()
                return decode(target,4,8)
            finally:
                leave()
                for tape in (source,target):
                    tape.clear(); erase_marker(tape)

    correct=conversion(convert)
    need(correct==(0,-1,0,1), 'negative downconversion truncates toward zero')

    def floor_down(value, amount):
        result=truncate(value,amount)
        try:
            with owned(scaled(result,amount)) as (recovered,):
                with owned(difference(value,recovered)) as (remainder,):
                    if value.negative and not remainder.magnitude.zero():
                        result.magnitude.increment();result.negative=True
            answer,result=result,None
            return answer
        finally:
            if result is not None:
                result.close()

    text=(Path(__file__).parent/'periodic_consumer.py').read_text()
    good='truncate(value, shift) if down else scaled(value, shift)'
    bad='floor_down(value, shift) if down else scaled(value, shift)'
    need(text.count(good)==1,'unique literal conversion mutation')
    mutant=ModuleType('_periodic_floor_mutation');mutant.__dict__['floor_down']=floor_down
    exec(compile(text.replace(good,bad),'<executed negative-floor conversion>','exec'),mutant.__dict__)
    wrong=conversion(mutant.convert)
    need(wrong==(-1,-2,0,1) and wrong!=correct,'executed arithmetic-floor mismatch')

    def band(product_first):
        with owned(Count.literal(3),Count.literal(1),Count.literal(8),Count.literal(2)) as (m,b,w,f):
            source=tape_for((3,3,3),w)
            coefficients=tape_for((0,1,1, 1,1,1, 1,1,0),w)
            target=Tape(); original=engine.arithmetic
            if product_first:
                class RoundedProduct:
                    def multiply(self,left,right,width):
                        with owned(original.multiply(left,right,width)) as (product,):
                            with owned(truncate(product,f)) as (rounded,):
                                return scaled(rounded,f)
                engine.arithmetic=RoundedProduct()
            enter()
            try:
                with no_decode(),sealed_constructors(),engine.scope.installed():
                    engine.band_apply(source,coefficients,target,m,b,w,f)
                    engine.pool.empty()
                target.rewind()
                return decode(target,3,8)
            finally:
                engine.arithmetic=original
                leave()
                for tape in (source,coefficients,target):
                    tape.clear();erase_marker(tape)

    completed=band(False); premature=band(True)
    need(completed==(1,1,2),'physical completed-dot and fold/unfold witness')
    need(premature==(0,0,0) and premature!=completed,'executed premature-product rounding mismatch')
    return dict(conversion=correct,arithmetic_floor=wrong,
                completed_dot=completed,premature_products=premature)
