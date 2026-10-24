/* Exact meet-in-the-middle search in M_2(F2[GL_4(F2)]): two coordinate
 * 3-cycles on coordinates 0,1,2 with spectator coordinate 3.
 *
 * Paid call D(g,N) = I + ([g]+[e]) N, g one of the 12 coordinate CNOTs of
 * GL_4(F2), N one of the 6 rank-one idempotents u v^T of M_2(F2): 72
 * generators, numbered 6*cnot + projector. States are kept sparsely: each of
 * the four entries is a sorted set of group-element indices (F2 coefficients).
 * A product of at most L calls has at most 2^L terms per entry.
 *
 * Reductions (sound for a shortest word): no adjacent equal letters; adjacent
 * commuting letters only in increasing order; in sym mode the first two
 * backward letters are the lexicographically least pair of their orbit under
 * the symmetries fixing the target and generator set (commutation order then
 * applies from the fourth backward letter on, never across the chosen pair).
 *
 * Usage:
 *   search count <d> [bits]
 *   search dump <g...>
 *   search selftest
 *   search <target> <fwd> <bwd> [sym|nosym] [workers] [bits]
 *     targets: c3c3 c3e s01s01 c3s01
 * A key match is checked exactly: distance <= 5 iff X * B lies in the stored
 * exact radius-two ball for some word B of length <= 3.
 */
#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/wait.h>
#include <unistd.h>

#define NG 20160
#define R 2
#define NP 6
#define NC 12
#define NGEN (NC * NP)
#define CAP 256
typedef struct { uint16_t n; uint16_t e[CAP]; } Set;
typedef struct { Set s[R][R]; } State;

static uint16_t idx_of[65536];
static uint16_t elem[NG];
static uint16_t rmul[NC][NG];
static int gen_u[NP], gen_v[NP];
static uint16_t cn[NC];

static void need(int ok, const char *m) { if (!ok) { fprintf(stderr, "FAIL: %s\n", m); exit(9); } }
static int mat_mul(int a, int b) {  /* rows: 4 bits each, row i at bits 4i */
    int r = 0;
    for (int i = 0; i < 4; i++) {
        int row = 0, ai = (a >> (4 * i)) & 15;
        for (int k = 0; k < 4; k++) if (ai >> k & 1) row ^= (b >> (4 * k)) & 15;
        r |= row << (4 * i);
    }
    return r;
}
static int invertible(int m) {
    int rows[4], r = 0;
    for (int i = 0; i < 4; i++) rows[i] = (m >> (4 * i)) & 15;
    for (int bit = 0; bit < 4; bit++) {
        int p = -1;
        for (int i = r; i < 4; i++) if (rows[i] >> bit & 1) { p = i; break; }
        if (p < 0) continue;
        int t = rows[r]; rows[r] = rows[p]; rows[p] = t;
        for (int i = 0; i < 4; i++) if (i != r && (rows[i] >> bit & 1)) rows[i] ^= rows[r];
        r++;
    }
    return r == 4;
}
static int identity4(void) { return 1 | (2 << 4) | (4 << 8) | (8 << 12); }
static int rowperm(const int *s) { int m = 0; for (int a = 0; a < 4; a++) m |= (1 << s[a]) << (4 * a); return m; }
static int transpose4(int a) { int r = 0; for (int i = 0; i < 4; i++) for (int j = 0; j < 4; j++) if ((a >> (4*i+j)) & 1) r |= 1 << (4*j+i); return r; }
static int inverse4(int a) {   /* Gauss-Jordan on [A | I] */
    int rows[4], inv[4];
    for (int i = 0; i < 4; i++) { rows[i] = (a >> (4 * i)) & 15; inv[i] = 1 << i; }
    for (int c = 0; c < 4; c++) {
        int p = -1;
        for (int i = c; i < 4; i++) if (rows[i] >> c & 1) { p = i; break; }
        if (p < 0) abort();
        int t = rows[c]; rows[c] = rows[p]; rows[p] = t; t = inv[c]; inv[c] = inv[p]; inv[p] = t;
        for (int i = 0; i < 4; i++) if (i != c && (rows[i] >> c & 1)) { rows[i] ^= rows[c]; inv[i] ^= inv[c]; }
    }
    int r = 0; for (int i = 0; i < 4; i++) r |= inv[i] << (4 * i);
    if (mat_mul(a, r) != identity4()) abort();
    return r;
}

/* sparse F2 set operations */
static void sym_into(Set *out, const Set *a, const Set *b) {   /* out = a xor b (sorted) */
    int i = 0, j = 0, n = 0;
    while (i < a->n && j < b->n) {
        if (a->e[i] < b->e[j]) out->e[n++] = a->e[i++];
        else if (a->e[i] > b->e[j]) out->e[n++] = b->e[j++];
        else { i++; j++; }
    }
    while (i < a->n) out->e[n++] = a->e[i++];
    while (j < b->n) out->e[n++] = b->e[j++];
    need(n <= CAP, "set capacity");
    out->n = (uint16_t)n;
}
static int cmp16(const void *a, const void *b) { return (int)*(const uint16_t *)a - (int)*(const uint16_t *)b; }
static void translate(Set *out, const Set *a, int gi) {   /* out = a * [g] */
    out->n = a->n;
    for (int i = 0; i < a->n; i++) out->e[i] = rmul[gi][a->e[i]];
    /* insertion sort (small) */
    for (int i = 1; i < out->n; i++) { uint16_t v = out->e[i]; int j = i - 1; while (j >= 0 && out->e[j] > v) { out->e[j+1] = out->e[j]; j--; } out->e[j+1] = v; }
}
static State apply(const State *x, int gen) {   /* x * D(g, u v^T) */
    int gi = gen / NP, ni = gen % NP, u = gen_u[ni], v = gen_v[ni];
    State r = *x;
    for (int i = 0; i < R; i++) {
        Set z, t, w, tmp;
        z.n = 0;
        for (int k = 0; k < R; k++) if (u >> k & 1) { sym_into(&tmp, &z, &x->s[i][k]); z = tmp; }
        translate(&t, &z, gi);
        sym_into(&w, &t, &z);
        for (int j = 0; j < R; j++) if (v >> j & 1) { sym_into(&tmp, &r.s[i][j], &w); r.s[i][j] = tmp; }
    }
    return r;
}
static int steq(const State *a, const State *b) {
    for (int i = 0; i < R; i++) for (int j = 0; j < R; j++) {
        if (a->s[i][j].n != b->s[i][j].n) return 0;
        if (memcmp(a->s[i][j].e, b->s[i][j].e, 2 * a->s[i][j].n)) return 0;
    }
    return 1;
}
static uint64_t mix(uint64_t z) { z ^= z >> 33; z *= 0xFF51AFD7ED558CCDULL; z ^= z >> 33; z *= 0xC4CEB9FE1A85EC53ULL; z ^= z >> 33; return z; }
static uint64_t fp(const State *x) {
    uint64_t h = 0x9E3779B97F4A7C15ULL;
    for (int i = 0; i < R; i++) for (int j = 0; j < R; j++) {
        const Set *s = &x->s[i][j];
        h = mix(h ^ (0x1000ULL * (uint64_t)(2*i+j+1) + s->n));
        for (int k = 0; k < s->n; k++) h = mix(h + s->e[k] + 0x9E37ULL);
    }
    return h | 8;
}

static uint64_t *table, tmask; static long distinct;
static void alloc_table(int bits) {
    size_t n = (size_t)1 << bits;
    table = mmap(NULL, n * 8, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    need(table != MAP_FAILED, "table allocation"); tmask = n - 1;
}
static void insert(uint64_t h, int d) {
    uint64_t key = h & ~7ULL, i = (h >> 7) & tmask;
    for (;;) { uint64_t t = table[i];
        if (!t) { table[i] = key | (uint64_t)d; distinct++; return; }
        if ((t & ~7ULL) == key) { if ((int)(t & 7) > d) table[i] = key | (uint64_t)d; return; }
        i = (i + 1) & tmask; }
}
static int lookup(uint64_t h) {
    uint64_t key = h & ~7ULL, i = (h >> 7) & tmask;
    for (;;) { uint64_t t = table[i]; if (!t) return -1; if ((t & ~7ULL) == key) return (int)(t & 7); i = (i + 1) & tmask; }
}

static unsigned char comm[NGEN][NGEN];
static int follows(int last, int g) { return last < 0 || (g != last && !(comm[last][g] && last > g)); }
static State identity_state(void) {
    State s; memset(&s, 0, sizeof s);
    for (int i = 0; i < R; i++) { s.s[i][i].n = 1; s.s[i][i].e[0] = idx_of[identity4()]; }
    return s;
}

/* exact radius-two ball for verification */
#define B2N 8192
static State *b2s; static signed char *b2d; static long b2n;
static uint64_t b2h[B2N * 2];   /* open addressing: index into b2s, +1 */
static int b2_find(const State *x) {
    uint64_t i = (fp(x) >> 7) & (B2N * 2 - 1);
    while (b2h[i]) { if (steq(&b2s[b2h[i]-1], x)) return (int)b2h[i]-1; i = (i + 1) & (B2N * 2 - 1); }
    return -1;
}
static void b2_add(const State *x, int d) {
    if (b2_find(x) >= 0) return;
    need(b2n < B2N, "ball2 capacity");
    uint64_t i = (fp(x) >> 7) & (B2N * 2 - 1);
    while (b2h[i]) i = (i + 1) & (B2N * 2 - 1);
    b2s[b2n] = *x; b2d[b2n] = (signed char)d; b2h[i] = (uint64_t)(++b2n);
}
static void build_b2(void) {
    b2s = malloc(sizeof(State) * B2N); b2d = malloc(B2N); need(b2s && b2d, "ball2 memory");
    State I = identity_state(); b2_add(&I, 0);
    State one[NGEN];
    for (int a = 0; a < NGEN; a++) { one[a] = apply(&I, a); b2_add(&one[a], 1); }
    for (int a = 0; a < NGEN; a++) for (int b = 0; b < NGEN; b++) { State y = apply(&one[a], b); b2_add(&y, 2); }
}
static int verify_exact(const State *x, int maxd) {   /* exact distance when <= maxd <= 5 */
    need(maxd <= 5, "exact verification covers distance <= 5");
    int best = 99, k = b2_find(x);
    if (k >= 0) best = b2d[k];
    for (int a = 0; a < NGEN; a++) {
        State y = apply(x, a); k = b2_find(&y);
        if (k >= 0 && b2d[k] + 1 < best) best = b2d[k] + 1;
        for (int b = 0; b < NGEN; b++) {
            State z = apply(&y, b); k = b2_find(&z);
            if (k >= 0 && b2d[k] + 2 < best) best = b2d[k] + 2;
            if (maxd >= 5 && best > 5) for (int c = 0; c < NGEN; c++) {
                State w = apply(&z, c); k = b2_find(&w);
                if (k >= 0 && b2d[k] + 3 < best) best = b2d[k] + 3;
            }
        }
    }
    return best <= maxd ? best : -1;
}

static int fwd_max;
static void fdfs(const State *x, int depth, int last) {
    insert(fp(x), depth);
    if (depth == fwd_max) return;
    for (int g = 0; g < NGEN; g++) if (follows(last, g)) { State y = apply(x, g); fdfs(&y, depth + 1, g); }
}

/* symmetries: alpha (automorphism of GL_4 preserving the CNOT set) x conjugation by S in GL_2(F2) */
#define NA 48
static uint16_t *amap[NA]; static int nalpha;
static int S2[6][2], S2i[6][2];
static State phi(const State *x, int a, int s) {
    State t, u, r; memset(&t, 0, sizeof t); memset(&u, 0, sizeof u); memset(&r, 0, sizeof r);
    for (int i = 0; i < R; i++) for (int j = 0; j < R; j++) {
        Set *o = &t.s[i][j]; o->n = x->s[i][j].n;
        for (int k = 0; k < o->n; k++) o->e[k] = amap[a][x->s[i][j].e[k]];
        qsort(o->e, o->n, 2, cmp16);
    }
    Set tmp;
    for (int i = 0; i < R; i++) for (int j = 0; j < R; j++) for (int k = 0; k < R; k++)
        if (S2[s][i] >> k & 1) { sym_into(&tmp, &u.s[i][j], &t.s[k][j]); u.s[i][j] = tmp; }
    for (int i = 0; i < R; i++) for (int j = 0; j < R; j++) for (int k = 0; k < R; k++)
        if (S2i[s][k] >> j & 1) { sym_into(&tmp, &r.s[i][j], &u.s[i][k]); r.s[i][j] = tmp; }
    return r;
}

static void setup(void) {
    int n = 0;
    for (int m = 0; m < 65536; m++) { idx_of[m] = 0xFFFF; if (invertible(m)) { idx_of[m] = (uint16_t)n; elem[n++] = (uint16_t)m; } }
    need(n == NG, "GL_4(F2) order");
    int c = 0;
    for (int i = 0; i < 4; i++) for (int j = 0; j < 4; j++) if (i != j) { int g = identity4() ^ ((1 << j) << (4 * i)); cn[c++] = idx_of[g]; }
    for (int gi = 0; gi < NC; gi++) for (int x = 0; x < NG; x++) rmul[gi][x] = idx_of[mat_mul(elem[x], elem[cn[gi]])];
    int p = 0;
    for (int u = 1; u < 4; u++) for (int v = 1; v < 4; v++) if (__builtin_popcount((unsigned)(u & v)) & 1) { gen_u[p] = u; gen_v[p] = v; p++; }
    need(p == NP, "projectors");
    /* automorphisms: conjugation by the 24 coordinate permutations, optionally composed with inverse-transpose */
    int perm[4] = {0, 1, 2, 3}; nalpha = 0;
    for (int a0 = 0; a0 < 4; a0++) for (int a1 = 0; a1 < 4; a1++) for (int a2 = 0; a2 < 4; a2++) for (int a3 = 0; a3 < 4; a3++) {
        if ((1<<a0|1<<a1|1<<a2|1<<a3) != 15) continue;
        perm[0]=a0; perm[1]=a1; perm[2]=a2; perm[3]=a3;
        int P = rowperm(perm), Pi = inverse4(P);
        for (int t = 0; t < 2; t++) {
            amap[nalpha] = malloc(2 * NG);
            for (int x = 0; x < NG; x++) { int y = mat_mul(mat_mul(P, elem[x]), Pi); if (t) y = transpose4(inverse4(y)); amap[nalpha][x] = idx_of[y]; }
            nalpha++;
        }
    }
    int ns = 0;
    for (int r0 = 1; r0 < 4; r0++) for (int r1 = 1; r1 < 4; r1++) if (r0 != r1) {
        S2[ns][0] = r0; S2[ns][1] = r1;
        for (int q0 = 1; q0 < 4; q0++) for (int q1 = 1; q1 < 4; q1++) {
            int o0 = 0, o1 = 0;   /* S * Q rows */
            for (int k = 0; k < 2; k++) { if (r0 >> k & 1) o0 ^= (k ? q1 : q0); if (r1 >> k & 1) o1 ^= (k ? q1 : q0); }
            if (o0 == 1 && o1 == 2) { S2i[ns][0] = q0; S2i[ns][1] = q1; }
        }
        ns++;
    }
    State I = identity_state(), ga[NGEN];
    for (int a = 0; a < NGEN; a++) ga[a] = apply(&I, a);
    for (int a = 0; a < NGEN; a++) for (int b = 0; b < NGEN; b++) { State x = apply(&ga[a], b), y = apply(&ga[b], a); comm[a][b] = (unsigned char)steq(&x, &y); }
}

typedef struct { long key_matches, nodes; int best; } Report;
static int bword[16];
static void visit(const State *x, int d, Report *rep) {
    rep->nodes++;
    int k = lookup(fp(x));
    if (k >= 0) { rep->key_matches++; if (k + d < rep->best) { int e = verify_exact(x, k); if (e >= 0 && e + d < rep->best) rep->best = e + d; } }
}
static void bdfs(const State *x, int d, int maxd, Report *rep) {
    visit(x, d, rep);
    if (d == maxd) return;
    for (int g = 0; g < NGEN; g++) {
        if (g == bword[d - 1] || (d >= 3 && !follows(bword[d - 1], g))) continue;
        bword[d] = g; State y = apply(x, g); bdfs(&y, d + 1, maxd, rep);
    }
}

int main(int argc, char **argv) {
    setup();
    if (argc < 2) return 2;
    if (!strcmp(argv[1], "count")) {
        int dmax = atoi(argv[2]), bits = argc > 3 ? atoi(argv[3]) : 24;
        alloc_table(bits);
        for (fwd_max = 1; fwd_max <= dmax; fwd_max++) {
            memset(table, 0, (tmask + 1) * 8); distinct = 0;
            State s = identity_state(); fdfs(&s, 0, -1);
            printf("depth<=%d distinct=%ld\n", fwd_max, distinct); fflush(stdout);
        }
        return 0;
    }
    if (!strcmp(argv[1], "dump")) {
        State s = identity_state();
        for (int i = 2; i < argc; i++) s = apply(&s, atoi(argv[i]));
        for (int i = 0; i < R; i++) for (int j = 0; j < R; j++) {
            printf("entry %d %d:", i, j);
            for (int k = 0; k < s.s[i][j].n; k++) printf(" %d", elem[s.s[i][j].e[k]]);
            printf("\n");
        }
        return 0;
    }
    if (!strcmp(argv[1], "selftest")) {
        long pairs = 0; for (int a = 0; a < NGEN; a++) for (int b = 0; b < NGEN; b++) pairs += a != b && comm[a][b];
        build_b2();
        /* exact verification: random words of length 3..5 verify at distance <= length; the target is rejected */
        unsigned seed = 4974; long verified = 0;
        for (int trial = 0; trial < 12; trial++) {
            int len = 3 + trial % 3; State y = identity_state();
            for (int i = 0; i < len; i++) { seed = seed * 1103515245u + 12345u; y = apply(&y, (int)((seed >> 8) % NGEN)); }
            int e = verify_exact(&y, 5);
            need(e >= 0 && e <= len, "random word verified within its length");
            verified++;
        }
        int c3[4] = {1, 2, 0, 3}; State T; memset(&T, 0, sizeof T);
        T.s[0][0].n = 1; T.s[0][0].e[0] = idx_of[rowperm(c3)]; T.s[1][1].n = 1; T.s[1][1].e[0] = idx_of[rowperm(c3)];
        need(verify_exact(&T, 5) == -1, "c3c3 is not within distance five");
        printf("selftest commuting_ordered_pairs=%ld ball2=%ld verified_words=%ld\n", pairs, b2n, verified);
        return 0;
    }
    if (argc < 4) return 2;
    int c3[4] = {1, 2, 0, 3}, s01[4] = {1, 0, 2, 3}, e4[4] = {0, 1, 2, 3};
    int a, b;
    if (!strcmp(argv[1], "c3c3")) { a = rowperm(c3); b = rowperm(c3); }
    else if (!strcmp(argv[1], "c3e")) { a = rowperm(c3); b = rowperm(e4); }
    else if (!strcmp(argv[1], "s01s01")) { a = rowperm(s01); b = rowperm(s01); }
    else if (!strcmp(argv[1], "c3s01")) { a = rowperm(c3); b = rowperm(s01); }
    else return 2;
    fwd_max = atoi(argv[2]);
    int bwd_max = atoi(argv[3]);
    need(fwd_max >= 0 && fwd_max <= 5 && bwd_max >= 0 && bwd_max <= 8, "depth range (exact verification covers forward depth <= 5)");
    int use_sym = !(argc > 4 && !strcmp(argv[4], "nosym"));
    int workers = argc > 5 ? atoi(argv[5]) : 1, bits = argc > 6 ? atoi(argv[6]) : 24;
    State T; memset(&T, 0, sizeof T);
    T.s[0][0].n = 1; T.s[0][0].e[0] = idx_of[a]; T.s[1][1].n = 1; T.s[1][1].e[0] = idx_of[b];

    State I = identity_state(), gstate[NGEN];
    for (int g = 0; g < NGEN; g++) gstate[g] = apply(&I, g);
    static int img[NA * 6][NGEN]; int nsym = 0;
    if (use_sym) for (int al = 0; al < nalpha; al++) for (int s = 0; s < 6; s++) {
        State pt = phi(&T, al, s);
        if (!steq(&pt, &T)) continue;
        int ok = 1;
        for (int g = 0; g < NGEN && ok; g++) {
            State pg = phi(&gstate[g], al, s); img[nsym][g] = -1;
            for (int h = 0; h < NGEN; h++) if (steq(&pg, &gstate[h])) { img[nsym][g] = h; break; }
            if (img[nsym][g] < 0) ok = 0;
        }
        if (ok) nsym++;
    }
    static unsigned char pair_ok[NGEN * NGEN]; long npairs = 0;
    for (int x = 0; x < NGEN; x++) for (int y = 0; y < NGEN; y++) {
        int ok = x != y;
        for (int s = 0; s < nsym && ok; s++) { int p2 = img[s][x], q2 = img[s][y]; if (p2 < x || (p2 == x && q2 < y)) ok = 0; }
        pair_ok[x * NGEN + y] = (unsigned char)ok; npairs += ok;
    }
    printf("target=%s symmetries=%d pairs=%ld mode=%s\n", argv[1], use_sym ? nsym : 1, npairs, use_sym ? "sym" : "nosym"); fflush(stdout);
    build_b2();
    alloc_table(bits);
    State s0 = identity_state(); fdfs(&s0, 0, -1);
    printf("forward_depth=%d distinct=%ld ball2=%ld\n", fwd_max, distinct, b2n); fflush(stdout);
    Report total = {0, 0, 99};
    { int k = lookup(fp(&T)); total.nodes++;
      if (k >= 0) { total.key_matches++; int e = verify_exact(&T, k); if (e >= 0) total.best = e; }
      for (int x = 0; x < NGEN; x++) {
          int any = 0; for (int y = 0; y < NGEN; y++) any |= pair_ok[x * NGEN + y];
          if (!any) continue;
          State y1 = apply(&T, x); total.nodes++; k = lookup(fp(&y1));
          if (k >= 0) { total.key_matches++; int e = verify_exact(&y1, k); if (e >= 0 && e + 1 < total.best) total.best = e + 1; }
      } }
    if (bwd_max >= 2) {
        int pipes[64][2];
        need(workers >= 1 && workers <= 64, "workers");
        for (int w = 0; w < workers; w++) {
            need(!pipe(pipes[w]), "pipe");
            pid_t pid = fork(); need(pid >= 0, "fork");
            if (pid == 0) {
                close(pipes[w][0]);
                Report rep = {0, 0, 99}; long pi = -1;
                for (int x = 0; x < NGEN; x++) {
                    State yx = apply(&T, x);
                    for (int y = 0; y < NGEN; y++) {
                        if (!pair_ok[x * NGEN + y]) continue;
                        if (++pi % workers != w) continue;
                        bword[0] = x; bword[1] = y;
                        State yy = apply(&yx, y);
                        bdfs(&yy, 2, bwd_max, &rep);
                    }
                }
                if (write(pipes[w][1], &rep, sizeof rep) != (ssize_t)sizeof rep) _exit(5);
                _exit(0);
            }
            close(pipes[w][1]);
        }
        for (int w = 0; w < workers; w++) {
            Report rep; need(read(pipes[w][0], &rep, sizeof rep) == (ssize_t)sizeof rep, "worker report");
            int st; wait(&st); need(WIFEXITED(st) && !WEXITSTATUS(st), "worker exit");
            total.key_matches += rep.key_matches; total.nodes += rep.nodes; if (rep.best < total.best) total.best = rep.best;
        }
    }
    printf("RESULT target=%s max_length=%d shortest=%d key_matches=%ld backward_nodes=%ld\n",
           argv[1], fwd_max + bwd_max, total.best == 99 ? -1 : total.best, total.key_matches, total.nodes);
    return 0;
}
