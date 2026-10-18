"""Reverse adjoints with exact dyadic integers, independently parsing both words."""
import hashlib
import json
from collections import Counter


def need(ok,why):
    if not ok:
        raise ValueError(why)


def check(base,word):
    # Width is only an arithmetic representation. Every division is checked;
    # this is exact dyadic arithmetic, not reduction modulo a prime or rounding.
    scale=1<<64
    original=list(base['initial_frames'])
    names=original+[f'L{k}' for k in range(word['lifetimes'])]
    columns={name:{name:scale} for name in names}
    events=[]
    position=0
    for op in word['ops'][1:]:
        tag=op[0]
        if tag in ('read','write'):
            cut=op[4]
            need(position<=cut<=len(base['program']),'independent cut')
            events.extend(base['program'][position:cut]);position=cut
        if tag=='read':events.append(['add',f'L{op[1]}',f'X{op[2]}',op[3]])
        elif tag=='write':events.append(['add',f'Y{op[1]}',f'L{op[2]}',op[3]])
        elif tag=='shear':events.append(['add',f'L{op[1]}',f'L{op[2]}',op[3]])
        elif tag=='move':events.append(['transport'])
        else:raise ValueError('independent unknown event')
    events.extend(base['program'][position:])
    updates=0
    for op in reversed(events):
        kind=op[0]
        if kind=='add':
            target,source=op[1:3]
            raw=str(op[3]).split('/')
            numerator=int(raw[0]);denominator=int(raw[1]) if len(raw)==2 else 1
            for output,value in columns[target].items():
                value*=numerator
                need(value%denominator==0,'exact dyadic divisibility')
                updated=columns[source].get(output,0)+value//denominator
                if updated:columns[source][output]=updated
                else:columns[source].pop(output,None)
            updates+=1
        elif kind=='erase':
            need(op[1] not in columns,'reverse private birth')
            columns[op[1]]={}
        elif kind=='copy':
            for output,value in columns[op[1]].items():
                changed=columns[op[2]].get(output,0)+value
                if changed:columns[op[2]][output]=changed
                else:columns[op[2]].pop(output,None)
            columns[op[1]]={}
        elif kind=='zero':
            del columns[op[1]]
        elif kind!='transport':
            raise ValueError('independent unsupported event')
    transcript=hashlib.sha256()
    nonzero=0
    for name in names:
        wanted={name:scale}
        if name.startswith('X'):wanted['Y'+name[1:]]=scale
        need(columns[name]==wanted,'independent full adjoint endpoint: '+name)
        row=[name,[[k,str(v//scale)] for k,v in sorted(columns[name].items())]]
        transcript.update((json.dumps(row,separators=(',',':'))+'\n').encode())
        nonzero+=len(wanted)
    return {'boundary_inputs':len(names),'matrix_coefficients':len(names)**2,'nonzero':nonzero,
            'reverse_scalar_updates':updates,'column_sha256':transcript.hexdigest(),
            'method':'Reverse event adjoints; exact 64-place dyadic integers with divisibility checks; no primary or predecessor imports'}


def check_floor(base,records):
    def space(vectors):
        values={0}
        for v in vectors:
            values.update(x^v for x in tuple(values))
        return frozenset(values)
    paths={s:[space(base['initial_frames'][f'X{s}'])] for s in range(104)}
    for op in base['program']:
        if op[0]=='transport' and op[1].startswith('X'):
            paths[int(op[1][1:])].append(space(op[3]))
    targets=[space(base['final_frames'][f'Y{t}']) for t in range(104)]
    need(all(len(H)==256 for H in targets),'independent target hyperplanes')
    source_lines={fs[0] for fs in paths.values()}
    target_paths=[space(base['initial_frames'][f'Y{t}']) for t in range(104)]
    target_paths += [space(op[3]) for op in base['program'] if op[0]=='transport' and op[1].startswith('Y')]
    need(len(source_lines)==104 and not any(v in source_lines for v in target_paths),'no direct source-line target delivery')
    for t,H in enumerate(targets):
        frames=[space(base['initial_frames'][f'Y{t}'])]+[space(op[3]) for op in base['program'] if op[0]=='transport' and op[1]==f'Y{t}']
        need(all(v<=H for v in frames),'independent target path containment')
    need([r['source'] for r in records]==list(range(104)),'complete source witness')
    distribution=Counter();later_count=0
    for row in records:
        s=row['source'];line=paths[s][0]
        need(all(line<=v for v in paths[s]),'independent source line containment')
        demand=[t for t,H in enumerate(targets) if line<=H]
        later=[t for t in demand if any(len(f)>2 and f<=targets[t] for f in paths[s])]
        forced=[t for t in demand if t not in later]
        need(row['later_targets']==later and row['forced_targets']==forced,'complete later-read classification')
        intersection=set(range(512))
        for t in forced:intersection.intersection_update(targets[t])
        need(intersection==line and sorted(intersection)==row['intersection'],'independent forced-line intersection')
        a,b=map(space,row['cover_planes'])
        need(len(a)==len(b)==4 and line<=a and line<=b,'cover planes')
        need(all(a<=targets[t] or b<=targets[t] for t in demand),'two-plane cover all demands')
        distribution[len(forced)]+=1;later_count+=len(later)
    return {'sources':len(records),'later_read_entries':later_count,'forced_count_distribution':dict(sorted(distribution.items())),
            'source_lines_distinct':True,'target_source_line_coincidences':0,
            'line_departure_floor':2*len(records),'method':'Literal F2 spans and full target intersections; no rational-row or RREF implementation imports'}
