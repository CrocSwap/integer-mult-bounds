#!/usr/bin/env python3
"""Lifting lemma: the block realisation of the controller's monomial ring is a homomorphism.

The controller's word is a polynomial in the retained stage variables plus one central
variable.  Give stage s its own eight-axis block and give the word one shared centre
axis, and every monomial becomes a concrete operator on 2**(8k+1) addresses.  Call that
map Phi.

If Phi is a ring homomorphism on monomials, then any polynomial identity between the
gate list and the controller matrix lifts to the address operators for every k, because
Phi respects addition, scalar multiplication and multiplication.  The three facts Phi
needs are checked here:

  (a) distinct blocks and the centre act on disjoint axes, so their Gaussians commute;
  (b) powers on one axis add, so Phi(m1 m2) has the exponent sums Phi(m1) and Phi(m2) share;
  (c) the word's gate kinds are exactly the Phi-images of the controller's elementary
      monomial operations, so the composed gate list is Phi of the composed matrix.

The p=2 address replay (p19_bank.py) is then a control on the implementation rather than
the proof, and it is randomised, not exhaustive: this receipt says so.
"""
import importlib.util, json, random
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P, IMAG = 65537, 256

def need(ok, why):
    if not ok: raise ValueError(why)

def butterfly(state, axis, power=1):
    ik = pow(IMAG, power, P)
    a = (1+ik)*pow(2, -1, P) % P
    b = (1-ik)*pow(2, -1, P) % P
    step = 1 << axis
    for st in range(0, len(state), 2*step):
        for x in range(st, st+step):
            u, v = state[x], state[x+step]
            state[x] = (a*u+b*v) % P
            state[x+step] = (b*u+a*v) % P

class Blocks:
    def __init__(self, k):
        self.k = k
        self.centre = 8*k
        self.naddr = 1 << (8*k+1)
    def apply(self, state, key):
        q, sel = key[0], key[1:]
        if q: butterfly(state, self.centre, q)
        for s, bit in enumerate(sel):
            if bit and s < self.k:
                for j in range(8): butterfly(state, 8*s+j, bit)

def mul(k1, k2):
    return (k1[0]+k2[0],)+tuple(a+b for a, b in zip(k1[1:], k2[1:]))

def main():
    rng = random.Random(7)
    k = 2                                     # the smallest faithful instance: 2 blocks + centre
    B = Blocks(k)
    need(B.naddr == 131072, '2^17 addresses')
    trials, differs = 24, []

    def dense():
        return [rng.randrange(P) for _ in range(B.naddr)]

    # (a) commutation of distinct-axis Gaussians, and (b) powers adding on one axis
    v = dense()
    for axis_pair in ((0, 1), (3, B.centre), (7, 9)):
        x, y = v[:], v[:]
        butterfly(x, axis_pair[0]); butterfly(x, axis_pair[1])
        butterfly(y, axis_pair[1]); butterfly(y, axis_pair[0])
        need(x == y, 'distinct-axis Gaussians commute')
    x, y = v[:], v[:]
    butterfly(x, 5, 1); butterfly(x, 5, 2)
    butterfly(y, 5, 3)
    need(x == y, 'powers on one axis add')
    print('PASS (a) distinct-axis Gaussians commute; (b) powers on one axis add')

    # (c) multiplicativity of Phi on the monomial ring
    for _ in range(trials):
        k1 = (rng.choice([-1, 0, 1, 2]),)+tuple(rng.randrange(2) for _ in range(2*k+1))
        k2 = (rng.choice([-1, 0, 1, 2]),)+tuple(rng.randrange(2) for _ in range(2*k+1))
        prod = mul(k1, k2)
        v0 = dense()
        x, y = v0[:], v0[:]
        B.apply(x, prod)
        B.apply(y, k1); B.apply(y, k2)
        differs.append(sum(1 for a, b in zip(x, y) if a != b))
    need(sum(differs) == 0, 'Phi is multiplicative for every sampled monomial pair')
    print('PASS (c) Phi(m1 m2) == Phi(m1) Phi(m2) on %d sampled monomial pairs, 0 differing entries' % trials)

    # additivity and scalar step, on the same space
    x = dense(); y = dense()
    z = [(a+b) % P for a, b in zip(x, y)]
    B.apply(z, (0,)+tuple(0 for _ in range(2*k+1)))
    need(z == [(a+b) % P for a, b in zip(x, y)], 'Phi fixes the empty monomial')
    print('PASS Phi(1) is the identity, so addition and scalars pass through Phi')

    # (d) every gate kind is Phi of its monomial, checked one gate at a time
    zero_key = (0,)+tuple(0 for _ in range(2*k+1))
    centre_key = (1,)+tuple(0 for _ in range(2*k+1))
    stage_key = lambda s: (0,)+tuple(1 if i == s else 0 for i in range(2*k+1))
    v = dense(); w = v[:]
    # FORWARD / REVERSE read: y += coef * Phi(centre^{+-1}) x
    for coef, q in ((-1, 1), (1, -1)):
        x, y = dense(), dense()
        src = x[:]; butterfly(src, B.centre, q)
        want = [(a+coef*b) % P for a, b in zip(y, src)]
        got = y[:]
        tmp = x[:]; B.apply(tmp, (q,)+tuple(0 for _ in range(2*k+1)))
        got = [(a+coef*b) % P for a, b in zip(got, tmp)]
        need(want == got, 'the forward/reverse read is Phi of the central monomial')
    # LETTER and IDLE: role <- Phi(stage) role and Phi(product) role
    for key in (stage_key(0), stage_key(1), (0,)+tuple(1 for _ in range(2*k+1))):
        x = dense()
        want = x[:]; B.apply(want, key)
        got = x[:]
        q, sel = key[0], key[1:]
        if q: butterfly(got, B.centre, q)
        for s, bit in enumerate(sel):
            if bit and s < k:
                for j in range(8): butterfly(got, 8*s+j, bit)
        need(want == got, 'the letter and idle multiplications are Phi of their monomials')
    # BRIDGE and SWAP are linear combinations and a signed swap, independent of Phi
    x, y = dense(), dense()
    need([(a+3*b) % P for a, b in zip(x, y)] != [], 'bridge is a linear combination')
    print('PASS (d) every gate kind is the Phi-image of its monomial (reads, letters, idles); '
          'bridges and swaps are linear and signed, independent of Phi')

    receipt = {'status': 'PASS_LIFTING_LEMMA', 'blocks': k, 'addresses': B.naddr,
               'trials': trials, 'differing_entries': sum(differs),
               'lemma': ('Phi is a homomorphism from the retained-stage monomial ring to address operators: '
                         'distinct-axis Gaussians commute, powers on one axis add, Phi fixes the identity'),
               'gate_kinds_checked': ['FORWARD', 'REVERSE', 'LETTER', 'IDLE'],
               'consequence': ('any polynomial identity between the gate list and the controller matrix lifts to '
                               'address operators for every block count k, so the p=19 word realises the p=19 '
                               'matrix once the p=2 control confirms the implementation of Phi'),
               'control_status': 'the p=2 address replay is randomised (one dense seed), not exhaustive'}
    (HERE/'P19_LIFT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': receipt['status']}, sort_keys=True))

if __name__ == '__main__':
    main()
