"""Read-only source binding and typed lifetime gates, not scientific execution."""
from pathlib import Path
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent
SOURCE = {
    'repository': 'CubeJerry/integer-mult-bounds',
    'commit': '172f4535ce8dcff79f626410af845f757c1563be',
    'path': 'research/literal-native-quadratic-phase/reference/selected-native.json.gz',
    'blob': '74563a7867d9d762b6588f65362369668841bb3e',
    'bytes': 350722,
    'sha256': '2b94953dc14a122e3ef089633f05b58ec689ec5156feb7c784ed3e137dc01883',
    'canonical_word_sha256': '91429a6b96729292a8764836e00c87a6f7cd3b76f05159033f4867f69a98d097',
}
EXPECTED = [
    (28037, ['INIT', 1526, 601]),
    (28041, ['ADD', 1526, 1349, '-1', 601]),
    (28129, ['ADD', 1526, 728, '-1', 601]),
    (28135, ['ADD', 1526, 729, '-1', 601]),
    (28139, ['ADD', 1526, 730, '-1', 601]),
    (28141, ['MOVE', 1526, 601, 470, True]),
    (28159, ['ADD', 1515, 1526, '1', 470]),
    (37618, ['CLEAR', 1526, 470]),
]

def need(ok, message):
    if not ok:
        raise ValueError(message)

def read_source(path=None):
    raw = (Path(path) if path else HERE/'inputs/selected-native.json.gz').read_bytes()
    need(len(raw) == SOURCE['bytes'] and hashlib.sha256(raw).hexdigest() == SOURCE['sha256'], 'selected archive pin')
    word = json.loads(gzip.decompress(raw))
    canonical = json.dumps(word, separators=(',', ':'), sort_keys=True).encode()
    need(hashlib.sha256(canonical).hexdigest() == SOURCE['canonical_word_sha256'], 'selected canonical word pin')
    return word

def touched(event):
    return event[1:3] if event[0] in ('ADD', 'COPY') else event[1:2]

def prefix_states(word, end):
    """Only exact frame/liveness typing; no numeric operation is interpreted."""
    frames = dict(enumerate(word['initial']))
    last_move = {}
    for index, event in enumerate(word['program'][:end]):
        op, owner = event[:2]
        if op == 'INIT':
            need(owner not in frames and owner >= word['public'], 'source INIT must open an absent owned lifetime')
            frames[owner] = event[2]
        elif op == 'CLEAR':
            need(frames.get(owner) == event[2] and owner >= word['public'], 'source CLEAR frame/lifetime')
            del frames[owner]
        elif op == 'MOVE':
            need(frames.get(owner) == event[2], 'source MOVE input frame')
            need(event[4] == (owner >= word['public']), 'source MOVE ownership flag')
            frames[owner] = event[3]
            last_move[owner] = index
        elif op in ('ADD', 'COPY'):
            need(frames.get(owner) == event[4] == frames.get(event[2]), 'source binary current frames')
        elif op == 'SCALE':
            need(frames.get(owner) == event[3], 'source SCALE current frame')
        else:
            raise ValueError('unknown source opcode')
    return frames, last_move

def bind_init(word, index=28037, owner=1526, donor=0, frame=601):
    need(word['program'][index] == ['INIT', owner, frame], 'binding is not the exact source INIT')
    need(owner != donor, 'donor/owned alias')
    current, last_move = prefix_states(word, index)
    need(owner not in current, 'owned lifetime already open')
    need(donor in current, 'header donor is not live')
    return {'index': index, 'owner': owner, 'donor': donor, 'frame': frame,
            'donor_last_MOVE': last_move.get(donor),
            'donor_frame': current[donor],
            'donor_frame_columns': word['frames'][current[donor]],
            'donor_public': donor < word['public']}

def audit():
    word = read_source()
    got = [(i, e) for i, e in enumerate(word['program']) if 1526 in touched(e)]
    need(got == EXPECTED, 'selected bank1526 full contact projection')
    binding = bind_init(word)
    at_init, moves = prefix_states(word, 28037)
    need(at_init[1349] == 3 and word['program'][28039] == ['MOVE', 1349, 3, 601, False], 'different-frame donor source fact changed')
    # Zero is invariant under every linear frame; frame3 is valid HEADER supply.
    different_frame_donor = bind_init(word, donor=1349)
    # Bind every selected contact in its genuine chronology, not a static-frame projection.
    for i, event in EXPECTED[1:]:
        current, _ = prefix_states(word, i)
        if event[0] == 'ADD':
            need(current[event[1]] == event[4] == current[event[2]], 'actual scalar contact frames')
        else:
            need(current[event[1]] == event[2], 'actual MOVE/CLEAR input frame')
    controls = []
    for label, kwargs in (
        ('wrong_INIT_frame', {'frame': 470}),
        ('inactive_owned_donor', {'donor': 1515}),
        ('donor_owned_alias', {'donor': 1526}),
        ('wrong_INIT_index', {'index': 28039}),
    ):
        try:
            bind_init(word, **kwargs)
        except ValueError:
            controls.append(label)
        else:
            raise ValueError('source negative control accepted: ' + label)
    # Audit every actual INIT using public donor0.  These are finite source
    # lifetimes, not a physical execution of all native operations.
    inits = [(i, e) for i, e in enumerate(word['program']) if e[0] == 'INIT']
    clears = [(i, e) for i, e in enumerate(word['program']) if e[0] == 'CLEAR']
    inventory = []
    counts = {}
    for i, event in inits:
        _, owner, frame = event
        b = bind_init(word, index=i, owner=owner, donor=0, frame=frame)
        matching = next((j for j, e in clears if j > i and e[1] == owner), None)
        need(matching is not None, 'unretired actual owned lifetime')
        need(not any(i < j < matching and e[1] == owner for j, e in inits), 'overlapping raw owned lifetimes')
        counts[owner] = counts.get(owner, 0)+1
        b.update(clear_index=matching, ordinal_for_raw_owner=counts[owner]-1)
        inventory.append(b)
    need(len(inventory) == 54 and len(counts) == 51, 'actual lifetime/label inventory changed')
    need(all(0 not in touched(e) for _, e in clears), 'public donor was cleared')
    need(all(all(0 < a < 512 for a in frame) for frame in word['frames']), 'native nine-coordinate frame labels')
    end_frames, _ = prefix_states(word, len(word['program']))
    need(set(end_frames) == set(range(word['public'])), 'full word did not restore exactly its public lifetime set')
    # Frame covariance applies to zero initialization only.  A nonzero scalar
    # contact still must match the exact current charts.
    changed = dict(word)
    changed['program'] = word['program'].copy()
    changed['program'][28041] = ['ADD', 1526, 1349, '-1', 470]
    try:
        prefix_states(changed, 28042)
    except ValueError:
        controls.append('wrong_nonzero_scalar_contact_frame')
    else:
        raise ValueError('wrong scalar contact frame accepted')
    changed['program'] = word['program'].copy()
    changed['program'][28129] = ['INIT', 1526, 601]
    try:
        bind_init(changed, index=28129, owner=1526, donor=0, frame=601)
    except ValueError:
        controls.append('overwrite_live_owned_lifetime')
    else:
        raise ValueError('live owned contents offered to inactive INIT')
    interleaved = [28127, 28131, 28133, 28137, 28153, 28161, 28165]
    return {'source': SOURCE, 'program_length': len(word['program']),
            'bank1526_contacts': got, 'INIT_binding': binding,
            'frames_at_INIT': {str(k): at_init[k] for k in (728, 729, 730, 1349)},
            'interleaving_witnesses': [(i, word['program'][i]) for i in interleaved],
            'different_frame_donor_accepted': different_frame_donor,
            'all_INIT_lifetimes': inventory,
            'owned_labels': len(counts), 'historical_owned_lifetimes': len(inventory),
            'reused_raw_labels': {str(k): v for k, v in counts.items() if v > 1},
            'common_format_boundary': 'all packets in the supplied raw-native invocation share f,r,P,S,w,c and grid; source word alone contains no Gamma6 producer',
            'controls': controls, 'scope': 'all exact INIT lifetime bindings; no numerical full-word execution or root format producer'}
