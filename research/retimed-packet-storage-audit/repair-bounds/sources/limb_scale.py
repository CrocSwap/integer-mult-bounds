"""Move arbitrary payloads under multiplication by any unit of a ternary digit field."""

from streaming_routes import copy_bytes, erase, negate_field, shift_field, work_tapes


def unit_scale(source, target, digits, prefixes, piece, unit, previous_swap):
    """Route x to unit*x modulo 3**digits without another full independent digit."""

    def odd_step(src, dst, branch_prefix, side, branch_piece, factor):
        # Convert a high field and a trailing trit into three whole high fields.
        with work_tapes(7) as tapes:
            ins, outs, scratch = tapes[:3], tapes[3:6], tapes[6]
            for _ in range(branch_prefix):
                for _ in range(side):
                    for tape in ins:
                        copy_bytes(src, tape, branch_piece)
                for t, tape in enumerate(ins):
                    tape.seek(0)
                    shift_field(
                        tape,
                        outs[factor * t % 3],
                        scratch,
                        1,
                        side,
                        1,
                        branch_piece,
                        None,
                        (factor * t // 3) % side,
                    )
                    erase(tape)
                for tape in outs:
                    tape.seek(0)
                for _ in range(side):
                    for tape in outs:
                        copy_bytes(tape, dst, branch_piece)
                for tape in outs:
                    erase(tape)

    def carry_step(src, dst, branch_prefix, base, branch_piece, factor, inv):
        with work_tapes(1) as (temporary,):
            for _ in range(branch_prefix):
                for low_after in range(base):
                    old_low = low_after * inv % base
                    carry = (factor * old_low // base) % base
                    shift_field(src, dst, temporary, 1, base, 1, branch_piece, None, carry)

    def schedule(v, a, front, tail):
        finishes = []
        while v:
            a %= 3**v
            if a == 1:
                break
            if v == 1:
                yield negate_field, (temporary, front, 3, tail)
                break
            if v % 2:
                v -= 1
                finishes.append((odd_step, (front, 3**v, tail, a)))
                tail *= 3
                continue
            v //= 2
            base = 3**v
            inv = pow(a, -1, base)
            swap = previous_swap, (v, front, 1, tail)

            # Scale the two limbs by reciprocal units before the one smaller call.
            if inv != 1:
                for upper, coefficient in (
                    (False, -inv),
                    (True, a - 1),
                    (False, 1),
                    (True, inv - 1),
                ):
                    coefficient %= base
                    if coefficient:
                        if upper:
                            yield swap
                        yield shift_field, (temporary, front, base, 1, tail, coefficient, 0)
                        if upper:
                            yield swap
            finishes.extend((swap, (carry_step, (front, base, tail, a, inv)), swap))
            a *= a
            tail *= base
        yield from reversed(finishes)

    if digits < 0 or unit % 3 == 0 or prefixes < 0 or piece < 1:
        raise ValueError("A unit and a complete ternary field are required")
    size = prefixes * 3**digits * piece
    with work_tapes(3) as (current, other, temporary):
        copy_bytes(source, current, size)
        for action, args in schedule(digits, unit, prefixes, piece):
            current.seek(0)
            action(current, other, *args)
            erase(current)
            current, other = other, current
        current.seek(0)
        copy_bytes(current, target, size)
