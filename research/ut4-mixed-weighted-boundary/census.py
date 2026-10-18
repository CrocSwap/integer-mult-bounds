#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Extend Nick Petalas's PR2175 census to its two open weighted-cost splits.

The profile-screen method is Aaron Wang's PR1690; concrete gap reconstruction
and the retained quotient/group routines are Nick Petalas's PR2175. The new
domains have one five-call outer side. No search heuristic or symmetry quotient
is used. All accepted endpoints would require full formal equality; this census
rejects every candidate already in a necessary quotient.
"""
from collections import defaultdict
from hashlib import sha256
from itertools import combinations_with_replacement, product
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load():
    source = json.loads((HERE / 'SOURCES.json').read_text())
    vendor = source['vendor']
    require(sha256((HERE / vendor['path']).read_bytes()).hexdigest() == vendor['sha256'],
            'predecessor source hash')
    for entry in source['files']:
        if entry['usage'] == 'input':
            require(sha256((ROOT / entry['path']).read_bytes()).hexdigest() == entry['sha256'],
                    'proof input hash: ' + entry['path'])
    spec = importlib.util.spec_from_file_location('ut4_retained_2175', HERE / vendor['path'])
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result, source


def catalogue(P, count):
    require(count in (4, 5), 'outer census domain')
    result = defaultdict(list)
    zeros = 0
    positions = tuple(combinations_with_replacement(range(6), count))
    for ns in product(P.COUPLINGS, repeat=count):
        if P.total(ns):
            continue
        zeros += 1
        for slots in positions:
            sums = [0] * 6
            for n, gap in zip(ns, slots):
                sums[gap] ^= n
            profile, running = [], 0
            for j in range(5):
                running ^= sums[j]
                profile.append(running)
            result[tuple(profile)].append((ns, slots))
    return dict(result), zeros


def run(P, progress=False):
    catalogues, inventories = {}, {}
    for count in (4, 5):
        cat, zeros = catalogue(P, count)
        catalogues[count] = cat
        inventories[str(count)] = dict(zero_sequences=zeros, profiles=len(cat),
                                       realizations=sum(map(len, cat.values())))
    profiles = {n: tuple(sorted(cat)) for n, cat in catalogues.items()}
    domains = {'4,5,4': (4, 4), '5,5,4': (5, 4), '4,5,5': (4, 5)}
    counts = {key: dict(middles=0, a_pass=0, c_pass=0, key_pairs=0,
                       profile_pairs=0, words=0, q_pass=0) for key in domains}
    digests = {key: sha256() for key in domains}
    failures = {key: defaultdict(int) for key in domains}
    planted = {}
    for middle in product(P.COUPLINGS, repeat=5):
        if P.total(middle):
            continue
        a4, c4 = P.screened_profiles(middle, profiles[4])
        a5, c5 = P.screened_profiles(middle, profiles[5])
        for key, a, c in (('4,5,4', a4, c4), ('5,5,4', a5, c4), ('4,5,5', a4, c5)):
            na, nc = domains[key]
            counter = counts[key]
            counter['middles'] += 1
            counter['a_pass'] += sum(map(len, a.values()))
            counter['c_pass'] += sum(map(len, c.values()))
            for ka, kc in P.compatible_keys(a, c):
                counter['key_pairs'] += 1
                for pa, pc in product(a[ka], c[kc]):
                    counter['profile_pairs'] += 1
                    for ra, rc in product(catalogues[na][pa], catalogues[nc][pc]):
                        for word in P.expanded_words(middle, ra, rc):
                            image = P.quotient(word)
                            counter['words'] += 1
                            different = [s for s in P.BASIS if image.get(s, 0) != P.TARGET.get(s, 0)]
                            require(bool(different), 'unexpected quotient survivor: ' + key)
                            failures[key][different[0]] += 1
                            digests[key].update(P.canonical([word, sorted(image.items())]) + b'\n')
                            if key not in planted:
                                planted[key] = dict(word=word, middle=middle,
                                                    a_profile=pa, c_profile=pc,
                                                    a_realization=ra, c_realization=rc,
                                                    quotient=sorted(image.items()))
        if progress and counts['4,5,4']['middles'] % 900 == 0:
            print('Checked middle sequences:', counts['4,5,4']['middles'], flush=True)
    for key in domains:
        counts[key]['expanded_transcript_sha256'] = digests[key].hexdigest()
        counts[key]['first_differing_coefficient'] = dict(sorted(failures[key].items()))
    return dict(outer_catalogues=inventories, domains=counts, planted_reconstruction_controls=planted)
