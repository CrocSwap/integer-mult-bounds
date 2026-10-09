#!/usr/bin/env python3
"""Verify the frozen sources, literal words, actual profiles and arithmetic."""
import argparse
from copy import deepcopy
from collections import Counter
import gzip
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import subprocess
import tempfile
from support import HERE, ROOT, SELECTED, write_json, json_value
from binary_frame_replay import replay
from binary_frame_profile_prepare import prepare
from arithmetic import certify, independent_audit
import generate


def require(value, message):
    if not value:
        raise ValueError(message)


def index(value, limit, message):
    require(type(value) is int and 0 <= value < limit, message)


def validate_word(word):
    require(set(word) == {'h', 'v', 'R', 'frames', 'ops', 'events', 'sources', 'outputs', 'scatter'}, 'Unexpected word schema')
    h, v, roles = word['h'], word['v'], word['R']
    require(type(h) is int and h in (23, 25), 'Unsupported axis')
    triples = list(combinations(range(h), 3))
    require(type(v) is int and v == len(triples), 'Source dimension')
    require(type(roles) is int and roles == {23: 27043, 25: 35505}[h], 'Selected role count')
    frames = word['frames']
    require(type(frames) is list and len(frames) > 0, 'Missing frames')
    for frame in frames:
        require(type(frame) is list and len(frame) == 2, 'Frame pair')
        c, u = frame
        index(c, 1 << h, 'Core mask bounds'); index(u, 1 << h, 'Cover mask bounds')
        require(c and not c & ~u, 'Core inclusion')
        require(c.bit_count() in (1, 2) or c == u and c.bit_count() == 3, 'Original-envelope frame')
    require(len({tuple(f) for f in frames}) == len(frames), 'Duplicate frame ID')
    for op in word['ops']:
        require(type(op) is list and len(op) == 3, 'XOR schema')
        a, b, g = op
        index(a, roles, 'XOR destination'); index(b, roles, 'XOR control'); index(g, len(frames), 'XOR frame')
        require(a != b, 'Noninvertible self XOR')
    for event in word['events']:
        require(type(event) is list and len(event) == 3, 'Event schema')
        s, a, b = event
        index(s, roles, 'Event role'); index(b, len(frames), 'Event target')
        require(type(a) is int and -1 <= a < len(frames), 'Event source')
    sources = word['sources']
    require(type(sources) is dict and set(sources) == {str(i) for i in range(v)}, 'Canonical complete source ports')
    for s in sources.values():
        index(s, roles, 'Source role')
    require(len(set(sources.values())) == v, 'Aliased source carriers')
    expected_scatter, output_roles = [], set()
    triple_index = {t: i for i, t in enumerate(triples)}
    for output in word['outputs']:
        require(type(output) is list and len(output) == 4, 'Output schema')
        s, g, common, triple = output
        index(s, roles, 'Output role'); index(g, len(frames), 'Output frame'); index(common, h, 'Common point')
        require(s not in output_roles, 'Aliased terminal role'); output_roles.add(s)
        require(type(triple) is list and len(triple) in (1, 3), 'Output triple schema')
        for x in triple:
            index(x, h, 'Triple point')
        require(triple == sorted(set(triple)) and common in triple, 'Canonical output triple')
        targets = [i for i, t in enumerate(triples) if common in t] if len(triple) == 1 else [triple_index[tuple(triple)]]
        expected_scatter.extend([[v+i, 2*v+s] for i in targets])
    for port in word['scatter']:
        require(type(port) is list and len(port) == 2, 'Scatter pair schema')
        a, b = port
        require(type(a) is int and v <= a < 2*v, 'Scatter destination bounds')
        require(type(b) is int and 2*v <= b < 2*v+roles, 'Scatter control bounds')
    # All these gates read scratch and write targets, so they commute. Point
    # conjugation changes their lexical order, but every multiplicity is paid.
    require(Counter(map(tuple, word['scatter'])) == Counter(map(tuple, expected_scatter)),
            'Literal scatter multiset must equal the charged terminal ports')


def check_manifest():
    source = json.loads((HERE/'SOURCE.json').read_text())
    for name, digest in source['files'].items():
        path = ROOT/name
        require(path.resolve().is_relative_to(ROOT.resolve()), 'Manifest path escaped repository')
        require(sha256(path.read_bytes()).hexdigest() == digest, 'Changed frozen file: '+name)
    return source


def check_axis(h, work, profiler, directory=SELECTED):
    packed = directory/f'word-{h}.json.gz'
    raw = gzip.decompress(packed.read_bytes())
    validate_word(json.loads(raw))
    actual_replay = replay(packed)
    expected_replay = json.loads((directory/f'replay-{h}.json').read_text())
    require(json_value(actual_replay) == expected_replay, 'Independent dirty replay changed')
    path = work/f'axis-{h}.bin'
    actual_transition = prepare(packed, path)
    require(json_value(actual_transition) == json.loads((directory/f'transitions-{h}.json').read_text()), 'Literal frame transitions changed')
    subprocess.run([str(profiler), str(path)], check=True)
    actual_profile = json.loads(Path(str(path)+'.profiles.json').read_text())
    require(actual_profile == json.loads((directory/f'profile-{h}.json').read_text()), 'Exact physical profile changed')
    print(f'PASS independent literal word, all dirty basis vectors and paid CRT profile h={h}', flush=True)


def verify(rebuild=False):
    check_manifest()
    with tempfile.TemporaryDirectory(prefix='balanced-split-') as temporary:
        work = Path(temporary)
        oracle, profiler = generate.binaries(work)
        if rebuild:
            for h in (23, 25):
                generate.generate_axis(h, work, oracle, profiler)
                actual = gzip.decompress((work/f'word-{h}.json.gz').read_bytes())
                expected = gzip.decompress((SELECTED/f'word-{h}.json.gz').read_bytes())
                require(actual == expected, 'Regenerated physical word differs byte-for-byte')
                for prefix in ('compiled', 'replay', 'profile', 'transitions', 'config'):
                    require(json.loads((work/f'{prefix}-{h}.json').read_text()) == json.loads((SELECTED/f'{prefix}-{h}.json').read_text()), 'Regenerated '+prefix+' differs')
        for h in (23, 25):
            check_axis(h, work, profiler)
    actual = certify(generate.combine(SELECTED))
    recorded = json.loads((SELECTED/'certificate.json').read_text())
    require(json_value(actual) == recorded, 'Complete exact arithmetic certificate changed')
    require(json_value(independent_audit(recorded)) == json.loads((SELECTED/'audit.json').read_text()), 'Independent arithmetic receipt changed')
    print('PASS complete PR82 exclusion, adjacent grid rejection, 47 strict constraints and seven margins', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rebuild', action='store_true')
    verify(parser.parse_args().rebuild)
