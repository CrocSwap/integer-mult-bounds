"""Reference-root pricing, with outward transcendental enclosures. Apache-2.0.

Brian Ross with substantial OpenAI Codex assistance. Reuses, with attribution,
woklerx PR1182's certified bisection and flemhhh PR1048's interval arithmetic.
No claim of arbitrary fixed-exponent ordering or neighborhood exhaustion.
"""
from fractions import Fraction as Q
from functools import lru_cache
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


old = load('pr1048_arithmetic', ROOT / 'research/bit-profile-pair-audit/code/bitprof.py')
repair = load('pr1182_bracket', ROOT / 'research/profile-bracket-audit64/repair.py')


def profile(p, m=64):
    need(isinstance(p, dict) and p, 'nonempty profile required')
    need(all(type(r) is int and 1 <= r <= m and type(c) is int and c >= 0
             for r, c in p.items()), 'nonnegative integer supported profile required')
    p = {r: c for r, c in p.items() if c}
    need(p, 'positive call count required')
    return p


def outward(lo, hi, digits=48):
    need(lo <= hi, 'invalid enclosure')
    scale = 10 ** digits
    a, b = lo * scale, hi * scale
    return Q(a.numerator // a.denominator, scale), Q(-(-b.numerator // b.denominator), scale)


@lru_cache(maxsize=256)
def rank_weight(rank, lower, upper, terms=34):
    """Enclose r**(1-a) for every a in [lower, upper], r>=1.

    exp(a*ln(r)) is positive and increasing, so invert/reverse both bounds.
    The frozen exp routine requires its entire argument interval in [0,1].
    """
    need(type(rank) is int and 1 <= rank <= 64, 'rank outside fixed domain')
    need(Q(0) <= lower <= upper <= Q(1, 10), 'exponent outside fixed domain')
    need(type(terms) is int and 1 <= terms <= 136, 'term budget')
    if rank == 1:
        return Q(1), Q(1)
    ll, lh = old.ln_bounds(Q(rank), terms)
    need(0 <= ll <= lh and upper * lh <= 1, 'exp envelope violated')
    elo = old.exp_bounds(lower * ll, terms)[0]
    ehi = old.exp_bounds(upper * lh, terms)[1]
    need(0 < elo <= ehi, 'positive exponential enclosure required')
    return outward(Q(rank) / ehi, Q(rank) / elo)


def signed_price(delta, lower, upper, m=64, terms=34):
    """Signed J_delta bounds; never pass signed counts to a positive oracle."""
    need(m == 64, 'fixed m=64 only')
    need(all(type(r) is int and 1 <= r <= m and type(c) is int
             for r, c in delta.items()), 'integer signed delta required')
    surcharge = Q(32 * m * m, 10 ** 16) * sum(delta.values())
    lo = hi = surcharge
    for r, c in sorted(delta.items()):
        if not c:
            continue
        a, b = rank_weight(r, lower, upper, terms)
        lo += c * (a if c > 0 else b)
        hi += c * (b if c > 0 else a)
    return lo, hi


class ReferencePricer:
    """Fixed PR589 pipeline and idle profile; no float acceptance decisions.

    Each candidate is a local integer profile with the same m,W, replication
    and idle profile. Continuous F_n is strictly increasing because its
    surcharge has positive coefficient and m>1. F_n(0)<0 plus unboundedness
    then proves a unique positive root, also for the candidate.
    """
    def __init__(self, local=None, *, digits=24, terms=34, max_terms=136):
        e = json.loads((ROOT / 'research/bit-profile-pair-audit/EXPECTED.json').read_text())
        pipeline = e['pipeline']
        need(pipeline['m'] == 64 and pipeline['W'] == 28416 and
             pipeline['T'] == 32 and pipeline['L'] == 9, 'fixed pipeline mismatch')
        self.m, self.W, self.factor = 64, 28416, 288
        self.idle = {int(r): c for r, c in pipeline['idle_remainder'].items()}
        self.local = profile(local if local is not None else
                             {int(r): c for r, c in e['tuned_word']['profile'].items()})
        self.terms = terms
        self.global_base = self.globalize(self.local)
        self.oracle = repair.profile_oracle(old, self.global_base, self.m, self.W, True)
        self.bracket_result = repair.bracket(self.oracle, digits, terms, max_terms)
        bounds = self.bracket_result['certified_bracket']
        self.bounds = tuple(map(Q, bounds)) if bounds else None
        if self.bounds:
            # Recheck final signs, including when a capped search retained a wider bracket.
            for x, sign, nterms in zip(self.bounds, (-1, 1), self.bracket_result['endpoint_terms']):
                need(repair.classify(*self.oracle(x, nterms)) == sign, 'uncertified final endpoint')

    def globalize(self, p):
        p = profile(p)
        out = dict(self.idle)
        for r, c in p.items():
            out[r] = out.get(r, 0) + self.factor * c
        return profile(out)

    def compare_delta(self, delta):
        need(all(type(r) is int and 1 <= r <= 64 and type(c) is int
                 for r, c in delta.items()), 'integer signed delta required')
        candidate = dict(self.local)
        for r, c in delta.items():
            candidate[r] = candidate.get(r, 0) + c
        candidate = profile(candidate)
        n = self.globalize(candidate)
        at_zero = sum(r * c for r, c in n.items()) + Q(32 * 64 ** 2, 10 ** 16) * sum(n.values()) - 64 * self.W
        if at_zero >= 0:
            return dict(status='UNRESOLVED', reason='candidate has no positive root in the stated domain')
        if not self.bounds:
            return dict(status='UNRESOLVED', reason='reference endpoints not certified')
        if not any(delta.values()):
            return dict(status='WORSE_OR_EQUAL', reason='identical profile: exact equal root', interval=['0', '0'])
        lo, hi = signed_price(delta, *self.bounds, terms=self.terms)
        status = 'BETTER' if hi < 0 else 'WORSE_OR_EQUAL' if lo >= 0 else 'UNRESOLVED'
        return dict(status=status, reason='J_delta across the complete certified reference bracket',
                    interval=list(map(str, (lo, hi))))


def compute():
    p = ReferencePricer()
    e = json.loads((ROOT / 'research/bit-profile-pair-audit/EXPECTED.json').read_text())
    base = {int(r): c for r, c in e['base_word']['profile'].items()}
    delta = {r: base.get(r, 0) - p.local.get(r, 0) for r in set(base) | set(p.local)}
    cases = {
        'PR555_vs_PR589': delta,
        'abstract_mass_preserving_improvement': {1: -3, 3: 1},
        'abstract_mass_preserving_worsening': {1: 3, 3: -1},
        'exact_profile_tie': {},
    }
    result = {k: p.compare_delta(v) for k, v in cases.items()}
    need(result['PR555_vs_PR589']['status'] == 'WORSE_OR_EQUAL', 'original word comparison')
    need(result['abstract_mass_preserving_improvement']['status'] == 'BETTER', 'improvement control')
    need(result['abstract_mass_preserving_worsening']['status'] == 'WORSE_OR_EQUAL', 'worsening control')
    need(result['exact_profile_tie']['interval'] == ['0', '0'], 'tie control')
    need(p.bounds == (Q(e['tuned_word']['shipped_c']), Q(e['tuned_word']['shipped_c']) + Q(1, 10 ** 24)), 'baseline shipped grid bracket')
    # This mass-preserving delta changes sign on a wide verified exponent interval.
    # It must not be promoted to a sign merely because one endpoint has one.
    wide = signed_price({1: -14, 2: 15, 4: -4}, Q(0), Q(1, 10))
    need(wide[0] < 0 < wide[1], 'ambiguous signed-price control')
    return dict(status='PASS_CERTIFIED_REFERENCE_PRICING', baseline_profile=p.local,
                global_profile=p.global_base, baseline_bracket=p.bracket_result,
                lambda_value=str(Q(32 * 64 ** 2, 10 ** 16)), factor=288,
                comparisons=result, wide_unresolved=list(map(str, wide)))


if __name__ == '__main__':
    print(json.dumps(compute(), sort_keys=True, indent=2))
