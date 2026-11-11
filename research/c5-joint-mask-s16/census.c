/* Exhaustive census: legal S(16) versus all fifteen weight-2 masks and the weight-6 mask.

A floor word has length 30 and uses each of six sources five times.
S(16) = 2 q_16 + e_{w_16} is legal when every coordinate lies in {0,1,5,6,10}.
The search enumerates first-occurrence canonical words whose centre is legal,
of the two shapes proved by the coordinate arithmetic in the README, and
rejects a partial word only when some required mask has no realizing pair in
the past prefixes or in the future count box. See README.md for the
completeness argument. This file does not read a SAT certificate.
*/
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

enum { K = 6, CAP = 5, LEN = 30, NEDGE = 15 };

static int resv(int v) { return v == 5 ? 0 : v; }
static int edge_index[K][K];
static int two_ok[6][2];
static int edge_a[NEDGE], edge_b[NEDGE];

static int counts[K];
static unsigned char seen[LEN + 1][K];
static int nseen;
static int realized, w6;
static int target_mode;
static uint64_t nodes, solutions, alive_roots, examined_roots;

static void init_tables(void) {
    int e = 0;
    for (int i = 0; i < K; i++)
        for (int j = i + 1; j < K; j++) {
            edge_index[i][j] = edge_index[j][i] = e;
            edge_a[e] = i;
            edge_b[e] = j;
            e++;
        }
    for (int L = 0; L <= 5; L++)
        for (int bit = 0; bit < 2; bit++) {
            int ok = 0;
            for (int x = L; x <= 5 && !ok; x++)
                for (int y = x; y <= 5; y++)
                    if ((resv(x) + resv(y)) % 5 == bit) ok = 1;
            two_ok[L][bit] = ok;
        }
    for (int L = 0; L <= 5; L++) {
        if (two_ok[L][1] != (L <= 3) || !two_ok[L][0]) {
            fprintf(stderr, "FAIL two-future table at L=%d\n", L);
            exit(1);
        }
    }
}

static int has_res(int L, int need) {
    if (need == 0) return 1; /* value 5 is always still available and has residue 0 */
    return L <= need && need <= 5;
}

static void reset_state(void) {
    memset(counts, 0, sizeof counts);
    memset(seen, 0, sizeof seen);
    nseen = 1;
    realized = 0;
    w6 = 0;
}

static int mask_alive_bits(int bits) {
    int two = 1;
    for (int j = 0; j < K; j++) {
        int bit = (bits >> j) & 1;
        if (!two_ok[counts[j]][bit]) { two = 0; break; }
    }
    if (two) return 1;
    for (int p = 0; p < nseen; p++) {
        int ok = 1;
        for (int j = 0; j < K; j++) {
            int bit = (bits >> j) & 1;
            int want = (bit - seen[p][j] + 50) % 5;
            if (!has_res(counts[j], want)) { ok = 0; break; }
        }
        if (ok) return 1;
    }
    return 0;
}

static int all_alive(void) {
    for (int e = 0; e < NEDGE; e++) {
        if ((realized >> e) & 1) continue;
        int bits = (1 << edge_a[e]) | (1 << edge_b[e]);
        if (!mask_alive_bits(bits)) return 0;
    }
    if (!w6 && !mask_alive_bits(63)) return 0;
    return 1;
}

static void absorb(void) {
    const unsigned char *nr = seen[nseen - 1];
    for (int p = 0; p < nseen; p++) {
        int good = 1, wt = 0, bits = 0;
        for (int j = 0; j < K; j++) {
            int s = (seen[p][j] + nr[j]) % 5;
            if (s > 1) { good = 0; break; }
            if (s) { bits |= 1 << j; wt++; }
        }
        if (!good) continue;
        if (wt == 6) w6 = 1;
        else if (wt == 2) {
            int a = __builtin_ctz(bits);
            int b = __builtin_ctz(bits & ~(1 << a));
            realized |= 1 << edge_index[a][b];
        }
    }
}

static int shape16(void) {
    int c5 = 0, c3 = 0, c2 = 0, c0 = 0, other = 0;
    for (int j = 0; j < K; j++) {
        int v = counts[j];
        if (v == 5) c5++;
        else if (v == 3) c3++;
        else if (v == 2) c2++;
        else if (v == 0) c0++;
        else other++;
    }
    if (target_mode == 0) return c5 == 2 && c3 == 2 && c0 == 2 && other == 0;
    return c5 == 1 && c3 == 3 && c2 == 1 && c0 == 1 && other == 0;
}

static void place(int j) {
    counts[j]++;
    for (int t = 0; t < K; t++) seen[nseen][t] = (unsigned char)resv(counts[t]);
    nseen++;
    absorb();
}

static void rec_suf(int depth, int nxt) {
    nodes++;
    if (depth == LEN) {
        if (realized == (1 << NEDGE) - 1 && w6) solutions++;
        return;
    }
    /* Sound extra cut: a node whose masks are already impossible has no witness below it. */
    if ((nodes & 15) == 0 && !all_alive()) return;
    for (int j = 0; j < K; j++) {
        if (counts[j] >= CAP) continue;
        if (counts[j] == 0 && j > nxt) continue;
        int c = counts[j];
        counts[j] = c + 1;
        for (int t = 0; t < K; t++) seen[nseen][t] = (unsigned char)resv(counts[t]);
        nseen++;
        int save_r = realized, save_w = w6;
        absorb();
        int shrink = (c == 1 || c == 2 || c == 3 || c == 4);
        if (!shrink || all_alive()) {
            int nnxt = c ? nxt : (j == nxt ? j + 1 : nxt);
            rec_suf(depth + 1, nnxt);
        }
        realized = save_r;
        w6 = save_w;
        nseen--;
        counts[j] = c;
        if (solutions) return;
    }
}

static void rec_pre(int depth, int nxt) {
    if (depth == 16) {
        if (!shape16()) return;
        int used = 0;
        for (int j = 0; j < K; j++) if (counts[j]) used++;
        for (int letter = 0; letter < K; letter++) {
            if (counts[letter] >= CAP) continue;
            if (counts[letter] == 0 && letter != used) continue;
            int ok = 1;
            for (int j = 0; j < K; j++) {
                int s = 2 * counts[j] + (j == letter);
                if (s != 0 && s != 1 && s != 5 && s != 6 && s != 10) { ok = 0; break; }
            }
            if (!ok) continue;
            examined_roots++;
            int c = counts[letter];
            int save_r = realized, save_w = w6, save_n = nseen;
            place(letter);
            if (all_alive()) {
                alive_roots++;
                int nnxt = c ? nxt : (letter == nxt ? letter + 1 : nxt);
                rec_suf(17, nnxt);
            }
            realized = save_r;
            w6 = save_w;
            nseen = save_n;
            counts[letter] = c;
            if (solutions) return;
        }
        return;
    }
    for (int j = 0; j < K; j++) {
        int c = counts[j];
        if (c >= CAP) continue;
        if (c == 0 && j > nxt) continue;
        int positive = 0, above3 = 0;
        for (int t = 0; t < K; t++) {
            int v = counts[t] + (t == j);
            if (v > 0) positive++;
            if (v > 3) above3++;
        }
        if (target_mode == 0) {
            if (positive > 4 || above3 > 2) continue;
        } else if (positive > 5 || above3 > 1) {
            continue;
        }
        int save_r = realized, save_w = w6, save_n = nseen;
        place(j);
        int nnxt = c ? nxt : (j == nxt ? j + 1 : nxt);
        rec_pre(depth + 1, nnxt);
        realized = save_r;
        w6 = save_w;
        nseen = save_n;
        counts[j] = c;
        if (solutions) return;
    }
}

/* Replay one literal word through the same residue update. */
static void walk(const char *text, int *pop, int *got_w6, int *w6_died) {
    reset_state();
    *w6_died = 0;
    for (int i = 0; text[i]; i++) {
        place(text[i] - '0');
        if (!w6 && !mask_alive_bits(63)) *w6_died = 1;
    }
    *pop = __builtin_popcount((unsigned)realized);
    *got_w6 = w6;
}

static int expect_mode(int mode, uint64_t ex, uint64_t al, uint64_t nd, uint64_t sol) {
    reset_state();
    target_mode = mode;
    nodes = solutions = alive_roots = examined_roots = 0;
    rec_pre(0, 0);
    printf("mode %d examined %llu alive %llu nodes %llu solutions %llu\n",
           mode,
           (unsigned long long)examined_roots,
           (unsigned long long)alive_roots,
           (unsigned long long)nodes,
           (unsigned long long)solutions);
    fflush(stdout);
    if (examined_roots != ex || alive_roots != al || nodes != nd || solutions != sol) {
        fprintf(stderr, "FAIL mode %d counters\n", mode);
        return 1;
    }
    return 0;
}

int main(int argc, char **argv) {
    init_tables();
    int pop = 0, got = 0, died = 0;
    walk("000001111122222333334444455555", &pop, &got, &died);
    if (pop != 15 || got != 0 || died != 1) {
        fprintf(stderr, "FAIL sorted walk pop=%d w6=%d died=%d\n", pop, got, died);
        return 1;
    }
    walk("012300333300112241122545545544", &pop, &got, &died);
    if (got != 1 || died != 0 || pop != 5) {
        fprintf(stderr, "FAIL weight-6 legal walk pop=%d w6=%d died=%d\n", pop, got, died);
        return 1;
    }
    printf("self_test sorted_w2=15 sorted_w6=0 weight6_legal_w6=1 weight6_legal_w2=%d\n", pop);
    fflush(stdout);
    if (argc > 1 && strcmp(argv[1], "self") == 0) return 0;
    if (expect_mode(0, 10090080ULL, 8793ULL, 31821ULL, 0ULL)) return 1;
    if (expect_mode(1, 67267200ULL, 13496310ULL, 419423032ULL, 0ULL)) return 1;
    printf("PASS_C5_JOINT_MASK_S16_CENSUS solutions=0\n");
    return 0;
}
