"""Optional exact hook comparison with an immutable local predecessor."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

ENGINE_SHA256 = '99ff0beccd9a4e94cc607e02114d62b8ce0ea57ee00748b07ce0a0af91aec85e'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def run(src):
    require(hashlib.sha256(src.read_bytes()).hexdigest() == ENGINE_SHA256,
            'immutable predecessor hash mismatch')
    # -B prevents new caches but does not prevent reading an existing cache.
    # Refuse either cache location so the source hash binds executed code.
    optimization = str(sys.flags.optimize) if sys.flags.optimize else ''
    cache = Path(importlib.util.cache_from_source(str(src), optimization=optimization))
    require(not cache.exists() and not src.with_suffix('.pyc').exists(),
            'remove no files automatically: replay requires an uncached source location')
    spec = importlib.util.spec_from_file_location('pinned_hook', src)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    D = m.lift_direction(1)
    K = m.compose(m.lift_direction(4), m.compose(m.lift_direction(2), D))
    h = [((x & 1) << 2) | (x & 2) | ((x & 4) >> 2) for x in range(8)]
    g = list(m.V_PERM)

    def cp(a, b):
        return [a[b[x]] for x in range(8)]

    hp = [list(range(8)), h, g, cp(h, g), cp(g, h), cp(h, cp(g, h))]
    phases = [m.I_POWERS[(x.bit_count() + sum(t.bit_count() for t in sub)) % 4]
              for x, sub in m.BASIS]

    def ph(cols):
        return [{i: m.mul(phases[i], v) for i, v in c.items()} for c in cols]

    def scale(cols, k):
        return [{i: m.mul(k, v) for i, v in c.items()} for c in cols]

    begin = ph(D)
    cases = [
        ('hecke', hp, [(k, 0) for k in [2, -2, 1, 1, 1, 1]], 144),
        ('hecke_plus_U_over_16', hp + [list(m.U_PERM)],
         [(k, 0) for k in [8, -8, 4, 4, 4, 4, 1]], 160),
        ('pencil_1_over_16', [list(m.U_PERM), list(m.V_PERM)], [(16, 0), (1, 0)], 160),
        ('pencil_minus_1_over_16', [list(m.U_PERM), list(m.V_PERM)], [(16, 0), (-1, 0)], 160),
        ('pencil_i_over_16', [list(m.U_PERM), list(m.V_PERM)], [(16, 0), (0, 1)], 160),
        ('pencil_minus_i_over_16', [list(m.U_PERM), list(m.V_PERM)], [(16, 0), (0, -1)], 160),
    ]
    reports, timing = [], []
    for name, perms, coeff, want in cases:
        start = time.perf_counter()
        mid = [{} for _ in D]
        for perm, k in zip(perms, coeff):
            mid = m.add_columns(mid, scale(m.apply_permutation(perm, begin), k))
        F = m.compose(D, ph(mid))
        rows = []
        for mask in m.CUTS:
            ix = m.cut_indices(mask)
            fr, kr = m.project(F, ix), m.project(K, ix)
            phi, joint = m.rank_exact(fr), m.rank_exact(kr + fr)
            require(phi == want and joint == 224, 'case ' + name + ', cut ' + str(mask))
            rows.append({'mask': mask, 'prefix_rank': phi, 'target_joint_rank': joint})
            print(json.dumps({'case': name, **rows[-1]}), flush=True)
        reports.append({'case': name, 'cuts': rows})
        timing.append({'case': name, 'elapsed_seconds': round(time.perf_counter() - start, 3)})
    return {'status': 'PASS_EXACT_HOOK_COMPARISON', 'engine_sha256': ENGINE_SHA256,
            'representation': 'V tensor exterior^4 V, dimension 560 at width five',
            'cases': reports, 'new_kappa': False}, timing


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--engine', type=Path,
                   default=Path(__file__).resolve().parent.parent / 'sources' / 'hook_engine.py')
    p.add_argument('--out', type=Path)
    p.add_argument('--check', type=Path)
    p.add_argument('--timing', type=Path)
    a = p.parse_args()
    report, timing = run(a.engine)
    if a.check:
        require(json.loads(a.check.read_text(encoding='utf-8')) == report,
                'stored hook result mismatch')
    if a.out:
        a.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    if a.timing:
        a.timing.write_text(json.dumps({'scope': 'single exact replay timing',
                                       'interpreter_mode': {'isolated': bool(sys.flags.isolated),
                                                            'optimization': sys.flags.optimize,
                                                            'dont_write_bytecode': sys.dont_write_bytecode},
                                       'records': timing},
                                       indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'cases': len(report['cases']),
                      'timing': timing}, sort_keys=True))


if __name__ == '__main__':
    main()
