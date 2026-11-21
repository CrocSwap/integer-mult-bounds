/* Run trit passes on four two-trit atoms. Each bucket has one write and one read head. */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

enum { TRITS = 8, BODY = 6561 };
static const size_t power3[] = {1,3,9,27,81,243,729,2187,6561};

/* Read [prefix][a][gap][b][suffix] and write [prefix][b][gap][a][suffix]. */
static void exchange(const uint8_t *src, uint8_t *dst, uint8_t *scratch,
                     size_t prefixes, size_t gap, size_t piece) {
    for (size_t p = 0; p < prefixes; ++p) {
        size_t put[9], get[9];
        for (size_t b = 0; b < 9; ++b) put[b] = get[b] = b * gap * piece;
        for (size_t a = 0; a < 3; ++a)
            for (size_t g = 0; g < gap; ++g)
                for (size_t b = 0; b < 3; ++b) {
                    size_t k = 3 * b + a;
                    memcpy(scratch + put[k], src, piece);
                    put[k] += piece;
                    src += piece;
                }
        for (size_t b = 0; b < 3; ++b)
            for (size_t g = 0; g < gap; ++g)
                for (size_t a = 0; a < 3; ++a) {
                    size_t k = 3 * b + a;
                    memcpy(dst, scratch + get[k], piece);
                    get[k] += piece;
                    dst += piece;
                }
        memset(scratch, 0, 9 * gap * piece);
    }
}

/* Read and write sequentially. Save the first run until the second run is copied. */
static void lower(const uint8_t *src, uint8_t *dst, uint8_t *scratch,
                  size_t prefixes, size_t gap, size_t piece, unsigned coefficient) {
    for (size_t p = 0; p < prefixes; ++p)
        for (size_t a = 0; a < 3; ++a)
            for (size_t g = 0; g < gap; ++g) {
                size_t last = (coefficient * a % 3) * piece;
                size_t first = 3 * piece - last;
                memcpy(scratch, src, first);
                src += first;
                memcpy(dst, src, last);
                src += last;
                dst += last;
                memcpy(dst, scratch, first);
                dst += first;
                memset(scratch, 0, first);
            }
}

static void negate(const uint8_t *src, uint8_t *dst, uint8_t *scratch,
                   size_t prefixes, size_t piece) {
    for (size_t p = 0; p < prefixes; ++p) {
        memcpy(dst, src, piece);
        src += piece;
        dst += piece;
        memcpy(scratch, src, piece);
        src += piece;
        memcpy(dst, src, piece);
        src += piece;
        dst += piece;
        memcpy(dst, scratch, piece);
        dst += piece;
        memset(scratch, 0, piece);
    }
}

/* An instruction is (kind, earlier trit, later trit, coefficient). */
int run_packet(uint8_t *data, size_t size, size_t suffix,
               const uint8_t *program, size_t count) {
    if (!suffix || suffix > SIZE_MAX / BODY || size != BODY * suffix) return 1;
    for (size_t i = 0; i < count; ++i) {
        const uint8_t *p = program + 4 * i;
        if (p[0] > 2 || p[1] > p[2] || p[2] >= TRITS ||
            (p[0] < 2 && p[1] == p[2]) || (p[0] == 2 && p[1] != p[2]) || p[3] > 2)
            return 1;
    }
    uint8_t *buf = malloc(size), *scratch = malloc(size);
    if (!buf || !scratch) { free(buf); free(scratch); return 2; }
    uint8_t *src = data, *dst = buf;
    for (size_t i = 0; i < count; ++i) {
        const uint8_t *p = program + 4 * i;
        size_t prefixes = power3[p[1]], piece = power3[TRITS - 1 - p[2]] * suffix;
        if (p[0] == 2) negate(src, dst, scratch, prefixes, piece);
        else {
            size_t gap = power3[p[2] - p[1] - 1];
            if (p[0] == 0) lower(src, dst, scratch, prefixes, gap, piece, p[3]);
            else exchange(src, dst, scratch, prefixes, gap, piece);
        }
        memset(src, 0, size);
        uint8_t *old = src;
        src = dst;
        dst = old;
    }
    if (src != data) memcpy(data, src, size);
    memset(buf, 0, size);
    memset(scratch, 0, size);
    free(scratch);
    free(buf);
    return 0;
}
