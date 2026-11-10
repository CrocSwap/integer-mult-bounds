"""Complete physical five-factor replay; observations never supply payloads.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys
import time
from unittest.mock import patch
from join_sources import HERE,COHORT,numerical,physical,load,need

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--preflight',action='store_true')
    parser.add_argument('--output',default=str(HERE/'PHYSICAL-RESULT.json'))
    args=parser.parse_args();started=time.monotonic()
    with numerical() as runtime:
        from admitted_context import AdmittedPartition
        from prepared_join import build_numeric,prepare_banks
        reference=runtime.reference.Reference(runtime.raw,7,1,2,1,3,64)
        partition=AdmittedPartition(runtime,reference,'narrow',2,2,1,((1,),))
        family=[[partition]]
        programs,windows,actions,blocks,plan=build_numeric(runtime,family)
        source_Q=[[windows[0][0].H]]
        need(partition.matrices[0][0][0].re==1 and partition.matrices[0][0][0].im==0,
             'finite fixture has identity scalar interior A')
        need(any(source_Q[0][0][i][j] for i in range(2) for j in range(2) if i!=j),
             'nonidentity original complete reference Q')
        print('PREFLIGHT '+json.dumps(plan,sort_keys=True),flush=True)
        if args.preflight:return
        types=(runtime.global_compiler.Hadamard,runtime.global_compiler.Diagonal)
    with physical() as state:
        from records import Tape
        from cardinal_counts import Count
        from physical_controls import PreparedFull,emit_signed
        from physical_join import CompleteCore
        from check_support import no_decode
        from session import erase_marker
        from words import BLANK
        import check_composed
        # External counters retain every constructed tape's historical backing.
        all_tapes=[];original_init=Tape.__init__
        def tracked(self,*a,**kw):
            original_init(self,*a,**kw);all_tapes.append(self)
        def meter():
            return tuple(sum(getattr(t.meter,k) for t in all_tapes) for k in ('reads','writes','moves'))
        def difference(before):return tuple(a-b for a,b in zip(meter(),before))
        with patch.object(Tape,'__init__',tracked):
            from fixture_tools import body,snapshot,integer
            folded=load('join_certified_floors',COHORT/'fixture_tools.py')
            prep_start=meter()
            prepared=[PreparedFull(program,Tape,Count,types) for program in programs]
            print('DENSE_CONTROLS_PREPARED',flush=True)
            ibank,fbank,keys=prepare_banks(family,windows,actions,blocks,plan)
            print('SPARSE_BANKS_PREPARED',flush=True)
            setup_actions=difference(prep_start)
            root,visits=check_composed.fixture('standard',False)
            observations={};width=plan['width'];P=plan['P']
            def values(tape):
                raw=body(tape)
                need(len(raw)%(2*width)==0,'complete observed common-width field')
                return tuple((integer(raw[i:i+width]),integer(raw[i+width:i+2*width]))
                             for i in range(0,len(raw),2*width))
            def observe(stage,phase,tape):
                observations.setdefault(stage,{})[phase]=values(tape)
                print('STAGE '+stage+' '+phase,flush=True)
            owner=CompleteCore(root,observe=observe,dense_leaf_bits=64)
            def normalized(tape):
                return bytes(tape.cells).rstrip(bytes((BLANK,)))
            initial_private={id(t):normalized(t) for t in owner.forbidden()}
            payload=Tape()
            inputs=(((1<<(P-3))+1,-(1<<(P-4))+3),
                    (-(1<<(P-5))+5,(1<<(P-6))+7))
            for pair in inputs:
                for x in pair:emit_signed(payload,x,width)
            payload.rewind()
            up=tuple(Count.literal(x) for x in (1,2,1,1,width,P))
            data=(payload,prepared[0].code,prepared[1].code,ibank,fbank,keys)
            ports=(*data,*(x.tape for x in (*prepared[0].parameters,*prepared[1].parameters,*up)))
            saved=snapshot(ports);before=meter();online_started=time.monotonic()
            bases={1,*(p.data_width for p in programs),
                   *(p.data_width+1 for p in programs),*(p.data_width+2 for p in programs)}
            with folded.certified_floors(bases) as (table,calls,misses):
                with no_decode():
                    returned=owner.run(*data,prepared[0].parameters,prepared[1].parameters,up)
                outputs=values(returned)
                online_actions=difference(before)
                need(not misses,'complete declared finite metadata specialization')
            need(snapshot(ports)==saved,'all borrowed payload/source/metadata heads and bodies restored')
            order=('D_Ainv_1','T1','D_A','T2','D_Ainv_2')
            previous=inputs
            for name in order:
                need(observations[name]['input']==previous,'literal current-input stage continuity')
                previous=observations[name]['output']
            need(previous==outputs,'protected return is actual last-stage result')
            observed=dict(allocation=plan,initial=inputs,returned=outputs,observations=observations,
                          source_Q=[[[[str(x) for x in row] for row in matrix]
                                     for matrix in context] for context in source_Q])
            Path(args.output).with_name(Path(args.output).stem+'-OBSERVED.json').write_text(
                json.dumps(observed,indent=2,sort_keys=True)+'\n')
            backing=sum(len(t.cells) for t in owner.forbidden())
            end=meter()
            with no_decode():owner.consume()
            consume_actions=difference(end)
            initial_marker=bytes((2,))
            need(all(t.head==1 and
                     (normalized(t) in (b'',initial_private[id(t)])
                      if initial_private[id(t)] in (b'',initial_marker)
                      else normalized(t)==initial_private[id(t)])
                     for t in owner.forbidden()),
                 'dynamic backing erased and native retained configuration restored')
            receipt=dict(status='PASS_COMPLETE_PHYSICAL_NARROW_CORE',
                scope='K1 g1 L2 identity scalar A; nonidentity complete original Q',
                allocation=plan,source=dict(parameters=list(reference.spec.__dict__.values()),
                    origin=2,interior=[1],reference_sha256=reference.description_hash,
                    Q=[[[[str(x) for x in row] for row in matrix] for matrix in context]
                       for context in source_Q]),
                dense_programs=[p.record() for p in programs],
                complete_dense_calls=3,complete_dense_events=2*programs[0].stages+programs[1].stages,
                complete_sparse_calls=[owner.inverse.child.calls,owner.forward.child.calls],
                initial=inputs,returned=outputs,observations=observations,
                dense_boundary_changed=[observations[s]['input'][0]!=observations[s]['output'][0]
                                        for s in ('D_Ainv_1','D_A','D_Ainv_2')],
                setup_actions=setup_actions,online_actions=online_actions,consume_actions=consume_actions,
                owned_retained_cells=backing,all_constructed_retained_cells=sum(len(t.cells) for t in all_tapes),
                tape_roles=len(all_tapes),metadata_bases=sorted(bases),metadata_calls=len(calls),
                initially_marked_or_configured_roles=sum(bool(v) for v in initial_private.values()),
                native_fixture='unchanged standard q2; fixed Karatsuba leaf64',
                seconds=time.monotonic()-started,online_seconds=time.monotonic()-online_started,
                no_new_kappa=True)
            Path(args.output).write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
            print('PASS '+args.output,flush=True)
            for p in prepared:p.close()
            for x in up:x.close()
            for t in (payload,ibank,fbank,keys):t.clear();erase_marker(t)

if __name__=='__main__':main()
