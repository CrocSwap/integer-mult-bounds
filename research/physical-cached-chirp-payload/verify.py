"""Registered source-bound physical transaction and mutation replay."""
from pathlib import Path
import importlib.util
import json
import math
import sys

P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('cached_chirp_loader',P/'sources.py')
S=importlib.util.module_from_spec(spec);sys.modules[spec.name]=S;spec.loader.exec_module(S)

def reduced_tables(radices,slopes,f):
    unit=1<<f;diagonal=math.isqrt(1<<(2*f-1)) if f else 0
    roots=((unit,0),(diagonal,-diagonal),(0,-unit),(-diagonal,-diagonal),
           (-unit,0),(-diagonal,diagonal),(0,unit),(diagonal,diagonal))
    return tuple(tuple(roots[s*x*x*(4//t)%8] for x in range(t))
                 for t,s in zip(radices,slopes))

def main():
    pins=S.authenticated_inputs()
    C=S.load('certified_chirp_tables',P/'chirp_tables.py')
    R=S.load('fresh_rounded_chirp',P/'rounded_oracle.py')
    A=S.load('direct_angle_chirp',P/'analytic_oracle.py')
    V=S.load('physical_chirp_checks',P/'physical_tests.py')
    intervals=S.interval_source()
    bundle=C.prepare((8,4),(7,3),1,10,oracle=intervals);plan=bundle.plan
    receipts=[];source_passes=[]
    with S.physical_runtime():
        from chirp_consumer import CachedChirp
        owner=CachedChirp();values=V.payload_words(32,plan.f)
        for conjugate in (False,True):
            actual,physical=V.exercise(owner,plan.radices,bundle.tables,plan.f,plan.W,R,conjugate,values)
            analytic=A.check(plan.radices,plan.slopes,values,actual,plan.f,
                             plan.payload_l1_error,intervals,conjugate)
            source_passes.append(dict(physical=physical,analytic=analytic))
        fixtures=(((4,2,4),(1,3,5),10,16),((4,4),(3,5),18,26),
                  ((2,),(1,),3,6),((2,2,2,2,2),(1,3,5,7,9),6,10),
                  ((4,),(3,),0,4))
        for radices,slopes,f,width in fixtures:
            tables=reduced_tables(radices,slopes,f)
            for conjugate in (False,True):
                data=((1,0),(-1,0),(0,1),(0,-1)) if f==0 else None
                _,receipt=V.exercise(owner,radices,tables,f,width,R,conjugate,data)
                receipts.append(receipt)
        guards=V.guards(owner,(4,2,4),reduced_tables((4,2,4),(1,3,5),10),10,16)
        mutations=V.mutations(plan.radices,bundle.tables,plan.f,plan.W,R)
        small=reduced_tables((2,),(1,),3)
        _,historical=V.exercise(owner,(2,),small,3,6,R)
        _,fresh=V.exercise(CachedChirp(),(2,),small,3,6,R)
        V.need(historical['symbol_actions']==fresh['symbol_actions'],
               'history-independent current live-body tariff')
        receipt=dict(status='PASS_CACHED_CHIRP_PAYLOAD',pins=pins,source=bundle.receipt(),
            source_passes=source_passes,fixtures=receipts,guards=guards,mutations=mutations,
            history=dict(used=historical,fresh=fresh))
    print(json.dumps(receipt,sort_keys=True,indent=2))

if __name__=='__main__':main()
