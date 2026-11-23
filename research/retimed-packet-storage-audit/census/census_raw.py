"""Count source raw-field lifetimes, abstracting only payload transformations."""
from collections import Counter
from fractions import Fraction
from pathlib import Path
from textwrap import dedent
from types import SimpleNamespace
import argparse
import inspect
import json
import sys


def need(ok, reason):
    if not ok:
        raise AssertionError(reason)


class Stock:
    def __init__(self, bound):
        self.live = self.peak = self.created = 0
        self.bound = bound
        self.methods = Counter()

    def field(self):
        self.live += 1
        self.created += 1
        self.peak = max(self.peak, self.live)
        need(self.live <= self.bound, 'per-context auxiliary field bound exceeded')
        return TokenField(self)


class TokenField:
    """One token per owned Field; a transform allocates its one replacement."""
    def __init__(self, stock):
        self.stock, self.live = stock, True

    def check(self):
        need(self.live, 'use of retired field')

    def blank(self):
        self.check()
        return self.stock.field()

    def clear(self):
        self.check()

    def copy(self):
        self.stock.methods['copy'] += 1
        return self.blank()

    def retire(self):
        self.check()
        self.live = False
        self.stock.live -= 1

    def replace(self, other):
        self.check(); other.check()
        need(self is not other and self.stock is other.stock, 'invalid replacement owner')
        other.retire()

    def transform(self, label):
        self.stock.methods[label] += 1
        self.replace(self.blank())

    def scale(self, *args):
        self.transform('scale')

    def scale_add(self, other, *args):
        other.check()
        self.transform('scale_add')


def artifacts():
    from upstream import HERE
    from strong_complex import load_changed, word, ODD
    from closed_caller import templates, placement
    from mixed_caller import instructions, layout_bindings
    import tagged_sources
    g, layout = load_changed(HERE / 'inputs')
    tagged = word(g, layout)
    caller = tagged_sources.packed(tagged_sources.pinned('data/CALLER.json.gz',
                                                       tagged_sources.PINS['data/CALLER.json.gz']))
    words, roots = templates(caller), placement(caller)
    binds, offsets, receipt = layout_bindings(words, roots, layout, 48)
    hosted = layout['hosted']
    pairs = dict(zip(hosted['Dports'], zip(hosted['X2'], hosted['Y2'], strict=True), strict=True))
    regs = [(x, x + 112) + pairs.get(i, ()) for i, x in enumerate(layout['live'])]
    dims = tuple(map(len, g['frames']))
    pair_ids = set(zip(g['initial'], g['final'], strict=True))
    pair_ids.update((a, b) for _, a, b in g['moves'])
    # Atlas matrices affect payload values, not retained field counts. The
    # source ranks and all graph, caller and binding instructions remain real.
    art = SimpleNamespace(graph=g, layout=layout, words=words, roots=roots,
        offsets=offsets, instructions=lambda: instructions(words, roots, binds, offsets),
        contacts=[((), ()) for _ in regs], port=[((), ()) for _ in regs],
        regs=regs, main={n for row in regs for n in row}, odd=ODD,
        factors={(a, b): (abs(dims[a] - dims[b]), (), ()) for a, b in pair_ids},
        moves={i: (a, b) for i, a, b in g['moves']},
        forms={i: tuple((j, Fraction(c)) for j, c in row) for i, row in g['forms']})
    need(len(tagged.targets) == 52608 and len(tagged.paid) == 281568,
         'changed raw source census')
    need(receipt['root_owners'] == 9840 and len(g['initial']) == 1291 and
         len(g['schedule']) == 6965, 'changed persistent owner census')
    return art, tagged, receipt


def run(mutation=False):
    from periodic import Job
    from raw48 import ComplexRaw
    from retimed_supplier import Raw, source_ranks
    art, tagged, receipt = artifacts()
    targets, paid = source_ranks(tagged)
    baseline, extra = len(targets), 9841
    stock = Stock(baseline + extra)
    fields = {i: stock.field() for i in range(baseline)}
    columns = 2
    ports = [Job(i, tuple(range(rank * columns))) for i, rank in enumerate(targets)]

    class RawCensus(ComplexRaw):
        def align(self, field, job, canonical):
            need(len(job.axes) == len(canonical), 'wrong alignment shape')
            field.transform('align_envelope')
            return ()

        def unalign(self, field, route):
            field.transform('unalign_envelope')

        def chart(self, field, tape, axes, cols, inverse=False):
            field.transform('chart_envelope')

        def head_flip(self, field, cols):
            field.transform('head_flip_envelope')

        def raw(self, productive, cols):
            for tag, job in super().raw(productive, cols):
                self.raw_serial += 1
                self.original = job
                yield tag, job

    physical = RawCensus(art, fields, SimpleNamespace(window=1, offset=0),
                         low=0, bundle=1, slots=4096)
    physical.raw_serial = 0
    adapter = Raw(tagged, physical)
    original_graph = ComplexRaw.graph
    if mutation:
        source = dedent(inspect.getsource(original_graph))
        old = 'for field in held.values():\n        field.retire()'
        need(source.count(old) == 1, 'graph retirement mutation is not unique')
        namespace = dict(original_graph.__globals__)
        exec(compile(source.replace(old, 'for field in held.values():\n        pass'),
                     '<omit-graph-retire>', 'exec'), namespace)
        ComplexRaw.graph = namespace['graph']
    try:
        seen = 0
        cuts = Counter()
        previous = None
        halves = []
        split_pairs = 0
        peak_yield = 0

        def finish():
            nonlocal split_pairs
            if not halves:
                return
            need(len(halves) in (1, 2), 'more than two cuts share a raw loan')
            need(tuple(axis for job in halves for axis in job.axes) == original.axes,
                 'split lost, duplicated or reordered axes')
            need(all(job.owner == original.owner for job in halves), 'split changed owner')
            split_pairs += len(halves) == 2

        for grade, job in zip(paid, adapter.native(ports, columns), strict=True):
            need(len(job.axes) == grade * columns, 'adapted loan has wrong size')
            fields[job.owner].check()
            serial = physical.raw_serial
            if serial != previous:
                finish()
                original = physical.original
                halves = []
                previous = serial
            halves.append(job)
            cuts[serial] += 1
            peak_yield = max(peak_yield, stock.live - baseline)
            seen += 1
        finish()
        need(seen == 564144 and split_pairs == 1008, 'wrong adapted chronology')
        need(stock.live == baseline and set(fields) == set(range(baseline)),
             'raw return retained an auxiliary field')
        need(all(field.live for field in fields.values()), 'raw return retired an input')
        return {'status': 'passed', 'source_targets': baseline, 'adapted_paid': seen,
                'original_raw_paid': physical.raw_serial, 'half_column_pairs': split_pairs,
                'max_extra_fields': stock.peak - baseline, 'max_extra_at_yield': peak_yield,
                'returned_fields': stock.live, 'field_allocations': stock.created,
                'primitive_counts': dict(stock.methods), 'binding_receipt': receipt,
                'scope': 'actual raw/scheduler labels and field lifetime skeleton; '
                         'payload transforms replaced by a one-replacement-field envelope'}
    finally:
        ComplexRaw.graph = original_graph


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--runtime', type=Path, required=True)
    cli.add_argument('--output', type=Path, required=True)
    cli.add_argument('--mutation', action='store_true')
    args = cli.parse_args()
    sys.path.insert(0, str(args.runtime.resolve()))
    from upstream import install
    install()
    if args.mutation:
        try:
            run(True)
        except AssertionError as error:
            need(str(error) == 'per-context auxiliary field bound exceeded',
                 'retirement mutation failed for an unexpected reason')
            result = {'status': 'rejected', 'mutation': 'omit-graph-retire', 'reason': str(error)}
        else:
            raise AssertionError('graph retirement mutation survived')
    else:
        result = run()
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS_RAW_OWNER_CENSUS', result.get('max_extra_fields', result['status']))


if __name__ == '__main__':
    main()
