"""Two uniform branches: rank-only controls and a scoped line obstruction.

No surviving rank profile is asserted to be a matrix representation.
"""
from collections import deque
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import argparse
import json
from local_support_elimination import ADJ,CAPACITY,TRIPLES,CLIQUE,INDEX,classes,initial_supports
from noncovariant_search import multiply

Y=sorted(i for _,y in classes() for i in y)


def color_y():
    """Small exact backtracking control, not an impossibility search."""
    supports,_=initial_supports((3,)*7)
    domains={i:{k for k in range(7) if supports[i]>>k&1} for i in Y}
    result={}
    def visit():
        if len(result)==len(Y):return True
        available={i:domains[i]-{v for j,v in result.items() if ADJ[i]>>j&1}
                   for i in Y if i not in result}
        i=min(available,key=lambda j:(len(available[j]),-sum(ADJ[j]>>k&1 for k in available),j))
        for v in sorted(available[i]):
            result[i]=v
            if visit():return True
            del result[i]
        return False
    assert visit()
    assert all(result[i]!=result[j] for i,j in combinations(Y,2) if ADJ[i]>>j&1)
    return result


def rank_on(directions,mask):
    nonzero={value for i,value in enumerate(directions) if mask>>i&1 and value}
    return 2 if -1 in nonzero or len(nonzero)>=2 else int(bool(nonzero))


def rank_profile(mode):
    """Coordinate row-space ranks, with an independent abstract basis per label.

    -1 is a full two-dimensional row space. Positive integers name distinct
    rational lines *within that label's internal two-space*.
    """
    a,b=initial_supports((mode,)*7);color=color_y();profiles=[]
    for i,t in enumerate(TRIPLES):
        row=[0]*8
        for k in range(8):
            if not a[i]>>k&1:continue
            if t in CLIQUE:row[k]=-1
            elif mode==2 and i in Y:row[k]=2 if k==color[i] else 1
            else:row[k]=k+1
        profiles.append(row)
    verify_profile(mode,profiles)
    return profiles


def verify_profile(mode,profiles):
    a,b=initial_supports((mode,)*7)
    assert len(profiles)==84 and a==b
    for i,row in enumerate(profiles):
        assert len(row)==8
        assert all((x!=0)==bool(a[i]>>k&1) for k,x in enumerate(row))
        assert row[7]!=-1
        assert rank_on(row,a[i])==2
        # A and B use the same abstract profile; the elementary product-rank
        # bound for a sum equal to I_2 is also satisfied.
        assert sum(rank_on(row,1<<k) for k in range(8))>=2
    for i,j in combinations(range(84),2):
        if ADJ[i]>>j&1:
            common=a[i]&b[j]
            assert rank_on(profiles[i],common)+rank_on(profiles[j],common)<=CAPACITY[common]
    return True


def line_graph(slot):
    supports,_=initial_supports((3,)*7)
    vertices=[i for i in Y if supports[i]>>slot&1]
    edges=[(i,j) for i,j in combinations(vertices,2)
           if ADJ[i]>>j&1 and supports[i]&supports[j]==1<<slot]
    neighbors={i:[] for i in vertices}
    for i,j in edges:neighbors[i].append(j);neighbors[j].append(i)
    colors={vertices[0]:0};tree=[];queue=deque([vertices[0]])
    while queue:
        i=queue.popleft()
        for j in neighbors[i]:
            if j not in colors:
                colors[j]=1-colors[i];queue.append(j);tree.append((i,j))
            assert colors[i]!=colors[j]
    assert len(colors)==len(vertices)==18 and len(edges)==54
    partitions=[]
    for _,group in classes():
        for outside in (7,8):
            clique=[i for i in group if outside in TRIPLES[i]]
            if all(i in vertices for i in clique):partitions.append(clique)
    assert len(partitions)==6
    return {'slot':slot,'vertices':vertices,'edges':edges,'colors':{str(i):c for i,c in colors.items()},
            'spanning_tree':tree,'saturated_clique_controls':partitions}


def verify_line_obstruction(data):
    supports,_=initial_supports((3,)*7)
    assert len(data['blocks'])==7
    for slot,block in enumerate(data['blocks']):
        assert block['slot']==slot
        vertices=set(block['vertices']);colors={int(i):c for i,c in block['colors'].items()}
        assert vertices=={i for i in Y if supports[i]>>slot&1}
        expected={tuple(sorted((i,j))) for i,j in combinations(vertices,2)
                  if ADJ[i]>>j&1 and supports[i]&supports[j]==1<<slot}
        assert {tuple(e) for e in block['edges']}==expected
        assert all(colors[i]!=colors[j] for i,j in expected)
        reached={min(vertices)}
        for i,j in block['spanning_tree']:
            assert tuple(sorted((i,j))) in expected and i in reached and j not in reached
            reached.add(j)
        assert reached==vertices
        for clique in block['saturated_clique_controls']:
            assert len(clique)==3 and all(ADJ[i]>>j&1 for i,j in combinations(clique,2))
            union=0
            for i in clique:union|=supports[i]
            assert CAPACITY[union]==6 and union>>slot&1
    assert len(data['edge_obstructions'])==7
    for point,edge in enumerate(data['edge_obstructions']):
        i,j=edge['edge'];assert ADJ[i]>>j&1
        assert i in classes()[point][1] and j in classes()[point][1]
        common=supports[i]&supports[j];same=[];opposite=[]
        assert not common&128
        for k in range(7):
            if common>>k&1:
                colors=data['blocks'][k]['colors']
                (same if colors[str(i)]==colors[str(j)] else opposite).append(k)
        assert len(same)==1 and len(opposite)==2
        assert same==edge['single_nonzero_block'] and opposite==edge['zero_blocks']
    stars=[set(edge['single_nonzero_block']+edge['zero_blocks']) for edge in data['edge_obstructions']]
    covers=[tuple(k for k in range(7) if mask>>k&1) for mask in range(128)
            if all(any(mask>>k&1 for k in star) for star in stars)]
    minimum=min(map(len,covers));assert minimum==data['minimum_bad_blocks']==3
    assert sorted(c for c in covers if len(c)==minimum)==[tuple(c) for c in data['minimum_bad_block_sets']]
    return True


def line_obstruction():
    blocks=[line_graph(k) for k in range(7)]
    supports,_=initial_supports((3,)*7);edges=[]
    for _,group in classes():
        clique=[i for i in group if 7 in TRIPLES[i]]
        i,j=clique[:2];same=[];opposite=[]
        for k in range(7):
            if (supports[i]&supports[j])&(1<<k):
                colors=blocks[k]['colors']
                (same if colors[str(i)]==colors[str(j)] else opposite).append(k)
        edges.append({'edge':[i,j],'single_nonzero_block':same,'zero_blocks':opposite})
    stars=[set(e['single_nonzero_block']+e['zero_blocks']) for e in edges]
    covers=[c for c in combinations(range(7),3) if all(set(c)&star for star in stars)]
    result={'scope':'Uniform mode 3. A block is good if every allowed A and B restriction of its 18 Y labels has rank one. At least three blocks must be bad (some restriction of rank zero or two). No whole branch is excluded.',
            'blocks':blocks,'edge_obstructions':edges,'minimum_bad_blocks':3,
            'minimum_bad_block_sets':covers}
    verify_line_obstruction(result)
    return result


def local_block_control(block):
    """Exact realizations of each isolated 18-label block test.

    These are restrictions of hypothetical factors, not full projectors.
    The obstruction only appears when three such blocks must be combined.
    """
    colors={int(i):c for i,c in block['colors'].items()};weights={}
    for clique in block['saturated_clique_controls']:
        for i in clique:
            weights[i]=Q(1,sum(colors[j]==colors[i] for j in clique))
    factors={}
    for i,c in colors.items():
        a=[[Q(0)]*2 for _ in range(2)];b=[[Q(0)]*2 for _ in range(2)]
        a[c][0]=1;b[0][c]=weights[i];factors[i]=(a,b)
    for i,j in block['edges']:
        assert multiply(factors[i][1],factors[j][0])==[[0,0],[0,0]]
        assert multiply(factors[j][1],factors[i][0])==[[0,0],[0,0]]
    for clique in block['saturated_clique_controls']:
        total=[[Q(0)]*2 for _ in range(2)]
        for i in clique:
            p=multiply(*factors[i])
            total=[[x+y for x,y in zip(row,other)] for row,other in zip(total,p)]
        assert total==[[1,0],[0,1]]
    return True


def audit():
    obstruction=line_obstruction()
    for block in obstruction['blocks']:local_block_control(block)
    return {'status':'SCOPED RANK-PROFILE EXCLUSION; NO NEW KAPPA',
            'rank_only_controls':{str(mode):rank_profile(mode) for mode in (2,3)},
            'rank_only_result':'Both uniform branches satisfy all pairwise restricted-rank inequalities with full rank-two factors in the abstract profiles. These are not matrix solutions.',
            'line_obstruction':obstruction,
            'isolated_block_rational_controls_passed':7,
            'unrestricted_dimension_15':'OPEN; the 103 surviving branch representatives have not been reduced by this scoped test.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=audit();args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status']);print(result['rank_only_result'])
