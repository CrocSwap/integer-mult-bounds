"""Test both directions of a fixed high-matrix shear on complete cover streams."""

from itertools import product
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from interchange import Port, block_word, close_cycle


def lower_add(port, data, sign, carry):
    # Each ordered tail is contiguous in suffix records.
    side, suffix = port.side, port.suffix
    output = []
    start = 0
    for _ in range(port.prefix):
        for head in range(side):
            for _ in range(port.gap):
                cut = ((-sign*head-carry) % side)*suffix
                end = start + side*suffix
                output.extend(data[start+cut:end])
                output.extend(data[start:start+cut])
                start = end
    return output


def shear(q, w, prefix, fibre, packets, sign):
    """Apply (x,y) -> (x+sign*y,y) to both rows by priced ordinary calls."""
    side = q**(w-1)
    outputs = {}
    ordinary = block_word(1, 2)
    for low, data in packets.items():
        target = list(low)
        for a in (0, 2):
            low_sum = low[a] + sign*low[a+1]
            carry, target[a] = divmod(low_sum, q)
            # P includes the old prefix. The last field preserves the whole fibre.
            port = Port(q, w-1, prefix*side**a, 1, side**(2-a)*fibre)
            data = close_cycle((ordinary,), 0, port, data, cutoff=1, fanout=5)
            data = lower_add(port, data, sign, carry)
            data = close_cycle((ordinary,), 0, port, data, cutoff=1, fanout=5)
        if tuple(target) in outputs:
            raise ValueError("low classes collided")
        outputs[tuple(target)] = data
    return outputs


def check(q, w, prefix, fibre, lows):
    side = q**(w-1)
    packet_size = prefix*side**4*fibre
    packets = {low: range(i*packet_size, (i+1)*packet_size) for i,low in enumerate(lows)}
    actual = shear(q, w, prefix, fibre, packets, 1)
    # Compute each address from full matrix entries over Z/q^w, independent of routing.
    modulus = q**w
    for low, before in packets.items():
        for row_prefix in range(prefix):
            for hi in product(range(side), repeat=4):
                a,b,c,d = [l+q*h for l,h in zip(low, hi, strict=True)]
                target = ((a+b) % modulus, b, (c+d) % modulus, d)
                dest_low = tuple(t % q for t in target)
                dest = src = row_prefix
                for old, new in zip(hi, target, strict=True):
                    src = src*side + old
                    dest = dest*side + new//q
                for bit in range(fibre):
                    if before[src*fibre+bit] != actual[dest_low][dest*fibre+bit]:
                        raise ValueError("lost cover bit, prefix, low class or carry")
    restored = shear(q, w, prefix, fibre, actual, -1)
    if restored.keys() != packets.keys() or any(restored[l] != list(v) for l,v in packets.items()):
        raise ValueError("inverse did not restore the full source")
    return len(lows)*packet_size


if __name__ == "__main__":
    q = 3
    gl = [v for v in product(range(q), repeat=4) if (v[0]*v[3]-v[1]*v[2]) % q]
    tested = check(q, 2, 3, 5, gl)
    tested += check(q, 3, 2, 3, [(2, 2, 1, 2)])
    print(f"PASS_BATCHED_HIGH_ROUTE low_classes={len(gl)} widths=2 payload_positions={tested}")
