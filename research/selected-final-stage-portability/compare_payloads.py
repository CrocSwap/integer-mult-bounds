#!/usr/bin/env python3
"""Compare two replay output trees file by file, by bytes and by canonical payload.

Classes: ``bytes`` (identical files), ``gzip-container`` (different .gz bytes,
identical decompressed bytes), ``json-format`` (different bytes, equal parsed
JSON), ``json-diff`` (parsed JSON differs; the differing JSON paths are listed),
``text-diff`` (other files whose bytes differ; differing line numbers listed),
``json-relocated`` (parsed JSON equal once each tree's own absolute input/work
directories are replaced by the same placeholder, in keys and string values),
``missing`` / ``extra``. A remaining JSON difference is reported as ``volatile``
only when every differing leaf is under a key named in VOLATILE_KEYS (wall-clock
``seconds``; a ``--volatile-key`` option adds more, e.g. ``log_sha256`` when the
logs print timings and are compared as files anyway); everything else is
reported as ``proof-relevant-candidate`` for a human to inspect.

Standard library only; Python 3.10+. Prepared with Claude Code (Claude Opus 5.5)
for JosieElliston's donated session 26. Apache-2.0.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

VOLATILE_KEYS = {'seconds'}


def files(root):
    return {str(p.relative_to(root)): p for p in sorted(root.rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts}


def json_diff(a, b, path=''):
    if type(a) is not type(b):
        return [(path, a, b)]
    if isinstance(a, dict):
        out = []
        for k in sorted(set(a) | set(b), key=str):
            if k not in a or k not in b:
                out.append((f'{path}/{k}', a.get(k, '<absent>'), b.get(k, '<absent>')))
            else:
                out += json_diff(a[k], b[k], f'{path}/{k}')
        return out
    if isinstance(a, list):
        if len(a) != len(b):
            return [(path + '#len', len(a), len(b))]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += json_diff(x, y, f'{path}/{i}')
        return out
    return [] if a == b else [(path, a, b)]


def volatile(diff):
    return diff[0].rsplit('/', 1)[-1] in VOLATILE_KEYS


def relocate(value, roots):
    """Replace absolute directory prefixes (longest first) by placeholders."""
    if isinstance(value, str):
        for token, prefix in roots:
            if value == prefix or value.startswith(prefix + '/'):
                return token + value[len(prefix):]
        return value
    if isinstance(value, dict):
        return {relocate(k, roots): relocate(v, roots) for k, v in value.items()}
    if isinstance(value, list):
        return [relocate(v, roots) for v in value]
    return value


def payload(path):
    raw = path.read_bytes()
    if path.name.endswith('.gz'):
        raw = gzip.decompress(raw)
    return raw


def classify(ref, run, ref_roots, run_roots):
    a, b = ref.read_bytes(), run.read_bytes()
    if a == b:
        return dict(cls='bytes')
    pa, pb = payload(ref), payload(run)
    gz = ref.name.endswith('.gz')
    if gz and pa == pb:
        return dict(cls='gzip-container')
    name = ref.name[:-3] if gz else ref.name
    if name.endswith('.json'):
        ja, jb = json.loads(pa), json.loads(pb)
        if ja == jb:
            return dict(cls='json-format', gzip=gz)
        ja, jb = relocate(ja, ref_roots), relocate(jb, run_roots)
        if ja == jb:
            return dict(cls='json-relocated', gzip=gz)
        diffs = json_diff(ja, jb)
        rel = [d for d in diffs if not volatile(d)]
        return dict(cls='json-diff', gzip=gz, differing=len(diffs),
                    verdict='volatile' if not rel else 'proof-relevant-candidate',
                    examples=[[d[0], repr(d[1])[:120], repr(d[2])[:120]] for d in (rel or diffs)[:8]])
    la, lb = pa.decode(errors='replace').splitlines(), pb.decode(errors='replace').splitlines()
    lines = [i + 1 for i in range(max(len(la), len(lb)))
             if (la[i] if i < len(la) else None) != (lb[i] if i < len(lb) else None)]
    return dict(cls='text-diff', lines=len(la), run_lines=len(lb), differing_lines=lines[:20],
                examples=[[(la[i-1] if i <= len(la) else '<absent>')[:160],
                           (lb[i-1] if i <= len(lb) else '<absent>')[:160]] for i in lines[:4]])


def roots(pairs):
    out = []
    for pair in pairs:
        token, _, prefix = pair.partition('=')
        if not token or not prefix.startswith('/'):
            raise SystemExit('expected TOKEN=/absolute/prefix: ' + pair)
        out.append((token, prefix.rstrip('/')))
    return sorted(out, key=lambda t: -len(t[1]))


def compare(ref_root, run_root, ref_roots=(), run_roots=()):
    ref, run = files(ref_root), files(run_root)
    out = {}
    for name in sorted(set(ref) | set(run)):
        if name not in run:
            out[name] = dict(cls='missing')
        elif name not in ref:
            out[name] = dict(cls='extra')
        else:
            out[name] = classify(ref[name], run[name], ref_roots, run_roots)
            out[name]['ref_sha256'] = hashlib.sha256(ref[name].read_bytes()).hexdigest()
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('ref', type=Path)
    ap.add_argument('run', type=Path)
    ap.add_argument('--ref-root', action='append', default=[], metavar='TOKEN=PREFIX',
                    help='absolute directory used by the reference run, mapped to TOKEN')
    ap.add_argument('--run-root', action='append', default=[], metavar='TOKEN=PREFIX',
                    help='absolute directory used by the compared run, mapped to TOKEN')
    ap.add_argument('--volatile-key', action='append', default=[],
                    help='additional JSON key whose differing values are classified volatile')
    ap.add_argument('--out', type=Path)
    a = ap.parse_args()
    VOLATILE_KEYS.update(a.volatile_key)
    result = compare(a.ref, a.run, roots(a.ref_root), roots(a.run_root))
    counts = {}
    for v in result.values():
        k = v['cls'] + (':' + v['verdict'] if 'verdict' in v else '')
        counts[k] = counts.get(k, 0) + 1
    report = dict(ref=str(a.ref), run=str(a.run), counts=counts, files=result)
    if a.out:
        a.out.write_text(json.dumps(report, indent=1, sort_keys=True) + '\n')
    print(json.dumps(counts, sort_keys=True))


if __name__ == '__main__':
    main()
