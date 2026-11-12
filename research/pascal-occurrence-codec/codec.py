"""Exact Pascal interval codec for a separated lockstep flow.

Apache-2.0. Prepared for CubeJerry with substantial OpenAI assistance.
This is an offline logical occurrence codec, not a fixed-tape dispatcher.
"""
from dataclasses import dataclass


def require(condition, message):
    if not condition:
        raise ValueError(message)


def natural(value, message):
    require(type(value) is int and value >= 0, message)


@dataclass(frozen=True)
class Rule:
    roles: tuple
    rounds: tuple
    owned: tuple = ("bank",)
    ambient: int | None = None

    def __post_init__(self):
        require(bool(self.roles) and bool(self.rounds), "nonempty rule")
        names = tuple(name for name, _ in self.roles)
        require(len(set(names)) == len(names), "duplicate productive role")
        require(len(set(self.owned)) == len(self.owned), "duplicate owned role")
        require(not set(names) & set(self.owned), "owned/productive alias")
        require(all(type(k) is int and k >= 2 for _, k in self.roles),
                "target ranks are integers at least two")
        require(all(type(r) is int and 1 <= r < min(k for _, k in self.roles)
                    and owner in names + self.owned for r, owner in self.rounds),
                "positive separated paid rank and real owner")
        if self.ambient is None:
            object.__setattr__(self, "ambient", max(k for _, k in self.roles))
        require(type(self.ambient) is int and
                self.ambient >= max(k for _, k in self.roles), "ambient cap")

    @property
    def types(self):
        return tuple(sorted(set(k for _, k in self.roles)))

    @property
    def weights(self):
        return tuple(sum(k == rank for _, k in self.roles) for rank in self.types)

    def type_of(self, role):
        names = tuple(name for name, _ in self.roles)
        require(role in names, "unknown productive role")
        rank = self.roles[names.index(role)][1]
        return self.types.index(rank)

    def same_type_roles(self, i):
        return tuple(name for name, k in self.roles if k == self.types[i])


@dataclass(frozen=True)
class Unit:
    path: tuple
    point: tuple
    ordinal: int


def validate_point(rule, point):
    require(len(point) == len(rule.types), "point dimension")
    for a in point:
        natural(a, "nonnegative integer point")


def column(rule, point):
    validate_point(rule, point)
    out = 1
    for k, a in zip(rule.types, point):
        for _ in range(a):
            out *= k
    return out


def multiplicity(rule, point):
    """Multinomial times weights, using exact small-factor arithmetic."""
    validate_point(rule, point)
    remaining, out = sum(point), 1
    for a, weight in zip(point, rule.weights):
        choose = 1
        for j in range(1, a + 1):
            choose = choose * (remaining - j + 1) // j
        out *= choose
        for _ in range(a):
            out *= weight
        remaining -= a
    return out


def remove_letter(point, i):
    require(0 <= i < len(point) and point[i] > 0, "missing target letter")
    return tuple(a - int(j == i) for j, a in enumerate(point))


def encode(rule, parent_point, child_ordinal, role):
    """Exact ordinal in the parent's Pascal bucket."""
    validate_point(rule, parent_point)
    i = rule.type_of(role)
    child_point = remove_letter(parent_point, i)
    natural(child_ordinal, "child ordinal")
    require(child_ordinal < multiplicity(rule, child_point), "child ordinal range")
    offset = 0
    for j in range(i):
        if parent_point[j]:
            offset += rule.weights[j] * multiplicity(rule, remove_letter(parent_point, j))
    same = rule.same_type_roles(i)
    return offset + len(same) * child_ordinal + same.index(role)


def decode(rule, parent_point, parent_ordinal):
    """Inverse: (child point, child ordinal, productive role)."""
    validate_point(rule, parent_point)
    require(sum(parent_point) > 0, "no Pascal split of an empty word")
    natural(parent_ordinal, "parent ordinal")
    require(parent_ordinal < multiplicity(rule, parent_point), "parent ordinal range")
    residual = parent_ordinal
    for i, a in enumerate(parent_point):
        if not a:
            continue
        child = remove_letter(parent_point, i)
        names = rule.same_type_roles(i)
        size = len(names) * multiplicity(rule, child)
        if residual < size:
            ordinal, role_index = divmod(residual, len(names))
            return child, ordinal, names[role_index]
        residual -= size
    raise ValueError("Pascal identity failed")


class FlowCodec:
    def __init__(self, rule, rank):
        natural(rank, "ambient rank")
        require(rank >= rule.ambient, "at least one unit fits")
        self.rule, self.rank = rule, rank
        capacity, self.height = rank // rule.ambient, 0
        power, smallest = 1, min(rule.types)
        while power <= capacity // smallest:
            power *= smallest
            self.height += 1

    def dilation(self, path):
        value = 1
        for j in path:
            natural(j, "paid occurrence")
            require(j < len(self.rule.rounds), "paid occurrence range")
            value *= self.rule.rounds[j][0]
        return value

    def validate_unit(self, unit):
        validate_point(self.rule, unit.point)
        require(len(unit.path) + sum(unit.point) == self.height, "class degree")
        natural(unit.ordinal, "unit ordinal")
        require(unit.ordinal < multiplicity(self.rule, unit.point), "unit ordinal range")
        require(self.rule.ambient * self.dilation(unit.path) *
                column(self.rule, unit.point) <= self.rank, "absent unit")

    def parent(self, unit, role):
        """None means a fresh source, otherwise the exact issuing parent."""
        self.validate_unit(unit)
        i = self.rule.type_of(role)
        if not unit.path:
            return None
        point = tuple(a + int(j == i) for j, a in enumerate(unit.point))
        path = unit.path[:-1]
        if self.rule.ambient * self.dilation(path) * column(self.rule, point) > self.rank:
            return None
        return Unit(path, point, encode(self.rule, point, unit.ordinal, role))

    def owner(self, unit, role, namespace="flow", replica=0):
        """Resolve a canonical field identity without any occurrence table."""
        natural(replica, "replica")
        self.validate_unit(unit)
        self.rule.type_of(role)
        while True:
            parent = self.parent(unit, role)
            if parent is None:
                return (namespace, replica, "source", unit.path, unit.point, unit.ordinal, role)
            parent_owner = self.rule.rounds[unit.path[-1]][1]
            if parent_owner in self.rule.owned:
                return (namespace, replica, "owned", parent.path, parent.point,
                        parent.ordinal, parent_owner)
            unit, role = parent, parent_owner

    def paid_owner(self, unit, j, namespace="flow", replica=0):
        self.validate_unit(unit)
        natural(j, "paid occurrence")
        require(j < len(self.rule.rounds), "paid occurrence range")
        owner = self.rule.rounds[j][1]
        if owner in self.rule.owned:
            return (namespace, replica, "owned", unit.path, unit.point, unit.ordinal, owner)
        return self.owner(unit, owner, namespace, replica)

    def iter_points(self, path):
        """Stream the predecessor's lexicographic lattice order."""
        degree = self.height - len(path)
        require(degree >= 0, "path too deep")
        limit = self.rank // (self.rule.ambient * self.dilation(path))
        types = self.rule.types

        def visit(i, left, value, prefix):
            if i == len(types):
                if left == 0:
                    yield tuple(prefix)
                return
            for a in range(left + 1):
                if value > limit:
                    break
                yield from visit(i + 1, left - a, value, prefix + [a])
                value *= types[i]

        yield from visit(0, degree, 1, [])

    def iter_units(self, path):
        for point in self.iter_points(path):
            for ordinal in range(multiplicity(self.rule, point)):
                yield Unit(path, point, ordinal)
