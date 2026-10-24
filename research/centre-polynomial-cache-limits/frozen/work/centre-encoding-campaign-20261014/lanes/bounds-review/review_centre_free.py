"""Review the centre-free word by an exact transpose replay."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import io
import json
import subprocess
import tarfile

BASE = 'bce54fb3f895cbe5cd4c0eb477c3afeed100190f'
ARCHIVE = 'research/community-frontier1042-audit/selected-replay.tar.gz'
ARCHIVE_HASH = '22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754'
WORD_HASH = '4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c'
PROGRAM_HASH = '9f41d53659e9be84e20c661560c5687abbf5cd0660cdecbe01ad5eb29e6b8ee3'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load_source(repo):
    proc = subprocess.Popen(['git', 'show', BASE + ':' + ARCHIVE], cwd=repo, stdout=subprocess.PIPE)
    digest = sha256()
    while chunk := proc.stdout.read(65536):
        digest.update(chunk)
    require(proc.wait() == 0 and digest.hexdigest() == ARCHIVE_HASH, 'archive pin')
    proc = subprocess.Popen(['git', 'show', BASE + ':' + ARCHIVE], cwd=repo, stdout=subprocess.PIPE)
    payload = {}
    with tarfile.open(fileobj=proc.stdout, mode='r|gz') as archive:
        for item in archive:
            if item.name in ('slots/local/CANONICAL-WORD.json.gz', 'slots/local/LOCAL-PROGRAMS.json.gz'):
                payload[item.name] = gzip.decompress(archive.extractfile(item).read())
    require(proc.wait() == 0, 'source extraction')
    word_raw = payload['slots/local/CANONICAL-WORD.json.gz']
    program_raw = payload['slots/local/LOCAL-PROGRAMS.json.gz']
    require(sha256(word_raw).hexdigest() == WORD_HASH, 'word pin')
    require(sha256(program_raw).hexdigest() == PROGRAM_HASH, 'program pin')
    return json.loads(word_raw), program_raw


def index(register):
    require(register[0] in ('L', 'C'), 'register kind')
    return register[1] + (704 if register[0] == 'C' else 0)


def scalar(event):
    gate = event[1]
    tag, target = gate[0], index(gate[1])
    if tag == 'clear':
        return tag, target, -1, Q(0)
    if tag == 'scale':
        return tag, target, -1, Q(gate[2], gate[3])
    require(tag in ('add', 'copy'), 'scalar kind')
    return tag, target, index(gate[2]), Q(1) if tag == 'copy' else Q(gate[3], gate[4])


def plus(target, source, scale):
    for j, v in source.items():
        z = target.get(j, Q(0)) + scale*v
        if z:
            target[j] = z
        else:
            target.pop(j, None)


def transpose(program, size=712):
    cols = [{i: Q(1)} for i in range(size)]
    for tag, target, source, coef in reversed(program):
        if tag == 'clear':
            cols[target] = {}
        elif tag == 'scale':
            cols[target] = {j: coef*v for j, v in cols[target].items() if coef*v}
        else:
            plus(cols[source], cols[target], coef)
            if tag == 'copy':
                cols[target] = {}
    return cols


def clean_rows(old, word):
    prefix = [scalar(e) for e in old[:old.index(['phase', 'centers'])] if e[0] == 'scalar']
    rows = []
    for centre in word['centers']:
        row = {centre: Q(1)}
        for tag, target, source, coef in reversed(prefix):
            x = row.get(target, Q(0))
            if tag == 'clear':
                row.pop(target, None)
            elif tag == 'scale':
                if coef*x:
                    row[target] = coef*x
                else:
                    row.pop(target, None)
            else:
                value = row.get(source, Q(0)) + coef*x
                if value:
                    row[source] = value
                else:
                    row.pop(source, None)
                if tag == 'copy':
                    row.pop(target, None)
        rows.append([row.get(j, Q(0)) for j in range(112)])
    require([[sum(a*b for a, b in zip(r, s)) for s in rows] for r in rows]
            == [[Q(56 if i == j else 0) for j in range(8)] for i in range(8)], 'independent R Gram')
    return rows


def check_frames(events, word):
    frames = word['start'].copy() + [None]*8
    live = set()
    peak = 0
    for event in events:
        if event[0] == 'center':
            raise ValueError('a centre child remains')
        if event[0] == 'climb':
            require(frames[event[2]] == event[3], 'climb entry')
            frames[event[2]] = event[4]
        if event[0] != 'scalar':
            continue
        tag, target, source, coef = scalar(event)
        frame = event[2]
        if tag == 'clear':
            frames[target] = frame
            live.discard(target)
        else:
            require(frames[target] == frame, 'scalar target frame')
            if source >= 0:
                require(frames[source] == frame, 'scalar source frame')
            if target >= 704:
                live.add(target)
                peak = max(peak, len(live))
    require(frames[:704] == word['final'], 'persistent final frames')
    require(frames[704:] == [0]*8 and not live, 'private final frames and lifetime')
    return peak


def one_vector(gates, source, omit):
    state = [Q(0)]*712
    state[source] = Q(1)
    for site, (tag, target, arg, coef) in enumerate(gates):
        if site == omit:
            continue
        if tag == 'clear':
            state[target] = Q(0)
        elif tag == 'scale':
            state[target] *= coef
        elif tag == 'copy':
            state[target] = state[arg]
        else:
            state[target] += coef*state[arg]
    return state


def review(repo, changed, orientation):
    word, raw = load_source(repo)
    old = json.loads(raw)[orientation]
    del raw
    # Derive R from the selected forward word, regardless of the reviewed direction.
    if orientation == 'forward':
        R = clean_rows(old, word)
    else:
        _, raw = load_source(repo)
        R = clean_rows(json.loads(raw)['forward'], word)
        del raw
    raw = gzip.decompress(changed.read_bytes())
    changed_hash = sha256(raw).hexdigest()
    new = json.loads(raw)[orientation]
    del raw
    native = lambda events: [e for e in events if e[0] in ('climb', 'adapter', 'residual_adapter')]
    old_native, new_native = native(old), native(new)
    require(old_native == new_native, 'persistent native stream changed')
    native_hash = sha256(json.dumps(new_native, separators=(',', ':')).encode()).hexdigest()
    old_paid = Counter(e[5] for e in old if e[0] == 'climb')
    old_paid.update(e[4] for e in old if e[0] == 'center')
    new_paid = Counter(e[5] for e in new if e[0] == 'climb')
    require(old_paid - new_paid == {8: 8} and not new_paid - old_paid, 'paid centre difference')
    peak = check_frames(new, word)
    require(peak == 1, 'private peak')
    J = [[Q(i == j) - sum(r[i]*r[j] for r in R)/4 for j in range(112)] for i in range(112)]
    gates = [scalar(e) for e in new if e[0] == 'scalar']
    del new, old, new_native, old_native, word
    actual = transpose(gates)
    for j, column in enumerate(actual):
        expected = {j: Q(1)} if j < 704 else {}
        if orientation == 'forward' and j < 112:
            expected.update({112+i: J[i][j] for i in range(112) if J[i][j]})
        if orientation == 'backward' and 112 <= j < 224:
            expected.update({i: -J[j-112][i] for i in range(112) if J[j-112][i]})
        require(column == expected, 'transpose column ' + str(j))
    first_clear = next(i for i, e in enumerate(gates) if e[:2] == ('clear', 704))
    bad_private = one_vector(gates, 704, first_clear)
    require(any(bad_private[:704]), 'private clear control')
    first_add = next(i for i in range(first_clear, len(gates)) if gates[i][0] == 'add')
    source = gates[first_add][2]
    correct = one_vector(gates, source, -1)
    bad_add = one_vector(gates, source, first_add)
    require(correct != bad_add, 'dirty correction control')
    return {
        'status': 'PASS_INDEPENDENT_TRANSPOSE_CENTRE_FREE_INTERFACE',
        'orientation': orientation,
        'base': BASE,
        'archive_sha256': ARCHIVE_HASH,
        'changed_payload_sha256': changed_hash,
        'full_columns': 712,
        'full_rows': 712,
        'persistent_native_events': 5056,
        'persistent_native_stream_sha256': native_hash,
        'removed_paid_profile': {'8': 8},
        'remaining_paid_profile': dict(sorted(new_paid.items())),
        'private_peak_live': peak,
        'negative_controls': ['omit first private clear', 'omit first dirty correction add'],
        'scope': 'Exact scalar and common-frame lift premises. No physical owner/controller or recursive supplier admission.',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--changed', type=Path, required=True)
    parser.add_argument('--orientation', choices=('forward', 'backward'), required=True)
    args = parser.parse_args()
    print(json.dumps(review(args.repo, args.changed, args.orientation), indent=2))
