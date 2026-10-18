"""Exact formal and natural censuses. Hanson Sun / OpenAI Codex, Apache-2.0."""

from collections import Counter, defaultdict
import hashlib

SEED = 18
ADDRESS_ID = 273  # Rows (1, 2, 4), three bits per row, low row first.
LABELS = [(i, j) for i in range(3) for j in range(3) if i != j]
GENERATORS = [(u, v, i, j) for u in range(1, 4) for v in range(1, 4)
              if (u & v).bit_count() % 2 for i, j in LABELS]
GENERATORS = GENERATORS[SEED:] + GENERATORS[:SEED]
NATURAL_ID = sum(1 << (6 * r + r) for r in range(6))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def multiply(a, b):
    """3x3 binary matrix product, using row combinations."""
    out = 0
    for row in range(3):
        value = 0
        for column in range(3):
            if a >> (3 * row + column) & 1:
                value ^= b >> (3 * column) & 7
        out |= value << (3 * row)
    return out


class Algebra:
    def __init__(self):
        labels = [ADDRESS_ID ^ (1 << (3 * i + j)) for i, j in LABELS]
        direct = {ADDRESS_ID: ()}
        queue = [ADDRESS_ID]
        for state in queue:
            for k, label in enumerate(labels):
                target = multiply(label, state)
                if target not in direct:
                    direct[target] = direct[state] + (k,)
                    queue.append(target)
        require(len(queue) == 168, "address Cayley group has wrong order")
        self.group = sorted(queue)
        self.index = {g: i for i, g in enumerate(self.group)}
        self.identity = self.index[ADDRESS_ID]
        self.direct = [len(direct[g]) for g in self.group]
        self.paths = [direct[g] for g in self.group]
        self.product = [[self.index[multiply(a, b)] for b in self.group]
                        for a in self.group]
        self.inverse = [next(b for b in range(168)
                             if self.product[a][b] == self.identity)
                        for a in range(168)]
        self.bits = [[1 << b for b in row] for row in self.product]
        self.labels = [self.index[g] for g in labels]
        self.generators = [(u, v, self.index[ADDRESS_ID ^ (1 << (3 * i + j))])
                           for u, v, i, j in GENERATORS]
        self.division = [[self.product[a][self.inverse[b]] for b in range(168)]
                         for a in range(168)]
        e = 1 << self.identity
        self.unit = (e, 0, 0, e)

    def translate(self, polynomial, g):
        out = 0
        image = self.bits[g]
        while polynomial:
            bit = polynomial & -polynomial
            polynomial ^= bit
            out ^= image[bit.bit_length() - 1]
        return out

    def step(self, matrix, generator):
        """Left multiplication by I + ([g]+1) uv^T, simultaneously."""
        u, v, g = generator
        a, b, c, d = matrix
        x = (a if v & 1 else 0) ^ (c if v & 2 else 0)
        y = (b if v & 1 else 0) ^ (d if v & 2 else 0)
        x ^= self.translate(x, g)
        y ^= self.translate(y, g)
        return (a ^ (x if u & 1 else 0), b ^ (y if u & 1 else 0),
                c ^ (x if u & 2 else 0), d ^ (y if u & 2 else 0))

    def word(self, word):
        state = self.unit
        for u, v, i, j in word:
            g = self.index[ADDRESS_ID ^ (1 << (3 * i + j))]
            state = self.step(state, (u, v, g))
        return state

    def target(self, a, b):
        return (1 << a, 0, 0, 1 << b)

    def direct_word(self, a, b):
        return ([(1, 1, *LABELS[k]) for k in self.paths[a]]
                + [(2, 2, *LABELS[k]) for k in self.paths[b]])

    def canonical_row(self, a, b):
        """Canonical row under monomial left translation, not linear span."""
        candidates = a or b
        require(candidates != 0, "zero row cannot belong to an invertible word")
        best = None
        coordinate = None
        while candidates:
            bit = candidates & -candidates
            candidates ^= bit
            g = bit.bit_length() - 1
            key = (self.translate(a, self.inverse[g]),
                   self.translate(b, self.inverse[g]))
            if best is None or key < best:
                best, coordinate = key, g
            elif key == best:
                raise ValueError("nontrivial row stabilizer in an invertible word")
        return best, coordinate


def census(identity, generators, step, radius=4):
    distance = {identity: 0}
    layer = [identity]
    layers = [1]
    transitions = 0
    for depth in range(1, radius + 1):
        following = []
        for state in layer:
            for generator in generators:
                transitions += 1
                target = step(state, generator)
                if target not in distance:
                    distance[target] = depth
                    following.append(target)
        layers.append(len(following))
        layer = following
    return distance, layers, transitions


def join(buckets, division):
    """All radius-four pairs; 9 means no word of length <=8, not distance 9."""
    minimum = [[9] * 168 for _ in range(168)]
    pairs = 0
    for entries in buckets.values():
        pairs += len(entries) ** 2
        for da, xa, ya in entries:
            rx, ry = division[xa], division[ya]
            for db, xb, yb in entries:
                row = minimum[rx[xb]]
                column = ry[yb]
                cost = da + db
                if cost < row[column]:
                    row[column] = cost
    return minimum, pairs


def formal_census(algebra):
    distances, layers, transitions = census(algebra.unit, algebra.generators,
                                            algebra.step)
    buckets = defaultdict(list)
    for state, distance in distances.items():
        top, a = algebra.canonical_row(*state[:2])
        bottom, b = algebra.canonical_row(*state[2:])
        buckets[top + bottom].append((distance, a, b))
    minimum, pairs = join(buckets, algebra.division)
    summary = {"layers": layers, "states": len(distances), "transitions": transitions,
               "cosets": len(buckets), "largest_coset": max(map(len, buckets.values())),
               "ordered_join_pairs": pairs, "table_sha256": table_digest(minimum)}
    return distances, minimum, summary


def natural_step(state, generator):
    u, v, i, j = generator
    source = 0
    for b in range(2):
        if v >> b & 1:
            source ^= state >> (6 * (3 * b + j)) & 63
    for a in range(2):
        if u >> a & 1:
            state ^= source << (6 * (3 * a + i))
    return state


def reduced_rows(rows):
    rows = list(rows)
    position = 0
    for column in range(6):
        pivot = next((i for i in range(position, 3) if rows[i] >> column & 1), None)
        if pivot is None:
            continue
        rows[position], rows[pivot] = rows[pivot], rows[position]
        for i in range(3):
            if i != position and rows[i] >> column & 1:
                rows[i] ^= rows[position]
        position += 1
        if position == 3:
            break
    require(position == 3, "singular row block")
    return tuple(rows)


def natural_census(algebra):
    distances, layers, transitions = census(NATURAL_ID, GENERATORS, natural_step)
    row_groups = defaultdict(list)
    for state, distance in distances.items():
        rows = [state >> (6 * r) & 63 for r in range(6)]
        row_groups[reduced_rows(rows[:3]) + reduced_rows(rows[3:])].append((state, distance))
    buckets = {}
    for key, entries in row_groups.items():
        maps = []
        for offset in (0, 3):
            span = {0: 0}
            for j, row in enumerate(key[offset:offset + 3]):
                span.update({s ^ row: c ^ (1 << j) for s, c in list(span.items())})
            maps.append(span)
        coordinates = []
        for state, distance in entries:
            a = sum(maps[0][state >> (6 * r) & 63] << (3 * r) for r in range(3))
            b = sum(maps[1][state >> (6 * (r + 3)) & 63] << (3 * r) for r in range(3))
            coordinates.append((distance, algebra.index[a], algebra.index[b]))
        buckets[key] = coordinates
    minimum, pairs = join(buckets, algebra.division)
    summary = {"layers": layers, "states": len(distances), "transitions": transitions,
               "cosets": len(buckets), "largest_coset": max(map(len, buckets.values())),
               "ordered_join_pairs": pairs, "table_sha256": table_digest(minimum)}
    return minimum, summary


def natural_image(algebra, matrix):
    out = 0
    for a in range(2):
        for b in range(2):
            polynomial = matrix[2 * a + b]
            block = 0
            while polynomial:
                bit = polynomial & -polynomial
                polynomial ^= bit
                block ^= algebra.group[bit.bit_length() - 1]
            for r in range(3):
                out ^= ((block >> (3 * r) & 7) << (3 * b)) << (6 * (3 * a + r))
    return out


def table_bytes(table):
    return bytes(value for row in table for value in row)


def table_digest(table):
    return hashlib.sha256(table_bytes(table)).hexdigest()


def state_bytes(state, distance):
    return b"".join(p.to_bytes(21, "little") for p in state) + bytes([distance])


def histogram(values):
    return {str(k): v for k, v in sorted(Counter(values).items())}
