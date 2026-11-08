#!/usr/bin/env python3
"""Physical full periodic caller, source inverse oracle, and executed controls.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Host decoding and arrays are external verification only.
"""
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from time import perf_counter
from types import SimpleNamespace

PACKAGE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


S=load('periodic_source_loader',PACKAGE/'sources.py')
P=load('periodic_page_producer',PACKAGE/'periodic_pages.py')
PC=load('periodic_page_checks',PACKAGE/'preparation_checks.py')
O=load('periodic_original_oracle',PACKAGE/'original_periodic.py')
R=load('periodic_rounded_oracle',PACKAGE/'rounded_oracle.py')
H=load('periodic_physical_controls',PACKAGE/'physical_checks.py')
B=load('periodic_independent_inverse',PACKAGE/'original_periodic_oracle.py')
TR=load('periodic_independent_transport',PACKAGE/'transport_review.py')


def unique(tapes):
    return tuple({id(t):t for t in tapes}.values())


def snapshot(tapes):
    return tuple((bytes(t.cells),t.head) for t in tapes)


def actions(tapes):
    return sum(t.meter.reads+t.meter.writes+t.meter.moves for t in unique(tapes))


def reject(name, operation, expected):
    try:
        operation()
    except ValueError as error:
        need(str(error)==expected,name+': wrong failure '+str(error))
        return name
    raise ValueError(name+': negative control escaped')


def original_check(reference, words, actual, precision, allowance, target):
    result=B.check(reference,words,actual,precision,allowance,Q(1,1<<target))
    need(result['wrong_wrap_exceeds_declared_bound'],'original wrap-removal negative control')
    return P.encoded(result)


def main():
    need(sys.argv[1:] in ([],['--main']), 'only optional extended --main fixture')
    extended=bool(sys.argv[1:])
    raw=S.authenticated_inputs();rs,C,D,RO=S.components()
    factory=lambda spec:rs.make_reference(raw,spec)
    preparation=PC.run(P,C,D,factory,O)
    spec,target=((17,1,2,2,3,96),24) if extended else ((7,2,2,1,3,96),16)
    reference=factory(spec)
    bundle=P.prepare(reference,1,target,run_coefficients=C,folded_pages=D)
    p=bundle.plan
    words=tuple((((-1 if i%2 else 1)*(i+1)*(1<<p.f))//(4*p.target_size),
                 ((-1 if i%3 else 1)*(p.target_size-i)*(1<<p.f))//(5*p.target_size))
                for i in range(p.target_size))
    need(max(sum(map(abs,v)) for v in words)<=1<<p.f,'promised component-l1 input radius')
    expected=R.action(words,bundle,RO,D)
    controls=[]
    with S.physical_runtime(rs):
        from check_support import no_decode
        from gaussian_rationals import write_count
        from periodic_consumer import PeriodicInverse
        from periodic_tapes import EncodedPeriodicPages,emit
        from records import Tape
        from session import borrowed_count,erase_marker
        from words import BLANK

        def decode(tape,length,width):
            result=[]
            for _ in range(length):
                value=0
                for j in range(width):
                    bit=tape.read();need(bit in(0,1),'complete physical return bit')
                    value|=bit<<j;tape.step(1)
                result.append(value-(1<<width) if value>>(width-1) else value)
            need(tape.read()==BLANK,'exact physical return extent')
            return tuple(result)

        def blank(owner):
            need(all(t.head==1 and all(b==BLANK for b in t.cells)
                     for t in unique(owner.forbidden())),'all fixed owned roles erased at origin')
            owner.idle()

        owner=PeriodicInverse();blank(owner)
        roles=len(unique(owner.forbidden()))
        with EncodedPeriodicPages(bundle) as pages:
            rhs=Tape();emit(tuple(x for row in words for x in row),rhs,pages.counts[5]);rhs.rewind()
            ports=(rhs,*pages.ports()); before=snapshot(ports)
            aliased=SimpleNamespace(**vars(pages));aliased.counts=(pages.counts[0],pages.counts[0],*pages.counts[2:])
            controls.append(reject('descriptor_alias',lambda:owner.run(rhs,aliased),'distinct external periodic ports'))
            deep=SimpleNamespace(**vars(pages));bad_count=borrowed_count(pages.counts[0])
            bad_count.tape=owner.folded_owner.solver.word.product.twiddles.pool.tapes[0]
            deep.counts=(bad_count,*pages.counts[1:])
            controls.append(reject('inactive_descendant_alias',lambda:owner.run(rhs,deep),'distinct external periodic ports'))
            bad_header=Tape();write_count(pages.counts[0],bad_header);bad_header.rewind()
            short=SimpleNamespace(**vars(pages));short.headers=bad_header
            controls.append(reject('truncated_run_header',lambda:owner.run(rhs,short),'complete rational record digit'))
            blank(owner);bad_header.clear();erase_marker(bad_header)
            need(snapshot(ports)==before,'failed-call borrowed restoration')
            meters=unique((*owner.forbidden(),*ports));before_actions=actions(meters)
            started=perf_counter()
            with no_decode():
                output=owner.run(rhs,pages)
            seconds=perf_counter()-started
            measured=actions(meters)-before_actions
            need(snapshot(ports)==before,'all 23 borrowed bodies and origins restored')
            controls.append(reject('protected_output_reentry',lambda:owner.run(rhs,pages),'consume prior periodic output'))
            output.rewind();flat=decode(output,2*p.target_size,p.W)
            actual=tuple(tuple(flat[2*i:2*i+2]) for i in range(p.target_size))
            need(actual==expected,'exact complete rounded periodic schedule')
            owner.consume();blank(owner)
            need(len(unique(owner.forbidden()))==roles,'unchanged full role inventory')
            scalar=4*sum(0 if r.n==1 else 9*r.n+2*r.native.plan.L*((r.n+r.native.plan.L-1)//r.native.plan.L-1) for r in bundle.runs)
            packed=4*sum(0 if r.n==1 else 8*((r.n+r.native.plan.L-1)//r.native.plan.L) for r in bundle.runs)
            boundary=6*p.boundary_size*(2*p.band+1)
            need(sum(owner.run_owner.scalar_word.calls.values())==scalar and
                 sum(owner.run_owner.convolution.word.calls.values())==packed and
                 sum(owner.folded_owner.solver.word.calls.values())==boundary,'exact complete word-product invoice')
            need(owner.run_owner.calls==4*len(bundle.runs) and owner.block_passes==4
                 and owner.folded_owner.calls==2 and owner.matrix_rows==4*p.boundary_size,
                 'full complex two-pass call counts')
            check=original_check(reference,words,actual,p.f,p.complex_error,target)
            need(R.action(words,bundle,RO,D,omit_k=True)!=actual,'omitted K exact-bit schedule control')
            need(R.action(words,bundle,RO,D,floor_down=True)!=actual,'floor conversion exact-bit schedule control')
            receipt=dict(spec=spec,target=target,seconds=seconds,physical_actions=measured,
                roles=roles,retained_owned_cells=sum(len(t.cells) for t in unique(owner.forbidden())),
                outer_pool_peak=owner.pool.peak,run_calls=owner.run_owner.calls,
                run_scalar_products=scalar,run_packed_products=packed,boundary_products=boundary,
                source_check=check,input_words=words,output_words=actual,
                words_sha256=sha256(json.dumps(actual).encode()).hexdigest(),pages=bundle.receipt())
            rhs.clear();erase_marker(rhs)
        primitive_controls=H.run(owner,decode,need);blank(owner)
        transport_controls=TR.run(owner,need);blank(owner)
    print('PASS_PHYSICAL_PERIODIC_FINE_GAP',flush=True)
    print(json.dumps(dict(extended=extended,physical=receipt,controls=controls,
          physical_mutations=primitive_controls,independent_transport=transport_controls,preparation=preparation,
          code_sha256={f:sha256((PACKAGE/f).read_bytes()).hexdigest() for f in
             ('periodic_consumer.py','periodic_tapes.py','periodic_pages.py','original_periodic.py')}),sort_keys=True),flush=True)


if __name__=='__main__':
    main()
