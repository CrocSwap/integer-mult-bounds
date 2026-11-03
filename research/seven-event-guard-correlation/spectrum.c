/*
 * Signed spectrum of the binary full-guard character sum, for K <= 7 vertices.
 *
 * Over F_2 let c range over zero-diagonal K x K matrices (K*(K-1) free bits),
 * let |c| be its number of ones, and define
 *
 *   Z(c) = sum over A subset of [K] such that every j not in A satisfies
 *          sum_{i in A} c_ij = 0 (mod 2), of 2^(K-|A|).
 *
 * This subset form equals the three-state sum
 *   sum_{sigma in {0,1,2}^K} (-1)^{sum_ij c_ij [sigma_i=1][sigma_j=2]}
 * (sum out the label-2 coordinates).  The program prints, for every z with
 * H[z] != 0, the line "z H[z]" where H[z] = sum_{c : Z(c)=z} (-1)^{|c|}.
 *
 * Modes (argv[2]):
 *   ext      orbit representatives of the K-2 base vertices under their
 *            symmetric group, all arcs of vertex K-2 to and from the base, and a
 *            table sweep over every arc pattern of the last vertex.  Z of the
 *            last vertex's 2^(2(K-1)) patterns is F1[u] + F2[v]: see sweep().
 *   labelled the same sweep with every labelled base matrix, weight one
 *            (no symmetry reduction; a control for the orbit weights).
 *   brute    every labelled K x K matrix, K <= 6 (a control that shares neither
 *            the orbit reduction nor the table sweep).
 *
 * usage: spectrum K [ext|labelled|brute] [shard nshards]
 * Shards split the base representatives (or the matrices) round-robin; the
 * caller adds the printed counts of all shards.  Diagnostics go to stderr.
 */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef int64_t i64;

enum {
    MAXK = 7,         /* vertices */
    MAXBASE = MAXK - 2,
    MAXPERM = 120,    /* 5! */
    MAXSUB = 64,      /* subsets of the K-1 earlier vertices */
    MAXZ = 2188       /* 3^7 + 1 */
};

typedef struct {
    int K;
    int zmax; /* 3^K, the largest possible Z */
    i64 hist[MAXZ];
    i64 characters; /* number of labelled characters accounted for */
} Spectrum;

typedef struct {
    int b;                         /* base vertices, K - 2 */
    int nbits;                     /* arcs among base vertices, b(b-1) */
    int pos[MAXBASE][MAXBASE];     /* bit index of arc (i,j), i != j */
    int nperm;
    int perm[MAXPERM][MAXBASE];
    uint32_t chunk[MAXPERM][3][256]; /* image of each 8-bit chunk of an arc mask */
} Base;

static int popc(uint32_t x) { return __builtin_popcount(x); }

static i64 pow3(int k) {
    i64 r = 1;
    for (int i = 0; i < k; i++) r *= 3;
    return r;
}

static void spectrum_add(Spectrum *s, int z, i64 amount) {
    assert(z >= 1 && z <= s->zmax);
    s->hist[z] += amount;
}

/* ------------------------------------------------------------ brute mode */

static void run_brute(Spectrum *s, int shard, int nshards) {
    int K = s->K, nbits = K * (K - 1), pos[MAXK][MAXK], t = 0;
    for (int i = 0; i < K; i++)
        for (int j = 0; j < K; j++)
            if (i != j) pos[i][j] = t++;
    assert(t == nbits && K <= 6);
    uint32_t nsub = 1u << K;
    uint64_t total = 1ull << nbits;
    for (uint64_t m = (uint64_t)shard; m < total; m += (uint64_t)nshards) {
        uint32_t rows[MAXK], r[1u << 6];
        for (int i = 0; i < K; i++) {
            rows[i] = 0;
            for (int j = 0; j < K; j++)
                if (i != j && ((m >> pos[i][j]) & 1u)) rows[i] |= 1u << j;
        }
        int z = 1 << K; /* A = empty set */
        r[0] = 0;
        for (uint32_t a = 1; a < nsub; a++) {
            r[a] = r[a & (a - 1)] ^ rows[__builtin_ctz(a)];
            if ((r[a] & ~a & (nsub - 1)) == 0) z += 1 << (K - popc(a));
        }
        int sign = (popc((uint32_t)(m & 0xffffffffu)) + popc((uint32_t)(m >> 32))) & 1 ? -1 : 1;
        spectrum_add(s, z, sign);
        s->characters++;
    }
}

/* ------------------------------------------------------------ ext modes */

/* Next permutation in lexicographic order; returns 0 after the last one. */
static int next_permutation(int *a, int n) {
    int i = n - 2;
    while (i >= 0 && a[i] > a[i + 1]) i--;
    if (i < 0) return 0;
    int j = n - 1;
    while (a[j] < a[i]) j--;
    int tmp = a[i]; a[i] = a[j]; a[j] = tmp;
    for (int lo = i + 1, hi = n - 1; lo < hi; lo++, hi--) {
        tmp = a[lo]; a[lo] = a[hi]; a[hi] = tmp;
    }
    return 1;
}

static void base_init(Base *B, int K) {
    int b = K - 2, t = 0;
    assert(b >= 1 && b <= MAXBASE);
    memset(B, 0, sizeof *B);
    B->b = b;
    for (int i = 0; i < b; i++)
        for (int j = 0; j < b; j++)
            if (i != j) B->pos[i][j] = t++;
    B->nbits = t;
    assert(t <= 24); /* three 8-bit chunks */
    int a[MAXBASE];
    for (int i = 0; i < b; i++) a[i] = i;
    do {
        assert(B->nperm < MAXPERM);
        memcpy(B->perm[B->nperm++], a, sizeof(int) * (size_t)b);
    } while (next_permutation(a, b));
    for (int p = 0; p < B->nperm; p++) {
        int image[24];
        for (int i = 0; i < b; i++)
            for (int j = 0; j < b; j++)
                if (i != j) image[B->pos[i][j]] = B->pos[B->perm[p][i]][B->perm[p][j]];
        for (int c = 0; c < 3; c++)
            for (int v = 0; v < 256; v++) {
                uint32_t out = 0;
                for (int q = 0; q < 8; q++)
                    if (c * 8 + q < B->nbits && ((v >> q) & 1)) out |= 1u << image[c * 8 + q];
                B->chunk[p][c][v] = out;
            }
    }
}

/* Orbit size of x if x is the least element of its orbit, else 0. */
static int base_orbit_size(const Base *B, uint32_t x) {
    int fixed = 0;
    for (int p = 0; p < B->nperm; p++) {
        uint32_t y = B->chunk[p][0][x & 255] | B->chunk[p][1][(x >> 8) & 255] | B->chunk[p][2][(x >> 16) & 255];
        if (y < x) return 0;
        if (y == x) fixed++;
    }
    assert(fixed >= 1 && B->nperm % fixed == 0);
    return B->nperm / fixed;
}

/*
 * Add every arc pattern of the last vertex to the digraph on the K-1 earlier
 * vertices whose adjacency rows are rows[0..K-2] (bit j of rows[i] is c_ij).
 * Let u be the set of earlier vertices with an arc into the last vertex and v
 * the set it points to.  For A' a subset of the earlier vertices let
 * r[A'] be the xor of its rows.  Subsets A not containing the last vertex
 * need r[A'] to vanish outside A' and an even overlap |u & A'|; subsets
 * A' + {last} need r[A'] xor v to vanish outside A'.  Hence
 * Z = F1[u] + F2[v] with
 *   F1[u] = sum over A' with r[A'] & ~A' = 0 and parity(u & A') = 0 of 2^(K-|A'|),
 *   F2[v] = sum over A' with (r[A'] ^ v) & ~A' = 0 of 2^(K-|A'|-1).
 * F1 comes from a Walsh-Hadamard transform and F2 from enumerating the v
 * that agree with r[A'] outside A'.  The sign of the last vertex's 2(K-1)
 * arcs is (-1)^(|u|+|v|); `signed_weight` carries the sign and orbit weight
 * of the rest.
 */
static void sweep(Spectrum *s, const uint32_t rows[], i64 signed_weight) {
    int K = s->K, B1 = K - 1;
    uint32_t nsub = 1u << B1, full = nsub - 1;
    uint32_t r[MAXSUB];
    int g[MAXSUB], f2[MAXSUB], wsum = 0;
    r[0] = 0;
    for (uint32_t a = 0; a < nsub; a++) {
        if (a) r[a] = r[a & (a - 1)] ^ rows[__builtin_ctz(a)];
        g[a] = ((r[a] & ~a & full) == 0) ? (1 << (K - popc(a))) : 0;
        wsum += g[a];
        f2[a] = 0;
    }
    for (uint32_t len = 1; len < nsub; len <<= 1) /* Walsh-Hadamard transform of g */
        for (uint32_t i = 0; i < nsub; i += 2 * len)
            for (uint32_t j = i; j < i + len; j++) {
                int x = g[j], y = g[j + len];
                g[j] = x + y;
                g[j + len] = x - y;
            }
    for (uint32_t a = 0; a < nsub; a++) {
        uint32_t target = r[a] & ~a & full, sub = a;
        int weight = 1 << (K - popc(a) - 1);
        for (;;) {
            f2[target | sub] += weight;
            if (sub == 0) break;
            sub = (sub - 1) & a;
        }
    }
    for (uint32_t u = 0; u < nsub; u++) {
        assert(((wsum + g[u]) & 1) == 0);
        int f1 = (wsum + g[u]) / 2;
        i64 su = (popc(u) & 1) ? -signed_weight : signed_weight;
        for (uint32_t v = 0; v < nsub; v++) spectrum_add(s, f1 + f2[v], (popc(v) & 1) ? -su : su);
    }
    s->characters += (i64)nsub * (i64)nsub * (signed_weight < 0 ? -signed_weight : signed_weight);
}

/* Extend one base matrix x (weight w) by the arcs of vertex b and sweep. */
static void expand_base(Spectrum *s, const Base *B, uint32_t x, int w) {
    int b = B->b;
    uint32_t rows[MAXBASE + 1];
    for (int i = 0; i < b; i++) {
        rows[i] = 0;
        for (int j = 0; j < b; j++)
            if (i != j && ((x >> B->pos[i][j]) & 1u)) rows[i] |= 1u << j;
    }
    for (uint32_t ext = 0; ext < (1u << (2 * b)); ext++) {
        uint32_t into = ext & ((1u << b) - 1), out_of = ext >> b, full[MAXBASE + 1];
        for (int i = 0; i < b; i++) full[i] = rows[i] | (((into >> i) & 1u) << b);
        full[b] = out_of;
        i64 sw = ((popc(x) + popc(ext)) & 1) ? -(i64)w : (i64)w;
        sweep(s, full, sw);
    }
}

static void run_ext(Spectrum *s, int labelled, int shard, int nshards) {
    static Base B;
    base_init(&B, s->K);
    uint64_t total = 1ull << B.nbits, index = 0;
    i64 reps = 0, orbit_total = 0;
    for (uint64_t x = 0; x < total; x++) {
        int w = labelled ? 1 : base_orbit_size(&B, (uint32_t)x);
        if (w == 0) continue;
        reps++;
        orbit_total += w;
        if ((int)(index++ % (uint64_t)nshards) == shard) expand_base(s, &B, (uint32_t)x, w);
    }
    assert(orbit_total == (i64)total);
    fprintf(stderr, "base_matrices=%lld orbit_total=%lld\n", (long long)reps, (long long)orbit_total);
}

int main(int argc, char **argv) {
    if (argc < 2 || (argc != 2 && argc != 3 && argc != 5)) {
        fprintf(stderr, "usage: spectrum K [ext|labelled|brute] [shard nshards]\n");
        return 2;
    }
    static Spectrum S;
    S.K = atoi(argv[1]);
    S.zmax = S.K >= 3 && S.K <= MAXK ? (int)pow3(S.K) : 0;
    const char *mode = argc >= 3 ? argv[2] : "ext";
    int shard = argc == 5 ? atoi(argv[3]) : 0, nshards = argc == 5 ? atoi(argv[4]) : 1;
    if (S.K < 3 || S.K > MAXK || shard < 0 || nshards < 1 || shard >= nshards) {
        fprintf(stderr, "bad arguments\n");
        return 2;
    }
    if (strcmp(mode, "brute") == 0 && S.K <= 6) run_brute(&S, shard, nshards);
    else if (strcmp(mode, "ext") == 0) run_ext(&S, 0, shard, nshards);
    else if (strcmp(mode, "labelled") == 0) run_ext(&S, 1, shard, nshards);
    else {
        fprintf(stderr, "unknown mode or K too large for brute\n");
        return 2;
    }
    for (int z = 0; z < MAXZ; z++)
        if (S.hist[z] != 0 && printf("%d %lld\n", z, (long long)S.hist[z]) < 0) return 1;
    fprintf(stderr, "characters=%lld\n", (long long)S.characters);
    return fflush(stdout) == 0 ? 0 : 1;
}
