# Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
"""Instance check H6 (PROOF.md §4): the #433 data-adapter identities, exhaustively on all 512 basis columns.

With the extended labels, the Lean theorem gives source i the block T_(T,final_i) T_(pre,i)^-1 = T_{final_i} T_{p_i}^-1 M_i
(M_i = the serialized source endpoint monomial) and target t = v+i the block T_(post,t) = N_t^-1 T_{final_t} (N_t = the
serialized target endpoint monomial, applied inverted).  The intended transform of #433
(lg_phys.expected) is F C_{q_i}^-1 for both, with F the Fourier gate on all nine axes and C_q the port gate.  This script
checks, for every port i, on all 512 basis columns, exactly over Z[i][1/2]:
    T_{p_i}^-1 M_i            == C_{q_i}^-1
    T_{final_i} T_{p_i}^-1 M_i == F C_{q_i}^-1
    N_t^-1 T_{final_t}        == F C_{q_i}^-1
T_F and C_q are the DEFINITIONS (vendored canonical_frame / cgate); M_i and N_t are decoded from the serialized recipes.

usage: check_adapters.py BASE VARIANT [VARIANT ...]     (BASE = the output directory of #484's verify.py; needs numpy)"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'e8-complex-gauge-kernel' / 'code' / 'lemmaG'))
from lg_lib import load  # noqa: E402
from lg_phys import Model  # noqa: E402
from gd import identity_batch, fourier_circ  # noqa: E402


def check(d):
    m = Model(d); c = d['c']; v = c['v']; I = identity_batch(); F = fourier_circ(range(9))
    fail = {'T_p^-1 M_i == C_q^-1': 0, 'T_final T_p^-1 M_i == F C_q^-1': 0, 'N_t^-1 T_final == F C_q^-1': 0}
    for i in range(v):
        fs, Mi = m.src_ad[i]; ft, Nt = m.tgt_ad[i]
        if fs != c['start'][i] or ft != c['final'][v + i] or Mi is None or Nt is None:
            raise SystemExit(f'port {i}: adapter frames ({fs}, {ft}) or operators do not match the word')
        Cinv = I.copy().apply_circ(m.Cq(i), inverse=True)
        a = I.copy().apply_circ(Mi).apply_circ(m.T(fs), inverse=True)
        fail['T_p^-1 M_i == C_q^-1'] += not a.equals(Cinv)
        target = Cinv.copy().apply_circ(F)
        fail['T_final T_p^-1 M_i == F C_q^-1'] += not a.copy().apply_circ(m.T(c['final'][i])).equals(target)
        fail['N_t^-1 T_final == F C_q^-1'] += not I.copy().apply_circ(m.T(ft)).apply_circ(Nt, inverse=True).equals(target)
    return v, fail


def main():
    base, ok = Path(sys.argv[1]), True
    for name in sys.argv[2:]:
        ports, fail = check(load(base / name))
        ok &= not any(fail.values())
        print(name, 'ports', ports, 'columns 512 each', 'failures', fail, flush=True)
    print('PASS adapter identities' if ok else 'FAIL adapter identities')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
