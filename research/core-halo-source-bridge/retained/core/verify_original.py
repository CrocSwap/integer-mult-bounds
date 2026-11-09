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
    parser.add_argument('--output',default=str(HERE/'ORIGINAL-PHYSICAL-RESULT.json'))
    args=parser.parse_args();started=time.monotonic()
    with numerical() as runtime:
        from admitted_context import AdmittedPartition
        from prepared_join import build_numeric,prepare_banks
        reference=runtime.reference.Reference(runtime.raw,7,1,2,1,3,64)
        from core_layout import Layout
        layout=Layout((1,3),(1,),1)
        family=[[AdmittedPartition(runtime,reference,'narrow',layout.core_starts(c)[0],2,1,((1,),))]
                for c in range(layout.labels)]
        partition=family[0][0]
        programs,windows,actions,blocks,plan=build_numeric(runtime,family)
        source_Q=[[w.H for w in row] for row in windows]
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
        from original_layout import OriginalCore,PreparedRoutes
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
            owner=OriginalCore(root,observe=observe)
            routes=PreparedRoutes(layout,family,width)
            def normalized(tape):
                return bytes(tape.cells).rstrip(bytes((BLANK,)))
            initial_private={id(t):normalized(t) for t in owner.forbidden()}
            payload=Tape()
            inputs=tuple(((((17*i+3)%19)-9)*(1<<(P-8))+(2*i+1),
                          (((11*i+5)%23)-11)*(1<<(P-8))+(2*i+3)) for i in range(16))
            def packed_index(i):return ((i>>1)&1)|((i&1)<<1)|(i&12)
            packed_inputs=[None]*16
            for i,pair in enumerate(inputs):packed_inputs[packed_index(i)]=pair
            packed_inputs=tuple(packed_inputs)
            for pair in inputs:
                for x in pair:emit_signed(payload,x,width)
            payload.rewind()
            up=tuple(Count.literal(x) for x in (1,2,1,1,width,P))
            data=(payload,prepared[0].code,prepared[1].code,ibank,fbank,keys)
            ports=(*data,routes.forward,routes.inverse,*(x.tape for x in
                    (*prepared[0].parameters,*prepared[1].parameters,*up,*routes.parameters)))
            saved=snapshot(ports);before=meter();online_started=time.monotonic()
            online_roles=len(all_tapes)
            private_ids=tuple(map(id,owner.forbidden()))
            bases={1,2,width,width+1,width+2,*(p.data_width for p in programs),
                   *(p.data_width+1 for p in programs),*(p.data_width+2 for p in programs)}
            with folded.certified_floors(bases) as (table,calls,misses):
                with no_decode():
                    returned=owner.run(payload,routes.forward,routes.inverse,routes.parameters,
                        *data[1:],prepared[0].parameters,prepared[1].parameters,up)
                outputs=values(returned)
                online_actions=difference(before)
                need(not misses,'complete declared finite metadata specialization')
            need(snapshot(ports)==saved,'all borrowed payload/source/metadata heads and bodies restored')
            need(len(all_tapes)==online_roles and tuple(map(id,owner.forbidden()))==private_ids,
                 'no new online tape roles through all global and eight-context child reuses')
            order=('D_Ainv_1','T1','D_A','T2','D_Ainv_2')
            previous=packed_inputs
            for name in order:
                need(observations[name]['input']==previous,'literal current-input stage continuity')
                previous=observations[name]['output']
            need(tuple(previous[packed_index(i)] for i in range(16))==outputs,
                 'actual inverse original-coordinate route returns every last-stage value')
            observed=dict(allocation=plan,initial=inputs,packed_initial=packed_inputs,
                          returned=outputs,packed_returned=previous,layout=layout.record(),observations=observations,
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
            receipt=dict(status='PASS_ORIGINAL_COORDINATE_PHYSICAL_NARROW_CORE',
                scope='K8 g1 L2 identity scalar A; actual nonidentity original-axis routes and nonidentity Q',
                allocation=plan,source=dict(parameters=list(reference.spec.__dict__.values()),
                    origins=[row[0].first for row in family],interior=[1],layout=layout.record(),
                        reference_sha256=reference.description_hash,
                    Q=[[[[str(x) for x in row] for row in matrix] for matrix in context]
                       for context in source_Q]),
                dense_programs=[p.record() for p in programs],
                complete_dense_calls=3,complete_dense_events=2*programs[0].stages+programs[1].stages,
                complete_sparse_calls=[owner.core.inverse.child.calls,owner.core.forward.child.calls],
                initial=inputs,returned=outputs,packed_initial=packed_inputs,packed_returned=previous,
                observations=observations,
                dense_boundary_changed=[observations[s]['input'][0]!=observations[s]['output'][0]
                                        for s in ('D_Ainv_1','D_A','D_Ainv_2')],
                setup_actions=setup_actions,online_actions=online_actions,consume_actions=consume_actions,
                owned_retained_cells=backing,all_constructed_retained_cells=sum(len(t.cells) for t in all_tapes),
                tape_roles=len(all_tapes),metadata_bases=sorted(bases),metadata_calls=len(calls),
                online_new_tapes=len(all_tapes)-online_roles,
                fixed_private_inventory=len(private_ids),
                initially_marked_or_configured_roles=sum(bool(v) for v in initial_private.values()),
                native_fixture='unchanged standard q2; fixed Karatsuba leaf64',
                seconds=time.monotonic()-started,online_seconds=time.monotonic()-online_started,
                no_new_kappa=True)
            Path(args.output).write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
            print('PASS '+args.output,flush=True)
            routes.close()
            for p in prepared:p.close()
            for x in up:x.close()
            for t in (payload,ibank,fbank,keys):t.clear();erase_marker(t)

if __name__=='__main__':main()
