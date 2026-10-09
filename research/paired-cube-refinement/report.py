"""Generate numerical exposition from the same exact certificate as the checker."""
from decimal import Decimal, localcontext
from fractions import Fraction


def decimal(value, places=18):
    value = Fraction(value)
    with localcontext() as context:
        context.prec = 70
        number = Decimal(value.numerator) / Decimal(value.denominator)
        return format(number, f'.{places}f')


def render(record):
    arithmetic = record['arithmetic']
    paid = arithmetic['paid_moment']
    final = arithmetic['assembly']
    row = record['bit']['profile']
    kappa = Fraction(record['kappa'])
    baseline = Fraction(record['baseline_kappa'])
    active = 'bit' if final['a'] == final['actual_bit_saving'] else 'weakened complex'
    lines = [
        '# Generated numerical results', '',
        'This file is generated from `certificate.json` and compared during verification.', '',
        f'The conditional saving is **kappa = {record["kappa"]} = {decimal(kappa)}**.',
        f'This exceeds PR168 by {decimal(100*(kappa/baseline-1), 8)} percent; '
        'the comparison concerns the asymptotic exponent saving, not measured runtime.', '',
        '| Quantity | Certified value |', '|---|---:|',
        f'| Bit coarse saving | {decimal(paid["coarse_saving"])} |',
        f'| Paid ordinary bit saving | {decimal(paid["ordinary_saving"], 24)} |',
        f'| Complex saving | {decimal(final["complex_saving"])} |',
        f'| Actual transfer saving | {decimal(final["a"], 24)} |',
        f'| Active supplier | {active} |',
        f'| Changed bit operation frames | {row["changed_operation_frames"]} |',
        f'| Bit persistent stock | {row["W_per_vertex"]} |',
        f'| Bit rank deficit | {row["deficit_per_vertex"]} |',
        f'| Largest bit child | {row["maxchild"]} |',
        f'| Complete fallback children per edge | {paid["envelope"]["fallback_children_per_edge"]} |', '',
        'The transfer uses `a = min(actual_bit_saving, (1-beta)*complex_saving - weakening)`.',
        'Both the ordinary supplier and the strict complex leaf inequality are checked.',
        'Every one of the 47 constraints and seven margins is strict; the next final grid point fails.', '',
        '## Matched comparisons', '',
        '| Construction and bill, with the same refined wrapper | kappa |', '|---|---:|']
    for item in arithmetic['matched_comparisons']:
        lines.append(f'| {item["name"]} | {decimal(item["kappa"])} |')
    lines += ['', 'All finite frame, prime and scalar checks are separate from the inherited '
              'all-size interfaces. Those interfaces remain assumptions.', '']
    return '\n'.join(lines)
