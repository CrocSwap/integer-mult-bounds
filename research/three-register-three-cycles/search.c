/* Exact meet-in-the-middle search in the formal model M_3(F2[GL_3(F2)]).
 *
 * A paid call is D(g,N) = I + ([g]+[e]) N, with g one of the six coordinate
 * CNOTs of GL_3(F2) and N one of the 28 rank-one binary idempotents u v^T
 * (v.u = 1) of M_3(F2): 168 generators, numbered 28*cnot + projector in the
 * order of research/swap-component-cut/formal.py. Free scalar maps are
 * normalized away (#4939 step 1). Every call is an involution, so if T * W = X
 * with X a product of k calls, then T = X * reverse(W) has length k + |W|.
 *
 * Word reductions, all sound for a shortest word:
 *   - adjacent equal letters cancel, so they are skipped;
 *   - adjacent commuting letters (exact algebra test) are kept only in
 *     increasing order (lexicographically least word of a commutation class);
 *   - backward search, "sym" mode: the first two backward letters range over
 *     lexicographically least representatives of their orbit under the
 *     symmetries fixing the target and the generator set; the commutation rule
 *     then applies from the third letter on, so it never moves those two.
 *
 * Usage:
 *   search count <d> [bits]                distinct states at depths <= 1..d
 *   search dump <g1> <g2> ...              print the product state, entry bits
 *   search commute                         number of commuting ordered pairs
 *   search selftest                        batched fingerprints, radius-two verifier
 *   search <target> <fwd> <bwd> [sym|nosym] [workers] [bits]
 *       targets: c3c3e c3ee c7c7e s01s01e c3s01e; fwd <= 4; table 2^bits slots
 *
 * Forward: DFS from I to depth <= fwd, storing 61-bit fingerprints with the
 * minimum depth. Backward: DFS from T to depth <= bwd in forked workers that
 * share the table, looking up every state. Fingerprints are deterministic, so
 * a real match always finds its key. Every key match is checked exactly: a
 * state at distance <= 4 is A * B with A in the stored exact radius-two ball
 * and |B| <= 2. Fingerprint collisions are counted as key matches and then
 * rejected; shortest = -1 excludes every word of length <= fwd + bwd.
 */
#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/wait.h>
#include <unistd.h>

#define NG 168
#define R 3
#define NP 28
#define NGEN (6 * NP)
typedef struct { uint64_t w[3]; } Set;
typedef struct { Set e[R][R]; } State;

static int elem[NG], idx_of[512];
static int cn[6];
static int gen_u[NP], gen_v[NP];
static Set trans[6][21][256];
static unsigned char comm[NGEN][NGEN];

static int mat_mul(int a, int b) {
    int r = 0;
    for (int i = 0; i < 3; i++) {
        int row = 0, ai = (a >> (3 * i)) & 7;
        for (int k = 0; k < 3; k++) if (ai >> k & 1) row ^= (b >> (3 * k)) & 7;
        r |= row << (3 * i);
    }
    return r;
}
static int transpose3(int a) {
    int r = 0;
    for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++)
        if ((a >> (3 * i + j)) & 1) r |= 1 << (3 * j + i);
    return r;
}
static int identity3(void) { return 1 | (2 << 3) | (4 << 6); }
static int invertible(int m) {
    int rows[3] = {m & 7, (m >> 3) & 7, (m >> 6) & 7}, r = 0;
    for (int bit = 0; bit < 3; bit++) {
        int p = -1;
        for (int i = r; i < 3; i++) if (rows[i] >> bit & 1) { p = i; break; }
        if (p < 0) continue;
        int t = rows[r]; rows[r] = rows[p]; rows[p] = t;
        for (int i = 0; i < 3; i++) if (i != r && (rows[i] >> bit & 1)) rows[i] ^= rows[r];
        r++;
    }
    return r == 3;
}
static int inverse3(int a) {
    for (int i = 0; i < NG; i++) if (mat_mul(a, elem[i]) == identity3()) return elem[i];
    abort();
}
/* row a of the result is row sigma[a] of the identity */
static int rowperm(int s0, int s1, int s2) {
    int s[3] = {s0, s1, s2}, m = 0;
    for (int a = 0; a < 3; a++) m |= (1 << s[a]) << (3 * a);
    return m;
}

static void sxor(Set *a, const Set *b) { a->w[0] ^= b->w[0]; a->w[1] ^= b->w[1]; a->w[2] ^= b->w[2]; }
static void sbit(Set *s, int b) { s->w[b >> 6] |= 1ULL << (b & 63); }
static int gbit(const Set *s, int b) { return (int)((s->w[b >> 6] >> (b & 63)) & 1); }
static int steq(const State *a, const State *b) { return memcmp(a, b, sizeof *a) == 0; }

static Set translate(int gi, const Set *s) {
    Set o = {{0, 0, 0}};
    for (int byte = 0; byte < 21; byte++) {
        int v = (int)((s->w[byte >> 3] >> (8 * (byte & 7))) & 255);
        if (v) sxor(&o, &trans[gi][byte][v]);
    }
    return o;
}
static State apply(const State *x, int gen) {   /* x * D(g, u v^T) = x + (x u)([g]+[e]) v^T */
    int gi = gen / NP, ni = gen % NP, u = gen_u[ni], v = gen_v[ni];
    State r = *x;
    for (int i = 0; i < R; i++) {
        Set z = {{0, 0, 0}};
        for (int k = 0; k < R; k++) if (u >> k & 1) sxor(&z, &x->e[i][k]);
        Set t = translate(gi, &z);
        sxor(&t, &z);
        for (int j = 0; j < R; j++) if (v >> j & 1) sxor(&r.e[i][j], &t);
    }
    return r;
}
/* additive fingerprint: a sum of independently mixed words, so a call that
 * changes a few entries updates it incrementally (children_fp) */
static uint64_t mix(uint64_t z, int k) {
    z ^= 0x9E3779B97F4A7C15ULL * (uint64_t)(k + 1);
    z ^= z >> 33; z *= 0xFF51AFD7ED558CCDULL;
    z ^= z >> 33; z *= 0xC4CEB9FE1A85EC53ULL;
    z ^= z >> 33;
    return z;
}
static uint64_t entry_mix(const Set *s, int i, int j) {
    int k = 3 * (R * i + j);
    return mix(s->w[0], k) + mix(s->w[1], k + 1) + mix(s->w[2], k + 2);
}
static uint64_t fp_raw(const State *s) {
    uint64_t h = 0;
    for (int i = 0; i < R; i++) for (int j = 0; j < R; j++) h += entry_mix(&s->e[i][j], i, j);
    return h;
}
static uint64_t fp(const State *s) { return fp_raw(s) | 8; }

/* fingerprints of x * D(g) for all generators g, sharing the 126 translates */
static void children_fp(const State *x, uint64_t out[NGEN]) {
    Set t[6][R][8];
    uint64_t base = fp_raw(x), old[R][R];
    for (int i = 0; i < R; i++) {
        Set z[8];
        memset(&z[0], 0, sizeof z[0]);
        for (int u = 1; u < 8; u++) {
            int low = u & -u, k = __builtin_ctz((unsigned)u);
            z[u] = z[u ^ low];
            sxor(&z[u], &x->e[i][k]);
        }
        for (int gi = 0; gi < 6; gi++) for (int u = 1; u < 8; u++) {
            t[gi][i][u] = translate(gi, &z[u]);
            sxor(&t[gi][i][u], &z[u]);
        }
        for (int j = 0; j < R; j++) old[i][j] = entry_mix(&x->e[i][j], i, j);
    }
    for (int gi = 0; gi < 6; gi++) for (int ni = 0; ni < NP; ni++) {
        int u = gen_u[ni], v = gen_v[ni];
        uint64_t h = base;
        for (int i = 0; i < R; i++) for (int j = 0; j < R; j++) if (v >> j & 1) {
            Set y = x->e[i][j];
            sxor(&y, &t[gi][i][u]);
            h += entry_mix(&y, i, j) - old[i][j];
        }
        out[gi * NP + ni] = h | 8;
    }
}

static uint64_t *table, tmask;
static long distinct;
static void insert(uint64_t h, int d) {
    uint64_t key = h & ~7ULL, i = (h >> 7) & tmask;
    for (;;) {
        uint64_t t = table[i];
        if (!t) { table[i] = key | (uint64_t)d; distinct++; return; }
        if ((t & ~7ULL) == key) { if ((int)(t & 7) > d) table[i] = key | (uint64_t)d; return; }
        i = (i + 1) & tmask;
    }
}
static int lookup(uint64_t h) {
    uint64_t key = h & ~7ULL, i = (h >> 7) & tmask;
    for (;;) {
        uint64_t t = table[i];
        if (!t) return -1;
        if ((t & ~7ULL) == key) return (int)(t & 7);
        i = (i + 1) & tmask;
    }
}
static void alloc_table(int bits) {
    size_t n = (size_t)1 << bits;
    table = mmap(NULL, n * 8, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (table == MAP_FAILED) { fprintf(stderr, "table allocation failed\n"); exit(3); }
    tmask = n - 1;
}

/* may letter g follow letter last? (no cancellation, commuting pairs ascending) */
static int follows(int last, int g) { return last < 0 || (g != last && !(comm[last][g] && last > g)); }

static int fwd_max;
static void fdfs(const State *x, int depth, int last) {
    insert(fp(x), depth);
    if (depth == fwd_max) return;
    for (int g = 0; g < NGEN; g++) if (follows(last, g)) { State y = apply(x, g); fdfs(&y, depth + 1, g); }
}
static State identity_state(void) {
    State s;
    memset(&s, 0, sizeof s);
    for (int i = 0; i < R; i++) sbit(&s.e[i][i], idx_of[identity3()]);
    return s;
}

/* exact radius-two ball, full states with their exact depth, for verification */
#define B2BITS 16
static State b2_state[1 << B2BITS];
static signed char b2_depth[1 << B2BITS];
static long b2_size;
static int b2_find(const State *x) {   /* slot of x, or of the empty slot where it belongs */
    uint64_t i = (fp_raw(x) >> 7) & ((1 << B2BITS) - 1);
    while (b2_depth[i] >= 0 && !steq(&b2_state[i], x)) i = (i + 1) & ((1 << B2BITS) - 1);
    return (int)i;
}
static void build_b2(void) {
    memset(b2_depth, -1, sizeof b2_depth);
    State I = identity_state(), layer1[NGEN];
    int s = b2_find(&I);
    b2_state[s] = I; b2_depth[s] = 0; b2_size = 1;
    for (int a = 0; a < NGEN; a++) {
        layer1[a] = apply(&I, a);
        s = b2_find(&layer1[a]);
        if (b2_depth[s] < 0) { b2_state[s] = layer1[a]; b2_depth[s] = 1; b2_size++; }
    }
    for (int a = 0; a < NGEN; a++) for (int b = 0; b < NGEN; b++) {
        State y = apply(&layer1[a], b);
        s = b2_find(&y);
        if (b2_depth[s] < 0) { b2_state[s] = y; b2_depth[s] = 2; b2_size++; }
    }
}
/* exact distance of x from I when it is at most maxd <= 4, else -1:
 * x = A * B with |A| <= 2, |B| <= 2 iff x * reverse(B) = A lies in the ball */
static int verify_exact(const State *x, int maxd) {
    int best = 99, s = b2_find(x);
    if (b2_depth[s] >= 0) best = b2_depth[s];
    for (int a = 0; a < NGEN; a++) {
        State y = apply(x, a);
        s = b2_find(&y);
        if (b2_depth[s] >= 0 && b2_depth[s] + 1 < best) best = b2_depth[s] + 1;
        for (int b = 0; b < NGEN; b++) {
            State z = apply(&y, b);
            s = b2_find(&z);
            if (b2_depth[s] >= 0 && b2_depth[s] + 2 < best) best = b2_depth[s] + 2;
        }
    }
    return best <= maxd ? best : -1;
}

/* symmetries: alpha (automorphism of GL_3 applied entrywise) x conjugation by S in GL_3(F2) */
static int alpha_map[12][NG];
static int m3inv[NG];
static State phi(const State *x, int a, int s) {   /* S alpha(x) S^-1, S = elem[s] acting on registers */
    State t, u, r;
    memset(&t, 0, sizeof t); memset(&u, 0, sizeof u); memset(&r, 0, sizeof r);
    int S = elem[s], Si = m3inv[s];
    for (int i = 0; i < R; i++) for (int j = 0; j < R; j++)
        for (int b = 0; b < NG; b++) if (gbit(&x->e[i][j], b)) sbit(&t.e[i][j], alpha_map[a][b]);
    for (int i = 0; i < R; i++) for (int j = 0; j < R; j++) for (int k = 0; k < R; k++)
        if ((S >> (3 * i + k)) & 1) sxor(&u.e[i][j], &t.e[k][j]);
    for (int i = 0; i < R; i++) for (int j = 0; j < R; j++) for (int k = 0; k < R; k++)
        if ((Si >> (3 * k + j)) & 1) sxor(&r.e[i][j], &u.e[i][k]);
    return r;
}

static void setup(void) {
    int n = 0;
    for (int m = 0; m < 512; m++) {
        idx_of[m] = -1;
        if (invertible(m)) { idx_of[m] = n; elem[n++] = m; }
    }
    if (n != NG) { fprintf(stderr, "GL_3(F2) order %d\n", n); exit(1); }
    for (int i = 0; i < NG; i++) m3inv[i] = inverse3(elem[i]);
    int c = 0;
    for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) if (i != j) {
        int g = identity3();
        g ^= (1 << j) << (3 * i);
        cn[c++] = idx_of[g];
    }
    int p = 0;
    for (int u = 1; u < (1 << R); u++) for (int v = 1; v < (1 << R); v++)
        if (__builtin_popcount((unsigned)(u & v)) & 1) { gen_u[p] = u; gen_v[p] = v; p++; }
    if (p != NP) exit(1);
    for (int gi = 0; gi < 6; gi++) for (int byte = 0; byte < 21; byte++) for (int val = 0; val < 256; val++) {
        Set o = {{0, 0, 0}};
        for (int b = 0; b < 8; b++) if (val >> b & 1) {
            int x = byte * 8 + b;
            if (x < NG) sbit(&o, idx_of[mat_mul(elem[x], elem[cn[gi]])]);
        }
        trans[gi][byte][val] = o;
    }
    int perms[6][3] = {{0, 1, 2}, {1, 0, 2}, {0, 2, 1}, {2, 1, 0}, {1, 2, 0}, {2, 0, 1}};
    int na = 0;
    for (int pi = 0; pi < 6; pi++) for (int t = 0; t < 2; t++) {
        int P = rowperm(perms[pi][0], perms[pi][1], perms[pi][2]), Pinv = inverse3(P);
        for (int x = 0; x < NG; x++) {
            int y = mat_mul(mat_mul(P, elem[x]), Pinv);
            if (t) y = transpose3(inverse3(y));
            alpha_map[na][x] = idx_of[y];
        }
        na++;
    }
    State I = identity_state(), ga[NGEN], gab[NGEN];
    for (int a = 0; a < NGEN; a++) ga[a] = apply(&I, a);
    for (int a = 0; a < NGEN; a++) {
        for (int b = 0; b < NGEN; b++) gab[b] = apply(&ga[a], b);
        for (int b = 0; b < NGEN; b++) { State ba = apply(&ga[b], a); comm[a][b] = (unsigned char)steq(&gab[b], &ba); }
    }
}

static void print_state(const State *s) {
    for (int i = 0; i < R; i++) for (int j = 0; j < R; j++) {
        printf("entry %d %d:", i, j);
        for (int b = 0; b < NG; b++) if (gbit(&s->e[i][j], b)) printf(" %d", elem[b]);
        printf("\n");
    }
}

#define MAXSYM (12 * NG)
static int img[MAXSYM][NGEN], nsym;


typedef struct { long key_matches, nodes; int best; int word[16], wlen, fwd; } Report;

/* backward DFS below a fixed pair (bword[0], bword[1]); the third letter only
 * avoids cancellation, later letters also follow the commutation order */
static int bword[16];
static void visit(const State *x, int d, uint64_t h, Report *rep) {
    rep->nodes++;
    int k = lookup(h);
    if (k >= 0) {
        rep->key_matches++;
        if (k + d < rep->best) {
            int e = verify_exact(x, k);
            if (e >= 0 && e + d < rep->best) {
                rep->best = e + d; rep->fwd = e; rep->wlen = d;
                memcpy(rep->word, bword, sizeof bword);
            }
        }
    }
}
static int allowed(int d, int g) { return g != bword[d - 1] && (d < 3 || follows(bword[d - 1], g)); }
static void bdfs(const State *x, int d, int maxd, Report *rep) {
    visit(x, d, fp(x), rep);
    if (d == maxd) return;
    if (d + 1 == maxd) {   /* leaves: batched fingerprints, prefetched probes */
        uint64_t h[NGEN];
        children_fp(x, h);
        for (int g = 0; g < NGEN; g++) __builtin_prefetch(&table[(h[g] >> 7) & tmask]);
        for (int g = 0; g < NGEN; g++) {
            if (!allowed(d, g)) continue;
            rep->nodes++;
            if (lookup(h[g]) < 0) continue;
            rep->nodes--;
            bword[d] = g;
            State y = apply(x, g);
            visit(&y, d + 1, h[g], rep);
        }
        return;
    }
    for (int g = 0; g < NGEN; g++) {
        if (!allowed(d, g)) continue;
        bword[d] = g;
        State y = apply(x, g);
        bdfs(&y, d + 1, maxd, rep);
    }
}

int main(int argc, char **argv) {
    setup();
    if (argc < 2) return 2;
    if (!strcmp(argv[1], "count")) {
        int d = atoi(argv[2]), bits = argc > 3 ? atoi(argv[3]) : 26;
        alloc_table(bits);
        for (fwd_max = 1; fwd_max <= d; fwd_max++) {
            memset(table, 0, (tmask + 1) * 8); distinct = 0;
            State s = identity_state();
            fdfs(&s, 0, -1);
            printf("depth<=%d distinct=%ld\n", fwd_max, distinct);
            fflush(stdout);
        }
        return 0;
    }
    if (!strcmp(argv[1], "dump")) {
        State s = identity_state();
        for (int i = 2; i < argc; i++) s = apply(&s, atoi(argv[i]));
        print_state(&s);
        return 0;
    }
    if (!strcmp(argv[1], "selftest")) {   /* batched leaf fingerprints equal direct ones */
        State s = identity_state();
        long checked = 0;
        for (int step = 0; step < 200; step++) {
            uint64_t h[NGEN];
            children_fp(&s, h);
            for (int g = 0; g < NGEN; g++) { State y = apply(&s, g); if (h[g] != fp(&y)) { printf("selftest FAIL\n"); return 1; } checked++; }
            s = apply(&s, (int)((step * 97 + 13) % NGEN));
        }
        build_b2();
        long words = 0;
        for (int trial = 0; trial < 400; trial++) {
            int len = trial % 5;
            State y = identity_state();
            for (int i = 0; i < len; i++) y = apply(&y, (int)((trial * 7919 + i * 104729 + 17) % NGEN));
            int e = verify_exact(&y, 4);
            if (e < 0 || e > len) { printf("selftest verify FAIL\n"); return 1; }
            words++;
        }
        printf("selftest children=%ld ok ball2=%ld verified_words=%ld\n", checked, b2_size, words);
        return 0;
    }
    if (!strcmp(argv[1], "commute")) {
        long pairs = 0;
        for (int a = 0; a < NGEN; a++) for (int b = 0; b < NGEN; b++) pairs += a != b && comm[a][b];
        printf("commuting_ordered_pairs=%ld of %d\n", pairs, NGEN * (NGEN - 1));
        return 0;
    }
    if (argc < 4) return 2;
    int t[R];
    int C3 = rowperm(1, 2, 0), S01 = rowperm(1, 0, 2), E = identity3();
    int C7 = mat_mul(mat_mul(elem[cn[0]], elem[cn[3]]), elem[cn[4]]);   /* C01 C12 C20 */
    if (!strcmp(argv[1], "c3c3e")) { t[0] = C3; t[1] = C3; t[2] = E; }
    else if (!strcmp(argv[1], "c3ee")) { t[0] = C3; t[1] = E; t[2] = E; }
    else if (!strcmp(argv[1], "c7c7e")) { t[0] = C7; t[1] = C7; t[2] = E; }
    else if (!strcmp(argv[1], "s01s01e")) { t[0] = S01; t[1] = S01; t[2] = E; }
    else if (!strcmp(argv[1], "c3s01e")) { t[0] = C3; t[1] = S01; t[2] = E; }
    else return 2;
    fwd_max = atoi(argv[2]);
    int bwd_max = atoi(argv[3]);
    if (fwd_max < 0 || fwd_max > 4 || bwd_max < 0 || bwd_max > 12) return 2;
    build_b2();
    int use_sym = !(argc > 4 && !strcmp(argv[4], "nosym"));
    int workers = argc > 5 ? atoi(argv[5]) : 1;
    int bits = argc > 6 ? atoi(argv[6]) : 26;
    State T;
    memset(&T, 0, sizeof T);
    for (int i = 0; i < R; i++) sbit(&T.e[i][i], idx_of[t[i]]);

    State gstate[NGEN], I = identity_state();
    for (int g = 0; g < NGEN; g++) gstate[g] = apply(&I, g);
    nsym = 0;
    if (use_sym) for (int al = 0; al < 12; al++) for (int s = 0; s < NG; s++) {
        State pt = phi(&T, al, s);
        if (!steq(&pt, &T)) continue;
        int okset = 1;
        for (int g = 0; g < NGEN && okset; g++) {
            State pg = phi(&gstate[g], al, s);
            img[nsym][g] = -1;
            for (int h = 0; h < NGEN; h++) if (steq(&pg, &gstate[h])) { img[nsym][g] = h; break; }
            if (img[nsym][g] < 0) okset = 0;
        }
        if (okset) nsym++;
    }
    static unsigned char pair_ok[NGEN * NGEN];
    long npairs = 0;
    int first_letters = 0;
    for (int a = 0; a < NGEN; a++) {
        int arep = 1;
        for (int s = 0; s < nsym; s++) if (img[s][a] < a) arep = 0;
        first_letters += !use_sym || arep;
        for (int b = 0; b < NGEN; b++) {
            int ok = a != b;
            for (int s = 0; s < nsym && ok; s++) {
                int x = img[s][a], y = img[s][b];
                if (x < a || (x == a && y < b)) ok = 0;
            }
            pair_ok[a * NGEN + b] = (unsigned char)ok;
            npairs += ok;
        }
    }
    printf("target=%s symmetries=%d first_letters=%d pairs=%ld mode=%s\n", argv[1], use_sym ? nsym : 1,
           first_letters, npairs, use_sym ? "sym" : "nosym");
    fflush(stdout);

    alloc_table(bits);
    State s0 = identity_state();
    fdfs(&s0, 0, -1);
    printf("forward_depth=%d distinct=%ld\n", fwd_max, distinct);
    fflush(stdout);

    /* length-one backward words: every first-letter representative, checked once here */
    Report total = {0, 0, 99, {0}, 0, -1};
    {
        int k = lookup(fp(&T));
        if (k >= 0) { total.key_matches++; int e = verify_exact(&T, k); if (e >= 0) total.best = e; }
        for (int a = 0; a < NGEN; a++) {
            int any = 0;
            for (int b = 0; b < NGEN; b++) any |= pair_ok[a * NGEN + b];
            if (!any) continue;
            State y = apply(&T, a);
            total.nodes++;
            k = lookup(fp(&y));
            if (k >= 0) { total.key_matches++; int e = verify_exact(&y, k); if (e >= 0 && e + 1 < total.best) total.best = e + 1; }
        }
    }
    /* depth >= 2: pairs distributed over forked workers sharing the table copy-on-write */
    if (bwd_max >= 2) {
        int pipes[64][2];
        if (workers < 1 || workers > 64) return 2;
        for (int w = 0; w < workers; w++) {
            if (pipe(pipes[w])) return 4;
            pid_t pid = fork();
            if (pid < 0) return 4;
            if (pid == 0) {
                close(pipes[w][0]);
                Report rep = {0, 0, 99, {0}, 0, -1};
                long pair_index = -1;
                for (int a = 0; a < NGEN; a++) {
                    State ya = apply(&T, a);
                    for (int b = 0; b < NGEN; b++) {
                        if (!pair_ok[a * NGEN + b]) continue;
                        if (++pair_index % workers != w) continue;
                        bword[0] = a; bword[1] = b;
                        State yb = apply(&ya, b);
                        bdfs(&yb, 2, bwd_max, &rep);
                    }
                }
                if (write(pipes[w][1], &rep, sizeof rep) != (ssize_t)sizeof rep) _exit(5);
                _exit(0);
            }
            close(pipes[w][1]);
        }
        for (int w = 0; w < workers; w++) {
            Report rep;
            if (read(pipes[w][0], &rep, sizeof rep) != (ssize_t)sizeof rep) { fprintf(stderr, "worker %d failed\n", w); return 5; }
            int status;
            wait(&status);
            if (!WIFEXITED(status) || WEXITSTATUS(status)) { fprintf(stderr, "worker exit\n"); return 5; }
            total.key_matches += rep.key_matches;
            total.nodes += rep.nodes;
            if (rep.best < total.best) {
                total.best = rep.best;
                printf("hit total=%d forward=%d backward_word=", rep.best, rep.fwd);
                for (int i = 0; i < rep.wlen; i++) printf("%d%s", rep.word[i], i + 1 < rep.wlen ? "," : "\n");
            }
        }
    }
    printf("RESULT target=%s max_length=%d shortest=%d key_matches=%ld backward_nodes=%ld\n",
           argv[1], fwd_max + bwd_max, total.best == 99 ? -1 : total.best, total.key_matches, total.nodes);
    return 0;
}
