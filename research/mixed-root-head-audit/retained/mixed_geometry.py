"""Bind each root to one absolute head operator and sixteen whole body blocks. Apache-2.0."""
from collections import Counter
from hashlib import sha256
import json

from mixed_caller import need

AMBIENT = 137
CENTRAL = tuple(1 << j for j in range(9))
BODIES = tuple(255 << (9 + 8*c) for c in range(16))


def central_contact(q, basis):
    """Return the coordinate map and both translations in the original nine axes."""
    from upstream_application import dot, polynomial, sub, terms, translation

    frame = (q, *basis)
    need(len(frame) == 9 and all(0 < v < 512 for v in frame) and
         all(dot(a, b) == (i == j) for i, a in enumerate(frame) for j, b in enumerate(frame)),
         'orthogonal change of central head')
    def push(value):
        out = value & ~511
        for axis, image in zip(CENTRAL, frame, strict=True):
            if value & axis:
                out ^= image
        return out

    def pull(value):
        return (value & ~511) | sum(axis for axis, image in zip(CENTRAL, frame, strict=True)
                                    if dot(value, image))

    def move(row, transform):
        return terms((transform(a), c) for a, c in row.items())

    def value(row, k):
        return sum(c*dot(a, k) for a, c in row.items()) % 4

    need(all(pull(push(x)) == push(pull(x)) == x for x in range(512)) and
         all(push(v) == pull(v) == v for v in (1 << i for i in range(9, AMBIENT))),
         'inverse central permutation and every body spectator')
    base = terms((v, 1) for v in CENTRAL)
    shift = translation(sub(base, move(base, push)))
    back = translation(sub(base, move(base, pull)))
    need(pull(shift) == back and push(back) == shift, 'ordered inverse head translation')
    # Both endpoints use the same central X frame. Y differs from X by the inverse head.
    for power in (0, -1):
        canonical = terms([*base.items(), (1, power)])
        local = terms([*base.items(), (q, power)])
        for src, dest, transform, tau in ((canonical, local, push, shift), (local, canonical, pull, back)):
            moved = move(src, transform)
            delta = sub(dest, terms([*moved.items(), (tau, 2)]))
            need(not polynomial(delta) and all(value(dest, k) == (value(moved, k) + 2*dot(tau, k)) % 4
                                                for k in range(512)), 'absolute central endpoint phase')
    # This tests Q, its adjoint and Q squared, which is the translated branch in LAMBDA.
    for power in (1, -1, 2):
        canonical = terms([(1, power)])
        local = terms([(q, power)])
        need(move(canonical, push) == local and move(local, pull) == canonical,
             'absolute signed head conjugation')
        need(all(value(local, k) == value(canonical, pull(k)) for k in range(512)),
             'signed head on every character')
    return list(frame), shift, back


def contact_atlas(layout, phase_bases):
    from binding16 import contact_phase
    from upstream_application import boundary

    ports, bases = layout['ports'], phase_bases['by_q']
    need(len(ports) == len(set(ports)) == 104 and all(str(q) in bases for q in ports),
         'phase basis for every physical port')
    atlas = []
    fault = False
    for q in ports:
        frame, shift, back = central_contact(q, bases[str(q)])
        if shift and not fault:
            # A missing translation changes the phase on a character in its support.
            key = shift & -shift
            need((2*(shift & key).bit_count()) % 4 == 2, 'detect omitted rehead translation')
        rows = []
        for color in range(16):
            offsets, control = contact_phase(q, bases[str(q)], color + 1, AMBIENT)
            rows.append(offsets)
            if shift and control and not fault:
                transform, (src, dst) = control
                try:
                    boundary(src, dst, transform, omit_translation=True)
                except ValueError as exc:
                    need(str(exc) == 'forward contact includes its phase', 'wrong omitted phase failure')
                    fault = True
                else:
                    raise ValueError('omitted native contact translation accepted')
        atlas.append([q, frame, shift, back, rows])
    need(fault, 'an absolute phase translation changes a signed contact')
    return atlas


def masks_and_contacts(words, roots, offsets, atlas):
    """Record the literal global axis set of each paid caller job and each productive field."""
    from upstream_application import terms, translation, sub

    head = 1
    paid, targets = Counter(), Counter()
    digest = sha256()
    seen = set()
    normalizer_digest = sha256()
    normalizer_count = 0
    local = {}
    def record(row):
        digest.update(json.dumps(row, separators=(',', ':')).encode())
        digest.update(b'\n')

    for kind, (events, endpoints) in words.items():
        jobs, normalizers = [], []
        for i, (op, *args) in enumerate(events):
            if op == 'QUERY':
                target, donor, sign = args
                jobs.append((op, i, target, donor, sign, ()))
            elif op in ('IDLE_ODD', 'IDLE_ONE'):
                target, mask, *sign = args
                jobs.append((op, i, target, None, sign[0] if sign else 0, mask))
            elif op == 'LAMBDA':
                target, sign = args
                need(sign in (-1, 1) and translation(terms([(head, 2)])) == head,
                     'canonical LAMBDA translation')
                normalizers.append((i, target, sign))
        local[kind] = jobs, endpoints, normalizers

    def axes(mask, perm):
        result = 0
        for j in mask:
            block = BODIES[perm[j]]
            need(result & block == 0, 'no repeated body in a whole job')
            result |= block
        return result

    checked_masks = {}
    for root, visits in sorted(roots.items()):
        kind = root[0]
        off, (jobs, endpoints, normalizers) = offsets[root], local[kind]
        for i, target, sign in normalizers:
            normalizer_digest.update(f'{i}/{off+target}/{sign}/{head}\n'.encode())
            normalizer_count += 1
        perm = tuple(t % 16 for t, _ in visits)
        need(set(perm) == set(range(16)), 'sixteen different body blocks on one root')
        for t, p in visits:
            seen.add((p, t % 16))
            need(len(atlas[p][4][t % 16]) == 4, 'four signed physical boundaries for actual visit')
        for op, index, target, donor, phase, mask in jobs:
            body = axes(mask, perm)
            rank = (body | (head if phase else 0)).bit_count()
            need(rank > 0 and rank == 8*len(mask) + int(phase != 0), 'actual paid axis rank')
            paid[rank] += 1
            record([op, index, off+target, off+donor if donor is not None else None, phase, hex(body)])
        for i, (phase, mask) in enumerate(endpoints):
            body = axes(mask, perm)
            if (phase, body) not in checked_masks:
                stage_axes = [1 << j for j in range(9, AMBIENT) if (body >> j) & 1]
                signed = terms([(head, phase)] + [(v, 1) for v in stage_axes])
                positive = terms([(head, 1)] + [(v, 1) for v in stage_axes])
                checked_masks[phase,body] = translation(sub(positive, signed))
            need(checked_masks[phase,body] == (head if phase == -1 else 0),
                 'absolute final head correction')
            rank = (body | head).bit_count()
            need(rank == 1 + 8*len(mask), 'actual productive axis rank')
            targets[rank] += 1
            record(['TARGET', off+i, phase, hex(body)])
    need(seen == {(p,c) for p in range(len(atlas)) for c in range(16)}, 'all physical port-color pairs')
    receipt = dict(central_bases=len(atlas), central_characters_per_phase=512,
                   distinct_contact_colors=len(seen), absolute_native_boundaries=4*len(seen),
                   canonical_head_axis=head, body_axis_masks=[hex(m) for m in BODIES],
                   used_paid_masks=sum(paid.values()), used_targets=sum(targets.values()),
                   distinct_signed_target_masks=len(checked_masks), whole_axis_sets_sha256=digest.hexdigest(),
                   atlas_sha256=sha256(json.dumps(atlas, separators=(',', ':')).encode()).hexdigest(),
                   nonzero_forward_rehead_shifts=sum(bool(a[2]) for a in atlas),
                   canonical_normalizers=normalizer_count,
                   ordinary_head_summands_sha256=normalizer_digest.hexdigest(),
                   native_phase_omission_rejected=True)
    return paid, targets, receipt
