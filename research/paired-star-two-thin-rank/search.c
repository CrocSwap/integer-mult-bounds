/* Two thin maps on the three-leaf F_2 paired star.
 *
 * Every legal orthogonal resolution and every order of the six full calls is
 * screened. A polynomial solution specializes at the sample points below, so
 * it sits in the affine space solved for each gap pair. Rank sums are taken
 * over that larger space: a minimum of 8 rules out ranks 6 and 7.
 *
 * Chronological order: the first call is the rightmost factor.
 * gcc -O3 -std=c11 -o search search.c && ./search
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <omp.h>

enum { N = 8, G = 3, NPERM = 720 };

static uint8_t MUL[256][256];

static void init_mul(void) {
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
}

static int mul2(int left, int right) {
    int out = 0;
    for (int i = 0; i < 2; i++) {
        for (int j = 0; j < 2; j++) {
            int bit = (((left >> (2 * i)) & 1) & ((right >> j) & 1)) ^
                      (((left >> (2 * i + 1)) & 1) & ((right >> (2 + j)) & 1));
            out |= bit << (2 * i + j);
        }
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
    for (int half = 0; half < 2; half++) {
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
}

static int rows_eq(const int x[4], const int y[4]) {
    return x[0] == y[0] && x[1] == y[1] && x[2] == y[2] && x[3] == y[3];
}

static void mul4(const int left[4], const int right[4], int out[4]) {
    for (int r = 0; r < 4; r++) {
        int value = 0, rest = left[r];
        while (rest) {
            int bit = rest & -rest;
            int index = __builtin_ctz(bit);
            value ^= right[index];
            rest ^= bit;
        }
        out[r] = value;
    }
}

static void embed(uint8_t rows[N], int cc, int cl, int lc, int ll, int leaf) {
    memset(rows, 0, N);
    for (int r = 0; r < 2; r++) {
        for (int c = 0; c < 2; c++) {
            if ((cc >> (2 * r + c)) & 1) rows[r] |= (uint8_t)(1u << c);
            if ((cl >> (2 * r + c)) & 1) rows[r] |= (uint8_t)(1u << (2 * leaf + c));
            if ((lc >> (2 * r + c)) & 1) rows[2 * leaf + r] |= (uint8_t)(1u << c);
            if ((ll >> (2 * r + c)) & 1) rows[2 * leaf + r] |= (uint8_t)(1u << (2 * leaf + c));
        }
    }
}

typedef struct {
    int a, b, complement;
} ResBits;

typedef struct {
    uint8_t proj[N];
    uint8_t readm[N];
    int stage;
} Call;

static int build_resolutions(ResBits bits[12]) {
    int n = 0;
    uint64_t seen_lo[12], seen_hi[12];
    for (int bits_a = 0; bits_a < 16; bits_a++) {
        if (mul2(bits_a, bits_a) != bits_a || rank2(bits_a) != 1) continue;
        int complement = bits_a ^ 0x9;
        for (int bits_b = 0; bits_b < 16; bits_b++) {
            int first[4], second[4], zero[4] = {0, 0, 0, 0};
            int fp[4], sp[4], fs[4], sf[4];
            block_rows(bits_a, bits_b, first);
            block_rows(complement, bits_b, second);
            mul4(first, first, fp);
            mul4(second, second, sp);
            mul4(first, second, fs);
            mul4(second, first, sf);
            if (!rows_eq(fp, first) || !rows_eq(sp, second) || !rows_eq(fs, zero) || !rows_eq(sf, zero))
                continue;
            uint64_t k1 = 0, k2 = 0;
            for (int i = 0; i < 4; i++) {
                k1 |= (uint64_t)first[i] << (4 * i);
                k2 |= (uint64_t)second[i] << (4 * i);
            }
            uint64_t lo = k1 < k2 ? k1 : k2;
            uint64_t hi = k1 < k2 ? k2 : k1;
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
    call->stage = stage;
    embed(call->proj, mixed, res->b, res->b, mixed, leaf);
    embed(call->readm, matrix_a, matrix_a, matrix_a, matrix_a, leaf);
}

static void eye(uint8_t m[N][N]) {
    memset(m, 0, N * N);
    for (int i = 0; i < N; i++) m[i][i] = 1;
}

static void matmul(uint8_t out[N][N], const uint8_t a[N][N], const uint8_t b[N][N]) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            unsigned acc = 0;
            for (int k = 0; k < N; k++)
                if (a[i][k]) acc ^= MUL[a[i][k]][b[k][j]];
            out[i][j] = (uint8_t)acc;
        }
    }
}

static void gate_of(uint8_t gate[N][N], const uint8_t proj[N], uint8_t scalar) {
    eye(gate);
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

static void support_e(uint8_t proj[N], int stage) {
    memset(proj, 0, N);
    proj[0] = 1;
    proj[1] = 2;
    int leaf = stage + 1;
    proj[2 * leaf] = (uint8_t)(1u << (2 * leaf));
    proj[2 * leaf + 1] = (uint8_t)(1u << (2 * leaf + 1));
}

static int same(const uint8_t a[N][N], const uint8_t b[N][N]) { return memcmp(a, b, N * N) == 0; }

static void heap_perms(uint8_t perms[NPERM][6]) {
    int a[6] = {0, 1, 2, 3, 4, 5}, c[6] = {0}, n = 0;
    for (int k = 0; k < 6; k++) perms[n][k] = (uint8_t)a[k];
    n++;
    int i = 0;
    while (i < 6) {
        if (c[i] < i) {
            int j = (i & 1) ? c[i] : 0;
            int tmp = a[j];
            a[j] = a[i];
            a[i] = tmp;
            for (int k = 0; k < 6; k++) perms[n][k] = (uint8_t)a[k];
            n++;
            c[i]++;
            i = 0;
        } else {
            c[i++] = 0;
        }
    }
    if (n != NPERM) {
        fprintf(stderr, "FAIL perm %d\n", n);
        exit(1);
    }
}

static int rank8(const uint8_t rows[N]) {
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

static int mat_inv(uint8_t out[N][N], const uint8_t in[N][N]) {
    uint8_t w[N][2 * N];
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) w[i][j] = in[i][j];
        for (int j = 0; j < N; j++) w[i][N + j] = (uint8_t)(i == j);
    }
    for (int col = 0; col < N; col++) {
        int pivot = -1;
        for (int i = col; i < N; i++)
            if (w[i][col]) {
                pivot = i;
                break;
            }
        if (pivot < 0) return 0;
        if (pivot != col)
            for (int j = 0; j < 2 * N; j++) {
                uint8_t tmp = w[col][j];
                w[col][j] = w[pivot][j];
                w[pivot][j] = tmp;
            }
        if (w[col][col] != 1) {
            uint8_t result = 1, base = w[col][col];
            int exp = 254;
            while (exp) {
                if (exp & 1) result = MUL[result][base];
                base = MUL[base][base];
                exp >>= 1;
            }
            for (int j = 0; j < 2 * N; j++) w[col][j] = MUL[result][w[col][j]];
        }
        for (int i = 0; i < N; i++) {
            if (i == col || !w[i][col]) continue;
            uint8_t factor = w[i][col];
            for (int j = 0; j < 2 * N; j++) w[i][j] ^= MUL[factor][w[col][j]];
        }
    }
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) out[i][j] = w[i][N + j];
    return 1;
}

typedef struct {
    uint64_t pivot_row[64];
    int pivot_rhs[64];
    int pivot_bit[64];
    int used[64];
    int np;
    int bad;
} Sys;

static void sys_clear(Sys *sys) { memset(sys, 0, sizeof *sys); }

/* High 7 bits of A*Z*B + C must vanish. Unknowns are the 64 bits of Z. */
static void sys_add(Sys *sys, const uint8_t A[N][N], const uint8_t B[N][N], const uint8_t C[N][N]) {
    if (sys->bad) return;
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            uint8_t coeff[64];
            for (int a = 0; a < N; a++) {
                uint8_t La = A[i][a];
                for (int b = 0; b < N; b++) coeff[a * N + b] = La ? MUL[La][B[b][j]] : 0;
            }
            for (int bit = 1; bit <= 7; bit++) {
                uint64_t row = 0;
                int rhs = (C[i][j] >> bit) & 1;
                for (int u = 0; u < 64; u++)
                    if ((coeff[u] >> bit) & 1) row |= 1ull << u;
                for (int p = 0; p < sys->np; p++)
                    if ((row >> sys->pivot_bit[p]) & 1ull) {
                        row ^= sys->pivot_row[p];
                        rhs ^= sys->pivot_rhs[p];
                    }
                if (!row) {
                    if (rhs) {
                        sys->bad = 1;
                        return;
                    }
                    continue;
                }
                int bitp = __builtin_ctzll(row);
                for (int p = 0; p < sys->np; p++)
                    if ((sys->pivot_row[p] >> bitp) & 1ull) {
                        sys->pivot_row[p] ^= row;
                        sys->pivot_rhs[p] ^= rhs;
                    }
                sys->pivot_row[sys->np] = row;
                sys->pivot_rhs[sys->np] = rhs;
                sys->pivot_bit[sys->np] = bitp;
                sys->used[bitp] = 1;
                sys->np++;
            }
        }
    }
}

static int sys_kernel(const Sys *sys, uint8_t particular[N], uint8_t kernel[][N]) {
    if (sys->bad) return -1;
    memset(particular, 0, N);
    for (int p = 0; p < sys->np; p++)
        if (sys->pivot_rhs[p]) {
            int u = sys->pivot_bit[p];
            particular[u >> 3] |= (uint8_t)(1u << (u & 7));
        }
    int kernel_n = 0;
    for (int u = 0; u < 64; u++) {
        if (sys->used[u]) continue;
        uint8_t *vec = kernel[kernel_n];
        memset(vec, 0, N);
        vec[u >> 3] |= (uint8_t)(1u << (u & 7));
        for (int p = 0; p < sys->np; p++)
            if ((sys->pivot_row[p] >> u) & 1ull) {
                int v = sys->pivot_bit[p];
                vec[v >> 3] |= (uint8_t)(1u << (v & 7));
            }
        kernel_n++;
    }
    return kernel_n;
}

static void z1_rows(uint8_t out[N], const uint8_t A[N][N], const uint8_t B[N][N], const uint8_t C[N][N],
                   const uint8_t rows[N]) {
    uint8_t acc[N][N];
    memset(acc, 0, sizeof acc);
    for (int a = 0; a < N; a++) {
        uint8_t ra = rows[a];
        if (!ra) continue;
        for (int b = 0; b < N; b++) {
            if ((ra & (1u << b)) == 0) continue;
            for (int i = 0; i < N; i++) {
                uint8_t Ai = A[i][a];
                if (!Ai) continue;
                for (int j = 0; j < N; j++) {
                    uint8_t Bb = B[b][j];
                    if (Bb) acc[i][j] ^= MUL[Ai][Bb];
                }
            }
        }
    }
    for (int i = 0; i < N; i++) {
        uint8_t bits = 0;
        for (int j = 0; j < N; j++) bits |= (uint8_t)(((C ? C[i][j] : 0) ^ acc[i][j]) & 1u) << j;
        /* C is always non-null; the ternary keeps the signature obvious. */
        (void)C;
        out[i] = 0;
        for (int j = 0; j < N; j++)
            if (((C[i][j] ^ acc[i][j]) & 1u)) out[i] |= (uint8_t)(1u << j);
        (void)bits;
    }
}

static int constant_row_rank(const uint8_t part[N], uint8_t ker[][N], int kn) {
    uint8_t m[N];
    memset(m, 0, N);
    int n = 0;
    for (int i = 0; i < N; i++) {
        int varies = 0;
        for (int t = 0; t < kn; t++)
            if (ker[t][i]) {
                varies = 1;
                break;
            }
        if (!varies) m[n++] = part[i];
    }
    return rank8(m);
}

typedef struct {
    int var[8];
    int nvar;
    uint8_t row2;
    uint8_t row1;
} Comp;

static volatile int found_low = 0;

typedef struct {
    uint8_t vec[8];
    uint8_t piv[8];
    int dim;
} Basis;

static void basis_clear(Basis *basis) { memset(basis, 0, sizeof *basis); }

static void basis_insert(Basis *basis, uint8_t row) {
    for (int i = 0; i < basis->dim; i++)
        if (row & (uint8_t)(1u << basis->piv[i])) row ^= basis->vec[i];
    if (!row) return;
    int pivot = __builtin_ctz((unsigned)row);
    uint8_t bit = (uint8_t)(1u << pivot);
    for (int i = 0; i < basis->dim; i++)
        if (basis->vec[i] & bit) basis->vec[i] ^= row;
    basis->vec[basis->dim] = row;
    basis->piv[basis->dim] = (uint8_t)pivot;
    basis->dim++;
}

static void basis_insert_rows(Basis *basis, const uint8_t rows[N], uint8_t which) {
    for (int i = 0; i < N; i++)
        if (which & (uint8_t)(1u << i)) basis_insert(basis, rows[i]);
}

static void apply_mask(uint8_t y2[N], uint8_t y1[N], const uint8_t z2[N], const uint8_t z1[N],
                       const uint8_t z2pat[][N], const uint8_t z1pat[][N], const Comp *comp, int mask) {
    memcpy(y2, z2, N);
    memcpy(y1, z1, N);
    int bits = mask;
    while (bits) {
        int b = __builtin_ctz(bits);
        int v = comp->var[b];
        for (int i = 0; i < N; i++) {
            y2[i] ^= z2pat[v][i];
            y1[i] ^= z1pat[v][i];
        }
        bits ^= 1 << b;
    }
}

static int eval_mask(const Comp *comp, const uint8_t z2[N], const uint8_t z1[N], const uint8_t z2pat[][N],
                     const uint8_t z1pat[][N], Basis b2, Basis b1, int mask) {
    uint8_t y2[N], y1[N];
    apply_mask(y2, y1, z2, z1, z2pat, z1pat, comp, mask);
    basis_insert_rows(&b2, y2, comp->row2);
    basis_insert_rows(&b1, y1, comp->row1);
    return b2.dim + b1.dim;
}

static void search_rec(const Comp *comp, int ncomp, int ci, const uint8_t z2pat[][N], const uint8_t z1pat[][N],
                       const uint8_t z2[N], const uint8_t z1[N], Basis b2, Basis b1, int *best, uint64_t *nodes) {
    if (b2.dim + b1.dim >= *best) return;
    if (ci == ncomp) {
        (*nodes)++;
        *best = b2.dim + b1.dim;
        return;
    }
    /* The last component is a flat loop: its children are leaves. */
    if (ci + 1 == ncomp) {
        int limit = 1 << comp[ci].nvar;
        (*nodes) += (uint64_t)limit;
        for (int mask = 0; mask < limit; mask++) {
            int total = eval_mask(&comp[ci], z2, z1, z2pat, z1pat, b2, b1, mask);
            if (total < *best) *best = total;
            if (*best <= 7) return;
        }
        return;
    }
    int limit = 1 << comp[ci].nvar;
    (*nodes) += (uint64_t)limit;
    for (int mask = 0; mask < limit; mask++) {
        uint8_t y2[N], y1[N];
        apply_mask(y2, y1, z2, z1, z2pat, z1pat, &comp[ci], mask);
        Basis n2 = b2, n1 = b1;
        basis_insert_rows(&n2, y2, comp[ci].row2);
        basis_insert_rows(&n1, y1, comp[ci].row1);
        if (n2.dim + n1.dim >= *best) continue;
        search_rec(comp, ncomp, ci + 1, z2pat, z1pat, y2, y1, n2, n1, best, nodes);
        if (*best <= 7) return;
    }
}

static int brute_min_rank(const uint8_t z2part[N], const uint8_t z1part[N], const uint8_t z2pat[][N],
                         const uint8_t z1pat[][N], int kn) {
    if (kn > 16) return -1;
    int best = 99;
    uint32_t limit = 1u << kn;
    for (uint32_t mask = 0; mask < limit; mask++) {
        uint8_t z2[N], z1[N];
        memcpy(z2, z2part, N);
        memcpy(z1, z1part, N);
        uint32_t bits = mask;
        while (bits) {
            int b = __builtin_ctz(bits);
            for (int i = 0; i < N; i++) {
                z2[i] ^= z2pat[b][i];
                z1[i] ^= z1pat[b][i];
            }
            bits ^= 1u << b;
        }
        int total = rank8(z2) + rank8(z1);
        if (total < best) best = total;
    }
    return best;
}

/* Minimum of rank(Z2)+rank(Z1) over the affine space. Stops at 7. */
static int min_rank_components(const uint8_t z2part[N], const uint8_t z1part[N], const uint8_t z2pat[][N],
                               const uint8_t z1pat[][N], int kn, uint64_t *nodes) {
    int parent[64];
    for (int t = 0; t < kn; t++) parent[t] = t;
    for (int pass = 0; pass < 2; pass++) {
        const uint8_t (*src)[N] = pass ? z1pat : z2pat;
        for (int i = 0; i < N; i++) {
            int root = -1;
            for (int t = 0; t < kn; t++) {
                if (!src[t][i]) continue;
                int b = t;
                while (parent[b] != b) b = parent[b];
                if (root < 0) root = b;
                else {
                    int a = root;
                    while (parent[a] != a) a = parent[a];
                    parent[b] = a;
                    root = a;
                }
            }
        }
    }
    int root_of[64], ncomp = 0, comp_id[64];
    memset(comp_id, -1, sizeof comp_id);
    for (int t = 0; t < kn; t++) {
        int a = t;
        while (parent[a] != a) a = parent[a];
        root_of[t] = a;
        if (comp_id[a] < 0) comp_id[a] = ncomp++;
    }
    Comp comp[64];
    memset(comp, 0, sizeof comp);
    for (int t = 0; t < kn; t++) {
        Comp *c = &comp[comp_id[root_of[t]]];
        if (c->nvar >= 8) return -3;
        c->var[c->nvar++] = t;
    }
    for (int pass = 0; pass < 2; pass++) {
        const uint8_t (*src)[N] = pass ? z1pat : z2pat;
        for (int i = 0; i < N; i++) {
            int owner = -1;
            for (int t = 0; t < kn; t++)
                if (src[t][i]) {
                    int id = comp_id[root_of[t]];
                    if (owner < 0) owner = id;
                    else if (owner != id) return -4;
                }
            if (owner >= 0) {
                if (pass) comp[owner].row1 |= (uint8_t)(1u << i);
                else comp[owner].row2 |= (uint8_t)(1u << i);
            }
        }
    }
    /* Rows touched by nobody are constant and fixed from the start. */
    uint8_t fixed2 = 0, fixed1 = 0;
    for (int i = 0; i < N; i++) {
        int hit2 = 0, hit1 = 0;
        for (int t = 0; t < kn; t++) {
            hit2 |= z2pat[t][i] != 0;
            hit1 |= z1pat[t][i] != 0;
        }
        if (!hit2) fixed2 |= (uint8_t)(1u << i);
        if (!hit1) fixed1 |= (uint8_t)(1u << i);
    }
    for (int i = 1; i < ncomp; i++) {
        Comp key = comp[i];
        int keyn = __builtin_popcount((unsigned)key.row1) + __builtin_popcount((unsigned)key.row2);
        int j = i - 1;
        while (j >= 0) {
            int jn = __builtin_popcount((unsigned)comp[j].row1) + __builtin_popcount((unsigned)comp[j].row2);
            if (jn >= keyn) break;
            comp[j + 1] = comp[j];
            j--;
        }
        comp[j + 1] = key;
    }
    Basis b2, b1;
    basis_clear(&b2);
    basis_clear(&b1);
    basis_insert_rows(&b2, z2part, fixed2);
    basis_insert_rows(&b1, z1part, fixed1);
    int best = 8;
    search_rec(comp, ncomp, 0, z2pat, z1pat, z2part, z1part, b2, b1, &best, nodes);
    return best;
}

static void die(const char *msg) {
    fprintf(stderr, "FAIL: %s\n", msg);
    exit(1);
}

int main(int argc, char **argv) {
    int slice_only = argc > 1 && strcmp(argv[1], "slice") == 0;
    int hist_only = argc > 1 && strcmp(argv[1], "hist") == 0;
    int triple_c0 = -1, triple_c1 = -1, triple_c2 = -1;
    int c0_lo = 0, c0_hi = 11;
    if (argc > 1 && strcmp(argv[1], "triple") == 0) {
        triple_c0 = atoi(argv[2]);
        triple_c1 = atoi(argv[3]);
        triple_c2 = atoi(argv[4]);
        c0_lo = c0_hi = triple_c0;
    } else if (argc > 1 && strcmp(argv[1], "range") == 0) {
        c0_lo = atoi(argv[2]);
        c0_hi = atoi(argv[3]);
    } else if (slice_only) {
        c0_hi = 0;
    }
    if (c0_lo < 0 || c0_hi > 11 || c0_lo > c0_hi) die("c0 range");
    init_mul();
    ResBits bits[12];
    int nres = build_resolutions(bits);
    if (nres != 12) die("resolution count");
    int diagonal = -1;
    for (int i = 0; i < 12; i++)
        if (bits[i].b == 0) {
            diagonal = i;
            break;
        }
    if (diagonal < 0) die("diagonal resolution");

    uint8_t perms[NPERM][6];
    heap_perms(perms);
    const uint8_t pts[2][3] = {{2, 3, 5}, {6, 7, 11}};
    const uint8_t *pt = pts[0];

    Call bank[12][6];
    for (int r = 0; r < 12; r++)
        for (int stage = 0; stage < G; stage++)
            for (int half = 0; half < 2; half++) make_call(&bank[r][stage * 2 + half], &bits[r], stage, half);

    uint8_t target[N][N];
    eye(target);
    for (int stage = 0; stage < G; stage++) {
        uint8_t eproj[N], egate[N][N], prod[N][N];
        support_e(eproj, stage);
        gate_of(egate, eproj, (uint8_t)(pt[stage] ^ 1));
        matmul(prod, egate, target);
        memcpy(target, prod, sizeof prod);
    }

    /* Control word: diagonal resolution, grouped halves, thins after stages 0 and 2. */
    {
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
        if (rank8(thin0) != 4 || rank8(thin1) != 4) die("control thin ranks");
        uint8_t right[N][N], gate[N][N], prod[N][N];
        eye(right);
        for (int stage = 0; stage < G; stage++) {
            for (int half = 0; half < 2; half++) {
                gate_of(gate, bank[diagonal][stage * 2 + half].proj, (uint8_t)(pt[stage] ^ 1));
                matmul(prod, gate, right);
                memcpy(right, prod, sizeof prod);
            }
        }
        if (!same(right, target)) die("control pure");
    }

    uint8_t target1[N][N];
    eye(target1);
    for (int stage = 0; stage < G; stage++) {
        uint8_t eproj[N], egate[N][N], prod[N][N];
        support_e(eproj, stage);
        gate_of(egate, eproj, (uint8_t)(pts[1][stage] ^ 1));
        matmul(prod, egate, target1);
        memcpy(target1, prod, sizeof prod);
    }

    uint64_t screened = 0, pure_hits = 0, both_hits = 0, slice = 0, consistent = 0;
    uint64_t hist[65], floor_hist[17];
    memset(hist, 0, sizeof hist);
    memset(floor_hist, 0, sizeof floor_hist);
    int global_min = 99, min_floor = 99, min_floor_high = 99, max_row_vars = 0, max_row_vars_z1 = 0,
        max_component = 0, max_joint = 0;
    uint64_t high_weak = 0, joint_hist[33];
    memset(joint_hist, 0, sizeof joint_hist);
    uint64_t one_agree = 0;
#pragma omp parallel for schedule(dynamic) reduction(+ : screened, pure_hits, both_hits, slice, consistent, one_agree) if (!slice_only && !hist_only && triple_c0 < 0)
    for (int c0 = c0_lo; c0 <= c0_hi; c0++) {
        uint8_t choice_proj[6][N], choice_read[6][N];
        int choice_stage[6];
        uint8_t gates[2][6][N][N];
        uint64_t nodes = 0;
        for (int c1 = 0; c1 < 12; c1++) {
            if (triple_c1 >= 0 && c1 != triple_c1) continue;
            if (found_low) continue;
            for (int c2 = 0; c2 < 12; c2++) {
                if (slice_only && (c1 || c2)) continue;
                if (triple_c2 >= 0 && c2 != triple_c2) continue;
                const int choice[3] = {c0, c1, c2};
                for (int stage = 0; stage < 3; stage++) {
                    for (int half = 0; half < 2; half++) {
                        int id = stage * 2 + half;
                        memcpy(choice_proj[id], bank[choice[stage]][id].proj, N);
                        memcpy(choice_read[id], bank[choice[stage]][id].readm, N);
                        choice_stage[id] = stage;
                        for (int point = 0; point < 2; point++)
                            gate_of(gates[point][id], choice_proj[id], (uint8_t)(pts[point][stage] ^ 1));
                    }
                }
                for (int p = 0; p < NPERM; p++) {
                    screened++;
                    uint8_t rightm[2][7][N][N], leftm[2][7][N][N], prod[N][N], need[2][N][N];
                    int pure_ok = 1;
                    for (int point = 0; point < 2; point++) {
                        eye(rightm[point][0]);
                        for (int k = 0; k < 6; k++) {
                            matmul(prod, gates[point][perms[p][k]], rightm[point][k]);
                            memcpy(rightm[point][k + 1], prod, sizeof prod);
                        }
                        const uint8_t (*want)[N] = point ? target1 : target;
                        if (!same(rightm[point][6], want)) {
                            pure_ok = 0;
                            break;
                        }
                    }
                    if (!pure_ok) {
                        /* Still count the published one-point pure hits. */
                        if (same(rightm[0][6], target)) pure_hits++;
                        continue;
                    }
                    pure_hits++;
                    both_hits++;
                    if (c0 == 0 && c1 == 0 && c2 == 0) slice++;
                    for (int point = 0; point < 2; point++) {
                        eye(leftm[point][6]);
                        for (int k = 5; k >= 0; k--) {
                            matmul(prod, leftm[point][k + 1], gates[point][perms[p][k]]);
                            memcpy(leftm[point][k], prod, sizeof prod);
                        }
                        memset(need[point], 0, sizeof need[point]);
                        for (int k = 0; k < 6; k++) {
                            int id = perms[p][k];
                            uint8_t Q[N][N], RQ[N][N], LRQ[N][N];
                            memset(Q, 0, sizeof Q);
                            uint8_t scale = pts[point][choice_stage[id]];
                            for (int i = 0; i < N; i++)
                                for (int j = 0; j < N; j++)
                                    if (choice_read[id][i] & (1u << j)) Q[i][j] = scale;
                            matmul(RQ, Q, rightm[point][k]);
                            matmul(LRQ, leftm[point][k + 1], RQ);
                            for (int i = 0; i < N; i++)
                                for (int j = 0; j < N; j++) need[point][i][j] ^= LRQ[i][j];
                        }
                        const uint8_t (*want)[N] = point ? target1 : target;
                        for (int i = 0; i < N; i++)
                            for (int j = 0; j < N; j++) need[point][i][j] ^= want[i][j];
                    }
                    uint8_t invL[2][7][N][N], invR[2][7][N][N];
                    for (int point = 0; point < 2; point++)
                        for (int g = 0; g <= 6; g++)
                            if (!mat_inv(invL[point][g], leftm[point][g]) || !mat_inv(invR[point][g], rightm[point][g]))
                                die("singular prefix");
                    for (int g = 0; g <= 6; g++) {
                        uint8_t zone[2][N][N], tmp[N][N];
                        for (int point = 0; point < 2; point++) {
                            matmul(tmp, invL[point][g], need[point]);
                            matmul(zone[point], tmp, invR[point][g]);
                        }
                        int agree = 1;
                        for (int i = 0; i < N && agree; i++)
                            for (int j = 0; j < N; j++)
                                if (zone[0][i][j] > 1 || zone[0][i][j] != zone[1][i][j]) {
                                    agree = 0;
                                    break;
                                }
                        if (agree) {
                            one_agree++;
                            printf("ONE_WITNESS choice=%d,%d,%d perm=%d gap=%d\n", c0, c1, c2, p, g);
                            found_low = 1;
                        }
                    }
                    if (found_low) continue;
                    for (int g0 = 0; g0 <= 6; g0++) {
                        for (int g1 = g0 + 1; g1 <= 6; g1++) {
                            Sys sys;
                            sys_clear(&sys);
                            uint8_t A[2][N][N], B[2][N][N], C[2][N][N], tmp[N][N];
                            for (int point = 0; point < 2; point++) {
                                matmul(A[point], invL[point][g0], leftm[point][g1]);
                                matmul(B[point], rightm[point][g1], invR[point][g0]);
                                matmul(tmp, invL[point][g0], need[point]);
                                matmul(C[point], tmp, invR[point][g0]);
                                sys_add(&sys, A[point], B[point], C[point]);
                                if (sys.bad) break;
                            }
                            if (sys.bad) continue;
                            uint8_t particular[N], kernel[64][N];
                            int kernel_n = sys_kernel(&sys, particular, kernel);
                            if (kernel_n < 0) continue;
                            consistent++;
#pragma omp atomic
                            hist[kernel_n]++;
                            if (!hist_only && !slice_only && kernel_n <= 12) {
                                /* Kept below as the independent brute-force check. */
                            }
                            if (hist_only) {
                                uint8_t z1part[N], z1k[64][N], zeroC[N][N];
                                memset(zeroC, 0, sizeof zeroC);
                                z1_rows(z1part, A[0], B[0], C[0], particular);
                                for (int t = 0; t < kernel_n; t++)
                                    z1_rows(z1k[t], A[0], B[0], zeroC, kernel[t]);
                                int floor_sum = constant_row_rank(particular, kernel, kernel_n) +
                                                constant_row_rank(z1part, z1k, kernel_n);
                                if (floor_sum < min_floor) min_floor = floor_sum;
                                if (floor_sum <= 16) floor_hist[floor_sum]++;
                                int maxrv = 0;
                                for (int i = 0; i < N; i++) {
                                    int c = 0;
                                    for (int t = 0; t < kernel_n; t++)
                                        if (kernel[t][i]) c++;
                                    if (c > maxrv) maxrv = c;
                                }
                                if (maxrv > max_row_vars) max_row_vars = maxrv;
                                int maxrv1 = 0;
                                for (int i = 0; i < N; i++) {
                                    int c = 0;
                                    for (int t = 0; t < kernel_n; t++)
                                        if (z1k[t][i]) c++;
                                    if (c > maxrv1) maxrv1 = c;
                                }
                                if (maxrv1 > max_row_vars_z1) max_row_vars_z1 = maxrv1;
                                int parent[64];
                                for (int t = 0; t < kernel_n; t++) parent[t] = t;
                                for (int i = 0; i < N; i++) {
                                    int first = -1;
                                    for (int t = 0; t < kernel_n; t++)
                                        if (kernel[t][i]) {
                                            if (first < 0) first = t;
                                            else {
                                                int a = first, b = t;
                                                while (parent[a] != a) a = parent[a];
                                                while (parent[b] != b) b = parent[b];
                                                parent[b] = a;
                                            }
                                        }
                                }
                                int comp[64] = {0};
                                int big = 0;
                                for (int t = 0; t < kernel_n; t++) {
                                    int a = t;
                                    while (parent[a] != a) a = parent[a];
                                    if (++comp[a] > big) big = comp[a];
                                }
                                if (big > max_component) max_component = big;
                                int jparent[64];
                                for (int t = 0; t < kernel_n; t++) jparent[t] = t;
                                for (int pass = 0; pass < 2; pass++) {
                                    uint8_t (*src)[N] = pass ? z1k : kernel;
                                    for (int i = 0; i < N; i++) {
                                        int first = -1;
                                        for (int t = 0; t < kernel_n; t++)
                                            if (src[t][i]) {
                                                int b = t;
                                                while (jparent[b] != b) b = jparent[b];
                                                if (first < 0) first = b;
                                                else {
                                                    int a = first;
                                                    while (jparent[a] != a) a = jparent[a];
                                                    jparent[b] = a;
                                                    first = a;
                                                }
                                            }
                                    }
                                }
                                int jcomp[64] = {0};
                                int jbig = 0;
                                for (int t = 0; t < kernel_n; t++) {
                                    int a = t;
                                    while (jparent[a] != a) a = jparent[a];
                                    if (++jcomp[a] > jbig) jbig = jcomp[a];
                                }
                                if (jbig > max_joint) max_joint = jbig;
                                if (jbig <= 32) joint_hist[jbig]++;
                                if (kernel_n >= 16) {
                                    if (floor_sum < min_floor_high) min_floor_high = floor_sum;
                                    if (floor_sum < 8) high_weak++;
                                }
                                continue;
                            }
                            uint8_t z1part[N], z1k[64][N], zeroC[N][N];
                            memset(zeroC, 0, sizeof zeroC);
                            z1_rows(z1part, A[0], B[0], C[0], particular);
                            for (int t = 0; t < kernel_n; t++) z1_rows(z1k[t], A[0], B[0], zeroC, kernel[t]);
                            int local = min_rank_components(particular, z1part, kernel, z1k, kernel_n, &nodes);
                            if (local < 0) die("component split");
                            if (slice_only && kernel_n <= 16) {
                                int brute = brute_min_rank(particular, z1part, kernel, z1k, kernel_n);
                                int capped = brute < 8 ? brute : 8;
                                if (capped != local) {
                                    fprintf(stderr, "mismatch brute=%d local=%d gaps=%d,%d kn=%d\n", brute, local, g0,
                                            g1, kernel_n);
                                    die("brute mismatch");
                                }
                                if (slice_only && c0 == 0 && p == 0 && g0 == 2 && g1 == 6)
                                    fprintf(stderr, "control brute_min=%d\n", brute);
                            }
                            if (local < global_min) {
#pragma omp critical
                                if (local < global_min) global_min = local;
                            }
                            if (local <= 7) {
                                printf("WITNESS rank_sum=%d choice=%d,%d,%d perm=%d gaps=%d,%d nullity=%d\n", local,
                                       c0, c1, c2, p, g0, g1, kernel_n);
                                found_low = 1;
                            }
                        }
                    }
                }
            }
        }
        fprintf(stderr, "c0=%d done min=%d nodes=%llu\n", c0, global_min, (unsigned long long)nodes);
        fflush(stderr);
        fprintf(stderr, "  z1_row_vars=%d z2_component=%d joint=%d\n", max_row_vars_z1, max_component, max_joint);
    }
    if (found_low) return 2;
    printf("screened=%llu pure_hits=%llu both_hits=%llu slice000=%llu consistent=%llu min_rank_sum=%d diagonal=%d one_agree=%llu\n",
           (unsigned long long)screened, (unsigned long long)pure_hits, (unsigned long long)both_hits,
           (unsigned long long)slice, (unsigned long long)consistent, global_min, diagonal,
           (unsigned long long)one_agree);
    for (int i = 0; i <= 64; i++)
        if (hist[i]) printf("nullity_%d=%llu\n", i, (unsigned long long)hist[i]);
    printf("min_floor=%d min_floor_high=%d max_row_vars=%d max_row_vars_z1=%d max_component=%d max_joint=%d high_weak=%llu\n",
           min_floor, min_floor_high, max_row_vars, max_row_vars_z1, max_component, max_joint,
           (unsigned long long)high_weak);
    for (int i = 0; i <= 16; i++)
        if (floor_hist[i]) printf("floor_%d=%llu\n", i, (unsigned long long)floor_hist[i]);
    for (int i = 0; i <= 32; i++)
        if (joint_hist[i]) printf("joint_%d=%llu\n", i, (unsigned long long)joint_hist[i]);
    if (triple_c0 >= 0 || slice_only || hist_only) return found_low ? 2 : 0;
    if (one_agree != 0) die("one thin agreement");
    if (global_min != 8) die("rank sum below 8");
    uint64_t expect_screened = (uint64_t)(c0_hi - c0_lo + 1) * 103680ull;
    if (screened != expect_screened) die("screened count");
    return 0;
}
