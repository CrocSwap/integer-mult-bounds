"""Install one chronological epoch and replay it on every actual owner group."""

from itertools import count
from tempfile import TemporaryFile

from periodic import row_axes

OPEN, ISSUE, CLOSE, FINISH = range(4)
EXTERNAL, LOAN = range(2)


def epoch(rule, plan):
    """Emit frame and loan numbers. Keep placement relative to the current round."""
    band = plan.forest
    ids = count()

    def layer(path, previous):
        frames, consumed = [], {}
        for unit in band.layers.get(path, ()):
            group = []
            for copy in range(plan.copies):
                frame = next(ids)
                operation = [OPEN, frame, unit.columns]
                for i, (kind, label) in enumerate(unit.ports):
                    size = rule.targets[i] * unit.columns
                    if kind == "parent":
                        operation.extend((LOAN, previous[label][copy], size))
                        consumed[label] = size
                    else:
                        base = copy * plan.owners_per_copy + plan.offsets[label]
                        operation.extend((EXTERNAL, base, size, plan.periods[label]))
                yield tuple(operation)
                group.append(frame)
            frames.append((unit, group))
        for j, paid in enumerate(rule.paid):
            child = path + (j,)
            requests = {}
            for unit, group in frames:
                loans = []
                for frame in group:
                    loan = next(ids)
                    yield (ISSUE, frame, loan, paid * unit.columns)
                    loans.append(loan)
                requests[unit.future] = loans
            if requests or child in band.prefixes:
                yield layer(child, requests)
        for _, group in frames:
            for frame in group:
                yield (CLOSE, frame)
        for label, loans in previous.items():
            for loan in loans:
                yield (FINISH, loan, consumed.get(label, 0))

    stack = [layer((), {})]
    while stack:
        entry = next(stack[-1], None)
        if entry is None:
            stack.pop()
        elif isinstance(entry, tuple):
            yield entry
        else:
            stack.append(entry)


def put_nat(stream, value):
    while value >= 128:
        stream.write(bytes((128 | (value & 127),)))
        value >>= 7
    stream.write(bytes((value,)))


def get_nat(stream):
    value = shift = 0
    while True:
        octet = stream.read(1)
        if not octet:
            raise EOFError("The installed instruction ended inside an integer")
        b = octet[0]
        value |= (b & 127) << shift
        if b < 128:
            return value
        shift += 7


class Image:
    def __init__(self, rule, plan):
        self.stream = TemporaryFile()
        self.records = 0
        for row in epoch(rule, plan):
            put_nat(self.stream, len(row))
            for value in row:
                put_nat(self.stream, value)
            self.records += 1
        self.size = self.stream.tell()

    def rows(self):
        # A recursive invocation can use the same tape head while a loan is open.
        offset = 0
        while offset < self.size:
            self.stream.seek(offset)
            row = tuple(get_nat(self.stream) for _ in range(get_nat(self.stream)))
            offset = self.stream.tell()
            yield row


class Compiler:
    """Keep one generated plan and one installed stream per fixed carrier rank."""

    def __init__(self, rule, floor):
        from band_compiler import make_planner

        self.rule = rule
        self.plan = make_planner(rule, floor)
        self.images = {}

    def __call__(self, rank):
        return self.plan(rank)

    def image(self, rank):
        if rank not in self.images:
            self.images[rank] = Image(self.rule, self.plan(rank))
        return self.images[rank]


def run(rule, n, fields, machine, *, planner):
    plan = planner(n)
    public = tuple(fields)
    if (
        len(public) != plan.width
        or len({job.owner for job in public}) != plan.width
        or any(len(job.axes) != n for job in public)
    ):
        raise ValueError("The carrier needs independent full input fields")

    def finish(job, first):
        for i in range(first, len(job.axes)):
            machine.leaf(job.select((i,)))

    if plan.forest is None:
        for job in public:
            finish(job, 0)
        return
    code = planner.image(n)
    fields = list(public)
    for _ in range(plan.copies * plan.owners_per_copy - plan.width):
        fields.append(machine.zero(public[0]))
    frames, loans = {}, {}
    end = object()
    for iteration in range(plan.rounds):
        for row in code.rows():
            op, key, *args = row
            if op == OPEN:
                columns, *descriptors = args
                entries = iter(descriptors)
                ports = []
                for kind in entries:
                    index, size = next(entries), next(entries)
                    if kind == LOAN:
                        job = loans[index].select(range(size))
                    else:
                        q = next(entries)
                        job = fields[index + iteration // q].select(
                            row_axes(plan.active, size, q, iteration % q)
                        )
                    ports.append(job)
                frames[key] = iter(machine.native(tuple(ports), columns))
            elif op == ISSUE:
                loan, size = args
                job = next(frames[key])
                if len(job.axes) != size:
                    raise ValueError("A native cut issued the wrong rank")
                loans[loan] = job
            elif op == CLOSE:
                if next(frames.pop(key), end) is not end:
                    raise ValueError("A native cut remained after the final return")
            elif op == FINISH:
                finish(loans.pop(key), args[0])
            else:
                raise ValueError("The installed instruction is unknown")
        if frames or loans:
            raise ArithmeticError("The epoch left an open frame or loan")
    for job in public:
        finish(job, plan.active)
    for job in reversed(fields[len(public) :]):
        machine.retire_zero(job)
