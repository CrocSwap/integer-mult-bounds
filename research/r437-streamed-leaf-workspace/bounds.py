"""Conservative source-parameter bounds; not a fresh runtime decoder.

Krzysztof Wójt with substantial OpenAI Codex assistance; Apache-2.0.
"""


def workspace_bound(*, q, fibre, prefix_body, program_body, callback_depth,
                    index_bits, residue_bits, entry_backing=0):
    values = (q, fibre, prefix_body, program_body, callback_depth,
              index_bits, residue_bits, entry_backing)
    if any(type(value) is not int for value in values):
        raise ValueError("integer bound parameters")
    if q < 2 or fibre < 1 or min(index_bits, residue_bits) < 1 or min(
            prefix_body, program_body, callback_depth, entry_backing) < 0:
        raise ValueError("nonnegative extents and positive radix/fibre/word widths")
    roles = q * q + 136
    stack_record = max(2 * index_bits + 4, residue_bits + 3)
    body = max(fibre, prefix_body, program_body,
               (2 * callback_depth + 3) * stack_record,
               index_bits + 3, residue_bits + 3, fibre.bit_length() + 3)
    return dict(roles=roles, stack_record=stack_record, body_bound=body,
                fresh_retained_cells=roles * (body + 2),
                with_entry_reserve=entry_backing + roles * (body + 2))


def clear_tariff(head, body):
    if type(head) is not int or type(body) is not int or head < 1 or body < 0:
        raise ValueError("valid starting head and contiguous body extent")
    return dict(reads=head + 2 * body + 2, writes=body, moves=head + 2 * body + 3)


def pooling_surcharge(roles, prefixes, acquisitions, callback_closes):
    if any(type(x) is not int or x < 0 for x in (roles, prefixes, acquisitions, callback_closes)) or roles == 0:
        raise ValueError("nonnegative tariff counts and positive role inventory")
    # Starting from blank origins, setup is `roles` writes and `roles` moves.
    # The interval assumes these prepared LEFT markers and heads are supplied.
    return acquisitions + 4 * roles * prefixes + 28 * callback_closes
