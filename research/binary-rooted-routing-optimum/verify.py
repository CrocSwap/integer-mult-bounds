"""Check the frozen binary transfer and the fixed-port routing optimum."""
from fractions import Fraction as F
from hashlib import sha1, sha256
from itertools import combinations
from pathlib import Path
import argparse
import gzip
import json
import time

HERE = Path(__file__).resolve().parent


def need(value, label):
    if not value:
        raise ValueError(label)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def bits(value):
    while value:
        low = value & -value
        yield low.bit_length()-1
        value ^= low


def xor(values):
    result = 0
    for value in values:
        result ^= value
    return result


def rank(rows):
    rows = [list(map(F, row)) for row in rows]
    r = 0
    for c in range(8):
        pivot = next((i for i in range(r, len(rows)) if rows[i][c]), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        scale = rows[r][c]
        rows[r] = [v/scale for v in rows[r]]
        for i in range(r+1, len(rows)):
            scale = rows[i][c]
            rows[i] = [v-scale*w for v,w in zip(rows[i], rows[r], strict=True)]
        r += 1
    return r


def literal(word, reverse=False, omit=None):
    n = word['public']
    origin, final = (word['final'], word['start']) if reverse else (word['start'], word['final'])
    state = {j:1<<j for j in range(n)}
    chart = dict(enumerate(origin))
    dirty = 0
    steps = list(enumerate(word['program']))
    for clock, (op, dst, *args) in reversed(steps) if reverse else steps:
        if clock == omit:
            continue
        if op in ('INIT', 'CLEAR'):
            opening = (op == 'CLEAR') if reverse else (op == 'INIT')
            need(dst >= n, 'private lifetime')
            if opening:
                need(dst not in state, 'new private field')
                state[dst], chart[dst] = 0, args[0]
            else:
                need(dst in state and chart[dst] == args[0], 'private erasure chart')
                dirty += bool(state[dst])
                del state[dst], chart[dst]
        elif op == 'ADD':
            src, location = args
            need(src != dst and chart[src] == chart[dst] == location, 'local ADD')
            if reverse:
                state[src] ^= state[dst]
            else:
                state[dst] ^= state[src]
        elif op == 'SWAP':
            src, = args
            state[src], state[dst] = state[dst], state[src]
            chart[src], chart[dst] = chart[dst], chart[src]
        else:
            need(op == 'MOVE', 'known operation')
            a,b = args[::-1] if reverse else args
            need(chart[dst] == a, 'paid chronology')
            chart[dst] = b
    need(chart == dict(enumerate(final)) and set(state) == set(range(n)), 'complete field retirement')
    return [state[i] for i in range(n)], dirty


def graph(word):
    n = word['public']
    state = {j:1<<j for j in range(n)}
    rows, routes = {}, {}
    for op, dst, *args in word['program']:
        if op == 'INIT':
            state[dst] = 0
        elif op == 'CLEAR':
            del state[dst]
        elif op == 'ADD':
            state[dst] ^= state[args[0]]
        elif op == 'SWAP':
            src, = args
            state[src], state[dst] = state[dst], state[src]
        else:
            need(op == 'MOVE', 'known graph operation')
            k = n+len(routes)
            routes[k], rows[k] = tuple(args), state[dst]
            state[dst] = 1<<k
    rows.update({~i:state[i] for i in range(n)})
    transpose = dict.fromkeys(rows, 0)
    for target, row in rows.items():
        for donor in bits(row):
            transpose[~donor if donor<n else donor] ^= 1<<(~target if target<0 else target)
    return {k:(b,a) for k,(a,b) in routes.items()}, transpose


def expand(n, routes, rows):
    values = {i:1<<i for i in range(n)}
    left = set(routes)
    order = []
    while left:
        ready = sorted(j for j in left if all(k in values for k in bits(rows[j])))
        need(ready, 'acyclic packet dependency')
        for j in ready:
            values[j] = xor(values[k] for k in bits(rows[j]))
            left.remove(j)
            order.append(j)
    output = [xor(values[k] for k in bits(rows[~i])) for i in range(n)]
    return output, values, order


def connected(edges):
    seen = {0}
    for _ in range(4):
        seen |= {v for a,b in edges for u,v in ((a,b),(b,a)) if u in seen}
    return len(seen) == 4


def networks(word):
    ports = [0,509,390,517]
    bases = [word['frames'][str(i)]['B'] for i in ports]
    dimensions = [rank(rows) for rows in bases]
    need(dimensions == [0,4,6,7], 'actual four port ranks')
    for a,b in combinations(range(4),2):
        need(rank(bases[a]+bases[b]) == dimensions[b], 'actual rational nested subspaces')
    edges = list(combinations(range(4),2))
    chain = {(0,1),(1,2),(2,3)}
    trees, graphs = [], []
    for mask in range(64):
        selected = [e for i,e in enumerate(edges) if mask>>i&1]
        if not connected(selected):
            continue
        weights = sorted(dimensions[b]-dimensions[a] for a,b in selected)
        graphs.append(selected)
        if len(selected) == 3:
            need(all(a<=b for a,b in zip([1,2,4],weights,strict=True)), 'tree rank dominance')
            need((weights == [1,2,4]) == (set(selected) == chain), 'unique minimum tree')
            trees.append(dict(edges=list(map(list,selected)), ranks=weights))
    need(len(trees) == 16 and len(graphs) == 38, 'complete four-vertex graph census')
    for selected in graphs:
        need(any(set(map(tuple,t['edges'])) <= set(selected) for t in trees), 'every connected graph contains a checked tree')
    return dict(ports=ports, dimensions=dimensions, trees=trees, connected_graphs=len(graphs), all_graphs=64)


def reject(name, action):
    try:
        action()
    except ValueError as error:
        return dict(control=name, rejection=str(error))
    raise ValueError('control passed: '+name)


def run():
    pins = read(HERE/'SOURCE-PINS.json')['sources']
    for p in pins:
        raw = (HERE/p['retained']).read_bytes()
        need(sha256(raw).hexdigest() == p['sha256'] and sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == p['git_blob'], 'retained bytes')
    word = read(HERE/'retained/binary/WORD.json.gz')
    canonical = sha256(json.dumps(word,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    need(canonical == 'd3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d', 'frozen word')
    n = word['public']
    need(n == 680, 'all independent owners')
    expected = [1<<i ^ (1<<(i-111) if 111<=i<222 else 0) for i in range(n)]
    adjoint = [1<<i ^ (1<<(i+111) if i<111 else 0) for i in range(n)]
    forward, dirty = literal(word)
    reverse, dirty_reverse = literal(word,True)
    need(forward == expected and reverse == adjoint, 'both complete scalar operators')
    need(dirty == dirty_reverse == 3554, 'all dirty private retirements')
    routes, rows = graph(word)
    output, values, order = expand(n,routes,rows)
    need(output == reverse, 'literal and packet adjoints agree')
    source = read(HERE/'retained/binary/intermediate/OWNER411.json')['components'][0]
    desired = sum(1<<i for i in source['rows']['2329']['desired_inputs'])
    roots = [j for j,r in routes.items() if r==(0,509) and values[j]==desired]
    need(len(roots)==1, 'unique source-bound exterior root')
    root, = roots
    middle, = [j for j,r in routes.items() if r==(509,390) and rows[j]==1<<root]
    last, = [j for j,r in routes.items() if r==(390,517) and rows[j]==1<<middle]
    need(rows[root].bit_count()==55 and desired.bit_count()==55, 'actual root direct and input supports')
    bridge, = [j for j,r in routes.items() if r==(1,509) and rows[j]==1<<411]
    need(rows[~411] == 1<<bridge and not desired>>411&1, 'independent helper bridge')
    need(rank(word['frames']['1']['B']) == 8 and rank(word['frames']['509']['B']) == 4,
         'independent bridge grade four')
    influence = dict.fromkeys(values,0)
    for i in range(n):
        for j in bits(rows[~i]):
            influence[j] ^= 1<<i
    for k in reversed(order):
        for j in bits(rows[k]):
            influence[j] ^= influence[k]
    need(influence[root] != 0 and all(values[j] != 0 for j in bits(rows[root])), 'every root term is essential')
    donor = min(bits(rows[root]))
    changed = rows | {root:rows[root] ^ 1<<donor}
    damaged,_,_ = expand(n,routes,changed)
    fault = [a^b for a,b in zip(damaged,output,strict=True)]
    need(fault == [values[donor] if influence[root]>>i&1 else 0 for i in range(n)], 'exact rank-one root fault')
    need(any(fault), 'nonzero root fault')
    zeroed,_,_ = expand(n,routes,rows | {root:0})
    need(zeroed != output, 'root-zero failure')
    unbridged,_,_ = expand(n,routes,rows | {bridge:0})
    need([a^b for a,b in zip(unbridged,output,strict=True)] == [1<<411 if i==411 else 0 for i in range(n)], 'isolated helper fault')
    cycle = rows | {root:1<<middle,middle:1<<last,last:1<<root}
    controls = [reject('unrooted equal-value cycle',lambda:expand(n,routes,cycle)),
                reject('missing final private CLEAR',lambda:literal(word,omit=len(word['program'])-1))]
    geometry = networks(word)
    changed_word = json.loads(json.dumps(word))
    changed_word['frames']['509']['B'] = changed_word['frames']['390']['B']
    controls.append(reject('changed root-port subspace',lambda:networks(changed_word)))
    return dict(source_files=len(pins),word_sha256=canonical,coefficients_each_orientation=n*n,
                dirty_retirements_each_orientation=dirty,paid_packets=len(routes),
                actual_packet_chain=[root,middle,last],independent_bridge=bridge,
                root_input_support=list(bits(desired)),root_direct_donors=list(bits(rows[root])),
                root_output_support=list(bits(influence[root])),essential_root_terms=55,
                sampled_omission_donor=donor,omission_changed_coefficients=sum(x.bit_count() for x in fault),
                root_zero_changed_coefficients=sum((a^b).bit_count() for a,b in zip(zeroed,output,strict=True)),
                helper_bridge_changed_coefficients=1,routing=geometry,controls=controls,
                optimal_paid_ranks=[1,2,4],owner_bridge_rank=4)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record',action='store_true')
    args=parser.parse_args()
    start=time.monotonic()
    result=run()
    if args.record:
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:
        need(result==read(HERE/'RESULT.json'),'deposited result')
    print('PASS_BINARY_ROOTED_ROUTING_OPTIMUM',result['coefficients_each_orientation'],
          'coefficients each way',len(result['routing']['trees']),'trees',round(time.monotonic()-start,2),'seconds')
