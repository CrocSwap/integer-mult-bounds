"""Exact H6 canonical-block correction and independent spectral cross-check."""
from pathlib import Path
from collections import Counter
from itertools import combinations_with_replacement
from fractions import Fraction as F
import hashlib, json, subprocess, sys, platform
import numpy as np

def require(ok, message):
    if not ok:
        raise ValueError(message)
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'research/niemeier-lattices/code'))
import e8_cubed as e
roots, fourth, P, profiles = e.construct_shell()
P = P[profiles & 4 == 0, :16].astype(np.int64)
rr = P[2160:]
a = np.unique(rr[:, :8], axis=0)
b = np.unique(rr[:, 8:], axis=0)
require(len(a) == 120 and len(b) == 240 and (len(rr) == 120 * 240), 'spectral exact check at original line 15')
require(np.array_equal(rr[:, :8], np.repeat(a, 240, axis=0)), 'spectral exact check at original line 16')
require(all((np.array_equal(np.unique(chunk[:, 8:], axis=0), b) for chunk in rr.reshape(120, 240, 16))), 'spectral exact check at original line 17')
require(np.array_equal(rr[:, 8:], np.tile(rr[:240, 8:], (120, 1))), 'spectral exact check at original line 18')
S = a @ a.T // 4
G = b @ b.T // 4
require(np.all((S == 0).sum(1) == 63) and np.all((np.abs(S) == 1).sum(1) == 56), 'spectral exact check at original line 20')
require(np.all((S == 2).sum(1) == 1) and (not (S == -2).any()), 'spectral exact check at original line 21')
block_counts = Counter(S.ravel().tolist())
full_counts = Counter(G[0].tolist())
for s in range(-2, 3):
    for t in range(-2, 3):
        require((s + t) ** 3 - 4 * (s + t) == s ** 3 + 3 * s * s * t + 3 * s * t * t + t ** 3 - 4 * s - 4 * t, 'spectral exact check at original line 28')
ranks = {}
for name, rows, degree, expected in [('root_linears', roots, 1, 8), ('root_quadratics', roots, 2, 36), ('root_cubics', roots, 3, 120), ('norm4_cubics', fourth, 3, 120)]:
    monomials = list(combinations_with_replacement(range(8), degree))
    features = np.stack([np.prod(rows[:, inds].astype(np.int64), axis=1) for inds in monomials], axis=1)
    witnesses = e.modular_rank_witnesses(features, 101)
    require(len(witnesses) == expected, 'spectral exact check at original line 34')
    ranks[name] = {'rank': expected, 'prime': 101, 'independent_rows': witnesses}
full_moments = []
for name, half, norm in [('roots', roots, 2), ('norm4', fourth, 4)]:
    rows = np.concatenate([half.astype(np.int64), -half.astype(np.int64)])
    for powers, wick in [([2], 1), ([4], 3), ([2, 2], 1), ([6], 15), ([4, 2], 3), ([2, 2, 2], 1)]:
        degree = sum(powers)
        numerator = int(np.prod(np.stack([rows[:, i] ** power for i, power in enumerate(powers)]), axis=0).sum())
        actual = F(numerator, 2 ** degree)
        denominator = 1
        for j in range(degree // 2):
            denominator *= 8 + 2 * j
        expected = F(len(rows) * norm ** (degree // 2) * wick, denominator)
        require(actual == expected, 'spectral exact check at original line 48')
        full_moments.append({'shell': name, 'full_vectors': len(rows), 'powers': powers, 'moment': str(actual)})
predecessor = ROOT / 'research/niemeier-lattices/workbench/helper-routes/compensation_rank.py'
old = json.loads(subprocess.check_output([sys.executable, '-B', str(predecessor)], text=True))
require(old['status'] == 'PASS_FULL_COMPENSATION_RANK', 'spectral exact check at original line 53')
probe = np.unique(np.concatenate([np.arange(0, 2160, 97), np.arange(2160, len(P), 719)]))
t = P[probe] @ P.T // 4
num = t ** 3 - 4 * t
checks = []
for offset in (0, 8):
    x = P[:, offset:offset + 8]
    y = P[:, 8 - offset:16 - offset]
    h = 10 * x[:, 0] ** 3 - 3 * np.sum(x * x, axis=1) * x[:, 0]
    mix = y[:, 0] * (x[:, 0] ** 2 - x[:, 1] ** 2)
    require(np.array_equal(num @ h, 48 * 39 * h[probe]), 'spectral exact check at original line 63')
    require(np.array_equal(num @ mix, 48 * 45 * mix[probe]), 'spectral exact check at original line 64')
    single = (x * x).sum(1) == 16
    rootroot = (x * x).sum(1) == 8
    R = np.stack([x[:, 0] * single, x[:, 0] * rootroot], axis=1)
    M = np.array([[9, -240], [-18, -195]], dtype=np.int64)
    require(np.array_equal(num @ R, 48 * R[probe] @ M), 'spectral exact check at original line 68')
    checks.append({'block': offset // 8, 'probe_rows': len(probe), 'pure_harmonic_eigenvalue': 39, 'mixed_eigenvalue': 45, 'radial_action_matrix': M.tolist()})
walsh_path = ROOT / 'research/h6-independent-audit/walsh/results.json'
walsh = json.loads(walsh_path.read_text())
hist = {int(k): v for k, v in walsh['pairing_histogram'].items()}
require(sum(hist.values()) == len(P) ** 2 == walsh['ordered_pairs_checked'], 'spectral exact check at original line 73')
trace2 = sum((F(count * (t ** 3 - 4 * t) ** 2, 48 ** 2) for t, count in hist.items()))
require(trace2 == F(old['trace_square']) == 2222640, 'spectral exact check at original line 75')
require(F(39 ** 2 * 224 + 45 ** 2 * 560 + ((-186) ** 2 - 2 * -6075) * 16) == trace2, 'spectral exact check at original line 76')
require(1 + 186 - 6075 == -5888, 'spectral exact check at original line 77')
off_diagonal_count = sum(v for k, v in block_counts.items() if k != 2)
require(off_diagonal_count == 14280 and off_diagonal_count != 28560,
        "canonical quotient block-count negative control")
ai, aj = next((i, j) for i in range(120) for j in range(120) if S[i, j] == 1)
left, right = ai*240, aj*240
pairing = int(rr[left] @ rr[right] // 4)
require(pairing == 3 and left != right, "off-diagonal sign fixture")
compensation = -F(pairing**3 - 4*pairing, 48)
require(compensation == -F(5,16) and compensation != F(5,16),
        "reversed compensation-block sign negative control")
result = {'status': 'PASS_CORRECTED_BLOCKS_AND_COMPENSATION_SPECTRUM', 'ports': len(P), 'canonical_a_lines': len(a), 'signed_b_roots': len(b), 'ordered_block_counts_by_signed_s': dict(sorted(block_counts.items())), 'full_signed_root_neighbours': dict(sorted(full_counts.items())), 'corrected_off_diagonal_per_a_line': {'s_0': 63, 'abs_s_1': 56, 'total': 119}, 'corrected_ordered_off_diagonal_blocks': 120 * 119, 'diagonal_blocks': 120, 'unordered_off_diagonal_block_pairs': 120 * 119 // 2, 'predecessor_wrong_ordered_off_diagonal_blocks': 28560, 'modular_feature_rank_witnesses': ranks, 'independent_full_antipodal_shell_moments': full_moments, 'kernel_spectrum': old['kernel_spectrum'], 'kernel_rank': 816, 'compensation_rank_over_real_numbers': 30960, 'binary_support_rank_over_F2': walsh['binary_rank'], 'operator_action_diagnostics': checks, 'trace': old['trace'], 'trace_square_from_exhaustive_pairing_histogram': str(trace2), 'source_pairing_histogram_sha256': hashlib.sha256(walsh_path.read_bytes()).hexdigest(), 'radial_polynomial_at_1': -5888, 'scope': 'Exact moment argument plus independent exact feature-rank witnesses and exhaustive histogram trace-square cross-check; no dense 30960-square real matrix rank calculation. F2 support rank16 does not bound real compensation rank. Full real rank lower-bounds scalar rank-one rectangle terms, not reusable arithmetic DAG helpers.', 'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [predecessor, ROOT / 'research/niemeier-lattices/code/e8_cubed.py', ROOT / 'research/h6-banked-breakeven/structure2.py']}, 'environment': {'python': sys.version, 'numpy': np.__version__, 'platform': platform.platform()}}
result['off_diagonal_compensation_sign_fixture'] = {'rootroot_rows': [left,right], 't': pairing, 'correct_I_minus_K': str(compensation), 'rejected_positive_f': '5/16'}
result['negative_controls'] = {'doubled_quotient_block_count': 28560, 'reversed_compensation_block_sign': '5/16'}
Path(__file__).with_name('results.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print(json.dumps({k: result[k] for k in ['status', 'ordered_block_counts_by_signed_s', 'corrected_ordered_off_diagonal_blocks', 'trace_square_from_exhaustive_pairing_histogram', 'kernel_rank', 'compensation_rank_over_real_numbers']}))
