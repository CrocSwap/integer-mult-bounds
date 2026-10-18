"""Exact real output channels for the fixed P104 lift. Apache-2.0.

Ross Richardson with OpenAI Codex assistance. Finite reference: ranks 1..7,
integer inputs of at most 4096 magnitude bits. No recursive child tariff.
"""

from collections import Counter


def need(value, message):
    if not value:
        raise ValueError(message)


def shape(rank):
    need(type(rank) is int and 1 <= rank <= 7, "rank in 1..7")
    return 2 << rank


def vector(value, rank):
    need(len(value) == shape(rank), "interleaved real vector shape")
    need(all(type(x) is int and x.bit_length() <= 4096 for x in value),
         "signed integer input limit")
    return list(value)


def quarter(real, imag, exponent):
    return ((real, imag), (-imag, real), (-real, -imag),
            (imag, -real))[exponent % 4]


def lift(value, rank):
    result = vector(value, rank)
    for bit in range(rank):
        for a in range(1 << rank):
            if a >> bit & 1:
                continue
            b = a ^ (1 << bit)
            dr = result[2*a] - result[2*b]
            di = result[2*a+1] - result[2*b+1]
            sr = result[2*b] + dr // 2
            si = result[2*b+1] + di // 2
            rr, ri = -di, dr
            br, bi = sr-rr//2, si-ri//2
            result[2*a:2*a+2] = (br+rr, bi+ri)
            result[2*b:2*b+2] = (br, bi)
    return result


def numerator(value, rank):
    """Return 2^rank U(value), with exact integer Gaussian butterflies."""
    result = vector(value, rank)
    for bit in range(rank):
        for a in range(1 << rank):
            if a >> bit & 1:
                continue
            b = a ^ (1 << bit)
            ar, ai, br, bi = result[2*a], result[2*a+1], result[2*b], result[2*b+1]
            result[2*a:2*a+2] = (ar-ai+br+bi, ar+ai-br+bi)
            result[2*b:2*b+2] = (ar+ai+br-bi, -ar+ai+br+bi)
    return result


def defect(value, rank):
    n = 1 << rank
    return [n*a-b for a, b in zip(lift(value, rank), numerator(value, rank), strict=True)]


def walsh(value, rank):
    need(len(value) == shape(rank), "Walsh vector shape")
    result = list(value)
    for bit in range(rank):
        for a in range(1 << rank):
            if a >> bit & 1:
                continue
            b = a ^ (1 << bit)
            for component in (0, 1):
                i, j = 2*a+component, 2*b+component
                x, y = result[i], result[j]
                result[i], result[j] = x+y, x-y
    return result


def modes(rank):
    shape(rank)
    result = []
    for mask in range(1 << rank):
        parities = sorted({(mask >> (j+1)).bit_count() % 2
                           for j in range(rank) if not (mask >> j & 1)})
        result.append((len(parities), parities[0] if parities else None))
    return result


def fibonacci(index):
    first, second = 0, 1
    for _ in range(index):
        first, second = second, first+second
    return first


def spectral(value, rank):
    """c=H L(value)-diag(i^weight) H value; all entries are integers."""
    actual, original = walsh(lift(value, rank), rank), walsh(value, rank)
    for mask in range(1 << rank):
        real, imag = quarter(*original[2*mask:2*mask+2], mask.bit_count())
        actual[2*mask] -= real
        actual[2*mask+1] -= imag
    return actual


def pack(spectrum, rank):
    need(len(spectrum) == shape(rank) and all(type(x) is int for x in spectrum),
         "integer spectrum shape")
    result = []
    for mask, (dimension, parity) in enumerate(modes(rank)):
        real, imag = spectrum[2*mask:2*mask+2]
        if dimension == 0:
            need(real == imag == 0, "zero all-ones mode")
        elif dimension == 1:
            need(imag == (2*parity-1)*real, "one-dimensional phase line")
            result.append(real)
        else:
            result.extend((real, imag))
    return result


def unpack(channels, rank):
    needed = sum(dimension for dimension, _ in modes(rank))
    need(len(channels) == needed and all(type(x) is int for x in channels),
         "integer channel shape")
    result, at = [0]*shape(rank), 0
    for mask, (dimension, parity) in enumerate(modes(rank)):
        if dimension == 1:
            real = channels[at]
            result[2*mask:2*mask+2] = real, (2*parity-1)*real
        elif dimension == 2:
            result[2*mask:2*mask+2] = channels[at:at+2]
        at += dimension
    return result


def encode(value, rank):
    return pack(spectral(value, rank), rank)


def decode(channels, rank):
    return walsh(unpack(channels, rank), rank)


def invoice(rank):
    n = 1 << rank
    counts = Counter(dimension for dimension, _ in modes(rank))
    widths, total = Counter(), 0
    for mask, (dimension, _) in enumerate(modes(rank)):
        if dimension:
            magnitude = (n//2)*(rank-mask.bit_count())
            # Minimum two's-complement width covering this symmetric bound.
            width = 1 + magnitude.bit_length()
            widths[width] += dimension
            total += width*dimension
    # Bound each real component of N*(L-Ux) using the forced (1-i) error phase.
    bound = (n//2)*sum(1 << (k//2) for k in range(rank))
    full_width = 1+bound.bit_length()
    spectral_bound = n*rank//2
    start_width = 1+spectral_bound.bit_length()
    delivery_widths = {str(start_width): 4*(n-1)}
    delivery_widths.update({str(start_width+k): 8*n for k in range(1, rank+1)})
    return {"rank": rank, "gaussian_coordinates": n,
            "mode_dimension_counts": {str(k): counts[k] for k in range(3)},
            "real_channels": sum(k*v for k, v in counts.items()),
            "fibonacci_codimension": fibonacci(rank+3),
            "encoded_signed_width_histogram": {str(k): widths[k] for k in sorted(widths)},
            "encoded_bank_bits": total,
            "full_scaled_defect_component_bound": bound,
            "full_scaled_defect_signed_width": full_width,
            "full_scaled_defect_bank_bits": 2*n*full_width,
            "one_out_of_place_walsh_real_additions": 2*n*rank,
            "one_out_of_place_walsh_result_writes": 2*n*rank,
            "one_out_of_place_walsh_operand_reads": 2*n*rank,
            "reversible_delivery_modular_add_width_histogram": delivery_widths,
            "reversible_delivery_modular_adds": 4*(n-1)+8*n*rank,
            "reversible_delivery_target_cnot": 2*n*full_width,
            "reversible_delivery_clean_bank_bits": 2*n*sum(start_width+k for k in range(rank+1)),
            "reversible_delivery_largest_word_bits": start_width+rank,
            "static_nonlinear_pair_sites": rank*n//2}


def delivery_program(rank):
    """Complete modular-ADD macro word, with immutable packed input at bank -1.

    Each tuple is (source bank,source index,target bank,target index,sign,width).
    Work banks 0..r are disjoint and start zero. The source bank is signed.
    """
    n = 1 << rank
    start_width = 1+(n*rank//2).bit_length()
    operations, source_at = [], 0
    for mask, (dimension, parity) in enumerate(modes(rank)):
        if dimension == 1:
            operations.extend(((-1, source_at, 0, 2*mask, 1, start_width),
                               (-1, source_at, 0, 2*mask+1, 2*parity-1, start_width)))
        elif dimension == 2:
            operations.extend(((-1, source_at, 0, 2*mask, 1, start_width),
                               (-1, source_at+1, 0, 2*mask+1, 1, start_width)))
        source_at += dimension
    for bit in range(rank):
        for a in range(n):
            if a >> bit & 1:
                continue
            b = a ^ (1 << bit)
            for component in (0, 1):
                i, j = 2*a+component, 2*b+component
                operations.extend(((bit, i, bit+1, i, 1, start_width+bit+1),
                                   (bit, j, bit+1, i, 1, start_width+bit+1),
                                   (bit, i, bit+1, j, 1, start_width+bit+1),
                                   (bit, j, bit+1, j, -1, start_width+bit+1)))
    return tuple(operations), tuple(start_width+k for k in range(rank+1))


def signed(word, width):
    word %= 1 << width
    return word-(1 << width) if word >> (width-1) else word


def signed_bits(values, width):
    return sum((value % (1 << width)) << (width*j) for j, value in enumerate(values))


def delivery_oracle(channels, target, work, rank):
    """XOR the low fixed-width decoded defect into arbitrary target; clean work.

    This is a literal modular-ADD macro circuit, not a CNOT/Toffoli lowering.
    Exact signed defect interpretation requires channels from encode(x,rank).
    """
    dimension = shape(rank)
    need(len(channels) == sum(k for k, _ in modes(rank)) and
         all(type(x) is int for x in channels), "delivery channels")
    operations, widths = delivery_program(rank)
    need(type(work) is list and len(work) == rank+1, "work bank count")
    need(all(type(bank) is list and len(bank) == dimension and
             all(type(x) is int and x == 0 for x in bank) for bank in work),
         "clean disjoint work banks required")
    need(len({id(bank) for bank in work}) == rank+1 and
         all(bank is not channels for bank in work), "work alias")
    output_width = invoice(rank)["full_scaled_defect_signed_width"]
    need(type(target) is int and 0 <= target < (1 << (dimension*output_width)),
         "arbitrary XOR target range")

    def apply(operation, direction):
        source_bank, source_index, target_bank, target_index, sign, width = operation
        value = (channels[source_index] if source_bank == -1 else
                 signed(work[source_bank][source_index], widths[source_bank]))
        work[target_bank][target_index] = (
            work[target_bank][target_index]+direction*sign*value) % (1 << width)

    for operation in operations:
        apply(operation, 1)
    target ^= signed_bits(work[-1], output_width)
    for operation in reversed(operations):
        apply(operation, -1)
    need(not any(any(bank) for bank in work), "literal bank cleanup")
    return target


def candidates(rank):
    d = shape(rank)
    for coordinate in range(d):
        for amplitude in (1, 2, 3, 4, 5, 7, 8):
            value = [0]*d
            value[coordinate] = amplitude
            yield {"coordinate": coordinate, "amplitude": amplitude}, value
    state = 0x104D0000 + rank
    for sample in range(1024):
        value = []
        for _ in range(d):
            state ^= (state << 13) & 0xffffffff
            state ^= state >> 17
            state ^= (state << 5) & 0xffffffff
            state &= 0xffffffff
            value.append((state % 31)-15)
        yield {"signed_sample": sample}, value


class ModularBasis:
    """Independent nonzero residues imply independence over Q and R."""
    def __init__(self, prime=65521):
        need(prime in (65521, 65537), "audited prime")
        self.prime, self.rows = prime, {}

    def append(self, value):
        prime = self.prime
        row = [x % prime for x in value]
        for column, old in sorted(self.rows.items()):
            if row[column]:
                factor = row[column]
                row = [(x-factor*y) % prime for x, y in zip(row, old, strict=True)]
        pivot = next((j for j, x in enumerate(row) if x), None)
        if pivot is None:
            return None
        inverse = pow(row[pivot], -1, prime)
        self.rows[pivot] = [(x*inverse) % prime for x in row]
        return pivot
