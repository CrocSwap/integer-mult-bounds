#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Supplemental PR589 identity guard; no supplier replay or moment certification.

Arham Tahir, with substantial OpenAI Codex assistance. Follows the provenance
question in Sagar Thakrar's PR1277 and credits the retained PR589 lineage.
"""
from fractions import Fraction
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import json
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_ROOT = 'research/e8-bit-p111'
RETAINED_ROOT = 'research/e8-bit-p111-tuned'
MERGE = 'b3eb785ac5b4b1ca2beea0f80db078a505626a90'
ASSEMBLIES = tuple('research/community-frontier%d-audit/ASSEMBLY.json' % n
                   for n in (741, 799, 1042, 1094))
BIT_RESULT = 'research/community-frontier741-audit/bit/RESULT9.json'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def same(actual, expected):
    """JSON equality that does not silently identify true with 1."""
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(same(actual[k], v) for k, v in expected.items())
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(same(a, b) for a, b in zip(actual, expected))
    return actual == expected


def git(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], check=True,
                          capture_output=True).stdout


def blob_id(raw):
    return sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def rank(rows, width=8):
    """Exact incremental elimination over Q, independent of the supplier code."""
    basis = {}
    for row in rows:
        require(len(row) == width and all(type(x) is int for x in row), 'integer root row')
        v = list(map(Fraction, row))
        for pivot, b in sorted(basis.items()):
            coefficient = v[pivot]
            if coefficient:
                v = [a - coefficient * c for a, c in zip(v, b)]
        pivot = next((i for i, x in enumerate(v) if x), None)
        if pivot is not None:
            coefficient = v[pivot]
            basis[pivot] = [x / coefficient for x in v]
    return len(basis)


def copy_ranks(word):
    """Follow only D/A frame assignments up to COPY, then rank the totals.

    Each gate lifts every operand to its named common frame. This is the
    source format's frame trace, not a check of gate legality or scalar values.
    """
    n = 2 * word['v'] + word['R']
    require(word['h'] == 8 and len(word['lines']) == word['v'], 'word dimensions')
    cur = list(word['start'])
    require(len(cur) == n, 'word register inventory')
    for section in ('D', 'A'):
        for frame, destination, sources in word[section]:
            require(type(frame) is int and 0 <= frame < len(word['frames']), 'frame id')
            operands = [destination, *sources]
            require(sources and len(set(operands)) == len(operands) and
                    all(type(q) is int and 0 <= q < n for q in operands), 'gate operands')
            for q in operands:
                cur[q] = frame
    totals = word['ret']
    require(len(set(totals)) == len(totals) and all(type(q) is int and 2 * word['v'] <= q < n
                                                  for q in totals), 'retained helper inventory')
    out = []
    for q in totals:
        frame = word['frames'][cur[q]]
        require(all(type(i) is int and 0 <= i < word['v'] for i in frame), 'frame label index')
        out.append(rank([word['lines'][i] for i in frame]))
    require(all(0 < r <= 8 for r in out), 'COPY rank range')
    return out


def derive(record, word):
    """Connect the stated deficit to actual COPY frames and the priced profile."""
    ranks = copy_ranks(word)
    summary = dict(v=word['v'], decoder_constant=sum(ranks), copy_ranks=ranks)
    for name, value in summary.items():
        require(same(record['word'][name], value), 'word record: ' + name)
    require(same(record['word']['R'], word['R']) and
            same(record['word']['retained_totals'], len(ranks)), 'word helper/total count')
    nine = record['nine']
    stages, replicas = 9, 32
    pairs, width = (stages - 1) // 2, 1 + 7 * stages
    live = 2 * pairs * word['v'] * replicas
    profile = nine['profile']
    require(all(type(k) is str and k.isdecimal() and str(int(k)) == k and 0 < int(k) < width
                and type(v) is int and v > 0 for k, v in profile.items()), 'priced profile integers')
    mass = sum(int(r) * count for r, count in profile.items())
    deficit = replicas * (2 * pairs * word['v'] - stages * sum(ranks))
    require(deficit > 0 and width * live - mass == deficit, 'COPY/profile deficit identity')
    require(same(nine['bit']['live'], live) and same(nine['bit']['rank_mass'], mass), 'bit rank mass')
    require(same(nine['bit']['hosted_residuals'], replicas * stages * word['R']), 'bit helper inventory')
    return dict(word=summary, derived_deficit=deficit, live=live, rank_mass=mass,
                stages=stages, replicas=replicas, profile=profile,
                deficit_formula='T(2Kv-L*cst), L=9 T=32 K=4 M=64')


def context(root=ROOT, sources_path=HERE / 'SOURCES.json'):
    """Authenticate pinned inputs and the source-to-main rename with Git objects."""
    sources = json.loads(sources_path.read_bytes())
    base = sources['base_commit']
    for item in sources['files']:
        name = item['path']
        pinned = git(root, 'show', base + ':' + name)
        require(sha256(pinned).hexdigest() == item['sha256'] and blob_id(pinned) == item['git_blob'],
                'historical source pin: ' + name)
        if item['usage'] == 'input':
            require((root / name).read_bytes() == pinned, 'live source pin: ' + name)
    selected = json.loads(git(root, 'show', base + ':certificates/selected-result.json'))
    head = selected['reviewed_dependency_heads']['589']
    require(git(root, 'cat-file', '-t', head).strip() == b'commit', 'reviewed PR589 commit')
    parents = git(root, 'show', '-s', '--format=%P', MERGE).decode('ascii').split()
    require(head in parents, 'PR589 is a preserved integration parent')
    git(root, 'merge-base', '--is-ancestor', MERGE, base)
    raw = (root / RETAINED_ROOT / 'tune/EXPECTED.json').read_bytes()
    record = json.loads(raw)
    word_name = record['word']['file']
    require(word_name == 'tune/bitE8mut-p111-tuned.json.gz', 'pinned word path')
    word_raw = (root / RETAINED_ROOT / word_name).read_bytes()
    objects = {}
    for name, current in (('tune/EXPECTED.json', raw), (word_name, word_raw)):
        source = git(root, 'show', head + ':' + SOURCE_ROOT + '/' + name)
        merged = git(root, 'show', MERGE + ':' + RETAINED_ROOT + '/' + name)
        require(source == merged == current, 'source/integration/retained bytes: ' + name)
        objects[name] = blob_id(current)
    payload = gzip.decompress(word_raw)
    require(sha256(word_raw).hexdigest() == record['word']['file_sha256'] and
            sha256(payload).hexdigest() == record['word']['content_sha256'], 'word payload binding')
    word = json.loads(payload)
    derived = derive(record, word)
    supplier = dict(pr=589, repository='CrocSwap/integer-mult-bounds', commit=head, merged_as=MERGE,
                    path=RETAINED_ROOT + '/tune/EXPECTED.json', git_blob_sha1=blob_id(raw),
                    word=derived['word'], derived_deficit=derived['derived_deficit'],
                    deficit_formula=derived['deficit_formula'])
    return dict(supplier=supplier, record=record, derived=derived, base_commit=base,
                record_sha256=sha256(raw).hexdigest(), word_content_sha256=sha256(payload).hexdigest(),
                git_objects=objects)


def check_assembly(assembly, ctx):
    """Guard an untrusted assembly, including outputs supplied via --assembly."""
    supplier = assembly.get('bit_supplier')
    require(type(supplier) is dict, 'missing bit_supplier')
    for name, expected in ctx['supplier'].items():
        require(name in supplier and same(supplier[name], expected), 'bit_supplier.' + name)
    require(assembly['input_sha256']['package:inputs/PR589-EXPECTED.json'] == ctx['record_sha256'],
            'assembly bit input digest')
    nine = ctx['record']['nine']
    require(same(assembly['bit_lower'], nine['bit_lower']), 'assembly bit endpoint')
    require(same(assembly['bit_decimal'], nine['bit_lower_decimal']), 'assembly bit decimal')
    require(assembly['surcharge_model']['bit'] is True, 'bit bad-residue surcharge')
    return ctx['derived']['derived_deficit']


def check_bit_result(result, ctx):
    """Bind the priced fields; intentionally make no execution-authentication claim."""
    expected = dict(R=ctx['record']['word']['R'], stages=9, replicas=32,
                    bit_lower=ctx['record']['nine']['bit_lower'],
                    bit_lower_decimal=ctx['record']['nine']['bit_lower_decimal'],
                    bit_profile=ctx['record']['nine']['profile'], bit=ctx['record']['nine']['bit'])
    for name, value in expected.items():
        require(name in result and same(result[name], value), 'bit result: ' + name)
    return True
