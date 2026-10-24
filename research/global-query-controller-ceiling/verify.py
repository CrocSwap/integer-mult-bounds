"""Exact ceiling for all prefix/suffix FULL/QUERY allocations.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The controller is due to Cinna Davis and the retained source authors.
The directed interval engine is due to zxv. See PROOF.md for the scope.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256, sha1
from pathlib import Path
import argparse
import json
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CEILING = Q('.00302728825')
TAIL = 96
PAID = {1: 2193, 2: 412, 3: 510, 4: 127, 5: 40}
HELPERS = {4: 28, 7: 7, 8: 47, 9: 318}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / path)
    sys.modules[name] = module
    exec(compile((ROOT / path).read_bytes(), module.__file__, 'exec'), module.__dict__)
    return module


def authenticate():
    result = {}
    for row in json.loads((HERE / 'SOURCES.json').read_text())['files']:
        if row['usage'] != 'input':
            continue
        raw = (ROOT / row['path']).read_bytes()
        digest = sha256(raw).hexdigest()
        need(digest == row['sha256'], 'Source SHA256: ' + row['path'])
        need(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
             == row['git_blob'], 'Source Git blob: ' + row['path'])
        result[row['path']] = digest
    return result


def check_profile(row):
    native = row['native']
    paid = {int(k): v for k, v in native['paid'].items()}
    helper = {int(k): v for k, v in native['source_replay']['helpers'].items()}
    need(paid == PAID and helper == HELPERS, 'Exact owned supplier profile')
    need(native['source_replay']['paid'] == native['paid'], 'Both source orientations')
    need(native['source_replay']['independent_persistent_columns'] == 624,
         'All retained source fields')


def formula(p, a, chosen):
    """Return the complete literal interval invoice for this family."""
    n = len(chosen)
    paid = Counter({r: n * c for r, c in PAID.items()})
    target = Counter({r: n * c for r, c in HELPERS.items()})
    paid[1] += 112 * (2 * p + 1 - n)
    target[1 + 8 * n] += 224
    for j in range(1, p):
        idle = range(2 * j) if j <= a else range(2 * j + 1, 2 * p + 1)
        count = sum(s in chosen for s in idle)
        even = int(2 * j in chosen)
        if count:
            paid[8 * count] += 224
        if even:
            paid[8] += 224
        target[1 + 8 * (count + even)] += 224
    return +paid, +target


def engine_checks(w, source):
    load('research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/bit-compression/carrier-reuse/reference/joint_pair_dag.py', 'joint_pair_dag')
    load('research/kappa-rebuild/bit/mixed_productive_bit.py', 'mixed_productive_bit')
    engine = load('research/kappa-rebuild/bit/complex_controller_factor.py', 'ceiling_controller_engine')
    query = load('research/query-thinned-controllers/controller.py', 'ceiling_query_engine')
    trials, factorizations, minima = 0, 0, {}
    def lower(paid, target):
        return sum(c * w[r][0] for r, c in paid.items()) - sum(c * w[r][1] for r, c in target.items())
    for p in range(1, 6):
        best = None
        for a in range(p):
            co, _, idles = engine.controller(p, query.keep_mask(p, a))
            factor = engine.factor(co)
            need(factor is not None, 'Exact full Laurent factorization')
            factorizations += 1
            terms = [sum((v != 0) << s for s, v in enumerate(k[1:])) for k in factor['diagonal']]
            idle_terms = [sum(1 << s for s in row['stages']) for row in idles if row['retained']]
            for mask in range(1 << (2 * p + 1)):
                n = mask.bit_count()
                paid = Counter({r: n * c for r, c in PAID.items()})
                target = Counter({r: n * c for r, c in HELPERS.items()})
                paid[1] += 112 * (2 * p + 1 - n)
                for term in terms:
                    target[1 + 8 * (mask & term).bit_count()] += 112
                for term in idle_terms:
                    rank = 8 * (mask & term).bit_count()
                    if rank:
                        paid[rank] += 224
                chosen = {s for s in range(2 * p + 1) if mask >> s & 1}
                need((+paid, +target) == formula(p, a, chosen), 'Literal interval invoice')
                bill = lower(paid, target)
                best = bill if best is None else min(best, bill)
                trials += 1
        minima[p] = best
    chosen = {0, 32, *range(1, 32, 2)}
    paid, target = formula(16, 7, chosen)
    need(paid == Counter({int(k): v for k, v in source['arithmetic']['paid'].items()}), 'Published complete paid profile')
    need(target == Counter({int(k): v for k, v in source['arithmetic']['targets'].items()}), 'Published complete target profile')
    # The retained p16 receipt supplies another diagonal and idle census.
    receipt = json.loads((ROOT / 'research/joint-helper-lattice/CONTROLLER.json').read_text())
    main = Counter()
    for term in receipt['diagonal']:
        main[1 + 8 * sum(term[1:])] += 112
    actual_main = Counter(target)
    actual_main.subtract({r: 18 * c for r, c in HELPERS.items()})
    need(+actual_main == main, 'Retained p16 main targets')
    need(sum(paid.values()) == 64116 and sum(target.values()) == 10784,
         'Complete p16 field and call counts')
    # An omitted whole idle falsely passes the moment test.
    wrong_paid = paid.copy()
    wrong_paid[64] -= 1
    need(wrong_paid != paid and lower(wrong_paid, target) < 0 < lower(paid, target),
         'Reject omitted idle with a false positive bill')
    # An unearned helper restores the discarded productive credit.
    wrong = json.loads(json.dumps(source))
    wrong['native']['source_replay']['helpers']['9'] += 8
    try:
        check_profile(wrong)
    except ValueError:
        pass
    else:
        raise ValueError('Unearned helper credit accepted')
    # A FULL even stage has a separate middle idle charge.
    changed = chosen | {2}
    changed_paid, _ = formula(16, 7, changed)
    need(changed_paid[8] == paid[8] + 224, 'Middle idle charge after a FULL even stage')
    return dict(exhaustive_masks=trials, full_Laurent_factorizations=factorizations,
                p16_paid_calls=sum(paid.values()), p16_targets=sum(target.values()),
                p16_lower_scaled=lower(paid, target),
                controls=['omitted_idle_false_positive', 'unearned_helper_credit', 'full_even_stage_middle_idle']), minima


def run():
    sources = authenticate()
    source = json.loads((HERE / 'source/transpose-RESULT.json').read_text())
    check_profile(source)
    engine = load('research/higher-moment-strictification/verify.py', 'ceiling_intervals')
    grid, t = engine.GRID, 1 - CEILING
    ranks = {0, 1, 2, 3, 4, 5, 7, 8, 9} | {8 * k + e for k in range(TAIL + 1) for e in (0, 1)}
    w = {0: (0, 0)}
    for rank in sorted(ranks - {0}):
        lo, hi = engine.power(rank, t)
        need((lo * grid).denominator == (hi * grid).denominator == 1, 'Exact outward grid')
        w[rank] = int(lo * grid), int(hi * grid)
    local = sum(c * w[r][0] for r, c in PAID.items()) - sum(c * w[r][1] for r, c in HELPERS.items())
    tail = 336 * grid + (local - 112 * grid) * TAIL - 224 * w[1 + 8 * TAIL][1]
    slope = Q(local, grid) - 112 - 1792 * t * Q(w[1 + 8 * TAIL][1], grid * (1 + 8 * TAIL))
    need(tail > 0 and slope > 0, 'Positive increasing tail for every n >= 96')
    dp = [[0, 0]]
    for q in range(1, TAIL):
        row = [None] * min(2 * q + 2, TAIL)
        for k, value in enumerate(dp[-1]):
            for odd in (0, 1):
                for even in (0, 1):
                    count = k + odd + even
                    if count >= TAIL:
                        continue
                    fee = 224 * (w[8 * (k + odd)][0] + even * w[8][0] - w[1 + 8 * count][1])
                    candidate = value + fee
                    if row[count] is None or candidate < row[count]:
                        row[count] = candidate
        need(all(v is not None for v in row), 'Every side state is reachable')
        dp.append(row)
    per_p, candidates, global_best = [], 0, None
    for p in range(1, TAIL + 1):
        best = None
        for a in range((p - 1) // 2 + 1):
            b = p - 1 - a
            for left, lvalue in enumerate(dp[a]):
                for right, rvalue in enumerate(dp[b]):
                    for center in (0, 1):
                        n = left + right + center
                        if n >= TAIL:
                            continue
                        bill = 112 * (2 * p + 1) * grid + (local - 112 * grid) * n + lvalue + rvalue - 224 * w[1 + 8 * n][1]
                        candidates += 1
                        if best is None or bill < best[0]:
                            best = bill, a, left, right, center
        need(best[0] > 0, 'Every finite controller fails the necessary moment')
        if global_best is None or best[0] < global_best[0]:
            global_best = best[0], p, *best[1:]
        per_p.append(dict(p=p, a=best[1], left_full=best[2], right_full=best[3], center=best[4], lower_scaled=best[0]))
    checks, brute_minima = engine_checks(w, source)
    need(all(per_p[p - 1]['lower_scaled'] == bill for p, bill in brute_minima.items()), 'Independent exhaustive minima equal the dynamic program')
    lo = Q(global_best[0], grid)
    need(global_best[1:] == (16, 7, 8, 9, 1), 'Best finite configuration')
    need(global_best[0] == checks['p16_lower_scaled'], 'Current p16 invoice attains the minimum lower bound')
    return dict(status='PASS_GLOBAL_QUERY_CONTROLLER_CEILING_NO_KAPPA_GAIN', new_kappa=None,
                ceiling=str(CEILING), ceiling_decimal='.00302728825', saving_domain='ceiling <= kappa < 1',
                profile=dict(paid=PAID, helpers=HELPERS), grid=str(grid), tail_start=TAIL,
                tail_lower=engine.display((Q(tail, grid),) * 2), tail_derivative_lower=engine.display((slope,) * 2),
                global_lower=engine.display((lo,) * 2), global_lower_exact=str(lo),
                best=dict(p=16, a=7, full_calls=18, left_full=8, right_full=9, center=1),
                finite_combinations=candidates, per_p=per_p, source_checks=checks, source_sha256=sources)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = run()
    if args.write:
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        saved = json.loads((HERE / 'RESULT.json').read_text())
        need(json.loads(json.dumps(result)) == saved, 'Deterministic exact receipt')
    print(result['status'])


if __name__ == '__main__':
    main()
