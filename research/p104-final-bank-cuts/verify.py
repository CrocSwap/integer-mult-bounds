"""Check two free bank cuts and their complete rational output operators."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha1, sha256
from pathlib import Path
import argparse
import importlib.util
import json
import time
from build_prefix import build, dump, digest, Network, encoded, read

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('operator7777', HERE/'retained/operator7777/verify.py')
op = importlib.util.module_from_spec(spec)
spec.loader.exec_module(op)
need = op.need


def terms(row):
    return [[j, str(q)] for j, q in sorted(row.items()) if q]


def cut(net, event, slope=F(1), inverse=True):
    """Change the two delivered coordinates, then remove a local transfer."""
    a_id, b_id = event['rotations'][0]['slots']
    need(net.moves[a_id] == net.moves[b_id], 'parallel basis inputs')
    rows = net.forms.copy()
    rows[a_id] = net.forms[b_id].copy()
    rows[b_id] = op.add({j:-q for j,q in net.forms[a_id].items()}, net.forms[b_id], slope)
    if inverse:
        for k, row in list(rows.items()):
            a, b = row.get(a_id, F(0)), row.get(b_id, F(0))
            if a or b:
                other = {j:q for j,q in row.items() if j not in (a_id,b_id)}
                rows[k] = op.add(other, {a_id:slope*a+b,b_id:-a}, F(1))
    arrivals, sends = set(event['arrivals']), set(event['sends'])
    local, crossing = {}, []
    for k, row in rows.items():
        chart = net.moves[k][0] if k in net.moves else net.final[k-net.first_output]
        if chart == event['old']:
            local[k] = terms(row)
            wrong = {j:q for j,q in row.items() if q and ((j in arrivals) != (k in sends))}
            if wrong:
                crossing.append([k,terms(wrong)])
    if crossing:
        return None, dict(local=local,crossing=crossing)
    moves = {k:(event['new'] if k in sends else a,event['new'] if k in arrivals else b) for k,(a,b) in net.moves.items()}
    gone = [k for k,(a,b) in moves.items() if a == b]
    need(gone == event['removed_paid'], 'exact removed transfers')
    for retired in gone:
        for k,row in list(rows.items()):
            if k != retired and retired in row:
                other = row.copy()
                q = other.pop(retired)
                rows[k] = op.add(other, rows[retired], q)
        del rows[retired]
        del moves[retired]
    return Network(net.first_output,net.initial,net.final,moves,rows),dict(local=local,crossing=[])


def run():
    pins = json.loads((HERE/'SOURCE-PINS.json').read_text())['sources']
    for pin in pins:
        raw = (HERE/pin['retained']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'], 'source SHA256')
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'], 'source Git blob')
    graph, before, last = build()
    events = [e['split'] for e in last['events']]
    need(len(events) == 2 and not last['new_frames'], 'two final cuts only')
    individual, receipts = [], []
    for event, stay in zip(events, [100093,96750]):
        a,b = event['rotations'][0]['slots']
        need(before.forms[stay][a] == 1 and before.forms[stay][b] == -1, 'crossing coefficient is slope minus one')
        after, receipt = cut(before,event)
        need(after is not None, 'zero crossing at slope one')
        _, wrong = cut(before,event,F(0))
        _, omitted = cut(before,event,inverse=False)
        need(wrong['crossing'] == [[stay,[[a,'-1']]]], 'wrong slope witness')
        need(len(omitted['crossing']) == 3, 'omitted inverse witnesses')
        # Check both matrix products for the whole rational one-parameter family.
        for s in [F(-3),F(0),F(1),F(7,3)]:
            m, inv = [[0,1],[-1,s]], [[s,-1],[1,0]]
            for left,right in [(m,inv),(inv,m)]:
                need([[sum(left[i][k]*right[k][j] for k in range(2)) for j in range(2)] for i in range(2)] == [[1,0],[0,1]], 'basis inverse')
        individual.append(after)
        receipts.append(dict(old_chart=event['old'],new_chart=event['new'],retired=event['removed_paid'][0],basis_slots=[a,b],before_local={k:terms(before.forms[k]) for k in receipt['local']},after_local=receipt['local'],wrong_slope=wrong['crossing'],omitted_inverse=omitted['crossing']))
    both,_ = cut(individual[0],events[1])
    reverse,_ = cut(individual[1],events[0])
    final = dump(both,graph['frames'])
    need(final == dump(reverse,graph['frames']), 'cuts commute byte for byte')
    need(digest(final) == last['result'], 'published final graph')
    first, count = graph['first_output'], len(graph['initial'])
    need(count == 1264, 'full public boundary')
    outputs, products, profiles = [], 0, []
    for net in [before,*individual,both]:
        g = dump(net,graph['frames'])
        need(all(g[k] == graph[k] for k in ['frames','initial','final','first_output']), 'unchanged protected boundary')
        values, work = op.expand(g,net.moves,net.forms)
        products += work
        terminal = [values[first+i] for i in range(count)]
        outputs.append(terminal)
        profile = Counter(abs(len(g['frames'][a])-len(g['frames'][b])) for a,b in net.moves.values())
        profiles.append(dict(graph_sha256=digest(g),paid=len(net.moves),ranks=dict(sorted(profile.items())),operator_sha256=sha256(encoded(terminal)).hexdigest()))
    need(all(output == outputs[0] for output in outputs[1:]), 'every arbitrary-input output coefficient')
    p = [Counter(v['ranks']) for v in profiles]
    delta = lambda a,b:{r:b[r]-a[r] for r in a|b if a[r]!=b[r]}
    need(delta(p[0],p[1]) == delta(p[0],p[2]) == {2:-1,3:-1,5:1}, 'individual paid moment')
    need(delta(p[0],p[3]) == {2:-2,3:-2,5:2}, 'combined paid moment')
    source = read('RESULT.json')
    caller = source['caller']
    need(caller['calls'] == 48, 'published caller multiplicity')
    full_paid = 48*len(both.moves)+sum(caller['fixed_caller_paid'].values())
    full_targets = 48*sum(source['native']['positive_helper_ranks'].values())+sum(caller['fixed_root_targets'].values())
    need((full_paid,full_targets) == (282864,51312), 'unchanged-caller invoice implication')
    # A same-chart coefficient error passes the structural checks and fails the operator.
    terminal_id = next(k for k in sorted(both.forms) if k >= first and both.forms[k])
    donor = next(iter(both.forms[terminal_id]))
    donor_vector = op.vector(values[donor])
    input_id = next(iter(donor_vector))
    changed = both.forms.copy()
    changed[terminal_id] = changed[terminal_id].copy()
    changed[terminal_id][donor] += 1
    expected = op.scalar(final,both.moves,both.forms,{input_id:F(1)})
    actual = op.scalar(final,both.moves,changed,{input_id:F(1)})
    error = actual[terminal_id]-expected[terminal_id]
    need(error == donor_vector[input_id] and error, 'valid-chart arithmetic mutant')
    layout = read('LAYOUT.json.gz')
    return dict(source_files=len(pins),public_owners=count,exact_scalar_products=products,cuts=receipts,states=profiles,commute=True,basis_matrix=[[0,1],[-1,1]],basis_inverse=[[1,-1],[1,0]],unique_slope='1',native_paid_gain=2,caller_multiplicity=48,full_paid_gain_if_caller_retained=96,unchanged_layout_sha256=sha256(encoded(layout)).hexdigest(),arithmetic_mutant=dict(output=terminal_id-first,donor=donor,input=input_id,error=str(error)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record',action='store_true')
    args = parser.parse_args()
    start = time.monotonic()
    result = json.loads(json.dumps(run()))
    if args.record:
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:
        need(result == json.loads((HERE/'RESULT.json').read_text()), 'deposited certificate')
    print('PASS_P104_FINAL_BANK_CUTS',result['public_owners'],'owners',len(result['states']),'operators','2 cuts',round(time.monotonic()-start,2),'seconds')
