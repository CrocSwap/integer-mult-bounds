/* Two thin maps on the g=3, d=2 paired-star full-call contract.
 *
 * The solver core is research/paired-star-two-thin-f4/search.c from
 * 8889385a5bbe64df6f1378047b35d89e1aea355c (PR #7006). The witness and
 * shape modes added below name one nullity-32 class, check its block
 * form, and compare one capped class of a different shape.
 * Prepared by unpaidmoon with substantial Cursor Grok assistance.
 * Apache-2.0.
 *
 * Full calls stay the twelve F_2 orthogonal resolutions. Thin entries may lie
 * in any characteristic-2 field. The endpoint equations are F_2-linear, so the
 * solution space over an extension is the scalar extension of an F_2-affine
 * space. This program decides that space over the concrete field
 * F_4 = F_2[a]/(a^2+a+1).
 *
 * Chronological order: the first call is the rightmost factor. List order
 * left-multiplies the earliest factor first.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <omp.h>

enum { N = 8, G = 3, NPERM = 720, NMONO = 27 };

static uint8_t MUL[256][256];
static uint8_t MONO_MUL[NMONO][NMONO];
static int overflow_count = 0;
static int shape_only = 0;
static int shape_n32 = 0;
static int shape_eight4 = 0;
static int shape_named_mask = 0;
static int shape_named_private = 0;
static uint64_t shape_free[40];
static uint64_t shape_z[40];
static uint64_t shape_h[40];
static int shape_mask_n[40];
static int shape_mask_count = 0;

static int mono_index(int e0, int e1, int e2) { return e0 + 3 * e1 + 9 * e2; }

static void init_tables(void) {
    for (int a = 0; a < 256; a++) {
        for (int b = 0; b < 256; b++) {
            unsigned prod = 0, x = (unsigned)a, y = (unsigned)b;
            while (y) {
                if (y & 1u) prod ^= x;
                x <<= 1;
                if (x & 0x100u) x ^= 0x11bu;
                y >>= 1u;
            }
            MUL[a][b] = (uint8_t)prod;
        }
    }
    for (int i = 0; i < NMONO; i++) {
        int e0 = i % 3, e1 = (i / 3) % 3, e2 = i / 9;
        for (int j = 0; j < NMONO; j++) {
            int f0 = j % 3, f1 = (j / 3) % 3, f2 = j / 9;
            int g0 = e0 + f0, g1 = e1 + f1, g2 = e2 + f2;
            MONO_MUL[i][j] = (g0 > 2 || g1 > 2 || g2 > 2) ? 255 : (uint8_t)mono_index(g0, g1, g2);
        }
    }
}

typedef uint32_t Poly;
typedef Poly Mat[N][N];

static void die(const char *msg) {
    fprintf(stderr, "FAIL: %s\n", msg);
    exit(1);
}

static Poly pmul(Poly a, Poly b) {
    Poly out = 0;
    while (a) {
        unsigned ba = a & -a;
        int i = __builtin_ctz(ba);
        a ^= ba;
        Poly bb = b;
        while (bb) {
            unsigned bb1 = bb & -bb;
            int j = __builtin_ctz(bb1);
            bb ^= bb1;
            uint8_t m = MONO_MUL[i][j];
            if (m == 255) {
                overflow_count++;
                continue;
            }
            out ^= (Poly)1u << m;
        }
    }
    return out;
}

static void mzero(Mat a) { memset(a, 0, sizeof(Mat)); }
static void meye(Mat a) {
    mzero(a);
    for (int i = 0; i < N; i++) a[i][i] = 1;
}
static int msame(const Mat a, const Mat b) { return memcmp(a, b, sizeof(Mat)) == 0; }
static void madd(Mat out, const Mat a, const Mat b) {
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) out[i][j] = a[i][j] ^ b[i][j];
}
static void mmul(Mat out, const Mat a, const Mat b) {
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) {
            Poly s = 0;
            for (int k = 0; k < N; k++)
                if (a[i][k] && b[k][j]) s ^= pmul(a[i][k], b[k][j]);
            out[i][j] = s;
        }
}

static int mul2(int left, int right) {
    int out = 0;
    for (int i = 0; i < 2; i++)
        for (int j = 0; j < 2; j++) {
            int bit = (((left >> (2 * i)) & 1) & ((right >> j) & 1)) ^
                      (((left >> (2 * i + 1)) & 1) & ((right >> (2 + j)) & 1));
            out |= bit << (2 * i + j);
        }
    return out;
}
static int rank2(int bits) {
    int rows[2] = {bits & 3, (bits >> 2) & 3};
    int rank = 0;
    for (int col = 0; col < 2; col++) {
        int mask = 1 << col, pivot = -1;
        for (int i = rank; i < 2; i++)
            if (rows[i] & mask) {
                pivot = i;
                break;
            }
        if (pivot < 0) continue;
        int tmp = rows[rank];
        rows[rank] = rows[pivot];
        rows[pivot] = tmp;
        if (rows[rank ^ 1] & mask) rows[rank ^ 1] ^= rows[rank];
        rank++;
    }
    return rank;
}
static void block_rows(int a, int b, int rows[4]) {
    int mixed = a ^ b;
    int blocks[2][2] = {{mixed, b}, {b, mixed}};
    int n = 0;
    for (int half = 0; half < 2; half++)
        for (int r = 0; r < 2; r++) {
            int mask = 0;
            for (int bc = 0; bc < 2; bc++) {
                int block = blocks[half][bc];
                for (int c = 0; c < 2; c++)
                    if ((block >> (2 * r + c)) & 1) mask |= 1 << (2 * bc + c);
            }
            rows[n++] = mask;
        }
}
static int rows_eq(const int x[4], const int y[4]) {
    return x[0] == y[0] && x[1] == y[1] && x[2] == y[2] && x[3] == y[3];
}
static void mul4(const int left[4], const int right[4], int out[4]) {
    for (int r = 0; r < 4; r++) {
        int value = 0, rest = left[r];
        while (rest) {
            int bit = rest & -rest;
            value ^= right[__builtin_ctz(bit)];
            rest ^= bit;
        }
        out[r] = value;
    }
}
static void embed_proj(uint8_t rows[N], int cc, int cl, int lc, int ll, int leaf) {
    memset(rows, 0, N);
    for (int r = 0; r < 2; r++)
        for (int c = 0; c < 2; c++) {
            if ((cc >> (2 * r + c)) & 1) rows[r] |= (uint8_t)(1u << c);
            if ((cl >> (2 * r + c)) & 1) rows[r] |= (uint8_t)(1u << (2 * leaf + c));
            if ((lc >> (2 * r + c)) & 1) rows[2 * leaf + r] |= (uint8_t)(1u << c);
            if ((ll >> (2 * r + c)) & 1) rows[2 * leaf + r] |= (uint8_t)(1u << (2 * leaf + c));
        }
}

typedef struct {
    int a, b, complement;
} ResBits;
typedef struct {
    uint8_t proj[N];
    uint8_t readm[N];
} Call;

static int build_resolutions(ResBits bits[12]) {
    int n = 0;
    uint64_t seen_lo[12], seen_hi[12];
    for (int bits_a = 0; bits_a < 16; bits_a++) {
        if (mul2(bits_a, bits_a) != bits_a || rank2(bits_a) != 1) continue;
        int complement = bits_a ^ 0x9;
        for (int bits_b = 0; bits_b < 16; bits_b++) {
            int first[4], second[4], zero[4] = {0}, fp[4], sp[4], fs[4], sf[4];
            block_rows(bits_a, bits_b, first);
            block_rows(complement, bits_b, second);
            mul4(first, first, fp);
            mul4(second, second, sp);
            mul4(first, second, fs);
            mul4(second, first, sf);
            if (!rows_eq(fp, first) || !rows_eq(sp, second) || !rows_eq(fs, zero) || !rows_eq(sf, zero)) continue;
            uint64_t k1 = 0, k2 = 0;
            for (int i = 0; i < 4; i++) {
                k1 |= (uint64_t)first[i] << (4 * i);
                k2 |= (uint64_t)second[i] << (4 * i);
            }
            uint64_t lo = k1 < k2 ? k1 : k2, hi = k1 < k2 ? k2 : k1;
            int already = 0;
            for (int s = 0; s < n; s++)
                if (seen_lo[s] == lo && seen_hi[s] == hi) already = 1;
            if (already) continue;
            if (n == 12) return -1;
            bits[n].a = bits_a;
            bits[n].b = bits_b;
            bits[n].complement = complement;
            seen_lo[n] = lo;
            seen_hi[n] = hi;
            n++;
        }
    }
    return n;
}

static void make_call(Call *call, const ResBits *res, int stage, int half) {
    int leaf = stage + 1;
    int matrix_a = half ? res->complement : res->a;
    int mixed = matrix_a ^ res->b;
    embed_proj(call->proj, mixed, res->b, res->b, mixed, leaf);
    embed_proj(call->readm, matrix_a, matrix_a, matrix_a, matrix_a, leaf);
}

static void pure_from_proj(Mat out, const uint8_t proj[N], int stage) {
    meye(out);
    int shift = stage == 0 ? 1 : stage == 1 ? 3 : 9;
    for (int i = 0; i < N; i++) {
        uint8_t row = proj[i];
        while (row) {
            unsigned bit = row & (unsigned)-((int)row);
            int col = __builtin_ctz(bit);
            out[i][col] ^= 1u;
            out[i][col] ^= (Poly)1u << shift;
            row = (uint8_t)(row ^ bit);
        }
    }
}
static void support_e(uint8_t proj[N], int stage) {
    memset(proj, 0, N);
    proj[0] = 1;
    proj[1] = 2;
    int leaf = stage + 1;
    proj[2 * leaf] = (uint8_t)(1u << (2 * leaf));
    proj[2 * leaf + 1] = (uint8_t)(1u << (2 * leaf + 1));
}
static void scale_read(Mat out, const uint8_t readm[N], int stage) {
    mzero(out);
    int shift = stage == 0 ? 1 : stage == 1 ? 3 : 9;
    for (int i = 0; i < N; i++) {
        uint8_t row = readm[i];
        while (row) {
            unsigned bit = row & (unsigned)-((int)row);
            int col = __builtin_ctz(bit);
            out[i][col] = (Poly)1u << shift;
            row = (uint8_t)(row ^ bit);
        }
    }
}
static void build_target(Mat target) {
    meye(target);
    for (int stage = 0; stage < G; stage++) {
        uint8_t eproj[N];
        Mat gate, prod;
        support_e(eproj, stage);
        pure_from_proj(gate, eproj, stage);
        mmul(prod, gate, target);
        memcpy(target, prod, sizeof prod);
    }
}

static uint8_t poly_at(Poly p, const uint8_t d[3]) {
    uint8_t out = 0;
    while (p) {
        unsigned bit = p & -p;
        int idx = __builtin_ctz(bit);
        p ^= bit;
        int e0 = idx % 3, e1 = (idx / 3) % 3, e2 = idx / 9;
        uint8_t term = 1;
        for (int i = 0; i < e0; i++) term = MUL[term][d[0]];
        for (int i = 0; i < e1; i++) term = MUL[term][d[1]];
        for (int i = 0; i < e2; i++) term = MUL[term][d[2]];
        out ^= term;
    }
    return out;
}

static int rank_f2(const uint8_t rows[N]) {
    uint8_t a[N];
    memcpy(a, rows, N);
    int rank = 0;
    for (int col = 0; col < N; col++) {
        uint8_t mask = (uint8_t)(1u << col);
        int pivot = -1;
        for (int i = rank; i < N; i++)
            if (a[i] & mask) {
                pivot = i;
                break;
            }
        if (pivot < 0) continue;
        uint8_t tmp = a[rank];
        a[rank] = a[pivot];
        a[pivot] = tmp;
        for (int i = 0; i < N; i++)
            if (i != rank && (a[i] & mask)) a[i] ^= a[rank];
        rank++;
    }
    return rank;
}

static void heap_perms(uint8_t perms[NPERM][6]) {
    int a[6] = {0, 1, 2, 3, 4, 5}, c[6] = {0}, n = 0;
    for (int k = 0; k < 6; k++) perms[n][k] = (uint8_t)a[k];
    n++;
    int i = 0;
    while (i < 6) {
        if (c[i] < i) {
            int j = (i & 1) ? c[i] : 0, tmp = a[j];
            a[j] = a[i];
            a[i] = tmp;
            for (int k = 0; k < 6; k++) perms[n][k] = (uint8_t)a[k];
            n++;
            c[i]++;
            i = 0;
        } else
            c[i++] = 0;
    }
    if (n != NPERM) die("perm count");
}

typedef uint64_t Eq[NMONO][N * N];
static void eq_clear(Eq eq) { memset(eq, 0, sizeof(Eq)); }
static void eq_add_map(Eq eq, const Mat left, const Mat right) {
    for (int a = 0; a < N; a++)
        for (int b = 0; b < N; b++) {
            int u = a * N + b;
            for (int i = 0; i < N; i++) {
                Poly Li = left[i][a];
                if (!Li) continue;
                for (int j = 0; j < N; j++) {
                    if (!right[b][j]) continue;
                    Poly p = pmul(Li, right[b][j]);
                    int e = i * N + j;
                    while (p) {
                        unsigned bit = p & -p;
                        eq[__builtin_ctz(bit)][e] ^= (uint64_t)1 << u;
                        p ^= bit;
                    }
                }
            }
        }
}

typedef struct {
    uint64_t lo[128], hi[128];
    uint8_t rhs[128], pvar[128];
    int16_t pivot_of[128];
    int np, bad;
} Basis;

static int basis_bit(uint64_t lo, uint64_t hi, int v) {
    return v < 64 ? (int)((lo >> v) & 1ull) : (int)((hi >> (v - 64)) & 1ull);
}
static void basis_clear(Basis *b) {
    memset(b, 0, sizeof *b);
    for (int i = 0; i < 128; i++) b->pivot_of[i] = -1;
}
/* Reduced row echelon form. Clearing only the lowest set bit is not enough:
 * that bit can be free while a higher bit is already a pivot. */
static void basis_insert(Basis *b, uint64_t lo, uint64_t hi, int rhs) {
    if (b->bad) return;
    for (int q = 0; q < b->np; q++) {
        int v = b->pvar[q];
        if (!basis_bit(lo, hi, v)) continue;
        lo ^= b->lo[q];
        hi ^= b->hi[q];
        rhs ^= b->rhs[q];
    }
    if (!lo && !hi) {
        if (rhs) b->bad = 1;
        return;
    }
    int v = lo ? __builtin_ctzll(lo) : 64 + __builtin_ctzll(hi);
    for (int q = 0; q < b->np; q++) {
        if (!basis_bit(b->lo[q], b->hi[q], v)) continue;
        b->lo[q] ^= lo;
        b->hi[q] ^= hi;
        b->rhs[q] ^= (uint8_t)rhs;
    }
    b->lo[b->np] = lo;
    b->hi[b->np] = hi;
    b->rhs[b->np] = (uint8_t)rhs;
    b->pvar[b->np] = (uint8_t)v;
    b->pivot_of[v] = (int16_t)b->np;
    b->np++;
}
static int solve_pair(Basis *b, const Eq eq_g, const Eq eq_h, const Mat defect) {
    basis_clear(b);
    for (int m = 0; m < NMONO; m++)
        for (int e = 0; e < N * N; e++) {
            uint64_t lo = eq_g[m][e], hi = eq_h[m][e];
            int rhs = (int)((defect[e >> 3][e & 7] >> m) & 1u);
            if (!lo && !hi && !rhs) continue;
            basis_insert(b, lo, hi, rhs);
            if (b->bad) return -1;
        }
    return 128 - b->np;
}
static int mats_satisfy(const Eq eq_g, const Eq eq_h, const Mat defect, const uint8_t zg[N], const uint8_t zh[N]) {
    for (int m = 0; m < NMONO; m++)
        for (int e = 0; e < N * N; e++) {
            int acc = (int)((defect[e >> 3][e & 7] >> m) & 1u);
            uint64_t lo = eq_g[m][e], hi = eq_h[m][e];
            while (lo) {
                uint64_t bit = lo & -lo;
                int u = __builtin_ctzll(bit);
                if (zg[u >> 3] & (1u << (u & 7))) acc ^= 1;
                lo ^= bit;
            }
            while (hi) {
                uint64_t bit = hi & -hi;
                int u = __builtin_ctzll(bit);
                if (zh[u >> 3] & (1u << (u & 7))) acc ^= 1;
                hi ^= bit;
            }
            if (acc) return 0;
        }
    return 1;
}
static void unpack_solution(uint8_t zg[N], uint8_t zh[N], const Basis *b) {
    memset(zg, 0, N);
    memset(zh, 0, N);
    for (int p = 0; p < b->np; p++) {
        if (!b->rhs[p]) continue;
        int v = b->pvar[p];
        if (v < 64)
            zg[v >> 3] |= (uint8_t)(1u << (v & 7));
        else
            zh[(v - 64) >> 3] |= (uint8_t)(1u << ((v - 64) & 7));
    }
}

static const uint8_t F4_MUL[4][4] = {{0, 0, 0, 0}, {0, 1, 2, 3}, {0, 2, 3, 1}, {0, 3, 1, 2}};
static const uint8_t F4_INV[4] = {0, 1, 3, 2};

typedef struct {
    uint8_t vec[8][8];
    uint8_t piv[8];
    int dim;
} RowBasis;
static void rb_clear(RowBasis *b) { memset(b, 0, sizeof *b); }
static void rb_insert(RowBasis *b, const uint8_t row_in[8]) {
    uint8_t row[8];
    memcpy(row, row_in, 8);
    for (int i = 0; i < b->dim; i++) {
        uint8_t factor = row[b->piv[i]];
        if (!factor) continue;
        for (int j = 0; j < 8; j++) row[j] ^= F4_MUL[factor][b->vec[i][j]];
    }
    int pivot = -1;
    for (int j = 0; j < 8; j++)
        if (row[j]) {
            pivot = j;
            break;
        }
    if (pivot < 0) return;
    uint8_t inv = F4_INV[row[pivot]];
    for (int j = 0; j < 8; j++) row[j] = F4_MUL[inv][row[j]];
    for (int i = 0; i < b->dim; i++) {
        uint8_t factor = b->vec[i][pivot];
        if (!factor) continue;
        for (int j = 0; j < 8; j++) b->vec[i][j] ^= F4_MUL[factor][row[j]];
    }
    memcpy(b->vec[b->dim], row, 8);
    b->piv[b->dim] = (uint8_t)pivot;
    b->dim++;
}

typedef struct {
    int var[8];
    int nvar;
    int rows[16];
    int nrows;
} AffComp;

static void materialize_row(uint8_t row[8], int row_id, const uint8_t c[32], const uint32_t dep[128],
                            const uint8_t part[128]) {
    int base = row_id < 8 ? 0 : 64;
    int rr = row_id < 8 ? row_id : row_id - 8;
    for (int col = 0; col < 8; col++) {
        int e = base + rr * 8 + col;
        uint8_t val = part[e];
        uint32_t bits = dep[e];
        while (bits) {
            val ^= c[__builtin_ctz(bits)];
            bits &= bits - 1;
        }
        row[col] = val;
    }
}

static void pack_basis(uint64_t out[2], const RowBasis *b) {
    int order[8];
    for (int i = 0; i < b->dim; i++) order[i] = i;
    for (int i = 1; i < b->dim; i++) {
        int key = order[i], j = i;
        while (j > 0 && b->piv[order[j - 1]] > b->piv[key]) {
            order[j] = order[j - 1];
            j--;
        }
        order[j] = key;
    }
    out[0] = out[1] = 0;
    for (int i = 0; i < b->dim; i++) {
        uint16_t bits = 0;
        for (int col = 0; col < 8; col++) bits |= (uint16_t)(b->vec[order[i]][col] & 3u) << (2 * col);
        int at = i * 16;
        if (at < 64)
            out[0] |= (uint64_t)bits << at;
        else
            out[1] |= (uint64_t)bits << (at - 64);
    }
}

static void unpack_basis(RowBasis *b, const uint64_t in[2]) {
    rb_clear(b);
    for (int i = 0; i < 8; i++) {
        int at = i * 16;
        uint16_t bits = (uint16_t)((at < 64 ? in[0] >> at : in[1] >> (at - 64)) & 0xffffu);
        if (!bits) break;
        int piv = -1;
        for (int col = 0; col < 8; col++) {
            b->vec[i][col] = (uint8_t)((bits >> (2 * col)) & 3u);
            if (piv < 0 && b->vec[i][col]) piv = col;
        }
        if (piv < 0) break;
        b->piv[i] = (uint8_t)piv;
        b->dim++;
    }
}

typedef struct {
    uint64_t w[4];
} Pack;

static uint32_t pack_hash(const Pack *p) {
    uint64_t x = p->w[0] ^ (p->w[1] * 0x9e3779b97f4a7c15ull) ^ (p->w[2] * 0xbf58476d1ce4e5b9ull) ^
                 (p->w[3] * 0x94d049bb133111ebull);
    x ^= x >> 30;
    x *= 0xbf58476d1ce4e5b9ull;
    x ^= x >> 27;
    return (uint32_t)x;
}

/* Frontier of partial row spaces whose rank sum is still below 8.
 * Assigning one component is a function of that component alone, so identical
 * spaces are merged before the next component. A frontier of 2^20 is the
 * certificate budget: exceeding it returns -3 and does not claim a minimum. */
static int rank_dp(const AffComp *comp, int ncomp, RowBasis g0, RowBasis h0, const uint32_t dep[128],
                   const uint8_t part[128], uint64_t *nodes, uint64_t cap) {
    enum { MAX_FRONT = 1 << 20, HASH_CAP = 1 << 22, MAX_BUNDLE = 16384 };
    Pack *cur = calloc(MAX_FRONT, sizeof(Pack));
    Pack *nxt = calloc(MAX_FRONT, sizeof(Pack));
    uint32_t *slot = malloc(HASH_CAP * sizeof(uint32_t));
    uint8_t *bundle = malloc((size_t)MAX_BUNDLE * 16 * 8);
    if (!cur || !nxt || !slot || !bundle) die("dp alloc");
    pack_basis(&cur[0].w[0], &g0);
    pack_basis(&cur[0].w[2], &h0);
    int ncur = 1;
    int result = 8;
    for (int ci = 0; ci < ncomp; ci++) {
        const AffComp *co = &comp[ci];
        int limit = 1;
        for (int i = 0; i < co->nvar; i++) limit *= 4;
        if (limit > MAX_BUNDLE) {
            result = -1;
            goto done;
        }
        int nb = 0;
        uint8_t c[32] = {0};
        memset(slot, 0xff, HASH_CAP * sizeof(uint32_t));
        for (int code = 0; code < limit; code++) {
            int x = code;
            for (int i = 0; i < co->nvar; i++) {
                c[co->var[i]] = (uint8_t)(x & 3);
                x >>= 2;
            }
            uint8_t *dst = bundle + (size_t)nb * 16 * 8;
            for (int r = 0; r < co->nrows; r++) materialize_row(dst + r * 8, co->rows[r], c, dep, part);
            uint64_t hx = 1469598103934665603ull;
            for (int i = 0; i < co->nrows * 8; i++) {
                hx ^= dst[i];
                hx *= 1099511628211ull;
            }
            uint32_t mask = HASH_CAP - 1;
            uint32_t hsh = (uint32_t)hx & mask;
            int dup = 0;
            for (;;) {
                uint32_t curi = slot[hsh];
                if (curi == 0xffffffffu) {
                    slot[hsh] = (uint32_t)nb++;
                    break;
                }
                if (memcmp(bundle + (size_t)curi * 16 * 8, dst, (size_t)co->nrows * 8) == 0) {
                    dup = 1;
                    break;
                }
                hsh = (hsh + 1) & mask;
            }
            if (dup) continue;
        }
        memset(slot, 0xff, HASH_CAP * sizeof(uint32_t));
        int nnxt = 0;
        for (int s = 0; s < ncur; s++) {
            RowBasis g, h;
            unpack_basis(&g, &cur[s].w[0]);
            unpack_basis(&h, &cur[s].w[2]);
            for (int b = 0; b < nb; b++) {
                if (*nodes >= cap) {
                    result = -3;
                    goto done;
                }
                (*nodes)++;
                RowBasis ng = g, nh = h;
                const uint8_t *rows = bundle + (size_t)b * 16 * 8;
                int dead = 0;
                for (int r = 0; r < co->nrows; r++) {
                    if (co->rows[r] < 8)
                        rb_insert(&ng, rows + r * 8);
                    else
                        rb_insert(&nh, rows + r * 8);
                    if (ng.dim + nh.dim >= 8) {
                        dead = 1;
                        break;
                    }
                }
                if (dead) continue;
                Pack key;
                pack_basis(&key.w[0], &ng);
                pack_basis(&key.w[2], &nh);
                uint32_t mask = HASH_CAP - 1;
                uint32_t hsh = pack_hash(&key) & mask;
                for (;;) {
                    uint32_t curi = slot[hsh];
                    if (curi == 0xffffffffu) {
                        if (nnxt >= MAX_FRONT) {
                            result = -3;
                            goto done;
                        }
                        nxt[nnxt] = key;
                        slot[hsh] = (uint32_t)nnxt++;
                        break;
                    }
                    if (memcmp(&nxt[curi], &key, sizeof key) == 0) break;
                    hsh = (hsh + 1) & mask;
                }
            }
        }
        if (nnxt == 0) {
            result = 8;
            goto done;
        }
        Pack *swap = cur;
        cur = nxt;
        nxt = swap;
        ncur = nnxt;
    }
    result = 7;
    for (int s = 0; s < ncur; s++) {
        RowBasis g, h;
        unpack_basis(&g, &cur[s].w[0]);
        unpack_basis(&h, &cur[s].w[2]);
        if (g.dim + h.dim < result) result = g.dim + h.dim;
    }
done:
    free(cur);
    free(nxt);
    free(slot);
    free(bundle);
    return result;
}


/* 8 when every F_4 point has rank sum at least 8, the discovered smaller
 * rank when one exists, -3 when the 2^20 frontier is full (not a lower
 * bound), -1 when the component shape is outside the enumerator. */
static int f4_rank_bb(const Basis *b, int nullity, uint64_t cap, uint64_t *nodes_out) {
    if (nullity <= 0 || nullity > 32) return -1;
    int free_var[32], nf = 0;
    uint8_t used[128] = {0};
    for (int p = 0; p < b->np; p++) used[b->pvar[p]] = 1;
    for (int v = 0; v < 128; v++)
        if (!used[v]) {
            if (nf == 32) return -1;
            free_var[nf++] = v;
        }
    if (nf != nullity) return -1;
    uint8_t part_g[N], part_h[N], part[128];
    unpack_solution(part_g, part_h, b);
    uint32_t dep[128];
    memset(dep, 0, sizeof dep);
    for (int e = 0; e < 64; e++) {
        part[e] = (uint8_t)((part_g[e >> 3] >> (e & 7)) & 1);
        part[64 + e] = (uint8_t)((part_h[e >> 3] >> (e & 7)) & 1);
    }
    for (int t = 0; t < nf; t++) {
        int v = free_var[t];
        dep[v] |= 1u << t;
        for (int p = 0; p < b->np; p++)
            if (basis_bit(b->lo[p], b->hi[p], v)) dep[b->pvar[p]] |= 1u << t;
    }
    int parentv[32];
    for (int t = 0; t < nf; t++) parentv[t] = t;
    uint32_t row_mask[16];
    for (int r = 0; r < 16; r++) {
        uint32_t mask = 0;
        int base = r < 8 ? 0 : 64, rr = r < 8 ? r : r - 8;
        for (int col = 0; col < 8; col++) mask |= dep[base + rr * 8 + col];
        row_mask[r] = mask;
        int first = -1;
        while (mask) {
            int t = __builtin_ctz(mask);
            mask &= mask - 1;
            if (first < 0)
                first = t;
            else {
                int a = first, c = t;
                while (parentv[a] != a) a = parentv[a];
                while (parentv[c] != c) c = parentv[c];
                parentv[c] = a;
                first = a;
            }
        }
    }
    int root_id[32], ncomp = 0;
    for (int t = 0; t < 32; t++) root_id[t] = -1;
    AffComp comp[16];
    memset(comp, 0, sizeof comp);
    for (int t = 0; t < nf; t++) {
        int a = t;
        while (parentv[a] != a) a = parentv[a];
        parentv[t] = a;
        if (root_id[a] < 0) {
            if (ncomp == 16) return -1;
            root_id[a] = ncomp++;
        }
        AffComp *co = &comp[root_id[a]];
        if (co->nvar == 8) return -1;
        co->var[co->nvar++] = t;
    }
    RowBasis g, h;
    rb_clear(&g);
    rb_clear(&h);
    uint8_t zero_c[32] = {0};
    for (int r = 0; r < 16; r++) {
        if (row_mask[r]) {
            int root = -1;
            uint32_t mask = row_mask[r];
            while (mask) {
                int t = __builtin_ctz(mask);
                mask &= mask - 1;
                int id = root_id[parentv[t]];
                if (root < 0)
                    root = id;
                else if (root != id)
                    return -1;
            }
            AffComp *co = &comp[root];
            if (co->nrows == 16) return -1;
            co->rows[co->nrows++] = r;
        } else {
            uint8_t row[8];
            materialize_row(row, r, zero_c, dep, part);
            if (r < 8)
                rb_insert(&g, row);
            else
                rb_insert(&h, row);
        }
    }
    if (g.dim + h.dim >= 8 && !shape_only) {
        if (nodes_out) *nodes_out = 0;
        return 8;
    }
    for (int i = 1; i < ncomp; i++) {
        AffComp key = comp[i];
        int j = i - 1;
        while (j >= 0 && comp[j].nvar < key.nvar) {
            comp[j + 1] = comp[j];
            j--;
        }
        comp[j + 1] = key;
    }
    if (shape_only) {
        static const int named_m[8][3] = {{0x33, 0x14, 0x40}, {0x33, 0x28, 0x80}, {0xcc, 0x01, 0x00},
                                           {0xcc, 0x02, 0x00}, {0x33, 0x01, 0x00}, {0x33, 0x02, 0x00},
                                           {0xcc, 0x00, 0x01}, {0xcc, 0x00, 0x02}};
        int eight4 = (nullity == 32 && ncomp == 8 && g.dim == 0 && h.dim == 0);
        for (int i = 0; i < ncomp; i++) {
            if (comp[i].nvar != 4 || comp[i].nrows != 2 || comp[i].rows[1] != comp[i].rows[0] + 8) eight4 = 0;
        }
        int named = (nullity == 32);
        uint64_t pack_f = 0, pack_z = 0, pack_h = 0;
        for (int rr = 0; rr < 8; rr++) {
            int free_m = 0, zc = 0, hc = 0;
            for (int col = 0; col < 8; col++) {
                int e = rr * 8 + col;
                if (dep[e]) free_m |= 1 << col;
                zc |= (int)part[e] << col;
                hc |= (int)part[64 + e] << col;
            }
            pack_f |= (uint64_t)free_m << (8 * rr);
            pack_z |= (uint64_t)zc << (8 * rr);
            pack_h |= (uint64_t)hc << (8 * rr);
            if (free_m != named_m[rr][0] || zc != named_m[rr][1] || hc != named_m[rr][2]) named = 0;
        }
        int private_ok = (nullity > 0 && nullity <= 32);
        uint32_t seen = 0;
        for (int e = 0; e < 64; e++) {
            if (dep[e] != dep[64 + e]) private_ok = 0;
            int pc = __builtin_popcount(dep[e]);
            if (pc > 1) private_ok = 0;
            if (pc == 1) {
                uint32_t bit = 1u << __builtin_ctz(dep[e]);
                if (seen & bit) private_ok = 0;
                seen |= bit;
            }
        }
        if (__builtin_popcount(seen) != nullity) private_ok = 0;
#pragma omp critical(shape_record)
        {
            if (nullity == 32) {
                shape_n32++;
                if (eight4) shape_eight4++;
                if (named) shape_named_mask++;
                if (named && private_ok) shape_named_private++;
                int found = 0;
                for (int i = 0; i < shape_mask_count; i++)
                    if (shape_free[i] == pack_f && shape_z[i] == pack_z && shape_h[i] == pack_h) {
                        shape_mask_n[i]++;
                        found = 1;
                        break;
                    }
                if (!found && shape_mask_count < 40) {
                    shape_free[shape_mask_count] = pack_f;
                    shape_z[shape_mask_count] = pack_z;
                    shape_h[shape_mask_count] = pack_h;
                    shape_mask_n[shape_mask_count] = 1;
                    shape_mask_count++;
                }
            }
        }
        if (nodes_out) *nodes_out = 0;
        return 8;
    }
    uint64_t nodes = 0;
    int got = rank_dp(comp, ncomp, g, h, dep, part, &nodes, cap);
    if (nodes_out) *nodes_out = nodes;
    return got;
}

static void fill_dep(const Basis *b, uint8_t part_g[N], uint8_t part_h[N], uint8_t part[128], uint32_t dep[128],
                     int *nf_out) {
    unpack_solution(part_g, part_h, b);
    memset(dep, 0, 128 * sizeof(uint32_t));
    uint8_t used[128] = {0};
    int nf = 0, free_var[32];
    for (int p = 0; p < b->np; p++) used[b->pvar[p]] = 1;
    for (int v = 0; v < 128; v++)
        if (!used[v] && nf < 32) free_var[nf++] = v;
    for (int e = 0; e < 64; e++) {
        part[e] = (uint8_t)((part_g[e >> 3] >> (e & 7)) & 1);
        part[64 + e] = (uint8_t)((part_h[e >> 3] >> (e & 7)) & 1);
    }
    for (int t = 0; t < nf; t++) {
        int v = free_var[t];
        dep[v] |= 1u << t;
        for (int p = 0; p < b->np; p++)
            if (basis_bit(b->lo[p], b->hi[p], v)) dep[b->pvar[p]] |= 1u << t;
    }
    *nf_out = nf;
}

static int affine_samples_ok(const Basis *b, const Eq eq_g, const Eq eq_h, const Mat defect) {
    uint8_t zg[N], zh[N];
    unpack_solution(zg, zh, b);
    if (!mats_satisfy(eq_g, eq_h, defect, zg, zh)) return 0;
    uint8_t used[128] = {0};
    for (int p = 0; p < b->np; p++) used[b->pvar[p]] = 1;
    for (int v = 0; v < 128; v++) {
        if (used[v]) continue;
        uint8_t yg[N], yh[N];
        memcpy(yg, zg, N);
        memcpy(yh, zh, N);
        if (v < 64)
            yg[v >> 3] ^= (uint8_t)(1u << (v & 7));
        else
            yh[(v - 64) >> 3] ^= (uint8_t)(1u << ((v - 64) & 7));
        for (int p = 0; p < b->np; p++) {
            if (!basis_bit(b->lo[p], b->hi[p], v)) continue;
            int pv = b->pvar[p];
            if (pv < 64)
                yg[pv >> 3] ^= (uint8_t)(1u << (pv & 7));
            else
                yh[(pv - 64) >> 3] ^= (uint8_t)(1u << ((pv - 64) & 7));
        }
        if (!mats_satisfy(eq_g, eq_h, defect, yg, yh)) return 0;
    }
    return 1;
}

static void run_control(const Call bank[12][6], int diagonal) {
    Mat target;
    build_target(target);
    uint8_t thin0[N] = {0}, thin1[N] = {0};
    for (int leaf = 1; leaf <= 2; leaf++)
        for (int r = 0; r < 2; r++) {
            thin0[r] |= (uint8_t)(1u << (2 * leaf + r));
            thin0[2 * leaf + r] |= (uint8_t)(1u << r);
        }
    for (int r = 0; r < 2; r++) {
        thin1[r] |= (uint8_t)(1u << (6 + r));
        thin1[6 + r] |= (uint8_t)(1u << r);
    }
    if (rank_f2(thin0) != 4 || rank_f2(thin1) != 4) die("control ranks");
    typedef struct {
        Mat p, e;
    } Dual;
    Dual word;
    meye(word.p);
    mzero(word.e);
    int chrono_stage[8] = {0, 0, -1, 1, 1, 2, 2, -2};
    int chrono_half[8] = {0, 1, 0, 0, 1, 0, 1, 0};
    for (int t = 0; t < 8; t++) {
        Dual factor, next;
        mzero(factor.e);
        if (chrono_stage[t] >= 0) {
            int stage = chrono_stage[t], half = chrono_half[t];
            const Call *call = &bank[diagonal][stage * 2 + half];
            pure_from_proj(factor.p, call->proj, stage);
            scale_read(factor.e, call->readm, stage);
        } else {
            meye(factor.p);
            const uint8_t *thin = chrono_stage[t] == -1 ? thin0 : thin1;
            for (int i = 0; i < N; i++)
                for (int j = 0; j < N; j++)
                    if (thin[i] & (1u << j)) factor.e[i][j] = 1;
        }
        mmul(next.p, factor.p, word.p);
        Mat pe, ep, sum;
        mmul(pe, factor.p, word.e);
        mmul(ep, factor.e, word.p);
        madd(sum, pe, ep);
        memcpy(next.e, sum, sizeof sum);
        word = next;
    }
    if (!msame(word.p, target) || !msame(word.e, target)) die("control dual product");

    Mat gates[6], right[7], left[7], prod, full, read, contrib, defect;
    for (int stage = 0; stage < G; stage++)
        for (int half = 0; half < 2; half++)
            pure_from_proj(gates[stage * 2 + half], bank[diagonal][stage * 2 + half].proj, stage);
    meye(right[0]);
    int order[6] = {0, 1, 2, 3, 4, 5};
    for (int k = 0; k < 6; k++) {
        mmul(prod, gates[order[k]], right[k]);
        memcpy(right[k + 1], prod, sizeof prod);
    }
    if (!msame(right[6], target)) die("control pure");
    meye(left[6]);
    for (int k = 5; k >= 0; k--) {
        mmul(prod, left[k + 1], gates[order[k]]);
        memcpy(left[k], prod, sizeof prod);
    }
    mzero(full);
    for (int k = 0; k < 6; k++) {
        scale_read(read, bank[diagonal][order[k]].readm, order[k] / 2);
        Mat tmp;
        mmul(tmp, read, right[k]);
        mmul(contrib, left[k + 1], tmp);
        madd(full, full, contrib);
    }
    madd(defect, full, target);
    Eq eq[7];
    for (int g = 0; g < 7; g++) {
        eq_clear(eq[g]);
        eq_add_map(eq[g], left[g], right[g]);
    }
    Basis basis;
    int nullity = solve_pair(&basis, eq[2], eq[6], defect);
    if (nullity != 16) die("control nullity");
    if (!affine_samples_ok(&basis, eq[2], eq[6], defect)) die("control affine");
    if (!mats_satisfy(eq[2], eq[6], defect, thin0, thin1)) die("control matrices");
    uint64_t nodes = 0;
    int got = f4_rank_bb(&basis, nullity, 2000000ull, &nodes);
    if (got != 8) die("control F4 rank");
    printf("control_nullity=16 control_f4_min=8 control_nodes=%llu\n", (unsigned long long)nodes);
    printf("PASS_CONTROL\n");
}

static void scalar_gate(uint8_t gate[N][N], const uint8_t proj[N], uint8_t scalar) {
    memset(gate, 0, N * N);
    for (int i = 0; i < N; i++) gate[i][i] = 1;
    if (!scalar) return;
    for (int i = 0; i < N; i++) {
        uint8_t row = proj[i];
        while (row) {
            unsigned bit = row & (unsigned)-((int)row);
            int col = __builtin_ctz(bit);
            gate[i][col] ^= scalar;
            row = (uint8_t)(row ^ bit);
        }
    }
}

static void scalar_mul(uint8_t out[N][N], const uint8_t a[N][N], const uint8_t b[N][N]) {
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) {
            unsigned acc = 0;
            for (int k = 0; k < N; k++)
                if (a[i][k]) acc ^= MUL[a[i][k]][b[k][j]];
            out[i][j] = (uint8_t)acc;
        }
}

static void run_audit(const Call bank[12][6], const uint8_t perms[NPERM][6], int c0_only) {
    const uint8_t pt[3] = {2, 3, 5};
    Mat target;
    build_target(target);
    uint8_t starget[N][N];
    memset(starget, 0, sizeof starget);
    for (int i = 0; i < N; i++) starget[i][i] = 1;
    for (int stage = 0; stage < G; stage++) {
        uint8_t eproj[N], egate[N][N], prod[N][N];
        support_e(eproj, stage);
        scalar_gate(egate, eproj, (uint8_t)(pt[stage] ^ 1));
        scalar_mul(prod, egate, starget);
        memcpy(starget, prod, sizeof prod);
    }
    int eval_mismatch = 0;
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            if (poly_at(target[i][j], pt) != starget[i][j]) eval_mismatch++;
    uint64_t poly_hits = 0, spec_hits = 0, eval_hits = 0, disagree = 0;
    int c0_hi = c0_only;
    for (int c0 = 0; c0 <= c0_hi; c0++)
        for (int c1 = 0; c1 < 12; c1++)
            for (int c2 = 0; c2 < 12; c2++) {
                const int choice[3] = {c0, c1, c2};
                Mat gates[6];
                uint8_t sgates[6][N][N];
                uint8_t proj[6][N];
                for (int stage = 0; stage < 3; stage++)
                    for (int half = 0; half < 2; half++) {
                        int id = stage * 2 + half;
                        memcpy(proj[id], bank[choice[stage]][id].proj, N);
                        pure_from_proj(gates[id], proj[id], stage);
                        scalar_gate(sgates[id], proj[id], (uint8_t)(pt[stage] ^ 1));
                    }
                for (int p = 0; p < NPERM; p++) {
                    Mat right[7], prod;
                    meye(right[0]);
                    uint8_t sright[7][N][N], sprod[N][N];
                    memset(sright, 0, sizeof sright);
                    for (int i = 0; i < N; i++) sright[0][i][i] = 1;
                    for (int k = 0; k < 6; k++) {
                        mmul(prod, gates[perms[p][k]], right[k]);
                        memcpy(right[k + 1], prod, sizeof prod);
                        scalar_mul(sprod, sgates[perms[p][k]], sright[k]);
                        memcpy(sright[k + 1], sprod, sizeof sprod);
                    }
                    int poly_ok = msame(right[6], target);
                    int spec_ok = memcmp(sright[6], starget, sizeof starget) == 0;
                    int eval_ok = 1;
                    for (int i = 0; i < N && eval_ok; i++)
                        for (int j = 0; j < N; j++)
                            if (poly_at(right[6][i][j], pt) != starget[i][j]) eval_ok = 0;
                    if (poly_ok) poly_hits++;
                    if (spec_ok) spec_hits++;
                    if (eval_ok) eval_hits++;
                    if (poly_ok != spec_ok || poly_ok != eval_ok) disagree++;
                }
            }
    printf("audit_eval_target_mismatch=%d poly_hits=%llu spec_hits=%llu eval_hits=%llu disagree=%llu overflow=%d\n",
           eval_mismatch, (unsigned long long)poly_hits, (unsigned long long)spec_hits, (unsigned long long)eval_hits,
           (unsigned long long)disagree, overflow_count);
    if (eval_mismatch || disagree || overflow_count) die("audit");
    printf("PASS_AUDIT\n");
}

static const uint8_t STAR_D[8] = {0x54, 0xa8, 0x01, 0x02, 0x01, 0x02, 0x01, 0x02};
static const int NAMED_MASK[8][3] = {{0x33, 0x14, 0x40}, {0x33, 0x28, 0x80}, {0xcc, 0x01, 0x00}, {0xcc, 0x02, 0x00},
                                      {0x33, 0x01, 0x00}, {0x33, 0x02, 0x00}, {0xcc, 0x00, 0x01}, {0xcc, 0x00, 0x02}};
static const int FOREIGN_NVAR[8] = {4, 4, 4, 4, 2, 2, 2, 2};
static const int FOREIGN_ROW[8] = {3, 4, 6, 7, 0, 1, 2, 5};

typedef struct {
    int nullity;
    int ncomp;
    int fixed_g, fixed_h;
    int nvar[16];
    int row_a[16];
    int row_b[16];
    int free_m[8];
    int zc[8];
    int hc[8];
    int private_ok;
} ShapeInfo;

static int read_shape(const Basis *b, ShapeInfo *out) {
    memset(out, 0, sizeof *out);
    int free_var[32], nf = 0;
    uint8_t used[128] = {0};
    for (int p = 0; p < b->np; p++) used[b->pvar[p]] = 1;
    for (int v = 0; v < 128; v++)
        if (!used[v]) {
            if (nf == 32) return -1;
            free_var[nf++] = v;
        }
    out->nullity = 128 - b->np;
    if (nf != out->nullity) return -1;
    uint8_t part_g[N], part_h[N], part[128];
    unpack_solution(part_g, part_h, b);
    uint32_t dep[128];
    memset(dep, 0, sizeof dep);
    for (int e = 0; e < 64; e++) {
        part[e] = (uint8_t)((part_g[e >> 3] >> (e & 7)) & 1);
        part[64 + e] = (uint8_t)((part_h[e >> 3] >> (e & 7)) & 1);
    }
    for (int t = 0; t < nf; t++) {
        int v = free_var[t];
        dep[v] |= 1u << t;
        for (int p = 0; p < b->np; p++)
            if (basis_bit(b->lo[p], b->hi[p], v)) dep[b->pvar[p]] |= 1u << t;
    }
    int parentv[32];
    for (int t = 0; t < nf; t++) parentv[t] = t;
    uint32_t row_mask[16];
    for (int r = 0; r < 16; r++) {
        uint32_t mask = 0;
        int base = r < 8 ? 0 : 64, rr = r < 8 ? r : r - 8;
        for (int col = 0; col < 8; col++) mask |= dep[base + rr * 8 + col];
        row_mask[r] = mask;
        int first = -1;
        while (mask) {
            int t = __builtin_ctz(mask);
            mask &= mask - 1;
            if (first < 0)
                first = t;
            else {
                int a = first, c = t;
                while (parentv[a] != a) a = parentv[a];
                while (parentv[c] != c) c = parentv[c];
                parentv[c] = a;
                first = a;
            }
        }
    }
    int root_id[32], ncomp = 0;
    for (int t = 0; t < 32; t++) root_id[t] = -1;
    AffComp comp[16];
    memset(comp, 0, sizeof comp);
    for (int t = 0; t < nf; t++) {
        int a = t;
        while (parentv[a] != a) a = parentv[a];
        parentv[t] = a;
        if (root_id[a] < 0) {
            if (ncomp == 16) return -1;
            root_id[a] = ncomp++;
        }
        AffComp *co = &comp[root_id[a]];
        if (co->nvar == 8) return -1;
        co->var[co->nvar++] = t;
    }
    RowBasis g, h;
    rb_clear(&g);
    rb_clear(&h);
    uint8_t zero_c[32] = {0};
    for (int r = 0; r < 16; r++) {
        if (row_mask[r]) {
            int root = -1;
            uint32_t mask = row_mask[r];
            while (mask) {
                int t = __builtin_ctz(mask);
                mask &= mask - 1;
                int id = root_id[parentv[t]];
                if (root < 0)
                    root = id;
                else if (root != id)
                    return -1;
            }
            AffComp *co = &comp[root];
            if (co->nrows == 16) return -1;
            co->rows[co->nrows++] = r;
        } else {
            uint8_t row[8];
            materialize_row(row, r, zero_c, dep, part);
            if (r < 8)
                rb_insert(&g, row);
            else
                rb_insert(&h, row);
        }
    }
    for (int i = 1; i < ncomp; i++) {
        AffComp key = comp[i];
        int j = i - 1;
        while (j >= 0 && comp[j].nvar < key.nvar) {
            comp[j + 1] = comp[j];
            j--;
        }
        comp[j + 1] = key;
    }
    out->ncomp = ncomp;
    out->fixed_g = g.dim;
    out->fixed_h = h.dim;
    for (int i = 0; i < ncomp; i++) {
        out->nvar[i] = comp[i].nvar;
        out->row_a[i] = comp[i].nrows > 0 ? comp[i].rows[0] : -1;
        out->row_b[i] = comp[i].nrows > 1 ? comp[i].rows[1] : -1;
    }
    int private_ok = 1;
    uint32_t seen = 0;
    for (int e = 0; e < 64; e++) {
        if (dep[e] != dep[64 + e]) private_ok = 0;
        int pc = __builtin_popcount(dep[e]);
        if (pc > 1) private_ok = 0;
        if (pc == 1) {
            uint32_t bit = 1u << __builtin_ctz(dep[e]);
            if (seen & bit) private_ok = 0;
            seen |= bit;
        }
    }
    if (__builtin_popcount(seen) != nf) private_ok = 0;
    for (int rr = 0; rr < 8; rr++) {
        int free_m = 0, zc = 0, hc = 0;
        for (int col = 0; col < 8; col++) {
            int e = rr * 8 + col;
            if (dep[e]) free_m |= 1 << col;
            zc |= (int)part[e] << col;
            hc |= (int)part[64 + e] << col;
        }
        out->free_m[rr] = free_m;
        out->zc[rr] = zc;
        out->hc[rr] = hc;
        if ((zc ^ hc) != STAR_D[rr]) private_ok = 0;
    }
    out->private_ok = private_ok;
    return 0;
}

static int solve_word(const Call bank[][6], const uint8_t perms[NPERM][6], const Mat target, int c0, int c1, int c2,
                      int perm, int g0, int g1, Basis *basis) {
    const int choice[3] = {c0, c1, c2};
    uint8_t readm[6][N];
    int stage_of[6];
    Mat gates[6];
    for (int stage = 0; stage < 3; stage++)
        for (int half = 0; half < 2; half++) {
            int id = stage * 2 + half;
            memcpy(readm[id], bank[choice[stage]][id].readm, N);
            stage_of[id] = stage;
            pure_from_proj(gates[id], bank[choice[stage]][id].proj, stage);
        }
    Mat right[7], left[7], prod;
    meye(right[0]);
    for (int k = 0; k < 6; k++) {
        mmul(prod, gates[perms[perm][k]], right[k]);
        memcpy(right[k + 1], prod, sizeof prod);
    }
    if (!msame(right[6], target)) return -1;
    meye(left[6]);
    for (int k = 5; k >= 0; k--) {
        mmul(prod, left[k + 1], gates[perms[perm][k]]);
        memcpy(left[k], prod, sizeof prod);
    }
    Mat full, read, contrib, defect;
    mzero(full);
    for (int k = 0; k < 6; k++) {
        int id = perms[perm][k];
        scale_read(read, readm[id], stage_of[id]);
        Mat tmp;
        mmul(tmp, read, right[k]);
        mmul(contrib, left[k + 1], tmp);
        madd(full, full, contrib);
    }
    madd(defect, full, target);
    Eq eq[7];
    for (int g = 0; g < 7; g++) {
        eq_clear(eq[g]);
        eq_add_map(eq[g], left[g], right[g]);
    }
    int nullity = solve_pair(basis, eq[g0], eq[g1], defect);
    if (nullity < 0) return -1;
    if (!affine_samples_ok(basis, eq[g0], eq[g1], defect)) return -2;
    return nullity;
}

static int rank_f4_buf(uint8_t *A, int n, int m) {
    uint8_t a[8][8];
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++) a[i][j] = A[i * m + j];
    int r = 0;
    for (int c = 0; c < m && r < n; c++) {
        int piv = -1;
        for (int i = r; i < n; i++)
            if (a[i][c]) {
                piv = i;
                break;
            }
        if (piv < 0) continue;
        if (piv != r)
            for (int j = c; j < m; j++) {
                uint8_t t = a[r][j];
                a[r][j] = a[piv][j];
                a[piv][j] = t;
            }
        uint8_t inv = F4_INV[a[r][c]];
        for (int j = c; j < m; j++) a[r][j] = F4_MUL[inv][a[r][j]];
        for (int i = 0; i < n; i++)
            if (i != r && a[i][c]) {
                uint8_t f = a[i][c];
                for (int j = c; j < m; j++) a[i][j] ^= F4_MUL[f][a[r][j]];
            }
        r++;
    }
    return r;
}

static void put_block(uint8_t *A, int stride, int br, int bc, const uint8_t M[4]) {
    for (int i = 0; i < 2; i++)
        for (int j = 0; j < 2; j++) A[(2 * br + i) * stride + (2 * bc + j)] = M[i * 2 + j];
}

static void mul_block(uint8_t out[4], const uint8_t A[4], const uint8_t B[4]) {
    for (int i = 0; i < 2; i++)
        for (int j = 0; j < 2; j++)
            out[i * 2 + j] = F4_MUL[A[i * 2]][B[j]] ^ F4_MUL[A[i * 2 + 1]][B[2 + j]];
}

static void add_block(uint8_t out[4], const uint8_t A[4], const uint8_t B[4]) {
    for (int i = 0; i < 4; i++) out[i] = (uint8_t)(A[i] ^ B[i]);
}

/* Ranks of Z, Z+D and the two Schur complements. Returns ez + 8*ed + 64*rz + 512*rzd. */
static int schur_ranks(const uint8_t P[4], const uint8_t Q[4], const uint8_t R[4], const uint8_t S[4],
                       const uint8_t T[4], const uint8_t U[4], const uint8_t V[4], const uint8_t W[4]) {
    const uint8_t I[4] = {1, 0, 0, 1};
    const uint8_t Z0[4] = {0, 0, 0, 0};
    uint8_t IQ[4], IT[4], RP[4], RIX[4], VP[4], VX[4], SP[4], SQ[4], WP[4], WQ[4], IRP[4], IWP[4];
    add_block(IQ, I, Q);
    add_block(IT, I, T);
    mul_block(RP, R, P);
    mul_block(RIX, R, IQ);
    mul_block(VP, V, P);
    mul_block(VX, V, IQ);
    mul_block(SP, S, P);
    mul_block(SQ, S, Q);
    mul_block(WP, W, P);
    mul_block(WQ, W, Q);
    add_block(IRP, I, RP);
    add_block(IWP, I, WP);
    uint8_t Z[64], ZD[64], EZ[36], ED[36], ZD_FORM[64];
    memset(Z, 0, sizeof Z);
    memset(ZD, 0, sizeof ZD);
    memset(EZ, 0, sizeof EZ);
    memset(ED, 0, sizeof ED);
    memset(ZD_FORM, 0, sizeof ZD_FORM);
    put_block(Z, 8, 0, 0, P);
    put_block(Z, 8, 0, 1, I);
    put_block(Z, 8, 0, 2, IQ);
    put_block(Z, 8, 1, 0, I);
    put_block(Z, 8, 1, 1, R);
    put_block(Z, 8, 1, 3, S);
    put_block(Z, 8, 2, 0, IT);
    put_block(Z, 8, 2, 2, U);
    put_block(Z, 8, 3, 1, V);
    put_block(Z, 8, 3, 3, W);
    put_block(ZD, 8, 0, 1, I);
    put_block(ZD, 8, 0, 2, I);
    put_block(ZD, 8, 0, 3, I);
    put_block(ZD, 8, 1, 0, I);
    put_block(ZD, 8, 2, 0, I);
    put_block(ZD, 8, 3, 0, I);
    for (int i = 0; i < 64; i++) ZD[i] ^= Z[i];
    put_block(ZD_FORM, 8, 0, 0, P);
    put_block(ZD_FORM, 8, 0, 2, Q);
    put_block(ZD_FORM, 8, 0, 3, I);
    put_block(ZD_FORM, 8, 1, 1, R);
    put_block(ZD_FORM, 8, 1, 3, S);
    put_block(ZD_FORM, 8, 2, 0, T);
    put_block(ZD_FORM, 8, 2, 2, U);
    put_block(ZD_FORM, 8, 3, 0, I);
    put_block(ZD_FORM, 8, 3, 1, V);
    put_block(ZD_FORM, 8, 3, 3, W);
    if (memcmp(ZD, ZD_FORM, sizeof ZD) != 0) return -1;
    put_block(EZ, 6, 0, 0, IRP);
    put_block(EZ, 6, 0, 1, RIX);
    put_block(EZ, 6, 0, 2, S);
    put_block(EZ, 6, 1, 0, IT);
    put_block(EZ, 6, 1, 1, U);
    put_block(EZ, 6, 2, 0, VP);
    put_block(EZ, 6, 2, 1, VX);
    put_block(EZ, 6, 2, 2, W);
    put_block(ED, 6, 0, 0, SP);
    put_block(ED, 6, 0, 1, R);
    put_block(ED, 6, 0, 2, SQ);
    put_block(ED, 6, 1, 0, T);
    put_block(ED, 6, 1, 2, U);
    put_block(ED, 6, 2, 0, IWP);
    put_block(ED, 6, 2, 1, V);
    put_block(ED, 6, 2, 2, WQ);
    int ez = rank_f4_buf(EZ, 6, 6), ed = rank_f4_buf(ED, 6, 6);
    int rz = rank_f4_buf(Z, 8, 8), rzd = rank_f4_buf(ZD, 8, 8);
    (void)Z0;
    return ez | (ed << 4) | (rz << 8) | (rzd << 12);
}

static void block_at(uint8_t out[4], int code) {
    /* 0, I, E11, E12. */
    static const uint8_t table[4][4] = {{0, 0, 0, 0}, {1, 0, 0, 1}, {1, 0, 0, 0}, {0, 1, 0, 0}};
    memcpy(out, table[code & 3], 4);
}

static void schur_smoke(void) {
    const uint8_t Z0[4] = {0, 0, 0, 0};
    const uint8_t I[4] = {1, 0, 0, 1};
    const uint8_t E11[4] = {1, 0, 0, 0};
    int zero = schur_ranks(Z0, Z0, Z0, Z0, Z0, Z0, Z0, Z0);
    int split = schur_ranks(I, I, I, Z0, I, Z0, Z0, Z0);
    int rank1 = schur_ranks(Z0, Z0, Z0, Z0, E11, Z0, Z0, Z0);
    if (zero != (2 | (2 << 4) | (4 << 8) | (4 << 12))) die("sharp zero");
    if (split != (0 | (4 << 4) | (2 << 8) | (6 << 12))) die("sharp split");
    if (rank1 != (2 | (2 << 4) | (4 << 8) | (4 << 12))) die("sharp rank1");
    int min_sum = 99, identity_bad = 0, points = 0;
    uint8_t B[8][4];
    for (int code = 0; code < 65536; code++) {
        int x = code;
        for (int k = 0; k < 8; k++) {
            block_at(B[k], x & 3);
            x >>= 2;
        }
        int packed = schur_ranks(B[0], B[1], B[2], B[3], B[4], B[5], B[6], B[7]);
        if (packed < 0) die("ZD formula");
        int ez = packed & 15, ed = (packed >> 4) & 15, rz = (packed >> 8) & 15, rzd = (packed >> 12) & 15;
        if (rz != 2 + ez || rzd != 2 + ed || ez + ed < 4) {
            fprintf(stderr, "grid fail code=%d ez=%d ed=%d rz=%d rzd=%d\n", code, ez, ed, rz, rzd);
            identity_bad++;
            break;
        }
        if (ez + ed < min_sum) min_sum = ez + ed;
        points++;
    }
    uint64_t state = 1;
    for (int n = 0; n < 20000; n++) {
        state = state * 6364136223846793005ULL + 1;
        uint32_t rnd = (uint32_t)(state >> 32);
        for (int k = 0; k < 8; k++)
            for (int t = 0; t < 4; t++) {
                B[k][t] = (uint8_t)(rnd & 3);
                rnd >>= 2;
                if (t == 1) {
                    state = state * 6364136223846793005ULL + 1;
                    rnd = (uint32_t)(state >> 32);
                }
            }
        int packed = schur_ranks(B[0], B[1], B[2], B[3], B[4], B[5], B[6], B[7]);
        if (packed < 0) die("ZD formula random");
        int ez = packed & 15, ed = (packed >> 4) & 15, rz = (packed >> 8) & 15, rzd = (packed >> 12) & 15;
        if (rz != 2 + ez || rzd != 2 + ed || ez + ed < 4) {
            fprintf(stderr, "random fail n=%d ez=%d ed=%d rz=%d rzd=%d\n", n, ez, ed, rz, rzd);
            for (int k = 0; k < 8; k++)
                fprintf(stderr, " %d%d%d%d", B[k][0], B[k][1], B[k][2], B[k][3]);
            fprintf(stderr, "\n");
            identity_bad++;
            break;
        }
        if (ez + ed < min_sum) min_sum = ez + ed;
        points++;
    }
    if (identity_bad || min_sum < 4) die("schur smoke");
    printf("schur_smoke points=%d grid=65536 random=20000 min_schur=%d identity_bad=%d sharp_zero=2,2 sharp_split=0,4 sharp_rank1=2,2\n",
           points, min_sum, identity_bad);
}

static void require_shape(const char *name, const ShapeInfo *info, int nullity, int ncomp) {
    if (info->nullity != nullity || info->ncomp != ncomp) {
        fprintf(stderr, "%s bad shape nullity=%d ncomp=%d\n", name, info->nullity, info->ncomp);
        die("shape");
    }
}

static void run_witness(const Call bank[][6], const uint8_t perms[NPERM][6], const Mat target) {
    Basis basis;
    int nullity = solve_word(bank, perms, target, 0, 0, 0, 0, 2, 4, &basis);
    if (nullity < 0) die("named solve");
    ShapeInfo info;
    if (read_shape(&basis, &info)) die("named shape");
    require_shape("named", &info, 32, 8);
    if (info.fixed_g || info.fixed_h || !info.private_ok) die("named private");
    for (int i = 0; i < 8; i++) {
        if (info.nvar[i] != 4 || info.row_a[i] != i || info.row_b[i] != i + 8) die("named components");
        if (info.free_m[i] != NAMED_MASK[i][0] || info.zc[i] != NAMED_MASK[i][1] || info.hc[i] != NAMED_MASK[i][2])
            die("named mask");
    }
    uint64_t nodes = 0;
    int got = f4_rank_bb(&basis, nullity, ~0ull, &nodes);
    if (got != -3) die("named dp");
    printf("named c=0,0,0 perm=0 gaps=2,4 nullity=32 block=1 private=1 dp=%d nodes=%llu\n", got,
           (unsigned long long)nodes);

    nullity = solve_word(bank, perms, target, 0, 0, 0, 4, 2, 4, &basis);
    if (nullity < 0) die("foreign solve");
    if (read_shape(&basis, &info)) die("foreign shape");
    require_shape("foreign", &info, 24, 8);
    if (info.fixed_g || info.fixed_h) die("foreign fixed");
    int all4 = 1;
    for (int i = 0; i < 8; i++) {
        if (info.nvar[i] != FOREIGN_NVAR[i] || info.row_a[i] != FOREIGN_ROW[i] ||
            info.row_b[i] != FOREIGN_ROW[i] + 8)
            die("foreign components");
        if (info.nvar[i] != 4) all4 = 0;
    }
    if (all4) die("foreign collapsed to the block shape");
    nodes = 0;
    got = f4_rank_bb(&basis, nullity, ~0ull, &nodes);
    if (got != -3) die("foreign dp");
    printf("foreign c=0,0,0 perm=4 gaps=2,4 nullity=24 block=0 dp=%d nodes=%llu\n", got, (unsigned long long)nodes);
    schur_smoke();
    printf("PASS_NULLITY32_SCHUR\n");
}

int main(int argc, char **argv) {
    init_tables();
    ResBits bits[12];
    int nres = build_resolutions(bits);
    if (nres != 12) die("resolution count");
    int diagonal = -1;
    for (int i = 0; i < 12; i++)
        if (bits[i].b == 0) diagonal = i;
    if (diagonal < 0) die("diagonal");
    Call bank[12][6];
    for (int r = 0; r < 12; r++)
        for (int stage = 0; stage < G; stage++)
            for (int half = 0; half < 2; half++) make_call(&bank[r][stage * 2 + half], &bits[r], stage, half);
    uint8_t perms[NPERM][6];
    heap_perms(perms);
    int c0_lo = 0, c0_hi = -1;
    /* The node counter is not the certificate budget. The DP stops only when a
     * class stores 2^20 partial row spaces. */
    uint64_t cap = ~0ull;
    if (argc > 1 && strcmp(argv[1], "witness") == 0) {
        Mat target;
        build_target(target);
        run_witness(bank, perms, target);
        return 0;
    } else if (argc > 1 && strcmp(argv[1], "shapes") == 0) {
        shape_only = 1;
        c0_lo = 0;
        c0_hi = 11;
    } else if (argc > 1 && strcmp(argv[1], "control") == 0) {
        run_control(bank, diagonal);
        return 0;
    } else if (argc > 1 && strcmp(argv[1], "audit") == 0) {
        run_audit(bank, perms, atoi(argv[2]));
        return 0;
    } else if (argc > 1 && strcmp(argv[1], "census") == 0) {
        c0_lo = atoi(argv[2]);
        c0_hi = atoi(argv[3]);
        if (argc > 4) cap = strtoull(argv[4], 0, 10);
    } else
        die("usage: search witness | search shapes | search control | search audit hi | search census lo hi");

    Mat target;
    build_target(target);
    enum { SIG_SLOTS = 1 << 21 };
    uint64_t *sig_tab = calloc(SIG_SLOTS, sizeof(uint64_t));
    if (!sig_tab) die("sig");
    int sig_count = 0, class_ge8 = 0, class_cap = 0, class_low = 0, class_bad = 0;
    int crank_bad = 0, dep_bad = 0, affine_bad = 0;
    int min_null = 99, max_null = -1, diff_bad = 0;
    static const uint8_t star_d[8] = {0x54, 0xa8, 0x01, 0x02, 0x01, 0x02, 0x01, 0x02};
    uint64_t screened = 0, exact_hits = 0, consistent = 0, inconsistent = 0;

#pragma omp parallel for schedule(dynamic) reduction(+ : screened, exact_hits, consistent, inconsistent)
    for (int c0 = c0_lo; c0 <= c0_hi; c0++) {
        for (int c1 = 0; c1 < 12; c1++)
            for (int c2 = 0; c2 < 12; c2++) {
                const int choice[3] = {c0, c1, c2};
                uint8_t readm[6][N];
                int stage_of[6];
                Mat gates[6];
                for (int stage = 0; stage < 3; stage++)
                    for (int half = 0; half < 2; half++) {
                        int id = stage * 2 + half;
                        memcpy(readm[id], bank[choice[stage]][id].readm, N);
                        stage_of[id] = stage;
                        pure_from_proj(gates[id], bank[choice[stage]][id].proj, stage);
                    }
                for (int p = 0; p < NPERM; p++) {
                    screened++;
                    Mat right[7], left[7], prod;
                    meye(right[0]);
                    int pure_ok = 1;
                    for (int k = 0; k < 6; k++) {
                        mmul(prod, gates[perms[p][k]], right[k]);
                        memcpy(right[k + 1], prod, sizeof prod);
                    }
                    if (!msame(right[6], target)) pure_ok = 0;
                    if (!pure_ok) continue;
                    exact_hits++;
                    meye(left[6]);
                    for (int k = 5; k >= 0; k--) {
                        mmul(prod, left[k + 1], gates[perms[p][k]]);
                        memcpy(left[k], prod, sizeof prod);
                    }
                    Mat full, read, contrib, defect;
                    mzero(full);
                    for (int k = 0; k < 6; k++) {
                        int id = perms[p][k];
                        scale_read(read, readm[id], stage_of[id]);
                        Mat tmp;
                        mmul(tmp, read, right[k]);
                        mmul(contrib, left[k + 1], tmp);
                        madd(full, full, contrib);
                    }
                    madd(defect, full, target);
                    Eq eq[7];
                    for (int g = 0; g < 7; g++) {
                        eq_clear(eq[g]);
                        eq_add_map(eq[g], left[g], right[g]);
                    }
                    for (int g0 = 0; g0 < 7; g0++)
                        for (int g1 = g0 + 1; g1 < 7; g1++) {
                            Basis basis;
                            int nullity = solve_pair(&basis, eq[g0], eq[g1], defect);
                            if (nullity < 0) {
                                inconsistent++;
                                continue;
                            }
                            consistent++;
                            uint8_t pg[N], ph[N], part[128];
                            uint32_t dep[128];
                            int nf = 0;
                            fill_dep(&basis, pg, ph, part, dep, &nf);
                            if (nf != nullity) die("free count");
                            int mismatch = 0;
                            for (int e = 0; e < 64; e++)
                                if (dep[e] != dep[64 + e]) mismatch = 1;
                            uint8_t diff[N];
                            for (int i = 0; i < N; i++) diff[i] = (uint8_t)(pg[i] ^ ph[i]);
                            int crank = rank_f2(diff);
                            int mapv[32];
                            for (int t = 0; t < 32; t++) mapv[t] = -1;
                            int nextv = 0;
                            uint64_t sig = 1469598103934665603ull;
                            for (int e = 0; e < 128; e++) {
                                int cst = e < 64 ? (int)((pg[e >> 3] >> (e & 7)) & 1)
                                                 : (int)((ph[(e - 64) >> 3] >> ((e - 64) & 7)) & 1);
                                uint32_t m = dep[e], cm = 0;
                                while (m) {
                                    int t = __builtin_ctz(m);
                                    m &= m - 1;
                                    if (mapv[t] < 0) mapv[t] = nextv++;
                                    cm |= 1u << mapv[t];
                                }
                                sig ^= (uint64_t)(cst + 2 * (int)cm + 1);
                                sig *= 1099511628211ull;
                            }
                            if (!sig) sig = 1;
                            int mine = 0;
#pragma omp critical
                            {
                                if (nullity < min_null) min_null = nullity;
                                if (nullity > max_null) max_null = nullity;
                                if (mismatch) dep_bad++;
                                if (crank != 4) crank_bad++;
                                for (int i = 0; i < 8; i++)
                                    if ((uint8_t)(pg[i] ^ ph[i]) != star_d[i]) diff_bad++;
                                uint32_t slot = (uint32_t)sig & (SIG_SLOTS - 1);
                                int guard = 0;
                                while (sig_tab[slot] && sig_tab[slot] != sig) {
                                    slot = (slot + 1) & (SIG_SLOTS - 1);
                                    if (++guard > SIG_SLOTS) break;
                                }
                                if (!sig_tab[slot]) {
                                    sig_tab[slot] = sig;
                                    sig_count++;
                                    mine = 1;
                                }
                            }
                            if (!mine) continue;
                            if (!affine_samples_ok(&basis, eq[g0], eq[g1], defect)) {
#pragma omp atomic
                                affine_bad++;
                                die("affine sample");
                            }
                            uint64_t nodes = 0;
                            int got = f4_rank_bb(&basis, nullity, cap, &nodes);
                            if (got >= 8) {
#pragma omp atomic
                                class_ge8++;
                            } else if (got == -3) {
#pragma omp atomic
                                class_cap++;
                            } else if (got < 0) {
#pragma omp atomic
                                class_bad++;
                            } else {
#pragma omp atomic
                                class_low++;
                                printf("LOW choice=%d,%d,%d perm=%d gaps=%d,%d nullity=%d rank=%d\n", c0, c1, c2, p,
                                       g0, g1, nullity, got);
                            }
                        }
                }
            }
    }
    if (overflow_count) die("degree overflow");
    printf("screened=%llu exact_hits=%llu consistent=%llu inconsistent=%llu\n", (unsigned long long)screened,
           (unsigned long long)exact_hits, (unsigned long long)consistent, (unsigned long long)inconsistent);
    printf("signatures=%d class_ge8=%d class_low=%d class_cap=%d class_bad=%d\n", sig_count, class_ge8, class_low,
           class_cap, class_bad);
    printf("min_nullity=%d max_nullity=%d dep_bad=%d crank_bad=%d diff_bad=%d affine_bad=%d\n", min_null, max_null,
           dep_bad, crank_bad, diff_bad, affine_bad);
    if (dep_bad || crank_bad || diff_bad || affine_bad || class_bad || class_low) die("census invariant");
    if (shape_only) {
        printf("shapes signatures=%d nullity32=%d eight4=%d named_mask=%d named_private=%d mask_patterns=%d\n",
               sig_count, shape_n32, shape_eight4, shape_named_mask, shape_named_private, shape_mask_count);
        for (int i = 0; i < shape_mask_count; i++)
            printf("mask_pattern count=%d free=%016llx z=%016llx h=%016llx\n", shape_mask_n[i],
                   (unsigned long long)shape_free[i], (unsigned long long)shape_z[i],
                   (unsigned long long)shape_h[i]);
        if (screened != 1244160ull || exact_hits != 159984ull || consistent != 566352ull ||
            inconsistent != 2793312ull || sig_count != 1746 || min_null != 7 || max_null != 32)
            die("shape totals");
        if (shape_n32 != 24 || shape_eight4 != 24 || shape_named_mask != 1 || shape_named_private != 1 ||
            shape_mask_count != 24)
            die("shape profile");
        printf("PASS_SHAPES\n");
        free(sig_tab);
        return 0;
    }
    if (c0_lo == 0 && c0_hi == 11) {
        if (screened != 1244160ull || exact_hits != 159984ull || consistent != 566352ull ||
            inconsistent != 2793312ull || sig_count != 1746 || class_ge8 != 1562 || class_cap != 184)
            die("census totals");
        if (min_null != 7 || max_null != 32) die("nullity range");
    }
    printf("PASS_CENSUS\n");
    free(sig_tab);
    return 0;
}
