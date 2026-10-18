#!/usr/bin/env python3
"""Bounded signed-integer machine; separate direct dense target oracle.

Apache-2.0. Prepared for Charles Bethin with substantial OpenAI Codex assistance.
Consumes literal instructions, not the compiler or symbolic interpreter.
The controller tariff is explicit; this is not a physical supplier backend.
"""
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = ((1, 1, 1), (1, 1, -1), (1, -1, 0))
GROUPS = [range(0, 2), range(2, 5), range(5, 9),
          range(9, 14), range(14, 20), range(20, 27)]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def encode(op):
    kind, f, p, q, sign = op
    code = {'F': 0, 'R': 1, 'S': 2}[kind]
    field = f if kind == 'F' else {-1: 0, 1: 1, 2: 2}[f]
    require(0 <= field < 32 and 0 <= p < 16 and 0 <= q < 16,
            'instruction fields')
    require(sign in (-1, 1), 'instruction sign')
    return code << 14 | field << 9 | p << 5 | q << 1 | (sign < 0)


def decode(token):
    require(type(token) is int and 0 <= token < 65536, '16-bit token')
    code, field = token >> 14, token >> 9 & 31
    p, q, sign = token >> 5 & 15, token >> 1 & 15, 1 - 2*(token & 1)
    require(code < 3, 'reserved opcode')
    if code == 0:
        require(field < 27 and p != q, 'factor or alias')
        return 'F', field, p, q, sign
    require(field in (0, 1, 2), 'scalar field')
    f = (-1, 1, 2)[field]
    require(code != 1 or p != q, 'root alias')
    require(code != 2 or (f in (-1, 1) and p == q), 'scale encoding')
    return ('R' if code == 1 else 'S'), f, p, q, sign


def width(L, D, H):
    # Three schedules and their literal inverses fit the same conservative bound.
    bound = 3**6 * max(1, D) * (1 + L*max(1, H))**308
    return (2*bound).bit_length() + 1


def control_bill(word, L, rows):
    F = sum(op[0] == 'F' for op in word)
    R = sum(op[0] == 'R' for op in word)
    S = len(word) - F - R
    n = len(word)
    cells = rows*L + 27*L*L
    return dict(program_bits=16*n, program_bit_reads=16*n,
                program_head_moves=32*n-2,
                instruction_decodes=n, decoder_masks_and_shifts=8*n,
                decoder_sign_arithmetic=2*n,
                seeks=3*F*L*L + 2*R*L + S*L + n,
                loop_resets=n + F*L,
                loop_tests=F*(L+1)**2 + (R+S)*(L+1),
                loop_increments=F*(L*L+L) + (R+S)*L,
                scalar_register_clears=3*(n+1),
                admission_reads=cells, admission_head_moves=2*(cells-1),
                mutable_words=rows*L, coefficient_words=27*L*L,
                numeric_registers=3,
                address_bits=max(1, cells.bit_length()))


def execute(word, initial, matrices, bits):
    """Data words are doubled numerators; coefficients are integers.

    LOAD overwrites owned scratch registers. CLEAR returns all three to zero.
    Each primitive starts and ends the data head at zero. No data copies exist.
    """
    rows, L = len(initial), len(initial[0])
    tape = [2*x for row in initial for x in row]
    tape += [x for matrix in matrices for row in matrix for x in row]
    registers = [0, 0, 0]
    pos = 0
    bill = dict(head_moves=0, coefficient_reads=0, source_reads=0,
                target_reads=0, target_writes=0, multiplications=0,
                dyadic_ops=0, additions=0, instructions=len(word),
                admission_reads=len(tape))
    peak = 0

    def bounded(x):
        nonlocal peak
        require(-(1 << (bits-1)) <= x < (1 << (bits-1)), 'word overflow')
        peak = max(peak, abs(x))
        return x

    for x in tape:
        bounded(x)

    def move(address):
        nonlocal pos
        require(0 <= address < len(tape), 'tape address')
        bill['head_moves'] += abs(address-pos)
        pos = address

    def load(address, register, category):
        move(address)
        bill[category] += 1
        registers[register] = tape[address]

    def write(address):
        require(pos == address, 'write at current head')
        tape[address] = bounded(registers[2])
        bill['target_writes'] += 1

    for literal in word:
        kind, f, p, q, sign = decode(encode(literal))
        require(p < rows and q < rows, 'row admission')
        if kind == 'F':
            for a in range(L):
                for b in range(L):
                    load(rows*L + f*L*L + a*L+b, 0, 'coefficient_reads')
                    load(p*L+b, 1, 'source_reads')
                    registers[1] = bounded(registers[0]*registers[1])
                    bill['multiplications'] += 1
                    load(q*L+a, 2, 'target_reads')
                    registers[2] = bounded(registers[2]+sign*registers[1])
                    bill['additions'] += 1
                    write(q*L+a)
        elif kind == 'R':
            for a in range(L):
                load(p*L+a, 1, 'source_reads')
                if abs(f) == 2:
                    registers[1] = bounded(2*registers[1])
                    bill['dyadic_ops'] += 1
                load(q*L+a, 2, 'target_reads')
                registers[2] = bounded(registers[2]+(1 if f*sign > 0 else -1)*registers[1])
                bill['additions'] += 1
                write(q*L+a)
        else:
            for a in range(L):
                load(q*L+a, 2, 'target_reads')
                if f*sign < 0:
                    require(registers[2] % 2 == 0, 'nonexact halving')
                    registers[2] //= 2
                else:
                    registers[2] = bounded(2*registers[2])
                bill['dyadic_ops'] += 1
                write(q*L+a)
        registers[:] = [0, 0, 0]
        move(0)
    require(registers == [0, 0, 0] and pos == 0, 'return contract')
    require(tape[rows*L:] == [x for M in matrices for row in M for x in row],
            'coefficient restoration')
    return [tape[i*L:(i+1)*L] for i in range(rows)], bill, peak


def matvec(M, v):
    return [sum(a*b for a, b in zip(row, v)) for row in M]


def direct(initial, matrices):
    # Independent mathematical model: evaluate the six product operators once.
    out = [[2*x for x in row] for row in initial]
    for j in range(3):
        v = initial[j][:]
        for f in GROUPS[j]:
            v = matvec(matrices[f], v)
        for i in range(3):
            t = v[:]
            for f in GROUPS[3+i]:
                t = matvec(matrices[f], t)
            out[3+i] = [a+2*TARGET[i][j]*b for a, b in zip(out[3+i], t)]
    return out


def main():
    receipt = json.loads((HERE/'two_root_invoice.json').read_text())
    words = receipt['literal_words']
    fixtures = 0
    max_bits_used = 0
    all_bills = {}
    rng = random.Random(20)
    for L in (1, 2, 3, 4):
        all_bills[str(L)] = {}
        for name, word in words.items():
            compact = name != 'two_root12'
            word = [(k, f, p-(compact and p>=8), q-(compact and q>=8), s)
                    for k, f, p, q, s in word]
            rows = 10 if compact else 11
            for _ in range(3):
                initial = [[rng.randrange(-3, 4) for _ in range(L)] for _ in range(rows)]
                matrices = [[[rng.randrange(-2, 3) for _ in range(L)] for _ in range(L)] for _ in range(27)]
                got, bill, peak = execute(word, initial, matrices, width(L, 3, 2))
                require(got == direct(initial, matrices), 'direct target mismatch')
                key = name+('_compact' if compact else '')
                require(bill == receipt['invoices'][str(L)][key], 'literal invoice mismatch')
                require(all(x % 2 == 0 for row in got for x in row), 'integer exit')
                inv = [(k,f,p,q,-s) for k,f,p,q,s in reversed(word)]
                # Use a fresh bound for the now larger input to the inverse.
                after = [[x//2 for x in row] for row in got]
                D = max(abs(x) for row in after for x in row)
                undone, _, _ = execute(inv, after, matrices, width(L,D,2))
                require(undone == [[2*x for x in row] for row in initial], 'literal inverse')
                fixtures += 1
                max_bits_used = max(max_bits_used, peak.bit_length()+1)
            all_bills[str(L)][name] = control_bill(word,L,rows)
    controls = []
    for label, thunk in [
        ('reserved opcode', lambda: decode(3 << 14)),
        ('factor alias', lambda: decode(encode(('F',0,2,2,1)))),
        ('word overflow', lambda: execute([('R',2,1,0,1)],[[7],[7]],[[[0]]]*27,4)),
        ('nonexact second halving', lambda: execute([('S',-1,0,0,1)]*2,[[1]],[[[0]]]*27,16)),
        ('missing row', lambda: execute([('R',1,1,0,1)],[[1]],[[[0]]]*27,16)),
    ]:
        try:
            thunk()
        except ValueError:
            controls.append(label)
        else:
            raise ValueError('missed control '+label)
    result = dict(status='PASS_TWO_ROOT_MACHINE',fixtures=fixtures,
                  inverse_fixtures=fixtures,controls=controls,
                  maximum_observed_signed_bits=max_bits_used,controller=all_bills,
                  scope='Exact bounded integer model. Three owned clean numeric registers; arbitrary dirty array restoration. No native supplier, bit-time comparison, or kappa.')
    (HERE/'two_root_machine.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS_TWO_ROOT_MACHINE fixtures='+str(fixtures)+' controls='+str(len(controls)))


if __name__ == '__main__':
    main()
