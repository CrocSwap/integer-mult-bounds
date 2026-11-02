/* Signed spectrum of the zero-diagonal binary full-guard character.

   For every edge-mask of a k-by-k zero-diagonal matrix, Z is the subset
   form of the three-state character sum. Output lines are "Z b" where
   b is the even-weight count minus the odd-weight count. k is 3, 4, 5 or 6.
*/
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    int vertices = argc > 1 ? atoi(argv[1]) : 6;
    if (vertices < 3 || vertices > 6) return 2;
    int edge_count = vertices * (vertices - 1);
    int subsets = 1 << vertices;
    int z_limit = 1;
    for (int i = 0; i < vertices; i++) z_limit *= 3;

    int *weight = calloc((size_t)subsets, sizeof(int));
    int *members = calloc((size_t)edge_count * subsets, sizeof(int));
    uint8_t *bit_of = calloc((size_t)edge_count * subsets, sizeof(uint8_t));
    int *member_count = calloc((size_t)edge_count, sizeof(int));
    if (!weight || !members || !bit_of || !member_count) return 3;
    for (int subset = 0; subset < subsets; subset++)
        weight[subset] = 1 << (vertices - __builtin_popcount((unsigned)subset));

    int edge = 0;
    for (int tail = 0; tail < vertices; tail++) {
        for (int head = 0; head < vertices; head++) {
            if (tail == head) continue;
            int count = 0;
            for (int subset = 0; subset < subsets; subset++) {
                if (((subset >> tail) & 1) && !((subset >> head) & 1)) {
                    members[edge * subsets + count] = subset;
                    bit_of[edge * subsets + count] = (uint8_t)(1u << head);
                    count++;
                }
            }
            member_count[edge] = count;
            edge++;
        }
    }

    int64_t *even = calloc((size_t)z_limit + 1, sizeof(int64_t));
    int64_t *odd = calloc((size_t)z_limit + 1, sizeof(int64_t));
    uint8_t *failed = calloc((size_t)subsets, 1);
    if (!even || !odd || !failed) return 3;
    int value = 0;
    for (int subset = 0; subset < subsets; subset++) value += weight[subset];
    if (value != z_limit) return 4;
    even[value]++;

    uint32_t limit = 1u << edge_count;
    for (uint32_t step = 1; step < limit; step++) {
        int flipped = __builtin_ctz(step);
        int base = flipped * subsets;
        int count = member_count[flipped];
        for (int index = 0; index < count; index++) {
            int subset = members[base + index];
            uint8_t before = failed[subset];
            uint8_t after = (uint8_t)(before ^ bit_of[base + index]);
            failed[subset] = after;
            if (before == 0) value -= weight[subset];
            else if (after == 0) value += weight[subset];
        }
        if ((unsigned)value > (unsigned)z_limit) return 5;
        if (step & 1u) odd[value]++;
        else even[value]++;
    }

    int64_t total = 0;
    int64_t signed_total = 0;
    for (int point = 0; point <= z_limit; point++) {
        total += even[point] + odd[point];
        int64_t coefficient = even[point] - odd[point];
        signed_total += coefficient;
        if (coefficient)
            printf("%d %lld\n", point, (long long)coefficient);
    }
    if (total != (1LL << edge_count) || signed_total != 0) return 6;
    return 0;
}
