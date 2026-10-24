"""Actual original/cached arithmetic comparisons and ownership failure controls.

JoyboyBrian; substantial OpenAI Codex assistance; Apache-2.0.
"""
from types import MethodType

def run(cached,cardinality,records,words,Count):
    def need(ok,message):
        if not ok:raise ValueError(message)
    def observe(value):
        body=value.tape.cells[1:];stop=body.index(words.RIGHT)
        return sum(bit<<i for i,bit in enumerate(body[:stop]))
    tapes=[];original_init=records.Tape.__init__
    def register(tape):original_init(tape);tapes.append(tape)
    records.Tape.__init__=register
    cases=0;controls=[]
    try:
        for q in(2,3,5):
            for w in(1,2,3):
                for exponent in(0,1,3):
                    for initial in(1,5,173):
                        ia,ra=words.Arena(8,64),words.Arena((q**w).bit_length()+1,128)
                        power=ra.literal(q**w);ring=words.Ring(power)
                        e=ia.literal(exponent);dirty=ra.literal(1)
                        saved=[(v,bytes(v.cells),v.head)for v in(power,ring.one,e,dirty)]
                        outputs=[];sequences=[]
                        for helper in(cardinality.multiply_atom_power,cached):
                            value=Count.literal(initial);calls=[]
                            original=value.multiply_small
                            def multiply(self,constant):calls.append(constant);original(constant)
                            value.multiply_small=MethodType(multiply,value)
                            inspect=words.Word.inspect;words.Word.inspect=lambda _:(_ for _ in()).throw(ValueError('runtime decode forbidden'))
                            try:helper(value,e,ring,q)
                            finally:words.Word.inspect=inspect
                            outputs.append(observe(value));sequences.append(calls);value.close()
                        need(outputs==[initial*(q**w)**exponent]*2,'exact original/cached output')
                        need(sequences==[[q]*(w*exponent)]*2,'unchanged full Count multiplier word')
                        need(all((bytes(v.cells),v.head)==(raw,head)for v,raw,head in saved),'borrowed numerical state')
                        ia.free(e);ra.free(dirty);ring.close();ra.free(power)
                        need(not ia.live and not ra.live,'comparison numerical cleanup');cases+=1
        for exponent in(0,1):
            ia,ra=words.Arena(8,64),words.Arena(4,128)
            power=ra.literal(6);ring=words.Ring(power);e=ia.literal(exponent)
            value=Count.literal(173);saved=(bytes(value.tape.cells),value.tape.head)
            try:cached(value,e,ring,3)
            except ValueError:controls.append('non-prime-power context rejected before Count writes')
            else:raise ValueError('invalid radix accepted')
            need((bytes(value.tape.cells),value.tape.head)==saved,'failed validation leaves Count untouched')
            value.close();ia.free(e);ring.close();ra.free(power)
            need(not ia.live and not ra.live,'invalid-radix numerical cleanup')
        ia,ra=words.Arena(8,64),words.Arena(5,128)
        power=ra.literal(9);ring=words.Ring(power);e=ia.literal(3);value=Count.literal(5)
        saved=[(v,bytes(v.cells),v.head)for v in(power,ring.one,e)]
        original=value.multiply_small
        failure=RuntimeError('injected Count failure after one completed write')
        def reject(self,constant):original(constant);raise failure
        value.multiply_small=MethodType(reject,value)
        try:cached(value,e,ring,3)
        except RuntimeError as error:
            need(error is failure and observe(value)==15,'partial Count output and original exception retained')
            controls.append('partial Count failure releases cache and Counter without output rollback')
        else:raise ValueError('injected failure ignored')
        need(all((bytes(v.cells),v.head)==(raw,head)for v,raw,head in saved),'failure preserves borrowed operands')
        value.close();ia.free(e);ring.close();ra.free(power)
        need(not ia.live and not ra.live,'failure numerical cleanup')
        ia,ra=words.Arena(8,64),words.Arena(4,128)
        power=ra.literal(6);ring=words.Ring(power);e=ia.literal(1);value=Count.literal(5)
        protected=set(ra.live)
        try:cardinality.multiply_atom_power(value,e,ring,3)
        except ValueError:pass
        else:raise ValueError('original malformed context unexpectedly accepted')
        need(len(ra.live-protected)==2,'original guard leaks returned quotient and remainder')
        controls.append('original malformed guard positive control leaks exactly two Words')
        ra.rollback(protected)  # Observer-only teardown after the failed original call.
        value.close();ia.free(e);ring.close();ra.free(power)
        need(not ia.live and not ra.live,'positive-control fixture disposal')
        need(all(t.head==1 and all(x==words.BLANK for x in t.cells[1:])for t in tapes),
             'all control Count/cache/Counter backing erased')
    finally:records.Tape.__init__=original_init
    return dict(original_cached_pairs=cases,unchanged_multiplier_words=cases,
                controls=controls,all_control_backing_erased=True)
