"""Check the public multiplier against school arithmetic and explicit convolution."""

from hashlib import sha256
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from multiply import geometry, multiply_bits, multiply_integer
from templates import admit, pack, repeat_sum, unpack


def positions(m):
    addresses = [0]
    stride = 1
    for _ in range(m):
        addresses += [i + stride for i in addresses]
        stride *= 3
    return addresses


def sample(m, rng):
    linear = rng.randrange(1 << m)
    constant = rng.randrange(2)
    edges = [(1 << i) | (1 << j) for i in range(m) for j in range(i)
             if rng.randrange(2)]
    output = 0
    for x, index in enumerate(positions(m)):
        q = (constant + (x & linear).bit_count() + sum(x & e == e for e in edges)) % 2
        output |= q << index
    return output


def checked(a, b, n, *, route=None):
    x, y = unpack(a, n), unpack(b, n)
    original = (bytes(x), bytes(y))
    evidence = {}
    digits = multiply_bits(x, y, evidence=evidence)
    if (x, y) != original or pack(digits) != a * b or len(digits) != max(1, (a*b).bit_length()):
        raise ValueError("The public product or an input differs")
    if route is not None and evidence["route"] != route:
        raise ValueError((route, evidence, n))
    if evidence["route"] == "clifford":
        moves = evidence["delivery"]
        extent = 3 ** evidence["sites"]
        if moves["ripple"] > moves["emits"] or moves["moves"] > 50 * extent:
            raise ValueError("The literal movement exceeded its uniform bound")
    return evidence


def main():
    rng = Random(11790)
    routes = {"ordinary": 0, "clifford": 0}
    for a in range(32):
        for b in range(32):
            item = checked(a, b, 5)
            routes[item["route"]] += 1
    if multiply_bits(b"", b"") != b"\0" or multiply_integer(-17, 33) != -561:
        raise ValueError("Incorrect empty or signed product")
    try:
        multiply_bits(bytes((1, 2)), b"\0")
    except ValueError:
        pass
    else:
        raise ValueError("Accepted a nonbinary record")

    dense = 0
    for m in range(3, 9):
        width = 1 << (m // 2)
        n = width * (3 ** m // width)
        _, _, count = geometry(n)
        g = ((1 << (count * width)) - 1) // ((1 << width) - 1)
        for pattern in range(5):
            left = sample(m, rng)
            right = sample(m, rng)
            ashort = (1 << (width - 1)) | rng.randrange((1 << (width - 1)) - 1)
            bshort = (1 << (width - 1)) | rng.randrange((1 << (width - 1)) - 1)
            a = ashort*g + (1 - 2*(pattern & 1)) * (left << width)
            b = bshort*g + (1 - 2*((pattern >> 1) & 1)) * (right << width)
            if pattern == 4:
                b = right
            item = checked(a, b, n, route="clifford")
            dense += 1
            if m == 8 and pattern == 1:
                print("dense_example", n, "bits", "shifts", item["shifts"],
                      "signs", item["signs"], "emits", item["delivery"]["emits"],
                      "moves", item["delivery"]["moves"],
                      "sha256_packed_le", sha256((a*b).to_bytes(((a*b).bit_length()+7)//8,"little")).hexdigest())
    for width in (1, 2, 3, 8, 13, 31):
        for count in (1, 2, 3, 17):
            for length in (1, width, 3*width+1):
                v = rng.getrandbits(length)
                expected = v * sum(1 << (j*width) for j in range(count))
                if pack(repeat_sum(unpack(v, length), width, count)) != expected:
                    raise ValueError("The shifted moving window missed a tail or carry")
    # An invalid hole must reach the ordinary fallback.
    data = bytes(int(i == 2 or i % 7 == 1) for i in range(81))
    m, width, count = geometry(len(data))
    if admit(data, m, width, count) is not None:
        raise ValueError("A nonmember passed both inspections")
    checked(pack(data), 103, 81, route="ordinary")
    cubic = sum(((x & 7) == 7 or (x & 7) in (1, 2, 4, 3)) << i
                for x, i in enumerate(positions(5)))
    # Use an independent interpolation test in check_io for full affine-hull coverage.
    checked(cubic, 741503, 243)
    check = {}
    if multiply_integer(741503, 466013, evidence=check) != 345550037539:
        raise ValueError("Incorrect public regression product")
    print("small_products", sum(routes.values()), "routes", routes,
          "dense_products", dense, "window_products", 72, "regression", check["route"])


if __name__ == "__main__":
    main()
