#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bind PR2423's changed R438 placement to exact pending projectors.

Prepared for commdata2338, with substantial OpenAI Codex assistance.
Projector algebra and geometry are credited to PR1307 and its predecessors.
This checker does not import a predecessor acceptance engine.
"""
import argparse
import ast
from collections import Counter, defaultdict
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BIT = 'research/e8-bit-p111-tuned/'
BASE = BIT + 'vendor/pr510/e8-r480-nine-stage/vendor/'
CONTROLLER = BASE + 'e8-r715-eleven-stage-whole/code/global_k.py'
HOSTING = BASE + 'idle-axis-hosting/hosting_core.py'
GEOMETRY = 'research/e8-bit-carrier-skeleton/code/nine/geometry.py'
V, STAGES, REPLICAS, WIDTH = 111, 9, 32, 64
LOW = 255
QPERP = 254


class Rejected(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Rejected(message)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def check_bytes(raw, pin):
    require(sha(raw) == pin['sha256'], 'source SHA256: ' + pin['path'])
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    require(blob == pin['git_blob'], 'source Git blob: ' + pin['path'])


def source_check():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    live = [p for p in pins['files'] if p['usage'] == 'input']
    for p in live:
        check_bytes((ROOT / p['path']).read_bytes(), p)
    for p in pins['vendored_files']:
        check_bytes((HERE / p['path']).read_bytes(), p)
    return pins


def function(path, name):
    """Extract a pinned pure source function, never its module main/imports."""
    nodes = [n for n in ast.parse((ROOT / path).read_text()).body
             if isinstance(n, ast.FunctionDef) and n.name == name]
    require(len(nodes) == 1, 'unique source function')
    ns = {'Counter': Counter, 'defaultdict': defaultdict}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), path, 'exec'), ns)
    return ns[name]


def pending(a, b):
    require(-1 <= a <= b <= 8, 'level range')
    axes = range(1 if a == -1 else 8 + 7*a, 8 + 7*b)
    return sum(1 << i for i in axes)


def chronology():
    levels = [-1]*4
    events, children = [], []

    def advance(pair, target):
        a = levels[pair]
        child = {'kind': 'idle', 'idx': len(children), 'pair': pair,
                 'source_level': a, 'target_level': target,
                 'rank': 7*(target-a), 'mask': pending(a, target)}
        children.append(child)
        events.append(child)
        levels[pair] = target

    for e in function(CONTROLLER, 'recipe')(4):
        events.append(e)
        if e['kind'] == 'local':
            s, p = e['stage'], e['pair']
            require(levels[p] == s-1, 'local source level')
            levels[p] = s
            if 1 <= s <= 6:
                advance((s+1)//2, s)
            if s == 8:
                for pair in range(4):
                    advance(pair, 8)
        elif e['kind'] == 'bridge':
            require(levels[e['src']] == levels[e['dst']], 'bridge levels')
        else:
            require(e['kind'] == 'exchange' and levels == [8]*4, 'final exchange')
    # Compare the geometry producer's literal table, without importing sympy.
    main = next(n for n in ast.parse((ROOT / GEOMETRY).read_text()).body
                if isinstance(n, ast.FunctionDef) and n.name == 'main')
    start = next(i for i, n in enumerate(main.body) if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == 'idle' for t in n.targets))
    nodes = main.body[start:start+3]
    require(len(nodes) == 3 and all(isinstance(n, ast.For) for n in nodes[1:]),
            'geometry table syntax')
    ns = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), GEOMETRY, 'exec'), ns)
    fields = ('pair', 'source_level', 'target_level', 'rank')
    require([[c[k] for k in fields] for c in children] ==
            [[c[k] for k in fields] for c in ns['idle']], 'geometry/controller binding')
    require(len(children) == 10 and len(events) == 29, 'chronology size')
    used = defaultdict(int)
    for c in children:
        require(c['mask'].bit_count() == c['rank'], 'pending rank')
        require(not used[c['pair']] & c['mask'], 'source children disjoint')
        used[c['pair']] |= c['mask']
    windows = {}
    calls = {e['stage']: (i, e['pair']) for i, e in enumerate(events) if e['kind'] == 'local'}
    for c in children:
        end = events.index(c)
        stages = []
        for stage, (begin, pair) in calls.items():
            if begin >= end or pair == c['pair']:
                continue
            touches = any((e['kind'] == 'local' and e['pair'] == c['pair']) or
                          (e['kind'] == 'bridge' and c['pair'] in (e['src'], e['dst']))
                          for e in events[begin+1:end])
            if not touches:
                stages.append(stage)
        windows[c['idx']] = (c['pair'], c['rank'], frozenset(stages))
    return events, children, windows


def expand(selection, children, windows, helpers):
    """Expand queues from the fixed selection; do not use source expand."""
    queues = defaultdict(list)
    seen = set()
    for child, width, stage, count in sorted(selection['stages']):
        require((child, width, stage) not in seen, 'duplicate demand')
        seen.add((child, width, stage))
        require(width == 8 and stage in windows[child][2] and type(count) is int and count > 0,
                'demand window/width')
        queues[child].extend([stage]*count)
    patterns = defaultdict(list)
    for child, widths, count in selection['patterns']:
        require(child in windows and all(w == 8 for w in widths) and count > 0, 'pattern domain')
        patterns[child].append((widths, count))
    next_helper, consumed = Counter(), Counter()
    slots, remainder = [], {}
    for c in children:
        child, copy = c['idx'], 0
        for widths, count in sorted(patterns[child], key=lambda p: (-sum(p[0]), p[0])):
            require(sum(widths) <= c['rank'], 'pattern extent')
            for _ in range(count):
                require(copy < 2*V, 'copy count')
                for offset in range(0, sum(widths), 8):
                    require(consumed[child] < len(queues[child]), 'demand underflow')
                    stage = queues[child][consumed[child]]
                    consumed[child] += 1
                    helper = next_helper[stage]
                    next_helper[stage] += 1
                    slots.append((child, copy, offset, 8, stage, helper))
                remainder[child, copy] = c['rank']-sum(widths)
                copy += 1
        while copy < 2*V:
            remainder[child, copy] = c['rank']
            copy += 1
        require(consumed[child] == len(queues[child]), 'unconsumed demand')
    require(dict(next_helper) == {s: helpers for s in range(STAGES)}, 'helper counts')
    # Independent producer agreement is a control, not the geometric test.
    ys = {(i, tuple(p)): n for i, p, n in selection['patterns']}
    zs = {(i, w, s): n for i, w, s, n in selection['stages']}
    original = function(HOSTING, 'expand')(windows, ys, zs,
                   {s: [(h, 8) for h in range(helpers)] for s in range(STAGES)}, 2*V)
    require(original == (slots, remainder), 'producer slot agreement')
    return slots, remainder


def axes(mask):
    return tuple(i for i in range(WIDTH) if mask >> i & 1)


def factorization(parts, target):
    used = 0
    for part in parts:
        require(part >= 0 and part < 1 << WIDTH, 'factor dimension')
        require(part & LOW in (0, QPERP), 'split q-perp')
        require(not part & used, 'overlapping factors')
        used |= part
    require(used == target, 'wrong pending operator')


def audit(slots, children, windows, helpers):
    by_deadline = defaultdict(list)
    seen = set()
    for child, copy, offset, width, stage, helper in slots:
        require(0 <= child < 10 and 0 <= copy < 2*V and 0 <= helper < helpers, 'slot indices')
        require(stage in windows[child][2] and width == 8, 'slot window/width')
        require((stage, helper) not in seen, 'duplicate helper')
        seen.add((stage, helper))
        axis = axes(children[child]['mask'])
        require(0 <= offset and offset+width <= len(axis), 'slot extent')
        support = sum(1 << i for i in axis[offset:offset+width])
        by_deadline[child, copy].append((support, stage, helper))
    require(seen == {(s, h) for s in range(STAGES) for h in range(helpers)}, 'missing helper')
    remainders, signatures, complement = Counter(), set(), {}
    for c in children:
        for copy in range(2*V):
            parts = [p for p, _, _ in by_deadline[c['idx'], copy]]
            used = 0
            for part in parts:
                require(not used & part, 'overlapping helper slices')
                used |= part
            require(not used & ~c['mask'], 'factor outside pending space')
            rest = c['mask'] ^ used
            factorization(parts+[rest], c['mask'])
            complement[c['idx'], copy] = rest
            remainders[rest.bit_count()] += 1
            signatures.add((c['mask'], tuple(parts+[rest])))
    occupied, multiple = {}, defaultdict(set)
    owner_rows = []
    for rep in range(REPLICAS):
        for (child, copy), pieces in sorted(by_deadline.items()):
            pair = children[child]['pair']
            side, port = divmod(copy, V)
            family = rep*8*V+(2*pair+side)*V+port
            require(divmod(family, 8*V)[0] == rep, 'replica binding')
            for support, stage, helper in pieces:
                require(not occupied.get(family, 0) & support, 'cross-child physical overlap')
                occupied[family] = occupied.get(family, 0) | support
                multiple[family].add(child)
                owner_rows.append((rep, stage, helper, family, child, support))
    require(len({r[:3] for r in owner_rows}) == REPLICAS*STAGES*helpers, 'owner role coverage')
    return {'slots': len(slots), 'physical_helpers': len(owner_rows),
            'deadline_families': REPLICAS*len(children)*2*V,
            'occupied_families': len(occupied),
            'families_with_multiple_children': sum(len(cs)>1 for cs in multiple.values()),
            'qperp_host_occurrences': REPLICAS*sum((p & LOW)==QPERP for ps in by_deadline.values() for p,_,_ in ps),
            'idle_per_replica_including_zero': dict(sorted(remainders.items())),
            'owner_projector_sha256': sha(canonical(owner_rows)),
            'factorization_sha256': sha(canonical(sorted(signatures)))}, signatures, complement


def low_apply(vector, q, enabled):
    """Direct rational 16-coordinate D(K_q) application, no mask-union rule."""
    if not enabled:
        return vector
    diff = [vector[8+i]-vector[i] for i in range(8)]
    dot = sum(q[i]*diff[i] for i in range(8))/Q(4)
    shift = [diff[i]-q[i]*dot for i in range(8)]
    return tuple(vector[i]+shift[i] for i in range(8)) + tuple(vector[8+i]-shift[i] for i in range(8))


def operator_check(lines, signatures):
    columns = 0
    for q in lines:
        require(len(q)==8 and all(type(x) is int for x in q) and sum(x*x for x in q)==4, 'port norm')
        K4 = [[4*(i==j)-q[i]*q[j] for j in range(8)] for i in range(8)]
        require(all(sum(K4[i][k]*K4[k][j] for k in range(8))==4*K4[i][j]
                    for i in range(8) for j in range(8)), 'rational projector')
        require(sum(K4[i][i] for i in range(8))==28, 'q-perp rank seven')
        for target, parts in signatures:
            # The local block is checked directly on all 16 rational basis columns.
            for j in range(16):
                v = tuple(Q(i==j) for i in range(16))
                got = v
                for part in parts:
                    got = low_apply(got, q, bool(part & LOW))
                require(got == low_apply(v, q, bool(target & LOW)), 'local address operator')
            # Each exterior coordinate has a literal two-by-two swap matrix.
            # Check both basis columns via parity of the executed factor list.
            for j in range(8, WIDTH):
                parity = sum((part >> j) & 1 for part in parts) % 2
                require(parity == ((target >> j)&1), 'exterior address operator')
            columns += 2*WIDTH
    return columns


def rank(rows):
    basis = {}
    for row in rows:
        x = list(map(Q, row))
        for pivot, b in sorted(basis.items()):
            v = x[pivot]
            if v:
                x = [a-v*c for a,c in zip(x,b)]
        pivot = next((j for j,v in enumerate(x) if v), None)
        if pivot is not None:
            v = x[pivot]
            basis[pivot] = [a/v for a in x]
    return len(basis)


def word_profile(word):
    require((word['h'],word['v'],word['R'])==(8,V,438), 'R438 word binding')
    dims = [rank([word['lines'][i] for i in f]) for f in word['frames']]
    now = word['start'][:]
    require(len(now)==660 and len(word['final'])==660, 'word arity')
    require(all(dims[f]==0 for f in now[2*V:]), 'helper entry widths')
    hist = Counter()

    def move(reg, frame):
        old = now[reg]
        if frame != old:
            require(set(word['frames'][old]) <= set(word['frames'][frame]), 'nested source frames')
            delta = dims[frame]-dims[old]
            require(delta > 0, 'positive frame increment')
            hist[delta] += 1
            now[reg] = frame

    copies = []
    for section in ('D','A','copy','B','C'):
        if section=='copy':
            copies = [dims[now[h]] for h in word['ret']]
            hist.update(copies)
        else:
            for frame, dst, srcs in word[section]:
                for reg in (dst,*srcs):
                    move(reg,frame)
    for reg,frame in enumerate(word['final']):
        move(reg,frame)
    require(copies==[7]*9, 'COPY charge')
    require(all(dims[f]==8 for f in now[2*V:]), 'helper exit widths')
    return hist


def controls(slots, children, windows, word, signatures, pin):
    names = []

    def reject(name, action, reason):
        try:
            action()
        except Rejected as e:
            require(reason in str(e), 'wrong rejection: '+name+': '+str(e))
            names.append(name)
            return
        raise Rejected('negative control accepted: '+name)

    reject('source_byte_corruption', lambda: check_bytes(b'wrong',pin), 'source SHA256')
    reject('missing_helper', lambda: audit(slots[1:],children,windows,438), 'missing helper')
    reject('duplicate_helper', lambda: audit(slots+[slots[0]],children,windows,438), 'duplicate helper')
    changed = [list(s) for s in slots]
    changed[0][2] += 1
    reject('split_qperp_slice', lambda: audit(changed,children,windows,438), 'split q-perp')
    changed = [list(s) for s in slots]
    changed[0][4] = 8
    reject('stage_outside_window', lambda: audit(changed,children,windows,438), 'slot window')
    target, parts = next(s for s in signatures if any(p.bit_count()==34 for p in s[1]))
    rest = next(p for p in parts if p.bit_count()==34)
    reject('omitted_rank34_remainder', lambda: factorization([p for p in parts if p!=rest],target), 'wrong pending')
    reject('duplicate_rank34_remainder', lambda: factorization(list(parts)+[rest],target), 'overlapping factors')
    # Equal-rank exterior substitution, with no local-chart or timing changes.
    old_axis = min(axes(rest))
    new_axis = next(i for i in range(8,WIDTH) if not target>>i&1)
    altered = rest ^ (1<<old_axis) ^ (1<<new_axis)
    require(altered.bit_count()==rest.bit_count(), 'rank-preserving control setup')
    mutated = tuple(altered if p==rest else p for p in parts)
    reject('equal_rank_wrong_exterior', lambda: operator_check(word['lines'][:1],{(target,mutated)}), 'exterior address')
    # A wrong port preserves rank 7 but changes its physical projector.
    qa = word['lines'][0]
    qb = next(q for q in word['lines'] if q!=qa and q!=[-x for x in qa])
    witness = next(j for j in range(16) if low_apply(tuple(Q(i==j) for i in range(16)),qa,True)
                   != low_apply(tuple(Q(i==j) for i in range(16)),qb,True))
    names.append('equal_rank_wrong_port_operator_witness')
    # Independently dirty replicas are distinguished by family, not projector rank.
    owner = lambda rep,pair,copy: rep*8*V+2*pair*V+copy
    require(owner(0,0,0)!=owner(1,0,0), 'replica separation')
    # A single arbitrary dirty head coordinate at a real child-6 family.
    # Apply the same selected exterior swap to the intended or wrong replica.
    victim = (owner(1,0,0), 22)
    dirty = {(victim[0], 'head', victim[1]): 1}
    def swap_at(family):
        result = dict(dirty)
        h, t = (family,'head',22), (family,'tail',22)
        a, b = result.pop(h,0), result.pop(t,0)
        if b: result[h] = b
        if a: result[t] = a
        return result
    intended = swap_at(owner(1,0,0))
    aliased = swap_at(owner(0,0,0))
    require(intended == {(victim[0],'tail',22):1} and aliased == dirty,
            'replica dirty-state witness')
    names.append('wrong_replica_dirty_basis_witness')
    return names, {'wrong_port_basis_column':witness,'wrong_exterior_axes':[old_axis,new_axis],
                   'replica_basis_witness':list(victim)}


def run():
    pins = source_check()
    receipt = json.loads((HERE/'sources/pr2423-rehost.json').read_text())
    word = json.loads(gzip.decompress((HERE/'sources/pr2423-word.json.gz').read_bytes()))
    _, children, windows = chronology()
    slots, producer_remainders = expand(receipt['placement']['selection'],children,windows,438)
    require(sha(json.dumps(slots,separators=(',',':')).encode()) == receipt['placement']['slot_list_sha256'],
            'exact predecessor placement digest')
    census, signatures, complement = audit(slots,children,windows,438)
    require(all(complement[k].bit_count()==n for k,n in producer_remainders.items()), 'remainder producer binding')
    idle = {str(r):n for r,n in census['idle_per_replica_including_zero'].items() if r}
    require(idle == receipt['placement']['idle_per_replica'], 'candidate remainder invoice')
    count = operator_check(word['lines'],signatures)
    local = word_profile(word)
    require(dict(local)=={1:1322,2:1342,3:79,4:44,5:102,6:11,7:18}, 'changed-word local profile')
    global_hist = Counter({r:STAGES*REPLICAS*n for r,n in local.items()})
    global_hist.update({int(r):REPLICAS*n for r,n in idle.items()})
    require(sum(global_hist.values())==904320 and sum(r*n for r,n in global_hist.items())==1808352,
            'full finite profile charge')
    selected = json.loads((ROOT/(BIT+'data/selection9-p111.json')).read_text())['bit']
    original_slots,_ = expand(selected,children,windows,439)
    original,_,_ = audit(original_slots,children,windows,439)
    require(original['physical_helpers']==126432, 'selected-layout positive control')
    names,witness = controls(slots,children,windows,word,signatures,pins['vendored_files'][0])
    return {'status':'PASS_R438_REHOST_PROJECTORS','predecessor_head':pins['dependency_heads']['2423'],
            'scope':'finite changed-placement projector binding; no new endpoint or supplier admission',
            'census':census, 'distinct_factorizations':len(signatures), 'port_projectors':len(word['lines']),
            'exact_basis_columns':count, 'local_profile':dict(sorted(local.items())),
            'global_profile':dict(sorted(global_hist.items())), 'children':sum(global_hist.values()),
            'rank_mass':sum(r*n for r,n in global_hist.items()), 'deficit':64*28416-1808352,
            'selected_control_helper_occurrences':original['physical_helpers'],
            'controls':names, 'control_witnesses':witness}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',type=Path,help='write a new receipt, exclusively')
    args=parser.parse_args()
    result=run()
    raw=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.write:
        with args.write.open('x') as out:
            out.write(raw)
    else:
        require(json.loads((HERE/'RESULT.json').read_text())==json.loads(raw), 'committed receipt equality')
    print('PASS_R438_REHOST_PROJECTORS helpers=126144 deadlines=71040 ports=111 '
          f"factorizations={result['distinct_factorizations']} controls={len(result['controls'])} no_new_kappa")


if __name__=='__main__':
    main()
