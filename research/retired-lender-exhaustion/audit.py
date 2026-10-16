"""Independent necessary-condition census using explicit GF(2)^9 sets.

No predecessor imports. The source-native alias construction is credited to
PR2559/2526 and their retained dirty-borrow lineage; this checks exhaustion.
"""
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FULL = frozenset(range(512))
FULL_BASIS = [256,128,64,32,16,8,4,2,1]


def need(ok, message):
    if not ok: raise ValueError(message)


def span(vectors):
    out = {0}
    for x in vectors:
        need(type(x) is int and 0 < x < 512, 'invalid frame vector')
        out |= {y ^ x for y in tuple(out)}
    return frozenset(out)


def dimension(space):
    need(len(space) > 0 and len(space) & (len(space)-1) == 0, 'space size')
    return len(space).bit_length()-1


def registers(event):
    need(event[0] in ('add','scale','warp'), 'opcode')
    return event[1:3] if event[0] == 'add' else event[1:2]


def load():
    for row in json.loads((HERE/'VENDOR.json').read_text())['files']:
        raw = (HERE/row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256 '+row['path'])
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'], 'source blob')
    return {f'{n}-{tag}':json.loads(gzip.decompress((HERE/f'predecessor/PR{n}-{tag}.json.gz').read_bytes()))
            for n in (2526,2559) for tag in ('base','extra')}


def inspect(word):
    need((word['report']['v'],word['report']['h'],word['report']['R']) == (112,9,480), 'geometry')
    live = set(range(704))-set(word['removed'])
    initial = {r:span([word['ports'][r]] if r < 112 else word['start_extra'].get(str(r),[])) for r in live}
    terminal = {r:(span(word['helper_final'][str(r)]) if str(r) in word['helper_final'] else
                   frozenset(x for x in range(512) if (x & word['ports'][r-112]).bit_count()%2 == 0)
                   if 112 <= r < 224 else FULL) for r in live}
    current = dict(initial)
    uses = {r:[] for r in live}
    early = {r for section in ('precondition','compensation','cut') for e in word[section] for r in registers(e)}
    restored = {r-704 for e in word['cleanup'] for r in registers(e) if r >= 704}
    paid = Counter()
    def climb(r,space):
        need(r in live and current[r] <= space, 'nonmonotone frame')
        delta = dimension(space)-dimension(current[r])
        if delta: paid[delta] += 1
        current[r] = space
    def scalar(e,t):
        space = span(e[-1])
        for r in registers(e):
            climb(r,space); uses[r].append((t,dimension(space)))
    for i,e in enumerate(word['A']):
        if e[0] == 'warp':
            r = e[1]
            need(current[r] == span(e[3]), 'prelude from-frame')
            need(dimension(span(e[3])) == dimension(span(e[4])), 'prelude dimension preservation')
            current[r] = span(e[4]); uses[r].append((2*i+1,dimension(current[r])))
        else: scalar(e,2*i+1)
    levels = {int(t):span(v) for t,v in word['target_levels'].items()}
    for r,vectors in zip(word['centers'],word['center_frames']):
        space = span(vectors)
        need(current[r] == space, 'centre entrance')
        targets = {levels.get(e[1]-112,frozenset({0})) for e in word['cut'] if e[2] == r}
        for target in sorted(targets,key=lambda x:-len(x)):
            need(target <= space, 'centre nesting')
            delta = dimension(space)-dimension(target)
            if delta: paid[delta] += 1
            space = target
    base = 2*len(word['A'])
    warp_users = {r[1] for r in word['warps']}
    for i in range(len(word['B'])+1):
        for position,r,columns,source,dest in word['warps']:
            if position == i:
                need(current[r] == span(source), 'B warp from-frame')
                need(dimension(span(source)) == dimension(span(dest)), 'warp dimension preservation')
                current[r] = span(dest)
                uses[r].append((base+2*i,dimension(current[r])))
        if i < len(word['B']): scalar(word['B'][i],base+2*i+1)
    restore_start = base+2*(len(word['B'])+1)
    for i,e in enumerate(word['restore']): scalar(e,restore_start+i)
    retirement = dict(current)
    helpers = [r for r in sorted(live) if r >= 224 and r not in word['centers'] and r not in early
               and r not in restored and str(r) not in word['helper_final'] and r not in warp_users
               and uses[r] and base <= uses[r][0][0] < restore_start]
    lenders = [r for r in sorted(live) if not 112 <= r < 224 and r not in word['centers']]
    rejected = Counter(); pairs = []
    for h in helpers:
        first,entrance = uses[h][0]
        for lender in lenders:
            if lender == h: rejected['same role'] += 1; continue
            if uses[lender] and uses[lender][-1][0] >= first: rejected['not retired'] += 1; continue
            if dimension(retirement[lender]) > entrance: rejected['entrance capacity'] += 1; continue
            if uses[h][-1][1] > dimension(terminal[lender]): rejected['terminal capacity'] += 1; continue
            pairs.append([h,lender])
    for r in sorted(live): climb(r,terminal[r])
    widths = Counter(dimension(terminal[r])-dimension(initial[r]) for r in live if r >= 224)
    need({str(k):v for k,v in sorted(paid.items())} == word['report']['local_profile'], 'literal paid profile')
    need({str(k):v for k,v in sorted(widths.items())} == word['report']['width_inventory'], 'literal width inventory')
    return dict(pairs=pairs,helpers=helpers,lenders=lenders,rejections=dict(sorted(rejected.items())),
                uses=uses,retirement=retirement,profile=dict(sorted(paid.items())),widths=dict(sorted(widths.items())),base=base)


def check_edit(before,after):
    """Bind the attaining word to only the two declared aliases and cleanup."""
    expected = deepcopy(before)
    extra = after['warps'][len(before['warps']):]
    need(len(extra) == 2, 'two new warps')
    substitutions = [(606,68),(653,49)]
    for (helper,lender),record in zip(substitutions,extra):
        position,owner,columns,source,dest = record
        need(owner == lender, 'declared lender')
        first = next(i for i,e in enumerate(expected['B']) if helper in registers(e))
        need(position == first, 'first use cut')
        def apply(x):
            out = 0
            for bit,column in enumerate(columns):
                if x>>bit & 1: out ^= column
            return out
        need(len(columns) == 9 and {apply(x) for x in range(512)} == set(range(512)), 'invertible warp')
        need({apply(x) for x in span(source)} == span(dest), 'warp source image')
        need(span(dest) <= span(expected['B'][first][-1]), 'warp destination entrance')
        for section in ('B','restore'):
            for e in expected[section]:
                for j in range(1,3 if e[0] == 'add' else 2):
                    if e[j] == helper: e[j] = lender
        expected['warps'].append(record)
        expected['removed'].append(helper)
        del expected['start_extra'][str(helper)]
    restored = {r-704 for e in before['cleanup'] for r in registers(e) if r >= 704}
    owner = lambda r:r+704 if r in restored else r
    events = list(expected['A'][expected['prelude_events']:])
    for i in range(len(expected['B'])+1):
        events.extend(['warp',r[1],j+1] for j,r in enumerate(expected['warps']) if r[0] == i)
        if i < len(expected['B']): events.append(expected['B'][i])
    events.extend(expected['restore'])
    cleanup = []
    for e in reversed(events):
        if e[0] != 'warp' and 112 <= e[1] < 224: continue
        if e[0] == 'warp': cleanup.append(['warp',owner(e[1]),-e[2],FULL_BASIS])
        elif e[0] == 'add': cleanup.append(['add',owner(e[1]),owner(e[2]),-e[3],e[4],FULL_BASIS])
        else: cleanup.append(['scale',owner(e[1]),e[3],e[2],FULL_BASIS])
    expected['cleanup'] = cleanup
    expected['report'] = deepcopy(after['report'])  # Independently priced by inspect.
    need(expected == after, 'complete declared edit and inverse cleanup')
    return extra
