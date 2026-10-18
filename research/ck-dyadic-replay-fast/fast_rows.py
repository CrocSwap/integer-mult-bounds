"""Exact sparse dyadic kernels for the pinned PR917 replay, opt-in only.

Sricharan Vagvala, with substantial OpenAI Codex assistance. Apache-2.0.
Rows are immutable, zero-free integer numerator maps divided by 2**exponent.
The original replay owns validation, endpoints, envelopes and all receipts.
"""

from contextlib import contextmanager


def _reduce_nonzero(terms, exponent):
    if not terms:
        return {}, 0
    reduction = exponent
    if reduction:
        for value in terms.values():
            # An odd numerator already proves the common valuation is zero.
            if value & 1:
                return terms, exponent
            reduction = min(reduction, (value & -value).bit_length() - 1)
        if reduction:
            return {column: value >> reduction for column, value in terms.items()}, exponent - reduction
    return terms, exponent


def normal_row(terms, exponent):
    return _reduce_nonzero({column: value for column, value in terms.items() if value}, exponent)


def sum_rows(left, right, sign):
    """Add canonical rows without modifying either input, including on COPY."""
    left_terms, left_exponent = left
    right_terms, right_exponent = right
    exponent = max(left_exponent, right_exponent)
    left_shift, right_shift = exponent - left_exponent, exponent - right_exponent
    result = ({column: value << left_shift for column, value in left_terms.items()}
              if left_shift else left_terms.copy())
    for column, value in right_terms.items():
        value = result.get(column, 0) + sign * (value << right_shift)
        if value:
            result[column] = value
        else:
            result.pop(column, None)
    return _reduce_nonzero(result, exponent)


@contextmanager
def accelerated(module):
    """Temporarily replace only the two arithmetic kernels; always restore."""
    original = module._normal_row, module._sum_rows
    module._normal_row, module._sum_rows = normal_row, sum_rows
    try:
        yield module
    finally:
        module._normal_row, module._sum_rows = original
