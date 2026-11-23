"""Full-field symbolic oracle for the imported finite compiler.

The contributor product/schedule is the implementation under test. This oracle
does not import its array model or expected leaf-count routine. It uses the group
algebra of order-four commuting axis gates and coordinate permutations, retaining
arbitrary complete input fields and their correlations. Nonzero private erasure
is explicitly counted as an inherited contract, not supplied by this test.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import cache
from types import ModuleType
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REF = HERE / "inputs/compiler"


def module(name):
    path = REF / (name + ".py")
    value = ModuleType(name)
    value.__file__ = str(path)
    sys.modules[name] = value
    # Execute the source bytes; a stale .pyc can never replace this oracle input.
    exec(compile(path.read_bytes(), str(path), "exec"), value.__dict__)
    return value


schedule = module("schedule")
product = module("product")


def need(ok, message):
    if not ok:
        raise ValueError(message)


class Oracle:
    def __init__(self, n, lift, width, native, fault=None):
        self.n, self.lift = n, lift
        self.dim = n * lift + 2
        self.ident = tuple(range(self.dim))
        self.zero_exponents = (0,) * self.dim
        self.fields = {i: {(i, self.ident, self.zero_exponents): Q(1)} for i in range(width)}
        self.next_owner = width
        self.public_width = width
        self.native_word = native
        self.fault = fault
        self.leaves = self.allocations = self.clean_retirements = self.dirty_retirements = 0
        self.zero_queries = self.dropped_queries = self.native_calls = 0
        self.first_zero = None

    def scale(self, owner, value):
        self.fields[owner] = {key: scalar * value for key, scalar in self.fields[owner].items()
                              if scalar * value}

    def add(self, target, source, value):
        row = Counter(self.fields[target])
        for key, scalar in self.fields[source].items():
            row[key] += value * scalar
        self.fields[target] = {key: scalar for key, scalar in row.items() if scalar}

    def zero(self):
        owner = self.next_owner
        self.next_owner += 1
        self.fields[owner] = {}
        self.allocations += 1
        if self.first_zero is None:
            self.first_zero = owner
        return self.first_zero if self.fault == "alias_zero" else owner

    def retire_zero(self, owner):
        need(not self.fields[owner], "a discarded target is not zero at its endpoint")
        self.clean_retirements += 1
        del self.fields[owner]

    def retire_owned(self, owner):
        self.dirty_retirements += bool(self.fields[owner])
        del self.fields[owner]

    def move(self, owner, order, inverse):
        need(len(order) == self.n and set(order) == set(range(self.n)), "whole axis permutation")
        if self.fault == "wrong_return" and inverse:
            inverse = False
        sigma = list(self.ident)
        for new, old in enumerate(order):
            for offset in range(self.lift):
                a, b = new * self.lift + offset, old * self.lift + offset
                if inverse:
                    sigma[a] = b
                else:
                    sigma[b] = a
        out = Counter()
        for (source, perm, powers), scalar in self.fields[owner].items():
            new_perm = tuple(sigma[old] for old in perm)
            new_powers = [0] * self.dim
            for old, exponent in enumerate(powers):
                new_powers[sigma[old]] = exponent
            out[(source, new_perm, tuple(new_powers))] += scalar
        self.fields[owner] = {key: scalar for key, scalar in out.items() if scalar}

    def leaf(self, owner, axis):
        need(0 <= axis < self.n, "leaf axis")
        if not self.fields[owner]:
            self.zero_queries += 1
            if self.fault == "drop_zero_query":
                self.dropped_queries += 1
                return
        self.leaves += 1
        out = Counter()
        for (source, perm, powers), scalar in self.fields[owner].items():
            updated = list(powers)
            for offset in range(self.lift):
                pos = axis * self.lift + offset
                updated[pos] = (updated[pos] + (-1 if self.fault == "inverse_leaf" else 1)) % 4
            out[(source, perm, tuple(updated))] += scalar
        self.fields[owner] = {key: scalar for key, scalar in out.items() if scalar}

    def native(self, owners, columns):
        self.native_calls += 1
        yield from self.native_word(self, owners, columns)

    def final_check(self):
        powers = (1,) * (self.n * self.lift) + (0, 0)
        expected = {i: {(i, self.ident, powers): Q(1)} for i in range(self.public_width)}
        need(self.fields == expected, "arbitrary complete-field endpoint or unretired owner")


def raw_word(machine, owners, columns):
    """Direct-sum ranks 1 and 3 on a true four-axis workspace."""
    x, y = owners
    temp = machine.zero()
    machine.add(temp, y, Q(1))
    exterior = Q(3, 5) ** columns if machine.fault == "tensor_exterior" else Q(3, 5)
    machine.scale(temp, exterior)
    machine.add(x, temp, Q(1))
    blocks = [tuple(range(i * columns, (i + 1) * columns)) for i in range(4)]
    order = blocks[2] + blocks[0] + blocks[1] + blocks[3] + tuple(range(4 * columns, machine.n))
    for owner in (x, temp):
        machine.move(owner, order, False)
    yield x, blocks[1]
    yield temp, blocks[1]
    machine.add(x, temp, Q(-1))
    yield temp, blocks[2] + blocks[0]
    for owner in (x, temp):
        machine.move(owner, order, True)
    machine.scale(temp, Q(5, 3))
    machine.fields[y], machine.fields[temp] = machine.fields[temp], machine.fields[y]
    machine.retire_owned(temp)


def independent_leaf_count(word, n):
    @cache
    def f(e):
        if e < word.grade:
            return Q(e)
        c, tail = divmod(e, word.grade)
        return tail + sum((f(r * c) for r in word.paid), Q(0)) / word.roles
    if n < word.ambient:
        return Q(n)
    cap = word.grade * (n // word.ambient)
    total = Q(0)
    used = 0
    while used < n:
        take = min(cap, n - used)
        total += f(take)
        used += take
    return total


def one_case(n, lift, fault=None):
    raw = product.Native(4, (1, 3), (1, 1, 2), raw_word)
    word, native = product.specialize(raw, {"1": 1, "3": 1}, 2)
    need((word.ambient, word.grade, word.roles) == (16, 3, 2), "homogeneous product data")
    need(Counter(word.paid) == {1: 4, 2: 6}, "every split request retained")
    width = word.root_width(n)
    machine = Oracle(n, lift, width, native, fault)
    schedule.expand(word, n, list(range(width)), machine)
    machine.final_check()
    need(machine.leaves == width * independent_leaf_count(word, n),
         "zero-valued queries cannot disappear from the full invoice")
    need(machine.clean_retirements and machine.dirty_retirements and machine.zero_queries,
         "fixture must exercise clean zeros, dirty private tags and zero queries")
    return {"n": n, "lift": lift, "width": width, "native_calls": machine.native_calls,
            "paid_leaves": machine.leaves, "zero_queries": machine.zero_queries,
            "clean_retirements": machine.clean_retirements,
            "nonzero_owned_retirements": machine.dirty_retirements}


def rejects(fault):
    try:
        one_case(35, 2, fault)
    except ValueError as error:
        return {"fault": fault, "detected": str(error)}
    raise ValueError("mutation survived: " + fault)


def main():
    cases = [one_case(n, lift) for n in (16, 17, 23, 32, 35, 48) for lift in (1, 2, 3)]
    mutations = [rejects(f) for f in ("alias_zero", "wrong_return", "drop_zero_query",
                                     "tensor_exterior", "inverse_leaf")]
    output = {"cases": cases, "mutations": mutations,
              "interpretation": "formal group algebra; nonzero private erasure remains assumed"}
    print(json.dumps(output, indent=2))
    print("PASS_JOINT_FULL_FIELD_SYNTAX")


if __name__ == "__main__":
    main()
