"""Bounded bit-word implementation of the pinned eight-mode inverse code.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
"""


def word_width(bound):
    if type(bound) is not int or bound < 0:
        raise ValueError("bound must be a nonnegative integer")
    return (56 * bound + 2).bit_length() + 1


def encode(value, width):
    if not -(1 << (width - 1)) <= value < (1 << (width - 1)):
        raise ValueError("signed input does not fit")
    return [(value >> bit) & 1 for bit in range(width)]


def decode(word):
    return sum(bit << index for index, bit in enumerate(word[:-1])) - (word[-1] << (len(word) - 1))


def check_word(word, width):
    if len(word) != width or any(type(bit) is not int or bit not in (0, 1) for bit in word):
        raise ValueError("expected a fixed-width binary word")


def add_into(target, source, sign):
    """Ripple ADD/SUB modulo 2^W; the invocation range proof excludes overflow."""
    carry = int(sign == -1)
    flip = carry
    for index, source_bit in enumerate(source):
        total = target[index] + (source_bit ^ flip) + carry
        target[index] = total & 1
        carry = total >> 1


def negate_if(word, negative):
    carry = negative
    for index, bit in enumerate(word):
        total = (bit ^ negative) + carry
        word[index] = total & 1
        carry = total >> 1


def clear(word):
    for index in range(len(word)):
        word[index] = 0


def within_bound(word, limit, work):
    for index, bit in enumerate(word):
        work[index] = bit
    negate_if(work, word[-1])
    comparison = 0
    for index in range(len(word) - 1, -1, -1):
        if comparison == 0 and work[index] != limit[index]:
            comparison = 1 if work[index] > limit[index] else -1
    clear(work)
    return comparison <= 0


def round52_into(word, work):
    """Nearest integer to signed word/52; exact ties go away from zero.

    The only division loop has 13 remainder states and consumes one bit.
    No integer division or remainder instruction is used.
    """
    negative = word[-1]
    for index, bit in enumerate(word):
        work[index] = bit
    negate_if(work, negative)
    low = work[0] + 2 * work[1]
    clear(word)
    remainder = 0
    for index in range(len(work) - 1, 1, -1):
        trial = 2 * remainder + work[index]
        digit = int(trial >= 13)
        remainder = trial - 13 * digit
        word[index - 2] = digit
    carry = int(4 * remainder + low >= 26)
    for index, bit in enumerate(word):
        total = bit + carry
        word[index] = total & 1
        carry = total >> 1
    negate_if(word, negative)
    clear(work)


def tape_invoice(width, components=1):
    """Constructive upper bounds in the explicitly described fixed multitape ABI."""
    if type(width) is not int or width < 3 or type(components) is not int or components < 0:
        raise ValueError("invalid tape geometry")
    return {
        "components_per_owner": components,
        "word_bits": width,
        "signed_adds": 896 * components,
        "round52_calls": 8 * components,
        "range_checks": 112 * components,
        "external_clear_scans": 9 + 8 * components,
        "internal_divider_clear_scans": 16 * components,
        "internal_range_clear_scans": 112 * components,
        "recursive_calls": 0,
        "owned_word_slots": 9,
        "owned_cells": 9 * (width + 1),
        "owner_cells": 112 * (components * (width + 1) + 1),
        "readonly_bound_cells": width + 1,
        "transition_upper": components * (2898 * width + 5922) + 18 * width + 100,
        "head_moves_upper": 122 * (components * (2898 * width + 5922) + 18 * width + 100),
    }


def recode(owner_words, mode_columns, bound, scratch):
    """Mutate 112 owner words, returning every one of the nine owned words clean.

    Input/output words use the same grid 2^-P; P is a representation parameter.
    Borrowed helper tapes are absent from this arithmetic interface.
    """
    width = word_width(bound)
    if len(owner_words) != 112 or len(mode_columns) != 8 or len(scratch) != 9:
        raise ValueError("expected 112 owners, eight modes and nine owned words")
    all_words = owner_words + scratch
    if len({id(word) for word in all_words}) != len(all_words):
        raise ValueError("owner and scratch words must be physically distinct")
    for word in all_words:
        check_word(word, width)
    if any(len(column) != 112 or any(type(c) is not int or c not in (-1, 0, 1) for c in column)
           for column in mode_columns):
        raise ValueError("invalid mode coefficients")
    if any(sum(c != 0 for c in column) != 56 for column in mode_columns) or any(
            sum(column[index] != 0 for column in mode_columns) != 4 for index in range(112)):
        raise ValueError("mode incidence does not satisfy the numerical ABI")
    for word in scratch:
        clear(word)
    modes, work = scratch[:8], scratch[8]
    limit = encode(bound, width)
    for word in owner_words:
        if not within_bound(word, limit, work):
            raise ValueError("input exceeds the numerical ABI")
    for column, target in zip(mode_columns, modes):
        for source, sign in zip(owner_words, column):
            if sign:
                add_into(target, source, sign)
    for mode in modes:
        round52_into(mode, work)
    for index, target in enumerate(owner_words):
        for mode, column in zip(modes, mode_columns):
            if column[index]:
                add_into(target, mode, -column[index])
    for word in modes:
        clear(word)
    return tape_invoice(width)
