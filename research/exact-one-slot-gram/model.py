"""Exact one-slot Gram model; Krzysztof Wojt with OpenAI Codex, Apache-2.0."""
from hashlib import sha256
import json
from pathlib import Path

import numpy as np

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
SOURCE = ("research/centre-polynomial-cache-limits/frozen/work/"
          "centre-encoding-campaign-20261014/lanes/circuit-interface/INTERFACE.json")
SOURCE_SHA256 = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
REPRESENTATIVES = (0, 1, 3, 7, 30, 128)
GENERATORS = tuple((tuple(range(8)), 1 << i) for i in range(1, 8)) + (
    ((0, 1, 2, 3, 5, 4, 7, 6), 0),
    ((0, 1, 2, 3, 6, 7, 4, 5), 0),
    ((0, 1, 3, 2, 4, 5, 7, 6), 0),
    ((0, 1, 4, 5, 2, 3, 6, 7), 0),
    ((0, 2, 1, 3, 4, 6, 5, 7), 0),
    ((1, 0, 2, 3, 4, 5, 7, 6), 0),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_query():
    raw = (ROOT / SOURCE).read_bytes()
    require(sha256(raw).hexdigest() == SOURCE_SHA256, "source hash")
    data = json.loads(raw)
    require(len(data["R"]) == 8 and len(data["ports"]) == 112, "query dimensions")
    roots = np.zeros((112, 8), dtype=np.int64)
    for i, row in enumerate(data["R"]):
        for j, value in row.items():
            roots[int(j), i] = int(value)
    ports = tuple(data["ports"])
    require(len(set(ports)) == 112, "port distinctness")
    require(all(type(q) is int and 0 < q < 512 and q.bit_count() % 2 for q in ports),
            "odd nine-bit port labels")
    require(np.all(np.isin(roots, (-1, 0, 1))), "root entries")
    require(np.all(np.count_nonzero(roots, axis=1) == 4), "root support")
    require(np.array_equal(roots.T @ roots, 56 * np.eye(8, dtype=np.int64)), "root normalization")
    return roots, ports


def canonical_root(root):
    values = tuple(int(x) for x in root)
    first = next(x for x in values if x)
    return tuple(first*x for x in values)


def linear_apply(images, value):
    result = 0
    for bit, image in enumerate(images):
        if value >> bit & 1:
            result ^= image
    return result


def label_map(ports, mapped_ports):
    pivots = {}
    for value, image in zip(ports, mapped_ports):
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                v, w = pivots[pivot]
                value, image = value ^ v, image ^ w
            else:
                pivots[pivot] = value, image
                break
        else:
            require(image == 0, "port map is linear")
    require(len(pivots) == 9, "port span")
    images = []
    for bit in range(9):
        value, image = 1 << bit, 0
        while value:
            v, w = pivots[value.bit_length()-1]
            value, image = value ^ v, image ^ w
        images.append(image)
    for i, a in enumerate(images):
        for j, b in enumerate(images):
            require((a & b).bit_count() % 2 == (i == j), "orthogonal label map")
    require(all(linear_apply(images, q) == r for q, r in zip(ports, mapped_ports)),
            "all-port label map")
    require(linear_apply(images, 511) == 511, "odd-vector fixed")
    return tuple(images)


def symmetries(roots, ports):
    lookup = {canonical_root(root): q for root, q in zip(roots, ports)}
    require(len(lookup) == 112, "root lines distinct")
    output = []
    for permutation, mask in GENERATORS:
        mapped = []
        for root in roots:
            transformed = [0]*8
            for i, x in enumerate(root):
                transformed[permutation[i]] = int(x) * (-1 if mask >> i & 1 else 1)
            mapped.append(lookup[canonical_root(transformed)])
        output.append((permutation, label_map(ports, mapped)))
    return tuple(output)


def label_orbits(generators, complement=True):
    unseen = set(range(512))
    result = []
    while unseen:
        first = min(unseen)
        orbit, queue = {first}, [first]
        for c in queue:
            images = [linear_apply(g[1], c) for g in generators]
            if complement:
                images.append(c ^ 511)
            for image in images:
                if image not in orbit:
                    orbit.add(image)
                    queue.append(image)
        unseen.difference_update(orbit)
        result.append(tuple(sorted(orbit)))
    return tuple(result)


def compose(left, right):
    """Composition of unsigned coordinate permutation and binary label map."""
    return (tuple(left[0][i] for i in right[0]),
            tuple(linear_apply(left[1], x) for x in right[1]))


def inverse(element):
    permutation, images = element
    inv_perm = tuple(permutation.index(i) for i in range(8))
    # Orthogonality makes the binary inverse the transpose.
    inv_images = tuple(sum(((images[j] >> i) & 1) << j for j in range(9)) for i in range(9))
    return inv_perm, inv_images


def stabilizer(c, generators):
    identity = tuple(range(8)), tuple(1 << i for i in range(9))
    transversal = {c: identity}
    queue = [c]
    for point in queue:
        for generator in generators:
            image = linear_apply(generator[1], point)
            if image not in transversal:
                transversal[image] = compose(generator, transversal[point])
                queue.append(image)
    result = set()
    for point in queue:
        for generator in generators:
            image = linear_apply(generator[1], point)
            h = compose(inverse(transversal[image]), compose(generator, transversal[point]))
            require(linear_apply(h[1], c) == c, "Schreier stabilizer")
            if h != identity:
                result.add(h)
    return tuple(sorted(result))


def sector(c, t, s, ports):
    require(c not in (0, 511) and 0 < c < 512 and t in (0, 1) and s in (-1, 1), "sector parameters")
    addresses = tuple(a for a in range(512)
                      if (a & (c ^ 511)).bit_count() % 2 == t and a < (a ^ c))
    require(len(addresses) == 128, "sector dimension")
    where = {a: i for i, a in enumerate(addresses)}
    targets, signs = [], []
    for q in ports:
        target, sign = [], []
        for a in addresses:
            if (q & c).bit_count() % 2:
                dest = a ^ q
                sign.append(1 if dest < (dest ^ c) else s)
                target.append(where[min(dest, dest ^ c)])
            else:
                target.append(where[a])
                sign.append(1 - 2*((q & a).bit_count() % 2))
        targets.append(target)
        signs.append(sign)
    return addresses, np.array(targets, dtype=np.int64), np.array(signs, dtype=np.int64)


def coordinate_orbits(c, addresses, group):
    where = {a:i for i,a in enumerate(addresses)}
    size = len(addresses)
    parent = list(range(8*size))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for permutation, images in group:
        mapped = [where[min(linear_apply(images, a), linear_apply(images, a)^c)] for a in addresses]
        for i in range(8):
            for j, image in enumerate(mapped):
                x, y = find(i*size+j), find(permutation[i]*size+image)
                if x != y:
                    parent[max(x, y)] = min(x, y)
    groups = {}
    for i in range(8*size):
        groups.setdefault(find(i), []).append(i)
    return tuple(tuple(v) for _,v in sorted(groups.items()))


def dense_matrix(roots, targets, signs):
    width = targets.shape[1]
    matrix = np.zeros((8*width, 8*width), dtype=np.int64)
    for root, target, sign in zip(roots, targets, signs):
        support = np.flatnonzero(root)
        for i in support:
            for j in support:
                matrix[i*width+target, j*width+np.arange(width)] += int(root[i]*root[j])*sign
    require(np.array_equal(matrix, matrix.T), "symmetric sector matrix")
    return matrix


def apply(value, roots, targets, signs, modulus=None):
    """Apply integer B=4A to one or several columns, with no floating arithmetic."""
    result = np.zeros_like(value)
    for root, target, sign in zip(roots, targets, signs):
        support = np.flatnonzero(root)
        lifted = sum((int(root[i])*value[i] for i in support))
        moved = lifted[target] * (sign if value.ndim == 2 else sign[:, None])
        for i in support:
            result[i] += int(root[i])*moved
    return result if modulus is None else result % modulus


def polynomial_action(coefficients, seeds, roots, targets, signs):
    """Integer Horner evaluation of coefficients in ascending order."""
    result = coefficients[-1]*seeds
    for coefficient in reversed(coefficients[:-1]):
        result = apply(result, roots, targets, signs)
        if coefficient:
            result += coefficient*seeds
    return result


def zero_matrices(roots, ports):
    signs = np.array([[1-2*((a&q).bit_count()%2) for q in ports] for a in range(512)], dtype=np.int64)
    return np.einsum('aq,qi,qj->aij', signs, roots, roots)
