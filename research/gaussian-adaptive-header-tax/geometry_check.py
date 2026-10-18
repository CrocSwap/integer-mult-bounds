"""Run the unchanged geometric premise with assertions enabled."""
import importlib.util
import json
from pathlib import Path
import sys

if not __debug__:
    raise RuntimeError('geometry premise requires assertions')
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'research/gaussian-clique-copy-bound'
spec = importlib.util.spec_from_file_location('geometry', SOURCE / 'geometry.py')
geometry = importlib.util.module_from_spec(spec)
sys.modules['geometry'] = geometry
spec.loader.exec_module(geometry)
spec = importlib.util.spec_from_file_location('gaussian_retained', SOURCE / 'verify.py')
retained = importlib.util.module_from_spec(spec)
spec.loader.exec_module(retained)
receipt = retained.calculate()
if receipt != json.loads((SOURCE / 'certificate.json').read_text()):
    raise RuntimeError('retained geometry receipt differs')
lines = geometry.gaussian_lines()
graph = geometry.nonorthogonality(lines)
cliques = geometry.maximal_cliques(graph)
print(json.dumps({'receipt': receipt, 'lines': lines, 'graph': graph, 'cliques': cliques}))
