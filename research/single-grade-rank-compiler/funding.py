"""Exact certificates for a single retained product rank and an 8^v paid cut."""

from fractions import Fraction
from functools import lru_cache


GRID = 1 << 275


def _need(condition, message):
    if not condition:
        raise ValueError(message)


def _ceil_ratio(numerator, denominator):
    return -((-numerator) // denominator)


def _ceil_log2(n):
    return (n - 1).bit_length()


def _log_ratio(n, d):
    """Enclose GRID log(n/d) for d <= n <= 2d."""
    u = (n - d) * GRID
    lo = u // (n + d)
    hi = _ceil_ratio(u, n + d)
    lo_sq = lo * lo // GRID
    hi_sq = _ceil_ratio(hi * hi, GRID)
    lower = upper = 0
    for j in range(95):
        lower += 2 * lo // (2 * j + 1)
        upper += _ceil_ratio(2 * hi, 2 * j + 1)
        lo = lo * lo_sq // GRID
        hi = _ceil_ratio(hi * hi_sq, GRID)
    # log(n/d) = 2 atanh((n-d)/(n+d)). The argument is at most 1/3.
    return lower, upper + _ceil_ratio(3 * GRID, 3**191)


@lru_cache(None)
def _log(n):
    _need(n >= 1, "logarithm needs a positive integer")
    h = n.bit_length() - 1
    if n == 1:
        return 0, 0
    lo, hi = _log_ratio(n, 1 << h)
    two_lo, two_hi = _log_ratio(2, 1)
    return lo + h * two_lo, hi + h * two_hi


@lru_cache(None)
def _rank_weight(rank, saving):
    """Enclose GRID rank^(1-saving) with integer arithmetic."""
    log_lo, log_hi = _log(rank)
    power = 113
    n = 1 << power
    den = saving.denominator * n
    lo = GRID - _ceil_ratio(log_hi * saving.numerator, den)
    hi = _ceil_ratio(GRID**2 * den, GRID * den + log_lo * saving.numerator)
    _need(lo > 0, "increase the exponent subdivision")
    # (1-x/n)^n <= exp(-x) <= (1+x/n)^(-n) for x = saving log(rank).
    for _ in range(power):
        lo = lo * lo // GRID
        hi = _ceil_ratio(hi * hi, GRID)
    return rank * lo, rank * hi


def _histogram(histogram):
    result = {}
    for key, count in histogram.items():
        rank = int(key)
        _need((type(key) is int or str(rank) == key) and rank > 0,
              "rank must be a positive integer")
        _need(type(count) is int and count > 0 and rank not in result,
              "counts must be positive integers at distinct ranks")
        result[rank] = count
    _need(result, "empty rank profile")
    return dict(sorted(result.items()))


def _target_weights(targets, saving):
    return {rank: count * _rank_weight(rank, saving)[0] for rank, count in targets.items()}


def _cut_log_slack(lower_target_sum, paid_rank_mass, saving):
    lower = _log(lower_target_sum)[0] - _log(GRID * paid_rank_mass)[1]
    return Fraction(lower, GRID) + saving * Fraction(_log(8)[0], GRID)


def _mode(weights, v):
    """Choose the v largest weights[i]/j over positive integers j."""
    total = sum(weights.values())
    counts = {k: v * a // total for k, a in weights.items()}
    # Every prefix priority is >= total/v and every remaining one is smaller.
    for _ in range(v - sum(counts.values())):
        k = max(weights, key=lambda i: Fraction(weights[i], counts[i] + 1))
        counts[k] += 1
    next_value = max(Fraction(weights[k], m + 1) for k, m in counts.items())
    last_value = min(Fraction(weights[k], m) for k, m in counts.items() if m)
    _need(sum(counts.values()) == v and next_value <= last_value,
          "the proposed type is not a multinomial mode")
    return counts


def _show_lower(x):
    """Round down to 30 decimal places and keep an exact rational literal."""
    scale = 10**30
    return str(Fraction(x.numerator * scale // x.denominator, scale))


def certificate(targets, paid, raw_saving, uniform_saving, ambient, *, cap="1/250"):
    """Certify one source invoice. All prices must be exact rational literals."""
    targets, paid = _histogram(targets), _histogram(paid)
    values = (raw_saving, uniform_saving, cap)
    _need(all(isinstance(x, (str, int, Fraction)) for x in values), "use exact price literals")
    raw, uniform, cap = map(Fraction, values)
    _need(0 < uniform < raw <= cap < 1, "need 0 < uniform < raw <= cap < 1")
    _need(type(ambient) is int and ambient >= max(max(targets), max(paid)),
          "ambient does not contain every source job")
    d = len(targets)
    p1 = sum(k * count for k, count in paid.items())
    weights = _target_weights(targets, raw)
    total = sum(weights.values())
    paid_upper = sum(n * _rank_weight(k, raw)[1] for k, n in paid.items())
    raw_slack = Fraction(total - paid_upper, total)
    cut_slack = _cut_log_slack(total, p1, raw)
    slack = min(raw_slack, cut_slack)
    _need(slack > 0, "raw or split moment lacks a strict certified margin")

    # f(s)=log(T_s). Its second derivative is the variance of log(rank).
    # f'(1-cap)>log(16) makes f(1-C)-log(P_1)+C log(8) decrease on [0,cap].
    cap_weights = _target_weights(targets, cap)
    cap_upper = sum(n * _rank_weight(k, cap)[1] for k, n in targets.items())
    cap_mean = Fraction(sum(a * _log(k)[0] for k, a in cap_weights.items()),
                        GRID * cap_upper)
    mean_slack = cap_mean - Fraction(_log(16)[1], GRID)
    cap_cut_slack = _cut_log_slack(sum(cap_weights.values()), p1, cap)
    _need(min(mean_slack, cap_cut_slack) > 0, "uniform 8,16 cuts are not certified")

    raw_tilt = Fraction(sum(a * _log(k)[0] for k, a in weights.items()), total * GRID)
    _need(raw_tilt > Fraction(_log(16)[1], GRID), "the rational mode cannot certify growth")

    # For J=8^v, the full split bill is <= P_t^v + 2 J^(t-1) P_1^v.
    # The modal target supplies >= (total/GRID)^v / (v+1)^d.
    # Thus mu <= 3 (v+1)^d exp(-v slack) < 1/2 under the integer test below.
    j = 0
    while True:
        v = 1 << j
        if v * slack >= d * (j + 1) + 3:
            counts = _mode(weights, v)
            k_margin = sum(n * _log(k)[0] for k, n in counts.items()) - v * _log(16)[1]
            if k_margin >= 0:
                break
        j += 1

    # N=2^H. H is a multiple of v to make the row stock B^(H/v) integral.
    # 2 (3 ambient^v)^raw < 2^[1+raw(2+v ceil(log2 ambient))].
    axis_bits = v * _ceil_log2(ambient)
    gap = raw - uniform
    price_bound = 1 + raw * (2 + axis_bits)
    depth = max(_ceil_ratio(1 + axis_bits, v), price_bound // (v * gap) + 1)
    h = v * depth
    _need(h >= 1 + axis_bits and h * gap > price_bound, "uniform dimension failed")
    width_degree = _ceil_log2(sum(targets.values()))
    # Per owner a node has at most (ambient * paid count)^v paid descendants.
    # (1+q)^depth bounds the number of visits at all levels when branches <=q.
    visit_degree = _ceil_log2(2 * ambient * sum(paid.values()))
    return {
        "raw_saving": str(raw), "uniform_saving": str(uniform), "price_cap": str(cap),
        "source_ambient": ambient, "source_target_count": sum(targets.values()),
        "source_paid_count": sum(paid.values()), "target_weights_grid_bits": 275,
        "raw_fraction_slack_lower": _show_lower(raw_slack),
        "cut_log_slack_lower": _show_lower(cut_slack),
        "cap_mean_minus_log16_lower": _show_lower(mean_slack),
        "cap_cut_log_slack_lower": _show_lower(cap_cut_slack),
        "v": v, "type": {str(k): m for k, m in counts.items()},
        "log_K_over_16_to_v_lower": _show_lower(Fraction(k_margin, GRID)),
        "split_cap": "8^v", "minimum_target": "16^v", "mu_upper": "3/8",
        "H": h, "N": "2^H", "depth_at_most": depth,
        "dimension_log_slack_lower": _show_lower(h * gap - price_bound),
        "batch_width_degree_upper": width_degree,
        "all_recursive_visits_degree_per_root_owner": visit_degree,
    }
