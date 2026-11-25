"""Hash-keyed memo + parallel prefetch for the finer-constant rational moment engines (package code).

The finer engines are deterministic pure functions of (engine source, H, m, W, z, bad). Several package stages
(assembly, admission controls, bit controls, geometry controls) each run the same assembler on the same valid inputs; this module
lets them share one computation: each result is stored in the directory named by FINE_ENGINE_CACHE (set by verify.py to a
directory inside the work directory), keyed by sha256 over (engine file sha256, all arguments). Without that variable nothing is cached
and nothing changes. `prefetch` computes the independent enclosures concurrently in worker processes (this file run as a script).
"""
import hashlib, json, os, subprocess, sys, time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE_FILES = {'fine_mercator': HERE / 'fine_mercator.py', 'fine_moment': HERE / 'fine_moment.py'}


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _key(name, H, m, W, z, bad, entries=None):
    blob = json.dumps([name, _sha(ENGINE_FILES[name]), sorted(H.items()) if H is not None else None, m, W, str(z), bool(bad),
                       entries], sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()


def _compute(name, H, m, W, z, bad, entries):
    if name == 'fine_mercator':
        import fine_mercator as E
        return E.moment(H, m, W, z, bad)
    import fine_moment as E
    return E.moment(m, W, entries if entries is not None else list(H.items()), z)


def _dump(res):
    return [[str(x.numerator), str(x.denominator)] for x in res]


def _load(raw):
    return tuple(F(int(a), int(b)) for a, b in raw)


def _log(d, what, name, key, t0):
    try:
        with open(Path(d) / 'LOG.txt', 'a') as f:
            f.write('%s %s %s %.1fs pid=%d\n' % (what, name, key[:12], time.monotonic() - t0, os.getpid()))
    except OSError:
        pass


def memo(name, key_parts, fn):
    """Pickle memo of a deterministic pure computation (used for the exact outer witness): key = sha256 of key_parts."""
    d = os.environ.get('FINE_ENGINE_CACHE')
    if not d:
        return fn()
    import pickle
    t0 = time.monotonic()
    k = hashlib.sha256(repr((name, key_parts)).encode()).hexdigest()
    p = Path(d) / (name + '-' + k + '.pkl')
    if p.is_file():
        try:
            blob = p.read_bytes()
            rec = pickle.loads(blob)
            if rec['key'] == k:
                _log(d, 'HIT', name, k, t0)
                return rec['value']
        except Exception:
            pass
    val = fn()
    Path(d).mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix('.tmp%d' % os.getpid())
    tmp.write_bytes(pickle.dumps(dict(key=k, value=val), pickle.HIGHEST_PROTOCOL))
    tmp.replace(p)
    _log(d, 'MISS', name, k, t0)
    return val


def moment(name, H, m, W, z, bad=False, entries=None):
    """fine_mercator.moment(H,m,W,z,bad) or fine_moment.moment(m,W,entries or H.items(),z), memoised on disk when enabled."""
    d = os.environ.get('FINE_ENGINE_CACHE')
    if not d:
        return _compute(name, H, m, W, z, bad, entries)
    k = _key(name, H, m, W, z, bad, entries)
    p = Path(d) / (k + '.json')
    t0 = time.monotonic()
    if p.is_file():
        try:
            rec = json.loads(p.read_text())
            if rec['key'] == k and rec['check'] == hashlib.sha256((k + json.dumps(rec['result'])).encode()).hexdigest():
                _log(d, 'HIT', name, k, t0)
                return _load(rec['result'])
        except (ValueError, KeyError, OSError):
            pass
    res = _compute(name, H, m, W, z, bad, entries)
    Path(d).mkdir(parents=True, exist_ok=True)
    raw = _dump(res)
    tmp = p.with_suffix('.tmp%d' % os.getpid())
    tmp.write_text(json.dumps(dict(key=k, result=raw, check=hashlib.sha256((k + json.dumps(raw)).encode()).hexdigest())))
    tmp.replace(p)
    _log(d, 'MISS', name, k, t0)
    return res


def prefetch(tasks, workers=None):
    """tasks: list of dicts(name,H,m,W,z,bad,entries). Computes the missing ones concurrently into the cache."""
    d = os.environ.get('FINE_ENGINE_CACHE')
    if not d:
        return
    Path(d).mkdir(parents=True, exist_ok=True)
    todo = [t for t in tasks if not (Path(d) / (_key(t['name'], t['H'], t['m'], t['W'], t['z'], t['bad'], t.get('entries')) + '.json')).is_file()]
    if not todo:
        return
    workers = max(1, min(int(workers or os.environ.get('FINE_ENGINE_WORKERS') or 8), len(todo), os.cpu_count() or 1))
    procs = []
    for w in range(workers):
        chunk = todo[w::workers]
        spec = Path(d) / ('.tasks%d-%d.json' % (os.getpid(), w))
        spec.write_text(json.dumps([dict(name=t['name'], H=sorted(t['H'].items()) if t['H'] is not None else None, m=t['m'], W=t['W'],
                                         z=str(t['z']), bad=bool(t['bad']), entries=t.get('entries')) for t in chunk]))
        procs.append((subprocess.Popen([sys.executable, '-B', str(Path(__file__).resolve()), str(spec)], stdout=subprocess.DEVNULL,
                                       stderr=subprocess.PIPE, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)), spec))
    for pr, spec in procs:
        err = pr.communicate()[1]
        spec.unlink()
        if pr.returncode:
            raise RuntimeError('fine-engine prefetch worker failed: ' + err.decode('utf-8', 'replace')[-800:])


if __name__ == '__main__':
    sys.set_int_max_str_digits(0)
    sys.path.insert(0, str(HERE))
    for t in json.loads(Path(sys.argv[1]).read_text()):
        H = {int(r): int(n) for r, n in t['H']} if t['H'] is not None else None
        entries = [tuple(e) for e in t['entries']] if t.get('entries') is not None else None
        moment(t['name'], H, t['m'], t['W'], F(t['z']), t['bad'], entries)
