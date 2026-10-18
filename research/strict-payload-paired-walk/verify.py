#!/usr/bin/env python3
"""Full retained corpus differential replay and scoped traversal controls.

ywz65, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import builtins
from collections import Counter
import gzip
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = 'research/strict-replay-payload-comparison/'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def bind(root=ROOT):
    manifest = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    expected = {OLD + x for x in ('compare.py', 'verify.py', 'RESULT.json',
                                  'SOURCES.json', 'TIMINGS.json', 'test_compare.py')}
    expected |= {'research/community-frontier1094-audit/' + x for x in (
        'selected-replay.tar.gz', 'RESULT.json', 'REPLAY.json', 'ASSEMBLY.json')}
    expected |= {'research/selected-final-stage-portability/' + x for x in ('compare_payloads.py', 'README.md')}
    rows = [r for r in manifest['files'] if r['usage'] == 'input']
    require(len(rows) == len(expected) and {r['path'] for r in rows} == expected,
            'input inventory differs')
    for row in rows:
        raw = (root / row['path']).read_bytes()
        require(row['usage'] == 'input' and hashlib.sha256(raw).hexdigest() == row['sha256'],
                'input SHA256 differs: ' + row['path'])
        require(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'],
                'input blob differs: ' + row['path'])
    return manifest


def module(path, aliases=None):
    mod = types.ModuleType('private_' + path.stem)
    mod.__file__ = str(path)
    env = dict(vars(builtins))
    def importing(name, *args, **kwargs):
        if aliases and name in aliases:
            return aliases[name]
        return builtins.__import__(name, *args, **kwargs)
    env['__import__'] = importing
    mod.__dict__['__builtins__'] = env
    exec(compile(path.read_bytes(), str(path), 'exec'), mod.__dict__)
    return mod


def setup():
    bind()
    fast = module(HERE / 'compare.py')
    retained = module(ROOT / OLD / 'verify.py', {'compare': fast.source})
    return fast, retained


def controls(fast, differential):
    total = 0
    atoms = [b'null', b'true', b'false', b'0', b'1', b'-1', b'1.0', b'1.00',
             b'0.00000000000000000000001', b'1e999', b'10e998', b'"x"', b'[]', b'{}']
    for a, b in itertools.product(atoms, repeat=2):
        for prefix, suffix in ((b'', b''), (b'[', b']'), (b'{"x":', b'}')):
            differential('p.json', prefix+a+suffix, prefix+b+suffix)
            total += 1
    ra, rb = fast.Roots([('W', '/a'), ('N', '/a/n')]), fast.Roots([('W', '/b'), ('N', '/b/n')])
    # Timing paths use original keys, not normalized key tags. Both masks must
    # designate the paired node; root-valued timing is also an allowed policy.
    pairs = [
        (b'{"s":[{"seconds":1.0}],"proof":17}', b'{"s":[{"seconds":2}],"proof":17}', [('s',0,'seconds')]),
        (b'{"s":[{"seconds":1.0}],"proof":17}', b'{"s":[{"seconds":2}],"proof":18}', [('s',0,'seconds')]),
        (b'1.0', b'2', [()]),
        (b'{"/a":1,"/b":2}', b'{"/a":2,"/b":1}', [('/a',)]),
        (b'{"/a":1,"/b":2}', b'{"/a":1,"/b":2}', [('/a',)]),
        (b'{"/a/n/file":1,"x":"/a/f"}', b'{"/b/n/file":1,"x":"/b/f"}', []),
        (b'{"x":"/a/f"}', b'{"x":"/a/f"}', []),
        (b'{"x":"/a/f"}', b'{"x":"W/f"}', []),
    ]
    for a,b,policy in pairs:
        for x,y in ((fast.EMPTY,fast.EMPTY),(ra,rb)):
            differential('p.json',a,b,x,y,policy); total += 1
    invalid = [b'{"a":1,"a":2}', b'NaN', b'Infinity', b'{', b'"\xff"']
    for a in invalid:
        for b in (a,b'{}'):
            differential('p.json',a,b); total += 1
    raw = b'{"x":1}'
    for a,b in [(gzip.compress(raw,mtime=1),gzip.compress(raw,mtime=2)),
                (gzip.compress(raw),gzip.compress(b'{"x":true}')),
                (gzip.compress(raw),gzip.compress(raw)[:-5]),(b'bad',b'bad')]:
        differential('p.json.gz',a,b); total += 1
    for policy in ([('s',0,'seconds')]*2,[('s',False,'seconds')],[('s',-1,'seconds')],
                   [('missing',)],None):
        differential('p.json',pairs[0][0],pairs[0][1],timing_paths=policy); total += 1
    for a,b in ((b'a',b'a'),(b'a',b'b')):
        differential('p.bin',a,b); total += 1
    return total


def run():
    fast, retained = setup()
    counts = Counter()
    def differential(*args, **kwargs):
        expected = fast.original_classify(*args, **kwargs)
        actual = fast.classify(*args, **kwargs)
        require(encoded(actual) == encoded(expected), 'complete classification differs: '+str(args[0]))
        counts[retained.label(actual)] += 1
        return actual
    # Original exact-source corpus generator and 39 original adverse witnesses.
    # Every classify invocation now checks the full original result, including
    # errors/first-difference paths; the stored original receipt also must match.
    proxy = types.SimpleNamespace(**vars(fast.source))
    proxy.classify = differential
    retained.strict = proxy
    inputs = retained.bound_inputs()
    data = retained.corpus(inputs)
    result = retained.audit(inputs,data)
    require(encoded(result) == encoded(json.loads((ROOT / OLD / 'RESULT.json').read_bytes())),
            'retained complete receipt differs')
    before = sum(counts.values())
    extra = controls(fast,differential)
    # Reformat every compressed JSON body too: these large positive payloads
    # exercise the optimized traversal rather than the equal-body shortcut.
    reformats = 0
    for name,raw in sorted(data.items()):
        if name.endswith('.json.gz'):
            body = gzip.decompress(raw)
            changed = b'\n'+body+b'\n'
            actual = differential(name,raw,gzip.compress(changed,mtime=123))
            require(actual == {'cls':'json-format'}, 'large reformat not exercised')
            reformats += 1
    return {'status':'PASS_STRICT_PAYLOAD_PAIRED_WALK', 'corpus_files':len(data),
            'retained_classify_calls':before, 'retained_adverse_witnesses':39,
            'extra_differential_cases':extra,'compressed_json_reformats':reformats,
            'classifications':dict(sorted(counts.items())),
            'scope':'exact comparison equivalence on stated corpus/controls; no supplier replay or new kappa'}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',type=Path)
    args=parser.parse_args()
    result=run()
    if args.write:
        with args.write.open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(result,stream,indent=2,sort_keys=True);stream.write('\n')
    else:
        require(encoded(result)==encoded(json.loads((HERE/'RESULT.json').read_bytes())), 'typed complete receipt differs')
    print(result['status'])
