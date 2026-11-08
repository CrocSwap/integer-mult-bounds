"""Complete two-axis actual Core cohort; an independent finite arithmetic oracle.

Prepared for @CubeJerry with OpenAI Codex assistance. Apache-2.0.
This is a complete semantic replay, not a physical tape replay.
"""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cohort_sources import opened,need
from core_layout import Layout
from core_caller import prepare
from oracles import check_complete
from check_source import fraction_record


def main():
    with opened() as r:
        refs=[r.reference.Reference(r.raw,63,1,1,1,5,192),
              r.reference.Reference(r.raw,63,1,3,1,1,192)]
        layout=Layout((1,6,6),(2,1),5)
        directions=[[(c+a)%2==1 for a in range(2)] for c in range(layout.labels)]
        program=prepare(r,layout,refs,['broad','narrow'],[2,2],directions,
                        target=5,radius_bits=7,incoming=1)
        need(all(root.children for block in program.roots for root in block),
             'every actual broad/narrow source is nonempty')
        need(len({len(child.plan) for block in program.roots for root in block
                  for child in root.children})>1,'unequal actual Full child depths')
        values=[((7*j)%5-2,(11*j)%7-3) for j in range(program.records)]
        output,counts,roundings,error=check_complete(program,values)
        need(roundings>0,'nontrivial realized fresh coefficient/data truncations')
        alpha=Q(99827101,100000000); eta=Q(332353,332929)
        beta=Q(39,40);xi=Q(15,16);epsilon=1-Q(1,10**30)
        need(3**5<2**8 and beta*alpha>Q(3,5),'exact Karatsuba absorption margin')
        need(beta<Q(997,1000) and beta+2*xi-2<1,'long-field and precision margins')
        need(1-epsilon<beta and beta<epsilon,'cache absorption and balanced groups')
        invoice=dict(beta=str(beta),xi=str(xi),epsilon=str(epsilon),alpha=str(alpha),eta=str(eta),
            gauge_power=str(beta+2*xi-2),dense_group_power=str(epsilon-(1-alpha)*beta),
            route_group_power=str(epsilon-(1-eta)*beta),
            scalar_group_power_upper=str(epsilon-beta+Q(3,5)),
            full_field_records=program.records,per_interior_data_padding=0,
            source_setup='K*g*2^O(ell)*poly(p); explicit cache and history space',
            inherited_native_constructor='fixed source constant under its own admission')
        result=dict(status='PASS_ACTUAL_CORE_MULTIAXIS',physical_execution=False,
            records=program.records,labels=program.labels,axes=program.axes,layout=layout.record(),
            source_families=['broad','narrow'],directions=program.directions,
            source_starts=[[root.partition.first for root in block] for block in program.roots],
            indices=[[root.partition.indices for root in block] for block in program.roots],
            depths=program.depths,stages=program.stages,grid=program.bits,width=program.data_width,
            counts=counts,nonzero_roundings=roundings,error_squared=fraction_record(error),
            output_sha256=sha256(json.dumps(output,separators=(',',':')).encode()).hexdigest(),
            complete_invoice=invoice)
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':main()
