/* Exhaust the two rank-3 arc families left by the height bound.

   A multiplicity-2 source is normalized to label 7 at the start of the word.
   The interior sojourn uses only labels 0,1,2 and visits every point of that
   3-flat. The complementary arc then has either 5 height steps and 16 quotient
   steps, or 4 height steps and 16 quotient steps. Quotient walks are reduced
   to one representative of each orbit under relabeling of labels 3,4,5,6.
*/
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXW 256
static int nw;
static uint8_t vert[MAXW][17];
static uint8_t wpath[MAXW][16];

static int lex_min_path(const uint8_t *path) {
    int perm[4];
    for (perm[0] = 0; perm[0] < 4; perm[0]++)
    for (perm[1] = 0; perm[1] < 4; perm[1]++) if (perm[1] != perm[0])
    for (perm[2] = 0; perm[2] < 4; perm[2]++) if (perm[2] != perm[0] && perm[2] != perm[1]) {
        perm[3] = 6 - perm[0] - perm[1] - perm[2];
        int smaller = 0;
        int greater = 0;
        for (int i = 0; i < 16; i++) {
            int image = perm[path[i]];
            if (!smaller && !greater) {
                if (image < path[i]) smaller = 1;
                else if (image > path[i]) greater = 1;
            }
            if (greater) break;
        }
        if (smaller) return 0;
    }
    return 1;
}

static void gen_walks(void) {
    uint8_t path[16];
    typedef struct { int pos, step, dir; uint16_t vis; int count[4]; } Frame;
    Frame stack[48];
    int sp = 0;
    memset(&stack[0], 0, sizeof stack[0]);
    stack[0].dir = -1;
    stack[0].vis = 1;
    while (sp >= 0) {
        Frame *frame = &stack[sp];
        if (frame->step == 16) {
            int ok = frame->vis == 0xffff;
            for (int dir = 0; dir < 4; dir++) {
                int count = frame->count[dir];
                if (count != 2 && count != 4 && count != 6) ok = 0;
            }
            if (ok && lex_min_path(path)) {
                int point = 0;
                vert[nw][0] = 0;
                for (int i = 0; i < 16; i++) {
                    wpath[nw][i] = path[i];
                    point ^= 1 << path[i];
                    vert[nw][i + 1] = (uint8_t)point;
                }
                nw++;
            }
            sp--;
            continue;
        }
        int advanced = 0;
        for (int dir = frame->dir + 1; dir < 4; dir++) {
            if (frame->count[dir] >= 6) continue;
            int next = frame->pos ^ (1 << dir);
            uint16_t seen = (uint16_t)(frame->vis | (1u << next));
            int left = 15 - frame->step;
            int unvisited = 16 - __builtin_popcount((unsigned)seen);
            if (left < unvisited) continue;
            frame->dir = dir;
            path[frame->step] = (uint8_t)dir;
            Frame child;
            memset(&child, 0, sizeof child);
            child.pos = next;
            child.step = frame->step + 1;
            child.dir = -1;
            child.vis = seen;
            memcpy(child.count, frame->count, sizeof child.count);
            child.count[dir]++;
            stack[++sp] = child;
            advanced = 1;
            break;
        }
        if (!advanced) sp--;
    }
}

static uint64_t hash_walks(void) {
    uint8_t packed[MAXW * 16];
    uint8_t order[MAXW * 16];
    for (int i = 0; i < nw; i++) memcpy(packed + 16 * i, wpath[i], 16);
    /* Insertion sort keeps the hash independent of generation order. */
    int index[MAXW];
    for (int i = 0; i < nw; i++) index[i] = i;
    for (int i = 1; i < nw; i++) {
        int key = index[i];
        int j = i;
        while (j > 0 && memcmp(packed + 16 * index[j - 1], packed + 16 * key, 16) > 0) {
            index[j] = index[j - 1];
            j--;
        }
        index[j] = key;
    }
    for (int i = 0; i < nw; i++) memcpy(order + 16 * i, packed + 16 * index[i], 16);
    uint64_t hash = 14695981039346656037ull;
    for (int i = 0; i < nw * 16; i++) {
        hash ^= order[i];
        hash *= 1099511628211ull;
    }
    return hash;
}

static int build_stations(const uint8_t *steps, int height_steps, int start,
                           const int *where, uint8_t *station, uint8_t *height) {
    int length = 16 + height_steps;
    uint8_t is_height[24] = {0};
    for (int i = 0; i < height_steps; i++) is_height[where[i]] = 1;
    int count = 0;
    int level = start;
    int place = 0;
    int used = 0;
    station[count] = 0;
    height[count] = (uint8_t)level;
    count++;
    for (int i = 0; i < length - 1; i++) {
        if (is_height[i]) level ^= 1 << steps[used++];
        else place++;
        station[count] = (uint8_t)place;
        height[count] = (uint8_t)level;
        count++;
    }
    return count;
}

static int heights_span(const uint8_t *height, int count, int start) {
    int mask = 1 | (1 << start);
    for (int i = 0; i < count; i++) mask |= 1 << height[i];
    int got = 0;
    for (int left = 0; left < 8; left++) if (mask & (1 << left))
        for (int right = left; right < 8; right++) if (mask & (1 << right))
            got |= 1 << (left ^ right);
    return got == 0xff;
}

static int outside_miss(const uint8_t *vertices, const uint8_t *station,
                        const uint8_t *height, int count) {
    int point[24];
    int n = 0;
    uint64_t low = 1;
    uint64_t high = 0;
    point[n++] = 0;
    for (int i = 0; i < count; i++) {
        int packed = height[i] | (vertices[station[i]] << 3);
        uint64_t bit = 1ull << (packed & 63);
        if (packed < 64) {
            if (low & bit) continue;
            low |= bit;
        } else {
            if (high & bit) continue;
            high |= bit;
        }
        point[n++] = packed;
    }
    uint64_t cover_low = 0;
    uint64_t cover_high = 0;
    for (int i = 0; i < n; i++) {
        for (int j = i; j < n; j++) {
            int sum = point[i] ^ point[j];
            if (sum < 64) cover_low |= 1ull << sum;
            else cover_high |= 1ull << (sum - 64);
        }
    }
    int inside = __builtin_popcountll(cover_low & 0xffull);
    int have = __builtin_popcountll(cover_low) + __builtin_popcountll(cover_high);
    return 120 - (have - inside);
}

static int self_test(void) {
    uint8_t path[16] = {0, 1, 2, 3, 0, 1, 2, 1, 0, 1, 2, 3, 0, 1, 2, 1};
    uint8_t vertices[17];
    vertices[0] = 0;
    int point = 0;
    for (int i = 0; i < 16; i++) {
        point ^= 1 << path[i];
        vertices[i + 1] = (uint8_t)point;
    }
    uint8_t steps[5] = {0, 0, 1, 1, 2};
    int where[5] = {0, 1, 2, 3, 4};
    uint8_t station[24], height[24];
    int count = build_stations(steps, 5, 4, where, station, height);
    return outside_miss(vertices, station, height, count) == 60;
}

static void search_family(int height_steps, long long *tests, int *best, int *found) {
    int nseq = 1;
    for (int i = 0; i < height_steps; i++) nseq *= 3;
    uint8_t steps[8];
    int where[8];
    uint8_t station[24], height[24];
    int length = 16 + height_steps;
    for (int id = 0; id < nseq; id++) {
        int mixed = id;
        int start = 0;
        for (int i = 0; i < height_steps; i++) {
            steps[i] = (uint8_t)(mixed % 3);
            start ^= 1 << steps[i];
            mixed /= 3;
        }
        for (int i = 0; i < height_steps; i++) where[i] = i;
        while (1) {
            int count = build_stations(steps, height_steps, start, where, station, height);
            if (heights_span(height, count, start)) {
                for (int walk = 0; walk < nw; walk++) {
                    int miss = outside_miss(vert[walk], station, height, count);
                    (*tests)++;
                    if (miss < *best) *best = miss;
                    if (miss == 0) {
                        (*found)++;
                        return;
                    }
                }
            }
            int cursor = height_steps - 1;
            while (cursor >= 0 && where[cursor] == length - height_steps + cursor) cursor--;
            if (cursor < 0) break;
            where[cursor]++;
            for (int j = cursor + 1; j < height_steps; j++) where[j] = where[j - 1] + 1;
        }
    }
}

int main(void) {
    clock_t started = clock();
    gen_walks();
    if (nw != 108) {
        fprintf(stderr, "canonical walk count %d\n", nw);
        return 1;
    }
    if (!self_test()) {
        fprintf(stderr, "self-test failed\n");
        return 1;
    }
    uint64_t digest = hash_walks();
    long long tests = 0;
    int best = 999;
    int found = 0;
    search_family(5, &tests, &best, &found);
    long long after_five = tests;
    if (!found) search_family(4, &tests, &best, &found);
    double seconds = (double)(clock() - started) / CLOCKS_PER_SEC;
    if (found || best == 0) {
        printf("FOUND best=%d tests=%lld\n", best, tests);
        return 2;
    }
    printf("PASS_RANK3_NONE walks=108 digest=%016llx five=%lld four=%lld best_miss=%d sec=%.1f\n",
           (unsigned long long)digest, after_five, tests - after_five, best, seconds);
    return 0;
}
