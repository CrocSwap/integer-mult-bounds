"""Part A: q-image group embedding at fine theta (PR1786 regime), on a stream/tape model.

Independent of the PR's code. Checks
 (1) the membership predicate of phase_fusion_note.tex:258-262 for every target k,
     for all s in [t/2, t) at small t, and for fine-theta primes s (theta in [1/(4P^2), 1/(2P^2-1)]) at larger t;
 (2) q increments are 1 or 2, holes = t-s, phase-cell lengths ~ 1/theta (so B=p^xi < cell holds when xi<2);
 (3) a one-pass group embedding of g axes with prefix/suffix spectators on a 2-tape stream equals the
     composition of g per-axis embeddings, and its head travel is (input + output) records, independent of g.
"""
import itertools, json, math, random, sys

def qmap(j, s, t): return (2 * t * j + s) // (2 * s)          # floor(t j / s + 1/2)
def cdiv(a, b): return -((-a) // b)
def inv(k, s, t):
    j = max(0, cdiv(s * (2 * k - 1), 2 * t))
    return j if (j < s and 2 * t * j < s * (2 * k + 1)) else None

def is_prime(n):
    if n < 2: return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0: return n == p
    d, r = n - 1, 0
    while d % 2 == 0: d //= 2; r += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True

def check_axis(s, t):
    img = [qmap(j, s, t) for j in range(s)]
    assert all(b - a in (1, 2) for a, b in zip(img, img[1:])), (s, t)
    assert img[0] == 0 and img[-1] < t
    pre = [inv(k, s, t) for k in range(t)]
    hit = {k: j for k, j in enumerate(pre) if j is not None}
    assert sorted(hit) == img and all(img[j] == k for k, j in hit.items()), (s, t)
    holes = t - s
    # cell lengths: maximal runs with q_j - j constant
    runs, cur = [], 1
    for a, b in zip(img, img[1:]):
        if b - a == 1: cur += 1
        else: runs.append(cur); cur = 1
    runs.append(cur)
    return holes, runs

out = {}
# (1) exhaustive small t
n_axes = 0
for e in range(1, 11):
    t = 1 << e
    for s in range(max(1, t // 2), t + 1):
        check_axis(s, t); n_axes += 1
out['exhaustive_axes_checked'] = n_axes

# (1b,2) fine-theta primes: theta = t/s - 1 in [1/(4P^2), 1/(2P^2-1)]
fine = []
for e, P in [(16, 8), (18, 12), (20, 16), (21, 30)]:
    t = 1 << e
    lo = math.ceil(t / (1 + 1 / (2 * P * P - 1))); hi = math.floor(t / (1 + 1 / (4 * P * P)))
    primes = [s for s in range(lo, hi + 1) if is_prime(s)]
    if not primes: fine.append(dict(t=t, P=P, primes=0)); continue
    s = primes[len(primes) // 2]
    holes, runs = check_axis(s, t)
    theta = t / s - 1
    inner = runs[1:-1]
    fine.append(dict(t=t, P=P, s=s, theta=theta, primes_in_window=len(primes), holes=holes,
                     min_inner_cell=min(inner), max_cell=max(runs), one_over_theta=1 / theta,
                     cells_at_least_2P2_minus_2=min(inner) >= 2 * P * P - 2))
out['fine_theta_axes'] = fine

# (3) one-pass group embedding with prefix/suffix spectators on a stream model
def stream_group_embed(data, shape, grp, sizes):
    """data: flat list in lexicographic order of `shape`; axes in grp (consecutive) go s->t.
    One sequential read pass + one sequential write pass. Returns output and (reads, writes)."""
    a0, a1 = grp[0], grp[-1] + 1
    pre = math.prod(shape[:a0]); suf = math.prod(shape[a1:])
    reads = writes = 0; outl = []; pos = 0
    for _ in range(pre):
        for k in itertools.product(*(range(t) for s, t in sizes)):
            if all(inv(kk, s, t) is not None for kk, (s, t) in zip(k, sizes)):
                outl.extend(data[pos:pos + suf]); pos += suf; reads += suf
            else:
                outl.extend([0] * suf)
            writes += suf
    assert pos == len(data)
    return outl, reads, writes

def ref_embed(arr, shape, axis, s, t):
    """per-axis embedding via an explicit index map (reference, not a stream)."""
    newshape = list(shape); newshape[axis] = t
    out = [0] * math.prod(newshape)
    for idx in itertools.product(*(range(n) for n in shape)):
        src = 0
        for i, n in zip(idx, shape): src = src * n + i
        j = list(idx); j[axis] = qmap(idx[axis], s, t)
        dst = 0
        for i, n in zip(j, newshape): dst = dst * n + i
        out[dst] = arr[src]
    return out, newshape

rng = random.Random(1673)
grp_res = []
for trial in range(6):
    g = rng.choice([2, 3, 4])
    sizes = []
    for _ in range(g):
        t = rng.choice([8, 16]); s = rng.randint(t // 2 + 1, t - 1); sizes.append((s, t))
    pre_n, suf_n = rng.choice([1, 2, 3]), rng.choice([1, 2, 3])
    shape = [pre_n] + [s for s, t in sizes] + [suf_n]
    data = [rng.randint(1, 10**6) for _ in range(math.prod(shape))]
    outl, r, w = stream_group_embed(data, shape, list(range(1, g + 1)), sizes)
    ref, sh = data, shape
    for i, (s, t) in enumerate(sizes): ref, sh = ref_embed(ref, sh, 1 + i, s, t)
    assert outl == ref
    S = math.prod(s for s, t in sizes); T = math.prod(t for s, t in sizes)
    seq_moves = 0; cur = list(shape)
    for i, (s, t) in enumerate(sizes):  # g per-axis passes would each read+write the whole current tensor
        seq_moves += math.prod(cur); cur[1 + i] = t; seq_moves += math.prod(cur)
    grp_res.append(dict(g=g, sizes=sizes, input=len(data), one_pass_moves=r + w, per_axis_pass_moves=seq_moves,
                        ratio=(r + w) / len(data), T_over_S=T / S))
out['group_embedding'] = grp_res
print(json.dumps(out, indent=1))
json.dump(out, open(sys.argv[1], 'w'), indent=1)
