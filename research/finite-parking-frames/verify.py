"""Exact finite-table evidence. Apache-2.0; ywz65 with OpenAI Codex."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import machine as M
import independent

need = M.need

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))

def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()

def serial(table):
    return [[*key, nxt, list(writes), list(moves)]
            for key, (nxt, writes, moves) in sorted(table.items())]

def authenticate():
    snapshots = json.loads((HERE/'SNAPSHOTS.json').read_text())['files']
    expected = {'inputs/'+x for x in ('PROOF.md','NOTICE.md','frame.py','vendor-pipeline.py','vendor-streams.py')}
    need(len(snapshots) == len(expected) and {x['snapshot'] for x in snapshots} == expected,
         'complete reference source inventory')
    for row in snapshots:
        raw = (HERE/row['snapshot']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source hash '+row['snapshot'])
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'], 'source blob')
    text = (HERE/'inputs/frame.py').read_text()
    for snippet in ('extents = [local.push(tape) for tape in inactive]',
                    'for index in reversed(range(len(extents))):',
                    'restored[index] = local.pop(extents[index])',
                    'child_park = ParkFrame(local)', 'child_park.close()'):
        need(snippet in text, 'matched-packet caller source')

def run_checked(m, operation, n, rows=None, want='done'):
    initial = [dict(x) for x in m.tapes]
    heads = list(m.heads)
    receipt = m.run(operation, 12*n+100)
    need(m.state == want, 'halt '+operation)
    if want == 'done':
        need(receipt == M.tariff(operation, n), 'tariff '+operation)
    if rows is not None:
        other = independent.execute(rows, initial, heads, operation, n+20, 12*n+100)
        need(other == (m.state, m.tapes, m.heads, receipt), 'separate dense interpreter')
    return receipt

def packet_fixture(bits, p=0, b=0):
    n = len(bits)
    parking = {p-j-1: M.ALPHABET[j % len(M.ALPHABET)] for j in range(19)}
    parking = {i: x for i, x in parking.items() if x != '_'}
    packet = {b-1: '^', b+n: '$', b+n+7: 'F', b-9: 'R'}
    packet.update({b+j: str(x) for j, x in enumerate(bits)})
    return M.Machine(parking, packet, (p, b))

def roundtrip(bits, p, b, rows, table=None):
    m = packet_fixture(bits, p, b)
    if table is not None:
        m.table = table
    original = [dict(x) for x in m.tapes]
    n = len(bits)
    run_checked(m, 'begin', n, rows)
    need(m.heads == [p+1, b], 'begin head')
    run_checked(m, 'push', n, rows)
    wantp = dict(original[0]); wantp[p] = 'F'; wantp[p+1] = 'R'
    wantp.update({p+j+2: str(x) for j, x in enumerate(bits)})
    wantb = {i: x for i, x in original[1].items() if not b <= i <= b+n}
    need(m.tapes == [wantp, wantb] and m.heads == [p+n+2, b], 'push exact endpoint')
    run_checked(m, 'pop', n, rows)
    after = dict(original[0]); after[p] = 'F'
    need(m.tapes == [after, original[1]] and m.heads == [p+1, b], 'pop exact endpoint/order')
    run_checked(m, 'end', n, rows)
    need(m.tapes == original and m.heads == [p, b], 'full exact restoration')
    need(min(m.visited[0]) >= p and min(m.visited[1]) >= b-1
         and max(m.visited[1]) <= b+n, 'opaque cells never scanned')
    return m.counts, m.transitions

def nested(depth, rows):
    p, b = -37, 23
    m = M.Machine({p-1: '$', p-2: 'F', p-3: '1'}, {b-1: '^', b-7: 'R'}, (p, b))
    original = [dict(x) for x in m.tapes]
    frames = []; volume = records = peak = 0
    live_volume = live_records = 0
    def boundary():
        nonlocal peak
        expected = live_volume+live_records+len(frames)
        need(m.heads[0]-p == expected, 'physical marker space')
        peak = max(peak, expected)
    for level in range(depth):
        run_checked(m, 'begin', 0, rows); frames.append([]); boundary()
        for j in range(3):
            n = (0, 1, 7, 23, 64)[(level+j) % 5]
            bits = tuple((k+level+j) % 2 for k in range(n))
            # Caller supplies the port; fixture setup is outside the charged controller.
            m.tapes[1].update({b+k: str(x) for k, x in enumerate(bits)}); m.tapes[1][b+n] = '$'
            run_checked(m, 'push', n, rows)
            frames[-1].append(bits); volume += n; records += 1
            live_volume += n; live_records += 1; boundary()
    for level in range(depth-1, -1, -1):
        for bits in reversed(frames[-1]):
            n = len(bits); run_checked(m, 'pop', n, rows)
            need([m.tapes[1].get(b+k) for k in range(n)] == list(map(str,bits))
                 and m.tapes[1].get(b+n) == '$' and m.heads[1] == b, 'nested ordered result')
            # Caller consumes the port; no free caller-movement claim is made.
            for k in range(n+1):
                del m.tapes[1][b+k]
            live_volume -= n; live_records -= 1; boundary()
        frames.pop(); run_checked(m, 'end', 0, rows); boundary()
    need(m.tapes == original and m.heads == [p,b], 'nested caller prefix and heads')
    want = dict(steps=5*volume+7*records+3*depth,
                reads=10*volume+14*records+6*depth,
                writes=4*volume+4*records+2*depth,
                moves=8*volume+8*records+2*depth)
    need(m.counts == want, 'all-node complete tariff')
    need(min(m.visited[0]) >= p and min(m.visited[1]) >= b-1, 'nested opaque scope')
    return dict(depth=depth, records=records, volume=volume, parking_peak=peak, counts=want)

def controls(rows):
    out = []
    for op in ('pop', 'end'):
        m = M.Machine({-1:'1'}, {-1:'^'}, (0,0)); m.run('begin')
        if op == 'end':
            m.tapes[1][0] = '$'; m.run('push')
        old = ([dict(x) for x in m.tapes], list(m.heads))
        run_checked(m, op, 0, rows, 'reject')
        need((m.tapes,m.heads) == old, 'boundary rejection unchanged')
        out.append(op+'_boundary_rejected_unchanged')
    for obstruction in range(5):
        m = packet_fixture((1,0,1,1)); m.run('begin'); m.run('push')
        m.tapes[1][obstruction] = '1'; old = [dict(x) for x in m.tapes]
        r = m.run('pop', 100)
        need(m.state == 'reject' and r['writes'] == 0 and m.tapes == old, 'read-only output preflight')
    out.append('five_output_obstructions_rejected_before_writes')
    mutations = [
        ('wrong_payload', ('push_copy','_','1'), ('push_copy',('0','_'),(1,1))),
        ('unremoved_record', ('pop_copy','R','^'), ('done',(None,None),(0,1))),
        ('wrong_output_direction', ('pop_copy','1','_'), ('pop_copy',('_','1'),(-1,1))),
        ('unrewound_packet', ('push_rewind','_','^'), ('done',(None,None),(0,0))),
        ('lost_empty_record', ('push','_','$'), ('push_copy',(None,None),(1,0))),
    ]
    for name,key,change in mutations:
        table = dict(M.TABLE); table[key] = change
        try:
            roundtrip((), 0,0,None,table)
            roundtrip((1,0,1),0,0,None,table)
        except (ValueError, KeyError):
            out.append(name+'_rejected')
        else:
            raise ValueError('accepted controller mutation '+name)
    table = dict(M.TABLE); del table['begin','_','_']
    try:
        M.certify(table)
    except ValueError:
        out.append('missing_transition_rejected')
    else:
        raise ValueError('incomplete table accepted')
    return out

def experiment():
    authenticate()
    entries = M.certify(M.TABLE); rows = serial(M.TABLE)
    need(canonical(rows) == canonical(json.loads((HERE/'TABLE.json').read_text())), 'literal transition certificate')
    cases = 0; used = set(); receipts=[]
    for n in range(11):
        for bits in itertools.product((0,1), repeat=n):
            r, seen = roundtrip(bits, 0,0,rows); cases += 1; used |= seen
            receipts.append([n, list(bits), r])
    translations = []
    for n in (0,1,2,31,127,1024,16384):
        for p,b in ((-191,53),(257,-79),(100003,100029)):
            bits = tuple((k*k+k//3+1)%2 for k in range(n))
            r, seen = roundtrip(bits,p,b,rows); used |= seen
            translations.append([n,p,b,r])
    nesting = [nested(d, rows) for d in (1,2,7,32,129)]
    return dict(status='PASS_FINITE_PARKING_FRAMES', finite_states=len(M.STATES),
                table_entries=entries, table_sha256=digest(rows), exhaustive_packets=cases,
                exhaustive_max_width=10, exhaustive_receipt_sha256=digest(receipts),
                translated_large_cases=translations, nested=nesting,
                positive_transition_keys_used=len(used), controls=controls(rows),
                scope='Matched records and trusted well-bracketed frame commands only; parking control tariff, not full tape allocation, dispatcher, supplier or kappa.')

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--out',type=Path); args=parser.parse_args()
    if args.out:
        need(not args.out.exists(), 'output must be new')
    result = experiment()
    if args.out:
        with args.out.open('x',encoding='utf-8',newline='\n') as stream:
            stream.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        need(canonical(result) == canonical(json.loads((HERE/'RESULT.json').read_text())), 'complete typed receipt')
    print(result['status'], 'packets='+str(result['exhaustive_packets']),
          'table='+str(result['table_entries']), 'controls='+str(len(result['controls'])))

if __name__ == '__main__':
    main()
