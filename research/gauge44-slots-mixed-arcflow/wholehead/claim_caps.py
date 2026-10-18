#!/usr/bin/env python3
"""Write or check CLAIM.json: the six packages of PR #1175 in the queue-census field names, each with its paid local
profile's packing cap under research/complex-local-word-ceiling's model and the fraction of that cap realised.

For every package: live stock W, calls N, the global paid profile and idle histogram (from data/SPEC.json), the local
profile per call (= the provider's actual_paid_profile; the global profile minus the idle histogram, divided by N), the
word's content SHA256, the exact kappa and complex endpoint (RESULT.json), the cap bracket of ceiling.ceiling() on the
local profile (m = 73, 2*4*112 live families per replica, 9 stages, centre 64, idle ranks <= 51), and
realised = kappa / kappa_cap. Also recorded: the stock-feasible optimum (every idle unit in a rank-48 child, the largest
bin of the retained template) and whether the package's map attains it.

Usage: claim_caps.py --main ROOT [--write]      (standard library; about 20 s)
Prepared by G. V. Chudnovsky with Anthropic Claude assistance. Apache-2.0.
"""
import argparse, gzip, hashlib, json, sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGES = [('research/gauge44-slots-arcflow', 8, 'slot word c2b29430 (#1018), arc-flow owner map'),
            ('research/gauge44-slots-t16-arcflow', 16, 'slot word c2b29430, sixteen replicas on the arc-flow map'),
            ('research/gauge44-slots-unpromo-arcflow', 8, 'sixteen restored dimension-four entrances (word 4ffb07de)'),
            ('research/gauge44-slots-deepen-arcflow', 8, 'ten deepened ends on the restored word (word 6ace902a), perfectly packed'),
            ('research/gauge44-slots-balance-arcflow', 8, 'fourteen restored entrances and ten deepened ends on the slot word (word a684e7c8), perfectly packed'),
            ('research/gauge44-slots-mixed-arcflow', 8, 'two providers mixed by replica parity: sixteen (6ace902a) and twelve (69c93a05) restored entrances with ten deepened ends, perfectly packed')]
M, PAIRS, PORTS, STAGES, CENTRE = 73, 4, 112, 9, 64
FAMILIES = 2 * PAIRS * PORTS


def read(p):
    b = Path(p).read_bytes(); return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)


def dec(q, digits=19):
    return '0.' + str(q.numerator * 10 ** digits // q.denominator).zfill(digits)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--main', type=Path, required=True); ap.add_argument('--write', action='store_true')
    a = ap.parse_args(); root = a.main.resolve()
    sys.path.insert(0, str(root / 'research/complex-local-word-ceiling'))
    import ceiling as C
    claims = []
    for rel, T, note in PACKAGES:
        p = root / rel; res = read(p / 'RESULT.json'); spec = read(p / 'data/SPEC.json'); plan = read(p / 'data/PLAN.json')
        W, N = 896 * T, 9 * T
        glob = {int(k): v for k, v in spec['expected']['global_profile'].items()}
        idle = {int(k): v for k, v in spec['expected']['idle_remainder_profile'].items()}
        regs = plan['provider_registry']; calls = Counter(c['provider'] for c in plan['provider_calls'])
        local = {}
        for pid, reg in regs.items():
            for k, v in reg['actual_paid_profile'].items(): local[int(k)] = local.get(int(k), 0) + Q(calls[pid] * v, N)
        local = {r: (int(v) if v.denominator == 1 else v) for r, v in local.items()}
        assert all(glob.get(r, 0) - idle.get(r, 0) == N * local.get(r, 0) for r in set(glob) | set(idle) | set(local)), rel
        mass = sum(r * n for r, n in glob.items()); assert mass == (M - 1) * W + CENTRE * N, rel
        lo, hi = C.ceiling(local, M, FAMILIES, STAGES, CENTRE)
        kcap = hi / (1 + hi); kappa = Q(res['kappa'])
        # stock-feasible optimum: all idle mass in rank-48 children (the retained template's largest idle bin)
        q = C.model(local, M, FAMILIES, STAGES, CENTRE); idle_mass = q['idle_mass'] * N
        assert idle_mass == sum(r * n for r, n in idle.items()), rel
        rank48 = {r: int(N * n) for r, n in local.items()}; rank48[48] = rank48.get(48, 0) + idle_mass // 48; rem = idle_mass % 48
        if rem: rank48[rem] = rank48.get(rem, 0) + 1
        at_stock_optimum = (idle == {48: idle_mass // 48} if rem == 0 else False)
        word_sha = {pid: spec['providers'][pid]['artifact_semantic_sha256']['CANONICAL-WORD.json.gz'] for pid in regs}
        if len(word_sha) == 1: word_sha = next(iter(word_sha.values()))
        claims.append(dict(pr=1175, package=rel, note=note, T=T, live=W, calls=N,
                           kappa=res['kappa'], kappa_decimal=res['kappa_decimal'], complex_lower=res['complex_lower'],
                           local_profile_per_call={str(r): (n if isinstance(n, int) else str(n)) for r, n in sorted(local.items())},
                           providers={pid: dict(calls=calls[pid], local_profile=regs[pid]['actual_paid_profile']) for pid in regs} if len(regs) > 1 else None,
                           idle_histogram={str(r): n for r, n in sorted(idle.items())},
                           global_profile={str(r): n for r, n in sorted(glob.items())}, rank_mass=mass,
                           canonical_word_content_sha256=word_sha,
                           cap=dict(model='research/complex-local-word-ceiling/ceiling.py: hosting, owner and idle repacking of this local word; '
                                          'idle ranks <= 51; coverage law mass = 72W + 64N', a_bracket=[str(lo), str(hi)],
                                    kappa_cap=str(kcap), kappa_cap_decimal=dec(kcap), realised_fraction=dec(kappa / kcap, 6),
                                    below_cap_percent=dec((1 - kappa / kcap) * 100, 4)),
                           stock_feasible_optimum=dict(idle_histogram={str(r): n for r, n in sorted(rank48.items()) if r not in local or r == 48},
                                                       attained=at_stock_optimum,
                                                       note='every idle unit in a rank-48 child, the largest idle bin of the retained template')))
        print(rel, 'kappa', res['kappa_decimal'], 'cap', dec(kcap, 10), 'realised', claims[-1]['cap']['realised_fraction'],
              'stock optimum attained', at_stock_optimum, flush=True)
    out = dict(schema='pr1175-claims/3', head_kappa='0.001675867534384272',
               head_kappa_package='research/gauge44-slots-mixed-arcflow (RESULT.json kappa_decimal, data/SPEC.json expected.kappa_decimal, '
                                  'construction/mixed/MIXED-PINS-k8.json kappa_decimal)',
               selected_record=dict(pr=1094, kappa_decimal='0.001672660197076918'),
               claims=claims,
               scope='Census field names (research/complex-queue-ceiling-census) for the six packages of PR #1175; caps are the '
                     'planning bounds of the cited ceiling model, not attainable optima of the retained template (whose idle bins '
                     'have ranks 8, 16, 32 and 48, so rank-48 children are the cheapest hosts actually available).')
    text = json.dumps(out, indent=1) + '\n'
    target = HERE.parent / 'CLAIM.json'
    if a.write:
        target.write_text(text); print('wrote', target)
    else:
        assert target.read_text() == text, 'CLAIM.json differs from this recomputation'
        print('PASS_CLAIM_CAPS', len(claims))


if __name__ == '__main__':
    main()
