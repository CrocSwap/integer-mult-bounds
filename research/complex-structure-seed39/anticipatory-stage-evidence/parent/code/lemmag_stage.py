# SPDX-License-Identifier: Apache-2.0
"""Package stage `lemmag-labels` (beside the frame-only `local-replay`): runs the Lemma G label / adapter checks of PR1964 (thakrarsagar; Lemma G by
DreamingOfClouds, PR509 / PR516; vendored verbatim in lemmag_checks.py) on every provider's emitted LOCAL-PROGRAMS, both orientations:
  * label_check strict and permissive and adapter_rule must each report 0 violations on the honest programs;
  * the physically wrong adapter mutants X (exit straddle), Y (entry straddle) and Z (exit adapters moved before a phase-B add), which the frame-only replay
    accepts, must each be REJECTED (at least one of the three checks reports a violation); the stage fails if a mutant is accepted or cannot be built.
usage: lemmag_stage.py OUT.json DIR [DIR ...]   (each DIR contains local/CANONICAL-WORD.json.gz and local/LOCAL-PROGRAMS.json.gz)"""
import gzip, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lemmag_checks as V


def main(out, dirs):
    report = {}
    for d in dirs:
        L = Path(d) / 'local'
        c = json.loads(gzip.decompress((L / 'CANONICAL-WORD.json.gz').read_bytes()))
        progs = json.loads(gzip.decompress((L / 'LOCAL-PROGRAMS.json.gz').read_bytes()))
        row = {'v': c['v'], 'R': c['R'], 'events': {o: len(p) for o, p in progs.items()}, 'honest': {}, 'mutants': {}}
        for o in ('forward', 'backward'):
            s, _ = V.label_check(c, progs[o], 'strict')
            p, _ = V.label_check(c, progs[o], 'permissive')
            r = V.adapter_rule(c, progs[o])
            row['honest'][o] = {'label_strict': len(s), 'label_permissive': len(p), 'adapter_rule': len(r)}
            assert not s and not p and not r, ('honest programs violate the Lemma G label / adapter checks', str(d), o, s[:2], p[:2], r[:2])
        fw = progs['forward']; t, s0 = c['v'], 0
        muts = {'X': lambda: V.straddle(fw, ['adapter', 'new_to_old', t, c['final'][t]], c['final'][t], t)[0],
                'Y': lambda: V.straddle(fw, ['adapter', 'old_to_new', s0, c['start'][s0]], c['start'][s0], s0)[0],
                'Z': lambda: V.exit_block_move(c, fw)[0]}
        for name, build in muts.items():
            m = build()
            st = len(V.label_check(c, m, 'strict')[0]); pe = len(V.label_check(c, m, 'permissive')[0]); ar = len(V.adapter_rule(c, m))
            row['mutants'][name] = {'label_strict': st, 'label_permissive': pe, 'adapter_rule': ar, 'rejected': bool(st or pe or ar)}
            assert st or pe or ar, ('adapter mutant ACCEPTED by the Lemma G checks', str(d), name)
        ws = [i for i, e in enumerate(fw) if e[0] == 'warp' and e[3] != 1]       # forward warps (from frame below FULL)
        if ws:   # BORROW controls: reference-change mutants must be rejected
            def rej(m): return bool(V.label_check(c, m, 'strict')[0] or V.label_check(c, m, 'permissive')[0] or V.adapter_rule(c, m))
            w0 = ws[0]; e0 = fw[w0]; other = next(f for f in range(2, len(c['frames'])) if f not in (e0[3], e0[4]))
            bw = {'warp_wrong_from_frame': fw[:w0] + [e0[:3] + [other, e0[4]]] + fw[w0 + 1:],
                  'warp_dropped': fw[:w0] + fw[w0 + 1:],
                  'warp_to_wrong_frame': fw[:w0] + [e0[:4] + [other]] + fw[w0 + 1:],
                  'inverse_warp_from_wrong_frame': [e[:3] + [other] + e[4:] if i == next(j for j, x in enumerate(fw) if x[0] == 'warp' and x[3] == 1) else e for i, e in enumerate(fw)],
                  'zero_buffer_not_freed': [e for e in fw if not (e[0] == 'zero_buffer' and e[1] == 'free')][:],
                  'zero_buffer_not_allocated': [e for e in fw if not (e[0] == 'zero_buffer' and e[1] == 'alloc')],
                  'zero_buffer_outside_cleanup': fw[:w0] + [['zero_buffer', 'alloc', next(e[2] for e in fw if e[0] == 'zero_buffer')]] + fw[w0:]}
            row['borrow_mutants'] = {}
            for name, m in bw.items():
                row['borrow_mutants'][name] = rej(m)
                assert rej(m), ('borrow mutant ACCEPTED', str(d), name)
        report[str(d)] = row
    Path(out).write_text(json.dumps(report, indent=1, sort_keys=True) + '\n')
    print('PASS_LEMMAG_LABELS dirs=%d mutants_rejected=%d borrow_mutants_rejected=%d' % (len(dirs), 3 * len(dirs), sum(len(r.get('borrow_mutants', {})) for r in report.values())))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
