# SPDX-License-Identifier: Apache-2.0
"""Shared, standard-library-only helpers for the T37 restoration-deferral note.

Nothing here imports producer, auditor or checker code from the selected
packages.  Inputs are read directly from the committed, hash-pinned replay
archives without extracting them to disk.
"""
import gzip
import hashlib
import json
import tarfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

SOURCES = json.loads((HERE / 'SOURCES.json').read_text())


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(obj):
    return json.dumps(obj, indent=1, sort_keys=True) + '\n'


def read_member(archive, member, payload_sha256):
    """Return the decompressed JSON payload of one gzip member of a pinned tar archive."""
    with tarfile.open(archive, 'r:gz') as tar:
        info = tar.getmember(member)
        require(info.isfile(), f'{member} is not a regular file')
        payload = gzip.decompress(tar.extractfile(info).read())
    require(sha256(payload) == payload_sha256, f'{member}: payload digest mismatch')
    return json.loads(payload)


def bound_member(name, template_key, member_key, container_key, payload_key, template, root=ROOT):
    """A gzip JSON member whose container digest is bound by the hosted template."""
    src = SOURCES['constructions'][name]
    with tarfile.open(Path(root) / src['archive'], 'r:gz') as tar:
        info = tar.getmember(src[member_key])
        require(info.isfile(), f'{src[member_key]} is not a regular file')
        container = tar.extractfile(info).read()
    (prov,) = template['local_providers'].values()
    require(sha256(container) == src[container_key] == prov[template_key],
            f'{name}: {src[member_key]} is not the one bound by the hosted template')
    payload = gzip.decompress(container)
    require(sha256(payload) == src[payload_key], f'{name}: {src[member_key]} payload digest mismatch')
    return json.loads(payload)


def load_canonical(name, template, root=ROOT):
    return bound_member(name, 'canonical_word_sha256', 'canonical_member', 'canonical_container_sha256',
                        'canonical_payload_sha256', template, root)


def archive_text(name, member_key, digest_key, root=ROOT):
    src = SOURCES['constructions'][name]
    with tarfile.open(Path(root) / src['archive'], 'r:gz') as tar:
        data = tar.extractfile(tar.getmember(SOURCES['outer_witness'][member_key])).read()
    require(sha256(data) == SOURCES['outer_witness'][digest_key], 'outer witness source digest')
    return data.decode()


def load_programs(name, template, root=ROOT):
    """Emitted forward/backward local programs, bound to the hosted template by container digest."""
    src = SOURCES['constructions'][name]
    archive = Path(root) / src['archive']
    with tarfile.open(archive, 'r:gz') as tar:
        info = tar.getmember(src['program_member'])
        require(info.isfile(), 'program member is not a regular file')
        container = tar.extractfile(info).read()
    (prov,) = template['local_providers'].values()
    require(sha256(container) == src['program_container_sha256'] == prov['local_programs_sha256'],
            f'{name}: program container is not the one bound by the hosted template')
    payload = gzip.decompress(container)
    require(sha256(payload) == src['program_payload_sha256'], f'{name}: program payload digest mismatch')
    return json.loads(payload)


def emitted_restoration(programs):
    """Rank profile of the emitted 'final' climbs and the phase order, per orientation."""
    out = {}
    for orientation in ('forward', 'backward'):
        prog = programs[orientation]
        phases = [e[1] for e in prog if e[0] == 'phase']
        final = Counter(e[5] for e in prog if e[0] == 'climb' and e[1] == 'final')
        climbs = Counter(e[5] for e in prog if e[0] == 'climb')
        centres = sum(1 for e in prog if e[0] == 'center')
        out[orientation] = dict(phases=phases, final=final, climbs=climbs, centres=centres)
    return out


def load_construction(name, root=ROOT):
    """Load the hosted global template and the local U8 word of a pinned construction."""
    src = SOURCES['constructions'][name]
    archive = Path(root) / src['archive']
    require(sha256(archive.read_bytes()) == src['archive_sha256'], f'{name}: archive digest mismatch')
    template = read_member(archive, src['template_member'], src['template_payload_sha256'])
    word = read_member(archive, src['word_member'], src['word_payload_sha256'])
    return template, word


# ---------------------------------------------------------------------------
# Local frame semantics (monotone nested F2^h frames).

class Span:
    """A subspace of F2^h held as a list of basis vectors in reduced echelon form."""
    __slots__ = ('basis',)

    def __init__(self, vectors=()):
        self.basis = []
        for x in vectors:
            self.insert(x)

    def residue(self, x):
        for b in self.basis:                      # basis sorted by decreasing leading bit
            if x ^ b < x:
                x ^= b
        return x

    def insert(self, x):
        x = self.residue(x)
        if not x:
            return False
        lead = x.bit_length() - 1
        self.basis = [b ^ x if (b >> lead) & 1 else b for b in self.basis]
        self.basis.append(x)
        self.basis.sort(reverse=True)
        return True

    @property
    def rank(self):
        return len(self.basis)

    def within(self, other):
        return all(other.residue(b) == 0 for b in self.basis)

    def same(self, other):
        return self.rank == other.rank and self.within(other)


def hyperplane(port, h):
    """{x in F2^h : <x, port> = 0}."""
    require(0 < port < 1 << h, 'port out of range')
    vectors = [x for x in (1 << i for i in range(h))]
    pivot = port & -port
    out = []
    for x in vectors:
        if x == pivot:
            continue
        out.append(x ^ (pivot if bin(x & port).count('1') % 2 else 0))
    U = Span(out)
    require(U.rank == h - 1, 'hyperplane rank')
    return U


def gate_registers(g):
    return list(g[1:3]) if g[0] == 'add' else list(g[1:2])


def canonical_restoration(cw):
    """Per-register restoration climbs of the template's canonical provider word.

    The canonical word indexes its frames through cw['frames'] and numbers its
    registers as the hosted template does, so its helper k is the template's
    pooled_slots helper k.  Same semantics as restoration_census.
    """
    h = cw['h']
    F = [Span(f) for f in cw['frames']]
    full = Span([1 << i for i in range(h)])
    require(not cw['target_levels'], 'canonical word has target levels')
    frame = [F[i] for i in cw['start']]

    def climb(q, U):
        require(frame[q].within(U), f'canonical word: non-monotone frame for register {q}')
        frame[q] = U

    for g in cw['A']:
        for q in gate_registers(g):
            climb(q, F[g[-1]])
    for q, i in zip(cw['centers'], cw['center_frames']):
        require(frame[q].same(F[i]), 'canonical word: centre frame at the cut')
    for g in cw['B'] + cw['tail']:
        for q in gate_registers(g):
            climb(q, F[g[-1]])
    restoration = []
    for q, i in enumerate(cw['final']):
        restoration.append(F[i].rank - frame[q].rank)
        climb(q, F[i])
    for g in cw['cleanup']:
        require(F[g[-1]].same(full), 'canonical cleanup gate is not full-frame')
    return restoration


def restoration_census(word):
    """Replay the literal frame chains of a local word.

    Returns the paid child profile, the width inventory, and for every register
    its start/end ranks, its final restoration climb (the climb from its last
    gate frame to its endpoint frame) and the number of full-frame cleanup
    gates that touch it.
    """
    rep = word['report']
    h, v, R = rep['h'], rep['v'], rep['R']
    n = 2 * v + R
    require(not word['target_levels'], 'this replay assumes empty target levels')
    full = Span([1 << i for i in range(h)])
    frame = [Span([p]) for p in word['ports']] + [Span() for _ in range(v + R)]
    for q, U in word['start_extra'].items():
        frame[int(q)] = Span(U)
    start = [f.rank for f in frame]
    paid = Counter()
    phase_mass = Counter()

    def climb(q, U, phase):
        require(frame[q].within(U), f'non-monotone frame for register {q} in {phase}')
        step = U.rank - frame[q].rank
        if step:
            paid[step] += 1
            phase_mass[phase] += step
        frame[q] = U

    for g in word['A']:
        for q in gate_registers(g):
            climb(q, Span(g[-1]), 'A')
    centre_children = Counter()
    for q, U in zip(word['centers'], word['center_frames']):
        U = Span(U)
        require(frame[q].same(U), 'centre frame at the cut')
        if any(g[2] == q for g in word['cut']):
            centre_children[U.rank] += 1
    paid.update(centre_children)
    for g in word['B']:
        for q in gate_registers(g):
            climb(q, Span(g[-1]), 'B')
    early = {}
    for i, U in word['early_cleanup']:
        early[i] = U
        for q in gate_registers(word['cleanup'][i]):
            climb(q, Span(U), 'early_cleanup')
    end = [full] * v + [hyperplane(p, h) for p in word['ports']] + [full] * R
    for q, U in word['helper_final'].items():
        end[int(q)] = Span(U)
    before_final = [f.rank for f in frame]
    for q in range(n):
        climb(q, end[q], 'final')
    full_touch = Counter()
    for i, g in enumerate(word['cleanup']):
        if i in early:
            continue
        require(Span(g[-1]).same(full), 'non-early cleanup gate is not full-frame')
        for q in gate_registers(g):
            require(end[q].same(full), 'full-frame cleanup touches a low end')
            full_touch[q] += 1
    registers = []
    for q in range(n):
        role = 'source' if q < v else 'target' if q < 2 * v else 'helper'
        registers.append(dict(register=q, role=role, start=start[q], end=end[q].rank,
                              restoration=end[q].rank - before_final[q],
                              low_end=str(q) in word['helper_final'],
                              full_cleanup_gates=full_touch[q]))
    widths = Counter(r['end'] - r['start'] for r in registers if r['role'] == 'helper')
    return dict(h=h, v=v, R=R, paid=paid, centre_children=centre_children,
                phase_mass=phase_mass, widths=widths, registers=registers)


# ---------------------------------------------------------------------------
# Global coverage semantics of the hosted nine-stage template.

def coverage_census(template, local_mass, data_step):
    """Per-family coordinate coverage of every live family.

    data_step is the paid frame climb of one data register per incidence,
    taken from the local word; the identity checked is
        data_step*k_f + 1 + hosted_f + idle_f = m      for every live family f.
    """
    W, m = template['live'], template['m']
    provider = template['local_providers']
    require(len(provider) == 1, 'one local provider expected')
    (pid, prov), = provider.items()
    v, R, widths = prov['v'], prov['R'], prov['widths']
    require(len(widths) == R, 'width list')
    k, hosted = Counter(), Counter()
    for call in template['calls']:
        require(call['provider_id'] == pid, 'provider dispatch')
        owners = call['owners']
        require(len(owners) == 2 * v + R, 'owner count')
        for i, (family, route) in enumerate(owners):
            require((route[0] == 1) == (i < 2 * v), 'data routes are exactly the data registers')
            if i < 2 * v:
                k[family] += 1
            else:
                hosted[family] += widths[i - 2 * v]
    pooled = Counter()
    for s in template['hosting']['pooled_slots']:
        require(widths[s['helper']] == s['width'], 'pooled slot width')
        pooled[s['family']] += s['width']
    require(pooled == hosted, 'pooled slots differ from call owners')
    idle = Counter()
    for c in template['idle_children']:
        require(c['replicas'] == 1 and c['rank'] > 0, 'idle child shape')
        idle[c['family']] += c['rank']
    outside = [f for f in set(k) | set(hosted) | set(idle) if not 0 <= f < W]
    require(not outside, 'coverage outside the live families')
    values = Counter(data_step * k[f] + 1 + hosted[f] + idle[f] for f in range(W))
    N = len(template['calls'])
    idle_mass = sum(idle.values())
    total = N * local_mass + idle_mass
    centres = template['private_namespace']['centers']
    return dict(live=W, m=m, calls=N, v=v, R=R,
                coverage_values={str(x): n for x, n in sorted(values.items())},
                data_incidences_per_family={str(x): n for x, n in sorted(Counter(k[f] for f in range(W)).items())},
                data_coordinates=data_step * sum(k.values()) + W,
                hosted_coordinates=sum(hosted.values()),
                idle_coordinates=idle_mass,
                total_rank_mass=total,
                deficit=m * W - total,
                private_centre_families=centres)


def global_profile(template, local_profile):
    H = Counter()
    for _ in template['calls']:
        H.update(local_profile)
    for c in template['idle_children']:
        H[c['rank']] += 1
    return H


# ---------------------------------------------------------------------------
# Restoration deferral: the explicit mechanism and its complete recurrence.

def window_deferral(template, local_profile, restoration_by_helper, chosen):
    """Profile after deferring the restoration climbs of the chosen helper indices.

    Each deferred climb of rank d leaves the local profile.  Its d host
    coordinates are returned to the pending set of the same hosting window
    (family, idle child), where they are advanced by that window's idle child.
    Coordinates returned to one window form one child, merged with any
    existing remainder of that window.  Rank mass is unchanged by construction.
    """
    H = global_profile(template, local_profile)
    remainder = {(c['family'], c['child']): c['rank'] for c in template['idle_children']}
    returned = defaultdict(int)
    removed = Counter()
    for s in template['hosting']['pooled_slots']:
        d = restoration_by_helper[s['helper']]
        if s['helper'] in chosen and d > 0:
            returned[(s['family'], s['child'])] += d
            removed[d] += 1
    H.subtract(removed)
    for w, d in returned.items():
        r0 = remainder.get(w, 0)
        if r0:
            H[r0] -= 1
        H[r0 + d] += 1
    H = +H
    return H, removed, Counter(returned.values())


def concentrated(H, removed, idle_ranks, cap):
    """Free-concentration relaxation: all idle coordinates in children of rank cap."""
    out = Counter(H)
    out.subtract(removed)
    out.subtract(idle_ranks)
    mass = sum(r * n for r, n in idle_ranks.items()) + sum(r * n for r, n in removed.items())
    q, r = divmod(mass, cap)
    out[cap] += q
    if r:
        out[r] += 1
    return +out


def rank_mass(H):
    return sum(int(r) * n for r, n in H.items())
