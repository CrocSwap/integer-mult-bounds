/* Canonical simple restored walks on F_2^n and the fixed L/2 firing census.
 * Usage: ./census n L   -> prints closed, universal, false prunes and per-mask counts.
 * Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static int n, L, base;
static int word[64], st[64];
static uint64_t closed, universal, prunes, per_mask[64];

static void classify(void) {
    closed++;
    int N = 1 << n;
    uint64_t sum = 0;                      /* difference set, as a bit mask over F_2^n */
    for (int i = 0; i < L; i++)
        for (int j = 0; j < L; j++) sum |= 1ULL << (st[i] ^ st[j]);
    if (sum != (N == 64 ? ~0ULL : ((1ULL << N) - 1))) return;
    universal++;
    for (int m = 1; m < N; m++) {
        uint64_t seen[2] = {0, 0};
        int size[2] = {0, 0};
        for (int i = 0; i < L; i++) size[__builtin_popcount(st[i] & m) & 1]++;
        for (int i = 0; i < L; i++) {
            int si = __builtin_popcount(st[i] & m) & 1;
            for (int j = i + 1; j < L; j++)
                if ((__builtin_popcount(st[j] & m) & 1) == si) seen[si] |= 1ULL << (st[i] ^ st[j]);
        }
        long excess = 0;
        for (int s = 0; s < 2; s++)
            excess += (long)size[s] * (size[s] - 1) / 2 - __builtin_popcountll(seen[s]);
        long d = (size[0] - size[1]) / 2;
        if (base < excess && excess <= base + d * d) { prunes++; per_mask[m]++; }
    }
}

static void walk(int depth, int state, uint64_t visited, int maxlab) {
    if (depth == L) { if (state == 0) classify(); return; }
    int top = maxlab + 1 < n - 1 ? maxlab + 1 : n - 1;
    for (int lab = 0; lab <= top; lab++) {
        int nxt = state ^ (1 << lab);
        if (depth == L - 1) { if (nxt != 0) continue; }
        else if ((visited >> nxt) & 1) continue;
        word[depth] = lab;
        st[depth + 1 < L ? depth + 1 : 0] = depth + 1 < L ? nxt : 0;
        walk(depth + 1, nxt, visited | (1ULL << nxt), lab > maxlab ? lab : maxlab);
    }
}

int main(int argc, char **argv) {
    if (argc != 3) { fprintf(stderr, "usage: census n L\n"); return 2; }
    n = atoi(argv[1]); L = atoi(argv[2]);
    if (n < 1 || n > 6 || L < 2 || L % 2 || L > (1 << n)) { fprintf(stderr, "domain\n"); return 2; }
    base = (L / 2) * (L / 2 - 1) - ((1 << (n - 1)) - 1);
    st[0] = 0;
    walk(0, 0, 1ULL, -1);
    printf("n=%d L=%d closed=%llu universal=%llu prunes=%llu", n, L,
           (unsigned long long)closed, (unsigned long long)universal, (unsigned long long)prunes);
    int fired = 0;
    for (int m = 1; m < (1 << n); m++) fired += per_mask[m] > 0;
    printf(" firing_masks=%d\n", fired);
    for (int m = 1; m < (1 << n); m++)
        if (per_mask[m]) printf("mask %d %llu\n", m, (unsigned long long)per_mask[m]);
    return 0;
}
