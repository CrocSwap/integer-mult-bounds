#!/usr/bin/env python3
"""Verify the dependency-respecting diagonal-batch count and its exact ceilings.

1. Pins: selected replay archive and the gauge44 LOCAL-PROGRAMS / CANONICAL-WORD members (PR1779's pins).
2. batch.py reorders rank-1 climbs inside their phase past events that do not touch their register and
   groups them into 16-batches on distinct destinations: 134 per orientation; per-phase cap 149.
3. The retained independent local checker (hpe_audit_local.py, unchanged) accepts the reordered
   programs, and its 'local' block and paid profiles equal those of the original programs.
4. Controls: a climb moved past a scalar on its own register, and a climb moved into another phase,
   are both rejected by the retained checker; PR1779's contiguous-run rule counts 8 on the original.
5. Exact ceilings (ceiling.py, grid 1e-15): 22 batches miss the +5% gate, 23 pass, 134 give a < 0.002358...

usage: verify.py [--write]
Prepared for Josie Elliston with Claude (Anthropic) assistance. Apache-2.0.
"""
from __future__ import annotations

import copy
import gzip
import hashlib
import io
import json
import subprocess
import sys
import tarfile
import tempfile
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'research/complex-local-word-ceiling'))
import batch as B  # noqa: E402
import ceiling as C  # noqa: E402

ARCHIVE = ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz'
ARCHIVE_SHA256 = 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6'
PREFIX = 'candidate/strict/global/base/providers/gauge44/'
MEMBERS = {
    'LOCAL-PROGRAMS.json.gz': '241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a',
    'CANONICAL-WORD.json.gz': '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219',
    'INDEPENDENT-LOCAL-REPLAY.json': '13dd18297162569532983db1a2ab67926b064330cd7edd3587e7b546b2dedf17',
}
CHECKER = ROOT / 'research/complex-571-cold14-k492b/code/hpe_audit_local.py'
CHECKER_PASS = 'PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY'
BASE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
GRID = Q(1, 10 ** 15)


def require(ok, why):
    if not ok:
        raise SystemExit('FAIL: ' + why)


def members():
    raw = ARCHIVE.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == ARCHIVE_SHA256, 'selected replay archive pin')
    out = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as tar:
        for name, sha in MEMBERS.items():
            data = tar.extractfile(PREFIX + name).read()
            require(hashlib.sha256(data).hexdigest() == sha, 'member pin ' + name)
            out[name] = data
    return out


def run_checker(word_gz, programs):
    """Run the retained checker unchanged on (word, programs); return its receipt or None if it rejects."""
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        (d / 'CANONICAL-WORD.json.gz').write_bytes(word_gz)
        with gzip.open(d / 'LOCAL-PROGRAMS.json.gz', 'wt') as fh:
            json.dump(programs, fh, separators=(',', ':'))
        p = subprocess.run([sys.executable, '-I', '-B', str(CHECKER), str(d)], capture_output=True, text=True)
        if p.returncode != 0 or CHECKER_PASS not in p.stdout:
            return None
        return json.loads((d / 'INDEPENDENT-LOCAL-REPLAY.json').read_text())


def reorder(programs, word):
    reordered, summary = {}, {}
    for orient, events in programs.items():
        new_events, per_phase, nb = [], {}, 0
        for ph, body in B.split_phases(events):
            if ph is not None:
                new_events.append(ph)
            body2, batches, n1, nmov = B.batch_phase(body)
            new_events.extend(body2)
            if n1:
                per_phase[ph[1]] = {'rank1': n1, 'movable': nmov, 'batches': len(batches), 'cap': n1 // B.BATCH}
            nb += len(batches)
        require(sorted(map(json.dumps, new_events)) == sorted(map(json.dumps, events)), orient + ' same multiset')
        require([e for e in new_events if not B.is_r1(e)] == [e for e in events if not B.is_r1(e)],
                orient + ' non-rank-1 order unchanged')
        B.replay_frames(new_events, word)
        reordered[orient] = new_events
        summary[orient] = {
            'batches': nb,
            'phase_cap': sum(v['cap'] for v in per_phase.values()),
            'per_phase': per_phase,
            'pr1779_rule_original': B.rank_one_runs_1779(events),
            'pr1779_rule_reordered': B.rank_one_runs_1779(new_events),
        }
    return reordered, summary


def bad_move_past_own_scalar(events):
    """Move the first rank-1 climb whose immediately preceding event is a scalar on its register before it."""
    es = copy.deepcopy(events)
    for i in range(1, len(es)):
        e, prev = es[i], es[i - 1]
        if B.is_r1(e) and prev[0] == 'scalar' and ('L', e[2]) in B.touched(prev):
            es[i - 1], es[i] = es[i], es[i - 1]
            return es
    raise SystemExit('FAIL: no control site')


def bad_move_across_phase(events):
    """Move the last rank-1 climb of phase A to just after the next phase marker."""
    es = copy.deepcopy(events)
    b = es.index(['phase', 'centers'])
    i = max(k for k in range(b) if B.is_r1(es[k]))
    ev = es.pop(i)
    es.insert(es.index(['phase', 'centers']) + 1, ev)
    return es


def bracket(nb):
    p = dict(BASE)
    p[1] -= B.BATCH * nb
    if nb:
        p[16] = nb
    return C.ceiling(p, 73, 896, 9, 64, grid=GRID)


def main():
    m = members()
    programs = json.loads(gzip.decompress(m['LOCAL-PROGRAMS.json.gz']))
    word = json.loads(gzip.decompress(m['CANONICAL-WORD.json.gz']))
    for orient, events in programs.items():
        B.replay_frames(events, word)

    reordered, summary = reorder(programs, word)
    for orient in ('forward', 'backward'):
        s = summary[orient]
        require(s['batches'] == 134 and s['phase_cap'] == 149, orient + ' batch count / cap')
        require(s['pr1779_rule_original'] == 8, orient + " PR1779's contiguous rule on the original")
        require(s['pr1779_rule_reordered'] == 134, orient + " PR1779's contiguous rule on the reordered")
    require(summary['forward'] == summary['backward'], 'orientation agreement')

    pinned = json.loads(m['INDEPENDENT-LOCAL-REPLAY.json'])
    orig = run_checker(m['CANONICAL-WORD.json.gz'], programs)
    require(orig is not None, 'retained checker accepts the original programs')
    require(orig['local'] == pinned['local'] and orig['paid_profiles'] == pinned['paid_profiles'],
            'original receipt equals the pinned selected receipt')
    new = run_checker(m['CANONICAL-WORD.json.gz'], reordered)
    require(new is not None, 'retained checker accepts the reordered programs')
    require(new['local'] == orig['local'] and new['paid_profiles'] == orig['paid_profiles'],
            'reordered receipt equals the original')

    controls = []
    for name, mut in (('climb_past_own_scalar', bad_move_past_own_scalar),
                      ('climb_across_phase', bad_move_across_phase)):
        bad = dict(reordered)
        bad['forward'] = mut(reordered['forward'])
        require(run_checker(m['CANONICAL-WORD.json.gz'], bad) is None, 'control accepted: ' + name)
        controls.append(name)

    base = bracket(0)
    target = base[1] * Q(105, 100)
    rows = {}
    for nb in (8, 22, 23, 134, 149):
        lo, hi = bracket(nb)
        rows[str(nb)] = {'a_lo': str(lo), 'a_hi': str(hi), 'passes_5pct_gate': lo > target,
                         'gain_pct_hi': f'{float(100 * (hi / base[1] - 1)):.4f}'}
    require(not rows['22']['passes_5pct_gate'] and Q(rows['22']['a_hi']) < target, '22 batches miss the gate')
    require(rows['23']['passes_5pct_gate'], '23 batches pass the gate')
    require(Q(rows['8']['a_hi']) == Q(1719107428154, 10 ** 15), "PR1779's 8-batch ceiling reproduced")

    # Idle-displacing charge headroom at 134 batches (discussion 1596 convention): E extra rank-1
    # children per call replace E units of idle mass. Sharp: E = 1258 passes the gate, 1259 fails.
    def charged(extra):
        p = dict(BASE)
        p[1] += extra - B.BATCH * 134
        p[16] = 134
        return C.ceiling(p, 73, 896, 9, 64, grid=GRID)
    pass_e, fail_e = charged(1258), charged(1259)
    require(pass_e[0] > target and fail_e[1] < target, 'sharp idle-displacing charge headroom 1258')
    headroom = {'convention': 'idle-displacing extra rank-1 children per call, 134 batches, +5% gate',
                'max_extra_rank1': 1258, 'per_batch': '1258/134',
                'a_lo_at_1258': str(pass_e[0]), 'a_hi_at_1259': str(fail_e[1])}

    result = {
        'status': 'PASS_DIAGONAL_BATCH_COMMUTATION',
        'base_ceiling': [str(base[0]), str(base[1])],
        'gate_target_a': str(target),
        'orientations': summary,
        'ceilings_by_batches': rows,
        'checker_controls_rejected': controls,
        'charge_headroom': headroom,
    }
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    out = HERE / 'RESULT.json'
    if '--write' in sys.argv:
        out.write_text(text)
    require(out.read_text() == text, 'RESULT.json receipt')
    print(f"PASS_DIAGONAL_BATCH_COMMUTATION batches=134 phase_cap=149 pr1779_rule=8->134 "
          f"gate_min=23 a_hi_134={float(Q(rows['134']['a_hi'])):.12f} controls={len(controls)}")


if __name__ == '__main__':
    main()
