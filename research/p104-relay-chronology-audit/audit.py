"""Independent full chronological rational-row audit; no predecessor imports."""
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations, product
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CHANNEL = ROOT / 'research/p104-native-channel/inputs'


def require(ok, why):
    if not ok:
        raise ValueError(why)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'))+'\n').encode()


def authenticate():
    manifest = json.loads((HERE/'SOURCES.json').read_bytes())
    for row in manifest['files']:
        if row['usage'] == 'input':
            raw = (ROOT/row['path']).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source drift')
    require({r['path'] for r in manifest['vendored_inputs']} == {
        'inputs/WORD.json', 'inputs/relay-README.md', 'inputs/check_p104_relay_construction.py',
        'inputs/WORD-v2.json','inputs/relay-v2-README.md'}, 'required retained inputs')
    for row in manifest['vendored_inputs']:
        raw = (HERE/row['path']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'retained source drift')
        require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'], 'retained Git blob')


def frame(vectors):
    pivots = {}
    for value in vectors:
        require(type(value) is int and 0 < value < 512, 'binary frame label')
        for bit in sorted(pivots, reverse=True):
            if value >> bit & 1:
                value ^= pivots[bit]
        if value:
            bit = value.bit_length()-1
            for other in pivots:
                if pivots[other] >> bit & 1:
                    pivots[other] ^= value
            pivots[bit] = value
    return tuple(pivots[k] for k in sorted(pivots))


def included(small, large):
    for value in small:
        for pivot in reversed(large):
            if value >> (pivot.bit_length()-1) & 1:
                value ^= pivot
        if value:
            return False
    return True


FULL = tuple(1 << k for k in range(9))


def load():
    authenticate()
    return (json.loads((CHANNEL/'LOWRANK-WITNESS.json').read_bytes()),
            json.loads((CHANNEL/'P104-FIXTURE.json').read_bytes()),
            json.loads((HERE/'inputs/WORD-v2.json').read_bytes()))


def correction(fixture):
    # Independent root construction in doubled Cartesian coordinates.
    roots = set()
    for i,j in combinations(range(8),2):
        for sign in (-1,1):
            vector = [0]*8
            vector[i],vector[j] = 2,2*sign
            roots.add(tuple(vector))
    for tail in product((-1,1),repeat=7):
        if sum(x<0 for x in tail)%2 == 0:
            roots.add((1,)+tail)
    record = fixture['section4_explicit_P104']
    removed = {tuple(v) for v in record['F0']+record['C']}
    ports = sorted(roots-removed)
    require(len(roots)==120 and len(ports)==104, 'root reconstruction')
    result = []
    for t,a in enumerate(ports):
        row = {}
        for s,b in enumerate(ports):
            value = Q(int(t==s))-Q(sum(x*y for x,y in zip(a,b)),8)
            if value:
                row[s]=value
        result.append(row)
    return result


def plus(target, coefficient, source):
    require(target is not source, 'distinct ADD registers')
    for key,value in source.items():
        value = target.get(key,Q(0))+coefficient*value
        if value:
            target[key]=value
        else:
            target.pop(key,None)


def trace_digest(rows, names):
    digest=hashlib.sha256()
    nonzero=0
    for name in names:
        terms=[[key,str(value)] for key,value in sorted(rows[name].items())]
        digest.update(canonical([name,terms]))
        nonzero+=len(terms)
    return digest.hexdigest(),nonzero


def replay(base, word, C):
    count=word['lifetimes']
    require(type(count) is int and count>0 and word['ops'][0]==['move_zero_all',count], 'lifetime header')
    names=list(base['initial_frames'])+[f'L{k}' for k in range(count)]
    require(len(names)==len(set(names)), 'unique boundary inputs')
    rows={name:{name:Q(1)} for name in names}
    frames={name:frame(basis) for name,basis in base['initial_frames'].items()}
    frames.update({f'L{k}':() for k in range(count)})
    new_profile,old_profile,operations=Counter(),Counter(),Counter()
    side_cuts=Counter()
    current_cut=0
    private=[]
    private_alive=False
    scalar_updates=0
    maximum_row_support=1

    def add(dst,src,c):
        nonlocal scalar_updates,maximum_row_support
        require(dst in rows and src in rows and frames[dst]==frames[src], 'common-chart ADD')
        plus(rows[dst],Q(c),rows[src])
        scalar_updates+=1
        maximum_row_support=max(maximum_row_support,len(rows[dst]))

    def advance(cut):
        nonlocal current_cut,private_alive
        require(type(cut) is int and current_cut<=cut<=len(base['program']), 'chronological cut range')
        while current_cut<cut:
            op=base['program'][current_cut]
            kind=op[0]
            if kind=='add':
                require(not op[1].startswith('X'), 'immutable X source')
                require(not op[2].startswith('Y'), 'no original target feedback')
                require(frames[op[1]]==frame(op[4]), 'base ADD annotation')
                add(op[1],op[2],op[3])
            elif kind=='transport':
                register,entry,exit_basis,rank=op[1:]
                outgoing=frame(exit_basis)
                require(frames[register]==frame(entry), 'base transport entry')
                require(included(frames[register],outgoing) or included(outgoing,frames[register]), 'base nested transport')
                require(abs(len(outgoing)-len(frames[register]))==rank, 'base transport rank')
                frames[register]=outgoing
                old_profile[rank]+=1
            elif kind=='zero':
                require(op[1]=='C' and not private_alive, 'owned private birth')
                rows['C']={};frames['C']=frame(op[2]);private_alive=True
            elif kind=='copy':
                require(private_alive and op[1]=='C' and not rows['C'] and frames['C']==frame(op[3]), 'owned private copy')
                require(frames[op[2]]==frames['C'], 'copy chart')
                rows['C']=dict(rows[op[2]])
            elif kind=='erase':
                require(private_alive and op[1]=='C' and frames['C']==frame(op[2]), 'owned private erase')
                private.append({'base_event':current_cut,'nonzero':bool(rows['C']), 'support':len(rows['C'])})
                del rows['C'];del frames['C'];private_alive=False
            else:
                raise ValueError('unknown base event')
            current_cut+=1

    for op in word['ops'][1:]:
        kind=op[0]
        operations[kind]+=1
        if kind in ('read','write'):
            require(len(op)==5,'cut-bearing event shape')
            advance(op[4])
            side_cuts[current_cut]+=1
        if kind=='move':
            require(len(op)==3,'move shape')
            name=f'L{op[1]}'
            require(name in frames,'known helper')
            new=frame(op[2]);old=frames[name]
            require(len(new)>len(old) and included(old,new),'strict nested helper move')
            new_profile[len(new)-len(old)]+=1;frames[name]=new
        elif kind=='shear':
            require(len(op)==4,'shear shape')
            add(f'L{op[1]}',f'L{op[2]}',op[3])
        elif kind=='read':
            require(type(op[2]) is int and 0<=op[2]<104,'source index')
            add(f'L{op[1]}',f'X{op[2]}',op[3])
        elif kind=='write':
            require(type(op[1]) is int and 0<=op[1]<104,'target index')
            add(f'Y{op[1]}',f'L{op[2]}',op[3])
        else:
            raise ValueError('unknown relay operation')
    advance(len(base['program']))
    require(not private_alive,'private lifecycle complete')
    for name in names:
        wanted={name:Q(1)}
        if name.startswith('Y'):
            wanted['X'+name[1:]]=Q(1)
        require(rows[name]==wanted,'full combined arbitrary-input endpoint: '+name)
        expected=FULL if name.startswith('L') else frame(base['final_frames'][name])
        require(frames[name]==expected,'full combined endpoint frame')
    require(all(sum(C[t].get(s,Q(0))!=0 for s in range(104))==48 for t in range(104)), 'correction supports')
    digest,nonzero=trace_digest(rows,names)
    return {'boundary_inputs':len(names),'endpoint_coefficients':len(names)**2,'endpoint_nonzero':nonzero,
            'endpoint_sha256':digest,'original_events':len(base['program']), 'relay_events':len(word['ops'])-1,
            'total_events':len(base['program'])+len(word['ops'])-1,'new_helpers':count,
            'relay_operations':dict(sorted(operations.items())),'side_access_cuts':dict(sorted(side_cuts.items())),
            'new_profile':dict(sorted(new_profile.items())),'base_profile':dict(sorted(old_profile.items())),
            'new_rank_mass':sum(k*v for k,v in new_profile.items()),'combined_rank_mass':sum(k*v for k,v in (new_profile+old_profile).items()),
            'private_erasures':private,'scalar_updates':scalar_updates,'max_row_support':maximum_row_support}


def floor_certificate(base,C):
    paths={s:[frame(base['initial_frames'][f'X{s}'])] for s in range(104)}
    for op in base['program']:
        if op[0]=='transport' and op[1].startswith('X'):
            paths[int(op[1][1:])].append(frame(op[3]))
    hyperplanes=[frame(base['final_frames'][f'Y{t}']) for t in range(104)]
    require(all(len(H)==8 for H in hyperplanes),'final target hyperplanes')
    source_lines={path[0] for path in paths.values()}
    require(len(source_lines)==104,'distinct source lines')
    target_path_frames=[frame(base['initial_frames'][f'Y{t}']) for t in range(104)]
    target_path_frames += [frame(op[3]) for op in base['program'] if op[0]=='transport' and op[1].startswith('Y')]
    require(all(f not in source_lines for f in target_path_frames),'no target visit to any source line')
    for t,H in enumerate(hyperplanes):
        target_frames=[frame(base['initial_frames'][f'Y{t}'])]+[frame(op[3]) for op in base['program'] if op[0]=='transport' and op[1]==f'Y{t}']
        require(all(included(v,H) for v in target_frames),'target paths stay inside final hyperplanes')
    records=[]
    for s in range(104):
        line=paths[s][0]
        require(len(line)==1,'one source line')
        require(all(included(line,v) for v in paths[s]),'source paths contain initial line')
        demands=[t for t in range(104) if s in C[t]]
        require(demands==[t for t in range(104) if included(line,hyperplanes[t])], 'root support versus frame geometry')
        later=[t for t in demands if any(len(f)>1 and included(f,hyperplanes[t]) for f in paths[s])]
        forced=[t for t in demands if t not in later]
        intersection=[v for v in range(512) if all(included(frame([v]) if v else (),hyperplanes[t]) for t in forced)]
        require(intersection==[0,line[0]], 'line-only demand intersection')
        # Concrete two-plane cover of ALL demands, independent of the stronger
        # lower-bound witness that uses only line-forced demands.
        planes=sorted({frame([line[0],v]) for v in range(1,512) if v!=line[0]})
        masks=[sum((included(p,hyperplanes[t]))<<j for j,t in enumerate(demands)) for p in planes]
        all_mask=(1<<len(demands))-1
        pair=next(((planes[i],planes[j]) for i in range(len(planes)) for j in range(i+1,len(planes)) if masks[i]|masks[j]==all_mask),None)
        require(pair is not None,'two-plane cover')
        records.append({'source':s,'line':list(line),'forced_targets':forced,'later_targets':later,'intersection':intersection,'cover_planes':pair})
    return records
