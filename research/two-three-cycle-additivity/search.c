/* Exact meet-in-the-middle search in the formal model M_2(F2[GL_3(F2)]).
 *
 * A paid call is D(g,N) = I + ([g]+[e]) N, with g one of the six coordinate
 * CNOTs of GL_3(F2) and N one of the six rank-one binary idempotents u v^T
 * (v.u = 1) of M_2(F2). Free scalar maps are normalized away (#4939 step 1),
 * so words consist of paid calls only. Every call is an involution, so if
 * T * W = X with X a product of k calls, then T = X * reverse(W) has length
 * k + |W|. Consecutive equal letters cancel and are skipped.
 *
 * Usage:
 *   search count <d>                     distinct states at depths <= 1..d
 *   search dump <g1> <g2> ...            print the product state, entry bits
 *   search <target> <fwd> <bwd> [sym|nosym] [lo hi]
 *       targets: c3c3 c3e s01s12 s01s01
 *       sym (default): first backward letter over orbit representatives of the
 *       generator set under symmetries fixing the target and generator set;
 *       nosym: every first letter in [lo, hi) (default all 36).
 *
 * Forward: DFS from I to depth <= fwd, storing fingerprints with minimum
 * depth. Backward: DFS from T to depth <= bwd, looking up every state. A
 * fingerprint hit is confirmed by an exact forward re-search. Since
 * fingerprints are deterministic, a real match always finds its key; the run
 * prints the number of key matches, so zero matches excludes every word of
 * length <= fwd + bwd.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NG 168
typedef struct { uint64_t w[3]; } Set;
typedef struct { Set e[2][2]; } State;

static int elem[NG], idx_of[512];
static int cn[6];
static int gen_u[6], gen_v[6];
static Set trans[6][21][256];

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
static State apply(const State *x, int gen) {   /* x * D(g, N) */
    int gi = gen / 6, ni = gen % 6, u = gen_u[ni], v = gen_v[ni];
    State r = *x;
    Set y[2][2];
    for (int i = 0; i < 2; i++) for (int k = 0; k < 2; k++) {
        y[i][k] = translate(gi, &x->e[i][k]);
        sxor(&y[i][k], &x->e[i][k]);
    }
    for (int i = 0; i < 2; i++) {
        Set z = {{0, 0, 0}};
        for (int k = 0; k < 2; k++) if (u >> k & 1) sxor(&z, &y[i][k]);
        for (int j = 0; j < 2; j++) if (v >> j & 1) sxor(&r.e[i][j], &z);
    }
    return r;
}
static uint64_t fp(const State *s) {
    uint64_t h = 0x9E3779B97F4A7C15ULL;
    for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) for (int w = 0; w < 3; w++) {
        h ^= s->e[i][j].w[w] + 0x9E3779B97F4A7C15ULL + (h << 6) + (h >> 2);
        h *= 0xBF58476D1CE4E5B9ULL;
        h ^= h >> 31;
    }
    return h | 8;
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

static int fwd_max;
static void fdfs(const State *x, int depth, int last) {
    insert(fp(x), depth);
    if (depth == fwd_max) return;
    for (int g = 0; g < 36; g++) if (g != last) { State y = apply(x, g); fdfs(&y, depth + 1, g); }
}
static const State *goal;
static int found_depth;
static void xdfs(const State *x, int depth, int maxd, int last) {
    if (steq(x, goal) && depth < found_depth) found_depth = depth;
    if (depth == maxd || depth + 1 >= found_depth) return;
    for (int g = 0; g < 36; g++) if (g != last) { State y = apply(x, g); xdfs(&y, depth + 1, maxd, g); }
}
static State identity_state(void) {
    State s;
    memset(&s, 0, sizeof s);
    sbit(&s.e[0][0], idx_of[identity3()]);
    sbit(&s.e[1][1], idx_of[identity3()]);
    return s;
}
static int verify_exact(const State *x, int maxd) {
    State s = identity_state();
    goal = x; found_depth = 99;
    xdfs(&s, 0, maxd, -1);
    return found_depth == 99 ? -1 : found_depth;
}

/* symmetries: alpha (automorphism of GL_3 applied entrywise) x conjugation by S in GL_2(F2) */
static int alpha_map[12][NG];
static int S2[6][2], S2inv[6][2];
static void m2mul(const int *a, const int *b, int *out) {
    for (int i = 0; i < 2; i++) {
        int row = 0;
        for (int k = 0; k < 2; k++) if (a[i] >> k & 1) row ^= b[k];
        out[i] = row;
    }
}
static State phi(const State *x, int a, int s) {
    State t, u, r;
    memset(&t, 0, sizeof t); memset(&u, 0, sizeof u); memset(&r, 0, sizeof r);
    for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++)
        for (int b = 0; b < NG; b++) if (gbit(&x->e[i][j], b)) sbit(&t.e[i][j], alpha_map[a][b]);
    for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) for (int k = 0; k < 2; k++)
        if (S2[s][i] >> k & 1) sxor(&u.e[i][j], &t.e[k][j]);
    for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) for (int k = 0; k < 2; k++)
        if (S2inv[s][k] >> j & 1) sxor(&r.e[i][j], &u.e[i][k]);
    return r;
}

static void setup(void) {
    int n = 0;
    for (int m = 0; m < 512; m++) {
        idx_of[m] = -1;
        if (invertible(m)) { idx_of[m] = n; elem[n++] = m; }
    }
    if (n != NG) { fprintf(stderr, "GL_3(F2) order %d\n", n); exit(1); }
    int c = 0;
    for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) if (i != j) {
        int g = identity3();
        g ^= (1 << j) << (3 * i);
        cn[c++] = idx_of[g];
    }
    int p = 0;
    for (int u = 1; u < 4; u++) for (int v = 1; v < 4; v++)
        if (__builtin_popcount((unsigned)(u & v)) & 1) { gen_u[p] = u; gen_v[p] = v; p++; }
    if (p != 6) exit(1);
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
    int ns = 0;
    for (int r0 = 1; r0 < 4; r0++) for (int r1 = 1; r1 < 4; r1++) if (r0 != r1) {
        S2[ns][0] = r0; S2[ns][1] = r1;
        for (int q0 = 1; q0 < 4; q0++) for (int q1 = 1; q1 < 4; q1++) {
            int qq[2] = {q0, q1}, out[2];
            m2mul(S2[ns], qq, out);
            if (out[0] == 1 && out[1] == 2) { S2inv[ns][0] = q0; S2inv[ns][1] = q1; }
        }
        ns++;
    }
}

static void print_state(const State *s) {
    for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) {
        printf("entry %d %d:", i, j);
        for (int b = 0; b < NG; b++) if (gbit(&s->e[i][j], b)) printf(" %d", elem[b]);
        printf("\n");
    }
}

int main(int argc, char **argv) {
    setup();
    if (argc < 2) return 2;
    if (!strcmp(argv[1], "count")) {
        int d = atoi(argv[2]);
        table = calloc(1ULL << 26, 8); tmask = (1ULL << 26) - 1;
        if (!table) return 3;
        for (fwd_max = 1; fwd_max <= d; fwd_max++) {
            memset(table, 0, (1ULL << 26) * 8); distinct = 0;
            State s = identity_state();
            fdfs(&s, 0, -1);
            printf("depth<=%d distinct=%ld\n", fwd_max, distinct);
        }
        return 0;
    }
    if (!strcmp(argv[1], "dump")) {
        State s = identity_state();
        for (int i = 2; i < argc; i++) s = apply(&s, atoi(argv[i]));
        print_state(&s);
        return 0;
    }
    if (argc < 4) return 2;
    int a, b;
    int C3 = rowperm(1, 2, 0), S01 = rowperm(1, 0, 2), S12 = rowperm(0, 2, 1), E = identity3();
    if (!strcmp(argv[1], "c3c3")) { a = C3; b = C3; }
    else if (!strcmp(argv[1], "c3e")) { a = C3; b = E; }
    else if (!strcmp(argv[1], "s01s12")) { a = S01; b = S12; }
    else if (!strcmp(argv[1], "s01s01")) { a = S01; b = S01; }
    else return 2;
    fwd_max = atoi(argv[2]);
    int bwd_max = atoi(argv[3]);
    int use_sym = !(argc > 4 && !strcmp(argv[4], "nosym"));
    int lo = argc > 6 ? atoi(argv[5]) : 0, hi = argc > 6 ? atoi(argv[6]) : 36;
    State T;
    memset(&T, 0, sizeof T);
    sbit(&T.e[0][0], idx_of[a]);
    sbit(&T.e[1][1], idx_of[b]);

    State gstate[36], I = identity_state();
    for (int g = 0; g < 36; g++) gstate[g] = apply(&I, g);
    int parent[36], first_ok[36], nsym = 0;
    for (int g = 0; g < 36; g++) parent[g] = g;
    for (int al = 0; al < 12; al++) for (int s = 0; s < 6; s++) {
        State pt = phi(&T, al, s);
        if (!steq(&pt, &T)) continue;
        int okset = 1, img[36];
        for (int g = 0; g < 36 && okset; g++) {
            State pg = phi(&gstate[g], al, s);
            img[g] = -1;
            for (int h = 0; h < 36; h++) if (steq(&pg, &gstate[h])) { img[g] = h; break; }
            if (img[g] < 0) okset = 0;
        }
        if (!okset) continue;
        nsym++;
        for (int g = 0; g < 36; g++) {
            int x = g, y = img[g];
            while (parent[x] != x) x = parent[x];
            while (parent[y] != y) y = parent[y];
            if (x != y) parent[y] = x;
        }
    }
    int reps = 0;
    for (int g = 0; g < 36; g++) {
        int x = g;
        while (parent[x] != x) x = parent[x];
        first_ok[g] = use_sym ? (x == g) : (g >= lo && g < hi);
        reps += first_ok[g];
    }
    printf("target=%s symmetries=%d first_letters=%d mode=%s\n", argv[1], nsym, reps, use_sym ? "sym" : "nosym");

    table = calloc(1ULL << 26, 8); tmask = (1ULL << 26) - 1;
    if (!table) return 3;
    State s0 = identity_state();
    fdfs(&s0, 0, -1);
    printf("forward_depth=%d distinct=%ld\n", fwd_max, distinct);

    int best = 99, word[16], gnext[16], depth = 0;
    long key_matches = 0, nodes = 0;
    State stack[16];
    stack[0] = T; gnext[0] = 0;
    if (use_sym || lo == 0) {
        int k = lookup(fp(&T));
        if (k >= 0) { key_matches++; int e = verify_exact(&T, k); if (e >= 0) best = e; }
    }
    while (depth >= 0) {
        if (depth == bwd_max || gnext[depth] >= 36) { depth--; continue; }
        int g = gnext[depth]++;
        if (depth > 0 && g == word[depth - 1]) continue;
        if (depth == 0 && !first_ok[g]) continue;
        word[depth] = g;
        stack[depth + 1] = apply(&stack[depth], g);
        gnext[depth + 1] = 0;
        int d = depth + 1;
        nodes++;
        int k = lookup(fp(&stack[d]));
        if (k >= 0) {
            key_matches++;
            if (k + d < best) {
                int e = verify_exact(&stack[d], k);
                if (e >= 0 && e + d < best) {
                    best = e + d;
                    printf("hit total=%d forward=%d backward_word=", best, e);
                    for (int i = 0; i < d; i++) printf("%d%s", word[i], i + 1 < d ? "," : "\n");
                }
            }
        }
        depth = d;
    }
    printf("RESULT target=%s max_length=%d shortest=%d key_matches=%ld backward_nodes=%ld\n",
           argv[1], fwd_max + bwd_max, best == 99 ? -1 : best, key_matches, nodes);
    return 0;
}
