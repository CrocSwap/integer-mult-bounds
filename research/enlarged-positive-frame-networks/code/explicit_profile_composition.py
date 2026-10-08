#!/usr/bin/env python3
"""Exact joint composition of explicit actual local/data profiles.

Local basis proofs and full data-family witnesses are separate inputs. This
driver never infers a profile from a rank or from an upstream headline ratio.
"""
import argparse,json,importlib.util
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from exact_composition import reconstruct,choose,moment,bridge,js,read

def main():
    p=argparse.ArgumentParser()
    for name in ('axes','phase','assembly','geometry','output'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--data',type=Path)
    a=p.parse_args();items=read(a.axes);rows=[x['producer'] for x in items]
    assert [r['h'] for r in rows]==[23,25]
    bit=reconstruct(rows)
    for k,item in enumerate(items):
        row=item['producer'];h=row['h'];prof=item['fixed_profile'];copies=bit['N']//row['v']
        assert prof['R']==row['R']
        assert prof.get('crt_disagreements',prof.get('different_modular_profiles'))==0
        assert sum(t*n for t,n in enumerate(prof['blocks']))==h*row['R']+2*row['loss']==prof['rank_sum']
        local=Counter({t:copies*n for t,n in enumerate(prof['blocks']) if t and n})
        assert local[h]>=copies*h
        local[h]-=copies*h;local[1]+=copies*h
        bit['parts'][f'local_{k}']=+local
    if a.data:
        data=read(a.data);assert data['pairs']==bit['N']
        null={int(t):n for t,n in data['null_blocks'].items()}
        assert min(null)>0 and min(null.values())>0
        assert sum(t*n for t,n in null.items())==47*bit['N']
        children=Counter({t:2*n for t,n in null.items()})
        children[481]+=2*bit['N'];bit['parts']['data']=children
        bit['data_profile_description']=data
    hist=sum(bit['parts'].values(),Counter())
    bit['child_multiplicities']={t:n for t,n in sorted(hist.items()) if n}
    assert sum(t*n for t,n in hist.items())==bit['W']*575-bit['N']+bit['L']
    bit['basis_mode']='explicit actual profiles; source compatibility in separate receipt'
    bm=choose(bit);pr=read(a.phase);phase=reconstruct([pr,pr],True)
    cm=moment(phase,Q(717,10**7));assert cm['strict_gap']>0
    f=bridge(bit,phase,[pr,pr]);spec=importlib.util.spec_from_file_location('credited_assembly',a.assembly)
    am=importlib.util.module_from_spec(spec);spec.loader.exec_module(am)
    saving=bm['saving'];backoff=Q(1,10**12);q=saving*(1-2*backoff)
    margin=(1-backoff)*q/(1+q);scaled=margin*10**14
    k=Q(scaled.numerator//scaled.denominator,10**14);assert k<margin
    assembly=am.assembly(f,saving,k);eventual=am.cutoffs(f,assembly)
    files=[a.axes,a.phase,a.assembly,a.geometry]+([a.data] if a.data else [])
    result=dict(bit=bit,phase=phase,bit_moment=bm,phase_moment=cm,finite_bridge=f,
        assembly=assembly,eventual=eventual,kappa=k,
        geometry_receipt=read(a.geometry),input_sha256={str(x):sha256(x.read_bytes()).hexdigest() for x in files},
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        status='Exact conditional arithmetic; source/frame/profile/compiler/proof acceptance must be recorded separately')
    assert not a.output.exists();a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(js(result),indent=2)+'\n')
    print(json.dumps(dict(a=str(saving),kappa=str(k),constraints=len(assembly['constraints']),W=bit['W'])))

if __name__=='__main__':main()
