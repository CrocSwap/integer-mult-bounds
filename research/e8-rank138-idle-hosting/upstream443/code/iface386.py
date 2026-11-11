"""Interface check of a bitE8/1 word against PR #386's local-stream conditions (our own reimplementation, data semantics
from #386's PROOF.txt; no #386 code run): export to PR249 records (our export249), replay forward and reflected streams
(reverse order, U -> U-perp, ERASE -> fresh COPY), F2 on all local columns + private centre, 9 copies of rank 8,
equal forward/reverse paid histograms, cancellation-free row l1 bounds and the nine-stage prefix 2^18 cf^5 cb^4 < 2^192,
helper initial/final frames (0 / FULL in #386; kernel pivots start at their entrance).  usage: iface386.py WORD.json.gz"""
import sys, os, json, tempfile
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e8core import load_word
from export249 import export
H = 8
def check(c, allow=int(os.environ.get("PREFIX_ALLOW", "192"))):
    st, frames, rec = export(c, tempfile.mkdtemp())
    v, n = st['v'], st['n']; dims = {int(k): z['dim'] for k, z in frames.items()}
    initial = [st['initial'][str(i)] for i in range(n)]; final = [st['final'][str(i)] for i in range(n)]
    nz_start = Counter(dims[initial[i]] for i in range(2 * v, n)); assert all(dims[final[i]] == H for i in range(2 * v, n))
    out = {}
    for reverse in (False, True):
        cur = (final if reverse else initial)[:] + [-1]; val = [1 << i for i in range(n)] + [0]
        norm = [1] * n + [0]; mx = 1; centre = None; hist = Counter(); copies = adds = 0
        dim = (lambda f: H - dims[f]) if reverse else (lambda f: dims[f])
        for op, x, y, cc, f, z in (reversed(rec) if reverse else rec):
            if op == 0:
                old, new = (cc, y) if reverse else (y, cc)
                assert cur[x] == old and dim(new) - dim(old) == f >= 0; cur[x] = new
                if f: hist[f] += 1
            elif op == 1:
                assert cur[x] == cur[y] == f and x != y and x < n
                if centre is not None: assert x != centre
                if y == n: assert centre is not None
                if cc & 1: val[x] ^= val[y]
                norm[x] += abs(cc) * norm[y]; mx = max(mx, norm[x]); adds += 1
            elif op == (3 if reverse else 2):
                assert centre is None and y == n and cur[x] == cc and val[n] == 0
                r = abs(dim(cc) - dim(f)); assert r == 8
                centre = x; cur[n] = f; val[n] = val[x]; norm[n] = norm[x]; hist[r] += 1; copies += 1
            else:
                assert centre == x and y == n and cur[x] == cc and cur[n] == f and val[n] == val[x]
                val[n] = 0; norm[n] = 0; cur[n] = -1; centre = None
        assert centre is None and copies == 9 and cur[:n] == (initial if reverse else final)
        for i in range(n): assert val[i] == (1 << i) ^ ((1 << (i - v)) if v <= i < 2 * v else 0)
        out['reverse' if reverse else 'forward'] = dict(adds=adds, copies=copies, row_l1=mx, hist=dict(sorted(hist.items())))
    assert out['forward']['hist'] == out['reverse']['hist']
    cf, cb = out['forward']['row_l1'], out['reverse']['row_l1']; pre = (1 << 18) * cf ** 5 * cb ** 4
    return dict(n=n, R=st['R'], helper_start_dims=dict(sorted(nz_start.items())), streams=out, prefix_bits=pre.bit_length(), prefix_ok=pre < 1 << allow, prefix_allow=allow)
if __name__ == '__main__':
    print(json.dumps(check(load_word(sys.argv[1]))))
