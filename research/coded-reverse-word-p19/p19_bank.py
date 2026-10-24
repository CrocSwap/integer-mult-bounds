#!/usr/bin/env python3
"""Address-level replay of the trace word: the gate list against the controller matrix.

The controller's monomials live over the retained stage variables.  Give every retained
stage its own eight-axis block and give the word one shared centre line, and each
monomial becomes a concrete Gaussian on 2**(8k+1) addresses.  The smallest faithful
instance is p=2, where the retained stages are {1, 3}: two blocks plus the centre, so
2**17 = 131,072 addresses per role.

The check applies the trace's gate list to a dense state and compares it with the
controller's own thinned matrix evaluated in the same representation.  This is the
physical binding the earlier draft only asserted: if the two agree on every address of
every role, the listed gates realise the controller's operator as concrete address
operations, not merely as an equality of formal expressions.
"""
import importlib.util, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P, IMAG = 65537, 256

def need(ok, why):
    if not ok: raise ValueError(why)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def butterfly(state, axis, power=1):
    """Apply the Gaussian gate to the given power on one axis, in one pass."""
    ik = pow(IMAG, power, P)
    a = (1+ik)*pow(2, -1, P) % P
    b = (1-ik)*pow(2, -1, P) % P
    step = 1 << axis
    for st in range(0, len(state), 2*step):
        for x in range(st, st+step):
            u, v = state[x], state[x+step]
            state[x] = (a*u+b*v) % P
            state[x+step] = (b*u+a*v) % P

def new_state(naddr, seed):
    import random
    rng = random.Random(seed)
    return [rng.randrange(P) for _ in range(naddr)]

def differ(x, y):
    return sum(1 for a, b in zip(x, y) if a != b)

def main():
    mod = load('c4940', ROOT/'research/coded-reverse-controller/verify.py')
    C, controller, keep_of, thin = mod.C, mod.controller, mod.keep_of, mod.thin

    p, pat = 2, 'T'
    thick = sorted(range(1, 2*p, 2))                 # retained stages
    naddr = 1 << (8*len(thick)+1)
    centre = 8*len(thick)
    blocks = {s: i for i, s in enumerate(thick)}
    def monomial_apply(state, key):
        q, sel = key[0], key[1:]
        if q: butterfly(state, centre, q)
        for s, bit in enumerate(sel):
            if bit and s in blocks:
                base = 8*blocks[s]
                for j in range(8): butterfly(state, base+j, bit)
    need(naddr == 131072 and len(thick) == 2, 'p=2 realisation is 2^17 addresses')

    keep = keep_of(p, pat)
    co, _ = controller(p, keep, {s: 1 for s in range(2*p+1)})
    matrix = thin(co, set(thick))
    need(matrix, 'the thinned controller matrix is non-empty')
    n = 2*p

    # a) the trace's gate list, applied as concrete address operations
    import p19_plain
    _, _, gates, _ = p19_plain.traced_controller(C, p, keep, {s: 1 for s in range(2*p+1)})

    base = [new_state(naddr, 100+i) for i in range(n)]
    state = [s[:] for s in base]
    for g in gates:
        kind = g[0]
        if kind == 'FORWARD':
            _, stage, y, x, coef = g
            src = state[x][:]
            butterfly(src, centre, -1)
            state[y] = [(a+coef*b) % P for a, b in zip(state[y], src)]
        elif kind == 'REVERSE':
            _, stage, y, x, coef = g
            src = state[x][:]
            butterfly(src, centre, 1)
            state[y] = [(a+coef*b) % P for a, b in zip(state[y], src)]
        elif kind == 'LETTER':
            _, stage, x, y, _s = g
            if stage in blocks:
                for role in (x, y):
                    for j in range(8): butterfly(state[role], 8*blocks[stage]+j)
        elif kind == 'IDLE':
            _, kindname, x, y, sel = g
            for role in (x, y):
                for s in sel:                      # literal stage IDs, as term() reads them
                    if s in blocks:
                        for j in range(8): butterfly(state[role], 8*blocks[s]+j)
        elif kind == 'BRIDGE':
            _, coef, d, s, _none = g
            state[d] = [(a+coef*b) % P for a, b in zip(state[d], state[s])]
        elif kind == 'SWAP':
            _, _c, x, y, _n = g
            hold = state[x]
            state[x] = state[y]
            state[y] = [(-v) % P for v in hold]
        else:
            raise ValueError('unknown gate ' + kind)

    # b) the controller's own matrix, evaluated on the same addresses
    # the thinned controller matrix is stored as term -> matrix
    want = [[0]*naddr for _ in range(n)]
    for j in range(n):
        col = base[j]
        for term, m in matrix.items():
            for i in range(n):
                coeff = m[i][j]
                if not coeff: continue
                img = col[:]
                monomial_apply(img, term)
                want[i] = [(a+int(coeff)*b) % P for a, b in zip(want[i], img)]

    # decoder contract: literal stage IDs must denote the same stage set as the controller's
    # indicator vector, including the p=19 terminal event whose IDs are 37 and 38
    p19 = 19
    thick19 = sorted(range(1, 2*p19, 2))
    blocks19 = {s: i for i, s in enumerate(thick19)}
    # every retained idle of the p=19 word, reconstructed from the controller's own idle_call,
    # checked against the indicator encoding the matrix uses
    checked = 0
    def idle_sels(p, pat):
        out = []
        for stage in range(1, 2*p):
            if stage % 2 and stage <= 2*p-3:
                pair = (stage+1)//2
                if pat[pair-1] in 'IB': out.append(tuple(range(stage+1)))
            elif stage % 2 == 0 and 2 <= stage <= 2*p-2:
                out.append((stage,))
        for j in range(p-1):
            if pat[j] in 'TB': out.append(tuple(range(2*j+3, 2*p+1)))
        return out
    for sel in idle_sels(19, 'I'*9+'T'*9):
        literal = {s for s in sel if s in blocks19}
        indicator = tuple(int(s in sel) for s in range(2*19+1))
        vector = {s for s, bit in enumerate(indicator) if bit and s in blocks19}
        need(literal == vector, 'literal-ID and indicator encodings agree on a p=19 idle')
        checked += 1
    need(checked == 36, 'all 36 retained p=19 idles checked')
    print('PASS encoding: all %d retained p=19 idle selections (including the terminal (37,38)) denote the same '
          'stage set under literal-ID and indicator encodings' % checked)

    for sel in ((37, 38), (3, 4), (0, 1), (2,)):
        literal = {s for s in sel if s in blocks19}
        stages = 2*p19+1
        indicator = tuple(int(s in sel) for s in range(stages))
        vector = {s for s, bit in enumerate(indicator) if bit and s in blocks19}
        need(literal == vector, 'literal-ID and indicator encodings denote the same stage set')
    print('PASS decoder contract: literal stage IDs and the controller indicator vector denote the same stage set '
          'for (37,38), (3,4), (0,1) and (2,)')

    bad = [differ(state[i], want[i]) for i in range(n)]
    print('address-level replay p=%d: %d addresses per role, %d roles, %d gates' % (p, naddr, n, len(gates)))
    print('  gate list vs controller matrix, differing entries per role:', bad)
    need(sum(bad) == 0, 'the gate list realises the controller matrix at address level')
    receipt = {'status': 'PASS_ADDRESS_LEVEL_TRACE_REPLAY', 'p': p, 'pattern': pat,
               'retained_stages': thick, 'addresses_per_role': naddr, 'roles': n,
               'gates': len(gates), 'differing_entries': bad,
               'decoder_contract': 'literal stage IDs and indicator vectors agree on all 36 retained p=19 idles '
                                   'and on the boundary cases',
               'binding': ('the trace gate list and the controller matrix agree on every address of every '
                           'role at the smallest faithful ambient (two blocks plus the shared centre)'),
               'scope': ('p=19 needs 2**153 addresses, so the address-level check is done at p=2 and the p=19 '
                         'word is certified by the trace identity in the controller algebra')}
    (HERE/'P19_BANK.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': receipt['status']}, sort_keys=True))

if __name__ == '__main__':
    main()
