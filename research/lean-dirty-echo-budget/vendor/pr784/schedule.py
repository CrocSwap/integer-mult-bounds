"""Minimum uniform leaf-call counts in the ordered dirty-echo tree grammar."""

from __future__ import annotations

from dataclasses import dataclass, field


def need(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Plan:
    children: tuple[Plan, ...] = ()
    factors: int = field(init=False)
    calls: int = field(init=False)
    scratch: int = field(init=False)

    def __post_init__(self):
        need(isinstance(self.children, tuple), "children must be a tuple")
        need(not self.children or len(self.children) >= 2, "internal nodes need two or more children")
        need(all(isinstance(child, Plan) for child in self.children), "invalid child plan")
        if self.children:
            factors = sum(child.factors for child in self.children)
            calls = sum(
                (2 if i in (0, len(self.children) - 1) else 4) * child.calls
                for i, child in enumerate(self.children)
            )
            scratch = len(self.children) - 1 + max(child.scratch for child in self.children)
        else:
            factors, calls, scratch = 1, 1, 0
        object.__setattr__(self, "factors", factors)
        object.__setattr__(self, "calls", calls)
        object.__setattr__(self, "scratch", scratch)


def plan_table(max_factors, max_scratch):
    """Return table[budget][factor_count]; None means no tree fits the budget.

    All positive contiguous partitions and all arities allowed by the budget
    are considered. Min-plus convolution avoids enumerating their products.
    """
    need(type(max_factors) is int and max_factors >= 1, "positive integer factor count required")
    need(type(max_scratch) is int and max_scratch >= 0, "nonnegative integer scratch budget required")
    table = []
    for budget in range(max_scratch + 1):
        row = table[-1][:] if table else [None] * (max_factors + 1)
        row[1] = Plan()
        for arity in range(2, min(max_factors, budget + 1) + 1):
            child_row = table[budget - arity + 1]
            prefixes = [None] * (max_factors + 1)
            prefixes[0] = (0, ())
            for position in range(arity):
                weight = 2 if position in (0, arity - 1) else 4
                remaining = arity - position - 1
                extended = [None] * (max_factors + 1)
                for used, prefix in enumerate(prefixes):
                    if prefix is None:
                        continue
                    for size in range(1, max_factors - remaining - used + 1):
                        child = child_row[size]
                        if child is None:
                            continue
                        cost = prefix[0] + weight * child.calls
                        total = used + size
                        if extended[total] is None or cost < extended[total][0]:
                            extended[total] = (cost, (*prefix[1], child))
                prefixes = extended
            for count, candidate in enumerate(prefixes):
                if candidate is not None and (row[count] is None or candidate[0] < row[count].calls):
                    row[count] = Plan(candidate[1])
        table.append(row)
    return table


def optimal_plan(factors, scratch_budget):
    """Minimize uniform leaf calls under the given simultaneous array budget."""
    need(type(factors) is int and factors >= 1, "positive integer factor count required")
    need(type(scratch_budget) is int and scratch_budget >= 0, "nonnegative integer scratch budget required")
    need((factors - 1).bit_length() <= scratch_budget, "no echo tree fits the scratch budget")
    return plan_table(factors, min(scratch_budget, factors - 1))[-1][factors]


def word(plan, sign=1):
    """Yield (factor, source, target, sign), with source 0 and target 1.

    Array indices 2 onward are arbitrary caller-supplied dirt. An inverse call
    reverses the full word, including the instruction order within children.
    """
    need(isinstance(plan, Plan), "invalid plan")
    need(type(sign) is int and sign in (-1, 1), "sign must be +1 or -1")

    def inverse(commands):
        return [(child, first, src, dst, -direction) for child, first, src, dst, direction in reversed(commands)]

    def emit(node, first, source, target, scratch_first, direction):
        if not node.children:
            yield first, source, target, direction
            return
        chain = []
        offset = first
        for i, child in enumerate(node.children[:-1]):
            src = source if i == 0 else scratch_first + i - 1
            chain.append((child, offset, src, scratch_first + i, 1))
            offset += child.factors
        last = (node.children[-1], offset, scratch_first + len(chain) - 1, target, 1)
        # Both dirty ladders and their inverses are required by PR673's echo.
        commands = chain + [last] + inverse(chain) + chain[1:] + inverse([last]) + inverse(chain[1:])
        if direction == -1:
            commands = inverse(commands)
        for child, start, src, dst, child_sign in commands:
            yield from emit(child, start, src, dst, scratch_first + len(chain), child_sign)

    yield from emit(plan, 0, 0, 1, 2, sign)


def compose(plan, source, target, scratch, leaf, sign=1, readonly=()):
    """Execute a plan through leaf(source, target, factor_index, sign).

    Each leaf must restore its source, be independent of its target, and have
    an exact subtracting inverse. Its external inputs must remain fixed.
    Declared read-only arrays are checked for identity aliases before mutation.
    """
    need(isinstance(plan, Plan), "invalid plan")
    need(type(sign) is int and sign in (-1, 1), "sign must be +1 or -1")
    need(callable(leaf), "leaf must be callable")
    need(len(scratch) >= plan.scratch, "insufficient dirty arrays")
    arrays = [source, target, *scratch]
    need(all(isinstance(array, list) for array in arrays), "mutable arrays must be lists")
    need(len({id(array) for array in arrays}) == len(arrays), "mutable arrays must be distinct")
    need(not any(value is array for value in readonly for array in arrays), "read-only array aliases mutable data")
    need(len(source) > 0 and all(len(array) == len(source) for array in arrays), "equal positive array lengths required")
    for factor, src, dst, direction in word(plan, sign):
        leaf(arrays[src], arrays[dst], factor, direction)


def multiplicities(plan):
    """Return each factor's total calls, including restoration calls."""
    counts = []

    def visit(node, weight):
        if not node.children:
            counts.append(weight)
        else:
            for i, child in enumerate(node.children):
                visit(child, weight * (2 if i in (0, len(node.children) - 1) else 4))

    visit(plan, 1)
    return counts
