/* Exhaustive rank census for one affine family of unsplit two-thin words.

   The eight parameters are arbitrary 2-by-2 matrices over F_2, packed in four
   bits with bit (2*row+col). The census visits every one of the 2^32 pairs
   (Z, W). A branch is skipped only when six leaf rows, none of which depend
   on A or P, already have rank(Z)+rank(W) at least 8. Rank is monotone under
   adding rows, so every skipped completion is at least 8. The counter must
   reach 2^32.
*/
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static int rank_of(const uint8_t *rows, int n) {
    uint8_t work[8];
    int rank = 0;
    int col;
    for (col = 0; col < n; col++) {
        work[col] = rows[col];
    }
    for (col = 0; col < 8; col++) {
        uint8_t mask = (uint8_t)(1u << col);
        int pivot = -1;
        int i;
        uint8_t piv;
        for (i = rank; i < n; i++) {
            if (work[i] & mask) {
                pivot = i;
                break;
            }
        }
        if (pivot < 0) {
            continue;
        }
        piv = work[rank];
        work[rank] = work[pivot];
        work[pivot] = piv;
        piv = work[rank];
        rank += 1;
        for (i = 0; i < n; i++) {
            if (i != rank - 1 && (work[i] & mask)) {
                work[i] ^= piv;
            }
        }
    }
    return rank;
}

static void put2(uint8_t *row0, uint8_t *row1, int bits, int shift) {
    if (bits & 1) {
        *row0 = (uint8_t)(*row0 | (uint8_t)(1u << shift));
    }
    if (bits & 2) {
        *row0 = (uint8_t)(*row0 | (uint8_t)(1u << (shift + 1)));
    }
    if (bits & 4) {
        *row1 = (uint8_t)(*row1 | (uint8_t)(1u << shift));
    }
    if (bits & 8) {
        *row1 = (uint8_t)(*row1 | (uint8_t)(1u << (shift + 1)));
    }
}

/* Standard family B: leaf0 fixed on Z, leaf1 free with difference I, leaf2 fixed on W. */
static void build(int A, int B, int C, int D, int H, int K, int P, int Q,
                  uint8_t z[8], uint8_t w[8]) {
    int i;
    for (i = 0; i < 8; i++) {
        z[i] = 0;
        w[i] = 0;
    }
    z[0] = (uint8_t)(1u << 2);
    z[1] = (uint8_t)(1u << 3);
    z[2] = (uint8_t)(1u << 0);
    z[3] = (uint8_t)(1u << 1);
    w[0] = (uint8_t)(1u << 6);
    w[1] = (uint8_t)(1u << 7);
    w[6] = (uint8_t)(1u << 0);
    w[7] = (uint8_t)(1u << 1);
    w[0] = (uint8_t)(w[0] | (uint8_t)(1u << 4));
    w[1] = (uint8_t)(w[1] | (uint8_t)(1u << 5));
    w[4] = (uint8_t)(1u << 0);
    w[5] = (uint8_t)(1u << 1);
    put2(&z[0], &z[1], A, 0);
    put2(&w[0], &w[1], A, 0);
    put2(&z[2], &z[3], B, 2);
    put2(&w[2], &w[3], B, 2);
    put2(&z[4], &z[5], C, 4);
    put2(&w[4], &w[5], C, 4);
    put2(&z[6], &z[7], D, 6);
    put2(&w[6], &w[7], D, 6);
    put2(&z[2], &z[3], H, 6);
    put2(&w[2], &w[3], H, 6);
    put2(&z[6], &z[7], K, 2);
    put2(&w[6], &w[7], K, 2);
    put2(&z[0], &z[1], P, 4);
    put2(&w[0], &w[1], P, 4);
    put2(&z[4], &z[5], Q, 0);
    put2(&w[4], &w[5], Q, 0);
}

int main(void) {
    const uint64_t total = 4294967296ull;
    uint64_t seen = 0;
    uint64_t hash = 0;
    uint64_t hash_free = 0;
    int best = 8;
    int A, B, C, D, H, K, P, Q;
    uint8_t z[8], w[8];

    for (A = 0; A < 16; A++) {
        for (B = 0; B < 16; B++) {
            for (C = 0; C < 16; C++) {
                for (D = 0; D < 16; D++) {
                    int sum;
                    build(A, B, C, D, 0, 0, 0, 0, z, w);
                    sum = rank_of(z, 8) + rank_of(w, 8);
                    hash = hash * 1315423911ull + (uint64_t)sum;
                }
            }
        }
    }

    build(0, 0, 0, 0, 0, 0, 0, 0, z, w);
    if (rank_of(z, 8) != 4 || rank_of(w, 8) != 4) {
        fprintf(stderr, "zero point ranks %d %d\n", rank_of(z, 8), rank_of(w, 8));
        return 1;
    }
    for (H = 0; H < 16; H++) {
        for (K = 0; K < 16; K++) {
            for (P = 0; P < 16; P++) {
                for (Q = 0; Q < 16; Q++) {
                    int sum;
                    build(0, 0, 0, 0, H, K, P, Q, z, w);
                    sum = rank_of(z, 8) + rank_of(w, 8);
                    hash_free = hash_free * 1315423911ull + (uint64_t)sum;
                }
            }
        }
    }

    for (Q = 0; Q < 16; Q++) {
        for (C = 0; C < 16; C++) {
            for (K = 0; K < 16; K++) {
                for (D = 0; D < 16; D++) {
                    for (B = 0; B < 16; B++) {
                        for (H = 0; H < 16; H++) {
                            uint8_t zl[6], wl[6];
                            build(0, B, C, D, H, K, 0, Q, z, w);
                            zl[0] = z[2];
                            zl[1] = z[3];
                            zl[2] = z[4];
                            zl[3] = z[5];
                            zl[4] = z[6];
                            zl[5] = z[7];
                            wl[0] = w[2];
                            wl[1] = w[3];
                            wl[2] = w[4];
                            wl[3] = w[5];
                            wl[4] = w[6];
                            wl[5] = w[7];
                            if (rank_of(zl, 6) + rank_of(wl, 6) >= 8) {
                                seen += 256;
                                continue;
                            }
                            for (A = 0; A < 16; A++) {
                                for (P = 0; P < 16; P++) {
                                    int sum;
                                    build(A, B, C, D, H, K, P, Q, z, w);
                                    sum = rank_of(z, 8) + rank_of(w, 8);
                                    if (sum < best) {
                                        fprintf(stderr, "best %d params %d %d %d %d %d %d %d %d\n",
                                                sum, A, B, C, D, H, K, P, Q);
                                        best = sum;
                                    }
                                    seen++;
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    if (seen != total) {
        fprintf(stderr, "count %llu\n", (unsigned long long)seen);
        return 1;
    }
    printf("min=%d count=%llu slice_hash=%llu free_hash=%llu\n", best,
           (unsigned long long)seen, (unsigned long long)hash,
           (unsigned long long)hash_free);
    return best == 8 ? 0 : 2;
}
