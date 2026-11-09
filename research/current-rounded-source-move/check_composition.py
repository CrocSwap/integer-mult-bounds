"""Actual descriptor consumers and exact-source rounding-placement controls.

Metadata checks do not execute a numerical MOVE. They use actual literal
serial/cutoff tables and unchanged monomial/leaf preparation methods.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from contextlib import ExitStack
from fractions import Fraction
from hashlib import sha256
import json
from types import SimpleNamespace
from rounded_move_sources import HERE,load,need,authenticate
from rounded_move import RoundedMove,S,P
from ordinary import Ordinary
from macro_code import Code
from check_rounded import Tape,put,body,encode_header,decode_header,encode_components

A=P.A

def factory():
    return Ordinary(2,SimpleNamespace(codes=SimpleNamespace(q=2)),SimpleNamespace(families=0),
                    (Code((("unreachable",),),0),),capacity=64)

def specimen(rank,f,h,K=1,coefficients=1):
    H=max(1,f-1);u=2*H;z=u+9*f*K;a=z+H;b=6*coefficients*(h+1)
    return dict(outer=2,rows=3,stock=6,row_bits=(1<<a)*b,within_bits=a,record_bits=b,
                p=9*f,d=9*f,K=K,G=1,H=H,q0=3,qF=0,qB=0,D=9,f=f,rho=K-1,
                active_start=u,back_start=z,selected_axes=9*f,entry_start=u,remainder=0,cutoff=145)

def fresh(rank):
    pc,triple=next((pc,t) for pc,t in S.catalog.catalog()[1].items() if t[1].rank==rank)
    provider=RoundedMove(triple,factory)
    work=[Tape(3+j%5) for j in range(provider.port_count)];field,context=Tape(9),Tape(11)
    provider.bind(work,{provider.owner:A.CodedPort(field)},A.BinaryContextPort(context))
    return provider,work,field,context,pc

def count_value(value):
    """Read-only checker observation of the physical Count encoding."""
    tape=value.tape.owned() if hasattr(value.tape,'owned') else value.tape
    data=body(tape.native_port.raw);symbols=[]
    need(len(data)%12==0,'complete native Count codes')
    for start in range(0,len(data),12):
        chunk=data[start:start+12]
        need(all(chunk[j]==0 for j in (0,1,3,4,6,7,9,10)),'binary symbols in native codec')
        symbols.append(sum(chunk[3*j+2]<<(3-j) for j in range(4)))
    need(symbols[0]==2 and 3 in symbols,'Count marker and delimiter')
    digits=symbols[1:symbols.index(3)];need(digits and all(x in (0,1) for x in digits),'Count digits')
    return sum(bit<<j for j,bit in enumerate(digits))

def prepare_native(native,field,context):
    native.cohort.start()
    try:
        with P.C.execution(),native.scope.installed(),ExitStack() as cleanup:
            header=native.read_header(context)
            for value in header.values():cleanup.callback(value.close)
            h=native.component_width(field);cleanup.callback(h.close)
            widths,rho,coefficients,rows=native.prepare(header,h,cleanup)
            # No provider branches on these host observations. They are read
            # only after the actual encoded preparation has returned.
            result=dict(h=count_value(h),widths=[count_value(x) for x in widths],
                        rho=count_value(rho),coefficients=count_value(coefficients),rows=count_value(rows))
        native.pool.empty()
        return result
    finally:native.cohort.finish()

def metadata_case(rank,f,h,K,c):
    provider,work,field,context,pc=fresh(rank)
    parent=specimen(rank,f,h,K,c);bits=encode_header(parent)
    put(context,bits);put(field,encode_components([0,0],h))
    tapes=(*work,field,context);ancestors=[bytes(t.cells[:t.origin]) for t in tapes]
    before=sum(t.actions() for t in tapes)
    provider.cohort.start();cleanup=ExitStack();reports=[]
    try:
        with P.C.execution(),provider.scope.installed():
            decoded=provider.read_header(A.BinaryContextPort(context))
            for value in decoded.values():cleanup.callback(value.close)
            width=provider.component_width(A.CodedPort(field));cleanup.callback(width.close)
            _g,_margin,_wide,_components,widened=provider.prepare(decoded,width,cleanup)
            provider.write_header(widened)
        w=h+rank*f+(rank*f+2)//2+1
        expected=dict(parent,record_bits=6*c*(w+1),row_bits=(1<<parent['within_bits'])*6*c*(w+1))
        need(decode_header(body(provider.wide_context.tape))==expected,'paid outer widened descriptor')
        engine=provider.child.engine
        # Only a signed format specimen is placed here. The astronomical
        # declared complete fields are NOT materialized or numerically run.
        put(engine.stage.tape,encode_components([0,0],w))
        for name,side in (('entrance',engine.entry),('exit',engine.exit)):
            side.view.prepare()
            try:
                for j in range(f):
                    child_header=decode_header(body(side.view.context.tape))
                    wanted=dict(expected,f=1,K=f*K,rho=parent['rho']+j*K,selected_axes=9)
                    need(child_header==wanted,'literal serial view preserves widened whole field and changes exact column fields')
                    result=prepare_native(side.native,engine.stage,side.view.context)
                    want_widths=[0,parent['H'],0,parent['H'],0]+[f*K]*9+[0,0]
                    need(result==dict(h=w,widths=want_widths,rho=f*K-1-parent['rho']-j*K,
                                      coefficients=c*(1<<parent['H']),rows=6),
                         'actual signed monomial prepare accepts the widened view with exact folded coefficients')
                    reports.append(dict(factor=name,column=j,prepared=result))
                    need(side.view.advance()==('finished' if j+1==f else 'ready'),'literal complete column iteration')
            finally:
                if side.view.active:side.view.release()
        child=engine.child;child.view.prepare()
        try:
            child_header=decode_header(body(child.view.context.tape))
            need(child_header==dict(expected,f=rank*f,cutoff=rank*parent['cutoff']),
                 'only the positive child receives scaled f and cutoff')
            result=prepare_native(child.native,engine.stage,child.view.context)
            need(result==dict(h=w,widths=[parent['active_start'],rank*f*K,
                parent['within_bits']-parent['active_start']-rank*f*K],rho=K-1-parent['rho'],
                coefficients=c,rows=6),'unchanged positive prepare consumes the exact expanded geometry')
            reports.append(dict(factor='positive',prepared=result))
        finally:child.view.release()
        A.retire(engine.stage.tape)
    finally:
        with P.C.execution(),provider.scope.installed():cleanup.close();provider.pool.empty()
        provider.cohort.finish()
        for port in work[:3]:A.retire(port)
    need(body(context)==bytes(bits) and all(not body(t) for t in work)
         and all(t.head==t.origin for t in tapes),'all 4368 roles and borrowed parent return')
    need(all(bytes(t.cells[:t.origin])==old for t,old in zip(tapes,ancestors)),'all ancestor prefixes preserved')
    return dict(source_event=pc,rank=rank,f=f,h=h,w=w,K=K,coefficients=c,
                complete_declared_records=6*(1<<parent['within_bits']),ports=len(work),
                consumer_results=reports,metadata_actions=sum(t.actions() for t in tapes)-before,
                metadata_only=True,numerical_MOVE_executed=False)

def source_checks():
    count=authenticate();entries=S.catalog.catalog()[1]
    representatives=[next(t for t in entries.values() if t[1].rank==r) for r in range(1,9)]
    ports=[]
    for triple in representatives:
        value=RoundedMove(triple,factory);ports.append(value.port_count)
        need(value.child.engine.child.view.__class__ is S.prior.cutoff.CutoffView,
             'explicit current cutoff child in exact direct coordinator')
    need(ports==[4368]*8 and S.common.monomial.Count is P.Count and S.common.monomial.Tape is P.Tape
         and S.serial.S.abi is P.A and S.serial.S.codec is P.C,
         'all source ranks share the exact physical object classes and fixed factory inventory')
    triple=representatives[0];bad=0
    for mutation in ((triple[2],triple[1],triple[0]),triple[:2]):
        try:RoundedMove(mutation,factory)
        except ValueError:bad+=1
        else:raise ValueError('invalid raw source chronology accepted')
    return dict(retained_files=count,shared_source_joins=109,raw_source_occurrences=len(entries),
                rank_inventories=ports,invalid_triples=bad,ordinary_runtime_invocations=0,
                child_substitution_explicit=True)

def round_up(value):
    return (value+Fraction(1,2)).numerator//(value+Fraction(1,2)).denominator

def early_overflow(reference,record,original):
    """Bounded actual-source counterexample to an intermediate h=2 downcast."""
    attempts=0
    for y in range(8):
        for angle in (0,1):
            attempts+=1
            middle=[(0,0)]*512
            middle[y]=reference.rotate((1,0),angle)
            middle[y^1]=reference.rotate((1,1),angle)
            inputs=[reference.rotate(middle[reference.binary_map(record['right']['matrix_rows'],x)
                        ^record['right']['offset']],-reference.phase(record['right'],x)) for x in range(512)]
            need(all(-2<=a<2 and -2<=b<2 for a,b in inputs),'all actual source inputs fit h=2')
            child,den=reference.evaluate([('C',1,1)],middle)
            early=[(round_up(Fraction(a,1<<den)),round_up(Fraction(b,1<<den))) for a,b in child]
            full,full_den=reference.evaluate(original.circuit,inputs)
            exit_exact=reference.monomial(child,record['left'])
            need([(Fraction(a,1<<den),Fraction(b,1<<den)) for a,b in exit_exact]
                 ==[(Fraction(a,1<<full_den),Fraction(b,1<<full_den)) for a,b in full],
                 'complete original source agrees with exact phased exit')
            final=[(round_up(Fraction(a,1<<full_den)),round_up(Fraction(b,1<<full_den))) for a,b in full]
            if any(not -2<=v<2 for pair in early for v in pair) and all(-2<=v<2 for pair in final for v in pair):
                index=next(j for j,pair in enumerate(early) if any(not -2<=v<2 for v in pair))
                return dict(component_width=2,middle_pair_address=y,quarter_phase=angle,
                    attempted_candidates=attempts,search_limit=16,early_overflow_address=index,
                    early_rounded_pair=early[index],all_512_final_outputs_fit=True,
                    input_sha256=sha256(json.dumps(inputs).encode()).hexdigest(),
                    final_sha256=sha256(json.dumps(final).encode()).hexdigest(),
                    actual_input_radius_domain_claim=False,physical_MOVE_execution=False)
    raise ValueError('bounded actual-source early-overflow counterexample not found')

def source_tie():
    # Reuse the independently written exact original-circuit evaluator from
    # the direct predecessor, with its unchanged source and credit retained.
    reference=load('rounded_move_original_matrix_oracle',HERE/'vendor/direct/check_move.py')
    pc=9896;triple,original,record=S.catalog.bind_move(S.catalog.catalog()[1][pc])
    candidates=[]
    for basis in range(8):
        for pair in ((1,0),(0,1),(-1,0),(0,-1)):
            values=[(0,0)]*512;values[basis]=pair
            entrance=reference.monomial(values,record['right'])
            middle,den=reference.evaluate([('C',1<<j,1) for j in range(record['rank'])],entrance)
            full,full_den=reference.evaluate(original.circuit,values)
            exact_exit=reference.monomial(middle,record['left'])
            need([(Fraction(a,1<<den),Fraction(b,1<<den)) for a,b in exact_exit]
                 ==[(Fraction(a,1<<full_den),Fraction(b,1<<full_den)) for a,b in full],
                 'exact full source factorization and absolute phase at the witness input')
            early=[(round_up(Fraction(a,1<<den)),round_up(Fraction(b,1<<den))) for a,b in middle]
            early_exit=reference.monomial(early,record['left'])
            final=[(round_up(Fraction(a,1<<full_den)),round_up(Fraction(b,1<<full_den))) for a,b in full]
            if early_exit!=final:
                at=next(j for j in range(512) if early_exit[j]!=final[j])
                return dict(event=pc,owner=triple[1].fields[0],rank=record['rank'],basis=basis,input_pair=pair,
                    differing_output=at,early_round_then_exit=early_exit[at],correct_final_round=final[at],
                    exact_final=[str(Fraction(x,1<<full_den)) for x in full[at]],
                    all_512_outputs_compared=True,physical_MOVE_execution=False,
                    premature_public_width_overflow=early_overflow(reference,record,original))
            candidates.append((basis,pair))
    raise ValueError('bounded actual-source tie discriminator not found')

def check():
    return dict(source=source_checks(),metadata=[metadata_case(*args) for args in (
        (1,1,2,1,1),(1,2,3,2,1),(2,1,4,1,2),(2,2,2,1,1),(8,1,3,1,1),(8,2,5,2,2))],
        actual_source_early_rounding_counterexample=source_tie(),new_whole_numerical_MOVE=False)

if __name__=='__main__':
    from argparse import ArgumentParser
    parser=ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args();result=check()
    if args.output:args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS_ROUNDED_MOVE_COMPOSITION',json.dumps(dict(metadata_cases=len(result['metadata']),
        source_occurrences=result['source']['raw_source_occurrences'],ports=4368,
        actual_tie=result['actual_source_early_rounding_counterexample'],new_whole_numerical_MOVE=False),sort_keys=True))
