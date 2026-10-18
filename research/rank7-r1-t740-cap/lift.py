#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Deterministic T740 allocation of PR #2979's unchanged words.

The allocation is defined by three things only:
  1. PR #2979's literal T74 allocation (research/rank7-joint-endframes/allocation: ORDER, DISPATCH, FILL);
  2. ten lockstep copies of it, in Dugongue's PR #2969 lift convention:
       call (s, r) at T74 time t  ->  call (s, r + 74 j) at T740 time 10 t + j      (j = 0..9),
       role (t, h, o, c, p, z)     ->  role (10 t + j, h, o + 74 j, c, p, z);
  3. allocation/RELOCATIONS.json: 332 roles [time, helper, owner_replica, child, port], each moved to the given bin.
Every bin that a relocated role leaves or enters is repacked as a compact prefix in (time, helper) order; no other row
changes. Standard library only. Columns of FILL rows: time, helper, owner_replica, child, port, offset.

Rohan Arun, with substantial AI assistance (Anthropic Claude). Apache-2.0.
"""
import gzip
import hashlib
import json
from collections import defaultdict
from pathlib import Path

COPIES = 10
SOURCE_T = 74
METHOD = ('PR2979 literal T74 fill lifted to ten lockstep copies (PR2969 convention, T740) plus 332 explicit whole-role '
          'relocations (allocation/RELOCATIONS.json); touched bins repacked as compact prefixes in (time, helper) order')


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw)


def canonical(obj):
    """Canonical JSON payload bytes; SHA-256 pins refer to these bytes (not to any gzip container)."""
    return (json.dumps(obj, sort_keys=True, separators=(',', ':')) + '\n').encode()


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def lift_order(order74):
    return [[s, r + SOURCE_T * j] for s, r in order74 for j in range(COPIES)]


def lift_dispatch(dispatch74):
    return [[s, r + SOURCE_T * j, p] for s, r, p in dispatch74 for j in range(COPIES)]


def lift_rows(fill74):
    return [[COPIES * t + j, h, o + SOURCE_T * j, c, p, z] for t, h, o, c, p, z in fill74['rows'] for j in range(COPIES)]


def build(source_allocation, relocations, providers):
    """Return (T, order, dispatch, fill, touched_bins). `providers` maps provider id -> {'widths': [...]}."""
    source = Path(source_allocation)
    order74, dispatch74, fill74 = read(source / 'ORDER.json'), read(source / 'DISPATCH.json'), read(source / 'FILL.json.gz')
    need(fill74['columns'] == ['time', 'helper', 'owner_replica', 'child', 'port', 'offset'], 'source fill columns')
    need(len(order74) == 9 * SOURCE_T and len(dispatch74) == 9 * SOURCE_T, 'source T74 order/dispatch')
    T = SOURCE_T * COPIES
    order, dispatch, rows = lift_order(order74), lift_dispatch(dispatch74), lift_rows(fill74)
    provider_of = {(s, r): p for s, r, p in dispatch}
    where = {(row[0], row[1]): i for i, row in enumerate(rows)}
    need(len(where) == len(rows), 'unique (time, helper) roles')
    touched, moved = set(), set()
    for entry in relocations:
        need(len(entry) == 5 and all(type(x) is int for x in entry), 'relocation shape [time, helper, owner, child, port]')
        t, h, o, c, p = entry
        need((t, h) in where and (t, h) not in moved, 'relocated role exists and moves once')
        moved.add((t, h))
        row = rows[where[t, h]]
        old = (row[2], row[3], row[4])
        need(old != (o, c, p), 'a relocation changes the bin')
        touched.add(old)
        touched.add((o, c, p))
        row[2], row[3], row[4] = o, c, p
    members = defaultdict(list)
    for i, row in enumerate(rows):
        key = (row[2], row[3], row[4])
        if key in touched:
            members[key].append(i)
    for key, ids in members.items():
        offset = 0
        for i in sorted(ids, key=lambda k: (rows[k][0], rows[k][1])):
            rows[i][5] = offset
            offset += providers[provider_of[tuple(order[rows[i][0]])]]['widths'][rows[i][1]]
    rows.sort()
    fill = {'columns': list(fill74['columns']), 'dispatch_overrides': [], 'method': METHOD, 'rows': rows}
    return T, order, dispatch, fill, touched


def write(out, T, order, dispatch, fill, profile):
    """Write the T740 allocation in PR2979's layout (gzip mtime 0) and return the canonical payload SHA-256 values."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    payloads = {'ORDER.json': order, 'DISPATCH.json': dispatch, 'FILL.json.gz': fill,
                'PROFILE.json': {str(r): n for r, n in sorted(profile.items())}}
    for name, obj in payloads.items():
        data = canonical(obj)
        (out / name).write_bytes(gzip.compress(data, mtime=0) if name.endswith('.gz') else data)
    return {name: digest(obj) for name, obj in payloads.items()}
