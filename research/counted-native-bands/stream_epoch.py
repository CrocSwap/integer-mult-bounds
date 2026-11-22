"""Issue the native calls in order. Store the current continuations and their actual loans."""

from functools import cache
from itertools import count

from counted_band import census, period
from epoch_tape import OPEN, ISSUE, CLOSE, FINISH, EXTERNAL, LOAN


def futures(length, ranks):
    """Count ordered labels with one cursor per digit. Do not copy the alphabet."""
    if length == 0:
        yield (), 1
        return
    stack = [enumerate(ranks())]
    labels, products = [], [1]
    while stack:
        item = next(stack[-1], None)
        if item is None:
            stack.pop()
            if stack:
                labels.pop()
                products.pop()
            continue
        index, rank = item
        if len(stack) == length:
            yield (*labels, index), products[-1] * rank
        else:
            labels.append(index)
            products.append(products[-1] * rank)
            stack.append(enumerate(ranks()))


def rows(rule, plan):
    band = plan.forest
    if band is None:
        return
    ids = count()
    offset = 0

    def layer(depth, prefix, last, incoming):
        nonlocal offset
        frames, consumed = [], {}
        if 0 < depth < band.height:
            for future, rest in futures(band.height - depth, rule.target_ranks):
                x = prefix * rest
                if x < band.floor * band.denominator or rule.ambient * x > band.limit * band.denominator:
                    continue
                columns = x // band.denominator - 1
                ports = []
                for i, k in enumerate(rule.target_ranks()):
                    size = k * columns
                    if rule.ambient * x * k > band.limit * band.denominator * last:
                        q = period(plan.active, size)
                        ports.append((EXTERNAL, offset, size, q))
                        offset += plan.rounds // q
                    else:
                        label = (i,) + future
                        ports.append((LOAN, incoming[label], size))
                        consumed[label] = size
                group = []
                for replica in range(plan.copies):
                    frame = next(ids)
                    operation = [OPEN, frame, columns]
                    for kind, loc, size, *extra in ports:
                        if kind == EXTERNAL:
                            operation.extend((kind, replica * plan.owners_per_copy + loc, size, *extra))
                        else:
                            operation.extend((kind, loc[replica], size))
                    yield tuple(operation)
                    group.append(frame)
                frames.append((future, columns, group))
        if depth < band.height:
            for paid in rule.paid_ranks():
                requests = {}
                for future, columns, group in frames:
                    loans = []
                    for frame in group:
                        loan = next(ids)
                        yield (ISSUE, frame, loan, paid * columns)
                        loans.append(loan)
                    requests[future] = loans
                if requests or depth + 1 < band.height:
                    yield layer(depth + 1, prefix * paid, paid, requests)
        for _, _, group in frames:
            for frame in group:
                yield (CLOSE, frame)
        for label, loans in incoming.items():
            for loan in loans:
                yield (FINISH, loan, consumed.get(label, 0))

    stack = [layer(0, 1, 1, {})]
    while stack:
        operation = next(stack[-1], None)
        if operation is None:
            stack.pop()
        elif isinstance(operation, tuple):
            yield operation
        else:
            stack.append(operation)
    if offset != plan.owners_per_copy:
        raise ArithmeticError("The labelled stream and the rank census disagree")


class Program:
    def __init__(self, rule, plan):
        self.rule, self.plan = rule, plan

    def rows(self):
        return rows(self.rule, self.plan)


class Compiler:
    def __init__(self, rule, floor):
        self.rule, self.floor = rule, floor

    @cache
    def __call__(self, rank):
        return census(self.rule, rank, self.floor)

    def image(self, rank):
        return Program(self.rule, self(rank))
