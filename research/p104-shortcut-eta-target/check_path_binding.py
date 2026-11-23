#!/usr/bin/env python3
"""Bind candidate producer, both native types and actual raw executor to the shortcut graph."""
from argparse import ArgumentParser
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import gzip
import inspect
import json
import sys

ap = ArgumentParser()
ap.add_argument('runtime', type=Path)
ap.add_argument('--output', type=Path, required=True)
args = ap.parse_args()
runtime = args.runtime.resolve()
started = datetime.now(timezone.utc)
sys.path.insert(0, str(runtime))
import strong_complex
from strong_complex import digest
from installations import ENTRY, TERMINAL
from grades import numerical_source, numerical_recipe
from band_product import Product, production_supplier
from retimed_supplier import Positive
from raw48 import ComplexRaw
from clock_ports import clock_word

atlas, word, targets, paid, cells = numerical_source()
expected = 'ed3bea7186f962f3a8a8ae389cecce3d1ef48a7a832cf9af6c9048a6b5919b35'
assert digest(atlas.graph) == expected
assert len(atlas.graph['moves']) == 5669 and len(atlas.moves) == 5669
assert atlas.moves == {k: (a, b) for k, a, b in atlas.graph['moves']}
assert len(word.targets) == 52608 and len(word.paid) == 281328
assert (len(numerical_recipe(1024).types()[0].paid), len(numerical_recipe(1024).types()[1].paid)) == (282336, 281328)
for profile in (ENTRY, TERMINAL):
    supplier = production_supplier(profile.complex_log, profile.positive_stop_denominator)
    recipe = numerical_recipe(profile.complex_log)
    assert supplier.physical is atlas and supplier.word is word and supplier.recipe is recipe
    assert recipe.targets is targets and recipe.paid is paid and recipe.cells is cells
    assert ComplexRaw(atlas, {}, None, low=0, bundle=1, slots=306).art is atlas

returns = [(prefix, entries) for prefix, entries in word.paid.segments if prefix and prefix[0] == 'return']
assert len(returns) == 48
ordered = tuple(k for k in atlas.graph['schedule'] if k in atlas.moves)
assert len(ordered) == 5669
new_nodes = {104489, 104490, 104491, 104492, 104493}
old_nodes = {95050, 95056, 95398, 95425, 96741, 96743, 97628, 99468, 100531, 101275}
for _, entries in returns:
    ids = tuple(node for node, rank in entries)
    assert ids == ordered and new_nodes.issubset(ids) and not old_nodes.intersection(ids)

source = inspect.getsource(ComplexRaw.graph)
assert all(fragment in source for fragment in ('g = a.graph', 'for node in g["schedule"]', 'a.forms[node]', 'node in a.moves'))
assert 'production_supplier' in inspect.getsource(Product.h)
assert 'numerical_source()' in inspect.getsource(Positive.__init__)
assert 'self.physical' in inspect.getsource(Positive._run)

# A valid compressed graph with one changed move must fail the installed
# content digest before it can be substituted into an atlas.
mutant = dict(atlas.graph)
mutant['moves'] = [list(row) for row in atlas.graph['moves']]
mutant['moves'][0][1] += 1
damaged = gzip.compress(json.dumps(mutant, separators=(',', ':'), sort_keys=True).encode())
word_path = runtime / 'w5669_shortcut5.json.gz'
original_read = Path.read_bytes

def patched_read(path):
    if path == word_path:
        return damaged
    return original_read(path)

strong_complex.load_changed.cache_clear()
with patch.object(Path, 'read_bytes', patched_read):
    try:
        strong_complex.load_changed(runtime / 'inputs')
        raise AssertionError('Damaged shortcut graph was accepted')
    except ValueError as exc:
        assert 'shortcut Gaussian graph differs' in str(exc)
strong_complex.load_changed.cache_clear()
assert digest(strong_complex.load_changed(runtime / 'inputs')[0]) == expected

# An explicit in-memory old-word fallback would yield a different paid stream
# and is rejected by the target digest and label checks.
from sparse_helpers import rebuild
from verify_split_helpers import read, reconstruct
parent, _ = rebuild()
old, _ = reconstruct(parent, read('BANK-FACTORS.json.gz'))
fake = SimpleNamespace(**vars(atlas))
fake.graph = old
fake.moves = {k: (a, b) for k, a, b in old['moves']}
old_word = clock_word(fake)
assert digest(old) != expected and len(old_word.paid) == 281568 and len(old_word.paid) != len(word.paid)

report = {'started_at': started.isoformat(), 'finished_at': datetime.now(timezone.utc).isoformat(),
          'graph_sha256': expected, 'old_graph_sha256': digest(old), 'native_calls': len(returns),
          'moves_per_native_call': len(ordered), 'productive_labels': len(word.targets),
          'paid_labels': len(word.paid), 'old_paid_labels': len(old_word.paid),
          'typed_paid_labels': [282336, 281328], 'entry_gaussian_height': ENTRY.complex_log,
          'terminal_gaussian_height': TERMINAL.complex_log,
          'altered_shortcut_digest_rejected': True, 'old_word_fallback_distinguished': True,
          'source_sha256': {name: sha256((runtime / name).read_bytes()).hexdigest() for name in
                            ('strong_complex.py', 'w5669_shortcut5.json.gz', 'grades.py', 'typed_raw.py', 'retimed_supplier.py', 'band_product.py')},
          'scope': 'Loader, graph, label and executor binding; finite product path is separately instrumented.'}
out = args.output.resolve()
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2) + '\n')
print('PASS_SHORTCUT_PATH_BINDING', json.dumps(report, sort_keys=True), flush=True)
