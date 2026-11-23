"""Exercise the actual calendar/decoder with explicit owner-custody tokens."""
from fractions import Fraction as F
from math import ceil
from pathlib import Path
from textwrap import dedent
import argparse
import inspect
import json
import sys


def need(ok, reason):
    if not ok:
        raise AssertionError(reason)


class Machine:
    def __init__(self, width, n, Job):
        self.Job = Job
        self.next_owner = width
        self.custody = dict.fromkeys(range(width))
        self.rows = [Job(i, tuple(range(n))) for i in range(width)]
        self.baseline = width
        self.peak = width
        self.zeros = set()
        self.contexts = set()
        self.context_serial = self.max_contexts = self.leaves = self.created_zeros = 0

    def allocate(self):
        owner = self.next_owner
        self.next_owner += 1
        self.custody[owner] = None
        self.peak = max(self.peak, len(self.custody))
        return owner

    def zero(self, exemplar):
        owner = self.allocate()
        self.zeros.add(owner)
        self.created_zeros += 1
        return self.Job(owner, exemplar.axes)

    def retire_zero(self, job):
        need(job.owner in self.zeros and self.custody[job.owner] is None,
             'zero retired before its raw context returned')
        self.zeros.remove(job.owner)
        self.custody.pop(job.owner)

    def native(self, ports, columns):
        self.context_serial += 1
        context = self.context_serial
        self.contexts.add(context)
        self.max_contexts = max(self.max_contexts, len(self.contexts))
        owners = [job.owner for job in ports]
        need(len(set(owners)) == len(owners), 'aliased productive owners')
        for owner in owners:
            need(self.custody[owner] is None, 'productive field already in another context')
            self.custody[owner] = context
        # One private borrowed field is retained across both half-column cuts.
        borrowed = self.allocate()
        self.custody[borrowed] = context
        for axes in (range(columns // 2), range(columns // 2, columns)):
            self.custody[borrowed] = None
            yield self.Job(borrowed, tuple(axes))
            need(self.custody[borrowed] is None, 'parent advanced while a child kept its owner')
            self.custody[borrowed] = context
        self.custody.pop(borrowed)
        for owner in owners:
            need(self.custody[owner] == context, 'native lost an input custody token')
            self.custody[owner] = None
        self.contexts.remove(context)

    def leaf(self, job):
        need(job.owner in self.custody and self.custody[job.owner] is None,
             'paid leaf used an unavailable owner')
        self.leaves += 1


def execute(plan, round_no, group):
    from periodic import Job
    machine = Machine(plan.width, plan.n, Job)
    exact_cover = sum(plan.count[e] * (len(plan.paid) * plan.delay[e] + 1)
                      for e in plan.bands)
    plan.decode(machine.rows, round_no, group, machine, plan.events())
    need(not machine.contexts, 'raw context survived epoch return')
    need(not machine.zeros and len(machine.custody) == plan.width,
         'zero owner survived epoch return')
    need(all(owner is None for owner in machine.custody.values()), 'custody not returned')
    need(machine.peak - plan.width <= 2 * exact_cover,
         'source lifetime cover failed for zero plus raw field')
    return {'round': round_no, 'group': group, 'zero_owners_created': machine.created_zeros,
            'maximum_live_contexts': machine.max_contexts, 'exact_lifetime_cover': exact_cover,
            'peak_extra_fields': machine.peak - plan.width, 'singleton_leaves': machine.leaves}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--runtime', type=Path, required=True)
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    sys.path.insert(0, str(args.runtime.resolve()))
    from upstream import install
    install()
    from transport import Plan
    plan = Plan(512, (2,), (F(1, 2), F(1, 2)), {(F(1, 2), 2): F(1)},
                F(1, 2), 10, 50, 512, 3, 128, delay_base=2, padding=1)
    last_group = ceil(F(plan.width, plan.source_width)) - 1
    cases = [execute(plan, r, g) for r in (0, 127) for g in sorted({0, last_group})]
    original = Plan.decode
    source = dedent(inspect.getsource(original))
    old = 'machine.retire_zero(job)'
    need(source.count(old) == 1, 'zero retirement mutation has no unique source site')
    namespace = dict(original.__globals__)
    exec(compile(source.replace(old, 'pass'), '<omit-zero-retire>', 'exec'), namespace)
    Plan.decode = namespace['decode']
    try:
        try:
            execute(plan, 127, last_group)
        except AssertionError as error:
            need(str(error) == 'zero owner survived epoch return', 'wrong zero control failure')
            zero_failure = str(error)
        else:
            raise AssertionError('zero retirement mutation survived')
    finally:
        Plan.decode = original
    delays = plan.delay.copy()
    plan.delay = {e: 1 for e in plan.bands}
    try:
        try:
            execute(plan, 0, 0)
        except (AssertionError, ArithmeticError) as error:
            delay_failure = str(error)
        else:
            raise AssertionError('equal-delay mutation survived')
    finally:
        plan.delay = delays
    result = {'status': 'passed', 'width': plan.width, 'source_width': plan.source_width,
              'counts': plan.count, 'delays': plan.delay, 'cases': cases,
              'source_mutations_rejected': {'omit-zero-retire': zero_failure,
                                            'equal-delay-table': delay_failure},
              'scope': 'actual Plan calendar/decoder, small parameters and custody backend; '
                       'full raw-field lifetime skeleton checked separately'}
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS_SCHEDULE_OWNER_CENSUS', plan.width, delay_failure)


if __name__ == '__main__':
    main()
