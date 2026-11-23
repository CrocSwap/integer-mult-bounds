"""Independently read literal production grade and constructor bindings."""

from __future__ import annotations

import ast
import gc
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import sys
import types
from tempfile import TemporaryDirectory


HERE = Path(__file__).resolve().parent
RUNTIME = Path('/workspace/scratch/5b0914ccc34e/work-storage/runtime-exact')
STOCK = Path('/workspace/scratch/5b0914ccc34e/work-storage/wave2-stock')


def main():
    sys.path.insert(0, str(RUNTIME))
    from upstream import install
    held = install()
    import strong_complex
    import tagged_sources
    from installations import BINARY_C, GAUSSIAN_C
    from strong_binary import graph, caller

    g = json.loads((STOCK / 'graph.json').read_bytes())
    layout = json.loads((STOCK / 'layout.json').read_bytes())
    assert strong_complex.digest(g) == strong_complex.WORD
    assert strong_complex.digest(layout) == strong_complex.LAYOUT
    raw = strong_complex.word(g, layout)
    namespace = {'F': F, 'SCALES': (1, 8), 'SMALL_SPLITS': 1008}
    source = (RUNTIME / 'retimed_supplier.py').read_text()
    node = next(n for n in ast.parse(source).body
                if isinstance(n, ast.FunctionDef) and n.name == 'source_ranks')
    exec(compile(ast.Module(body=[node], type_ignores=[]),
                 '<source_ranks>', 'exec'), namespace)
    targets, paid = namespace['source_ranks'](raw)
    bit = tagged_sources.binary_ports(graph(), caller())

    rows = {
        'gaussian': {
            'ambient': 8 * raw.ambient,
            'target_max': max(targets),
            'paid_min': str(min(paid)),
            'targets': len(targets),
            'paid': len(paid),
            'd': (1 - GAUSSIAN_C).denominator.bit_length() - 1,
            't': str(1 - GAUSSIAN_C),
        },
        'binary': {
            'ambient': bit.ambient,
            'target_max': max(p.rank for p in bit.targets),
            'paid_min': str(min(p.rank for p in bit.paid)),
            'targets': len(bit.targets),
            'paid': len(bit.paid),
            'd': (1 - BINARY_C).denominator.bit_length() - 1,
            't': str(1 - BINARY_C),
        },
        'source_hashes': {
            name: sha256((RUNTIME / name).read_bytes()).hexdigest()
            for name in ('transport.py', 'installations.py', 'retimed_supplier.py',
                         'raw_binary_stage.py', 'strong_complex.py', 'strong_binary.py')
        },
        'graph_sha256': strong_complex.digest(g),
        'layout_sha256': strong_complex.digest(layout),
        'tagged_sources_sha256': sha256(Path(tagged_sources.__file__).read_bytes()).hexdigest(),
        'held_source_layers': len(held),
    }
    for item in ('gaussian', 'binary'):
        assert rows[item]['target_max'] <= 1032
        assert F(rows[item]['paid_min']) >= F(1, 2)
        assert rows[item]['d'] <= 60
        assert F(rows[item]['t']) >= F(1, 2)
        assert rows[item]['ambient'] >= 1

    transport_source = (RUNTIME / 'transport.py').read_text()
    module = types.ModuleType('review_transport_binding')
    sys.modules[module.__name__] = module
    exec(compile(transport_source, '<literal transport.py>', 'exec'), module.__dict__)
    module.Plan = lambda *args, **kwargs: (args, kwargs)
    constructors = {}
    literal_plan = next(n for n in ast.parse(transport_source).body
                        if isinstance(n, ast.ClassDef) and n.name == 'Plan')
    measure_call = next(n.value for n in ast.walk(literal_plan)
                        if isinstance(n, ast.Assign)
                        and any(isinstance(v, ast.Name) and v.id == 'measure' for v in n.targets))
    for name, ambient, target_list, paid_list, trial in (
        ('gaussian', 8 * raw.ambient, targets, paid, GAUSSIAN_C),
        ('binary', bit.ambient, tuple(p.rank for p in bit.targets),
         tuple(p.rank for p in bit.paid), BINARY_C),
    ):
        recipe = module.Recipe(1024, ambient, target_list, paid_list, {}, trial)
        args, kwargs = recipe.open()
        n, tt, lower, upper, volume = args[0], args[4], args[5], args[6], args[7]
        assert n == 1 << 1024
        assert args[1] is target_list and args[2] is paid_list
        assert tt == 1 - trial and volume == n ** 6
        assert lower == 2 ** 15 and lower < upper <= n
        assert upper == 2 * (n // (2048 * ambient))
        assert kwargs['width'] == 1 << (92 * 1024)
        actual_measure = eval(compile(ast.Expression(measure_call), '<Plan measure binding>', 'eval'),
                              {'Measure': lambda *items: items, 'max': max},
                              {'n': n, 't': tt, 'volume': volume})
        assert actual_measure == (tt, volume, max(256, 64 * n.bit_length()))
        p = actual_measure[2]
        assert (1 << p) > n ** 64
        constructors[name] = {
            'rank_log': 1024, 'lower': lower, 'upper_le_n': True,
            'volume_is_n_to_six': True, 'precision': p,
            'grid_gt_n_to_64': True, 'max_nonempty_endpoint_le_2064n': True,
            'method': 'literal Recipe.open with Plan capture; literal Plan Measure expression',
        }
    rows['constructor_binding'] = constructors
    for item in held:
        if hasattr(item, 'cleanup'):
            item.cleanup()
    # The retained grade loader owns a second cached temporary directory.
    # This process creates no caller-owned directories; clean its loader
    # objects explicitly so strict warning replay also closes them cleanly.
    for item in gc.get_objects():
        if isinstance(item, TemporaryDirectory):
            item.cleanup()
    (HERE / 'PRODUCTION-BINDING.json').write_text(json.dumps(rows, indent=2) + '\n')
    print(json.dumps(rows, indent=2))


if __name__ == '__main__':
    main()
