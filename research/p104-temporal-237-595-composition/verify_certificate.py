"""Check literal path translation, guarded pairing and every emitted byte."""
from collections import defaultdict
from hashlib import sha1, sha256
from pathlib import Path
import argparse
import gzip
import json
import sys
import tarfile
sys.path.insert(0, str(Path(__file__).resolve().parent))
from source import HERE, canonical, frozen, need, read, sources
from certificate import check, controls, observe
from construct import construct, scalar_width


def common_word(parent):
    pin = read(parent/'INPUTS.json')
    path = pin['prefix']+'/WORD.json.gz'
    row = next(x for x in pin['files'] if x['path'] == path)
    with tarfile.open(parent/pin['archive']) as tar:
        packed = tar.extractfile(path).read()
    need(sha256(packed).hexdigest() == row['sha256']
         and sha1(b'blob '+str(len(packed)).encode()+b'\0'+packed).hexdigest() == row['git_blob'],
         'Exact common #7145 word')
    return json.loads(gzip.decompress(packed))


def translated_paths(common, source, peer_hit, peer_paths, parent_hit, hit, paths):
    n = common['public']
    need(source['public'] == n+1 and source['frames'] == common['frames'], 'Literal common chart catalogue')
    need((hit['frame'], hit['pivot'], hit['ranks']) == (237, 1082, [4, 5]), 'Exact scoped helper')
    need((source['initial'][1082], source['final'][1082]) == (3, 127), 'Actual helper group')
    need((hit['path']['old'], hit['path']['new'], hit['path']['role']) == (734, 127, 820), 'Exact paid route')
    need(len(peer_paths) == len(paths) == 8, 'Eight neutral path brackets')
    need(peer_hit['cut'] == peer_paths[0]['lo'] and hit['cut'] == paths[0]['lo'], 'Cut follows first gather bracket')

    def map_event(event, time):
        out = event.copy()
        for k in (1, 2) if event[0] in ('ADD', 'COPY') else (1,):
            r = event[k]
            out[k] = n if r == parent_hit['pivot'] and time >= parent_hit['cut'] else r+(r >= n)
        return out

    old_paths, new_paths = [*peer_paths, peer_hit['path']], [*paths, hit['path']]
    # Index complete contact spans on the selected literal public roles.
    roles = {p['role'] for p in old_paths}
    seq = source['program']
    contacts = defaultdict(list)
    moves = defaultdict(list)
    for i, e in enumerate(seq):
        op, r = e[:2]
        if op == 'MOVE':
            if r in roles:
                moves[r].append(i)
        else:
            for x in (r, e[2]) if op in ('ADD', 'COPY') else (r,):
                if x in roles:
                    contacts[x].append(i)

    result = []
    for old, new in zip(old_paths, new_paths):
        r = old['role']
        need(r < n and r != parent_hit['pivot'] and new['role'] == r, 'Separate literal public role')
        a, b = old['lo'], old['hi']
        need(0 < a < b < len(common['program']) and len(old['moves']) == 1, 'One original MOVE in bounded span')
        before = map_event(common['program'][a-1], a-1)
        after = map_event(common['program'][b], b)
        step = map_event(common['program'][old['moves'][0]], old['moves'][0])
        found = []
        for lo, hi in zip(contacts[r], contacts[r][1:]):
            if seq[lo] == before and seq[hi] == after:
                middle = [i for i in moves[r] if lo < i < hi]
                if len(middle) == 1 and seq[middle[0]] == step:
                    found.append((lo+1, hi, middle))
        need(found == [(new['lo'], new['hi'], new['moves'])], 'Unique translated bracket and literal MOVE')
        result.append(dict(role=r, before=[a, b], after=[new['lo'], new['hi']], move=new['moves'][0]))

    for key in ('gathers', 'injections'):
        bound = 'lo' if key == 'gathers' else 'hi'
        need(len(peer_hit[key]) == len(hit[key]), 'Every timed recipe term retained')
        for old, new in zip(peer_hit[key], hit[key]):
            pos = old.get('path', 8)
            expected = dict(old, cut=new_paths[pos][bound])
            need(old['cut'] == old_paths[pos][bound] and new == expected, 'Only literal observation clocks translated')
    for key in ('c', 'd', 'paid_delta'):
        need(hit[key] == peer_hit[key], 'Preserved exact recipe: '+key)
    return result


def run():
    need(__debug__, 'Assertions are proof obligations')
    with sources() as (_, _, _, _, parent, source), frozen(7147) as peer:
        hit, paths = read(HERE/'WITNESS.json'), read(HERE/'PATHS.json')
        brackets = translated_paths(common_word(parent), source, read(peer/'WITNESS.json'),
                                    read(peer/'PATHS.json'), read(parent/'WITNESS.json'), hit, paths)
        snapshots = observe(source, hit)
        record = check(hit, snapshots)
        candidate = construct(source, hit, paths)
        raw = canonical(candidate)
        need(raw == gzip.decompress((HERE/'WORD.json.gz').read_bytes()), 'Every reconstructed candidate byte')
        record.update(source_sha256=sha256(canonical(source)).hexdigest(),
                      candidate_sha256=sha256(raw).hexdigest(),
                      controls=controls(source, hit, paths, snapshots),
                      neutral_paths=len(paths), paid_paths=1, brackets=brackets,
                      scalar_width=scalar_width(candidate))
        return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = run()
    if args.out:
        with args.out.open('x') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
    else:
        need(result == read(HERE/'CERTIFICATE.json'), 'Every frozen timed certificate field')
    print(result['status'], flush=True)
