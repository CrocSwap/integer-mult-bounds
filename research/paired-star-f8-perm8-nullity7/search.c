/* The next distinct nullity-7 class of two thin maps on the g=3, d=2
 * paired star, after the class settled by the lex-first scan.
 *
 * Full calls stay the twelve F_2 orthogonal resolutions. The endpoint
 * equations are F_2-linear. Lex order is stage resolutions, then the heap
 * permutation, then the gap pair. The settled class is resolutions (0, 0, 3),
 * permutation 4, gaps 2 and 5. The next system, permutation 5, has the same
 * reduced basis. The next distinct affine class is permutation 8, gaps 2 and 5.
 * Chronological order: the first call is the rightmost factor.
 *
 * The rank obstruction is the case analysis in PROOF.md. The enumeration is
 * an exhaustive finite check of this one affine space over F_8.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
enum { N = 8, G = 3, NPERM = 720, NMONO = 27 };

static uint8_t MONO_MUL[NMONO][NMONO];
static int overflow_count = 0;

static int mono_index(int e0, int e1, int e2) { return e0 + 3 * e1 + 9 * e2; }

static void init_tables(void) {
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


static int same_basis(const Basis *a, const Basis *b) {
    return memcmp(a, b, sizeof(Basis)) == 0;
}

/* Lex order: resolutions, heap permutation, then gap pair. Nullity below 7
 * before the recorded class is a hard failure. A nullity-7 system whose
 * reduced basis matches the settled class is the same affine space. */
static int find_next(const Call bank[12][6], const uint8_t perms[NPERM][6], Basis *out, int *screened_out) {
    Mat target;
    build_target(target);
    int screened = 0, hits = 0, saw_settled = 0, duplicates = 0;
    Basis settled;
    memset(&settled, 0, sizeof settled);
    for (int c0 = 0; c0 < 12; c0++)
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
                    for (int k = 0; k < 6; k++) {
                        mmul(prod, gates[perms[p][k]], right[k]);
                        memcpy(right[k + 1], prod, sizeof prod);
                    }
                    if (!msame(right[6], target)) continue;
                    hits++;
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
                            if (nullity >= 0 && nullity < 7) die("nullity below 7");
                            if (nullity != 7) continue;
                            if (!saw_settled) {
                                if (!(c0 == 0 && c1 == 0 && c2 == 3 && p == 4 && g0 == 2 && g1 == 5))
                                    die("settled class moved");
                                settled = basis;
                                saw_settled = 1;
                                printf("settled_choice=0,0,3 settled_perm=4 settled_gaps=2,5 settled_screened=%d\n",
                                       screened);
                                continue;
                            }
                            if (same_basis(&basis, &settled)) {
                                if (!(c0 == 0 && c1 == 0 && c2 == 3 && p == 5 && g0 == 2 && g1 == 5) || duplicates)
                                    die("unexpected duplicate");
                                duplicates++;
                                printf("duplicate_choice=0,0,3 duplicate_perm=5 duplicate_gaps=2,5 duplicate_calls=");
                                for (int k = 0; k < 6; k++)
                                    printf("%d%s", perms[p][k], k == 5 ? "\n" : ",");
                                continue;
                            }
                            if (!(c0 == 0 && c1 == 0 && c2 == 3 && p == 8 && g0 == 2 && g1 == 5))
                                die("next class moved");
                            if (duplicates != 1) die("duplicate count");
                            *out = basis;
                            *screened_out = screened;
                            printf("next_screened=%d next_hits=%d\n", screened, hits);
                            return 7;
                        }
                }
            }
    die("next class missing");
    return -1;
}

static const uint8_t STAR[8] = {0x54, 0xa8, 0x01, 0x02, 0x01, 0x02, 0x01, 0x02};

static uint8_t F8_MUL[8][8];
static uint8_t F8_INV[8];

static void init_f8(void) {
    for (int a = 0; a < 8; a++) {
        for (int b = 0; b < 8; b++) {
            unsigned prod = 0, x = (unsigned)a, y = (unsigned)b;
            while (y) {
                if (y & 1u) prod ^= x;
                x <<= 1;
                if (x & 8u) x ^= 0xbu;
                y >>= 1u;
            }
            F8_MUL[a][b] = (uint8_t)prod;
        }
    }
    F8_INV[0] = 0;
    for (int a = 1; a < 8; a++) {
        int inv = -1;
        for (int b = 1; b < 8; b++)
            if (F8_MUL[a][b] == 1) inv = b;
        if (inv < 0) die("F8 inverse");
        F8_INV[a] = (uint8_t)inv;
    }
    if (F8_MUL[2][2] != 4 || F8_MUL[2][4] != 3) die("F8 generator");
}

static int rank_f8(uint8_t m[8][8]) {
    int rank = 0;
    for (int col = 0; col < 8; col++) {
        int pivot = -1;
        for (int i = rank; i < 8; i++)
            if (m[i][col]) {
                pivot = i;
                break;
            }
        if (pivot < 0) continue;
        if (pivot != rank) {
            for (int j = 0; j < 8; j++) {
                uint8_t tmp = m[rank][j];
                m[rank][j] = m[pivot][j];
                m[pivot][j] = tmp;
            }
        }
        uint8_t inv = F8_INV[m[rank][col]];
        for (int j = 0; j < 8; j++) m[rank][j] = F8_MUL[inv][m[rank][j]];
        for (int i = 0; i < 8; i++) {
            if (i == rank || !m[i][col]) continue;
            uint8_t factor = m[i][col];
            for (int j = 0; j < 8; j++) m[i][j] ^= F8_MUL[factor][m[rank][j]];
        }
        rank++;
    }
    return rank;
}

static void fill_class(const Basis *b, uint8_t part[128], uint32_t dep[128], int free_var[8], int *nf_out) {
    uint8_t used[128] = {0};
    for (int p = 0; p < b->np; p++) used[b->pvar[p]] = 1;
    int nf = 0;
    for (int v = 0; v < 128; v++)
        if (!used[v]) free_var[nf++] = v;
    uint8_t zg[N], zh[N];
    unpack_solution(zg, zh, b);
    memset(dep, 0, 128 * sizeof(uint32_t));
    for (int e = 0; e < 64; e++) {
        part[e] = (uint8_t)((zg[e >> 3] >> (e & 7)) & 1);
        part[64 + e] = (uint8_t)((zh[e >> 3] >> (e & 7)) & 1);
    }
    for (int t = 0; t < nf; t++) {
        int v = free_var[t];
        dep[v] |= 1u << t;
        for (int p = 0; p < b->np; p++)
            if (basis_bit(b->lo[p], b->hi[p], v)) dep[b->pvar[p]] |= 1u << t;
    }
    *nf_out = nf;
}

static void materialize(uint8_t zg[8][8], uint8_t zh[8][8], const uint8_t c[8], const uint8_t part[128],
                        const uint32_t dep[128]) {
    for (int row = 0; row < 8; row++) {
        for (int col = 0; col < 8; col++) {
            int eg = row * 8 + col;
            int eh = 64 + eg;
            uint8_t vg = part[eg], vh = part[eh];
            uint32_t bg = dep[eg], bh = dep[eh];
            while (bg) {
                vg ^= c[__builtin_ctz(bg)];
                bg &= bg - 1;
            }
            while (bh) {
                vh ^= c[__builtin_ctz(bh)];
                bh &= bh - 1;
            }
            zg[row][col] = vg;
            zh[row][col] = vh;
        }
    }
}

static uint8_t eq_c[4][8];
static int eq_rg[4], eq_rh[4], eq_n;

static int rank2_f8(uint8_t a, uint8_t b, uint8_t c, uint8_t d) {
    uint8_t m[2][2] = {{a, b}, {c, d}};
    int rank = 0;
    for (int col = 0; col < 2; col++) {
        int pivot = -1;
        for (int i = rank; i < 2; i++)
            if (m[i][col]) {
                pivot = i;
                break;
            }
        if (pivot < 0) continue;
        if (pivot != rank) {
            uint8_t t0 = m[rank][0], t1 = m[rank][1];
            m[rank][0] = m[pivot][0];
            m[rank][1] = m[pivot][1];
            m[pivot][0] = t0;
            m[pivot][1] = t1;
        }
        uint8_t inv = F8_INV[m[rank][col]];
        m[rank][0] = F8_MUL[inv][m[rank][0]];
        m[rank][1] = F8_MUL[inv][m[rank][1]];
        int other = rank ^ 1;
        if (m[other][col]) {
            uint8_t factor = m[other][col];
            m[other][0] ^= F8_MUL[factor][m[rank][0]];
            m[other][1] ^= F8_MUL[factor][m[rank][1]];
        }
        rank++;
    }
    return rank;
}

static int rank_zh_blocks(const uint8_t c[8]) {
    return (c[6] == 1 ? 2 : 4) + rank2_f8(c[0], c[1], c[4], c[5]) + (c[2] != 0) + (c[3] != 0);
}

static void enumerate_field(const uint8_t part[128], const uint32_t dep[128], int q, const char *name) {
    uint64_t hist[17];
    memset(hist, 0, sizeof hist);
    int min_sum = 99, best_rg = -1, best_rh = -1;
    uint8_t best[8] = {0};
    if (q == 8) eq_n = 0;
    uint64_t count = 0;
    uint64_t checksum = 1469598103934665603ull;
    uint8_t c[8] = {0};
    uint64_t limit = 1;
    for (int i = 0; i < 7; i++) limit *= (uint64_t)q;
    for (uint64_t code = 0; code < limit; code++) {
        uint64_t x = code;
        for (int i = 0; i < 7; i++) {
            c[i] = (uint8_t)(x % (uint64_t)q);
            x /= (uint64_t)q;
        }
        uint8_t zg[8][8], zh[8][8], ag[8][8], ah[8][8];
        materialize(zg, zh, c, part, dep);
        memcpy(ag, zg, sizeof ag);
        memcpy(ah, zh, sizeof ah);
        int rg = rank_f8(ag);
        int rh = rank_f8(ah);
        if (q == 8 && rh != rank_zh_blocks(c)) die("Zh block formula");
        int sum = rg + rh;
        hist[sum]++;
        checksum ^= (uint64_t)(sum + 17 * rg + 1);
        checksum *= 1099511628211ull;
        if (sum < min_sum) {
            min_sum = sum;
            best_rg = rg;
            best_rh = rh;
            memcpy(best, c, 7);
        }
        if (q == 8 && sum == 8 && eq_n < 4) {
            memcpy(eq_c[eq_n], c, 7);
            eq_rg[eq_n] = rg;
            eq_rh[eq_n] = rh;
            eq_n++;
        }
        count++;
    }
    printf("%s_count=%llu %s_min=%d %s_rg=%d %s_rh=%d %s_checksum=%llu %s_below8=%llu\n", name,
           (unsigned long long)count, name, min_sum, name, best_rg, name, best_rh, name,
           (unsigned long long)checksum, name, (unsigned long long)(hist[0] + hist[1] + hist[2] + hist[3] + hist[4] +
                                                                    hist[5] + hist[6] + hist[7]));
    printf("%s_best=", name);
    for (int i = 0; i < 7; i++) printf("%d%s", best[i], i == 6 ? "\n" : ",");
    printf("%s_hist=", name);
    for (int s = 0; s <= 16; s++) printf("%llu%s", (unsigned long long)hist[s], s == 16 ? "\n" : ",");
    if (q == 8) {
        printf("f8_eq8=%d\n", eq_n);
        for (int n = 0; n < eq_n; n++) {
            printf("f8_eq8_%d=", n);
            for (int i = 0; i < 7; i++) printf("%d%s", eq_c[n][i], i == 6 ? "" : ",");
            printf(" rg=%d rh=%d\n", eq_rg[n], eq_rh[n]);
        }
    }
}

/* This class: c0 at (2,2), c1 at (2,5), c2 at (3,3), c3 at (4,4),
 * c4 at (5,2), c5 at (5,5), c6 on the four diagonal sites.
 * The settled class instead uses (3,4), (4,3) and a lone (5,5). */
static int shape_var(int row, int col) {
    if ((row == 0 && col == 0) || (row == 1 && col == 1) || (row == 6 && col == 6) || (row == 7 && col == 7))
        return 6;
    if (row == 2 && col == 2) return 0;
    if (row == 2 && col == 5) return 1;
    if (row == 3 && col == 3) return 2;
    if (row == 4 && col == 4) return 3;
    if (row == 5 && col == 2) return 4;
    if (row == 5 && col == 5) return 5;
    return -1;
}
static int settled_var(int row, int col) {
    if ((row == 0 && col == 0) || (row == 1 && col == 1) || (row == 6 && col == 6) || (row == 7 && col == 7))
        return 6;
    if (row == 2 && col == 2) return 0;
    if (row == 3 && col == 3) return 1;
    if (row == 3 && col == 4) return 2;
    if (row == 4 && col == 3) return 3;
    if (row == 4 && col == 4) return 4;
    if (row == 5 && col == 5) return 5;
    return -1;
}
static int shape_const_g(int row, int col) {
    return (row == 0 && (col == 2 || col == 4)) || (row == 1 && (col == 3 || col == 5)) ||
           (row == 2 && col == 0) || (row == 3 && col == 1) || (row == 4 && col == 0) || (row == 5 && col == 1);
}
static int shape_const_h(int row, int col) {
    return (row == 0 && col == 6) || (row == 1 && col == 7) || (row == 6 && col == 0) || (row == 7 && col == 1);
}
static int shape_matches_var(const uint8_t part[128], const uint32_t dep[128], int (*var_at)(int, int)) {
    for (int row = 0; row < 8; row++)
        for (int col = 0; col < 8; col++) {
            int e = row * 8 + col;
            int var = var_at(row, col);
            uint32_t expect = var < 0 ? 0u : (1u << var);
            if (dep[e] != expect || dep[64 + e] != expect) return 0;
            if (part[e] != (uint8_t)shape_const_g(row, col)) return 0;
            if (part[64 + e] != (uint8_t)shape_const_h(row, col)) return 0;
        }
    return 1;
}

static void poly_control(const Call bank[12][6], int diagonal) {
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
    if (!msame(word.p, target) || !msame(word.e, target)) die("control identity");
    printf("control_identity=1\n");
}

static int solve_at(const Call bank[12][6], const uint8_t perms[NPERM][6], int c0, int c1, int c2, int p, int g0,
                    int g1, Basis *out) {
    Mat target;
    build_target(target);
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
        mmul(prod, gates[perms[p][k]], right[k]);
        memcpy(right[k + 1], prod, sizeof prod);
    }
    if (!msame(right[6], target)) return -2;
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
    int nullity = solve_pair(out, eq[g0], eq[g1], defect);
    if (nullity < 0) return -1;
    uint8_t zg[N], zh[N];
    unpack_solution(zg, zh, out);
    if (!mats_satisfy(eq[g0], eq[g1], defect, zg, zh)) return -3;
    uint8_t used[128] = {0};
    for (int pivot = 0; pivot < out->np; pivot++) used[out->pvar[pivot]] = 1;
    for (int v = 0; v < 128; v++) {
        if (used[v]) continue;
        uint8_t yg[N], yh[N];
        memcpy(yg, zg, N);
        memcpy(yh, zh, N);
        if (v < 64)
            yg[v >> 3] ^= (uint8_t)(1u << (v & 7));
        else
            yh[(v - 64) >> 3] ^= (uint8_t)(1u << ((v - 64) & 7));
        for (int pivot = 0; pivot < out->np; pivot++) {
            if (!basis_bit(out->lo[pivot], out->hi[pivot], v)) continue;
            int pv = out->pvar[pivot];
            if (pv < 64)
                yg[pv >> 3] ^= (uint8_t)(1u << (pv & 7));
            else
                yh[(pv - 64) >> 3] ^= (uint8_t)(1u << ((pv - 64) & 7));
        }
        if (!mats_satisfy(eq[g0], eq[g1], defect, yg, yh)) return -4;
    }
    return nullity;
}

int main(void) {
    init_tables();
    init_f8();
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
    poly_control(bank, diagonal);
    Basis found;
    int screened = 0;
    int nullity = find_next(bank, perms, &found, &screened);
    if (nullity != 7 || screened != 2169) die("scan");
    Basis again;
    int replay = solve_at(bank, perms, 0, 0, 3, 8, 2, 5, &again);
    if (replay != 7 || !same_basis(&found, &again)) die("replay nullity");
    uint8_t part[128];
    uint32_t dep[128];
    int free_var[8], nf = 0;
    fill_class(&again, part, dep, free_var, &nf);
    if (nf != 7) die("free count");
    int dep_bad = 0, star_bad = 0;
    uint8_t zg[8], zh[8];
    unpack_solution(zg, zh, &again);
    for (int e = 0; e < 64; e++)
        if (dep[e] != dep[64 + e]) dep_bad++;
    for (int i = 0; i < 8; i++)
        if ((zg[i] ^ zh[i]) != STAR[i]) star_bad++;
    for (int t = 0; t < 7; t++)
        if (dep[free_var[t]] != (1u << t)) die("free coordinate");
    if (!shape_matches_var(part, dep, shape_var)) die("shape");
    if (shape_matches_var(part, dep, settled_var)) die("settled shape");
    if (dep_bad || star_bad) die("star");
    printf("choice=0,0,3 perm=8 gaps=2,5 nullity=7 dep_bad=0 star_bad=0 new_shape=1 settled_shape=0\n");
    printf("resolution_ab=%d,%d;%d,%d;%d,%d\n", bits[0].a, bits[0].b, bits[0].a, bits[0].b, bits[3].a, bits[3].b);
    printf("perm_calls=");
    for (int k = 0; k < 6; k++) printf("%d%s", perms[8][k], k == 5 ? "\n" : ",");
    printf("free_var=");
    for (int t = 0; t < 7; t++) printf("%d%s", free_var[t], t == 6 ? "\n" : ",");
    enumerate_field(part, dep, 8, "f8");
    printf("PASS_PAIRED_STAR_F8_PERM8_NULLITY7\n");
    return 0;
}
