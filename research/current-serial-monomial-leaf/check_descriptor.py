"""Actual physical iterator checked against a separate integer observer.

Fixture arrays and decoded integers occur only in this checker.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
import json
from column_view import ColumnView, S, ROLES, PARENT, VIEW, PRIVATE, R
from serial_sources import need

SCHEMA = tuple(ROLES)


def encode(values):
    out = []
    for name in SCHEMA:
        digits = [int(x) for x in bin(values[name])[2:][::-1]]
        out += [1] * len(digits) + [0] + digits
    return out


def decode(bits):
    at, out = 0, {}
    for name in SCHEMA:
        length = 0
        while at < len(bits) and bits[at] == 1:
            length += 1
            at += 1
        need(length > 0 and at < len(bits) and bits[at] == 0, "positive header prefix")
        at += 1
        digits = bits[at:at+length]
        need(len(digits) == length and all(x in (0, 1) for x in digits)
             and (length == 1 or digits[-1] == 1), "canonical header digits")
        out[name] = sum(x << i for i, x in enumerate(digits))
        at += length
    need(at == len(bits), "exact header end")
    return out


def put(tape, bits):
    stop = tape.origin + len(bits)
    if len(tape.cells) < stop:
        tape.cells.extend([6] * (stop - len(tape.cells)))
    tape.cells[tape.origin:stop] = bytearray(bits)
    for i in range(stop, len(tape.cells)):
        tape.cells[i] = 6
    tape.head = tape.origin
    tape.high = max(tape.high, stop)


def body(tape):
    out, ended = [], False
    for value in tape.cells[tape.origin:]:
        if value == 6:
            ended = True
        else:
            need(not ended and value in (0, 1), "complete raw prefix")
            out.append(value)
    return out


def values(m=9, f=3, K=2, rho=1, remainder=0, long=0):
    H = max(1, f-1)
    u = 2*H + remainder*K + 3
    z = u + m*f*K + 5
    a = z + H + 2
    b = 30
    return dict(outer=(1 << long)+1, rows=3, stock=1, row_bits=b << a,
                within_bits=a, record_bits=b, p=max(m*f+remainder, 2),
                d=m*f+remainder, K=K, G=1, H=H, q0=3, qF=4, qB=5,
                D=m*f+remainder, f=f, rho=rho, active_start=u, back_start=z,
                selected_axes=m*f+remainder, entry_start=u-remainder*K,
                remainder=remainder, cutoff=3*m*f)


def hardware(m):
    v = ColumnView(m)
    work = [S.codec.DenseTape(3+i%5) for i in PRIVATE]
    parent = S.codec.DenseTape(11)
    for tape in (*work, parent):
        for j in range(tape.origin-1):
            tape.cells[j] = j % 2
    v.bind(work, S.abi.BinaryContextPort(parent))
    return v, work, parent


def case(m, parent_values, reuse=None):
    owner, work, parent = hardware(m) if reuse is None else reuse
    initial = encode(parent_values)
    put(parent, initial)
    ancestors = [bytes(t.cells[:t.origin]) for t in (*work, parent)]
    before = sum(t.actions() for t in (*work, parent))
    owner.prepare()
    seen, maximum = [], 0
    try:
        for j in range(parent_values['f']):
            current = body(owner.context.tape)
            expected = dict(parent_values, f=1, K=parent_values['f']*parent_values['K'],
                            rho=j*parent_values['K']+parent_values['rho'],
                            selected_axes=m+parent_values['remainder'])
            need(decode(current) == expected and current == encode(expected), "all23 exact private fields")
            need(body(parent) == initial and parent.head == parent.origin, "borrowed parent preserved")
            need(all(t.head == t.origin for t in work), "all native-cut private origins")
            for i in range(m):
                need(expected['active_start']+i*expected['K']+expected['rho'] ==
                     parent_values['active_start']+(i*parent_values['f']+j)*parent_values['K']+parent_values['rho'],
                     "original source bit positions")
            maximum = max(maximum, len(current))
            seen.append(expected['rho'])
            need(owner.advance() == ('finished' if j+1 == parent_values['f'] else 'ready'),
                 "exact finite iteration stopping")
    finally:
        owner.release()
    need(body(parent) == initial and parent.head == parent.origin, "parent restored at return")
    need(all(t.head == t.origin and not body(t) for t in work), "all private current prefixes erased")
    need([bytes(t.cells[:t.origin]) for t in (*work,parent)] == ancestors, "ancestors preserved")
    bill = sum(t.actions() for t in (*work,parent))-before
    # A deliberately loose bound proved by finite per-digit loop accounting.
    need(bill <= 10000*(parent_values['f']+1)*(len(initial)+1), "explicit positive metadata ceiling")
    report = dict(rank=m, f=parent_values['f'], input_bits=len(initial),
                  maximum_view_bits=maximum, columns=len(seen), physical_actions=bill,
                  retained_materialized_cells=sum(len(t.cells) for t in work))
    return report, (owner,work,parent)


def run():
    results = []
    for m in (1,2,9):
        reused = None
        for f in (1,2,3,7,17):
            for K in (1,3):
                v=values(m=m,f=f,K=K,rho=K-1,remainder=m-1)
                report,reused=case(m,v,reused)
                results.append(report)
    long,reused=case(9,values(long=4096))
    short,reused=case(9,values(f=1,K=1,rho=0),reused)
    fresh,_=case(9,values(f=1,K=1,rho=0))
    need(short['physical_actions']==fresh['physical_actions'], "no old-backing time surcharge")
    need(short['retained_materialized_cells']>fresh['retained_materialized_cells'], "old backing retained")
    rejected=[]
    for key in ('f','K'):
        v,work,parent=hardware(2)
        bad=values(m=2);bad[key]=0
        put(parent,encode(bad))
        try:v.prepare()
        except ValueError:rejected.append('zero_'+key)
        else:raise ValueError('invalid positive field accepted')
        need(not v.active and all(not body(t) and t.head==t.origin for t in work), "failed view retired")
        case(2,values(m=2),(v,work,parent))
    v,work,parent=hardware(2)
    bad=list(v.prepare_table)
    at=max(i for i,row in enumerate(bad) if row==('write',ROLES['f'],'1'))
    bad[at]=('write',ROLES['f'],'0')
    v.prepare_table=tuple(bad)
    put(parent,encode(values(m=2)))
    v.prepare()
    need(decode(body(v.context.tape))['f'] != 1, "unscaled/malformed child-f mutant detected by exact oracle")
    v.release()
    return dict(status='PASS_SERIAL_MONOMIAL_DESCRIPTOR', cases=results,
                long=long,history=dict(reused_small=short,fresh_small=fresh),
                controls=rejected+['child_f_zero_mutant'],
                ports=ColumnView.port_count, complete_numeric_execution=False)


if __name__=='__main__':
    print(json.dumps(run(),sort_keys=True))
