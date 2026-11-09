"""Root cut arithmetic (THEOREM.md section 6): the closed form 8[f(18) + 2 f(9)] + 87.35 = 819.97 per chain, read from the mask incidences of the two
all-pivot roots, with the scope controls. f(x) = x ln x. 50-digit decimal arithmetic; standard library only. Prints 'ok   ' lines and PASS_ROOTCUT."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decimal import Decimal, getcontext
from collections import Counter
from common import req, finish
from rootmodel import load_root, merged_word

getcontext().prec = 50


def f(x):
    return Decimal(0) if x == 0 else Decimal(x) * Decimal(x).ln()


def hub_term(L, body):
    return f(body * L + 1) - L * f(body)


def own_term(m, body):
    return f(body * m + 1) - f(body * (m - 1)) - f(body)


def cut_chain(L, body=8):
    """one hub of incidence L and two arms of own fields with incidences 1..L/2"""
    return hub_term(L, body) + 2 * sum(own_term(m, body) for m in range(1, L // 2 + 1))


def closed_form(L, body=8):
    remainder = (f(body * L + 1) - f(body * L)) + 2 * sum(f(body * m + 1) - f(body * m) for m in range(1, L // 2 + 1))
    return body * (f(L) + 2 * f(L // 2)) + remainder, remainder


def main():
    # identity f(8a) = a f(8) + 8 f(a)
    ident = all(abs(f(8 * a) - a * f(8) - 8 * f(a)) < Decimal(10) ** -40 for a in range(1, 40))
    req(ident, 'identity f(8a) - a f(8) = 8 f(a) for a = 1..39 (50 digits)')
    # the incidence multiset of the data: two hubs of incidence 18, four own fields of each incidence 1..9
    for name in ('root_h.json', 'root_t0_dsum.json'):
        W = load_root(name)
        inc = Counter(sum(1 for lab in W.labels if c in lab['mask']) for c in range(W.n))
        inc.pop(0, None)
        want = Counter({18: 2, **{m: 4 for m in range(1, 10)}})
        req(inc == want, '%s: nonzero field incidences = two hubs of 18 and four fields of each incidence 1..9 (sum %d)' % (name, sum(k * v for k, v in inc.items())))
    # total cut from the incidences, per root, and the closed form per chain
    inc = Counter({18: 2, **{m: 4 for m in range(1, 10)}})
    total = inc[18] * hub_term(18, 8) + sum(inc[m] * own_term(m, 8) for m in range(1, 10))
    chain = cut_chain(18)
    cf, rem = closed_form(18)
    req(abs(total - 2 * chain) < Decimal(10) ** -40, 'cut summed over the fields of a root = 2 x cut per chain')
    req(abs(chain - cf) < Decimal(10) ** -40, 'cut per chain = 8[f(18) + 2 f(9)] + remainder exactly (50 digits)')
    req(abs(chain - Decimal('819.9667')) < Decimal('0.0005') and abs(8 * (f(18) + 2 * f(9)) - Decimal('732.6139')) < Decimal('0.0005') and abs(rem - Decimal('87.3528')) < Decimal('0.0005'),
        'values: cut per chain %.4f = %.4f + %.4f, two chains %.4f' % (chain, 8 * (f(18) + 2 * f(9)), rem, 2 * chain))
    req(abs(hub_term(18, 8) - Decimal('422.1868')) < Decimal('0.0005') and abs(2 * sum(own_term(m, 8) for m in range(1, 10)) - Decimal('397.7799')) < Decimal('0.0005'),
        'split: hub part %.4f, arm part %.4f' % (hub_term(18, 8), 2 * sum(own_term(m, 8) for m in range(1, 10))))
    # t is not an input among all-pivot words: the two roots have the same incidences, hence the same cut
    h = load_root('root_h.json')
    z = load_root('root_t0_dsum.json')
    ih = Counter(sum(1 for lab in h.labels if c in lab['mask']) for c in range(h.n))
    iz = Counter(sum(1 for lab in z.labels if c in lab['mask']) for c in range(z.n))
    ih.pop(0, None); iz.pop(0, None)
    req(ih == iz, 'all-pivot roots at t = -1/2 and t = 0 have the same incidence multiset, so the same cut')
    # outside the scope: words with an interior stage at t = -1 have a different multiset (total below 216)
    base = z
    for J in (4, 7):
        M = merged_word(base, J)
        im = Counter(sum(1 for lab in M.labels if c in lab['mask']) for c in range(M.n))
        tot = sum(k * v for k, v in im.items())
        req(im != Counter({0: im[0], **inc}) and tot < 216, 'merged J=%d: incidence multiset differs from the all-pivot one (total %d < 216), so the closed form does not apply' % (J, tot))
    # controls: the body and the remainder are inputs; a wrong closed form is rejected
    req(abs(cut_chain(18, 7) - chain) > 90 and abs(cut_chain(18, 9) - chain) > 90, 'control: body 7 and body 9 move the cut by more than 90 (the body 8 is an input)')
    req(abs(8 * (f(18) + 2 * f(9)) - chain) > 80, 'control: the entropy part alone (without the 87.35 remainder) is not the cut')
    req(abs(cut_chain(18) - cut_chain(17)) > 1, 'control: the formula is sensitive to the stage count L (L = 17 differs)')
    finish('PASS_ROOTCUT')


if __name__ == '__main__':
    main()
