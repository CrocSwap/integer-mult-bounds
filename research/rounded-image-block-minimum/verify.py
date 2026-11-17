"""Exact rounded-image block counts. Produced by Nick Petalas; Apache-2.0."""

import hashlib
import itertools
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
MAX_AXES = 16
MAX_ELL = 64
CENSUS_BITS = 10
MAX_PACKETS = 5000
MAX_FILE_BYTES = 131072


def need(condition, message):
    if not condition:
        raise ValueError(message)


def checked_shape(shape):
    need(isinstance(shape, tuple) and 1 <= len(shape) <= MAX_AXES,
         "one through sixteen axes")
    for axis in shape:
        need(isinstance(axis, tuple) and len(axis) == 2, "axis pair")
        ell, s = axis
        need(type(ell) is int and 2 <= ell <= MAX_ELL, "bounded exponent")
        need(type(s) is int and (1 << (ell - 1)) < s < (1 << ell),
             "strict source-period guard")
    return shape


def block_count(shape):
    """Evaluate R_i = (t_i-s_i) S_{i+1} + b_i R_{i+1}."""
    shape = checked_shape(shape)
    runs, size = 1, 1
    for ell, s in reversed(shape):
        t = 1 << ell
        touches_right = int(3 * s > 2 * t)
        runs = (t - s) * size + touches_right * runs
        size *= s
    need(1 <= runs <= size, "nonempty run-count range")
    return runs


def closed_sum(shape):
    """Independent implementation of the displayed finite-sum formula."""
    shape = checked_shape(shape)
    suffix = math.prod(s for _, s in shape)
    prefix, result = 1, 0
    for ell, s in shape:
        suffix //= s
        result += prefix * ((1 << ell) - s) * suffix
        prefix *= int(3 * s > 2 * (1 << ell))
    return result + prefix


def direct_addresses(shape):
    """Literal rational nearest rounding of every source coordinate."""
    checked_shape(shape)
    need(sum(ell for ell, _ in shape) <= CENSUS_BITS, "literal volume cap")
    axes = tuple(range(s) for _, s in reversed(shape))
    addresses = []
    for reverse_j in itertools.product(*axes):
        address, stride = 0, 1
        for (ell, s), j in zip(shape, reversed(reverse_j)):
            address += ((2 * (1 << ell) * j + s) // (2 * s)) * stride
            stride <<= ell
        addresses.append(address)
    need(len(addresses) == math.prod(s for _, s in shape), "source extent")
    return tuple(addresses)


def target_mask(shape):
    """Scan target digits; detect a source point by exact half-open bounds."""
    checked_shape(shape)
    bits = sum(ell for ell, _ in shape)
    need(bits <= CENSUS_BITS, "literal volume cap")
    selected = []
    for address in range(1 << bits):
        rest, occupied = address, True
        for ell, s in shape:
            t = 1 << ell
            digit, rest = rest % t, rest // t
            # At most one j lies in this interval because s/t < 1.
            lower = -(-(s * (2 * digit - 1)) // (2 * t))
            upper = -(-(s * (2 * digit + 1)) // (2 * t))
            occupied = occupied and max(lower, 0) < min(upper, s)
        selected.append(occupied)
    return tuple(selected)


def maximal_blocks(addresses):
    need(1 <= len(addresses) <= (1 << CENSUS_BITS), "bounded nonempty image")
    blocks, start, previous = [], addresses[0], addresses[0]
    for address in addresses[1:]:
        need(previous < address, "strict source order")
        if address != previous + 1:
            blocks.append((start, previous + 1))
            start = address
        previous = address
    blocks.append((start, previous + 1))
    return tuple(blocks)


def all_packets():
    """Every ordered packet with sum(ell) <= 10, including all valid s."""
    queue = [((), 0)]
    for index in range(MAX_PACKETS):
        if index == len(queue):
            break
        shape, bits = queue[index]
        for ell in range(2, CENSUS_BITS - bits + 1):
            for s in range((1 << (ell - 1)) + 1, 1 << ell):
                need(len(queue) < MAX_PACKETS, "packet capacity")
                queue.append((shape + ((ell, s),), bits + ell))
    need(index == len(queue), "complete bounded worklist")
    counts = [0] * (CENSUS_BITS + 1)
    counts[0] = 1
    for bits in range(2, CENSUS_BITS + 1):
        counts[bits] = sum(((1 << (ell - 1)) - 1) * counts[bits - ell]
                           for ell in range(2, bits + 1))
    need(sum(counts) == len(queue), "independent packet-coverage recurrence")
    return tuple(shape for shape, _ in queue[1:])


def census():
    totals = dict(packets=0, target_records=0, selected_records=0, blocks=0)
    for shape in all_packets():
        addresses = direct_addresses(shape)
        mask = target_mask(shape)
        selected = tuple(i for i, occupied in enumerate(mask) if occupied)
        need(addresses == selected, "independent source and target engines")
        blocks = maximal_blocks(addresses)
        need(len(blocks) == block_count(shape) == closed_sum(shape),
             "exact recurrence, finite sum and literal run count")
        copied = tuple(i for start, end in blocks for i in range(start, end))
        need(copied == addresses, "complete ordered copy with no holes")
        totals["packets"] += 1
        totals["target_records"] += len(mask)
        totals["selected_records"] += len(addresses)
        totals["blocks"] += len(blocks)
    return totals


def literal_fixture():
    shape = ((2, 3), (3, 7), (3, 5))
    addresses = direct_addresses(shape)
    blocks = maximal_blocks(addresses)
    # Every payload is distinct; hole values are arbitrary and nonzero.
    source = tuple(("record", 7 * i + 1) for i in range(256))
    frozen = tuple(source)
    result = tuple(value for start, end in blocks for value in source[start:end])
    need(source == frozen and result == tuple(source[i] for i in addresses),
         "arbitrary-payload preservation and exact readout")
    need(len(blocks) == block_count(shape) == 43, "named tensor fixture")
    return dict(shape=shape, T=len(source), S=len(result), blocks=len(blocks))


def controls():
    rejected = 0
    bad_shapes = ((), ((1, 1),), ((65, 3),), ((2, True),), ((2, 2),),
                  ((2, 4),), ((2,),), ((2, 3),) * 17, [(2, 3)])
    for shape in bad_shapes:
        try:
            block_count(shape)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid shape accepted")
    need(block_count(((2, 3),)) == 2, "fixed seam is not a cyclic seam")
    need(block_count(((3, 5),)) == 3, "trailing hole blocks a carry join")
    need(block_count(((2, 3), (3, 5))) == 8, "mixed carry fixture")
    need(block_count(((3, 5), (2, 3))) == 9, "axis order is part of contract")
    need(block_count(((2, 3),) * 16) == (3 ** 16 + 1) // 2,
         "large tensor evaluation without volume enumeration")
    return dict(rejected_inputs=rejected, boundary_controls=5)


def authenticated_files():
    manifest_path = HERE / "SOURCES.json"
    need(manifest_path.stat().st_size <= MAX_FILE_BYTES, "manifest size cap")
    source_manifest = json.loads(manifest_path.read_bytes())
    need(1 <= len(source_manifest["files"]) <= 8, "source-row cap")
    root = HERE.parents[1]
    bound_inputs = {}
    for row in source_manifest["files"]:
        if row["usage"] != "input":
            continue
        path = root / row["path"]
        need(path.is_file() and not path.is_symlink(), "regular source text")
        need(path.stat().st_size <= MAX_FILE_BYTES, "source size cap")
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        need(digest == row["sha256"], "source SHA256")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw)
        need(blob.hexdigest() == row["git_blob"], "source Git blob")
        bound_inputs[row["path"]] = digest
    package_hashes = {}
    for name in ("README.md", "PROOF.md", "SOURCES.json", "TASK.json",
                 "VERIFY.json", "verify.py"):
        path = HERE / name
        need(path.is_file() and not path.is_symlink(), "regular package file")
        need(path.stat().st_size <= MAX_FILE_BYTES, "package size cap")
        package_hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return dict(inputs=bound_inputs, package=package_hashes)


def main():
    hashes = authenticated_files()
    result = dict(status="PASS_ROUNDED_IMAGE_BLOCK_MINIMUM", census=census(),
                  fixture=literal_fixture(), controls=controls(), hashes=hashes,
                  scope="Scoped written proof with exact finite corroboration; no new kappa.")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
