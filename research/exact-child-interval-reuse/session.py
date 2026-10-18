"""Bounded process-local memoization of unchanged exact child-cost intervals.

Every source model and bisection still executes. Sessions are private, serial,
and never load a persisted cache. Gareth Davidson / OpenAI Codex, Apache-2.0.
"""
from collections import OrderedDict, Counter
from contextlib import redirect_stdout
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import fractions
import io
import json
import sys
import types

_MISSING = object()


def need(ok, message):
    if not ok:
        raise ValueError(message)


def freeze(value):
    """Preserve all values and types in an ordered call trace."""
    if type(value) is Q:
        return ['rational', value.numerator, value.denominator]
    if type(value) in (int, bool, str, float, type(None)):
        return [type(value).__name__, repr(value)]
    if type(value) in (list, tuple):
        return [type(value).__name__, [freeze(x) for x in value]]
    if type(value) is dict:
        items = [[freeze(k), freeze(v)] for k, v in value.items()]
        return ['dict', sorted(items, key=lambda x: json.dumps(x[0], sort_keys=True))]
    raise TypeError('unsupported exact trace value: ' + type(value).__name__)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


class Session:
    """A caller must supply authenticated source bytes; no shared result cache."""
    def __init__(self, engine_path, fixture_path, pins, reuse=True, max_entries=8192):
        need(type(max_entries) is int and max_entries >= 1, 'positive cache capacity')
        self.paths = {'engine': Path(engine_path), 'fixture': Path(fixture_path)}
        self.pins = dict(pins)
        need(set(self.pins) == set(self.paths), 'complete source roles')
        self.reuse, self.max_entries = reuse, max_entries
        self._weights = OrderedDict()
        self._fraction_path = Path(fractions.__file__).resolve()
        self._fraction_digest = sha256(self._fraction_path.read_bytes()).hexdigest()
        self._runtime = (sys.version, sys.implementation.name, Q)
        raw = {}
        for role, path in self.paths.items():
            raw[role] = path.read_bytes()
            need(sha256(raw[role]).hexdigest() == self.pins[role], 'source changed: ' + role)
        self._fixture = raw['fixture']
        module = types.ModuleType('ceiling')
        module.__file__ = str(self.paths['engine'])
        exec(compile(raw['engine'], str(self.paths['engine']), 'exec'), module.__dict__)
        self._module = module
        self._precision = module.PREC
        self.events = []
        self.counts = Counter()
        for name in ('model', 'child_cost', 'relax', 'ceiling'):
            original = getattr(module, name)
            setattr(module, name, self._wrapped(name, original))
        self._bindings = {name: value for name, value in module.__dict__.items()
                          if not name.startswith('__') and callable(value)}
        self.context = {'source_sha256': self.pins, 'precision': self._precision,
                        'python': sys.version, 'implementation': sys.implementation.name,
                        'fractions_sha256': self._fraction_digest}
        self.context_id = sha256(canonical(self.context).encode()).hexdigest()

    def guard(self):
        try:
            for role, path in self.paths.items():
                need(sha256(path.read_bytes()).hexdigest() == self.pins[role], 'source changed: ' + role)
            need(sha256(self._fraction_path.read_bytes()).hexdigest() == self._fraction_digest,
                 'runtime dependency changed')
            need((sys.version, sys.implementation.name, Q) == self._runtime, 'runtime identity changed')
            need(type(self._module.PREC) is type(self._precision) and self._module.PREC == self._precision,
                 'precision context changed')
            need(all(getattr(self._module, name, None) is value for name, value in self._bindings.items()),
                 'engine binding changed')
        except (ValueError, OSError):
            self._weights.clear()
            raise

    def _wrapped(self, name, original):
        def call(*args, **kwargs):
            if name == 'ceiling':
                self.guard()
            event = {'function': name, 'args': freeze(args), 'kwargs': freeze(kwargs)}
            try:
                # Only the exact types used by the original planner are reused.
                # Numeric equality must not alias a float/subclass with a Fraction.
                eligible = (name == 'child_cost' and len(args) == 3 and not kwargs
                            and type(args[0]) is int and type(args[1]) is int and type(args[2]) is Q)
                if self.reuse and eligible:
                    r, m, a = args
                    key = (self._precision, r, m, a.numerator, a.denominator)
                    if key in self._weights:
                        result = self._weights.pop(key)
                        self._weights[key] = result
                        self.counts['hits'] += 1
                    else:
                        result = original(*args, **kwargs)
                        self.counts['misses'] += 1
                        self._weights[key] = result
                        if len(self._weights) > self.max_entries:
                            self._weights.popitem(last=False)
                            self.counts['evictions'] += 1
                else:
                    result = original(*args, **kwargs)
                    self.counts['uncached'] += int(name == 'child_cost')
                event['result'] = freeze(result)
            except Exception as error:
                event['error'] = [type(error).__name__, str(error)]
                self.events.append(event)
                raise
            self.events.append(event)
            return result
        return call

    def reset_trace(self):
        self.events = []
        self.counts = Counter()

    def invoke(self, name, *args, **kwargs):
        need(name in ('model', 'child_cost', 'relax', 'ceiling'), 'supported pricing operation')
        self.reset_trace()
        self.guard()
        result = getattr(self._module, name)(*args, **kwargs)
        self.guard()
        return result

    def fixture(self):
        """Execute the unchanged seven-lever script with this private module."""
        self.reset_trace()
        self.guard()
        old_module, old_path = sys.modules.get('ceiling', _MISSING), list(sys.path)
        out = io.StringIO()
        try:
            sys.modules['ceiling'] = self._module
            with redirect_stdout(out):
                exec(compile(self._fixture, str(self.paths['fixture']), 'exec'),
                     {'__name__': '__main__', '__file__': str(self.paths['fixture'])})
        finally:
            sys.path[:] = old_path
            if old_module is _MISSING:
                sys.modules.pop('ceiling', None)
            else:
                sys.modules['ceiling'] = old_module
        self.guard()
        return out.getvalue()

    def evidence(self, stdout):
        raw = canonical(self.events).encode()
        return {'trace_sha256': sha256(raw).hexdigest(), 'trace_bytes': len(raw),
                'event_counts': dict(sorted(Counter(e['function'] for e in self.events).items())),
                'stdout': stdout, 'cache_counts': dict(self.counts), 'entries': len(self._weights),
                'max_entries': self.max_entries,
                'ceiling_results': [e for e in self.events if e['function'] == 'ceiling']}
