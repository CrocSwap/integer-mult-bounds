#!/usr/bin/env python3
"""Emit and replay a complete eight-column actual H6 compensation block."""
from collections import Counter
from fractions import Fraction
import hashlib
import gzip
import json
from pathlib import Path
import sys
import shutil
import numpy as np

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from artifact import write_receipt

SOURCE = ROOT / 'research/niemeier-lattices/code/e8_cubed.py'
sys.path.insert(0, str(SOURCE.parent))
import e8_cubed as e


def require(value, message):
    if not value:
        raise ValueError(message)


def basis(words):
    pivots = {}
    for word in words:
        value = int(word)
        for pivot in sorted(pivots, reverse=True):
            if value >> pivot & 1:
                value ^= pivots[pivot]
        if value:
            pivot = value.bit_length() - 1
            for old in list(pivots):
                if pivots[old] >> pivot & 1:
                    pivots[old] ^= value
            pivots[pivot] = value
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def contained(small, large):
    return len(basis(small + large)) == len(large)


def perp(word):
    pivot = (word & -word).bit_length() - 1
    return basis((1 << bit) ^ ((1 << pivot) if word >> bit & 1 else 0)
                 for bit in range(17) if bit != pivot)


def rank_modular(rows, prime=101):
    active, witnesses = {}, []
    for i, row in enumerate(rows):
        row = row.astype(np.int64).copy() % prime
        for pivot in sorted(active):
            row = (row - row[pivot] * active[pivot]) % prime
        nz = np.flatnonzero(row)
        if len(nz):
            pivot = int(nz[0])
            active[pivot] = row * pow(int(row[pivot]), -1, prime) % prime
            witnesses.append(i)
    return witnesses


def compress_network(path):
    """Preserve the expanded event payload in a compact lossless artifact."""
    destination = path.with_suffix(path.suffix + '.gz')
    with path.open('rb') as source, destination.open('wb') as raw_output:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw_output, mtime=0) as output:
            shutil.copyfileobj(source, output)
    path.unlink()
    return destination.name


def main():
    out = Path(__file__).resolve().parent
    roots, _, shell, profiles = e.construct_shell()
    P = shell[(profiles & 4) == 0, :16].astype(np.int64)
    _, packed, _ = e.binary_labels(roots, P)
    word = int(packed[0])
    S = np.flatnonzero(packed == word)
    require(S.tolist() == [0, 1, 2, 11, 44, 125, 286, 1079], 'pinned eight-source label fiber')
    raw = P @ P[S].T
    require(np.all(raw % 4 == 0), 'integer actual pairings')
    t = raw // 4
    T = np.flatnonzero(np.all(t & 1, axis=1))
    require(len(T) == 15872, 'complete fiber support')
    require(np.array_equal(np.any(t & 1, axis=1), np.all(t & 1, axis=1)), 'identical source support')
    C = (4 * t[T] - t[T] ** 3).astype(np.int64)
    require(np.all(np.isin(C, [-15, -3, 3, 15])), 'actual full coefficients including exception')
    rank_witnesses = rank_modular(C)
    require(len(rank_witnesses) == 8, 'exact rational rank eight lower bound modulo101')
    require(not set(S.tolist()) & set(T.tolist()), 'source and target roles disjoint')
    F = basis([word])
    FULL = basis(1 << bit for bit in range(17))
    caps = {int(target): perp(int(packed[target])) for target in T}
    require(all(len(cap) == 16 and contained(F, cap) for cap in caps.values()), 'all target incidences')
    regs = [f's{i}' for i in range(8)] + [f'h{i}' for i in range(8)] + [f't{int(i)}' for i in T]
    starts = {r: F if r.startswith('s') else () for r in regs}
    ends = {r: caps[int(r[1:])] if r.startswith('t') else FULL for r in regs}
    frames = dict(starts)
    paths = {r: [] for r in regs}
    # Sparse exact forward scalar replay: targets retain their own identity;
    # helper rows have sixteen source/dirt columns. Target coefficients use
    # common denominator48, which includes all actual compensation entries.
    helper_rows = np.concatenate((np.zeros((8, 8), dtype=np.int64), np.eye(8, dtype=np.int64)), axis=1)
    target_rows = np.zeros((len(T), 16), dtype=np.int64)
    # Independent inverse-transpose replay in the SAME event order. Target
    # rows remain identity; only source/helper rows require explicit storage.
    dual_rows = np.zeros((16, len(T) + 16), dtype=np.int64)
    dual_rows[:, :16] = 48 * np.eye(16, dtype=np.int64)
    target_position = {int(target): row for row, target in enumerate(T)}
    digest = hashlib.sha256()
    events_count = 0
    network = out / 'NETWORK.jsonl'
    with network.open('w') as stream:
        def event(item):
            nonlocal events_count
            payload = json.dumps(item, sort_keys=True, separators=(',', ':')) + '\n'
            stream.write(payload)
            digest.update(payload.encode())
            events_count += 1
            if item['op'] == 'climb':
                register = item['register']
                frame = tuple(item['frame'])
                require(frame == basis(frame), 'canonical frame')
                require(contained(frames[register], frame), 'ordinary descent prohibited')
                increment = len(frame) - len(frames[register])
                if increment:
                    paths[register].append(increment)
                frames[register] = frame
                return
            dst, src, numerator, denominator = item['dst'], item['src'], item['numerator'], item['denominator']
            require(frames[dst] == frames[src], 'addition requires equal current frames')
            if dst.startswith('t'):
                row, lane = target_position[int(dst[1:])], int(src[1:])
                require(denominator == 48 and src.startswith('h'), 'scatter encoding')
                target_rows[row] += numerator * helper_rows[lane]
                # Inverse transpose: h -= q*t, with target identity48.
                dual_rows[8 + lane, 16 + row] -= numerator
            else:
                lane, source = int(dst[1:]), int(src[1:])
                require(dst.startswith('h') and src.startswith('s') and denominator == 1, 'gather encoding')
                helper_rows[lane, source] += numerator
                # Inverse transpose: s -= q*h.
                dual_rows[source] -= numerator * dual_rows[8 + lane]

        def add(dst, src, numerator, denominator=1):
            event(dict(op='add', dst=dst, src=src, numerator=int(numerator), denominator=denominator))

        def climb(register, frame):
            event(dict(op='climb', register=register, frame=list(frame)))

        # Dirt precompensation before any target leaves zero.
        for row, target in enumerate(T):
            for lane in range(8):
                add(f't{int(target)}', f'h{lane}', -C[row, lane], 48)
        for register in regs[8:]:
            climb(register, F)
        for lane in range(8):
            add(f'h{lane}', f's{lane}', 1)
        for row, target in enumerate(T):
            for lane in range(8):
                add(f't{int(target)}', f'h{lane}', C[row, lane], 48)
        for register in regs[:16]:
            climb(register, FULL)
        for lane in range(8):
            add(f'h{lane}', f's{lane}', -1)
        for target in T:
            climb(f't{int(target)}', caps[int(target)])

    require(frames == ends, 'all endpoint frames')
    require(np.array_equal(target_rows[:, :8], C) and not target_rows[:, 8:].any(), 'forward actual block and arbitrary dirt')
    require(np.array_equal(helper_rows[:, :8], np.zeros((8, 8), dtype=np.int64)), 'ordinary helper cleanup')
    require(np.array_equal(helper_rows[:, 8:], np.eye(8, dtype=np.int64)), 'all helper dirt retained')
    require(np.array_equal(dual_rows[:, :16], 48*np.eye(16, dtype=np.int64)), 'dual source and arbitrary dirt restoration')
    require(np.array_equal(dual_rows[:8, 16:], -C.T) and not dual_rows[8:, 16:].any(), 'inverse-transpose actual block')
    profiles = Counter(tuple(path) for path in paths.values())
    require(profiles == Counter({(16,): 8, (1, 16): 8, (1, 15): 15872}), 'paid emitted paths')
    # Minimal chronology obstruction: target287 already has u,v span;
    # target295 permits u but rejects v. They cannot share an ordinary
    # helper at a common frame once the first target acquired v.
    v = int(packed[3]); a, b = 287, 295
    joint = basis([word, v])
    require(contained(joint, caps[a]), 'positive second-line target')
    require(not contained(joint, caps[b]), 'incompatible second-line target')
    require(contained(F, caps[b]), 'both targets initially share u')
    require(len(joint) == 2, 'decisive two-line obstruction')
    network_filename = compress_network(network)
    result = dict(status='PASS_COMPLETE_EIGHT_COLUMN_ACTUAL_COMPENSATION_BLOCK',
        source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        source_ports=S.tolist(), source_label=word, target_ports=T.tolist(),
        coefficients_denominator=48, coefficient_numerators=C.tolist(),
        source_frame=list(F), source_cap_incidence_count=len(T),
        rational_block_rank=8, modular_rank_prime=101,
        rank_witness_target_ports=T[rank_witnesses].tolist(),
        helper_count=8, edge_baseline_helper_count=int(C.size),
        ordinary_private_copies=0, private_descent_rank=0,
        expanded_event_count=events_count, expanded_network_sha256=digest.hexdigest(),
        expanded_network_gzip_filename=network_filename,
        source_paths=dict(count=8, path=[16]), target_paths=dict(count=len(T), path=[1,15]),
        helper_paths=dict(count=8, path=[1,16]),
        total_local_transition_rank=sum(sum(path) for path in paths.values()),
        edge_baseline_helper_transition_rank=int(C.size)*17,
        full_forward_and_same_order_dual_checks=True,
        negative_controls=dict(omit_precompensation='target dirt equals C/48, hence nonzero',
            omit_cleanup='each helper retains one source coefficient, hence fails restoration',
            target_chronology=dict(source_u=0, source_v=3, target_allows_uv=a,
                target_rejects_v=b, u_label=word, v_label=v, joint_frame=list(joint),
                statement='Any common frame after target287 acquires v contains v and cannot lie in target295 cap. This rejects chaining all label fibers at their original line frame; it does not reject different routes.')),
        scope='Complete actual I-K contribution of eight source columns to all their allowed targets, with exact arbitrary-dirt and frame replay. Local shared word only; not the all-port sum, a full supplier invoice, or a kappa claim.')
    write_receipt(out/'RESULT.json', result, fields=['target_ports', 'coefficient_numerators'])
    print(json.dumps({key: result[key] for key in ('status','helper_count','edge_baseline_helper_count','expanded_event_count','total_local_transition_rank')}, sort_keys=True))


if __name__ == '__main__':
    main()
