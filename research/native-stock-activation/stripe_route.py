"""Apply an opaque-record permutation by changing one contiguous stripe at a time."""

from math import isqrt


def stripe_count(width, record_units):
    """Use a public field width in bits or trits and a positive bit or byte extent."""
    if width < 0 or record_units < 1:
        raise ValueError("Invalid public width or record extent")
    return min(record_units, max(1, isqrt(width)))


def striped_in_place(bank, records, record_units, stripes, route):
    """Replace one interval. Entry and return leave the public head at its start.

    The callback has two empty-or-rewound stripe tapes, the positive stripe
    width, and the same number of whole address records at every call.
    A unit is one byte in this reference implementation.
    """
    from streaming_routes import copy_bytes, erase, work_tapes

    if records < 1 or not 1 <= stripes <= record_units:
        raise ValueError("Every stripe must contain a positive portion of every record")
    origin = bank.tell()
    short, long_count = divmod(record_units, stripes)
    before = 0
    with work_tapes(2) as (source, result):
        for j in range(stripes):
            width = short + (j < long_count)
            after = record_units - before - width
            for _ in range(records):
                bank.seek(bank.tell() + before)
                copy_bytes(bank, source, width)
                bank.seek(bank.tell() + after)
            bank.seek(origin)
            source.seek(0)
            route(source, result, width)
            if result.seek(0, 2) != records * width:
                raise ValueError("The subordinate route did not return its full interval")
            erase(source)
            result.seek(0)
            for _ in range(records):
                bank.seek(bank.tell() + before)
                copy_bytes(result, bank, width)
                bank.seek(bank.tell() + after)
            erase(result)
            bank.seek(origin)
            before += width


def striped_exchange(bank, width, prefix, gap, suffix_bytes, service):
    """Exchange two full equal binary fields on a writable public interval."""
    if min(width, prefix, gap, suffix_bytes) < 0 or not (prefix and gap and suffix_bytes):
        raise ValueError("Use a nonnegative width and positive rectangular ranges")
    records = prefix * gap * (1 << (2 * width))

    def run(source, target, size):
        service(source, target, width, prefix, gap, size)

    striped_in_place(bank, records, suffix_bytes, stripe_count(width, suffix_bytes), run)


def striped_packed_bits(bank, width, prefix, gap, suffix_bits, service, *, first_bit=0):
    """Preserve neighboring bits and zero only the high bits of temporary octets."""
    from streaming_routes import erase, read_exact, work_tapes

    if min(width, first_bit) < 0 or first_bit >= 8 or min(prefix, gap, suffix_bits) < 1:
        raise ValueError("Invalid bit offset or public intervals")
    records = prefix * gap * (1 << (2 * width))
    origin = bank.tell()
    stripes = stripe_count(width, suffix_bits)
    short, extra = divmod(suffix_bits, stripes)
    before = 0
    with work_tapes(2) as (source, result):
        for j in range(stripes):
            bits = short + (j < extra)
            piece = (bits + 7) // 8
            mask = (1 << bits) - 1
            for writing in (False, True):
                if writing:
                    source.seek(0)
                    service(source, result, width, prefix, gap, piece)
                    if result.seek(0, 2) != records * piece:
                        raise ValueError("The bit-stripe exchange did not return all records")
                    erase(source)
                    result.seek(0)
                position = first_bit + before
                for _ in range(records):
                    index, offset = divmod(position, 8)
                    span = (offset + bits + 7) // 8
                    bank.seek(origin + index)
                    old = int.from_bytes(read_exact(bank, span), "little")
                    if writing:
                        new = int.from_bytes(read_exact(result, piece), "little")
                        if new & ~mask:
                            raise ArithmeticError("The route changed the private high padding bits")
                        word = (old & ~(mask << offset)) | (new << offset)
                        bank.seek(origin + index)
                        bank.write(word.to_bytes(span, "little"))
                    else:
                        source.write(((old >> offset) & mask).to_bytes(piece, "little"))
                    position += suffix_bits
                bank.seek(origin)
            erase(result)
            before += bits
