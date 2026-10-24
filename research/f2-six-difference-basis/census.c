/* Exhaustive normalized difference bases in F_2^6.
   A set contains 0 and the standard basis. Extras are the other nonzero
   vectors, taken in increasing order. Coverage counts nonzero pairwise sums
   of {0} union the listed points. Apache-2.0. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

static int rest[57];
static int nrest;
static const int basis[6] = {1, 2, 4, 8, 16, 32};
static const uint64_t FULL = ~1ULL;

static void init_rest(void) {
    nrest = 0;
    for (int i = 1; i < 64; i++) {
        int is_basis = 0;
        for (int k = 0; k < 6; k++) {
            if (i == basis[k]) {
                is_basis = 1;
            }
        }
        if (!is_basis) {
            rest[nrest++] = i;
        }
    }
    if (nrest != 57) {
        fprintf(stderr, "rest count %d\n", nrest);
        exit(1);
    }
}

static int cover_count(const int *pts, int n, uint64_t *out) {
    uint64_t seen = 0;
    for (int i = 0; i < n; i++) {
        seen |= 1ULL << pts[i];
        for (int j = i + 1; j < n; j++) {
            seen |= 1ULL << (pts[i] ^ pts[j]);
        }
    }
    if (out) {
        *out = seen;
    }
    return __builtin_popcountll(seen);
}

static void run5(void) {
    long hits = 0;
    long n = 0;
    int best = 0;
    int witness[11] = {0};
    for (int a = 0; a < nrest; a++) {
        for (int b = a + 1; b < nrest; b++) {
            for (int c = b + 1; c < nrest; c++) {
                for (int d = c + 1; d < nrest; d++) {
                    for (int e = d + 1; e < nrest; e++) {
                        int pts[11] = {
                            1, 2, 4, 8, 16, 32,
                            rest[a], rest[b], rest[c], rest[d], rest[e]
                        };
                        uint64_t seen = 0;
                        int cvd = cover_count(pts, 11, &seen);
                        if (cvd > best) {
                            best = cvd;
                            for (int i = 0; i < 11; i++) {
                                witness[i] = pts[i];
                            }
                        }
                        if (seen == FULL) {
                            hits++;
                        }
                        n++;
                    }
                }
            }
        }
    }
    printf("extra=5 n=%ld hits=%ld best=%d\n", n, hits, best);
    printf("witness12");
    for (int i = 0; i < 11; i++) {
        printf(" %d", witness[i]);
    }
    printf("\n");
}

static void run6(void) {
    long hits = 0;
    long n = 0;
    int best = 0;
    int witness[12] = {0};
    for (int a = 0; a < nrest; a++) {
        for (int b = a + 1; b < nrest; b++) {
            for (int c = b + 1; c < nrest; c++) {
                for (int d = c + 1; d < nrest; d++) {
                    for (int e = d + 1; e < nrest; e++) {
                        for (int f = e + 1; f < nrest; f++) {
                            int pts[12] = {
                                1, 2, 4, 8, 16, 32,
                                rest[a], rest[b], rest[c], rest[d], rest[e], rest[f]
                            };
                            uint64_t seen = 0;
                            int cvd = cover_count(pts, 12, &seen);
                            if (cvd > best) {
                                best = cvd;
                                for (int i = 0; i < 12; i++) {
                                    witness[i] = pts[i];
                                }
                            }
                            if (seen == FULL) {
                                hits++;
                            }
                            n++;
                        }
                    }
                }
            }
        }
    }
    printf("extra=6 n=%ld hits=%ld best=%d\n", n, hits, best);
    printf("witness13");
    for (int i = 0; i < 12; i++) {
        printf(" %d", witness[i]);
    }
    printf("\n");
}

static void run7(void) {
    long hits = 0;
    long n = 0;
    int best = 0;
    const int fixed[13] = {1, 2, 4, 8, 16, 32, 3, 5, 6, 24, 40, 48, 63};
    int found_fixed = 0;
    for (int a = 0; a < nrest; a++) {
        for (int b = a + 1; b < nrest; b++) {
            for (int c = b + 1; c < nrest; c++) {
                for (int d = c + 1; d < nrest; d++) {
                    for (int e = d + 1; e < nrest; e++) {
                        for (int f = e + 1; f < nrest; f++) {
                            for (int g = f + 1; g < nrest; g++) {
                                int pts[13] = {
                                    1, 2, 4, 8, 16, 32,
                                    rest[a], rest[b], rest[c], rest[d],
                                    rest[e], rest[f], rest[g]
                                };
                                uint64_t seen = 0;
                                int cvd = cover_count(pts, 13, &seen);
                                if (cvd > best) {
                                    best = cvd;
                                }
                                if (seen == FULL) {
                                    hits++;
                                    int same = 1;
                                    for (int i = 0; i < 13; i++) {
                                        if (pts[i] != fixed[i]) {
                                            same = 0;
                                        }
                                    }
                                    if (same) {
                                        found_fixed = 1;
                                    }
                                }
                                n++;
                            }
                        }
                    }
                }
            }
        }
    }
    printf("extra=7 n=%ld hits=%ld best=%d fixed=%d\n", n, hits, best, found_fixed);
}

int main(void) {
    init_rest();
    run5();
    run6();
    run7();
    return 0;
}
