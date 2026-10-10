"""Source-bound composition of PR223, PR211's frames, and compatible PR217 butterflies.

Apache-2.0. Developed with OpenAI Codex assistance. See NOTICE.md for predecessors.
"""
import base64
import copy
import gzip
import hashlib
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

PINS = {
    'bit': 'a1175449f34d39ff933d9d8ab23ced1f32b290ec',
    'complex': '187e1010ac8b259af8e9b5166f68b64bc27b4b47',
    'served': '8786fec0148a41409874cad133123da227d93751',
    'frames': 'b739fc226a54a4a507989aa1bef092d491287451',
}
BIT_PACKAGE = Path('research/paired-cube-diagonal-bit-168')
SERVED_PACKAGE = Path('research/served-diagonal-bit')
FRAMES_PACKAGE = Path('research/butterfly-coordinated-bit-211')
BACKEND = Path('references/pr168-v4/research/paired-cube-bit/check_paired_cube_bit.py')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def check_sources(roots):
    """Bind sources to full commits and reject modified/deleted tracked files."""
    for name, commit in PINS.items():
        root = roots[name]
        head = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
        assert head == commit, ('wrong dependency commit', name, head)
        subprocess.run(['git', '-C', str(root), 'diff', '--exit-code', '--quiet', 'HEAD', '--'], check=True)


def construct(roots, output):
    """Emit the complete effective inputs; admit them through a fresh Candidate instance."""
    bit = roots['bit'] / BIT_PACKAGE
    served = roots['served'] / SERVED_PACKAGE
    frames = roots['frames'] / FRAMES_PACKAGE
    adapter = load('served_composition_adapter', served / 'bit/served_word.py')
    word = adapter.Candidate(bit, served / 'selected/served')
    original = json.loads((bit / 'selected/bit/word_p12.json').read_bytes())
    old_ops, new_ops = original['ops'], word.ops
    # Source-copy nodes repeat, so greedy node matching would be ambiguous.
    # No composite operation is deleted: align those first, then identify each
    # deleted control by its surviving served consumer, and compact exactly.
    old_composites = [(i, op) for i, op in enumerate(old_ops) if op[2] >= word.v]
    new_composites = [(i, op) for i, op in enumerate(new_ops) if op[2] >= word.v]
    assert len(old_composites) == len(new_composites)
    removed_roles = set()
    for (oi, old), (ni, new) in zip(old_composites, new_composites):
        assert old[2] == new[2], 'composite sequence changed'
        if ni in word.served:
            assert new[1] == -1-word.served[ni][0]
            removed_roles.add(old[1])
    removed_ops = [i for i, (a, b, n) in enumerate(old_ops) if a in removed_roles]
    assert len(removed_ops) == len(removed_roles) == 373
    removed_set = set(removed_ops)
    mapping = {old: new for new, old in enumerate(i for i in range(len(old_ops)) if i not in removed_set)}
    rmap = {old: new for new, old in enumerate(i for i in range(word.R+373) if i not in removed_roles)}
    assert len(mapping) == len(new_ops)
    for old, new in mapping.items():
        a, b, n = old_ops[old]
        control = -1-word.served[new][0] if new in word.served else rmap[b]
        assert new_ops[new] == [rmap[a], control, n], 'inexact compact operation map'
        assert original['op_frame'][old] == word.opframe[new], 'unexplained frame change before composition'
    assert len(removed_roles) == 373 and not removed_roles.intersection(rmap)
    assert removed_roles | set(rmap) == set(range(word.R + 373))
    for i in removed_ops:
        a, b, n = old_ops[i]
        assert n < word.v and a in removed_roles and b in rmap
        uses = [j for j, (x, y, _) in enumerate(old_ops) if x == a or y == a]
        assert len(uses) == 2 and uses[0] == i
        consumer = mapping[uses[1]]
        assert consumer in word.served and old_ops[uses[1]][1] == a
        assert word.served[consumer][0] == n

    raw = gzip.decompress(base64.b64decode((frames / 'opframe-bases.json.gz.b64').read_bytes()))
    assert sha(raw) == '56b2ed0f6b867e8cafdc32ac70419cfda36d02838844572098b3fc77f8026e58'
    leader = json.loads(raw)
    assert len(leader) == len({i for i, _ in leader}) == 6191
    overlaps = []
    for old, basis in leader:
        assert old in mapping, 'refinement touches a deleted operation'
        i = mapping[old]
        f = word.register(basis)
        word.opframe[i] = f
        if i in word.served:
            d, old_frame = word.served[i]
            word.served[i] = (d, f)
            entry = next(e for e in word.k['entries'] if e['passive'] == d)
            entry['passive_chain'][2] = f
            overlaps.append(dict(original_operation=old, operation=i, passive=d,
                                 previous_frame=old_frame, refined_frame=f))
    assert len(overlaps) == 1

    overlay_raw = (frames / 'butterfly-overlay.json').read_bytes()
    assert sha(overlay_raw) == 'ca66a9c3d8f3a29dc805dc89306f0b23b8e934cbbbf3a9334e7391fbbc1086ee'
    plans = json.loads(overlay_raw)['plans']
    accepted, blocked = [], []
    used = set()
    for index, plan in enumerate(plans):
        missing_roles = sorted(set(plan['roles']) - set(rmap))
        missing_ops = sorted(set(plan['operations']) - set(mapping))
        if missing_roles or missing_ops:
            blocked.append(dict(plan=index, deleted_roles=missing_roles, deleted_operations=missing_ops))
            continue
        i, j, k = [mapping[o] for o in plan['operations']]
        a, b, c, d = [rmap[r] for r in plan['roles']]
        assert word.ops[i][:2] == [a, d] and word.ops[j][:2] == [b, c]
        assert word.ops[k][:2] == [a, b]
        assert not used.intersection((a, b, c, d)), 'overlapping butterfly rewrites'
        used.update((a, b, c, d))
        word.ops[i][1], word.ops[j][1] = c, d
        for op, n, args, basis in zip((i, j), plan['pair_nodes'], plan['new_pair_source_args'], plan['new_pair_frames']):
            assert word.ops[op][2] == n
            word.g['args'][n] = args
            f = word.register(basis)
            word.opframe[op] = f
            word.w['node_frame'][str(n)] = f
        accepted.append(index)
    assert len(accepted) == 67 and len(blocked) == 373
    assert all(len(p['deleted_roles']) == 1 and not p['deleted_operations'] for p in blocked)
    assert {p['deleted_roles'][0] for p in blocked} == removed_roles

    word.w['op_frame'] = word.opframe[:]
    word.w['served'] = [[i, d, f] for i, (d, f) in sorted(word.served.items())]
    complete_frames = copy.deepcopy(word.C.fr)
    for f, basis in word.C.B.items():
        if str(f) not in complete_frames['frames']:
            complete_frames['frames'][str(f)] = dict(b=[list(row) for row in basis], dim=len(basis))
    selected = output / 'selected/bit'
    selected.mkdir(parents=True)
    payloads = {
        'graph_p12.json': canonical(word.g),
        'word_p12.json': canonical(word.w),
        'frames_p12.json': canonical(complete_frames),
        'kchron_p12.json': canonical(word.k),
        # Only R and the inherited deficit/loss are inputs. The actual profile is recounted.
        'profile_p12.json': canonical(word.C.prof),
    }
    for name, data in payloads.items():
        (selected / name).write_bytes(data)
        if name in ('word_p12.json', 'frames_p12.json'):
            (selected / (name + '.gz')).write_bytes(gzip.compress(data, mtime=0))
    (output / BACKEND).parent.mkdir(parents=True)
    shutil.copyfile(bit / BACKEND, output / BACKEND)
    # Re-reading the emitted program revalidates role/operation chronology and all aliases.
    fresh = adapter.Candidate(output, selected)
    assert fresh.ops == word.ops and fresh.opframe == word.opframe and fresh.served == word.served
    metadata = dict(frame_refinements=len(leader), served_operations=len(fresh.served),
                    served_frame_overlaps=overlaps, butterflies=accepted, blocked_butterflies=blocked,
                    first_butterfly_operations=[mapping[o] for o in plans[accepted[0]]['operations']],
                    deleted_operations=removed_ops, deleted_roles=sorted(removed_roles),
                    emitted_sha256={name: sha(data) for name, data in payloads.items()})
    return fresh, metadata
