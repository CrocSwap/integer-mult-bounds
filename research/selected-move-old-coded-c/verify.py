"""Independent old-address integer oracle; decoded values are checker-only.
Prepared for @CubeJerry with OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
from hashlib import sha1, sha256
import json
import sys
import types
HERE = Path(__file__).resolve().parent
C = types.ModuleType('_checked_composition'); C.__file__ = str(HERE / 'compose.py')
sys.modules[C.__name__] = C
exec(compile((HERE / 'compose.py').read_bytes(), C.__file__, 'exec'), C.__dict__)
SCHEMA = ('outer','rows','stock','row_bits','within_bits','record_bits','p','d',
          'K','G','H','q0','qF','qB','D','f','rho','active_start','back_start',
          'selected_axes','entry_start','remainder','cutoff')


def need(condition, message):
    if not condition: raise ValueError(message)


def authenticate():
    entries = json.loads((HERE/'SOURCE-PINS.json').read_text())['files']
    for entry in entries:
        raw = (HERE/entry['local']).read_bytes()
        def matches(data):
            blob = sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            return len(data) == entry['bytes'] and sha256(data).hexdigest() == entry['sha256'] and blob == entry['git_blob']
        need(matches(raw), 'exact input bytes: '+entry['local'])
        need(not matches(raw+b' '), 'source drift negative control')
    return len(entries)


def header(h):
    out = []
    for key in SCHEMA:
        binary = list(map(int, bin(h[key])[2:][::-1]))
        out += [1] * len(binary) + [0] + binary
    return out


def old_word(values, width):
    out = []
    for value in values:
        for bit in range(width): out += [0, 0, (value >> bit) & 1]
        out += [0, 1, 0]
    return out


def packet(a=9, u=0, r=1, width=3, rows=1, cutoff=1, scale=2, imaginary=False):
    h = dict.fromkeys(SCHEMA, 0)
    h.update(outer=1, rows=rows, row_bits=(1 << a) * 6 * r * (width + 1),
             within_bits=a, record_bits=6*r*(width+1), f=1, K=1, rho=0,
             active_start=u, cutoff=cutoff, G=1, H=1, d=9,
             selected_axes=9, back_start=a-1)
    values = []
    for row in range(rows):
        for address in range(1 << a):
            for coefficient in range(r):
                real = scale * ((13*address + 2*coefficient + row) % 3 - 1)
                imag = scale * ((5*address + coefficient + 2*row) % 3 - 1) if imaginary else 0
                values += [real, imag]
    return h, r, width, values


def integer_c_old_address(values, h, r, width):
    """Tuple addresses stay in the old order; no packing helper is used."""
    result = list(values); a = h['within_bits']; size = 1 << a
    for column in reversed(range(h['f'])):
        position = h['active_start'] + column*h['K'] + h['rho']
        mask = 1 << (a-1-position)
        for row in range(h['outer']*h['rows']):
            for left in range(size):
                if left & mask: continue
                right = left | mask
                for coefficient in range(r):
                    li = ((row*size+left)*r+coefficient)*2
                    ri = ((row*size+right)*r+coefficient)*2
                    ar, ai = result[li:li+2]; br, bi = result[ri:ri+2]
                    nums = (ar-ai+br+bi, ar+ai-br+bi,
                            ar+ai+br-bi, -ar+ai+br+bi)
                    if any(x % 2 for x in nums): raise ArithmeticError('nonintegral prefix')
                    out = tuple(x//2 for x in nums)
                    if any(not -(1 << (width-1)) <= x < (1 << (width-1)) for x in out):
                        raise OverflowError('signed prefix outside width')
                    result[li:li+2], result[ri:ri+2] = out[:2], out[2:]
    return result


def tapes_for(data, context):
    tapes = [C.Tape(origin=3+i%7, permanent_guard=i<43) for i in range(70)]
    tapes[0] = C.Tape(data, origin=3)
    tapes[1] = C.Tape(context, origin=4)
    return tapes


def body(tape):
    end = tape.origin
    while end < len(tape.cells) and tape.cells[end] != C.BLANK: end += 1
    return tape.cells[tape.origin:end]


def check_return(tapes, expected, context):
    need(body(tapes[0]) == expected, 'exact direct old-address C output')
    need(body(tapes[1]) == context and tapes[1].writes == 0, 'immutable original context')
    for i, tape in enumerate(tapes):
        need(tape.head == tape.origin, 'all 70 head origins returned')
        need(tape.low >= tape.origin-1, 'no opaque left exterior visited')
        need(tape.cells[tape.origin-2] == 7, 'opaque exterior preserved')
        need(tape.cells[tape.origin-1] == (C.LEFT if i<43 else C.BLANK), 'permanent or retired guard')
        if i >= 2:
            need(all(x == C.BLANK for x in tape.cells[tape.origin:]), 'all 68 private bodies retired')


def positive(code, labels, args, root_domain=False):
    h, r, width, values = packet(**args)
    expected = integer_c_old_address(values, h, r, width)
    need(expected != values, 'nonidentity arithmetic fixture')
    data, context = old_word(values, width), header(h)
    tapes = tapes_for(data, context); owner = tapes[0]
    cpu = C.CPU(code, tapes, labels)
    need(cpu.run() == 'DONE', 'uninterrupted joined success')
    need(cpu.leaf_entries == cpu.exit_entries == 1, 'one real child and one inverse continuation')
    need(tapes[0] is owner, 'original public owner identity')
    check_return(tapes, old_word(expected, width), context)
    V, E, f = len(data), len(context), h['f']
    history = sum(t.high-t.low+1 for t in tapes[2:])
    need(cpu.steps <= 2**24*(f*V+E+1), 'complete combined time envelope')
    need(history <= 128*(V+E+1), 'complete retained private history envelope')
    if root_domain:
        # Complete-root t=0 model, after a separately supplied right monomial.
        n, p, magnitude_h, depth = 9, 0, 1, 0
        need(width == p+magnitude_h+2*n+3 and 356*depth < n, 'common-root width and depth')
        need(h['within_bits'] == n and 9*f <= n, 'complete root embedding')
        need(all(x % (1 << n) == 0 and abs(x) < (1 << (magnitude_h+n)) for x in values),
             'original grid and strict root magnitude')
    return {'parameters': args, 'V_old': V, 'E': E, 'transitions': cpu.steps,
            'incremental_private_history': history, 'actual_C_changed_output': True,
            'common_root_model': root_domain, 'first_numerator_write': cpu.first_numerator_write}


def rejection(code, labels, record, reason, truncate=False):
    h, r, width, values = record
    data = old_word(values, width)
    if truncate: data = data[:-1]
    context = header(h); tapes = tapes_for(data, context)
    cpu = C.CPU(code, tapes, labels)
    need(cpu.run(limit=40_000_000) == 'REJECT', 'expected rejection: '+reason)
    need(body(tapes[0]) == data and tapes[0].writes == 0, 'precommit original source protected')
    need(body(tapes[1]) == context and tapes[1].writes == 0, 'rejected context protected')
    return {'control': reason, 'steps': cpu.steps, 'leaf_entered': bool(cpu.leaf_entries)}


def controls(code, labels, first_write):
    receipts = []
    base = packet(width=2, scale=0)
    h, r, width, values = base
    odd = list(values); odd[0] = 1
    try: integer_c_old_address(odd, h, r, width)
    except ArithmeticError: pass
    else: raise ValueError('independent parity oracle failed')
    receipts.append(rejection(code, labels, (h,r,width,odd), 'nonintegral first C axis'))
    overflow = list(values); overflow[0:2] = (-2,1); overflow[512:514] = (-2,-1)
    try: integer_c_old_address(overflow, h, r, width)
    except OverflowError: pass
    else: raise ValueError('independent signed-fit oracle failed')
    receipts.append(rejection(code, labels, (h,r,width,overflow), 'integral out-of-range C row'))
    receipts.append(rejection(code, labels, base, 'short old-coded field', truncate=True))
    wrong_port = list(code)
    for pc in range(labels['LEAF'], len(code)):
        ins = code[pc]
        if ins[0] in ('R','W','M') and ins[1] == 2:
            wrong_port[pc] = (ins[0], 0, *ins[2:])
    receipts.append(rejection(tuple(wrong_port), labels, packet(width=3, r=2), 'child DATA wrongly bound to old-coded owner'))
    wrong_bit = list(code); ins = wrong_bit[first_write]
    need(ins[0] == 'W' and ins[1] == labels['NUM'] and ins[2] in (0,1), 'reachable numerator mutation site')
    wrong_bit[first_write] = ('W', ins[1], 1-ins[2])
    receipts.append(rejection(tuple(wrong_bit), labels, packet(width=3, r=2), 'reachable numerator branch bit mutation'))
    dirty = tapes_for(old_word(values,width), header(h)); dirty[69] = dirty[68]
    try: C.CPU(code,dirty,labels)
    except ValueError: receipts.append({'control':'aliased private physical owner','detected':True})
    else: raise ValueError('alias guard failed')
    # Exact algebraic endpoint-only control: no full f=2 graph run is claimed.
    fibre = (1,0,0,1)
    need(fibre[0] + fibre[1] == 1, 'half-integral first pair')
    gaussian = (((1,1),(1,-1)),((1,-1),(1,1)))
    tensor = []
    for out in range(4):
        real = imag = 0
        for inp in range(4):
            ar,ai=gaussian[out>>1][inp>>1]; br,bi=gaussian[out&1][inp&1]
            real += fibre[inp]*(ar*br-ai*bi); imag += fibre[inp]*(ar*bi+ai*br)
        need(real%4 == imag%4 == 0, 'endpoint numerator divisibility')
        tensor.append((real//4,imag//4))
    need(tensor == [(0,0),(1,0),(1,0),(0,0)], 'endpoint-only admission remains invalid')
    receipts.append({'control':'endpoint-only f2 algebraic obstruction','actual_f2_graph_run':False})
    return receipts


def main():
    sources = authenticate()
    code, labels = C.compile_composition()
    need(len(code) == 12829 and max(ins[1] for ins in code if ins[0] in ('R','W','M')) == 69,
         'fixed graph/tape count')
    cases = [positive(code, labels, {'r':2,'width':3}),
             positive(code, labels, {'a':10,'u':1,'width':3}),
             positive(code, labels, {'width':22,'scale':512,'imaginary':True,'cutoff':(1<<137)+3}, True)]
    negative = controls(code,labels,cases[0]['first_numerator_write'])
    print(json.dumps({'status':'PASS_ACTUAL_OLD_CODED_C_JOIN','fixed_tapes':70,
                      'authenticated_sources':sources,'source_mutations_detected':sources,
                      'instructions':len(code),'graph_sha256':C.digest(code),
                      'compose_sha256':sha256((HERE/'compose.py').read_bytes()).hexdigest(),
                      'positive_cases':cases,'negative_controls':negative,
                      'assumptions_discharged':[],'new_kappa':False},indent=2))


if __name__ == '__main__': main()
