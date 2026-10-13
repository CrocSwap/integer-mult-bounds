"""Nominate the frozen whole-residual hosting selection (data/eleven/hosting.json) for this word: PR #442's integer
programme (hosting_core.solve, DaysSky) on the eleven-stage schedule of PR #445/#472 with the eight replicas pooled as
in PR #472 (copies 2*V*T per idle child), every helper residual forced onto an idle child (all R*T residuals of each
stage hosted; no banks).  The verifier never runs this: it only replays the frozen selection (hosting_core.expand)
and audits it.  Needs scipy.
usage: host_select.py WORD.json.gz OUT_hosting.json [pad_value]
Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0."""
import gzip
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "code" / "hub" / "idle-axis-hosting"))
import hosting_core as HC  # noqa: E402

H, L, K, T, M, V = 8, 11, 5, 8, 78, 120


def recipe():   # PR #445 emit.py recipe(), verbatim logic
    out = [dict(kind='local', stage=0, pair=0, reverse=False)]; stage = 1
    for j in range(K):
        out.append(dict(kind='local', stage=stage, pair=j, reverse=True)); stage += 1
        if j < K - 1: out.append(dict(kind='bridge', dst=j, src=j + 1, coefficient=1))
        out.append(dict(kind='local', stage=stage, pair=j, reverse=False)); stage += 1
        if j < K - 1: out.append(dict(kind='bridge', dst=j, src=j + 1, coefficient=-1))
    for j in reversed(range(K - 1)): out.append(dict(kind='bridge', dst=j + 1, src=j, coefficient=1))
    out.append(dict(kind='exchange'))
    return out


def schedule():  # the idle events exactly as PR #445/#472 emit.py inserts them
    levels = [-1] * K; sched = []; idx = 0
    for e in recipe():
        if e['kind'] == 'local':
            s, p = e['stage'], e['pair']; levels[p] = s
            sched.append(dict(kind='local', stage=s, pair=p))
            idles = []
            if s in range(1, 2 * K - 1, 2):
                j = (s + 1) // 2; levels[j] = s; idles.append((j, 7 * (s + 1)))
            elif s in range(2, 2 * K, 2):
                j = s // 2; levels[j] = s; idles.append((j, 7))
            elif s == 2 * K:
                for j in range(K):
                    idles.append((j, 7 * (2 * K - levels[j]))); levels[j] = 2 * K
            for j, r in idles:
                sched.append(dict(kind='idle', idx=idx, pair=j, rank=r)); idx += 1
        elif e['kind'] == 'bridge':
            sched.append(dict(kind='bridge', dst=e['dst'], src=e['src']))
    return sched


def main():
    w = json.loads(gzip.decompress(Path(sys.argv[1]).read_bytes()))
    R = w['R']
    assert all(f == w['start'][2 * V] for f in w['start'][2 * V:]) and not w['frames'][w['start'][2 * V]], \
        "this nominator assumes every helper starts at frame zero (residual width 8)"
    win = {i: x for i, x in HC.windows(schedule()).items() if x[1] and x[2]}
    avail = Counter()
    for s in range(L):
        avail[s, H] += R * T
    pad = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    ys, zs, val = HC.solve(win, 2 * V * T, dict(avail), M, pad_value=pad, group={H: 10 ** 9})
    used = Counter()
    for (i, wd, s), n in zs.items():
        used[s, wd] += n
    assert all(used[k] == a for k, a in avail.items()), "not every residual hosted"
    out = Path(sys.argv[2])
    if out.exists():
        out.unlink()
    HC.save_selection(out, 'bit', ys, zs, val)
    print("selection saved:", out, "windows", len(win), "proxy saving", val)


if __name__ == "__main__":
    main()
