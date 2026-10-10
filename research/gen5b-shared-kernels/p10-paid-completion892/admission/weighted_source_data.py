from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import support
support.require_assertions()
from functools import lru_cache
import json, gzip
PACKAGE_ROOT = Path(__file__).resolve().parent
PACKAGE_OUTPUT = support.ADM
OUTPUT = PACKAGE_OUTPUT
SOURCE = support.INPUTS
HEAD = support.HEAD
pins = support.pins
read_bytes = support.read_bytes
verify = support.verify_inputs
def read(name):
    name = {'graph.json': 'bitword/selected/bit/graph_p10.json', 'frames.json': 'bitword/selected/bit/frames_p10.json.gz', 'kchron.json': 'bitword/selected/bit/kchron_p10.json'}.get(name, name)
    raw = read_bytes(name)
    return json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)
