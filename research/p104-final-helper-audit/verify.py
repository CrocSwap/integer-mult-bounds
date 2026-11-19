"""Check the final helper split and its rational pulse error space."""
from collections import Counter
from fractions import Fraction as F
from graphlib import TopologicalSorter
from hashlib import sha1, sha256
from pathlib import Path
import argparse
import importlib.util
import json
import time

HERE = Path(__file__).resolve().parent


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


v = module('coefficient_audit7777', HERE/'retained/operator7777/verify.py')
need, read, add, terms = v.need, v.read, v.add, v.terms


def digest(value):
    return sha256(v.encoded(value)).hexdigest()


def pack(graph, rows):
    deps = {k: sorted(j for j in row if j >= 0) for k, row in sorted(rows.items())}
    return dict(graph, forms=[[k, terms(row)] for k, row in sorted(rows.items())],
                schedule=list(TopologicalSorter(deps).static_order()))


def reverse_graph(graph, rows):
    first, n = graph['first_output'], len(graph['initial'])
    def reverse(k):
        return first + ~k if k < 0 else ~(k-first) if k >= first else k
    result = {k:{} for k, _, _ in graph['moves']}
    result.update({first+i:{} for i in range(n)})
    for k, row in rows.items():
        for j, q in row.items():
            result[reverse(j)][reverse(k)] = q
    return pack(dict(graph, initial=graph['final'], final=graph['initial'],
                     moves=[[k,b,a] for k,a,b in graph['moves']]), result), result


class Network:
    def __init__(self, first_output, initial, final, moves, forms):
        self.first_output, self.initial, self.final = first_output, initial, final
        self.moves, self.forms = moves, forms


def recover(graph, rows, event):
    """Undo the terminal change, pulse and input map, in this order."""
    first, fresh, h = graph['first_output'], len(graph['initial'])-1, event['role']
    need((h, fresh) == (1164, 1278), 'named owner pair')
    old = {k:r.copy() for k,r in rows.items()}
    old[first+h] = add({j:-q/F(4) for j,q in rows[first+fresh].items()}, rows[first+1166], -F(1,4))
    old[first+1166] = {j:-q for j,q in rows[first+fresh].items()}
    del old[first+fresh]
    calibration = {j:F(q) for j,q in event['calibration']}
    need(all(j >= 0 for j in calibration), 'calibration has only paid returns')
    for k, literal in event['pulse']:
        q = F(literal)
        add(old[k], {~fresh:F(1)}, -q/8)
        add(old[k], calibration, q/8)
    p = {i:F(q) for i,q in event['source_covector']}
    d = {i:F(q) for i,q in event['source_direction']}
    restored = {}
    for k,row in old.items():
        result = {j:q for j,q in row.items() if j >= 0}
        for j,q in row.items():
            if j >= 0:
                continue
            i = ~j
            need(i < fresh, 'fresh input removed')
            if i == h:
                add(result, {~t:a for t,a in p.items()}, q)
            else:
                add(result, {j:F(1)}, q)
                if i in d:
                    add(result, {~h:F(1)}, -q*d[i]/d[h])
        restored[k] = result
    final = graph['final'][:-1]
    final[h] = event['return_chart']
    return pack(dict(graph, initial=graph['initial'][:-1], final=final), restored), restored


def expected(layout, n):
    result = [{i:F(1)} for i in range(n)]
    mains = set()
    for i,x in enumerate(layout['live']):
        y = x+112
        mains.update((x,y))
        if i in layout['hosted']['Dports']:
            result[y][x] = F(1)
        else:
            result[x][y] = F(-1)
            result[y] = {x:F(1,2), y:F(1,2)}
    for x,y in zip(layout['hosted']['X2'],layout['hosted']['Y2'],strict=True):
        result[x][y] = F(-1)
        mains.update((x,y))
    need(len(mains) == 400, 'all main ports')
    return result, mains


def construct(before, event):
    """Apply the stated input substitution and terminal projection."""
    moves, old = v.unpack(before)
    h, fresh, first = event['role'], len(before['initial']), before['first_output']
    d, p, r, k = [{i:F(q) for i,q in event[name]} for name in
                  ('source_direction','source_covector','return_direction','return_covector')]
    pd, kr = v.dot(p,d), v.dot(k,r)
    multiplier = {~i:-q/pd for i,q in p.items() if i != h}
    multiplier[~h] = 1/pd
    def substitute(row):
        result = {j:q for j,q in row.items() if j != ~h}
        coefficient = sum(row.get(~i,0)*q for i,q in d.items())
        return add(result,multiplier,coefficient)
    rows = {j:substitute(row) for j,row in old.items()}
    readout = substitute({i:F(q) for i,q in event['readout']})
    calibration = substitute({i:F(q) for i,q in event['calibration']})
    excitation = add({~fresh:1/kr},calibration,-1/kr)
    for j,q in event['pulse']:
        add(rows[j],excitation,F(q))
    returned = {}
    for i,q in k.items():
        add(returned,rows[first+i],q)
    pivot = rows[first+h]
    for i,q in r.items():
        if i != h:
            add(rows[first+i],pivot,-q/r[h])
    rows[first+h], rows[first+fresh] = readout, returned
    final = before['final']+[event['return_chart']]
    final[h] = event['split_chart']
    graph = pack(dict(before,initial=before['initial']+[event['split_chart']],final=final),rows)
    return graph


def run():
    pins = read(HERE/'SOURCE-PINS.json')['sources']
    for pin in pins:
        raw = (HERE/pin['retained']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'] and
             sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'], 'exact source bytes')
    source = HERE/'retained/source7781/complex'
    pure, original_layout, journal = [read(source/f) for f in ('WORD.json.gz','LAYOUT.json.gz','FINAL-BIRTH.json')]
    overlay = module('overlay7781',source/'overlay.py')
    original = overlay.apply(pure,read(source/'OVERLAY.json.gz'))
    need(digest(original) == journal['source']['graph_sha256'], 'published pre-split overlay')
    graph = construct(original,journal['event'])
    layout = dict(original_layout,public=original_layout['public']+1,
                  source_labels=original_layout['source_labels']+[journal['owners']['new_label']])
    need(digest(graph) == journal['result']['graph_sha256'] and digest(layout) == journal['result']['layout_sha256'], 'exact final objects')
    moves, rows = v.unpack(graph)
    event, first, n = journal['event'], graph['first_output'], len(graph['initial'])
    before, old = recover(graph, rows, event)
    need(digest(before) == journal['source']['graph_sha256'], 'independently recovered preimage')
    need(v.encoded(before) == v.encoded(original), 'exact recovered overlay')
    before_layout = dict(layout, public=n-1, source_labels=layout['source_labels'][:-1])
    need(digest(before_layout) == journal['source']['layout_sha256'], 'prior layout')
    need(digest(graph['moves']) == journal['paid_manifest_sha256'] and len(moves) == 5714, 'identical paid table')
    algebra = module('split7776', HERE/'retained/algebra7776/birth_event.py')
    original = Network(first,before['initial'],before['final'],moves,old)
    roundtrip = algebra.apply_split(original,event)
    need(roundtrip.forms == rows and roundtrip.initial == graph['initial'] and roundtrip.final == graph['final'], 'retained forward round trip')
    changes = [[k,terms(old[k]) if k in old else None,terms(rows[k])] for k in sorted(rows) if old.get(k) != rows[k]]
    need(digest(changes) == journal['changed_row_delta_sha256'], 'literal delta receipt')
    want, mains = expected(layout,n)
    products = 0
    for label, g, r, target in [('before',before,old,want[:-1]),('after',graph,rows,want)]:
        values, count = v.expand(g,moves,r)
        products += count
        need(all(v.vector(values[first+i]) == row for i,row in enumerate(target)), label+' complete operator')
        if label == 'after':
            calibration_row, readout_row = {}, {}
            for field,destination in [('calibration',calibration_row),('readout',readout_row)]:
                for node,q in event[field]:
                    add(destination,v.vector(values[node]),F(q))
            p = {i:F(q) for i,q in event['source_covector']}
            expected_calibration = {i:q/F(757680) for i,q in p.items() if i != 1164}
            add(expected_calibration,{1164:F(1)},-F(1,757680))
            add(expected_calibration,{1166:F(1)},F(-1))
            need(calibration_row == expected_calibration and readout_row == {1164:F(1)}, 'exact local probes')
        del values
    adjoint, adjoint_rows = reverse_graph(graph,rows)
    transposed = [{} for _ in want]
    for i,row in enumerate(want):
        for j,q in row.items():
            transposed[j][i] = q
    values, count = v.expand(adjoint, {k:(b,a) for k,(a,b) in moves.items()},adjoint_rows)
    products += count
    need(all(v.vector(values[first+i]) == row for i,row in enumerate(transposed)), 'complete adjoint operator')
    del values
    # Each independent injection response is computed on the submitted graph.
    pulses = [(k,F(q)) for k,q in event['pulse']]
    response = [v.scalar(graph,moves,rows,{},[(k,q/8)]) for k,q in pulses]
    calibration = {k:F(q) for k,q in event['calibration']}
    readout = {k:F(q) for k,q in event['readout']}
    need(all(sum(q*a[k] for k,q in calibration.items()) == 0 and
             sum(q*a[k] for k,q in readout.items()) == 0 for a in response), 'each pulse is invisible to both local probes')
    columns = [{i:a[first+i] for i in range(n) if a[first+i]} for a in response]
    minor = [[c.get(i,F(0)) for c in columns] for i in [17,38,1278]]
    need(minor == [[-F(5,2),0,F(5,2)],[F(5,2),-F(5,2),0],[0,F(1,2),F(1,2)]], 'rank-three response minor')
    total_response = {}
    for column in columns:
        add(total_response,column,F(1))
    need(total_response == {1278:F(1)}, 'complete pulse has only the fresh return')
    basis = {}
    for column in columns:
        reduced = v.reduced(column,basis)
        if reduced:
            pivot = max(reduced)
            basis[pivot] = {j:q/reduced[pivot] for j,q in reduced.items()}
    controls = []
    for mask in range(8):
        changed = {k:r.copy() for k,r in rows.items()}
        for bit,(k,q) in enumerate(pulses):
            if not (mask>>bit & 1):
                add(changed[k], {~(n-1):F(1)}, -q/8)
        actual = v.scalar(graph,moves,changed,{n-1:F(1)})
        error = {i:actual[first+i]-(i == n-1) for i in range(n)}
        predicted = {}
        for bit,column in enumerate(columns):
            if not (mask>>bit & 1):
                add(predicted,column,F(-1))
        need({i:q for i,q in error.items() if q} == predicted, 'all fresh-term omission subsets')
        controls.append(dict(mask=mask,errors=terms(predicted)))
    # Compare full pulse changes with the exact outer-product error law.
    weights = [(F(0),F(0),F(0)),(F(1,2),F(-2,3),F(7,5)),(F(1),F(1),F(1))]
    rational_controls = []
    for inputs in ({n-1:F(1)},{1164:F(1)},{1166:F(1)},{3:F(1),683:F(-2),n-1:F(3)}):
        good = v.scalar(graph,moves,rows,inputs)
        excitation = inputs.get(n-1,F(0))-sum(q*good[k] for k,q in calibration.items())
        for weight in weights:
            changed = {k:r.copy() for k,r in rows.items()}
            for (k,q),scale in zip(pulses,weight,strict=True):
                add(changed[k], {~(n-1):F(1)}, (scale-1)*q/8)
                add(changed[k], calibration, -(scale-1)*q/8)
            actual = v.scalar(graph,moves,changed,inputs)
            prediction = {}
            for scale,column in zip(weight,columns,strict=True):
                add(prediction,column,excitation*(scale-1))
            error = {i:actual[first+i]-good[first+i] for i in range(n) if actual[first+i] != good[first+i]}
            need(error == prediction, 'all rational pulse-weight errors')
            rational_controls.append(dict(input=terms(inputs),weights=[str(q) for q in weight],error=terms(error)))
    rank = lambda a,b: len(graph['frames'][b])-len(graph['frames'][a])
    h = event['role']
    spans = [v.span(f) for f in graph['frames']]
    need(spans[3] < spans[232] < spans[517] and [rank(3,232),rank(232,517),rank(3,517)] == [4,4,8], 'productive split geometry')
    need(all((before['initial'][i],before['final'][i]) == (graph['initial'][i],graph['final'][i]) for i in range(n-1) if i != h), 'all other owner charts')
    paid = Counter(abs(rank(a,b)) for a,b in moves.values())
    targets = Counter(rank(a,b) for i,(a,b) in enumerate(zip(graph['initial'],graph['final'],strict=True)) if i not in mains)
    need({str(k):v for k,v in paid.items()} == journal['result']['native_inventory']['paid'] and
         {str(k):v for k,v in targets.items()} == journal['result']['native_inventory']['targets'], 'literal native invoice')
    return dict(source_files=len(pins),source_graph=digest(before),final_graph=digest(graph),
                public_owners=n,paid_moves=len(moves),changed_rows=len(changes),
                coefficient_positions=(n-1)**2+2*n*n,exact_scalar_products=products,
                pulse_ids=[k for k,q in pulses],pulse_response_columns=[terms(c) for c in columns],
                pulse_response_rank=len(basis),response_minor=[[str(q) for q in row] for row in minor],
                response_minor_determinant='25/4',calibration_row=terms(calibration_row),
                omission_controls=controls,rational_controls=rational_controls,
                paid=dict(sorted(paid.items())),targets=dict(sorted(targets.items())),
                native_delta=dict(paid={},targets={4:2,8:-1}),both_probes_blind_to_each_pulse=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record',action='store_true')
    args = parser.parse_args()
    start = time.monotonic()
    result = json.loads(v.encoded(run()))
    if args.record:
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:
        need(result == read(HERE/'RESULT.json'),'deposited exact certificate')
    print('PASS_P104_FINAL_HELPER_AUDIT',result['public_owners'],'owners',result['pulse_response_rank'],'pulse rank',round(time.monotonic()-start,2),'seconds')
