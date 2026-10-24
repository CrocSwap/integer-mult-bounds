"""Independent shared-native-map extension of a binary chart certificate.

Uses only Python's standard library. Does not import predecessor graph or
minimum-rank code. Every claimed minimum is bounded by dimension and marked-line
membership, then attained by the actual original shared map on the same source.
This is a geometric invoice check; it grants no physical or phase admission.
"""
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
import argparse, copy, gzip, hashlib, itertools, json

SOURCE_SHA256='aa4a8241da76abd2c06e6576a3ac09e77781321deaac3ad7d3ce4519342a36e6'

def need(ok,message):
    if not ok:raise ValueError(message)

def span(vectors):
    s={0}
    for v in vectors:s|={x^v for x in tuple(s)}
    return frozenset(s)

def dimension(s):
    need(s and not len(s)&(len(s)-1),'binary subspace cardinality')
    return len(s).bit_length()-1

@lru_cache(None)
def basis(s):
    out=[];covered=frozenset({0})
    for v in sorted(s):
        if v not in covered:out.append(v);covered=span(out)
    need(covered==s,'subspace closure')
    return tuple(out)

def mv(columns,v):
    result=0
    for i,c in enumerate(columns):
        if v>>i&1:result^=c
    return result

def image(columns,s):return frozenset(mv(columns,v) for v in s)

def inverse(columns):
    lookup={mv(columns,v):v for v in range(1<<len(columns))}
    need(len(lookup)==1<<len(columns),'invertible source map')
    return tuple(lookup[1<<i] for i in range(len(columns)))

def distance(a,b):return dimension(a)+dimension(b)-2*dimension(a&b)

def lower_bound(a,b,line=None):
    """Any k-space G(A) intersects an l-space B in at most min(k,l).

    If a is in A but b is outside B, its required image b consumes one
    dimension outside B. If a is outside A but b is in B, invertibility
    excludes b from G(A), consuming one dimension of B outside G(A).
    """
    k,l=dimension(a),dimension(b);intersection=min(k,l)
    if line is not None:
        x,y=line;need(x and y,'nonzero marked lines')
        if x in a and y not in b:intersection=min(intersection,k-1)
        if x not in a and y in b:intersection=min(intersection,l-1)
    need(intersection>=0,'consistent marked-line dimensions')
    return k+l-2*intersection

def projected_chart(chart):
    need(len(chart)==9 and all(type(v)is int and 0<v<(1<<18) for v in chart),'canonical chart rows')
    need(len(span(chart))==512,'canonical chart dimension')
    s=span(v&511 for v in chart)
    for v in chart:
        need(all((((v&511)^(v>>9))&u).bit_count()%2==0 for u in basis(s)),'canonical chart phase')
    return s

def chronological_nodes(payload):
    c=payload['canonical'];frames=list(map(span,c['frames']))
    nodes=[];fixed=set();warps=[]
    def new(value,frozen=False):
        i=len(nodes);nodes.append(value)
        if frozen:fixed.add(i)
        return i
    current=[new(frames[f],r<224) for r,f in enumerate(c['start'])]
    for event_index,event in enumerate(payload['programs']['forward']):
        kind=event[0]
        if kind=='scalar':
            gate,f=event[1:];refs=gate[1:3] if gate[0] in ('add','copy') else gate[1:2]
            n=new(frames[f],any(typ!='L' for typ,r in refs))
            for typ,r in refs:
                if typ=='L':current[r]=n
        elif kind=='warp':
            _,role,op,a,b=event;need(role[0]=='L','persistent native occurrence')
            i=new(frames[a]);j=new(frames[b]);current[role[1]]=j
            warps.append({'event':event_index,'op':op,'input':i,'output':j})
        elif kind=='adapter':fixed.add(current[event[2]])
        else:need(kind in ('climb','center','phase'),'known unchanged source event')
    for r,f in enumerate(c['final']):new(frames[f],r<224)
    return nodes,fixed,warps

def verify(payload,witness):
    raw=json.dumps(payload,sort_keys=True,separators=(',',':')).encode()
    need(hashlib.sha256(raw).hexdigest()==SOURCE_SHA256,'pinned combined source')
    nodes,base_fixed,warps=chronological_nodes(payload)
    props={int(i):projected_chart(chart) for i,chart in witness['proposals'].items()}
    need(all(0<=i<len(nodes) for i in props),'proposal node range')
    need(not set(props)&base_fixed,'fixed main/owned/adapter charts')
    maps={w['op']:tuple(w['G_columns']) for w in payload['canonical']['warps']}
    signed_maps=dict(maps);signed_maps.update({-op:inverse(g) for op,g in maps.items()})
    grouped=defaultdict(list)
    for w in warps:
        a,b=w['input'],w['output']
        need(image(signed_maps[w['op']],nodes[a])==nodes[b],'original native image')
        grouped[abs(w['op'])].append(w)
    selected=[];lines={};extra_fixed=set();profiles=Counter();tables=[]
    old_cost_tables={(a,b,op,sign):ranks for a,b,op,sign,ranks in witness['tables']}
    for op,occurrences in grouped.items():
        late=[w for w in occurrences if 2<=dimension(nodes[w['input']])<=8]
        need(len(late)==1 and late[0]['op']==op,'one positive nontrivial late occurrence per map')
        chosen=late[0];selected.append([chosen['input'],chosen['output'],op])
        prescribed=set()
        for w in occurrences:
            if w is chosen:continue
            a,b=w['input'],w['output'];extra_fixed.update((a,b))
            need(a not in props and b not in props,'other native occurrence endpoints fixed')
            da,db=dimension(nodes[a]),dimension(nodes[b]);need(da==db,'source native dimensions')
            profiles[da]+=1
            if da==1:
                x=next(v for v in nodes[a] if v);y=next(v for v in nodes[b] if v)
                prescribed.add((x,y) if w['op']>0 else (y,x))
            else:need(da in (0,9),'only zero/full or line constraints outside late occurrence')
        need(len(prescribed)<=1,'single normalized shared prelude line')
        line=next(iter(prescribed)) if prescribed else None
        if line:
            lines[op]=list(line);need(mv(maps[op],line[0])==line[1],'incumbent shared line compatibility')
        a,b=chosen['input'],chosen['output'];left=[nodes[a],props.get(a,nodes[a])];right=[nodes[b],props.get(b,nodes[b])]
        bounds=[];attained=[]
        for i,j in [(0,0),(1,0),(0,1),(1,1)]:
            bound=lower_bound(left[i],right[j],line)
            actual=distance(image(maps[op],left[i]),right[j])
            need(bound==actual,'original shared G attains each independent lower bound')
            bounds.append(bound);attained.append(actual)
        need(bounds[0]==0,'baseline late rank zero')
        if a in props or b in props:
            need(old_cost_tables[a,b,op,1]==bounds,'shared rank table matches full invoice certificate')
        tables.append([a,b,op,bounds])
    need(len(selected)==72 and len(lines)==12,'all 72 late maps and 12 prelude lines')
    need(selected==witness['selected_late_maps'],'selected occurrence inventory')
    need(lines=={int(k):v for k,v in witness['prelude_lines'].items()},'prelude line inventory')
    need(sorted(extra_fixed-base_fixed)==witness['frozen_earlier_warp_nodes'],'other occurrence frozen-node inventory')
    need(witness['excluded_proposals']==[] and witness['changed_native_tables']==[],'no excluded choices or improved native table')
    return {'status':'PASS_INDEPENDENT_SHARED_MAP_EXTENSION','source_sha256':SOURCE_SHA256,
            'native_occurrences':len(warps),'selected_late_maps':len(selected),'four_state_minima':4*len(selected),
            'prelude_lines':len(lines),'other_occurrence_dimensions':{str(k):v for k,v in sorted(profiles.items())},
            'other_native_nodes_fixed':len(extra_fixed),'baseline_fixed_native_nodes':len(extra_fixed&base_fixed),
            'all_original_shared_maps_attain_minima':True,'changed_native_tables':0,
            'late_tables_sha256':hashlib.sha256(json.dumps(tables,separators=(',',':')).encode()).hexdigest(),
            'scope':'Geometric lower bound over all compatible shared G matrices for the declared original/least chart choices. All other native occurrence charts remain fixed; no physical or phase admission and no new kappa.'}

def small_formula_audit():
    cases=maps_total=0
    for n in (1,2,3):
        universe=range(1<<n)
        spaces={span(v for v in range(1,1<<n) if mask>>(v-1)&1) for mask in range(1<<((1<<n)-1))}
        maps=[g for g in itertools.product(range(1,1<<n),repeat=n) if len(span(g))==1<<n]
        maps_total+=len(maps)
        for line in (None,(1,1)):
            eligible=[g for g in maps if line is None or g[0]==1]
            for a in spaces:
                possible={image(g,a) for g in eligible}
                for b in spaces:
                    need(lower_bound(a,b,line)==min(distance(c,b) for c in possible),'small-dimension exhaustive minimum')
                    cases+=1
    need(lower_bound(span([1]),span([2]),(1,1))==2,'equal-dimension incompatible line costs rank two')
    return {'dimensions':[1,2,3],'exact_minima':cases,'invertible_maps':maps_total,'wrong_line_rank_two_control':True}

def controls(payload,witness):
    result=[]
    def reject(name,changed,expected):
        try:verify(payload,changed)
        except ValueError as exc:
            need(expected in str(exc),'unexpected control rejection: '+str(exc));result.append(name)
        else:raise ValueError('accepted corruption: '+name)
    bad=copy.deepcopy(witness);first=next(iter(bad['prelude_lines']));bad['prelude_lines'][first][1]^=1
    reject('wrong prelude line',bad,'prelude line inventory')
    bad=copy.deepcopy(witness);bad['selected_late_maps'][0][2]*=-1
    reject('wrong selected operator sign',bad,'selected occurrence inventory')
    bad=copy.deepcopy(witness);bad['frozen_earlier_warp_nodes']=bad['frozen_earlier_warp_nodes'][1:]
    reject('omitted frozen native endpoint',bad,'other occurrence frozen-node inventory')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--word',type=Path,required=True);p.add_argument('--witness',type=Path,required=True)
    p.add_argument('--output',type=Path);p.add_argument('--self-test',action='store_true')
    args=p.parse_args();raw=args.word.read_bytes();payload=json.loads(gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw)
    witness=json.loads(args.witness.read_bytes());result=verify(payload,witness)
    result['small_formula_audit']=small_formula_audit()
    if args.self_test:result['negative_controls']=controls(payload,witness)
    if args.output:args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
