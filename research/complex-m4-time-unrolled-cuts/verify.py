"""Re-check research/complex-m4-time-unrolled-cuts.

Standard library only. Exact integer and Gaussian-integer arithmetic. Leaves no files behind.

  --part main      (under 1 s)  builds the 35 x 35 plane matrices of the block-4 calls and of the target from their
                   definitions; checks their structure; evaluates two end-state chain rows (n0's scrambled-program order,
                   45 < 48; n0 ending in the two-bit call 3, 47 < 48); checks every certificate of data/n0_certs.txt
                   (324, all 3,628,800 orders of n0) and of data/two-in-seven/ (3,098, all 5,040 orders of each of
                   the 38 lists) exactly, with coverage; checks the sha256 of every data file; prints
                   PASS_COMPLEX_M4_TIME_UNROLLED_CUTS_MAIN
  --part recount   (about 4 s)  the plane rows at the 1,524 sets of data/cut_sets_and_images.txt leave exactly
                   1,097 lists of 10 directions for W = 3 (80 orbits under the 24 bit permutations, none of 9) and
                   398 lists of 7 for W = 2 (38 orbits, none of 6), and the orbit representatives are the lists
                   of data/ten-move-orbit-lists.txt and data/two-in-seven/schedules.txt; prints
                   PASS_COMPLEX_M4_TIME_UNROLLED_CUTS_RECOUNT
  --part controls  (under 1 s)  each corrupted certificate file or false claim must be rejected; prints
                   PASS_COMPLEX_M4_TIME_UNROLLED_CUTS_CONTROLS

The model (README section 3). At width f = 3 the antisymmetric part Lambda^3(C^16) has the basis
a(T) = e_x ^ e_y ^ e_z, T = {x < y < z}; T lies in the plane {0, x+y, x+z, y+z}, one of 35 two-dimensional subspaces
of F_2^4. For the trivial shift character, v(D) = sum_z S_z a(T_D) (T_D the smallest triple of plane D) spans the
part of plane D's block on which every shift acts as 1; (2 C_w)^3 maps v(E) into the span of the v(D), with
2 C_w e_x = (1+i) e_x + (1-i) e_(x+w); M_w[D, E] is that coefficient. The other 15 characters give the same ranks
of every block (they are rescalings; checked for every call in the source repository's checker, and for one call
here). The target is K = C_1 C_2 C_4 C_8, so its plane matrix is M_1 M_2 M_4 M_8.

End-state chain row (README section 4): for every chain U_s <= ... <= U_0 of plane sets and every program of the
game without address maps with calls along w_1..w_s,  sum_t rank M_(w_t)[U_t, U_(t-1)^c] >= W rank K[U_s, U_0^c].
A certificate line  CERT <suffix> SET A CHAIN c_0,..,c_m COST x RHS y  says: every order that ends with the suffix
violates the row whose chain stays at c_0 through the other calls and then steps c_0 > c_1 > ... > c_m = A with the
suffix calls; x is its left side and y its right side. Coverage: the certified suffixes are pairwise not nested, so
the sets of orders they cover are disjoint, and the numbers of orders they cover add up to all orders of the list.
"""
import hashlib
import itertools
import math
import pathlib
import sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "data"
NA, NP = 16, 35

SHA256 = {
    "data/cut_sets_and_images.txt": "576b86be6e355dbe8e89ebca8276ec55224eda503e54c1264bfb9aa9d71cc74f",
    "data/n0_certs.txt": "dc7c314796ed75f64d96fb84bdaf583049b593c794d485a668d55750f6a3ab80",
    "data/ten-move-orbit-lists.txt": "20dbdf383467f16a613c8faaf7177e2009d1ce3d3657a64cef9b0624da135902",
    "data/two-in-seven/final_00.txt": "a5986ac273898d34bf09d1cc08cde3fefbd8576c6080784f18b3e743c785f9eb",
    "data/two-in-seven/final_01.txt": "9f132885a2c46891950450561bfee2db60f939de9be7798dc4c8285a953a4b68",
    "data/two-in-seven/final_02.txt": "e0a10609c03c392375336ad2893d2a6e8b7a223a4bc3641929491505008b28b2",
    "data/two-in-seven/final_03.txt": "c62189d06a24e64c33a5ec3ed236188618c19b7154758e8b0d1fa2f13525d0e3",
    "data/two-in-seven/final_04.txt": "c9a606864aa77893fa1e07be5b697066b7bc4ee2f5fc866d120ee4ce12261919",
    "data/two-in-seven/final_05.txt": "754bd9ddc16fa8a1dff5565e2f70f2670d6c8ad49b043092054bb499d1ee498b",
    "data/two-in-seven/final_06.txt": "0c3d1e1562ff016b1d7b01b4a1bd90ac2369d82f7187ce9577876cc7d6845409",
    "data/two-in-seven/final_07.txt": "cfb9a0a5113b37011e43758025374d83311af3a16947abd368448321ee4cf410",
    "data/two-in-seven/final_08.txt": "090e35ab9abab8dfd2d3c131fe14ed08e0e0cf49f60667862717dd5a2c971da8",
    "data/two-in-seven/final_09.txt": "a7f7c4464aedc6d3077b62f045c3bcc8ffa1e87ef2a461d0533be4d7badb1ec4",
    "data/two-in-seven/final_10.txt": "51e69fa6be0f15bec624c3da9acf2a61f399d050dd719e2a97119dfc2c6079b6",
    "data/two-in-seven/final_11.txt": "6993f0845838a250d7e5ee5dafb1660c0c25f32df5c17f5e2c8e403afa6a7692",
    "data/two-in-seven/final_12.txt": "760899e874e607cb76065c296c8bd18330d7a59596afcc1bd6db3c42b196336a",
    "data/two-in-seven/final_13.txt": "824daf248c114dfdf06b4ff9004ba580c91c51be4e59fe4b86a1e58c12346f92",
    "data/two-in-seven/final_14.txt": "b2670acdae0e434b80829324a786849c50a190cab6e549e5d6de654fb84237c2",
    "data/two-in-seven/final_15.txt": "0d8fc29e60fc8282647f000fcdebba260f148f151d6f58ef91887f816d6982ee",
    "data/two-in-seven/final_16.txt": "9abbdfcf5eef6babb83bc81fbe6fe1456447da70865968e03bcd40b7ffcbfc3f",
    "data/two-in-seven/final_17.txt": "06e6ca01f3fc8791ea49d3f3882131d64412d8564570bd7389c59ce78082df9f",
    "data/two-in-seven/final_18.txt": "6e923de287ae2442a24cfa447ebcfb67b3f5634a01f6ceefe42116b35d64b05e",
    "data/two-in-seven/final_19.txt": "dcf7ab3c213ba51c3c74625d99a3463b7f1cc0b42220b897f64f5b6c034b35ab",
    "data/two-in-seven/final_20.txt": "045af93d4a399ddecfa1798a96f3eaba3dc34ade88febbd74c05ff71920476f6",
    "data/two-in-seven/final_21.txt": "a6df995780150ec73743582f3183152bce5abaefad39e7609659050d2aa24fe8",
    "data/two-in-seven/final_22.txt": "7de2060f4fdaebe1790ad60d19b47e3cbc334eb2ce4adacb7e00a97b8a0cfaf0",
    "data/two-in-seven/final_23.txt": "14de7c6a39b126e3a8509168d7cb124120f74504acb4bc8fcdd270a5f37b90b3",
    "data/two-in-seven/final_24.txt": "22b9a649531bcbede5d225b5f40be41d9e0f8338b5e265aee310ebbc0aa019cf",
    "data/two-in-seven/final_25.txt": "72d85ea2ce4649a362e4600d96624f44728688f2b1298f1fbc2cf865e8a22e05",
    "data/two-in-seven/final_26.txt": "137bb70581857204bd10d7115f5778991a0b138a1957edcbb1fe0ba235e1bae9",
    "data/two-in-seven/final_27.txt": "a2baf3556a259f47c8030f6d79dfee855ccb654f10e6c63a7204e9f36f80b66a",
    "data/two-in-seven/final_28.txt": "5cdae1c0b7736c97ef8be04a4ace453ea20809ca6af4d66dc2d5cb13fc650efd",
    "data/two-in-seven/final_29.txt": "da44269c7377a4ea1f1857b5f63c798d81df5e85fb837cd93767e78e096dd6bd",
    "data/two-in-seven/final_30.txt": "842a411331e57c51ebb4e47a6cd69c4df9b31496ba0ba2e1f7b2d9f0be0ee7a5",
    "data/two-in-seven/final_31.txt": "86ba9c03e27698dfdfa60d71af114fe89ca994820a127e21e23a90464cff82f9",
    "data/two-in-seven/final_32.txt": "6c2ad0b2f04b879873b8ff36d06a43449960ffc6e3c67c41579f96cccef82da0",
    "data/two-in-seven/final_33.txt": "126d83ce5c7f28befb351d2d8e85a9588400e3e9de4c8d5813943bc157ebf6a6",
    "data/two-in-seven/final_34.txt": "6ef83f5f753d4d62ca4150caefba452db359dd450695d97ecff45a6908440609",
    "data/two-in-seven/final_35.txt": "b9b421d4c5f835cbd5d119e0ffbcdba29a50938b1857d4fc9efe28c54c80cc32",
    "data/two-in-seven/final_36.txt": "4eaca7fc0d5f53455caa54b71794ad8ff50549490e2226679fbb7b720141ae1d",
    "data/two-in-seven/final_37.txt": "7a8e50b089dfe11ee9d31fc7b0f5fd7f620cbb7d5fc644b95681f3f29bad0c0d",
    "data/two-in-seven/schedules.txt": "a3e7abdd6ec40d8d012f692746ee2bb0e070459a2bfcd6d622fe830cc2c87b1e",
}


# ---------------------------------------------------------------- the model, from the definitions
def gm(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def ga(a, b):
    return (a[0] + b[0], a[1] + b[1])


Z = (0, 0)
TRIPLES = list(itertools.combinations(range(NA), 3))


def plane_of(t):
    x, y, z = t
    return frozenset({0, x ^ y, x ^ z, y ^ z})


PLANES = sorted({plane_of(t) for t in TRIPLES}, key=lambda d: sorted(d))
REF = [min(t for t in TRIPLES if plane_of(t) == d) for d in PLANES]


def wedge(xs, c):
    if len(set(xs)) < 3:
        return None
    s = sorted(xs)
    perm = [xs.index(v) for v in s]
    inv = sum(1 for i in range(3) for j in range(i + 1, 3) if perm[i] > perm[j])
    return tuple(s), (c if inv % 2 == 0 else (-c[0], -c[1]))


def apply3(single, vec):
    out = {}
    for t, c in vec.items():
        for (y1, c1), (y2, c2), (y3, c3) in itertools.product(single(t[0]), single(t[1]), single(t[2])):
            r = wedge([y1, y2, y3], gm(gm(gm(c, c1), c2), c3))
            if r is not None:
                out[r[0]] = ga(out.get(r[0], Z), r[1])
    return {k: v for k, v in out.items() if v != Z}


def chi(u, z):
    return -1 if bin(u & z).count("1") % 2 else 1


def vbasis(d, u):
    out = {}
    for z in range(NA):
        for k, v in apply3(lambda x: [(x ^ z, (1, 0))], {REF[d]: (1, 0)}).items():
            s = chi(u, z)
            out[k] = ga(out.get(k, Z), (s * v[0], s * v[1]))
    return {k: v for k, v in out.items() if v != Z}


def call_matrix(w, u):
    vb = [vbasis(d, u) for d in range(NP)]
    for d in range(NP):
        assert vb[d].get(REF[d]) == (1, 0) and len(vb[d]) == 16
    cols = []
    for e in range(NP):
        img = apply3(lambda x: [(x, (1, 1)), (x ^ w, (1, -1))], vb[e])
        coef = [img.get(REF[d], Z) for d in range(NP)]
        rec = {}
        for d in range(NP):
            if coef[d] != Z:
                for k, v in vb[d].items():
                    rec[k] = ga(rec.get(k, Z), gm(coef[d], v))
        assert {k: v for k, v in rec.items() if v != Z} == img, "image not in the span of the plane vectors"
        cols.append(coef)
    return [[cols[e][d] for e in range(NP)] for d in range(NP)]


def build():
    m = {w: call_matrix(w, 0) for w in range(1, NA)}
    assert all(v[1] == 0 for w in m for r in m[w] for v in r), "trivial-character matrices must be real"
    real = {w: [[v[0] for v in r] for r in m[w]] for w in m}

    def mm(a, b):
        return [[sum(a[i][t] * b[t][j] for t in range(NP)) for j in range(NP)] for i in range(NP)]

    k = mm(mm(mm(real[1], real[2]), real[4]), real[8])
    return real, k


def rank_int(mat, rows, cols):
    a = [[mat[i][j] for j in cols] for i in rows]
    a = [r for r in a if any(r)]
    if not a or not cols:
        return 0
    rk = 0
    for c in range(len(cols)):
        q = next((i for i in range(rk, len(a)) if a[i][c] != 0), None)
        if q is None:
            continue
        a[rk], a[q] = a[q], a[rk]
        p = a[rk]
        pv = p[c]
        for i in range(len(a)):
            if i != rk and a[i][c] != 0:
                f = a[i][c]
                r = [pv * x - f * y for x, y in zip(a[i], p)]
                g = 0
                for x in r:
                    g = math.gcd(g, x)
                a[i] = [x // g for x in r] if g > 1 else r
        rk += 1
        if rk == len(a):
            break
    return rk


class Model:
    def __init__(self):
        self.m, self.k = build()
        self.cache = {}

    def cost(self, w, u, uprev):
        rows = tuple(sorted(u))
        cols = tuple(j for j in range(NP) if j not in uprev)
        key = (w, rows, cols)
        if key not in self.cache:
            mat = self.k if w == "K" else self.m[w]
            self.cache[key] = rank_int(mat, rows, cols) if rows and cols else 0
        return self.cache[key]


def mask(x):
    return frozenset(i for i in range(NP) if x >> i & 1)


def arrangements(c):
    r = math.factorial(sum(c.values()))
    for v in c.values():
        r //= math.factorial(v)
    return r


def check_file(md, lines, sched, w_arrays):
    """True when every certificate is valid and the certificates cover every order of sched."""
    full = Counter(sched)
    sufs = []
    for line in lines:
        if not line.startswith("CERT "):
            continue
        f = line.split()
        if len(f) != 10 or f[2] != "SET" or f[4] != "CHAIN" or f[6] != "COST" or f[8] != "RHS":
            return False, "bad line"
        suf = tuple(int(x) for x in f[1].split(","))
        rem = full - Counter(suf)
        if any(Counter(suf)[w] > full[w] for w in suf):
            return False, "suffix not in the list"
        sets = [mask(int(x)) for x in f[5].split(",")]
        if len(sets) != len(suf) + 1 or sets[-1] != mask(int(f[3])):
            return False, "chain shape"
        if any(not sets[i + 1] <= sets[i] for i in range(len(suf))):
            return False, "chain not decreasing"
        left = sum(md.cost(w, sets[0], sets[0]) * n for w, n in rem.items())
        left += sum(md.cost(suf[j], sets[j + 1], sets[j]) for j in range(len(suf)))
        right = w_arrays * md.cost("K", sets[-1], sets[0])
        if not left < right:
            return False, "row not violated"
        if (left, right) != (int(f[7]), int(f[9])):
            return False, "numbers differ from the file"
        sufs.append(suf)
    s = set(sufs)
    if len(s) != len(sufs):
        return False, "duplicate suffix"
    if any(t[k:] in s for t in s for k in range(1, len(t))):
        return False, "nested suffixes"
    if sum(arrangements(full - Counter(t)) for t in s) != arrangements(full):
        return False, "orders not covered"
    return True, "%d certificates, %d orders" % (len(sufs), arrangements(full))


def chain_row(md, order, base, extra, w_arrays=3):
    chain = [base | frozenset(e) for e in extra]
    terms = [md.cost(order[t], chain[t + 1], chain[t]) for t in range(len(order))]
    return terms, w_arrays * md.cost("K", chain[-1], chain[0])


def two_in_seven():
    lists = {}
    for line in (DATA / "two-in-seven" / "schedules.txt").read_text().split("\n"):
        if line.strip():
            i, s = line.split()
            lists[i] = [int(x) for x in s.split(",")]
    return lists


def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)


# ---------------------------------------------------------------- parts
def part_main():
    md = Model()
    # structure: every call matrix is -8 (I - 2Q) with Q a projection of rank 7
    for w in range(1, NA):
        q = [[((8 if i == j else 0) + md.m[w][i][j]) for j in range(NP)] for i in range(NP)]  # 16 Q
        q2 = [[sum(q[i][t] * q[t][j] for t in range(NP)) for j in range(NP)] for i in range(NP)]
        if any(q2[i][j] != 16 * q[i][j] for i in range(NP) for j in range(NP)):
            fail("call %d is not -8(I - 2Q) with Q a projection" % w)
        if rank_int(q, range(NP), range(NP)) != 7:
            fail("projection rank of call %d" % w)
    # one call in a second character: the same rank on a few blocks
    m3 = call_matrix(3, 5)
    for rows in ([0, 1, 2, 3, 4], list(range(10, 25))):
        cols = [j for j in range(NP) if j not in rows]
        sub = [[m3[i][j] for j in cols] for i in rows]
        # Gaussian rank by elimination over Q(i) with fractions avoided: use the real/imaginary stacked form
        stacked = [[v[0] for v in r] + [-v[1] for v in r] for r in sub] + [[v[1] for v in r] + [v[0] for v in r] for r in sub]
        if rank_int(stacked, range(len(stacked)), range(2 * len(cols))) != 2 * rank_int(md.m[3], rows, cols):
            fail("character 5 of call 3 differs in rank")
    print("plane matrices: 15 calls of the form -8(I - 2Q), rank Q = 7; target = M1 M2 M4 M8; one character rechecked")
    a = mask(34125373701)
    t, r = chain_row(md, [3, 6, 2, 8, 5, 12, 1, 10, 4, 9], a, [{1, 7}] * 3 + [{7}] * 2 + [set()] * 6)
    if (sum(t), r) != (45, 48):
        fail("scrambled-program order")
    print("n0, scrambled-program order 3,6,2,8,5,12,1,10,4,9: costs", t, "sum", sum(t), "< right side", r)
    t, r = chain_row(md, [1, 2, 4, 5, 6, 8, 9, 10, 12, 3], mask(31533252720), [{2}] * 10 + [set()])
    if (sum(t), r) != (47, 48):
        fail("n0 ending in 3")
    print("n0 ending in the two-bit call 3: sum", sum(t), "< right side", r)
    ok, why = check_file(md, (DATA / "n0_certs.txt").read_text().split("\n"), [1, 2, 3, 4, 5, 6, 8, 9, 10, 12], 3)
    if not ok or why != "324 certificates, 3628800 orders":
        fail("n0 certificates: " + why)
    print("n0 for W = 3:", why, "-> every order excluded")
    n = 0
    lists = two_in_seven()
    if len(lists) != 38:
        fail("38 lists expected")
    for i, s in sorted(lists.items()):
        ok, why = check_file(md, (DATA / "two-in-seven" / ("final_%s.txt" % i)).read_text().split("\n"), s, 2)
        if not ok or not why.endswith("5040 orders"):
            fail("2 in 7, list %s: %s" % (i, why))
        n += int(why.split()[0])
    if n != 3098:
        fail("3,098 certificates expected")
    print("2 in 7 for W = 2: 38 lists, %d certificates, every one of the 5,040 orders of each excluded" % n)
    found = sorted(DATA.rglob("*.txt"))
    if len(found) != len(SHA256):
        fail("expected %d data files, found %d" % (len(SHA256), len(found)))
    for p in found:
        rel = p.relative_to(HERE).as_posix()
        if SHA256.get(rel) != hashlib.sha256(p.read_bytes()).hexdigest():
            fail("sha256 of " + rel)
    print("sha256: all %d data files match" % len(SHA256))
    print("PASS_COMPLEX_M4_TIME_UNROLLED_CUTS_MAIN")


def bitperms():
    return [[sum(1 << p[j] for j in range(4) if x >> j & 1) for x in range(16)] for p in itertools.permutations(range(4))]


def recount(md, rows, w_arrays, k):
    rows = list(rows)

    def passes(ms):
        for i, (lam, d) in enumerate(rows):
            if sum(lam[w] for w in ms) < d:
                if i:
                    rows.insert(0, rows.pop(i))
                return False
        return True

    bp = bitperms()
    res = {}
    for kk in (k, k - 1):
        surv = [ms for ms in itertools.combinations_with_replacement(range(1, 16), kk) if passes(ms)]
        orbs = sorted(set(min(tuple(sorted(g[w] for w in ms)) for g in bp) for ms in surv))
        res[kk] = (len(surv), orbs)
    return res


def part_recount():
    md = Model()
    masks = sorted(set(int(l.split()[0]) for l in (DATA / "cut_sets_and_images.txt").read_text().split("\n") if l.strip()))
    if len(masks) != 1524:
        fail("1,524 sets expected")
    rows = []
    for x in masks:
        u = mask(x)
        rows.append(([0] + [md.cost(w, u, u) for w in range(1, 16)], md.cost("K", u, u)))
    for w_arrays, k, n_lists, n_orbs in ((3, 10, 1097, 80), (2, 7, 398, 38)):
        r = recount(md, [(lam, w_arrays * d) for lam, d in rows], w_arrays, k)
        if r[k][0] != n_lists or len(r[k][1]) != n_orbs or r[k - 1][0] != 0:
            fail("recount W = %d" % w_arrays)
        if w_arrays == 2 and r[k][1] != sorted(tuple(v) for v in two_in_seven().values()):
            fail("2-in-7 representatives differ from the certificate lists")
        if w_arrays == 3:
            ref = sorted(tuple(int(x) for x in l.split()[1].split(","))
                         for l in (DATA / "ten-move-orbit-lists.txt").read_text().split("\n") if l.strip())
            if r[k][1] != ref or (1, 2, 3, 4, 5, 6, 8, 9, 10, 12) not in ref:
                fail("the 80 representatives differ from data/ten-move-orbit-lists.txt")
        print("W = %d: %d lists of %d directions pass the plane rows, in %d orbits; none of %d"
              % (w_arrays, n_lists, k, n_orbs, k - 1))
    print("PASS_COMPLEX_M4_TIME_UNROLLED_CUTS_RECOUNT")


def part_controls():
    md = Model()
    n0 = [1, 2, 3, 4, 5, 6, 8, 9, 10, 12]
    lines = (DATA / "n0_certs.txt").read_text().split("\n")
    certs = [l for l in lines if l.startswith("CERT ")]
    rejected = 0
    tries = []
    # 1. one certificate dropped: orders uncovered
    tries.append(("one certificate dropped", certs[1:], n0, 3))
    # 2. a claimed cost changed by one
    f = certs[0].split(); f[7] = str(int(f[7]) - 1)
    tries.append(("a claimed cost lowered by one", [" ".join(f)] + certs[1:], n0, 3))
    # 3. a chain that does not shrink
    f = certs[0].split(); ch = f[5].split(",")
    b = next(i for i in range(NP) if not int(ch[0]) >> i & 1)
    ch[-1] = str(int(ch[-1]) | (1 << b)); f[5] = ",".join(ch); f[3] = ch[-1]
    tries.append(("a chain whose last set grows", [" ".join(f)] + certs[1:], n0, 3))
    # 4. the same certificates for 2 arrays: the right side drops
    tries.append(("n0's certificates read with W = 2", certs, n0, 2))
    # 5. the plain 12-call list for 3 arrays is not excluded by n0's certificates
    tries.append(("n0's certificates applied to the plain list", certs, [1, 2, 4, 8] * 3, 3))
    # 6. a 2-in-7 file read with W = 1
    s = two_in_seven()["05"]
    tries.append(("a 2-in-7 file read with W = 1",
                  (DATA / "two-in-seven" / "final_05.txt").read_text().split("\n"), s, 1))
    for name, ls, sched, w_arrays in tries:
        ok, why = check_file(md, ls, sched, w_arrays)
        print("control:", name, "->", "accepted (WRONG)" if ok else "rejected (" + why + ")")
        rejected += not ok
    # 7. the rule must not exclude the plain program: plane rows at the n0 certificates' bottom sets
    plain = Counter([1, 2, 4, 8] * 3)
    viol = 0
    for l in certs:
        a = mask(int(l.split()[3]))
        viol += sum(md.cost(w, a, a) * n for w, n in plain.items()) < 3 * md.cost("K", a, a)
    print("control: plane rows of the plain 12-call program at the %d bottom sets: %d violations" % (len(certs), viol))
    if rejected != len(tries) or viol:
        fail("a control was not rejected")
    print("PASS_COMPLEX_M4_TIME_UNROLLED_CUTS_CONTROLS")


if __name__ == "__main__":
    part = sys.argv[sys.argv.index("--part") + 1] if "--part" in sys.argv else "main"
    {"main": part_main, "recount": part_recount, "controls": part_controls}[part]()
