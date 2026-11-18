#!/usr/bin/env python3
"""Independent exact check of a banked circuit against a source word (standard library only).

usage: certify.py WORD CIRCUIT [--caller CALLER] [--frames GRAPH] [--columns] [--reference REF_CIRCUIT] [--claim K]

Checks, each fatal on failure:
  1. locality (every donor is cocharted with its reader) and an acyclic schedule;
  2. every paid edge joins GF(2)-nested charts with positive rank, and the symplectic rank of T_b T_a^-1 equals
     |dim b - dim a|;
  3. (--columns) for every paid chart pair that is not a MOVE of the word, an exact Gaussian state simulation spreads
     each of the 512 columns over exactly 2^r basis states of equal modulus;
  4. exact rational outputs: without --reference, every main output equals the fold of WORD and every helper (including
     fresh roles) returns its own input; with --reference, every output equals the reference circuit's output;
  5. PRICEKIT invoice of the circuit on CALLER (helper targets from the circuit's own boundary) and a certified
     enclosure of the crossing; with --claim, the certified lower end must exceed K.
--frames takes the chart frames from another JSON file with a 'frames' list (for example a published banked graph)."""
import sys, os, json, hashlib, argparse
from fractions import Fraction as Q
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bank
from bank import load, fold, schedule, hist, load_circuit, pk
from exval import exact_values
import nest, phys, gauss


class CertifyError(Exception):
    pass


def need(c, m):
    if not c: raise CertifyError(m)


def mains_of(W):
    h = W['hosted']
    return set(W['live']) | {r + 112 for r in W['live']} | set(h.get('X2', [])) | set(h.get('Y2', []))


def canon_sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def certify(W, net, frames=None, columns=False, reference=None, caller=None, digits=30, log=print):
    fr = frames if frames is not None else W['frames']; dim = [len(f) for f in fr]
    schedule(net); log('1. locality + acyclic schedule: PASS (%d paid edges, %d public roles)' % (len(net.moves), len(net.init)))
    pairs = sorted(set(net.moves.values()))
    for a, b in pairs:
        r = nest.trank(fr, a, b)
        need(r is not None and r > 0, 'edge %s not nested or rank 0' % ((a, b),))
        need(phys.trank(fr[a], fr[b]) == r, 'symplectic rank of %s' % ((a, b),))
    log('2. %d distinct chart pairs nested, positive rank, symplectic rank = |dim diff|: PASS' % len(pairs))
    if columns:
        wordpairs = {(e[2], e[3]) for e in W['program'] if e[0] == 'MOVE'}
        newp = [p for p in pairs if p not in wordpairs]
        for a, b in newp:
            need(gauss.column_rank(fr[a], fr[b]) == abs(dim[a] - dim[b]), 'Gaussian column rank %s' % ((a, b),))
        log('3. %d pairs outside the word: Gaussian column rank = |dim diff| on all 512 columns: PASS' % len(newp))
    EVc = exact_values(net); n = len(net.init); mains = mains_of(W)
    if reference is None:
        ref = fold(W); EVr = exact_values(ref)
        need(all(EVc[net.first + r] == EVr[ref.first + r] for r in mains), 'a main output differs from the word')
        need(all(net.final[r] == W['final'][r] and net.init[r] == W['initial'][r] for r in mains), 'a main endpoint differs')
        need(all(EVc[net.first + r] == {r: Q(1)} for r in range(n) if r not in mains), 'a helper does not return its input')
        log('4. EXACT: %d main outputs equal the word (canonical SHA-256 %s); %d helpers return their own input: PASS'
            % (len(mains), canon_sha(W)[:16], n - len(mains)))
    else:
        EVr = exact_values(reference)
        need(reference.init == net.init and reference.final == net.final, 'boundary differs from the reference')
        need(all(EVc[net.first + r] == EVr[reference.first + r] for r in range(n)), 'an output differs from the reference')
        log('4. EXACT: all %d outputs equal the reference circuit: PASS' % n)
    if caller: bank.CALLER = caller
    pr, inv = bank.price_net(W, net, dim, digits)
    k = pr['kappa']; need(k['status'] == 'OK', 'no certified unique crossing')
    log('5. paid/native %d, paid %d, targets %d, S %d; crossing in (%s, %s)' % (
        sum(hist(net, dim).values()), pr['paid_jobs'], sum(inv['T'].values()), pr['S'], str(k['lo'])[:20], str(k['hi'])[:20]))
    return pr, inv


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('word'); ap.add_argument('circuit')
    ap.add_argument('--caller'); ap.add_argument('--frames'); ap.add_argument('--reference'); ap.add_argument('--claim')
    ap.add_argument('--columns', action='store_true')
    a = ap.parse_args(argv)
    W = load(a.word); net = load_circuit(a.circuit)
    fr = load(a.frames)['frames'] if a.frames else None
    ref = load_circuit(a.reference) if a.reference else None
    try:
        pr, _ = certify(W, net, fr, a.columns, ref, a.caller)
        if a.claim: need(Q(str(pr['kappa']['lo'])) > Q(a.claim), 'certified lower end is not above %s' % a.claim)
    except (CertifyError, AssertionError) as e:
        print('FAIL:', e); return 1
    print(pk.cite(os.path.basename(a.circuit), pr))
    print('PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
