"""Read a sparse open-boundary tensor train and sample exact cut bases."""

from dataclasses import dataclass
from field import Basis, G, ONE, ZERO, dot


@dataclass(frozen=True)
class Core:
    left: int
    right: int
    slices: tuple


def positive(value):
    if type(value) is not int or value < 1:
        raise ValueError("a dimension must be a positive integer")
    return value


def index(value, upper):
    if type(value) is not int or not 0 <= value < upper:
        raise ValueError("index outside its declared dimension")
    return value


def read_train(data):
    if data["format"] != "clifford-tt/1":
        raise ValueError("unknown input format")
    n = positive(data["qubits"])
    alphabet = 4**n
    cores = []
    for record in data["cores"]:
        left, right = positive(record["left"]), positive(record["right"])
        entries = [dict() for _ in range(alphabet)]
        for q, i, j, re, im in record["entries"]:
            slot = entries[index(q, alphabet)]
            key = index(i, left), index(j, right)
            if key in slot:
                raise ValueError("duplicate matrix entry")
            slot[key] = G.parse(re, im)
        slices = tuple(tuple((i, j, z) for (i, j), z in sorted(a.items()) if z)
                       for a in entries)
        cores.append(Core(left, right, slices))
    chain = tuple(cores[index(i, len(cores))] for i in data["sites"])
    if not chain or chain[0].left != 1 or chain[-1].right != 1:
        raise ValueError("the train needs two scalar boundaries")
    if any(a.right != b.left for a, b in zip(chain, chain[1:])):
        raise ValueError("incompatible adjacent dimensions")
    # A COO file can name a very large unused bond by a single integer.
    # Only indices present on both sides can carry a nonzero term.
    occupied = {}
    for core in chain:
        if id(core) not in occupied:
            entries = [entry for matrix in core.slices for entry in matrix]
            occupied[id(core)] = ({i for i, _, _ in entries}, {j for _, j, _ in entries})
    cuts = [(0,)]
    for a, b in zip(chain, chain[1:]):
        cuts.append(tuple(sorted(occupied[id(a)][1] & occupied[id(b)][0])))
    cuts.append((0,))
    packed, packed_chain = {}, []
    for t, core in enumerate(chain):
        left_keys, right_keys = cuts[t:t+2]
        key = (id(core), left_keys, right_keys)
        if key not in packed:
            li = {v: i for i, v in enumerate(left_keys)}
            ri = {v: i for i, v in enumerate(right_keys)}
            slices = tuple(tuple((li[i], ri[j], z) for i, j, z in matrix
                                 if i in li and j in ri) for matrix in core.slices)
            packed[key] = Core(max(1, len(li)), max(1, len(ri)), slices)
        packed_chain.append(packed[key])
    return n, tuple(packed_chain)


def advance(v, matrix, size, backward=False):
    result = [ZERO] * size
    for i, j, value in matrix:
        if backward:
            i, j = j, i
        if v[i]:
            result[j] = result[j] + v[i] * value
    return tuple(result)


def cut_basis(cores, backward=False):
    states = [((), (ONE,))]
    for core in cores:
        size = core.left if backward else core.right
        # Equal slices give the same boundary state for each sampled word.
        unique = {}
        for q, matrix in enumerate(core.slices):
            if matrix:
                unique.setdefault(matrix, q)
        new = []
        basis = Basis()
        for word, v in states:
            for matrix, q in unique.items():
                value = advance(v, matrix, size, backward)
                if basis.add(value):
                    new.append(((q,) + word if backward else word + (q,), value))
                    if len(new) == size:
                        break
            if len(new) == size:
                break
        states = new
    return states


def cut_slices(left, core, right):
    cache = {}
    result = []
    for physical in core.slices:
        if physical not in cache:
            rows = [advance(v, physical, core.right) for _, v in left]
            cache[physical] = tuple(tuple(dot(row, v) for _, v in right) for row in rows)
        result.append(cache[physical])
    return result


def exact_match(chain, signatures, coefficients):
    """Test zero on the full product alphabet by reachable row spaces."""
    states = [(ONE, *coefficients)]
    for t, core in enumerate(chain):
        alphabet = dict.fromkeys(
            (matrix, tuple(w[q] for w in signatures))
            for q, matrix in enumerate(core.slices)
        )
        last = t == len(chain) - 1
        next_states = []
        basis = Basis()
        for v in states:
            for matrix, letters in alphabet:
                actual = advance(v[:core.left], matrix, core.right)
                prediction = tuple(a*b for a, b in zip(v[core.left:], letters, strict=True))
                if last:
                    if actual[0] != sum(prediction, ZERO):
                        return False
                else:
                    extended = (*actual, *prediction)
                    if basis.add(extended):
                        next_states.append(extended)
            if not last and len(next_states) == core.right + len(signatures):
                break
        states = next_states
    return True
