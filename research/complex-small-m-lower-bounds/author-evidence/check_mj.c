/* 23 Oct 2026.  INDEPENDENT CHECKER of a nonsingular-minor certificate for the hook demand of a partial product of
 * letters g_L = prod over b in L of dir(e_b) (shares no code with gen_mj.c; different determinant routine, no subset
 * tables, no sorting signs; it extends check_m0.c, which is the case L = all bits).
 * Definitions: n = 2^m; Q_L[u][v] = (-i)^{popcount(u xor v)} if u xor v lies inside L, else 0, with i -> I
 *   (I^2 = -1 mod p); g_L = ((1+i)/2)^|L| Q_L.  For a row set U = {u_1 < ... < u_k} (0 not in U) and a column set
 *   T = {t_1 < ... < t_k} (0 in T):
 *   M_alpha[U][T] = sum over s in F_2^m of (-1)^{alpha.s} * Q_L[0][s] * det( Q_L[u_a][t_b xor s] )_{a,b=1..k}.
 *   The hook N = span{e_x (x) e_T : x in T} is a coordinate subspace of V (x) Lambda^k V; the shifts X^s act freely
 *   on its basis and on the complementary basis (rows (0,U), columns (0,T) are orbit representatives) and commute
 *   with g_L, so the demand f(g_L) = rank (1 - P_N) G P_N, G = g_L (x) Lambda^k g_L, is the sum over the 2^m
 *   characters alpha of rank M_alpha.
 * The certificate file lists m, k, lab (the mask of L), alpha, p, I, and `size` pairs (row mask, col mask).  The
 * checker verifies: p is prime, I^2 = -1 mod p, the row masks are distinct k-subsets of {1..n-1}, the col masks
 * distinct k-subsets containing 0; then, for alpha from the header (or for each ALPHA given on the command line,
 * the same rows and columns), builds the size x size matrix from the formula above and computes its determinant
 * mod p.  Nonzero determinant mod p  =>  the minor of M_alpha over Z[i] is nonzero  =>  rank M_alpha over
 * Q(i) >= size.  With every alpha in 0..n-1 passing: f(g_L) >= n * size, with no further lemma.
 * Build: cc -O2 -o check_mj check_mj.c          Run: ./check_mj CERTFILE [ALPHA ...]
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
typedef uint64_t u64;
static u64 p;
static u64 mulm(u64 a, u64 b) { return a * b % p; }   /* exact: p < 2^31 is checked, so a*b < 2^62 */
static u64 powm(u64 b, u64 e) { u64 r = 1; b %= p; while (e) { if (e & 1) r = mulm(r, b); b = mulm(b, b); e >>= 1; } return r; }
static int bits(unsigned x) { int c = 0; while (x) { c += x & 1; x >>= 1; } return c; }
/* determinant mod p of an N x N matrix (row-major, destroyed), Gaussian elimination with row swaps */
static u64 detm(u64 *A, int N) {
    u64 det = 1;
    for (int c = 0; c < N; c++) {
        int piv = -1;
        for (int r = c; r < N; r++) if (A[(size_t)r * N + c] % p) { piv = r; break; }
        if (piv < 0) return 0;
        if (piv != c) {
            for (int j = 0; j < N; j++) { u64 t = A[(size_t)c * N + j]; A[(size_t)c * N + j] = A[(size_t)piv * N + j]; A[(size_t)piv * N + j] = t; }
            det = (p - det) % p;
        }
        u64 a = A[(size_t)c * N + c]; det = mulm(det, a);
        u64 ia = powm(a, p - 2);
        for (int r = c + 1; r < N; r++) {
            u64 b = A[(size_t)r * N + c]; if (!b) continue;
            u64 f = mulm(b, ia);
            u64 *rr = A + (size_t)r * N, *rc = A + (size_t)c * N;
            for (int j = c; j < N; j++) rr[j] = (rr[j] + p - mulm(f, rc[j])) % p;
        }
    }
    return det;
}
int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: check_mj CERT [ALPHA ...]\n"); return 2; }
    FILE *fi = fopen(argv[1], "r"); if (!fi) { perror("cert"); return 2; }
    int m, k, size; unsigned lab, alpha0; unsigned long long pp, II;
    if (fscanf(fi, "m %d k %d lab %u alpha %u p %llu I %llu size %d", &m, &k, &lab, &alpha0, &pp, &II, &size) != 7) { fprintf(stderr, "bad header\n"); return 2; }
    p = pp; u64 I = II; int n = 1 << m;
    int prime = p > 2 && p < (1ULL << 31);
    for (u64 d = 2; d * d <= p && prime; d++) if (p % d == 0) prime = 0;
    int okI = mulm(I, I) == p - 1;
    int okL = m >= 1 && m <= 4 && lab != 0 && !(lab >> m) && k >= 1 && k < n;
    unsigned *R = malloc(sizeof(unsigned) * size), *C = malloc(sizeof(unsigned) * size);
    for (int i = 0; i < size; i++) if (fscanf(fi, "%u %u", &R[i], &C[i]) != 2) { fprintf(stderr, "short cert\n"); return 2; }
    fclose(fi);
    char *seenR = calloc((size_t)1 << n, 1), *seenC = calloc((size_t)1 << n, 1); int okS = okL;
    for (int i = 0; i < size && okS; i++) {
        if (R[i] >> n || C[i] >> n || bits(R[i]) != k || bits(C[i]) != k || (R[i] & 1) || !(C[i] & 1) || seenR[R[i]] || seenC[C[i]]) okS = 0;
        else { seenR[R[i]] = 1; seenC[C[i]] = 1; }
    }
    printf("cert: m=%d k=%d lab=%u p=%llu (prime: %s) I^2=-1: %s, %d distinct well-formed rows/cols: %s\n",
           m, k, lab, pp, prime ? "yes" : "NO", okI ? "yes" : "NO", size, okS ? "yes" : "NO");
    if (!(prime && okI && okS)) { printf("RESULT: FAIL (format)\n"); return 1; }
    int na = argc > 2 ? argc - 2 : 1;
    unsigned *alphas = malloc(sizeof(unsigned) * na);
    for (int a = 0; a < na; a++) {
        alphas[a] = argc > 2 ? (unsigned)strtoul(argv[2 + a], NULL, 10) : alpha0;
        if (alphas[a] >> m) { printf("RESULT: FAIL (alpha %u out of range)\n", alphas[a]); return 1; }
    }
    u64 mi[4] = {1, p - I, p - 1, I};                 /* (-i)^0, (-i)^1, (-i)^2, (-i)^3 */
    u64 *A = malloc(sizeof(u64) * (size_t)size * size); if (!A) { fprintf(stderr, "alloc\n"); return 1; }
    u64 *B = malloc(sizeof(u64) * k * k);
    int allok = 1;
    for (int ai = 0; ai < na; ai++) {
        unsigned alpha = alphas[ai];
        for (int i = 0; i < size; i++) {
            int u[32], L = 0; for (int x = 0; x < n; x++) if (R[i] >> x & 1) u[L++] = x;
            for (int j = 0; j < size; j++) {
                int t[32], L2 = 0; for (int x = 0; x < n; x++) if (C[j] >> x & 1) t[L2++] = x;
                u64 acc = 0;
                for (int s = 0; s < n; s++) {
                    if ((unsigned)s & ~lab) continue;                     /* Q_L[0][s] = 0 */
                    for (int a = 0; a < k; a++) for (int b = 0; b < k; b++) {
                        unsigned d = (unsigned)(u[a] ^ (t[b] ^ s));
                        B[a * k + b] = (d & ~lab) ? 0 : mi[bits(d) & 3];
                    }
                    u64 dd = detm(B, k);
                    u64 term = mulm(mi[bits((unsigned)s) & 3], dd);
                    if (bits(alpha & (unsigned)s) & 1) term = (p - term) % p;
                    acc = (acc + term) % p;
                }
                A[(size_t)i * size + j] = acc;
            }
            if (i % 500 == 0) { fprintf(stderr, "  alpha %u: built row %d / %d\n", alpha, i, size); }
        }
        u64 d = detm(A, size);
        printf("det mod p of the %d x %d minor of M_%u (lab %u) = %llu\n", size, size, alpha, lab, (unsigned long long)d);
        printf("ALPHA %u: %s  -> rank M_%u over Q(i) >= %d%s\n", alpha, d ? "PASS" : "FAIL", alpha, d ? size : 0, d ? "" : " (not certified)");
        fflush(stdout);
        if (!d) allok = 0;
    }
    printf("RESULT: %s  (%d alpha value%s checked, %d x %d each)\n", allok ? "PASS" : "FAIL", na, na == 1 ? "" : "s", size, size);
    return allok ? 0 : 1;
}
