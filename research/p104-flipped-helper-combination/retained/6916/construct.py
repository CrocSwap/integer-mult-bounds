"""Deterministic witnessed helper splits; no candidate search is trusted.

Ali Romman's helper-basis mechanism, extended by @CubeJerry with substantial
OpenAI assistance. Apache-2.0. See PROOF.md and SOURCE-PINS.json.
"""
from copy import deepcopy
import gzip
import json
from pathlib import Path
import sys
from linear import HERE, canonical, digest, need, read, replay
from split import split


def construct(word, hit):
    """Prepare optional paid retiming, then check and split an independent cut."""
    hit = deepcopy(hit)
    cut = hit['cut']
    removed, before, after = set(), [], []
    for path in hit['paths']:
        r, old, new, frame = (path[k] for k in ('role', 'old', 'new', 'frame'))
        need(frame == hit['frame'], 'Retiming target frame')
        need(path['lo'] <= cut <= path['hi'], 'Cut lies in contact-free window')
        for index in range(path['lo'], path['hi']):
            e = word['program'][index]
            need(e[0] == 'MOVE' or (e[1] != r and not (e[0] in ('ADD', 'COPY') and e[2] == r)),
                 ('No scalar contact during retiming', index, r))
        for index in path['moves']:
            e = word['program'][index]
            need(e[0] == 'MOVE' and e[1] == r, 'Retimed source MOVE')
            need(index not in removed, 'No duplicate removed MOVE')
            removed.add(index)
        if old != frame:
            before.append(['MOVE', r, old, frame, path['private']])
        if frame != new:
            after.append(['MOVE', r, frame, new, path['private']])
    prefix = [e for i, e in enumerate(word['program'][:cut]) if i not in removed] + before
    suffix = after + [e for i, e in enumerate(word['program'][cut:], start=cut) if i not in removed]
    prepared = deepcopy(word)
    prepared['program'] = prefix + suffix
    witness = {k: hit[k] for k in ('frame', 'pivot', 'ranks', 'a', 'b', 'c', 'd')}
    if 'basis_version' in hit:
        witness['basis_version'] = hit['basis_version']
    witness['cut_after'] = len(prefix) - 1
    return split(prepared, witness), witness


def regenerate(witnesses, verify_each=True):
    source = read(HERE / 'retained/data/word.json.gz')
    current = source
    checks = []
    for index, entry in enumerate(witnesses, 1):
        need(digest(current) == entry['source_payload_sha256'], ('Frozen step input', index))
        current, actual_cut = construct(current, entry['witness'])
        need(actual_cut == entry['prepared_split'], ('Reconstructed split cut', index))
        need(digest(current) == entry['payload_sha256'], ('Frozen step output', index))
        if verify_each:
            checks.append(replay(current, source))
    return current, checks


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', nargs='?')
    parser.add_argument('--steps', type=int)
    args = parser.parse_args()
    witnesses = read(HERE / 'WITNESSES.json')
    if args.steps is not None:
        need(1 <= args.steps <= len(witnesses), 'Recorded prefix length')
        witnesses = witnesses[:args.steps]
    result, checks = regenerate(witnesses)
    if args.output:
        Path(args.output).write_bytes(gzip.compress(canonical(result), mtime=0))
    print(json.dumps({'steps': len(checks), 'payload_sha256': digest(result), 'native': checks[-1]}, sort_keys=True))
    print('PASS_REGENERATED_HELPER_SPLITS')
