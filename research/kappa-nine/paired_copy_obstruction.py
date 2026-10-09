"""Uniform mode 3: paired outside copies strengthen the exception bound.

The complementary-block lemma is used only under its checked two-regular-
block hypotheses. A clique-dimension contradiction then excludes every
exception pattern having a point incident with exactly one exceptional line.
"""
from itertools import combinations
from pathlib import Path
import argparse
import json
from local_support_elimination import ADJ,CLIQUE,TRIPLES,classes,initial_supports
from local_rank_test import line_obstruction,verify_line_obstruction
from mixed_rank_obstruction import forcing_witness,local_control


def make_witness(exceptions,point):
    exceptions=sorted(exceptions)
    sources=[forcing_witness(point,outside,exceptions) for outside in (7,8)]
    block=sources[0]['exception_block']
    target_point=next(j for j in CLIQUE[block] if j!=point)
    targets=[i for i in classes()[target_point][1] if 7 in TRIPLES[i]]
    support,_=initial_supports((3,)*7);transfers=[]
    for target in targets:
        source=next(w['vertex'] for w in sources if ADJ[w['vertex']]>>target&1)
        assert support[source]&support[target]==1<<block
        transfers.append({'source':source,'target':target,'deleted_block':block})
    return {'exception_blocks':exceptions,'source_point':point,'full_rank_sources':sources,
            'target_point':target_point,'target_clique':targets,'forced_zeros':transfers,
            'required_image_dimension':6,'available_image_dimension':4}


def verify_witness(witness):
    exceptions=witness['exception_blocks'];point=witness['source_point']
    sources=witness['full_rank_sources'];assert len(sources)==2
    assert {w['outside'] for w in sources}=={7,8}
    for w in sources:assert w==forcing_witness(point,w['outside'],exceptions)
    block=sources[0]['exception_block']
    assert all(w['exception_block']==block for w in sources)
    target_point=witness['target_point']
    assert target_point!=point and target_point in CLIQUE[block]
    targets=witness['target_clique']
    assert targets==[i for i in classes()[target_point][1] if 7 in TRIPLES[i]]
    assert len(targets)==3 and all(ADJ[i]>>j&1 for i,j in combinations(targets,2))
    support,_=initial_supports((3,)*7);remaining={i:support[i] for i in targets}
    source_vertices={w['vertex'] for w in sources}
    assert len(witness['forced_zeros'])==3
    covered=set()
    for step in witness['forced_zeros']:
        i=step['source'];j=step['target'];k=step['deleted_block']
        assert i in source_vertices and j in targets and k==block
        assert ADJ[i]>>j&1
        assert support[i]&support[j]==1<<block
        remaining[j]&=~(1<<block);covered.add(j)
    assert covered==set(targets)
    union=0
    for mask in remaining.values():union|=mask
    assert union&128==0
    available=2*union.bit_count();required=2*len(targets)
    assert available==witness['available_image_dimension']==4
    assert required==witness['required_image_dimension']==6
    assert available<required
    return True


def audit():
    # Recheck the prior all-regular-star obstruction and the block-inverse
    # control, rather than assuming an earlier solver result.
    verify_line_obstruction(line_obstruction());local_control()
    stars=[{k for k,c in enumerate(CLIQUE) if j in c} for j in range(7)]
    old=[];new=[];survive=[]
    for mask in range(128):
        exceptions={k for k in range(7) if mask>>k&1}
        if any(not star&exceptions for star in stars):
            old.append(sorted(exceptions));continue
        point=next((j for j,star in enumerate(stars) if len(star&exceptions)==1),None)
        if point is not None:
            witness=make_witness(exceptions,point);assert verify_witness(witness);new.append(witness)
        else:survive.append(sorted(exceptions))
    assert len(old)==64 and len(new)==56 and len(survive)==8
    assert min(map(len,survive))==6
    return {'status':'EXACT PAIRED-COPY EXCLUSION; NO NEW KAPPA',
            'scope':'Uniform mode 3 only. A regular block has rank-one restrictions on both A and B for all 18 supported Y labels.',
            'minimum_exceptional_blocks':6,'maximum_regular_blocks':1,
            'previous_regular_star_exclusions':old,'paired_copy_certificates':new,
            'surviving_exception_sets':survive,
            'newly_excluded_beyond_previous_round':49,
            'full_branch_status':'OPEN; all 103 complete branch representatives remain open.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=audit();args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status']);print('56 paired-copy certificates replay; at least six exceptional blocks required.')
