# SPDX-License-Identifier: Apache-2.0
# Prepared by Sagar Thakrar with substantial Anthropic Claude assistance.
"""Opt-in exact accelerator for the pinned PR635 hpe_audit_and_transport.py; the audited file is NOT edited.

install_import_hook() lets a control script import hpe_audit_and_transport by its own sys.path rule.  It loads that
file from the bytes it hashes (never from a .pyc) and, only when the sha256 is validated (PINNED_SHA256), rebinds five
module globals.  Every replacement returns exactly the values the original returns:

  Q          exact Fraction constructor; an integral value is returned as int (same value, ==, hash, truthiness,
             .numerator/.denominator; same exceptions, since Fraction(a, b) is evaluated first)
  apply      the same sparse row update, assertions and lazy row access in the same order; int arithmetic while all
             operands are integral, reduced rational arithmetic otherwise; zero entries are dropped at the same points
  copy       deepcopy replaced by a structural copy for flat JSON gate records (atoms and flat lists of atoms);
             anything deeper or of another type goes, as a whole, to copy.deepcopy
  basis      memoised on a type-strict key (only all-int inputs are cached); basis() is a pure function of its inputs
  state_maps the same P and P^-1 (equal exact values, same keys, same key order) computed in scaled-integer dyadic
             arithmetic when every prefix gate is a well-formed dyadic primitive; anything else uses the pinned code

run(), cone_violations(), inverse(), dual(), every assertion and message, and all serialisation remain the pinned
module's own code objects.  Helpers return int for integral values after installation, so only run() is claimed
equivalent; do not install into a process that does its own arithmetic with apply() or state_maps().  Python 3.10+.  FAST_HPE_PUBLIC_FRACTION=1 forces the public Fraction constructor instead of
Fraction._from_coprime_ints (3.12+), so both construction paths can be tested.
"""
import copy as _copy
import hashlib
import importlib.abc
import importlib.machinery
import importlib.util
import os
import sys
import types
from fractions import Fraction as _F
from math import gcd as _gcd

# sha256 of the module bytes validated here: PR635 complex-571-cold14-st2/code/hpe_audit_and_transport.py, identical
# to complex-sw4-frame8/local/hpe_audit_and_transport.py.  Other versions are refused and run unaccelerated.
PINNED_SHA256 = frozenset({'c9a05ff291016b870b4fc925b317abd9c3a604c73ffc8920dfdbbeb475e20aa3'})

_ATOMS = (int, str, type(None), bool, float)
_mk = _F if os.environ.get('FAST_HPE_PUBLIC_FRACTION') else (getattr(_F, '_from_coprime_ints', None) or _F)


def Qx(a, b=None):
    f = _F(a) if b is None else _F(a, b)
    return f.numerator if f.denominator == 1 else f


def _rat_add_mul(t, qn, qd, x):
    """Exact t + (qn/qd)*x for t in {None, int, Fraction}, x in {int, Fraction}: int when integral, else reduced."""
    if type(x) is int:
        pn, pd = qn*x, qd
    else:
        pn, pd = qn*x.numerator, qd*x.denominator
    if t is None:
        num, den = pn, pd
    elif type(t) is int:
        num, den = t*pd + pn, pd
    else:
        td = t.denominator
        num, den = t.numerator*pd + pn*td, td*pd
    if den == 1 or not num:
        return num
    g = _gcd(num, den)
    if g != 1:
        num //= g
        den //= g
    return num if den == 1 else _mk(num, den)


def fast_apply(e, rows):
    if e[0] == 'scale':
        _, target, a, b, *_ = e
        q = Qx(a, b)
        assert q
        if q == -1:
            rows[target] = {j: -x for j, x in rows[target].items()}
            return
        qn, qd = (q, 1) if type(q) is int else (q.numerator, q.denominator)
        rows[target] = {j: _rat_add_mul(None, qn, qd, x) for j, x in rows[target].items()}
        return
    _, target, source, a, b, *_ = e
    assert target != source
    q = Qx(a, b)
    src = rows[source]
    if not src:                          # the pinned loop body (and so rows[target]) is never reached
        return
    dst = rows[target]
    if dst is src:                       # aliasing is impossible for list rows after the assertion; kept for safety
        src = dict(src)
    get, pop = dst.get, dst.pop
    qn, qd = (q, 1) if type(q) is int else (q.numerator, q.denominator)
    if qd == 1 and (qn == 1 or qn == -1):
        neg = qn == -1
        for j, x in src.items():
            t = get(j)
            if type(x) is int and (t is None or type(t) is int):
                value = (-x if neg else x) if t is None else (t - x if neg else t + x)
            else:
                value = _rat_add_mul(t, qn, 1, x)
            if value:
                dst[j] = value
            else:
                pop(j, None)
    else:
        for j, x in src.items():
            t = get(j)
            if qd == 1 and type(x) is int and (t is None or type(t) is int):
                value = qn*x if t is None else t + qn*x
            else:
                value = _rat_add_mul(t, qn, qd, x)
            if value:
                dst[j] = value
            else:
                pop(j, None)


def _deepcopy(x, memo=None):
    """Structural copy of a flat JSON gate record (atoms and flat lists of atoms), else copy.deepcopy(x, memo).

    Only depth-2 lists take the fast path, so any deeper structure is copied by copy.deepcopy itself and reaches the
    interpreter's recursion limit at the same nesting depth as in the pinned module (one extra frame at most)."""
    if type(x) is list:
        out = []
        for y in x:
            t = type(y)
            if t in _ATOMS:
                out.append(y)
            elif t is list and all(type(z) in _ATOMS for z in y):
                out.append(y[:])
            else:
                return _copy.deepcopy(x, memo)
        return out
    return _copy.deepcopy(x, memo)


def make_basis(orig):
    cache = {}

    def basis(vs):
        key = tuple(vs)
        if not all(type(x) is int for x in key):
            return orig(key)             # floats, bools and other types take the pinned path every time
        r = cache.get(key)
        if r is None:
            r = cache[key] = orig(key)
        return r
    basis.cache = cache
    return basis


def _dyadic(a, b):
    """(num, k) with Fraction(a, b) == num / 2**k, or None unless a, b are ints and the value is an exact dyadic."""
    if type(a) is not int or type(b) is not int or not b:
        return None
    f = _F(a, b)
    den = f.denominator
    if den & (den - 1):
        return None
    return f.numerator, den.bit_length() - 1


def _dyadic_replay(gates, rows, dens):
    """rows[r]: dict j -> int X meaning X / 2**dens[r]; gates are ('s', t, num, k) or ('a', t, s, num, k)."""
    for g in gates:
        if g[0] == 's':
            _, t, num, k = g
            if num == -1:
                rows[t] = {j: -x for j, x in rows[t].items()}
            elif num != 1:
                rows[t] = {j: num*x for j, x in rows[t].items()}
            dens[t] += k
            continue
        _, t, s, num, k = g
        dst, src = rows[t], rows[s]
        if not src:
            continue
        dt, e = dens[t], k + dens[s]
        if e > dt:
            sh = e - dt
            for j in dst:
                dst[j] <<= sh
            dens[t] = dt = e
        if dt > e:
            num <<= dt - e
        get, pop = dst.get, dst.pop
        for j, x in src.items():
            p = x if num == 1 else (-x if num == -1 else num*x)
            t0 = get(j)
            value = p if t0 is None else t0 + p
            if value:
                dst[j] = value
            else:
                pop(j, None)
        if dt > 24 and dst:              # keep the common power of two reduced; exactness does not depend on it
            m = 0
            for x in dst.values():
                m |= x
            tz = min((m & -m).bit_length() - 1, dt)
            if tz:
                for j in dst:
                    dst[j] >>= tz
                dens[t] = dt - tz


def make_state_maps(orig):
    def state_maps(prefix, n):
        fwd, inv = [], []
        for e in prefix:
            if type(e) is not list or not e or e[0] not in ('add', 'scale'):
                return orig(prefix, n)
            if e[0] == 'scale':
                if len(e) < 4 or type(e[1]) is not int or not 0 <= e[1] < n or not e[2]:
                    return orig(prefix, n)
                c, ci = _dyadic(e[2], e[3]), _dyadic(e[3], e[2])
                if c is None or ci is None:
                    return orig(prefix, n)
                fwd.append(('s', e[1], c[0], c[1]))
                inv.append(('s', e[1], ci[0], ci[1]))
            else:
                if len(e) < 5 or type(e[1]) is not int or type(e[2]) is not int or e[1] == e[2] \
                        or not (0 <= e[1] < n and 0 <= e[2] < n):
                    return orig(prefix, n)
                c = _dyadic(e[3], e[4])
                if c is None or not c[0]:
                    return orig(prefix, n)
                fwd.append(('a', e[1], e[2], c[0], c[1]))
                inv.append(('a', e[1], e[2], -c[0], c[1]))
        state_maps.dyadic_calls += 1
        out = []
        for gates in (fwd, inv[::-1]):
            rows, dens = [{r: 1} for r in range(n)], [0]*n
            _dyadic_replay(gates, rows, dens)
            out.append([{j: Qx(x, 1 << d) for j, x in row.items()} if d else row for row, d in zip(rows, dens)])
        return out[0], out[1]
    state_maps.dyadic_calls = 0
    return state_maps


_MARKER = object()


def install(atc, require=False, state_maps=True):
    """Accelerate an imported module in place if its file has a validated sha256; return True when installed.

    Prefer install_import_hook(), which also guarantees that the executed code is compiled from the hashed bytes."""
    if getattr(atc, '_fast_hpe_marker', None) is _MARKER:
        return True
    with open(atc.__file__, 'rb') as stream:
        digest = hashlib.sha256(stream.read()).hexdigest()
    if digest not in PINNED_SHA256:
        refuse(atc.__file__, digest, require)
        return False
    _accelerate(atc, state_maps)
    return True


def refuse(path, digest, require):
    message = 'fast_hpe_transport: %s has sha256 %s (not validated); running it unaccelerated' % (path, digest)
    if require:
        raise SystemExit(message)
    print(message, file=sys.stderr)


def _accelerate(atc, state_maps):
    atc._fast_original = dict(Q=atc.Q, apply=atc.apply, copy=atc.copy, basis=atc.basis, state_maps=atc.state_maps)
    atc.Q = Qx
    atc.apply = fast_apply
    atc.copy = types.SimpleNamespace(deepcopy=_deepcopy)
    atc.basis = make_basis(atc._fast_original['basis'])
    if state_maps:
        atc.state_maps = make_state_maps(atc._fast_original['state_maps'])
    atc._fast_hpe_marker = _MARKER


class _HashedSourceLoader(importlib.abc.Loader):
    """Executes exactly the hashed source bytes (never a .pyc), then optionally accelerates and calls on_load."""

    def __init__(self, path, source, accelerate, state_maps, on_load):
        self.path, self.source = path, source
        self.accelerate, self.state_maps, self.on_load = accelerate, state_maps, on_load

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        module.__file__ = self.path
        exec(compile(self.source, self.path, 'exec', dont_inherit=True), module.__dict__)
        if self.accelerate:
            _accelerate(module, self.state_maps)
        if self.on_load:
            self.on_load(module)


class _AuditFinder(importlib.abc.MetaPathFinder):
    """Resolves 'hpe_audit_and_transport' exactly as the normal path finder would, from the importing script's own
    sys.path at import time, and loads that file from its hashed bytes."""

    def __init__(self, accelerate, require, state_maps, on_load):
        self.accelerate, self.require, self.state_maps, self.on_load = accelerate, require, state_maps, on_load
        self.loaded = []

    def find_spec(self, fullname, path=None, target=None):
        if fullname != 'hpe_audit_and_transport':
            return None
        spec = importlib.machinery.PathFinder.find_spec(fullname, path)
        if spec is None or not isinstance(spec.loader, importlib.machinery.SourceFileLoader):
            return spec
        with open(spec.origin, 'rb') as stream:
            source = stream.read()
        digest = hashlib.sha256(source).hexdigest()
        accelerate = self.accelerate and digest in PINNED_SHA256
        if self.accelerate and not accelerate:
            refuse(spec.origin, digest, self.require)
        self.loaded.append(dict(path=spec.origin, sha256=digest, accelerated=accelerate))
        return importlib.util.spec_from_file_location(
            fullname, spec.origin, loader=_HashedSourceLoader(spec.origin, source, accelerate, self.state_maps, self.on_load))


def install_import_hook(accelerate=True, require=False, state_maps=True, on_load=None):
    """Register the finder; the control script's own import then decides which file is the audit module."""
    if 'hpe_audit_and_transport' in sys.modules:
        raise RuntimeError('hpe_audit_and_transport already imported')
    finder = _AuditFinder(accelerate, require, state_maps, on_load)
    sys.meta_path.insert(0, finder)
    return finder
