"""One bounded genuine cached/Cyclic/common-grid transaction and controls.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from join_sources import opened,authenticate,need
from oracle import staged,ideal,external,decode

def main():
    auth=authenticate()
    with opened() as state:
        from join_preparation import Prepared,allocate
        from joined_middle import Middle
        from chirp_fixture import compiled_setup
        from check_composed import fixture
        from check_support import no_decode
        from convolution_engine import Convolution
        from cyclic_engine import Cyclic
        from fourier_engine import Fourier
        from words import BLANK
        q,chi=10,7
        prepared=Prepared((4,2),(3,1),q,chi,state.intervals)
        p=prepared.plan
        values=[(400,0),(-256,64),(100,-50),(141,211),(-88,-241),(300,1),(-100,17),(11,-301)]
        expected,phase=staged(values,q,p.f)
        want=ideal(values,q)
        error=max(abs(Fraction(a,1<<q)-c)+abs(Fraction(b,1<<q)-d)
                  for (a,b),(c,d) in zip(expected,want))
        declared=Fraction(p.coefficient,1<<p.f)+Fraction(2,1<<q)
        need(error<declared<=Fraction(1,1<<chi),'actual-input universal defect envelope')
        source=state.B.Tape('borrowed q-grid prefix',external(values,q));state.B.home(source)
        saved_source=source.inspect()
        saved_ports=[(bytes(t.cells),t.head) for t in prepared.ports()]
        machine=Middle(state,prepared,Cyclic(Convolution(Fourier(fixture()[0]))))
        with compiled_setup() as setup,no_decode():
            returned=machine.run(source)
        actual=decode(returned.inspect(),q)
        need(actual==expected,'genuine composite matches independent integer oracle')
        need(source.inspect()==saved_source and source._head==1,'borrowed source body and origin')
        need(saved_ports==[(bytes(t.cells),t.head) for t in prepared.ports()],'borrowed source banks and origins')
        need(machine.cached.calls==3 and machine.cached.records==24 and machine.cached.cache_updates==24,
             'three actual shared-bank cached passes')
        need(machine.cached.arithmetic.products==192 and machine.arithmetic.products==16,
             'actual cached products and radius squares')
        need(machine.cyclic.calls==dict(tables=1,twists=2,convolutions=1,narrowings=1,untwists=1),
             'actual complete cyclic transaction')
        need(machine.cyclic.convolution.calls==dict(forward=2,product=1,opposite=1,scale=1),
             'three actual Fourier children and one exact M scale')
        # Pending return is protected even after an observer moves its head.
        try:machine.run(source)
        except ValueError:pass
        else:raise ValueError('missing pending-return rejection')
        need(decode(returned.inspect(),q)==expected,'protected return bytes')
        machine.consume()
        bad=state.B.Tape('over-radius input',external([(600,0)]+values[1:],q));state.B.home(bad)
        try:
            with no_decode():machine.run(bad)
        except ValueError as e:need('disk radius' in str(e),'actual radius guard rejection')
        else:raise ValueError('missing radius rejection')
        need(machine.cached.calls==3,'radius failure precedes cached work')
        need(machine.closed and not machine.pending and not machine.pool.live,'closed middle after failure')
        need(all(t.head==1 and all(v==BLANK for v in t.cells)
                 for t in (*machine.pool.tapes,*machine.banks)),'middle scratch/field erasure')
        machine.cached.idle();machine.cyclic.idle();machine.word.idle()
        controls=['pending_return','actual_radius_before_phase','shared_borrowed_origin','same_grid_signed_width']
        for name,kwargs in [('first_conjugate',{'first_conjugate':False}),
                            ('last_conjugate',{'last_conjugate':False}),('exact_M_scale',{'scale':False})]:
            wrong,_=staged(values,q,p.f,**kwargs)
            need(wrong!=expected,'independent distinguishing seam control: '+name);controls.append(name)
        wrong,_=staged(values,q,p.f,final_drop=False)
        need(wrong!=expected and any(abs(a)>=(1<<(q+1)) or abs(b)>=(1<<(q+1)) for a,b in wrong),
             'omitting actual final grid drop changes values and overflows external carrier')
        controls.append('final_external_grid_drop')
        cases=0
        for D in range(2,17):
            radices=(4,)*(D-1)+(2,)
            for target in (0,1,7,31,63):
                a=allocate(radices,(1,)*D,target+2,target)
                need(Fraction(a.coefficient,1<<a.f)+Fraction(2,1<<a.q)<=Fraction(1,1<<target),
                     'complete allocation guard')
                cases+=1
        receipt={
            'claim':'source-bound cached chirp / cyclic / grid join; no new kappa',
            'canonical_inputs':auth[0],'public_dependencies':auth[1],
            'q':q,'f':p.f,'W':p.W,'chi':chi,'T':p.volume,'D':p.D,'A':p.A,
            'output':actual,'output_sha256':sha256(external(actual,q).encode()).hexdigest(),
            'maximum_component_l1_error':str(error),'universal_bound':str(declared),
            'cached_calls':machine.cached.calls,'cached_scalar_products':machine.cached.arithmetic.products,
            'input_radius_scalar_products_before_rejection':16,
            'cyclic_calls':machine.cyclic.calls,'convolution_calls':machine.cyclic.convolution.calls,
            'compiled_metadata_setup':setup,'controls':controls,'allocation_cases':cases,
            'native_boundary':'Retained exact q2 finite provider; production GL64/O73 not executed.',
            'fixture_setup':'Canonical compiled_setup proves exact three small floor-power constants; numerical/physical children unchanged.',
            'full_fine_family_execution':False,'complete_multiplier_claim':False}
        prepared.close()
    print('PASS_CACHED_CHIRP_CYCLIC_JOIN')
    print(json.dumps(receipt,sort_keys=True,indent=2))

if __name__=='__main__':main()
