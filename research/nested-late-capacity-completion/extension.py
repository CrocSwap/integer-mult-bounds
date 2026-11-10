"""Bounded prime-field reference for the nested late-capacity theorem.

Vectors act on the left; matrix rows are images of coordinate vectors.
The universal statement is in PROOF.md. This offline reference accepts
prime fields through seven, dimension at most six and at most eight contacts.
"""

from dataclasses import dataclass


def require(condition, message):
    if not condition:
        raise ValueError(message)


def reduced(rows, q, width):
    """Canonical row basis; callers have validated the finite dimensions."""
    work = [list(row) for row in rows]
    pivot = 0
    for column in range(width):
        found = next((i for i in range(pivot, len(work)) if work[i][column]), None)
        if found is None:
            continue
        work[pivot], work[found] = work[found], work[pivot]
        scale = pow(work[pivot][column], -1, q)
        work[pivot] = [(x * scale) % q for x in work[pivot]]
        for i in range(len(work)):
            if i != pivot:
                scale = work[i][column]
                work[i] = [(x - scale * y) % q
                           for x, y in zip(work[i], work[pivot])]
        pivot += 1
        if pivot == len(work):
            break
    return tuple(tuple(row) for row in work[:pivot])


def combine(coefficients, rows, q, n):
    return tuple(sum(a * row[j] for a, row in zip(coefficients, rows)) % q
                 for j in range(n))


def kernel(rows, q, width):
    basis = reduced(rows, q, width)
    pivots = tuple(next(j for j, x in enumerate(row) if x) for row in basis)
    result = []
    for free in range(width):
        if free not in pivots:
            vector = [0] * width
            vector[free] = 1
            for pivot, row in zip(pivots, basis):
                vector[pivot] = -row[free] % q
            result.append(tuple(vector))
    return tuple(result)


def intersection_images(u, images, source, q, n):
    """Images under h of a basis of U intersect source."""
    columns = u + tuple(tuple(-x % q for x in row) for row in source)
    relations = kernel(tuple(zip(*columns)), q, len(columns))
    values = tuple(combine(row[:len(u)], images, q, n) for row in relations)
    return reduced(values, q, n)


@dataclass(frozen=True)
class Problem:
    q: int
    n: int
    u: tuple
    images: tuple
    sources: tuple
    capacities: tuple

    def validate(self):
        require(type(self.q) is int and self.q in (2, 3, 5, 7), "unsupported field")
        require(type(self.n) is int and 0 <= self.n <= 6, "dimension outside 0..6")
        require(type(self.u) is tuple and type(self.images) is tuple,
                "partial-map bases must be tuples")
        require(type(self.sources) is tuple and type(self.capacities) is tuple,
                "contacts must be tuples")
        require(len(self.sources) == len(self.capacities) <= 8, "contact count")
        spaces = (self.u, self.images) + self.sources + self.capacities
        for space in spaces:
            require(type(space) is tuple and len(space) <= self.n, "basis shape")
            for row in space:
                require(type(row) is tuple and len(row) == self.n, "vector shape")
                require(all(type(x) is int and 0 <= x < self.q for x in row),
                        "noncanonical coordinate")
            require(len(reduced(space, self.q, self.n)) == len(space),
                    "dependent supplied basis")
        require(len(self.u) == len(self.images), "partial map is not an injection")
        previous = ()
        for capacity in self.capacities:
            require(len(reduced(previous + capacity, self.q, self.n)) == len(capacity),
                    "target capacities are not nested")
            previous = capacity


def stages(problem):
    """Return cumulative source bases and their exact quotient invariants."""
    problem.validate()
    q, n = problem.q, problem.n
    cumulative = ()
    result = []
    for source, capacity in zip(problem.sources, problem.capacities):
        cumulative = reduced(cumulative + source, q, n)
        fixed = intersection_images(problem.u, problem.images, cumulative, q, n)
        compatible = len(reduced(fixed + capacity, q, n)) == len(capacity)
        e = len(reduced(problem.u + cumulative, q, n)) - len(problem.u)
        c0 = len(capacity) + len(problem.images) - len(
            reduced(capacity + problem.images, q, n))
        result.append((cumulative, compatible, e, len(capacity), c0))
    return tuple(result)


def count_extensions(problem):
    count, previous = 1, 0
    for _, compatible, e, c, c0 in stages(problem):
        if not compatible or e > c - c0:
            return 0
        count *= problem.q ** (c0 * (e - previous))
        for j in range(previous, e):
            count *= problem.q ** (c - c0) - problem.q ** j
        previous = e
    for j in range(len(problem.u) + previous, problem.n):
        count *= problem.q ** problem.n - problem.q ** j
    require(count > 0, "feasible count must be positive")
    return count


def add_pair(vector, choices, domain, image, q, n):
    """Append one independent vector and its independently chosen image."""
    if len(reduced(tuple(domain) + (vector,), q, n)) == len(domain):
        return
    chosen = next((w for w in choices if
                   len(reduced(tuple(image) + (w,), q, n)) > len(image)), None)
    require(chosen is not None, "proved capacity unexpectedly exhausted")
    domain.append(vector)
    image.append(chosen)


def construct_extension(problem):
    data = stages(problem)
    if any(not compatible or e > c - c0 for _, compatible, e, c, c0 in data):
        return None
    q, n = problem.q, problem.n
    domain, image = list(problem.u), list(problem.images)
    for (source, _, _, _, _), capacity in zip(data, problem.capacities):
        for vector in source:
            add_pair(vector, capacity, domain, image, q, n)
    standard = tuple(tuple(int(i == j) for j in range(n)) for i in range(n))
    for vector in standard:
        add_pair(vector, standard, domain, image, q, n)
    require(len(domain) == len(image) == n, "completion dimension")
    augmented = tuple(left + right for left, right in zip(domain, image))
    answer = tuple(row[n:] for row in reduced(augmented, q, 2 * n))
    require(len(reduced(answer, q, n)) == n, "completion must be invertible")
    for vector, expected in zip(problem.u, problem.images):
        require(combine(vector, answer, q, n) == expected, "prescribed value")
    for source, capacity in zip(problem.sources, problem.capacities):
        actual = tuple(combine(v, answer, q, n) for v in source)
        require(len(reduced(actual + capacity, q, n)) == len(capacity),
                "late inclusion")
    return answer
