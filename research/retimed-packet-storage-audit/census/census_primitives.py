"""Check the one-extra-Field contract on the actual small physical methods."""
from fractions import Fraction
from pathlib import Path
from textwrap import dedent
import argparse
import inspect
import json
import sys


def need(ok, reason):
    if not ok:
        raise AssertionError(reason)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--runtime', type=Path, required=True)
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    sys.path.insert(0, str(args.runtime.resolve()))
    from upstream import install
    install()
    from spool import Arena, Field, cold_swap
    from compact_columns import Columns

    class ObservedArena(Arena):
        def __init__(self):
            super().__init__(3, 2)
            self.created = []
            self.peak = 0

        def field(self):
            result = super().field()
            self.created.append(result)
            self.peak = max(self.peak, self.live)
            return result

    arena = ObservedArena()
    x, y = arena.field(), arena.field()
    x.write([(0, 0)] * 8)
    y.write([(0, 0)] * 8)
    columns = Columns(1, 0, 1, 0, 0, 0, 0, cold_swap)
    methods = (
        ('copy-and-retire', lambda: x.copy().retire()),
        ('scale', lambda: x.scale(Fraction(1, 2025))),
        ('scale-add', lambda: x.scale_add(y, 2, 3)),
        ('self-scale-add', lambda: x.scale_add(x, 2, 3)),
        ('phase', lambda: x.phase(lambda address: address % 4)),
        ('rotate', lambda: x.rotate(0, 1, lambda _: 1)),
        ('swap', lambda: x.swap(0, 2, 1, cold_swap)),
        ('column-repair', lambda: columns.repair(x, lambda _: True, lambda a: a)),
    )
    checked = []
    try:
        for name, operation in methods:
            arena.peak = arena.live
            operation()
            need(arena.live == 2, 'physical method retained a replacement field')
            need(arena.peak == 3, 'physical method violated one-extra-Field bound')
            need(all(pair == (0, 0) for pair in x.values()), 'zero owner changed value')
            checked.append({'method': name, 'peak_extra': arena.peak - 2})
        original = Field.replace
        source = dedent(inspect.getsource(original))
        need(source.count('other.retire()') == 1, 'replacement control site differs')
        namespace = dict(original.__globals__)
        exec(compile(source.replace('other.retire()', 'pass'), '<omit-replace-retire>', 'exec'),
             namespace)
        Field.replace = namespace['replace']
        try:
            x.scale(1)
            need(arena.live == 3, 'replacement retirement mutation was not detected')
            control = 'retained an extra physical replacement slot'
        finally:
            Field.replace = original
    finally:
        for field in arena.created:
            if field.stream.slot is not None:
                field.retire()
        arena.close()
    result = {'status': 'passed', 'methods': checked,
              'source_mutation_rejected': {'omit-replace-retire': control},
              'scope': 'actual finite tapes and allocation methods; zero values receive no storage discount'}
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS_PHYSICAL_FIELD_CENSUS', len(checked))


if __name__ == '__main__':
    main()
