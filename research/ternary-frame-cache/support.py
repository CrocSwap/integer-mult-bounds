"""Source admission and exact edge transcripts for the optional checker.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import inspect
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      allow_nan=False).encode('ascii')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def verify_sources(root=ROOT):
    need(not sys.flags.optimize, 'Assertions must remain enabled')
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for relative, expected in pins['files'].items():
        actual = hashlib.sha256((root / relative).read_bytes()).hexdigest()
        need(actual == expected, 'Pinned source changed: ' + relative)
    return pins


def verify_loaded_sources():
    pins = verify_sources()
    for module in tuple(sys.modules.values()):
        filename = getattr(module, '__file__', None)
        if filename is None:
            continue
        path = Path(filename).resolve()
        if path.is_relative_to(ROOT / 'scripts') and path.suffix == '.py':
            need(path.relative_to(ROOT).as_posix() in pins['files'],
                 'Unpinned imported source: ' + str(path))


class Trace:
    """Record every visited edge, with full exact matrices rather than hashes."""
    def __init__(self):
        self.matrices = []
        self.indices = {}
        self.edges = []

    def index(self, matrix):
        if matrix not in self.indices:
            self.indices[matrix] = len(self.matrices)
            self.matrices.append(matrix)
        return self.indices[matrix]

    def __call__(self, reverse, slot, old, new, rank_delta, dimension_delta):
        self.edges.append([int(reverse), slot, self.index(old), self.index(new),
                           rank_delta, dimension_delta])

    def payload(self):
        return dict(matrices=[[[[x.numerator, x.denominator] for x in row]
                               for row in matrix] for matrix in self.matrices],
                    edges=self.edges)


def observed_reference(module, observe):
    """Insert only a callback into the pinned original, before its edge check.

    Timed reference runs call the original function directly, without this
    observer. This derived function is used solely for full trace comparison.
    """
    source = inspect.getsource(module.verify_invocation_frames)
    anchor = "                require(a==abs(change),'A physical edge has a non-nested rank charge')"
    need(source.count(anchor) == 1, 'Reference observer anchor changed')
    source = source.replace(anchor,
                            '                observe(reverse,slot,old,F,a,change)\n' + anchor)
    namespace = dict(vars(module), observe=observe)
    exec(compile(source, '<observed-pinned-reference>', 'exec', optimize=0), namespace)
    return namespace['verify_invocation_frames']


def expected_controls():
    certificate = json.loads((ROOT / 'certificates/ternary-side.json').read_text())
    return {control['construction']['h']: control
            for control in certificate['complete_invocation_controls']}


def compare_traces(reference, candidate):
    # Equality includes every numerator, denominator, orientation, slot, ordered
    # endpoint, rank difference, and dimension change, with edge multiplicity.
    need(reference == candidate, 'Complete ordered rational edge transcript differs')
