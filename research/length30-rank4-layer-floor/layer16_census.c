/* Exhaustive census of the rank-4 layer with exactly 16 points.

   Each of the eight cosets of a fixed 4-flat carries exactly two points, and
   the identity coset is fixed as {0,1} by the symmetry argument in PROOF.md.
   A placement covers the complement of the flat if and only if, for every
   nonzero quotient difference, the four pairwise sumsets partition F_2^4.
   Pruning rejects a partial placement as soon as one of those conditions
   fails. The search is single-threaded and deterministic.
*/
#include <stdint.h>
#include <stdio.h>
#include <time.h>

enum { SUBSETS = 120, WIDTH = 16 };

static int subsets[SUBSETS];
static int sumset[SUBSETS][SUBSETS];
static unsigned char spans[SUBSETS][SUBSETS];
static int chosen[8];
static int covered[8];
static int pairs[8];
static int saved_covered[8][8];
static int saved_pairs[8][8];
static unsigned long long nodes;
static unsigned long long solutions;

static int popcount16(int value) {
    return __builtin_popcount((unsigned)value & 0xFFFF);
}

static void initialize(void) {
    int count = 0;
    for (int left = 0; left < WIDTH; left++) {
        for (int right = left + 1; right < WIDTH; right++) {
            subsets[count++] = (1 << left) | (1 << right);
        }
    }
    for (int i = 0; i < SUBSETS; i++) {
        for (int j = 0; j < SUBSETS; j++) {
            int got = 0;
            for (int a = 0; a < WIDTH; a++) {
                if ((subsets[i] & (1 << a)) == 0) {
                    continue;
                }
                for (int b = 0; b < WIDTH; b++) {
                    if (subsets[j] & (1 << b)) {
                        got |= 1 << (a ^ b);
                    }
                }
            }
            sumset[i][j] = got;
            spans[i][j] = (unsigned char)(popcount16(got) == 4);
        }
    }
}

static uint32_t checksum(void) {
    uint32_t total = 0;
    for (int i = 0; i < SUBSETS; i++) {
        for (int j = 0; j < SUBSETS; j++) {
            total += (uint32_t)sumset[i][j];
        }
    }
    return total;
}

static int commit(int just) {
    for (int delta = 0; delta < 8; delta++) {
        saved_covered[just][delta] = covered[delta];
        saved_pairs[just][delta] = pairs[delta];
    }
    for (int earlier = 0; earlier < just; earlier++) {
        int delta = earlier ^ just;
        int block = sumset[chosen[earlier]][chosen[just]];
        if (!spans[chosen[earlier]][chosen[just]] || (covered[delta] & block)) {
            for (int restore = 0; restore < 8; restore++) {
                covered[restore] = saved_covered[just][restore];
                pairs[restore] = saved_pairs[just][restore];
            }
            return 0;
        }
        covered[delta] |= block;
        pairs[delta]++;
        if (pairs[delta] == 4 && covered[delta] != 0xFFFF) {
            for (int restore = 0; restore < 8; restore++) {
                covered[restore] = saved_covered[just][restore];
                pairs[restore] = saved_pairs[just][restore];
            }
            return 0;
        }
    }
    return 1;
}

static void rollback(int just) {
    for (int delta = 0; delta < 8; delta++) {
        covered[delta] = saved_covered[just][delta];
        pairs[delta] = saved_pairs[just][delta];
    }
}

static void search(int depth, int locked_second) {
    nodes++;
    if (depth == 8) {
        solutions++;
        return;
    }
    int begin = 0;
    int end = SUBSETS;
    if (depth == 0) {
        end = 1;
    }
    if (locked_second >= 0 && depth == 1) {
        begin = locked_second;
        end = locked_second + 1;
    }
    for (int index = begin; index < end; index++) {
        chosen[depth] = index;
        if (!commit(depth)) {
            continue;
        }
        search(depth + 1, locked_second);
        rollback(depth);
    }
}

static int direction_partitions(const int masks[8], int delta) {
    int seen = 0;
    int pair_count = 0;
    for (int left = 0; left < 8; left++) {
        int right = left ^ delta;
        if (right < left) {
            continue;
        }
        int block = 0;
        for (int a = 0; a < WIDTH; a++) {
            if ((masks[left] & (1 << a)) == 0) {
                continue;
            }
            for (int b = 0; b < WIDTH; b++) {
                if (masks[right] & (1 << b)) {
                    block |= 1 << (a ^ b);
                }
            }
        }
        if (popcount16(block) != 4 || (seen & block)) {
            return 0;
        }
        seen |= block;
        pair_count++;
    }
    return pair_count == 4 && seen == 0xFFFF;
}

static int control_passes(void) {
    const int masks[8] = {
        (1 << 0) | (1 << 1),
        (1 << 0) | (1 << 2),
        (1 << 4) | (1 << 5),
        (1 << 0) | (1 << 2),
        (1 << 8) | (1 << 9),
        (1 << 0) | (1 << 2),
        (1 << 12) | (1 << 13),
        (1 << 0) | (1 << 2),
    };
    for (int delta = 1; delta < 8; delta++) {
        int partitioned = direction_partitions(masks, delta);
        if (partitioned != (delta & 1)) {
            return 0;
        }
    }
    return subsets[0] == 3 && subsets[1] == 5;
}

int main(void) {
    initialize();
    if (!control_passes()) {
        fprintf(stderr, "rank-4 layer control failed\n");
        return 1;
    }
    clock_t started = clock();
    search(0, 1);
    unsigned long long branch_nodes = nodes;
    unsigned long long branch_solutions = solutions;
    for (int delta = 0; delta < 8; delta++) {
        covered[delta] = 0;
        pairs[delta] = 0;
    }
    nodes = 0;
    solutions = 0;
    search(0, -1);
    double seconds = (double)(clock() - started) / CLOCKS_PER_SEC;
    printf(
        "PASS_RANK4_LAYER16 solutions=%llu nodes=%llu "
        "branch1_nodes=%llu branch1_solutions=%llu checksum=%u subsets=%d sec=%.3f\n",
        solutions, nodes, branch_nodes, branch_solutions, checksum(), SUBSETS, seconds);
    return solutions == 0 && branch_solutions == 0 ? 0 : 2;
}
